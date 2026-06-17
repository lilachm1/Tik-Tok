#!/usr/bin/env python3
"""Extract image URLs from window data and element attributes on AliExpress."""

import io
import json
import re
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

UA_DESKTOP = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
URL = "https://he.aliexpress.com/item/1005006956233010.html"

# All known AliExpress CDN domains
CDN_DOMAINS = [
    "alicdn.com",
    "aliexpress-media.com",
    "aliexpress.com/kf",
    "ae01.alicdn",
    "ae-pic",
]

def has_aliexpress_cdn(url):
    return any(d in url for d in CDN_DOMAINS)


with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent=UA_DESKTOP,
        locale="en-US",
    )
    page = ctx.new_page()
    page.goto(URL, timeout=45000, wait_until="networkidle")
    page.wait_for_timeout(3000)

    # 1. Investigate window.__INIT_DATA_CALLBACK__ and window.data
    print("=== Window global data keys ===")
    init_data = page.evaluate("""() => {
        try {
            const d = window.__INIT_DATA_CALLBACK__ || window.data || null;
            if (!d) return null;
            return JSON.stringify(d).substring(0, 5000);
        } catch(e) { return 'ERROR: ' + e.message; }
    }""")
    if init_data:
        # Look for image URLs in the data
        cdn_urls = re.findall(r'https?://[^\s"\'\\]+aliexpress[^\s"\'\\]+', init_data or '')
        print(f"AliExpress URLs in window data: {len(cdn_urls)}")
        for u in cdn_urls[:20]:
            print(f"  {u}")
    else:
        print("No __INIT_DATA_CALLBACK__ or data found")

    # 2. Check ALL attributes on slider--img elements
    print("\n=== slider--img element - all attributes ===")
    slider_attrs = page.evaluate("""() => {
        const els = document.querySelectorAll('[class*="slider--img"]');
        return Array.from(els).slice(0, 5).map(el => {
            const attrs = {};
            for (const attr of el.attributes) {
                attrs[attr.name] = attr.value.substring(0, 200);
            }
            // Also check children
            const children = Array.from(el.children).map(child => {
                const childAttrs = {};
                for (const a of child.attributes) childAttrs[a.name] = a.value.substring(0, 200);
                return {tag: child.tagName, attrs: childAttrs, childCount: child.children.length};
            });
            return {tag: el.tagName, attrs, children: children.slice(0, 5)};
        });
    }""")
    print(json.dumps(slider_attrs, ensure_ascii=False, indent=2))

    # 3. Check ALL attributes on slider--item elements
    print("\n=== slider--item element - all attributes ===")
    slider_item_attrs = page.evaluate("""() => {
        const els = document.querySelectorAll('[class*="slider--item"]');
        return Array.from(els).slice(0, 3).map(el => {
            const attrs = {};
            for (const attr of el.attributes) {
                attrs[attr.name] = attr.value.substring(0, 200);
            }
            const innerImgs = Array.from(el.querySelectorAll('img, [style*="background"]')).map(child => {
                const childAttrs = {};
                for (const a of child.attributes) childAttrs[a.name] = a.value.substring(0, 200);
                return {tag: child.tagName, attrs: childAttrs};
            });
            return {tag: el.tagName, attrs, innerImgs: innerImgs.slice(0, 5)};
        });
    }""")
    print(json.dumps(slider_item_attrs, ensure_ascii=False, indent=2))

    # 4. ALL img elements regardless of CDN
    print("\n=== ALL img elements on page ===")
    all_imgs = page.evaluate("""() =>
        Array.from(document.querySelectorAll('img')).map(img => ({
            src: img.src || '',
            ds: img.getAttribute('data-src') || '',
            nw: img.naturalWidth,
            nh: img.naturalHeight,
            cls: (typeof img.className === 'string' ? img.className : '').substring(0, 80)
        }))
    """)
    # Filter to only images with non-placeholder content
    meaningful = [i for i in all_imgs if (i['nw'] > 50 or i['nh'] > 50 or len(i['src']) > 30) and i['src']]
    print(f"Meaningful img elements: {len(meaningful)}")
    for im in meaningful[:20]:
        print(f"  {im['nw']}x{im['nh']}  cls='{im['cls'][:60]}'")
        print(f"    src: {im['src'][:120]}")

    # 5. Intercept network requests for image URLs
    print("\n=== Try clicking first slider item to trigger image load ===")
    try:
        # Click on slider to activate
        slider = page.query_selector('[class*="slider--item"]')
        if slider:
            slider.click()
            page.wait_for_timeout(1000)

        # Now check slider--img bg again
        bg_after = page.evaluate("""() => {
            const res = [];
            for (const el of document.querySelectorAll('[class*="slider--img"], [class*="magnifier"]')) {
                try {
                    const bg = window.getComputedStyle(el).backgroundImage;
                    const src = el.getAttribute('src') || '';
                    if ((bg && bg !== 'none') || src) {
                        res.push({
                            tag: el.tagName,
                            cls: (typeof el.className === 'string' ? el.className : '').substring(0, 60),
                            bg: bg || '',
                            src: src
                        });
                    }
                } catch(e) {}
            }
            return res;
        }""")
        print(f"slider--img elements after click: {len(bg_after)}")
        for b in bg_after:
            print(f"  {b['tag']} {b['cls'][:50]}")
            if b['bg'] and b['bg'] != 'none': print(f"    bg: {b['bg'][:120]}")
            if b['src']: print(f"    src: {b['src'][:120]}")
    except Exception as e:
        print(f"Click probe error: {e}")

    # 6. Intercept: look at network image requests
    print("\n=== Reload with network interception ===")
    browser.close()

# Second pass: intercept all image requests to capture CDN image URLs
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent=UA_DESKTOP,
        locale="en-US",
    )
    page = ctx.new_page()

    captured_image_urls = []

    def on_response(response):
        url = response.url
        ct = response.headers.get("content-type", "")
        if "image" in ct and ("alicdn" in url or "aliexpress-media" in url):
            captured_image_urls.append(url)

    page.on("response", on_response)
    page.goto(URL, timeout=45000, wait_until="networkidle")
    page.wait_for_timeout(2000)

    # Scroll to trigger lazy loads
    for y in [300, 600, 0]:
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(500)

    page.wait_for_timeout(2000)

    print(f"Intercepted {len(captured_image_urls)} image requests from AliExpress CDN:")
    seen = set()
    for u in captured_image_urls:
        if u not in seen:
            seen.add(u)
            print(f"  {u}")

    browser.close()
