#!/usr/bin/env python3
"""
validate_click_fix.py — One-time validation for the _open_video_detail
click-target fix in tiktok_analytics_collect.py.

Runs the collection pipeline for exactly ONE known variant (008B) using the
fixed code path, prints the extracted metrics, and saves a screenshot — but
does NOT write anything to data/video_results.csv. Use this to confirm the
fix actually reaches the video detail/analytics page before running a full
historical backfill.
"""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tiktok_analytics_collect import (
    sync_playwright, launch_with_session, check_session_valid,
    detect_all_products, collect_one_variant, ANALYTICS_DIR,
)

TARGET_PID = "008"
TARGET_LETTER = "B"
TARGET_VARIANT = f"{TARGET_PID}{TARGET_LETTER}"

# Known-good baseline from the existing CONFIRMED row, for comparison.
# Views may have grown naturally since; likes/comments should match closely.
KNOWN_VIEWS, KNOWN_LIKES, KNOWN_COMMENTS = 114, 1, 0


def main():
    print("=" * 62)
    print(f"SINGLE-VARIANT VALIDATION — {TARGET_VARIANT}")
    print("=" * 62)

    products = detect_all_products({TARGET_PID})
    if TARGET_PID not in products or TARGET_LETTER not in products[TARGET_PID]["variants"]:
        print(f"ERROR: {TARGET_VARIANT} not found in detected products.")
        sys.exit(1)

    vinfo = products[TARGET_PID]["variants"][TARGET_LETTER]
    cta_code = vinfo["cta_code"]
    print(f"Target: {TARGET_VARIANT}  (cta_code={cta_code})")
    print(f"Known-good baseline (existing CSV row): views={KNOWN_VIEWS} likes={KNOWN_LIKES} comments={KNOWN_COMMENTS}")
    print()

    with sync_playwright() as pw:
        browser, context = launch_with_session(pw)
        page = context.new_page()

        print("Verifying session...")
        if not check_session_valid(page):
            print("ERROR: Session expired. Run: python scripts/tiktok_session_login.py")
            browser.close()
            sys.exit(1)
        print("Session valid.\n")

        raw = collect_one_variant(
            page, cta_code,
            skip_count=vinfo.get("bare_index") or 0,
            caption_search_text=vinfo.get("caption_search_text", ""),
            video_id=vinfo.get("video_id"),
        )

        browser.close()

    print()
    print("=" * 62)
    print("RESULT")
    print("=" * 62)
    print(f"not_found:       {raw.get('not_found')}")
    print(f"detail_opened:   {raw.get('_detail_opened')}")
    print(f"views:           {raw.get('views')!r}   (expected ~{KNOWN_VIEWS}, natural growth OK)")
    print(f"likes:           {raw.get('likes')!r}   (expected {KNOWN_LIKES})")
    print(f"comments:        {raw.get('comments')!r}   (expected {KNOWN_COMMENTS})")
    print(f"saves:                     {raw.get('saves')!r}")
    print(f"shares:                    {raw.get('shares')!r}")
    print(f"average_watch_time:        {raw.get('average_watch_time')!r}")
    print(f"retention_rate:            {raw.get('retention_rate')!r}")
    print(f"watched_full_video_rate:   {raw.get('watched_full_video_rate')!r}")
    print(f"first_2_second_retention:  {raw.get('first_2_second_retention')!r}")
    ss_path = ANALYTICS_DIR / f"product{cta_code[:3]}" / f"{cta_code}_analytics.png"
    print(f"\nScreenshot saved to: {ss_path}")
    print("NOTE: nothing was written to data/video_results.csv — this is a read-only validation run.")


if __name__ == "__main__":
    main()
