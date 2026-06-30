#!/usr/bin/env python3
"""Browse Israeli AliExpress to find a valid product URL with 5+ images."""

import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

UA_DESKTOP = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# Search for phone accessories on Israeli AliExpress
SEARCH_URL = "https://he.aliexpress.com/wholesale?SearchText=phone+holder+stand&SortType=total_tranpro_desc"

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent=UA_DESKTOP,
        locale="en-US",
    )
    page = ctx.new_page()

    print("Searching AliExpress Israel for phone stand / holder...")
    page.goto(SEARCH_URL, timeout=45000, wait_until="domcontentloaded")
    page.wait_for_timeout(4000)

    print("URL:", page.url[:120])
    print("Title:", page.title())

    # Find product links
    product_links = page.evaluate("""() =>
        Array.from(document.querySelectorAll('a[href*="/item/"]'))
            .map(a => a.href)
            .filter(h => h.includes('/item/'))
            .filter((v, i, arr) => arr.indexOf(v) === i)
            .slice(0, 20)
    """)
    print(f"Product links found: {len(product_links)}")
    for link in product_links[:10]:
        print(" ", link[:100])

    if not product_links:
        print("No product links found on search page. Taking screenshot...")
        page.screenshot(path="C:/Automation/TikTok/scripts/debug_search.png")
        print("Screenshot: debug_search.png")
        # Try homepage instead
        page.goto("https://he.aliexpress.com/", timeout=30000, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        product_links = page.evaluate("""() =>
            Array.from(document.querySelectorAll('a[href*="/item/"]'))
                .map(a => a.href)
                .filter(h => h.includes('/item/'))
                .filter((v, i, arr) => arr.indexOf(v) === i)
                .slice(0, 20)
        """)
        print(f"Product links on homepage: {len(product_links)}")
        for link in product_links[:10]:
            print(" ", link[:100])

    # Try to open the first product and check it has images
    if product_links:
        test_url = product_links[0]
        print(f"\nProbing first product: {test_url[:100]}")
        page.goto(test_url, timeout=45000, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)
        print("Final URL:", page.url[:120])
        print("Title:", page.title())

        imgs = page.evaluate("""() =>
            Array.from(document.querySelectorAll('img'))
                .map(i => ({
                    src: i.src || i.getAttribute('data-src') || '',
                    nw: i.naturalWidth, nh: i.naturalHeight
                }))
                .filter(i => i.src.includes('alicdn') && i.nw > 150 && i.nh > 150)
        """)
        print(f"Large product images: {len(imgs)}")
        for im in imgs[:10]:
            print(f"  {im['nw']}x{im['nh']}  ...{im['src'][-80:]}")

        page.screenshot(path="C:/Automation/TikTok/scripts/debug_product.png")
        print("Screenshot: debug_product.png")

    browser.close()
