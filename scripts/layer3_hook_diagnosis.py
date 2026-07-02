#!/usr/bin/env python3
"""
layer3_hook_diagnosis.py — ANALYZER_V3_SPEC.md Layer 3 (Hook Diagnosis).

Unlike Layer 7 (a pure numeric classifier), Layer 3's core question --
which of causes a/b/c/d/e/h is responsible for weak retention -- requires
actually looking at the opening frames and reading the hook text. That is
not something to fake with a rule-based heuristic pretending to be visual
analysis; it follows the SAME division of labor this project's own
pipeline already uses for STEP 11B/11C/11D (ffmpeg extracts frames, Claude
reads them and renders judgment). This script does ONLY the mechanical,
deterministic half:

  1. Reads the variant's first_2_second_retention from video_results.csv
     and classifies it STRONG/MARGINAL/WEAK/CRITICAL (same bands as C.F).
  2. Reads the hook segment's exact text/position from
     data/{pid}-video-config.json.
  3. Parses the upload package .md for this variant's STEP 11D score and
     verdict (the pre-launch PREDICTION, made before any real data existed).
  4. Extracts opening frames from the rendered MP4 via ffmpeg at
     0/0.5/1/1.5/2/2.5/3s -- OR, if ffmpeg is unavailable in this
     environment (confirmed missing 2026-07-02 -- shutil.which('ffmpeg')
     returned None), falls back to whichever of this product's *existing*
     STEP 11B/11D QA frames (scripts/qa_{pid}_{letter}_{s}s.png) already
     exist on disk, at whatever granularity those happen to be (typically
     0/1/3s, not sub-second) -- and says so explicitly rather than
     silently pretending fresh sub-second frames were extracted.
  5. Prints an evidence bundle for the agent to actually read the frames
     against, and a template for the a/b/c/d/e/h ratings -- this script
     does NOT fill those in itself.

Does NOT write to data/video_results.csv. Saves the evidence bundle (minus
the visual/textual judgment, which the agent fills in afterward) to
data/tiktok-analytics/product{pid}/{cta_code}_layer3_evidence.json.

Usage:
    python scripts/layer3_hook_diagnosis.py --product-id 008 --variant B
"""

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
VIDEOS_DIR = PROJECT_ROOT / "videos"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
ANALYTICS_DIR = DATA_DIR / "tiktok-analytics"
CSV_FILE = DATA_DIR / "video_results.csv"

RETENTION_BANDS = [
    (0.65, "STRONG"),
    (0.40, "MARGINAL"),
    (0.20, "WEAK"),
    (0.0, "CRITICAL"),
]

CAUSES = {
    "a": "Weak opening visual — flat catalog shot, no motion cue",
    "b": "Unclear product in first second",
    "c": "AliExpress catalog feel — reads as a marketplace thumbnail, not organic TikTok",
    "d": "Generic hook text — no specific number/problem/surprise",
    "e": "Hook–product mismatch — text promises something the image doesn't show",
    "h": "Non-native Hebrew phrasing — grammatically valid but reads as translated/stilted",
}


def classify_retention(value):
    if value is None:
        return "NO_DATA"
    for threshold, label in RETENTION_BANDS:
        if value >= threshold:
            return label
    return "CRITICAL"


