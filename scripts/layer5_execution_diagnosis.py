#!/usr/bin/env python3
"""
layer5_execution_diagnosis.py — ANALYZER_V3_SPEC.md Layer 5 (Video /
Creative Execution).

Determines whether the RENDERED VIDEO ITSELF is responsible for the
OPENING_SEQUENCE_PROBLEM Layer 7 found and Layer 3 partially explained, by
measuring the actual render against its own plan — not by looking at it and
guessing:

  - THE PLAN: data/{pid}-video-config.json segment timings/text/position/
    asset, and the Ken Burns motion table parsed directly out of
    generate_videos.py's own source text via ast.literal_eval (not
    hand-copied, so it can't silently drift from the real code; not
    imported, since this environment's generate_videos.py pulls in numpy/
    PIL/moviepy, none of which are installed here).
  - THE EXECUTION: the actual rendered MP4, via ffmpeg frame extraction at
    every segment boundary plus intermediate points, PLUS a real pixel-
    difference metric (SSIM, via ffmpeg's own ssim filter) between frames —
    not a visual "look and compare."

REAL CORRECTION TO LAYER 3, CONFIRMED 2026-07-02: Layer 3's agents visually
compared 008B's opening frames and rated cause (a) "no motion cue" LIKELY,
describing the frames as "pixel-identical." A real SSIM measurement between
the SAME frames shows a clean, monotonically decreasing trend relative to
0s (0.927 @0.5s, 0.896 @1s, 0.871 @1.5s, 0.854 @2s, 0.843 @2.5s) — exactly
the signature of a real, continuously-applied pan, matching
generate_videos.py's own Ken Burns table for variant B segment 0
(pan_left, -30px over the 3s segment). The eye test missed real motion a
pixel diff caught. This does NOT mean the opening is fine — 30px over 3s on
a 1080px canvas may still be too subtle to function as a scroll-stopping
cue, especially since displacement is ~0px at t=0 and only ~10px by t=1s —
but it changes the diagnosis from "no motion was executed" (an execution
failure) to "motion was executed exactly as planned, but the plan's
magnitude may be too subtle" (a planning/calibration question). Every
Layer 5 run checks this the same rigorous way rather than assuming either
answer.

Distinguishes explicitly, per instruction:
  PLANNING    — is the segment/motion PLAN itself (config + Ken Burns
                table) reasonable, independent of whether it rendered
                correctly?
  EXECUTION   — does the actual rendered motion match what was planned
                (magnitude, direction), measured via SSIM trend?
  EDITING     — how abrupt are the cuts between segments (SSIM at each
                boundary — a hard cut is this pipeline's actual design,
                not inherently a defect; what matters is whether a cut
                coincides with a real viewer-loss spike per Layer 7)
  PACING      — do segment lengths line up with where retention actually
                drops (cross-referenced against Layer 7's cached curve)?
  Text timing — does overlay text actually appear/disappear at the
                config's specified start/end (checked from frames at each
                boundary — agent-verified, this script only extracts)

Product-reveal-timing, first-frame quality, movement (qualitative read),
and overall creative quality still require the agent to actually look at
the frames — this script does not fake that, same division of labor as
Layer 3.

Does NOT write to data/video_results.csv. Saves evidence to
data/tiktok-analytics/product{pid}/{cta_code}_layer5_evidence.json.

Usage:
    python scripts/layer5_execution_diagnosis.py --product-id 008 --variant B
"""

import argparse
import ast
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
VIDEOS_DIR = PROJECT_ROOT / "videos"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
ANALYTICS_DIR = DATA_DIR / "tiktok-analytics"

# SSIM below this between consecutive within-segment frames suggests real,
# meaningful motion is occurring (not just PNG/encoding noise, which stays
# very close to 1.0). Calibrated against 008B's confirmed real pan: 0.927
# at just 0.5s in was already a clear signal.
MOTION_SSIM_THRESHOLD = 0.97


def parse_ken_burns_table():
    """
    Extracts KEN_BURNS = {...} directly from generate_videos.py's source
    text via ast.literal_eval -- never hand-copied, never imported (that
    module needs numpy/PIL/moviepy, none of which are installed in this
    environment).
    """
    src = (SCRIPTS_DIR / "generate_videos.py").read_text(encoding="utf-8")
    m = re.search(r"KEN_BURNS\s*=\s*(\{.*?\n\})", src, flags=re.DOTALL)
    if not m:
        return None
    try:
        return ast.literal_eval(m.group(1))
    except Exception as exc:
        print(f"  WARNING: could not parse KEN_BURNS table: {exc}")
        return None


def load_segments(pid, letter):
    cfg_path = DATA_DIR / f"{pid}-video-config.json"
    if not cfg_path.exists():
        return None
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    for vcfg in cfg.get("variants", []):
        if vcfg.get("id") == letter:
            return vcfg.get("segments", [])
    return None


