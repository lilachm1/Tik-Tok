import sys
import io

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
elif hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from bidi.algorithm import get_display

try:
    from moviepy import VideoClip, concatenate_videoclips
except ImportError:
    from moviepy.editor import VideoClip, concatenate_videoclips


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_DIR = Path(r"C:\Automation\TikTok")

CANVAS_W, CANVAS_H = 1080, 1920
SAFE_W = 900

FONT_SEARCH_ORDER = [
    Path(r"C:\Windows\Fonts\ArialUni.ttf"),
    Path(r"C:\Windows\Fonts\tahoma.ttf"),
    Path(r"C:\Windows\Fonts\arial.ttf"),
    Path(r"C:\Windows\Fonts\David.ttf"),
]

BASE_FONT_SIZES = {0: 78, 1: 72, 2: 66, 3: 66, 4: 72}
BASE_FONT_SIZE  = 72

TEXT_COLORS = {
    "white":  ("#FFFFFF", "#000000"),
    "yellow": ("#FFE600", "#000000"),
    "red":    ("#FF2D2D", "#FFFFFF"),
}
VALID_COLORS    = set(TEXT_COLORS)
VALID_POSITIONS = {"top-center", "center", "bottom"}

OUTLINE_OFFSETS = [(-3, 0), (3, 0), (0, -3), (0, 3), (-3, -3), (3, -3), (-3, 3), (3, 3)]

# Ken Burns per-variant, per-segment: (motion_type, param1, param2)
# zoom_in/out:  param1=start_scale, param2=end_scale
# pan_right/left: param1=overscan_scale (1.06), param2=pan_pixels (+right / -left)
KEN_BURNS = {
    "A": [
        ("zoom_in",   1.00, 1.08),
        ("zoom_in",   1.00, 1.06),
        ("pan_right", 1.06, 30),
        ("zoom_in",   1.00, 1.08),
        ("zoom_out",  1.08, 1.00),
    ],
    "B": [
        ("pan_left",  1.06, -30),
        ("zoom_in",   1.00, 1.06),
        ("zoom_in",   1.00, 1.10),
        ("pan_right", 1.06, 20),
        ("zoom_in",   1.00, 1.05),
    ],
    "C": [
        ("zoom_out",  1.08, 1.00),
        ("pan_left",  1.06, -20),
        ("pan_right", 1.06, 30),
        ("zoom_in",   1.00, 1.08),
        ("zoom_out",  1.08, 1.00),
    ],
    "D": [
        ("pan_right", 1.06, 30),
        ("zoom_in",   1.00, 1.08),
        ("zoom_out",  1.08, 1.00),
        ("zoom_in",   1.00, 1.06),
        ("pan_left",  1.06, -20),
    ],
}


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def info(msg):
    print(f"[generate_videos] {msg}", flush=True)

def warn(msg):
    print(f"⚠️  {msg}", flush=True)


# ---------------------------------------------------------------------------
# Phase 1 — Font
# ---------------------------------------------------------------------------

def _measure_text(font, text):
    try:
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        try:
            return font.getsize(text)
        except Exception:
            return len(text) * max(4, font.size // 2), font.size


def verify_font(path: Path) -> bool:
    try:
        font = ImageFont.truetype(str(path), 72)
        img  = Image.new("RGB", (200, 100), "white")
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "ש", font=font, fill="black")
        dark = int((np.array(img) < 200).sum())
        return dark > 20
    except Exception:
        return False


def find_font(font_path_arg=None):
    candidates = []
    if font_path_arg:
        candidates.append(Path(font_path_arg))
    candidates.extend(FONT_SEARCH_ORDER)
    fonts_dir = Path(r"C:\Windows\Fonts")
    if fonts_dir.exists():
        for pat in ("*[Nn]oto*[Hh]ebrew*.ttf", "*noto*hebrew*.ttf"):
            candidates.extend(fonts_dir.glob(pat))
    for path in candidates:
        if path.exists() and verify_font(path):
            return path
    return None


# ---------------------------------------------------------------------------
# Image frame rendering
# ---------------------------------------------------------------------------

