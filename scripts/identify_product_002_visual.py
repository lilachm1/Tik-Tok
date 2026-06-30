#!/usr/bin/env python3
"""
identify_product_002_visual.py — Visual identity confirmation for Product 002 variants.

Product 002's 4 variants share an identical TikTok caption and a bare CTA code
("002", no variant letter), so text/caption-based matching cannot distinguish
them (see PROJECT_STATUS.md, 2026-06-30 blocker).

This script tests an independent identifier: each variant has a UNIQUE hook-text
overlay baked into the video pixels at 0-2s (top-center position), per
data/002-video-config.json:
  A: "לא תאמיני כמה זה עולה בעלי אקספרס..."
  B: "ראיתי את זה בטיקטוק ולא האמנתי שזה קיים..."
  C: "מצאתי את הפתרון לבעיה שכולנו מכירות"
  D: "כולן מדברות על זה ואני סוף סוף הזמנתי..."

If TikTok's auto-generated thumbnail is a frame from early in the video, this
text should be visible and readable in the thumbnail/cover image, giving a
visual (not text-DOM) confirmation of which row is which variant.

This script does NOT decide identity itself — it filters to the 4 Product 002
rows via caption search (reusing the proven search_box_find approach from
tiktok_analytics_collect.py) and saves a labeled screenshot crop of each row's
thumbnail for human/agent visual inspection. It also records each row's
position, bounding box, and any href/video-id found, for cross-reference.

No metrics are written by this script. Read-only.
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
CONTENT_TAB_URL = "https://www.tiktok.com/tiktokstudio/content"

DESKTOP_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

CAPTION_SUBSTRING = "מצאתי מחזיק טלפון"  # opening words, identical across all 4 captions
MAX_SCROLLS = 30
TARGET_MATCHES = 4


JS_FIND_CONTAINER = """() => {
    return [...document.querySelectorAll('*')].find(
        e => e.scrollHeight > e.clientHeight + 50 && e.clientHeight > 100
    );
}"""

JS_GET_SCROLLTOP = """() => {
    const el = [...document.querySelectorAll('*')].find(
        e => e.scrollHeight > e.clientHeight + 50 && e.clientHeight > 100
    );
    return el ? el.scrollTop : 0;
}"""

JS_SCROLL_CONTAINER = """(frac) => {
    const el = [...document.querySelectorAll('*')].find(
        e => e.scrollHeight > e.clientHeight + 50 && e.clientHeight > 100
    );
    if (!el) return null;
    el.scrollTop += el.clientHeight * frac;
    return el.scrollTop;
}"""

JS_SCAN = """(substr) => {
    const all = document.querySelectorAll('div, span, p, a, td, li');
    const found = [];
    const seenRows = [];
    for (const el of all) {
        const t = el.textContent || '';
        if (!t.includes(substr)) continue;
        const r = el.getBoundingClientRect();
        if (!(r.width > 0 && r.height > 0 && r.height < 100)) continue;
        // climb ancestors to find the full-width row container (thumbnail + text + stats)
        let node = el, rowNode = el;
        for (let i = 0; i < 6 && node.parentElement; i++) {
            node = node.parentElement;
            const rr = node.getBoundingClientRect();
            if (rr.width > 600 && rr.height >= 40 && rr.height <= 130) {
                rowNode = node;
                break;
            }
        }
        const rr = rowNode.getBoundingClientRect();
        // de-dupe multiple nested text matches pointing at the same row
        if (seenRows.some(sr => Math.abs(sr.y - rr.y) < 10)) continue;
        seenRows.push({y: rr.y});
        let href = '';
        const a = rowNode.querySelector('a') || rowNode.closest('a');
        if (a) href = a.getAttribute('href') || '';
        found.push({x: rr.x, y: rr.y, width: rr.width, height: rr.height, text: t.slice(0, 200), href});
    }
    return found;
}"""


def find_and_capture_all(page, substring, out_dir, max_scrolls=MAX_SCROLLS):
    """
    Scroll the FULL unfiltered content list (search box does not filter — see
    investigation notes) and collect every row whose caption text contains
    `substring`. Uses raw JS textContent.includes() scanning instead of
    Playwright's text= engine, which was confirmed unreliable for Hebrew/RTL
    text in this project (0 matches found across a full scroll-through).
    Dedups by absolute page Y. For each new match, immediately screenshots the
    enclosing row before scrolling further, to avoid acting on a stale/
    virtualized element handle.
    """
    seen_y = []
    results = []
    last_scroll_top = -1
    stagnant_count = 0

    for scroll_i in range(max_scrolls):
        try:
            candidates = page.evaluate(JS_SCAN, substring)
        except Exception as exc:
            print(f"  JS scan error: {exc}")
            candidates = []

        scroll_y = page.evaluate(JS_GET_SCROLLTOP)

        for cand in candidates:
            abs_y = round(cand["y"] + scroll_y)
            if any(abs(abs_y - y) < 50 for y in seen_y):
                continue
            seen_y.append(abs_y)

            idx = len(results) + 1
            row_id = f"row{idx}"
            print(f"\n--- {row_id}  (scroll {scroll_i}, abs_y={abs_y}) ---")
            print(f"  matched text: {cand['text']}")
            print(f"  href: {cand['href'][:100]}")

            # Screenshot immediately via raw viewport coordinates (clip) — no
            # Locator round-trip, since the virtualized list recycles DOM
            # nodes and any attribute/handle set a moment ago may already be
            # gone by the time a follow-up query runs.
            shot_path = out_dir / f"{row_id}_row.png"
            try:
                clip = {"x": cand["x"], "y": cand["y"], "width": cand["width"], "height": cand["height"]}
                page.screenshot(path=str(shot_path), clip=clip)
                print(f"  Saved: {shot_path.name}")
            except Exception as exc:
                print(f"  Screenshot failed: {exc}")
                shot_path = None

            results.append({
                "row_id": row_id,
                "abs_y": abs_y,
                "href": cand["href"],
                "text_content": cand["text"],
                "screenshot": shot_path.name if shot_path else None,
            })

        if len(results) >= TARGET_MATCHES:
            print(f"\nReached {TARGET_MATCHES} matches — doing 2 extra scrolls to confirm no more exist.")
            for _ in range(2):
                page.evaluate(JS_SCROLL_CONTAINER, 0.7)
                time.sleep(1.2)
            extra = page.evaluate(JS_SCAN, substring)
            scroll_y2 = page.evaluate(JS_GET_SCROLLTOP)
            for cand in extra:
                abs_y = round(cand["y"] + scroll_y2)
                if any(abs(abs_y - y) < 50 for y in seen_y):
                    continue
                print(f"  WARNING: additional match found beyond {TARGET_MATCHES} at abs_y={abs_y}: {cand['text']}")
            break

        moved = page.evaluate(JS_SCROLL_CONTAINER, 0.7)
        print(f"  [scroll] container.scrollTop -> {moved}")
        if moved is not None and moved == last_scroll_top:
            stagnant_count += 1
            if stagnant_count >= 3:
                print(f"  Scroll position stagnant at {moved} for 3 steps — reached bottom of list.")
                break
        else:
            stagnant_count = 0
        last_scroll_top = moved
        time.sleep(1.5)

    return results


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

        print("Navigating to TikTok Studio content tab...")
        page.goto(CONTENT_TAB_URL, wait_until="domcontentloaded", timeout=30_000)
        time.sleep(3)

        if "login" in page.url.lower() or "passport" in page.url.lower():
            print("ERROR: Session expired. Run scripts/tiktok_session_login.py")
            browser.close()
            return

        # Diagnostic: find the real scrollable container (window/body scroll
        # was confirmed stuck at 30px — the list is virtualized inside a
        # nested overflow:auto div).
        scroll_candidates = page.evaluate("""() => {
            const out = [];
            document.querySelectorAll('*').forEach(el => {
                if (el.scrollHeight > el.clientHeight + 50 && el.clientHeight > 100) {
                    const r = el.getBoundingClientRect();
                    out.push({
                        tag: el.tagName, cls: (el.className || '').slice(0, 80),
                        scrollHeight: el.scrollHeight, clientHeight: el.clientHeight,
                        x: r.x, y: r.y, width: r.width, height: r.height
                    });
                }
            });
            return out;
        }""")
        print(f"\nScrollable container candidates ({len(scroll_candidates)}):")
        for c in scroll_candidates[:15]:
            print(f"  <{c['tag']} class='{c['cls']}'> scrollH={c['scrollHeight']} clientH={c['clientHeight']} "
                  f"rect=({c['x']:.0f},{c['y']:.0f},{c['width']:.0f},{c['height']:.0f})")

        print(f"\nScrolling full content list for caption substring: {CAPTION_SUBSTRING!r}")
        print("(Search box does not filter the list in this TikTok Studio build — bypassing it.)")

        results = find_and_capture_all(page, CAPTION_SUBSTRING, OUTPUT_DIR)

        print(f"\n{'='*60}")
        print(f"TOTAL MATCHES FOUND: {len(results)} (expected {TARGET_MATCHES})")
        print(f"{'='*60}")

        manifest_path = OUTPUT_DIR / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nManifest saved: {manifest_path}")

        print("\nClosing browser...")
        browser.close()


if __name__ == "__main__":
    main()