def find_video(pid, letter):
    matches = list(VIDEOS_DIR.glob(f"*-product-{pid}-{letter}.mp4"))
    return matches[0] if matches else None


def extract_frame(video_path, t, out_path):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return False
    try:
        subprocess.run(
            [ffmpeg, "-y", "-ss", str(t), "-i", str(video_path),
             "-vframes", "1", str(out_path)],
            capture_output=True, timeout=30, check=True,
        )
        return out_path.exists()
    except Exception:
        return False


def ssim(frame_a, frame_b):
    """Real pixel-difference metric via ffmpeg's own ssim filter. Returns
    the 'All:' SSIM value (1.0 = identical), or None on failure."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return None
    try:
        result = subprocess.run(
            [ffmpeg, "-i", str(frame_a), "-i", str(frame_b), "-lavfi", "ssim", "-f", "null", "-"],
            capture_output=True, timeout=30, text=True,
        )
        m = re.search(r"All:([\d.]+)", result.stderr)
        return float(m.group(1)) if m else None
    except Exception:
        return None


def load_retention_curve(pid, cta_code):
    path = ANALYTICS_DIR / f"product{pid}" / f"{cta_code}_retention_curve.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        curve = {int(k): v for k, v in data.get("curve", {}).items()}
        curve[0] = 100.0
        return {"duration_s": data.get("duration_s"), "curve": curve}
    except Exception:
        return None


def load_layer3_evidence(pid, cta_code):
    path = ANALYTICS_DIR / f"product{pid}" / f"{cta_code}_layer3_evidence.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def analyze_segment_motion(video_path, frame_dir, cta_code, seg_idx, start, end):
    """
    Extracts 4 evenly-spaced frames within [start, end) and computes SSIM of
    each against the segment's own first frame. A monotonically decreasing
    trend (each frame less similar to frame 0 than the last) is the real
    signature of continuous motion; near-1.0 throughout means genuinely
    static; erratic (non-monotonic) small variation is likely encoding
    noise, not real motion.
    """
    duration = end - start
    fracs = [0.0, 0.33, 0.67, 0.95]
    timestamps = [start + duration * f for f in fracs]
    paths = []
    for i, t in enumerate(timestamps):
        out_path = frame_dir / f"{cta_code}_seg{seg_idx}_{i}.png"
        if extract_frame(video_path, t, out_path):
            paths.append((t, out_path))

    if len(paths) < 2:
        return {"error": "could not extract enough frames"}

    base_t, base_path = paths[0]
    ssim_values = []
    for t, path in paths[1:]:
        s = ssim(base_path, path)
        ssim_values.append({"t": round(t, 2), "ssim_vs_segment_start": s})

    values_only = [v["ssim_vs_segment_start"] for v in ssim_values if v["ssim_vs_segment_start"] is not None]
    is_monotonic_decreasing = all(
        values_only[i] >= values_only[i + 1] for i in range(len(values_only) - 1)
    ) if len(values_only) >= 2 else None

    min_ssim = min(values_only) if values_only else None
    if min_ssim is None:
        motion_verdict = "UNKNOWN"
    elif min_ssim >= MOTION_SSIM_THRESHOLD and (is_monotonic_decreasing is False or is_monotonic_decreasing is None):
        motion_verdict = "STATIC_NO_REAL_MOTION"
    elif min_ssim < MOTION_SSIM_THRESHOLD and is_monotonic_decreasing:
        motion_verdict = "REAL_GRADUAL_MOTION_CONFIRMED"
    elif min_ssim < MOTION_SSIM_THRESHOLD and not is_monotonic_decreasing:
        motion_verdict = "SOME_DIFFERENCE_BUT_NOT_CLEAN_MOTION_TREND"
    else:
        motion_verdict = "STATIC_NO_REAL_MOTION"

    return {
        "segment_start": start, "segment_end": end,
        "ssim_trend_vs_segment_start": ssim_values,
        "monotonic_decrease": is_monotonic_decreasing,
        "min_ssim": min_ssim,
        "motion_verdict": motion_verdict,
        "frame_paths": [str(p) for _, p in paths],
    }


def analyze_transition(video_path, frame_dir, cta_code, seg_idx, boundary_t):
    """SSIM immediately before vs. immediately after a segment boundary —
    quantifies cut abruptness. Low SSIM is EXPECTED (this pipeline concatenates
    raw clips, no crossfade by design) — not itself a defect. What matters is
    whether Layer 7's retention curve shows a real viewer-loss spike at this
    exact second."""
    before_path = frame_dir / f"{cta_code}_boundary{seg_idx}_before.png"
    after_path = frame_dir / f"{cta_code}_boundary{seg_idx}_after.png"
    ok_before = extract_frame(video_path, max(0, boundary_t - 0.1), before_path)
    ok_after = extract_frame(video_path, boundary_t + 0.1, after_path)
    if not (ok_before and ok_after):
        return {"error": "could not extract boundary frames"}
    s = ssim(before_path, after_path)
    return {
        "boundary_s": boundary_t,
        "ssim_across_cut": s,
        "before_frame": str(before_path),
        "after_frame": str(after_path),
    }


def find_steepest_drop(curve_data):
    if not curve_data or not curve_data.get("curve"):
        return None
    curve = curve_data["curve"]
    seconds = sorted(curve)
    drops = []
    for i in range(len(seconds) - 1):
        s0, s1 = seconds[i], seconds[i + 1]
        drop = curve[s0] - curve[s1]
        drops.append((s1, drop))
    if not drops:
        return None
    steepest = max(drops, key=lambda d: d[1])
    return {"second": steepest[0], "drop_pct": steepest[1], "all_drops": drops}


def main():
    parser = argparse.ArgumentParser(description="Layer 5 execution diagnosis — evidence gathering")
    parser.add_argument("--product-id", required=True)
    parser.add_argument("--variant", required=True)
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    pid = args.product_id.strip().zfill(3)
    letter = args.variant.upper()
    cta_code = f"{pid}{letter}"

    segments = load_segments(pid, letter)
    if not segments:
        print(f"ERROR: no segments found for {cta_code}")
        sys.exit(1)

    video_path = find_video(pid, letter)
    if not video_path:
        print(f"ERROR: no rendered video found for {cta_code}")
        sys.exit(1)

    ken_burns = parse_ken_burns_table()
    planned_motion = ken_burns.get(letter) if ken_burns else None

    frame_dir = ANALYTICS_DIR / f"product{pid}" / "layer5_frames"
    frame_dir.mkdir(parents=True, exist_ok=True)

    segment_analyses = []
    transition_analyses = []
    for i, seg in enumerate(segments):
        start, end = seg.get("start"), seg.get("end")
        planned = planned_motion[i] if planned_motion and i < len(planned_motion) else None
        analysis = analyze_segment_motion(video_path, frame_dir, cta_code, i, start, end)
        analysis["planned_ken_burns"] = planned
        analysis["config_text"] = seg.get("text")
        analysis["config_position"] = seg.get("position")
        analysis["config_asset"] = seg.get("asset")
        segment_analyses.append(analysis)

        if i > 0:
            trans = analyze_transition(video_path, frame_dir, cta_code, i, start)
            transition_analyses.append(trans)

    retention_curve = load_retention_curve(pid, cta_code)
    steepest_drop = find_steepest_drop(retention_curve)
    layer3_evidence = load_layer3_evidence(pid, cta_code)

    evidence = {
        "variant": cta_code,
        "video_path": str(video_path),
        "segments_plan": segments,
        "ken_burns_planned_motion": planned_motion,
        "segment_motion_analysis": segment_analyses,
        "transition_analysis": transition_analyses,
        "retention_curve": retention_curve,
        "steepest_retention_drop": steepest_drop,
        "layer3_cause_a_rating": (
            (layer3_evidence or {}).get("causes_rated_by_agent", {}).get("a")
            if layer3_evidence else None
        ),
        "dimensions_requiring_agent_review": {
            "planning_quality": None,       # is the plan itself (config+KB table) reasonable?
            "product_reveal_timing": None,  # when does the product become the visual focus?
            "first_frame_quality": None,    # technical competence (resolution/framing/exposure)
            "overall_creative_quality": None,
            "text_timing_verified": None,   # does text actually appear/disappear at config times, per frames?
        },
    }

    out_path = ANALYTICS_DIR / f"product{pid}" / f"{cta_code}_layer5_evidence.json"
    out_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    print("=" * 62)
    print(f"LAYER 5 — VIDEO/CREATIVE EXECUTION EVIDENCE — {cta_code}")
    print("=" * 62)
    for i, a in enumerate(segment_analyses):
        print(f"\nSegment {i} [{a['segment_start']}-{a['segment_end']}s]: "
              f"planned={a.get('planned_ken_burns')}")
        print(f"  Motion verdict: {a.get('motion_verdict')}  "
              f"(min_ssim={a.get('min_ssim')}, monotonic_decrease={a.get('monotonic_decrease')})")
        for v in a.get("ssim_trend_vs_segment_start", []):
            print(f"    t={v['t']}s  ssim_vs_start={v['ssim_vs_segment_start']}")
    print("\nTransitions:")
    for t in transition_analyses:
        print(f"  boundary@{t.get('boundary_s')}s  ssim_across_cut={t.get('ssim_across_cut')}")
    print(f"\nSteepest single-second retention drop: {steepest_drop}")
    print(f"\nLayer 3's cause (a) rating for reference: {evidence['layer3_cause_a_rating']}")
    print(f"\nEvidence saved to: {out_path}")
    print("Remaining qualitative fields (planning_quality, product_reveal_timing, "
          "first_frame_quality, overall_creative_quality, text_timing_verified) "
          "left null for agent review — not filled in by this script.")
    print("NOTE: nothing was written to data/video_results.csv.")


if __name__ == "__main__":
    main()