def make_frame(pil_image: Image.Image) -> np.ndarray:
    """Scale to 1080×1920 with blur-background fill. Returns RGB numpy array."""
    img = pil_image.convert("RGB")
    iw, ih = img.size

    if ih > iw * 1.5:
        scale  = max(CANVAS_W / iw, CANVAS_H / ih)
        bw, bh = int(iw * scale), int(ih * scale)
        filled = img.resize((bw, bh), Image.LANCZOS)
        left   = (bw - CANVAS_W) // 2
        top    = (bh - CANVAS_H) // 2
        return np.array(filled.crop((left, top, left + CANVAS_W, top + CANVAS_H)))

    fg_scale   = min(CANVAS_W / iw, CANVAS_H / ih)
    fw, fh     = int(iw * fg_scale), int(ih * fg_scale)
    foreground = img.resize((fw, fh), Image.LANCZOS)

    bg_scale   = max(CANVAS_W / iw, CANVAS_H / ih)
    bw, bh     = int(iw * bg_scale), int(ih * bg_scale)
    background = img.resize((bw, bh), Image.LANCZOS)
    left       = (bw - CANVAS_W) // 2
    top        = (bh - CANVAS_H) // 2
    background = background.crop((left, top, left + CANVAS_W, top + CANVAS_H))
    background = background.filter(ImageFilter.GaussianBlur(radius=35))
    bg_arr     = np.clip(np.array(background, dtype=np.float32) * 0.7, 0, 255).astype(np.uint8)
    background = Image.fromarray(bg_arr)

    canvas = background.copy()
    canvas.paste(foreground, ((CANVAS_W - fw) // 2, (CANVAS_H - fh) // 2))
    return np.array(canvas)


# ---------------------------------------------------------------------------
# Text rendering
# ---------------------------------------------------------------------------

def strip_unsupported_chars(text: str) -> str:
    """Remove non-BMP Unicode characters (code point > U+FFFF).
    Tahoma and most Windows Hebrew fonts only cover the Basic Multilingual
    Plane. Emoji (U+1F000+) render as broken squares — strip them before
    any text reaches Pillow so artefacts are impossible regardless of what
    the video-config contains."""
    cleaned = "".join(ch for ch in text if ord(ch) <= 0xFFFF)
    return " ".join(cleaned.split())


def _wrap_lines(logical_text: str, font, max_w: int) -> list:
    visual_full = get_display(logical_text)
    w, _ = _measure_text(font, visual_full)
    if w <= max_w:
        return [visual_full]

    words, lines, current = logical_text.split(), [], []
    for word in words:
        test    = " ".join(current + [word])
        visual  = get_display(test)
        tw, _   = _measure_text(font, visual)
        if tw <= max_w:
            current.append(word)
        else:
            if current:
                lines.append(get_display(" ".join(current)))
                current = [word]
            else:
                lines.append(get_display(word))
    if current:
        lines.append(get_display(" ".join(current)))
    return lines or [visual_full]


def build_text_layer(text: str, font_path: Path, font_size: int,
                     color_str: str, position_str: str) -> np.ndarray:
    """Returns 1080×1920 RGBA numpy array with text overlay."""
    text = strip_unsupported_chars(text)
    text_color, outline_color = TEXT_COLORS[color_str]

    current_size = font_size
    lines = []
    font  = None
    while True:
        font  = ImageFont.truetype(str(font_path), current_size)
        lines = _wrap_lines(text, font, SAFE_W)
        if len(lines) <= 3:
            break
        current_size -= 6
        if current_size < 24:
            lines = lines[:3]
            font  = ImageFont.truetype(str(font_path), current_size)
            break

    line_h  = int(current_size * 1.25)
    total_h = line_h * len(lines)

    if position_str == "top-center":
        y_start = 100
    elif position_str == "center":
        y_start = CANVAS_H // 2 - total_h // 2
    else:  # bottom
        y_start = 1820 - total_h

    overlay = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)

    for i, line in enumerate(lines):
        y     = y_start + i * line_h
        tw, _ = _measure_text(font, line)
        x     = (CANVAS_W - tw) // 2
        for dx, dy in OUTLINE_OFFSETS:
            draw.text((x + dx, y + dy), line, font=font, fill=outline_color)
        draw.text((x, y), line, font=font, fill=text_color)

    return np.array(overlay)


# ---------------------------------------------------------------------------
# Segment clip builder (Ken Burns + text composited per frame)
# ---------------------------------------------------------------------------

def _make_frame_func(bg_pil: Image.Image, text_pil: Image.Image,
                     motion: tuple, duration: float):
    """Return a make_frame(t) closure for one segment."""
    mtype, p1, p2 = motion
    d = duration

    def make_frame(t):
        frac = min(1.0, t / d) if d > 0 else 1.0

        if mtype in ("zoom_in", "zoom_out"):
            scale = p1 + (p2 - p1) * frac
            nw    = max(CANVAS_W, int(CANVAS_W * scale))
            nh    = max(CANVAS_H, int(CANVAS_H * scale))
            img   = bg_pil.resize((nw, nh), Image.BILINEAR)
            left  = max(0, (nw - CANVAS_W) // 2)
            top   = max(0, (nh - CANVAS_H) // 2)
        else:  # pan_right / pan_left
            scale    = p1        # 1.06
            pan_px   = p2        # positive=right, negative=left
            nw       = int(CANVAS_W * scale)
            nh       = int(CANVAS_H * scale)
            img      = bg_pil.resize((nw, nh), Image.BILINEAR)
            base_x   = (nw - CANVAS_W) // 2
            x_offset = int(pan_px * frac)
            left     = max(0, min(nw - CANVAS_W, base_x + x_offset))
            top      = max(0, (nh - CANVAS_H) // 2)

        frame = img.crop((left, top, left + CANVAS_W, top + CANVAS_H))
        if frame.size != (CANVAS_W, CANVAS_H):
            frame = frame.resize((CANVAS_W, CANVAS_H), Image.BILINEAR)

        frame_rgba = frame.convert("RGBA")
        frame_rgba.alpha_composite(text_pil)
        return np.array(frame_rgba.convert("RGB"))

    return make_frame


# ---------------------------------------------------------------------------
# Asset index
# ---------------------------------------------------------------------------

def build_asset_index(manifest: dict, assets_dir: Path, product_id: str) -> dict:
    product_dir = assets_dir / product_id
    idx = {
        "main_image":        None,
        "product_images":    [],
        "detail_images":     [],
        "screenshot_main":   None,
        "screenshot_price":  None,
        "screenshot_rating": None,
        "screenshot_reviews":[],
        "scroll_asset":      [],
    }

    for entry in manifest.get("assets", []):
        atype = entry.get("asset_type", "")
        fpath = product_dir / entry["file_path"]

        if atype == "product_image":
            idx["product_images"].append((entry.get("index", 99), fpath))
            if entry.get("is_main"):
                idx["main_image"] = fpath
            else:
                idx["detail_images"].append((entry.get("index", 99), fpath))
        elif atype == "screenshot_main":
            idx["screenshot_main"] = fpath
        elif atype == "screenshot_price":
            idx["screenshot_price"] = fpath
        elif atype == "screenshot_rating":
            idx["screenshot_rating"] = fpath
        elif atype == "screenshot_review":
            idx["screenshot_reviews"].append(fpath)
        elif atype in ("scroll_video", "scroll_frame"):
            idx["scroll_asset"].append(fpath)

    idx["product_images"] = [p for _, p in sorted(idx["product_images"])]
    idx["detail_images"]  = [p for _, p in sorted(idx["detail_images"])]

    if not idx["main_image"] and idx["product_images"]:
        idx["main_image"] = idx["product_images"][0]

    return idx


def select_segment_assets(variant_id: str, idx: dict) -> list:
    v_offset = {"A": 0, "B": 1, "C": 2, "D": 3}[variant_id]
    pi = idx["product_images"]
    di = idx["detail_images"]
    rv = idx["screenshot_reviews"]

    def first_exists(*candidates):
        for c in candidates:
            if c is not None and isinstance(c, Path) and c.exists():
                return c
        return None

    def at(lst, i, fallback=None):
        return lst[i % len(lst)] if lst else fallback

    return [
        first_exists(idx["main_image"],        at(pi, 0)),
        first_exists(idx["screenshot_price"],  at(pi, 1), at(pi, 0)),
        first_exists(at(di, v_offset),         at(pi, 2), at(pi, 1)),
        first_exists(idx["screenshot_rating"], at(rv, 0), at(pi, 3),
                     pi[-1] if pi else None),
        first_exists(idx["main_image"],        at(pi, 0)),
    ]


# ---------------------------------------------------------------------------
# Variant generation
# ---------------------------------------------------------------------------

def generate_variant(variant_id: str, segs_config: list, asset_paths: list,
                     font_path: Path, font_sizes: dict, output_path: Path):
    kb_table = KEN_BURNS[variant_id]
    clips    = []

    for i, (seg, asset_path, motion) in enumerate(zip(segs_config, asset_paths, kb_table)):
        duration = float(seg["end"]) - float(seg["start"])

        if asset_path is None or not asset_path.exists():
            warn(f"Variant {variant_id} segment {i}: asset not found, using blank frame")
            bg_pil = Image.new("RGB", (CANVAS_W, CANVAS_H), "black")
        else:
            bg_pil = Image.fromarray(make_frame(Image.open(str(asset_path))))

        text_arr = build_text_layer(
            seg["text"], font_path, font_sizes[i], seg["color"], seg["position"]
        )
        text_pil = Image.fromarray(text_arr)

        fn = _make_frame_func(bg_pil, text_pil, motion, duration)
        clips.append(VideoClip(fn, duration=duration))

    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(
        str(output_path),
        fps=30,
        codec="libx264",
        audio=False,
        logger=None,
        ffmpeg_params=["-crf", "23", "-preset", "slow", "-pix_fmt", "yuv420p"],
    )


# ---------------------------------------------------------------------------
# QA
# ---------------------------------------------------------------------------

def run_ffprobe_qa(mp4_path: Path) -> tuple:
    failures = []

    if not mp4_path.exists():
        return False, ["PG-A: file does not exist"]

    size_kb = mp4_path.stat().st_size / 1024
    if not (500 <= size_kb <= 50 * 1024):
        failures.append(f"PG-B: size {size_kb:.0f}KB not in [500KB, 50MB]")

    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error",
             "-select_streams", "v:0",
             "-show_entries", "stream=width,height,r_frame_rate,codec_name",
             "-show_entries", "format=duration",
             "-of", "json", str(mp4_path)],
            capture_output=True, text=True, timeout=30,
        )
        probe  = json.loads(r.stdout)
        stream = (probe.get("streams") or [{}])[0]
        fmt    = probe.get("format", {})
    except Exception as e:
        return False, [f"ffprobe failed: {e}"]

    duration = float(fmt.get("duration") or stream.get("duration") or 0)
    if not (13.0 <= duration <= 17.0):
        failures.append(f"PG-C: duration {duration:.2f}s not in [13, 17]")

    w, h = stream.get("width", 0), stream.get("height", 0)
    if w != CANVAS_W or h != CANVAS_H:
        failures.append(f"PG-D: resolution {w}x{h} (expected {CANVAS_W}x{CANVAS_H})")

    codec = stream.get("codec_name", "")
    if codec != "h264":
        failures.append(f"PG-E: codec {codec!r} (expected h264)")

    fps_str = stream.get("r_frame_rate", "")
    if fps_str != "30/1":
        failures.append(f"PG-F: r_frame_rate {fps_str!r} (expected 30/1)")

    try:
        ra = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a",
             "-show_entries", "stream=codec_type", "-of", "json", str(mp4_path)],
            capture_output=True, text=True, timeout=15,
        )
        if json.loads(ra.stdout).get("streams"):
            failures.append("PG-G: audio stream present")
    except Exception:
        pass

    try:
        frame_tmp = mp4_path.parent / f"_qaframe_{mp4_path.stem}.png"
        subprocess.run(
            ["ffmpeg", "-y", "-ss", "0.5", "-i", str(mp4_path),
             "-vframes", "1", "-f", "image2", str(frame_tmp)],
            capture_output=True, timeout=30,
        )
        if frame_tmp.exists():
            arr  = np.array(Image.open(frame_tmp).convert("RGB"), dtype=np.float32)
            mean = float(arr.mean())
            frame_tmp.unlink(missing_ok=True)
            if mean < 5:
                failures.append(f"PG-H: first frame is black (brightness={mean:.1f})")
    except Exception:
        pass

    return len(failures) == 0, failures