def load_csv_row(variant):
    if not CSV_FILE.exists():
        return None
    with open(CSV_FILE, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("variant") == variant:
                return row
    return None


def load_hook_segment(pid, letter):
    cfg_path = DATA_DIR / f"{pid}-video-config.json"
    if not cfg_path.exists():
        return None
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    for vcfg in cfg.get("variants", []):
        if vcfg.get("id") == letter:
            segs = vcfg.get("segments", [])
            return segs[0] if segs else None
    return None


def find_upload_package(pid):
    matches = list(OUTPUT_DIR.glob(f"*-product-{pid}-upload_package.md"))
    return matches[0] if matches else None


def parse_step11d_score(pkg_path, letter):
    """
    Looks for a line like:
      **Upload order: 1st — LEAD VARIANT (STEP 11C: 9/10 | STEP 11D: PASS 9/10)**
    under the '## VARIANT {letter} —' heading, plus the STEP 11D KEY FINDINGS
    bullet for this letter if present. Returns dict or None -- never invents
    a score that isn't literally present in the file.
    """
    if not pkg_path or not pkg_path.exists():
        return None
    text = pkg_path.read_text(encoding="utf-8")

    heading_pat = rf"^##\s*VARIANT\s+{letter}\s*[—-].*$"
    m = re.search(heading_pat, text, flags=re.MULTILINE)
    if not m:
        return None
    section = text[m.end(): m.end() + 1500]

    score_m = re.search(r"STEP 11D:\s*(PASS|WARNING|FAIL)\s*(\d+)/10", section)
    result = {"verdict": None, "score": None, "key_finding": None}
    if score_m:
        result["verdict"] = score_m.group(1)
        result["score"] = int(score_m.group(2))

    finding_m = re.search(
        rf"^-\s*{letter}:\s*(.+)$", text, flags=re.MULTILINE
    )
    if finding_m:
        result["key_finding"] = finding_m.group(1).strip()

    return result if result["verdict"] else None


def extract_frames_ffmpeg(video_path, out_dir, cta_code):
    """Fine-grained 0/0.5/1/1.5/2/2.5/3s extraction. Returns list of paths,
    or [] if ffmpeg isn't available or extraction fails -- never guesses."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg or not video_path.exists():
        return []
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for t in [0, 0.5, 1, 1.5, 2, 2.5, 3]:
        out_path = out_dir / f"{cta_code}_opening_{t}s.png"
        try:
            subprocess.run(
                [ffmpeg, "-y", "-ss", str(t), "-i", str(video_path),
                 "-vframes", "1", str(out_path)],
                capture_output=True, timeout=30, check=True,
            )
            if out_path.exists():
                paths.append(out_path)
        except Exception:
            pass
    return paths


def find_existing_qa_frames(pid, letter):
    """
    Fallback when ffmpeg is unavailable: reuse this product's own
    pre-launch STEP 11B/11D QA frame extractions already on disk
    (scripts/qa_{pid}_{letter}_{s}s.png), at whatever seconds happen to
    exist -- confirmed present for 0/1/3/5/7/9/11/14s on at least product
    008 as of 2026-07-02. Returns {second: path}, only for seconds <= 3
    (the opening window this layer cares about).
    """
    found = {}
    for path in SCRIPTS_DIR.glob(f"qa_{pid}_{letter}_*s.png"):
        m = re.search(r"_(\d+)s\.png$", path.name)
        if m:
            second = int(m.group(1))
            if second <= 3:
                found[second] = path
    return found


def main():
    parser = argparse.ArgumentParser(description="Layer 3 hook diagnosis — evidence gathering")
    parser.add_argument("--product-id", required=True)
    parser.add_argument("--variant", required=True, help="single variant letter, e.g. B")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    pid = args.product_id.strip().zfill(3)
    letter = args.variant.upper()
    cta_code = f"{pid}{letter}"

    row = load_csv_row(cta_code)
    if row is None:
        print(f"ERROR: {cta_code} not found in video_results.csv")
        sys.exit(1)

    retention_raw = row.get("first_2_second_retention", "")
    retention_val = float(retention_raw) if retention_raw and retention_raw != "NOT_FOUND" else None
    retention_class = classify_retention(retention_val)

    hook_segment = load_hook_segment(pid, letter)
    pkg_path = find_upload_package(pid)
    step11d = parse_step11d_score(pkg_path, letter)

    video_path = None
    video_candidates = list(VIDEOS_DIR.glob(f"*-product-{pid}-{letter}.mp4"))
    if video_candidates:
        video_path = video_candidates[0]

    frame_dir = ANALYTICS_DIR / f"product{pid}" / "layer3_frames"
    frames = extract_frames_ffmpeg(video_path, frame_dir, cta_code) if video_path else []
    frame_source = "ffmpeg_fresh_subsecond"

    if not frames:
        existing = find_existing_qa_frames(pid, letter)
        frames = [existing[s] for s in sorted(existing)]
        frame_source = (
            "fallback_existing_qa_frames (ffmpeg unavailable in this "
            "environment — reused pre-launch STEP 11B/11D frames already "
            "on disk, integer-second granularity only, not sub-second)"
            if frames else "none_available"
        )

    evidence = {
        "variant": cta_code,
        "views": row.get("views"),
        "first_2_second_retention": retention_val,
        "retention_classification": retention_class,
        "hook_segment": hook_segment,
        "step11d_prelaunch_prediction": step11d,
        "frame_source": frame_source,
        "frame_paths": [str(p) for p in frames],
        "causes_to_rate": CAUSES,
        "causes_rated_by_agent": None,  # filled in after visual/textual review
        "step11d_divergence_note": None,  # filled in after comparing prediction vs frames
    }

    out_path = ANALYTICS_DIR / f"product{pid}" / f"{cta_code}_layer3_evidence.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=" * 62)
    print(f"LAYER 3 — HOOK DIAGNOSIS EVIDENCE — {cta_code}")
    print("=" * 62)
    print(f"Views: {evidence['views']}")
    print(f"first_2_second_retention: {retention_val}  ({retention_class})")
    print(f"Hook segment (0-{hook_segment.get('end') if hook_segment else '?'}s): "
          f"{hook_segment.get('text') if hook_segment else 'NOT FOUND'}")
    print(f"STEP 11D pre-launch prediction: {step11d}")
    print(f"Frame source: {frame_source}")
    print(f"Frames available for review: {[str(p) for p in frames]}")
    print()
    print("Causes to rate (LIKELY/POSSIBLE/UNLIKELY), each requires the agent")
    print("to actually read the frames + hook text -- not filled in by this script:")
    for k, v in CAUSES.items():
        print(f"  ({k}) {v}")
    print()
    print(f"Evidence bundle saved to: {out_path}")
    print("NOTE: nothing was written to data/video_results.csv.")


if __name__ == "__main__":
    main()
