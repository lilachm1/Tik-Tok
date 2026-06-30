#!/usr/bin/env python3
"""Debug: inspect AliExpress page structure to find product image selectors."""

import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
)
URL = "https://www.aliexpress.com/item/1005002771124894.html"


with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, user_agent=UA)
    page = ctx.new_page()
    page.goto(URL, timeout=45000, wait_until="networkidle")
    page.wait_for_timeout(2000)

    title = page.title()
    print("TITLE:", title[:100])
    print()

    # All img elements with alicdn.com in src or data-src
    imgs = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('img'))
            .map(img => ({
                src: img.src || '',
                ds: img.getAttribute('data-src') || '',
                nw: img.naturalWidth,
                nh: img.naturalHeight,
                cls: (img.className || '').substring(0, 80)
            }))
            .filter(i => i.src.includes('alicdn') || i.ds.includes('alicdn'))
    }""")

    print("ALICDN IMAGES FOUND:", len(imgs))
    for i, im in enumerate(imgs[:30]):
        src = im["src"] or im["ds"]
        print(f"  [{i:02d}] {im['nw']}x{im['nh']}  cls='{im['cls'][:50]}'")
        print(f"        src=...{src[-90:]}")
    print()

    # Relevant CSS class names on the page
    classes = page.evaluate("""() => {
        const found = new Set();
        for (const el of document.querySelectorAll('[class]')) {
            for (const c of (el.className || '').split(' ')) {
                if (/image|gallery|slider|thumb|photo|product|magnif/i.test(c)) {
                    found.add(c);
                }
            }
        }
        return Array.from(found).sort();
    }""")
    print("RELEVANT CSS CLASSES:")
    for c in classes:
        print("  ", c)
    print()

    # Try to find what selector the main gallery uses
    # Check a few candidate selectors
    test_selectors = [
        ".pdp-product-img img",
        "[class*='pdp'] img",
        "[class*='slider'] img",
        "[class*='image'] img",
        "[class*='gallery'] img",
        "[class*='photo'] img",
        "[class*='magnif'] img",
        "[class*='main'] img",
        "div img[src*='alicdn']",
    ]
    print("SELECTOR PROBE:")
    for sel in test_selectors:
        try:
            count = page.evaluate(
                f"() => document.querySelectorAll('{sel}').length"
            )
            if count > 0:
                # Get first few srcs
                srcs = page.evaluate(
                    f"""() => Array.from(document.querySelectorAll('{sel}'))
                        .slice(0,3)
                        .map(img => img.src || img.getAttribute('data-src') || '')
                        .filter(s => s.length > 0)"""
                )
                print(f"  '{sel}' -> {count} elements")
                for s in srcs:
                    print(f"    ...{s[-80:]}")
        except Exception as e:
            print(f"  '{sel}' -> ERROR: {e}")
    print()

    # Snapshot of full page HTML structure (first 5000 chars)
    html_snippet = page.evaluate("() => document.body.innerHTML.substring(0, 3000)")
    print("HTML SNIPPET (first 3000 chars):")
    print(html_snippet)

    browser.close()
