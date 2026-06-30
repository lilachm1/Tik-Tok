#!/usr/bin/env python3
"""
identify_002_seek_start.py — Re-open specific Product 002 videos and force-seek
the <video> element to t=0.1s before screenshotting, to read the unique
hook-text overlay baked into segment 1 (0-2s) of each variant.
"""

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

VIDEO_IDS = [
    "7651330918107385109",
]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

        for video_id in VIDEO_IDS:
            url = f"https://www.tiktok.com/@matziot.il/video/{video_id}"
            print(f"\n--- {video_id} ---")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30_000)
                time.sleep(3)
            except Exception as exc:
                print(f"  Nav error: {exc}")
                continue

            for dismiss_sel in ['[aria-label="Close"]', 'text="Maybe later"', 'button:has-text("Maybe later")']:
                try:
                    btn = page.locator(dismiss_sel).first
                    if btn.is_visible(timeout=1500):
                        btn.click()
                        time.sleep(0.5)
                        print(f"  dismissed popup via {dismiss_sel}")
                except Exception:
                    pass

            # Force-seek the player to just after t=0 and pause, repeatedly
            # (TikTok's player may reset/autoplay over a single attempt).
            for attempt in range(5):
                try:
                    state = page.evaluate("""() => {
                        const v = document.querySelector('video');
                        if (!v) return {found: false};
                        v.pause();
                        v.currentTime = 0.15;
                        return {found: true, currentTime: v.currentTime, paused: v.paused, readyState: v.readyState};
                    }""")
                except Exception as exc:
                    state = {"found": False, "error": str(exc)}
                time.sleep(0.4)
                if state.get("found"):
                    break

            print(f"  video element state: {state}")
            time.sleep(0.5)

            shot_path = OUTPUT_DIR / f"seek0_{video_id}.png"
            try:
                page.screenshot(path=str(shot_path))
                print(f"  Saved: {shot_path.name}")
            except Exception as exc:
                print(f"  Screenshot failed: {exc}")

        browser.close()


if __name__ == "__main__":
    main()
