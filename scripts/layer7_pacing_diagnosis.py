#!/usr/bin/env python3
"""
layer7_pacing_diagnosis.py — ANALYZER_V3_SPEC.md Layer 7 (Pacing / Retention
Diagnosis), first implementation of any Analyzer v3 layer.

The current analyzer's C.F only has two aggregate numbers per variant
(first_2_second_retention, average_watch_time) — enough to say "retention is
weak" but not where in the video viewers actually leave. This script adds
the missing capability the spec calls for: the full per-second retention
curve (via tiktok_analytics_collect._extract_full_retention_curve, a
mechanical generalization of the already-validated t=2s hover-read
technique), and classifies each variant into one of four problem types:

    OPENING_SEQUENCE_PROBLEM   — most of the total viewer loss happens in
                                 the opening window (default: first 3s)
    ENDING_PROBLEM             — a disproportionate share of the loss
                                 happens only in the last few seconds
    VIDEO_LENGTH_PROBLEM        — retention plateaus at a real value before
                                 the storyboard's own content even ends
                                 (per data/{pid}-video-config.json segment
                                 timings) — not a retention failure, a
                                 pacing/length mismatch
    MID_VIDEO_PACING_PROBLEM   — the default: loss is spread through the
                                 middle of the video, matching neither of
                                 the above

SCOPE LIMIT, fixed 2026-07-02 after a real methodology challenge: this
layer's ONLY input is the retention curve — WHEN viewers stop watching. It
has never looked at a single video frame, so OPENING_SEQUENCE_PROBLEM and
ENDING_PROBLEM are TEMPORAL findings only, not causal ones. The classifier
was originally named "HOOK_PROBLEM" for an early drop, which smuggled in an
unsupported claim that the hook concept/wording specifically was at fault.
Hook concept, product-reveal timing, first-frame quality, movement,
editing, and text overlays all live inside the same opening seconds and
this layer cannot tell them apart — that requires Layer 3 (Hook Diagnosis)
and Layer 5 (Video/Creative Execution) to actually inspect the frames,
neither implemented yet. Every OPENING_SEQUENCE_PROBLEM / ENDING_PROBLEM
result carries an explicit `cause_unresolved_note` in its evidence saying
exactly this — never presented as a finished diagnosis.

Does NOT write to data/video_results.csv and does NOT touch
tiktok_analytics_collect.collect_one_variant()'s own flow — this is a
standalone diagnostic tool, consistent with how tiktok_collect_qa.py and
analyze_qa.py stand alone from the collector/analyzer they check. Curve
data is cached to
data/tiktok-analytics/product{pid}/{cta_code}_retention_curve.json (the
live extraction takes ~13s/variant; re-runs reuse the cache unless
--refresh is passed).

Usage:
    python scripts/layer7_pacing_diagnosis.py --product-id 008 --variant B
    python scripts/layer7_pacing_diagnosis.py --product-id 008            # all variants of 008
    python scripts/layer7_pacing_diagnosis.py --product-id 008 --variant B --refresh
"""

import argparse
import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tiktok_analytics_collect import (
    sync_playwright, launch_with_session, check_session_valid,
    detect_all_products, _open_video_detail_direct, _find_video_id_via_posts_tab,
    click_analytics_tab, scroll_container, _extract_full_retention_curve,
    CSV_FILE, DATA_DIR, ANALYTICS_DIR,
)

# ANALYZER_V3_SPEC.md Confidence Rules — proposed MIN_CONFIDENT_VIEWS.
MIN_CONFIDENT_VIEWS = 50
# Matches the existing STEP 11B/3A opening-frame sampling convention (0,1,3s).
# Named for the TIME WINDOW, not for "the hook" as a creative element -- this
# function has no way to know if the hook specifically is what's in that
# window versus product-reveal timing, first-frame quality, editing, etc.
OPENING_WINDOW_END = 3
ENDING_WINDOW = 3


def _curve_path(pid, cta_code):
    return ANALYTICS_DIR / f"product{pid}" / f"{cta_code}_retention_curve.json"


def load_video_config_segments(pid, letter):
    cfg_path = DATA_DIR / f"{pid}-video-config.json"
    if not cfg_path.exists():
        return None
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    for vcfg in cfg.get("variants", []):
        if vcfg.get("id") == letter:
            return vcfg.get("segments", [])
    return None