def check_duplicate_hashes(paths: dict) -> list:
    hashes, warnings = {}, []
    for vid, path in paths.items():
        if path and path.exists():
            h = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    h.update(chunk)
            hashes[vid] = h.hexdigest()
    seen = {}
    for vid, hsh in hashes.items():
        if hsh in seen:
            warnings.append(f"PG-I: variant {vid} and {seen[hsh]} are identical — check config")
        else:
            seen[hsh] = vid
    return warnings


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Compose 4 silent TikTok MP4 variants from AliExpress product assets."
    )
    parser.add_argument("--product-id", required=True)
    parser.add_argument("--date",       required=True)
    parser.add_argument("--output-dir", default=str(BASE_DIR / "videos"))
    parser.add_argument("--assets-dir", default=str(BASE_DIR / "assets"))
    parser.add_argument("--data-dir",   default=str(BASE_DIR / "data"))
    parser.add_argument("--font-path",  default=None)
    parser.add_argument("--font-size",  type=int, default=BASE_FONT_SIZE)
    parser.add_argument("--variant",    default=None, choices=["A", "B", "C", "D"])
    args = parser.parse_args()

    # ---- Phase 0 ----
    info("Phase 0 — Setup and validation starting...")

    if not re.match(r"^[0-9A-Za-z_-]+$", args.product_id):
        print("❌ Error: --product-id must match [0-9A-Za-z_-]+")
        sys.exit(2)
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", args.date):
        print("❌ Error: --date must match YYYY-MM-DD")
        sys.exit(2)

    data_dir   = Path(args.data_dir)
    assets_dir = Path(args.assets_dir)
    output_dir = Path(args.output_dir)

    config_path   = data_dir / f"{args.product_id}-video-config.json"
    manifest_path = assets_dir / args.product_id / "manifest.json"

    if not config_path.exists():
        print(f"❌ Error: video-config.json not found: {config_path}")
        sys.exit(2)
    if not manifest_path.exists():
        print(f"❌ Error: manifest.json not found: {manifest_path}")
        sys.exit(2)

    output_dir.mkdir(parents=True, exist_ok=True)

    scale_f    = args.font_size / BASE_FONT_SIZE
    font_sizes = {k: max(18, int(v * scale_f)) for k, v in BASE_FONT_SIZES.items()}

    info(f"Phase 0 — Output: {output_dir}")

    # ---- Phase 1 ----
    info("Phase 1 — Font search starting...")
    font_path = find_font(args.font_path)
    if font_path is None:
        print("❌ No Hebrew-compatible font found. Install Noto Sans Hebrew or set --font-path.")
        sys.exit(2)
    info(f"Phase 1 — Font: using {font_path} (Hebrew verified)")

    # ---- Phase 2 ----
    info("Phase 2 — Loading video config...")
    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)

    variants_list = config.get("variants", [])
    variant_ids   = [v.get("id") for v in variants_list]
    if sorted(variant_ids) != ["A", "B", "C", "D"]:
        print(f"❌ PG-1: Expected variants A,B,C,D — found {variant_ids}")
        sys.exit(2)

    variants = {v["id"]: v for v in variants_list}
    cta_id   = config.get("cta_id", "")

    for vid, vdata in variants.items():
        segs = vdata.get("segments", [])
        if len(segs) != 5:
            print(f"❌ PG-2: Variant {vid} has {len(segs)} segments (expected 5)")
            sys.exit(2)
        if segs[0].get("start", -1) != 0:
            print(f"❌ PG-3: Variant {vid} segment 0 start={segs[0].get('start')}, expected 0")
            sys.exit(2)
        if cta_id and cta_id not in segs[4].get("text", ""):
            print(f"❌ PG-4: Variant {vid} segment 4 does not contain cta_id '{cta_id}'")
            sys.exit(2)
        total_dur = segs[4].get("end", 0)
        if not (13 <= total_dur <= 17):
            print(f"❌ PG-5: Variant {vid} total duration {total_dur}s not in [13, 17]")
            sys.exit(2)
        for j, seg in enumerate(segs):
            if seg.get("color") not in VALID_COLORS:
                print(f"❌ PG-6: Variant {vid} segment {j} color {seg.get('color')!r} invalid")
                sys.exit(2)
            if seg.get("position") not in VALID_POSITIONS:
                print(f"❌ PG-7: Variant {vid} segment {j} position {seg.get('position')!r} invalid")
                sys.exit(2)

    info("Phase 2 — Config loaded: 4 variants, 5 segments each")

    # ---- Phase 3 ----
    info("Phase 3 — Loading manifest...")
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    summary = manifest.get("summary", {})
    if not summary.get("qa_passed"):
        print("❌ PG-8: Manifest qa_passed is not true. Re-run generate_assets.py first.")
        sys.exit(2)
    img_count = summary.get("image_count", 0)
    if img_count < 5:
        print(f"❌ PG-9: Manifest has {img_count} product images (need >= 5)")
        sys.exit(2)

    asset_idx = build_asset_index(manifest, assets_dir, args.product_id)

    for name, val in [("screenshot_main",   asset_idx["screenshot_main"]),
                      ("screenshot_price",  asset_idx["screenshot_price"]),
                      ("screenshot_rating", asset_idx["screenshot_rating"])]:
        if val is None:
            warn(f"{name} not in manifest — segment will use product image fallback")

    all_seqs = [tuple(str(p) for p in select_segment_assets(v, asset_idx)) for v in "ABCD"]
    if len(set(all_seqs)) == 1:
        warn("Limited assets — variants will share images. Visual differentiation relies on hook text only.")

    info(f"Phase 3 — Manifest loaded: {img_count} product images, "
         f"{summary.get('screenshot_count', 0)} screenshots")

    # ---- Phase 4 ----
    variants_to_run = [args.variant] if args.variant else ["A", "B", "C", "D"]
    output_paths    = {}
    results         = {}

    for vid in variants_to_run:
        segs_config = variants[vid]["segments"]
        asset_paths = select_segment_assets(vid, asset_idx)
        out_path    = output_dir / f"{args.date}-product-{args.product_id}-{vid}.mp4"
        output_paths[vid] = out_path

        info(f"Phase 4 — Generating variant {vid}...")

        success       = False
        last_failures = []

        for attempt in range(1, 4):
            if out_path.exists():
                try:
                    out_path.unlink()
                except Exception:
                    pass
            try:
                generate_variant(vid, segs_config, asset_paths, font_path, font_sizes, out_path)
                passed, failures = run_ffprobe_qa(out_path)
                if passed:
                    success = True
                    break
                last_failures = failures
                info(f"Variant {vid} attempt {attempt}/3 failed: {failures[0]}. Retrying...")
                if out_path.exists():
                    out_path.unlink()
            except Exception as e:
                last_failures = [str(e)]
                info(f"Variant {vid} attempt {attempt}/3 exception: {e}. Retrying...")
                if out_path.exists():
                    try:
                        out_path.unlink()
                    except Exception:
                        pass

        if not success:
            info(f"Variant {vid} FAILED after 3 attempts — REQUIRES HUMAN REVIEW")

        results[vid] = (success, last_failures)

    # PG-I
    good_paths = {v: output_paths[v] for v in variants_to_run if results[v][0]}
    for w in check_duplicate_hashes(good_paths):
        warn(w)

    # ---- Phase 6 ----
    passed_count = sum(1 for v in variants_to_run if results[v][0])
    total_count  = len(variants_to_run)

    if passed_count == total_count:
        print(f"\n✅ Videos generated — {passed_count}/{total_count} variants ready")
        exit_code = 0
    elif passed_count >= 3:
        print(f"\n⚠️  Videos generated — {passed_count}/{total_count} variants ready")
        exit_code = 1
    else:
        print(f"\n❌ FAILED — REQUIRES HUMAN REVIEW")
        exit_code = 2

    for vid in variants_to_run:
        p         = output_paths[vid]
        ok, fails = results[vid]
        if ok and p.exists():
            size_mb = p.stat().st_size / (1024 * 1024)
            try:
                r   = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "json", str(p)],
                    capture_output=True, text=True, timeout=15,
                )
                dur = float(json.loads(r.stdout).get("format", {}).get("duration", 0))
                print(f"{p} ✅  ({dur:.0f}s, {size_mb:.1f}MB)")
            except Exception:
                print(f"{p} ✅  ({size_mb:.1f}MB)")
        else:
            print(f"{p} ⚠️  FAILED — REQUIRES HUMAN REVIEW")
            if fails:
                print(f"Reason for {vid} failure: {fails[0]}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
