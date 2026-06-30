#!/usr/bin/env python3
"""
identify_002_open_each.py — Open each of the 4 confirmed Product 002 video URLs
directly and capture a larger screenshot + exact post timestamp, for visual
hook-text identification and upload-order cross-validation.

Video IDs were confirmed unique via identify_product_002_visual.py (each of
the 4 rows sharing Product 002's caption has a distinct href/video ID — the
prior "no unique identifier exists" conclusion was a tooling bug, not a DOM
limitation).
"""

import json
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

# hrefs captured from identify_product_002_visual.py manifest.json, in the
# scroll-order they were found (topmost to bottommost in the Studio list)
VIDEO_HREFS = [
    "/@matziot.il/video/7651330918107385109",
    "/@matziot.il/video/7651330347824696596",
    "/@matziot.il/video/7651327807460642068",
    "/@matziot.il/video/7651320643010514197",
]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not SESSION_FILE.exists():
        print(f"ERROR: Session file not found: {SESSION_FILE}")
        return

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

        manifest = []
        for i, href in enumerate(VIDEO_HREFS):
            video_id = href.rstrip("/").split("/")[-1]
            url = f"https://www.tiktok.com{href}"
            print(f"\n--- video {i+1}: {video_id} ---")
            print(f"  URL: {url}")

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30_000)
                time.sleep(4)
            except Exception as exc:
                print(f"  Nav error: {exc}")
                continue

            # Dismiss any popup
            try:
                close_btn = page.locator('[aria-label="Close"]').first
                if close_btn.is_visible(timeout=1500):
                    close_btn.click()
                    time.sleep(0.5)
            except Exception:
                pass

            shot_path = OUTPUT_DIR / f"video_{video_id}.png"
            try:
                page.screenshot(path=str(shot_path))
                print(f"  Saved: {shot_path.name}")
            except Exception as exc:
                print(f"  Screenshot failed: {exc}")
                shot_path = None

            # Try to read caption/description text + posted time from the page
            page_text = ""
            try:
                page_text = page.locator("body").inner_text(timeout=3000)
            except Exception:
                pass

            manifest.append({
                "video_id": video_id,
                "href": href,
                "url": url,
                "screenshot": shot_path.name if shot_path else None,
                "page_text_excerpt": page_text[:500],
            })

        manifest_path = OUTPUT_DIR / "open_each_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        print(f"\nManifest saved: {manifest_path}")

        browser.close()


if __name__ == "__main__":
    main()