def load_csv_row(variant):
    if not CSV_FILE.exists():
        return None
    with open(CSV_FILE, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("variant") == variant:
                return row
    return None


def classify_curve(curve, duration_s, segments=None):
    """
    Returns (classification, evidence_dict). Every field in evidence is a
    number or timestamp pulled directly from the curve — no invented
    reasoning, per ANALYZER_V3_SPEC.md's Evidence Requirement.

    IMPORTANT SCOPE LIMIT (fixed 2026-07-02, after a real methodology
    challenge): this function's ONLY input is the retention curve -- WHEN
    viewers stop watching. It has never looked at a single video frame,
    storyboard segment, or text overlay, so it cannot and must not name a
    specific creative cause. The classification below was originally named
    "HOOK_PROBLEM" for an early drop, which smuggled in an unsupported
    causal claim (that the hook concept/wording specifically is at fault)
    on top of the one thing this function actually measured (a temporal
    fact: most loss happens early). Hook concept, product-reveal timing,
    first-frame visual quality, movement, editing, and text overlays all
    live inside the same first few seconds and this function cannot tell
    them apart -- that requires Layer 3 (Hook Diagnosis) and Layer 5
    (Video/Creative Execution) to actually inspect the frames, neither of
    which is implemented yet. Renamed to OPENING_SEQUENCE_PROBLEM: a
    temporal-only finding, not a diagnosis of which component failed.
    """
    if not curve:
        return "INSUFFICIENT_DATA", {"reason": "no curve points extracted"}

    # t=0 is always 100% by platform definition (not measured, a fact).
    # Keys must be normalized to int: JSON round-tripping through the curve
    # cache file turns int dict keys into strings, which a fresh live
    # extraction never has -- confirmed by a live TypeError on a cached-file
    # run, 2026-07-02, that a same-session fresh-extraction run didn't hit.
    points = {0: 100.0}
    points.update({int(k): v for k, v in curve.items()})
    final_second = max(points)
    final_value = points[final_second]
    total_drop = 100.0 - final_value

    if total_drop <= 1.0:
        return "NO_DROP_DETECTED", {
            "final_second": final_second,
            "final_retention_pct": round(final_value, 1),
        }

    opening_second = max((s for s in points if s <= OPENING_WINDOW_END), default=0)
    opening_value = points[opening_second]
    drop_by_opening_end = 100.0 - opening_value
    opening_share = drop_by_opening_end / total_drop

    ending_start = max(0, duration_s - ENDING_WINDOW)
    ending_second = min((s for s in points if s >= ending_start), default=final_second)
    ending_value = points[ending_second]
    drop_in_ending = max(0.0, ending_value - final_value)
    ending_share = drop_in_ending / total_drop

    evidence = {
        "curve": points,
        "duration_s": duration_s,
        "total_drop_pct": round(total_drop, 1),
        "opening_window_end_s": opening_second,
        "drop_by_opening_window_end_pct": round(drop_by_opening_end, 1),
        "opening_window_share_of_total_drop": round(opening_share, 2),
        "ending_window_start_s": ending_second,
        "drop_in_ending_window_pct": round(drop_in_ending, 1),
        "ending_share_of_total_drop": round(ending_share, 2),
        "final_retention_pct": round(final_value, 1),
        "cause_unresolved_note": None,  # filled in below whenever a classification needs one
    }

    # VIDEO_LENGTH_PROBLEM: retention plateaus at a real (non-trivial) value
    # at/before where the storyboard's OWN content ends — cross-referenced
    # against data/{pid}-video-config.json, not inferred from the curve alone.
    # This one IS a supported causal claim -- it's not "something in the
    # ending is wrong," it's the specific, checkable fact that the video
    # keeps running after the storyboard's own last segment ends.
    if segments:
        content_end = max((seg.get("end", 0) for seg in segments), default=duration_s)
        if content_end < duration_s - 1:
            tail_points = {s: v for s, v in points.items() if s >= content_end}
            if len(tail_points) >= 2:
                tail_values = list(tail_points.values())
                tail_spread = max(tail_values) - min(tail_values)
                if tail_spread <= 3 and min(tail_values) > 15:
                    evidence["content_ends_at_s"] = content_end
                    evidence["video_duration_s"] = duration_s
                    evidence["tail_retention_pct"] = round(min(tail_values), 1)
                    return "VIDEO_LENGTH_PROBLEM", evidence

    if opening_share >= 0.5:
        evidence["cause_unresolved_note"] = (
            "Temporal finding only: most loss is concentrated in the opening "
            f"{opening_second}s. WHICH component is responsible -- hook concept, "
            "product-reveal timing, first-frame quality, movement, editing, or "
            "text overlays -- is not determined by this layer. Requires Layer 3 "
            "(Hook Diagnosis) and Layer 5 (Video/Creative Execution)."
        )
        return "OPENING_SEQUENCE_PROBLEM", evidence
    if ending_share >= 0.4 and drop_in_ending >= 5:
        evidence["cause_unresolved_note"] = (
            "Temporal finding only: a disproportionate share of loss happens in "
            "the final seconds. Whether this is CTA placement, pacing fatigue, or "
            "something else is not determined by this layer. Requires Layer 5 "
            "(Video/Creative Execution) and Layer 8 (CTA/Buyer Intent)."
        )
        return "ENDING_PROBLEM", evidence
    return "MID_VIDEO_PACING_PROBLEM", evidence


def diagnose_variant(page, pid, letter, video_id_hint, refresh):
    cta_code = f"{pid}{letter}"
    curve_file = _curve_path(pid, cta_code)

    if curve_file.exists() and not refresh:
        print(f"  [{cta_code}] using cached curve: {curve_file}")
        curve_data = json.loads(curve_file.read_text(encoding="utf-8"))
    else:
        print(f"  [{cta_code}] extracting live retention curve...")
        video_id = video_id_hint or _find_video_id_via_posts_tab(page, cta_code)
        if not video_id:
            print(f"  [{cta_code}] could not resolve a video_id — skipping")
            return None
        opened = _open_video_detail_direct(page, video_id)
        if not opened:
            print(f"  [{cta_code}] could not open detail page — skipping")
            return None
        time.sleep(1)
        click_analytics_tab(page)
        for _ in range(5):
            scroll_container(page, 0.9)
            time.sleep(0.6)
        curve_data = _extract_full_retention_curve(page)
        if curve_data is None:
            print(f"  [{cta_code}] could not locate retention chart — skipping")
            return None
        curve_file.parent.mkdir(parents=True, exist_ok=True)
        curve_file.write_text(json.dumps(curve_data, indent=2), encoding="utf-8")
        print(f"  [{cta_code}] curve saved to {curve_file}")

    row = load_csv_row(cta_code)
    views = int(row["views"]) if row and str(row.get("views", "")).isdigit() else None
    segments = load_video_config_segments(pid, letter)

    classification, evidence = classify_curve(
        curve_data.get("curve", {}), curve_data.get("duration_s", 15), segments
    )

    low_confidence = views is not None and views < MIN_CONFIDENT_VIEWS
    return {
        "variant": cta_code,
        "views": views,
        "low_confidence": low_confidence,
        "classification": classification,
        "evidence": evidence,
    }


def print_report(results):
    print()
    print("=" * 62)
    print("LAYER 7 — PACING / RETENTION DIAGNOSIS")
    print("=" * 62)
    for r in results:
        if r is None:
            continue
        conf_tag = (
            f" [LOW CONFIDENCE — n={r['views']} views, below {MIN_CONFIDENT_VIEWS}]"
            if r["low_confidence"] else ""
        )
        print(f"\n{r['variant']}  (n={r['views']} views){conf_tag}")
        print(f"  Classification: {r['classification']}")
        ev = r["evidence"]
        if "curve" in ev:
            curve_str = ", ".join(f"{s}s={v:.0f}%" for s, v in sorted(ev["curve"].items()))
            print(f"  Curve: {curve_str}")
            ending_span = ev.get("duration_s", 0) - ev.get("ending_window_start_s", 0)
            print(
                f"  Total drop: {ev.get('total_drop_pct')}%  |  "
                f"drop by {ev.get('opening_window_end_s')}s: {ev.get('drop_by_opening_window_end_pct')}% "
                f"({ev.get('opening_window_share_of_total_drop', 0)*100:.0f}% of total drop)  |  "
                f"drop in last {ending_span}s: {ev.get('drop_in_ending_window_pct')}% "
                f"({ev.get('ending_share_of_total_drop', 0)*100:.0f}% of total drop)"
            )
            if "content_ends_at_s" in ev:
                print(
                    f"  Storyboard content ends at {ev['content_ends_at_s']}s but video "
                    f"runs {ev['video_duration_s']}s; retention plateaus at "
                    f"{ev['tail_retention_pct']}% through the extra runtime."
                )
            if ev.get("cause_unresolved_note"):
                print(f"  ⚠ CAUSE NOT YET DETERMINED: {ev['cause_unresolved_note']}")
        else:
            print(f"  Evidence: {ev}")
    print()
    print("=" * 62)


def main():
    parser = argparse.ArgumentParser(description="Layer 7 pacing/retention diagnosis")
    parser.add_argument("--product-id", required=True, help="e.g. 008")
    parser.add_argument("--variant", help="single variant letter, e.g. B (default: all variants)")
    parser.add_argument(
        "--refresh", action="store_true",
        help="re-extract live even if a cached curve already exists",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    pid = args.product_id.strip().zfill(3)
    products = detect_all_products({pid})
    if pid not in products:
        print(f"ERROR: product {pid} not found")
        sys.exit(1)

    letters = [args.variant.upper()] if args.variant else sorted(products[pid]["variants"].keys())

    # Skip launching a browser entirely if every requested variant already
    # has a cached curve and --refresh wasn't passed.
    needs_live = args.refresh or any(
        not _curve_path(pid, f"{pid}{letter}").exists() for letter in letters
    )

    results = []
    if needs_live:
        with sync_playwright() as pw:
            browser, context = launch_with_session(pw)
            page = context.new_page()
            print("Verifying session...")
            if not check_session_valid(page):
                print("ERROR: session expired. Run: python scripts/tiktok_session_login.py")
                sys.exit(1)
            print("Session valid.\n")

            for letter in letters:
                vinfo = products[pid]["variants"].get(letter)
                if not vinfo:
                    continue
                results.append(
                    diagnose_variant(page, pid, letter, vinfo.get("video_id"), args.refresh)
                )

            browser.close()
    else:
        print("All requested variants already have cached curves — no live session needed.\n")
        for letter in letters:
            vinfo = products[pid]["variants"].get(letter)
            if not vinfo:
                continue
            results.append(diagnose_variant(None, pid, letter, None, False))

    print_report(results)
    print(
        "\nNOTE: nothing was written to data/video_results.csv — curve data is cached "
        f"to data/tiktok-analytics/product{pid}/*_retention_curve.json only."
    )


if __name__ == "__main__":
    main()
