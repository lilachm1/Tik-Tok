#!/usr/bin/env python3
"""
tiktok_session_login.py  —  One-time TikTok Creator Center login.

Saves browser session cookies to data/tiktok-session.json so the collector
script can reuse them without storing any password.

Usage:
    python scripts/tiktok_session_login.py

A visible Chrome window opens. Log in normally (password, QR code, Google,
or any method TikTok supports, including 2FA). When you can see your Creator
Center analytics dashboard, press Enter in this terminal.
"""

import io
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SESSION_FILE = PROJECT_ROOT / "data" / "tiktok-session.json"
GITIGNORE    = PROJECT_ROOT / ".gitignore"

CREATOR_CENTER_URLS = [
    "https://www.tiktok.com/creator-center/analytics",
    "https://creator.tiktok.com/creator-center/analytics",
    "https://www.tiktok.com/analytics",
]

DESKTOP_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def _check_gitignore() -> None:
    if not GITIGNORE.exists():
        return
    content = GITIGNORE.read_text(encoding="utf-8")
    if "tiktok-session.json" not in content:
        print("⚠️  WARNING: data/tiktok-session.json is NOT listed in .gitignore.")
        print("   Add it before committing to prevent leaking session cookies.")
        print()


def main() -> None:
    _check_gitignore()

    print("=" * 60)
    print("TikTok Session Login  —  One-time setup")
    print("=" * 60)
    print()
    print("A Chrome window will open at TikTok Creator Center.")
    print("Log in with your TikTok account using any method.")
    print("Complete 2FA if prompted — the script waits for you.")
    print()
    print("Once you see your analytics dashboard, come back here")
    print("and press Enter.")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        context = browser.new_context(
            viewport=None,
            user_agent=DESKTOP_UA,
        )
        page = context.new_page()

        opened = False
        for url in CREATOR_CENTER_URLS:
            try:
                print(f"Opening: {url}")
                page.goto(url, wait_until="domcontentloaded", timeout=30_000)
                opened = True
                break
            except PWTimeout:
                print(f"  Timeout on {url}, trying next...")
            except Exception as exc:
                print(f"  Error on {url}: {exc}, trying next...")

        if not opened:
            print("Could not open TikTok Creator Center automatically.")
            print("Navigate to https://www.tiktok.com/creator-center/analytics manually.")

        print()
        print("Waiting for login — checking for TikTok auth cookies every 5 s (timeout 5 min).")
        print("Log in to TikTok in the browser. Do not close it.")
        print()
        AUTH_COOKIES = ("sessionid", "sid_guard", "uid_tt")
        deadline = time.time() + 300
        detected = False
        while time.time() < deadline:
            present = {c["name"] for c in context.cookies()}
            if any(k in present for k in AUTH_COOKIES):
                print(f"  Auth cookies detected — login confirmed.")
                time.sleep(2)
                detected = True
                break
            time.sleep(5)
        if not detected:
            print("  5-minute timeout — saving current session anyway.")
        print()

        SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        context.storage_state(path=str(SESSION_FILE))
        browser.close()

    print(f"✅  Session saved → {SESSION_FILE.relative_to(PROJECT_ROOT)}")
    print()
    print("Session lasts approximately 30 days.")
    print("Re-run this script if the collector reports a login redirect.")
    print()
    print("Next step:")
    print("  python scripts/tiktok_analytics_collect.py")
    print()


if __name__ == "__main__":
    main()
