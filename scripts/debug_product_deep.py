#!/usr/bin/env python3
"""Deep probe of a specific AliExpress Israel product page."""

import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

UA_DESKTOP = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

URL = "https://he.aliexpress.com/item/1005006956233010.html"


def probe_page(page, label):
    print(f"\n--- {label} ---")
    print("URL:", page.url[:100])
    print("Title:", page.title()[:80])

    # ALL img elements
    all_imgs = page.evaluate("""() =>
        Array.from(document.querySelectorAll('img')).map(img => ({
            src: img.src || '',
            ds: img.getAttribute('data-src') || '',
            nw: img.naturalWidth,
            nh: img.naturalHeight,
            cls: (typeof img.className === 'string' ? img.className : '').substring(0, 60)
        }))
    """)
    print(f"Total img elements: {len(all_imgs)}")

    alicdn_all = [i for i in all_imgs if 'alicdn' in (i['src'] + i['ds'])]
    alicdn_big = [i for i in alicdn_all if i['nw'] > 100 or i['nh'] > 100]
    print(f"  with alicdn: {len(alicdn_all)}, large (>100px): {len(alicdn_big)}")
    for im in alicdn_all[:15]:
        src = im['src'] or im['ds']
        print(f"  {im['nw']}x{im['nh']}  cls='{im['cls'][:40]}'  ...{src[-70:]}")

    # Check for background-image CSS with alicdn URLs
    bg_imgs = page.evaluate("""() => {
        const res = [];
        for (const el of document.querySelectorAll('*')) {
            const bg = window.getComputedStyle(el).backgroundImage;
            if (bg && bg.includes('alicdn')) {
                const m = bg.match(/url\\(["']?([^"')]+)["']?\\)/);
                if (m) res.push({
                    tag: el.tagName,
                    cls: (typeof el.className === 'string' ? el.className : '').substring(0, 50),
                    url: m[1].substring(m[1].length - 80)
                });
            }
        }
        return res.slice(0, 20);
    }""")
    print(f"  background-image alicdn: {len(bg_imgs)}")
    for b in bg_imgs[:10]:
        print(f"    {b['tag']}  cls='{b['cls'][:40]}'  ...{b['url']}")

    # CSS classes containing image/gallery keywords
    cls_set = page.evaluate("""() => {
        const found = new Set();
        for (const el of document.querySelectorAll('[class]')) {
            const cn = typeof el.className === 'string' ? el.className : '';
            for (const c of cn.split(' ')) {
                if (/image|gallery|slider|thumb|photo|product|magnif|pic|img/i.test(c) && c.length > 2)
                    found.add(c);
            }
        }
        return Array.from(found).sort().slice(0, 50);
    }""")
    print("Image-related CSS classes:", cls_set[:30])

    # Any lazy-load containers
    lazy = page.evaluate("""() =>
        Array.from(document.querySelectorAll('[data-src], [data-lazy], [data-original]'))
            .filter(el => {
                const s = el.getAttribute('data-src') || el.getAttribute('data-lazy') || el.getAttribute('data-original') || '';
                return s.includes('alicdn');
            })
            .map(el => el.getAttribute('data-src') || el.getAttribute('data-lazy') || el.getAttribute('data-original') || '')
            .slice(0, 10)
    """)
    print(f"Lazy-load elements with alicdn data-src: {len(lazy)}")
    for l in lazy:
        print(f"  ...{l[-80:]}")


with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent=UA_DESKTOP,
        locale="en-US",
    )
    page = ctx.new_page()

    page.goto(URL, timeout=45000, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    probe_page(page, "After initial load")

    # Scroll down to trigger lazy loading
    page.evaluate("window.scrollTo(0, 300)")
    page.wait_for_timeout(1500)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)
    probe_page(page, "After scroll")

    # Try networkidle
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        pass
    page.wait_for_timeout(2000)
    probe_page(page, "After networkidle")

    # Take screenshot
    page.screenshot(path="C:/Automation/TikTok/scripts/debug_deep.png", full_page=False)
    print("\nScreenshot saved: debug_deep.png")

    # Dump first 2000 chars of body
    body = page.evaluate("() => document.body ? document.body.innerText.substring(0, 1000) : ''")
    print("\nBody text (1000 chars):")
    print(body)

    browser.close()
