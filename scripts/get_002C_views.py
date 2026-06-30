#!/usr/bin/env python3
"""Scroll TikTok Studio content list to the Product 002 cluster and take a
full-viewport screenshot to read 002C's views (clip-based capture failed
earlier due to a bounds edge case)."""
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output" / "identify_002"
SESSION_FILE = DATA_DIR / "tiktok-session.json"
DESKTOP_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

JS_SCROLL_CONTAINER = """(target) => {
    const el = [...document.querySelectorAll('*')].find(
        e => e.scrollHeight > e.clientHeight + 50 && e.clientHeight > 100
    );
    if (!el) return null;
    el.scrollTop = target;
    return el.scrollTop;
}"""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=["--start-maximized"])
    context = browser.new_context(storage_state=str(SESSION_FILE), viewport=None, user_agent=DESKTOP_UA)
    page = context.new_page()
    page.goto("https://www.tiktok.com/tiktokstudio/content", wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)
    for target in (739, 800, 900, 1000):
        page.evaluate(JS_SCROLL_CONTAINER, target)
        time.sleep(1.2)
        page.screenshot(path=str(OUTPUT_DIR / f"studio_scroll_{target}.png"))
        print(f"saved studio_scroll_{target}.png")
    browser.close()
