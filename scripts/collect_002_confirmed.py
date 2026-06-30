#!/usr/bin/env python3
"""
collect_002_confirmed.py — Collect analytics for Product 002 A/B/C/D using the
identity mapping confirmed via visual hook-text matching (see
output/identify_002/ screenshots and PROJECT_STATUS.md).

CONFIRMED MAPPING (visual match against data/002-video-config.json hook text,
each variant's hook is unique and baked into the video pixels at 0-2s):
  video 7651330918107385109 -> D  ("כולן מדברות על זה ואני..." partial match + elimination)
  video 7651330347824696596 -> C  ("מצאתי את הפתרון לבעיה שכולנו מכירות" - exact match)
  video 7651327807460642068 -> B  ("ראיתי את זה בטיקטוק ולא האמנתי שזה קיים..." - exact match)
  video 7651320643010514197 -> A  ("לא תאמיני כמה זה עולה בעלי אקספרס..." - exact match)

This bypasses caption/CTA-based search entirely (proven unreliable) and
navigates directly to each confirmed video URL in TikTok Studio to scrape
Views/Likes/Comments from the row, using the same elementFromPoint technique
proven in tiktok_analytics_collect.py.
"""

import json
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output" / "identify_002"
SESSION_FILE = DATA_DIR / "tiktok-session.json"

DESKTOP_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

CONFIRMED_MAPPING = {
    "7651330918107385109": "D",
    "7651330347824696596": "C",
    "7651327807460642068": "B",
    "7651320643010514197": "A",
}


def _parse_count(text):
    text = text.strip().replace(",", "")
    if not text:
        return ""
    try:
        if text.endswith(("K", "k")):
            return str(int(float(text[:-1]) * 1_000))
        if text.endswith(("M", "m")):
            return str(int(float(text[:-1]) * 1_000_000))
        return str(int(float(text)))
    except ValueError:
        return ""


def main():
    if not SESSION_FILE.exists():
        print(f"ERROR: Session file not found: {SESSION_FILE}")
        return

    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            storage_state=str(SESSION_FILE),
            viewport=None,
            user_agent=DESKTOP_UA,
        )
        page = context.new_page()

        for video_id, variant in CONFIRMED_MAPPING.items():
            url = f"https://www.tiktok.com/@matziot.il/video/{video_id}"
            print(f"\n--- 002{variant}  (video {video_id}) ---")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30_000)
                time.sleep(3)
            except Exception as exc:
                print(f"  Nav error: {exc}")
                continue

            # On the public video page, like/comment/save/share counts are
            # rendered as labeled buttons in the right-side action rail.
            stats = page.evaluate("""() => {
                const out = {};
                const labels = {like: ['heart', 'like'], comment: ['comment'], save: ['favorite', 'save', 'bookmark'], share: ['share']};
                document.querySelectorAll('[data-e2e]').forEach(el => {
                    const e2e = el.getAttribute('data-e2e') || '';
                    const t = (el.textContent || '').trim();
                    if (e2e.includes('like-count')) out.likes = t;
                    if (e2e.includes('comment-count')) out.comments = t;
                    if (e2e.includes('undefined-count') || e2e.includes('share-count')) out.shares = t;
                    if (e2e.includes('browse-video-desc') || e2e.includes('video-views')) out.views_raw = t;
                });
                return out;
            }""")
            print(f"  data-e2e stats: {stats}")

            shot_path = OUTPUT_DIR / f"collect_002{variant}_{video_id}.png"
            try:
                page.screenshot(path=str(shot_path))
            except Exception:
                pass

            results[f"002{variant}"] = {
                "video_id": video_id,
                "variant": variant,
                "url": url,
                "likes": _parse_count(stats.get("likes", "")),
                "comments": _parse_count(stats.get("comments", "")),
                "shares": _parse_count(stats.get("shares", "")),
                "raw_stats": stats,
                "screenshot": shot_path.name,
            }
            print(f"  -> likes={results[f'002{variant}']['likes']} "
                  f"comments={results[f'002{variant}']['comments']} "
                  f"shares={results[f'002{variant}']['shares']}")

        browser.close()

    out_path = OUTPUT_DIR / "confirmed_collection.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
