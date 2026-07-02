#!/usr/bin/env python3
"""
diagnose_view_data_button.py — Locate the 008B row, scroll the table
horizontally to reveal whatever sits past the right edge, and screenshot it.
Does NOT click anything. Purely diagnostic: the screenshot gets read with
vision to identify the real "View Data" control before writing any selector.
"""
import sys
import time
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
    detect_all_products, scroll_container_horizontal, PROJECT_ROOT,
)

TARGET_PID = "008"
TARGET_LETTER = "B"
CTA_CODE = f"{TARGET_PID}{TARGET_LETTER}"
OUT_PATH = PROJECT_ROOT / "output" / "diagnose_view_data_row.png"
OUT_PATH_WIDE = PROJECT_ROOT / "output" / "diagnose_view_data_row_scrolled.png"


def main():
    products = detect_all_products({TARGET_PID})
    vinfo = products[TARGET_PID]["variants"][TARGET_LETTER]

    with sync_playwright() as pw:
        browser, context = launch_with_session(pw)
        page = context.new_page()

        print("Verifying session...")
        if not check_session_valid(page):
            print("ERROR: Session expired.")
            browser.close()
            sys.exit(1)
        print("Session valid.")

        vp = page.viewport_size
        print(f"Viewport size: {vp}")

        # Find the row by CTA text (read-only — no click)
        el = page.locator(f"text={CTA_CODE}").first
        found = False
        for scroll_i in range(25):
            try:
                if el.is_visible(timeout=800):
                    found = True
                    break
            except Exception:
                pass
            page.evaluate("""() => {
                const e = [...document.querySelectorAll('*')].find(
                    x => x.scrollHeight > x.clientHeight + 50 && x.clientHeight > 100
                );
                if (e) e.scrollTop += e.clientHeight * 0.8;
            }""")
            time.sleep(1.5)

        if not found:
            print(f"ERROR: could not find row for {CTA_CODE}")
            browser.close()
            sys.exit(1)

        print(f"Row found for {CTA_CODE}. Scrolling it into view...")
        el.evaluate("el => el.scrollIntoView({block: 'center', inline: 'end'})")
        time.sleep(0.5)

        page.screenshot(path=str(OUT_PATH), full_page=False)
        print(f"Saved (before horizontal scroll): {OUT_PATH}")

        print("Scrolling table horizontally to reveal any cut-off columns...")
        for _ in range(8):
            moved = scroll_container_horizontal(page, 0.9)
            time.sleep(0.4)
            if moved is None:
                print("  no horizontally-scrollable container found")
                break

        page.screenshot(path=str(OUT_PATH_WIDE), full_page=False)
        print(f"Saved (after horizontal scroll): {OUT_PATH_WIDE}")

        browser.close()


if __name__ == "__main__":
    main()
