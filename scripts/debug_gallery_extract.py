#!/usr/bin/env python3
"""Extract actual product image URLs from AliExpress gallery CSS background-images and data attributes."""

import io
import json
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

UA_DESKTOP = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
URL = "https://he.aliexpress.com/item/1005006956233010.html"

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent=UA_DESKTOP,
        locale="en-US",
    )
    page = ctx.new_page()
    page.goto(URL, timeout=45000, wait_until="networkidle")
    page.wait_for_timeout(2000)

    print("Title:", page.title()[:80])
    print()

    # --- 1. CSS background-image on ALL elements ---
    print("=== ALL background-image URLs with alicdn ===")
    bg_all = page.evaluate("""() => {
        const res = [];
        for (const el of document.querySelectorAll('*')) {
            try {
                const bg = window.getComputedStyle(el).backgroundImage;
                if (bg && bg !== 'none' && bg.includes('alicdn')) {
                    const m = bg.match(/url\\(["']?([^"')]+)["']?\\)/);
                    if (m) res.push({
                        tag: el.tagName,
                        cls: (typeof el.className === 'string' ? el.className : '').substring(0, 80),
                        url: m[1]
                    });
                }
            } catch(e) {}
        }
        return res;
    }""")
    print(f"Total: {len(bg_all)}")
    for b in bg_all:
        print(f"  {b['tag']}  cls='{b['cls'][:60]}'")
        print(f"    URL: {b['url']}")
    print()

    # --- 2. Elements with known gallery class names ---
    print("=== Elements with gallery/slider class names ===")
    gallery_probe = page.evaluate("""() => {
        const classes = [
            '[class*="slider--img"]',
            '[class*="slider--item"]',
            '[class*="magnifier--image"]',
            '[class*="main-image"]',
            '[class*="image-view"]',
            '[class*="sku-item--image"]'
        ];
        const res = {};
        for (const sel of classes) {
            const els = document.querySelectorAll(sel);
            if (els.length === 0) continue;
            const items = [];
            for (const el of els) {
                const item = {
                    tag: el.tagName,
                    cls: (typeof el.className === 'string' ? el.className : '').substring(0, 80),
                    src: el.getAttribute('src') || '',
                    ds: el.getAttribute('data-src') || '',
                    bg: ''
                };
                try {
                    const bg = window.getComputedStyle(el).backgroundImage;
                    if (bg && bg !== 'none') item.bg = bg.substring(0, 120);
                } catch(e) {}
                items.push(item);
            }
            res[sel] = items.slice(0, 10);
        }
        return res;
    }""")
    for sel, items in gallery_probe.items():
        if items:
            print(f"  Selector: {sel}  ({len(items)} elements)")
            for it in items:
                print(f"    {it['tag']}  cls='{it['cls'][:60]}'")
                if it['src']: print(f"    src: {it['src'][:100]}")
                if it['ds']:  print(f"    data-src: {it['ds'][:100]}")
                if it['bg']:  print(f"    bg: {it['bg'][:100]}")
    print()

    # --- 3. Extract URLs from window.__AER_DATA__ or similar global vars ---
    print("=== JavaScript global data (window keys with 'data'/'sku'/'image') ===")
    js_data_keys = page.evaluate("""() =>
        Object.keys(window)
            .filter(k => /data|sku|image|product|item|gallery/i.test(k) && k.length < 40)
            .slice(0, 30)
    """)
    print("Relevant window keys:", js_data_keys)
    print()

    # --- 4. Try to find the image list in embedded JSON/script tags ---
    print("=== Script tags containing alicdn image URLs ===")
    script_data = page.evaluate("""() => {
        const results = [];
        for (const script of document.querySelectorAll('script')) {
            const text = script.innerText || script.textContent || '';
            if (text.includes('alicdn') && text.includes('800x800')) {
                // Extract URLs
                const matches = text.match(/https?:\\/\\/ae0[0-9]\\.alicdn\\.com[^"'\\s,]+/g) || [];
                if (matches.length > 0) {
                    results.push({
                        len: text.length,
                        urls: matches.slice(0, 15)
                    });
                }
            }
        }
        return results;
    }""")
    print(f"Script blocks with alicdn 800x800 URLs: {len(script_data)}")
    for block in script_data:
        print(f"  Script length: {block['len']}")
        for u in block['urls']:
            print(f"    {u}")
    print()

    # --- 5. Extract image URLs from all script content ---
    print("=== All alicdn URLs in script tags (any size) ===")
    all_script_urls = page.evaluate("""() => {
        const found = new Set();
        for (const script of document.querySelectorAll('script')) {
            const text = script.innerText || script.textContent || '';
            const matches = text.match(/https?:\\/\\/(ae|img)\\.alicdn\\.com[^"'\\s,<>\\\\]+/g) || [];
            for (const m of matches) {
                if (m.length > 30 && m.length < 300) found.add(m);
            }
        }
        return Array.from(found).slice(0, 30);
    }""")
    print(f"Total unique alicdn URLs in scripts: {len(all_script_urls)}")
    for u in all_script_urls[:20]:
        print(f"  {u}")

    browser.close()
