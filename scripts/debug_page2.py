#!/usr/bin/env python3
"""Debug 2: screenshot the page, check URL, try different UAs and strategies."""

import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

URL = "https://www.aliexpress.com/item/1005002771124894.html"

UA_MOBILE = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
)
UA_DESKTOP = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def probe(label, ua, viewport, extra_wait=0):
    print(f"\n=== {label} ===")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport=viewport,
            user_agent=ua,
            locale="en-US",
            timezone_id="Asia/Jerusalem",
        )
        page = ctx.new_page()
        try:
            page.goto(URL, timeout=45000, wait_until="domcontentloaded")
            page.wait_for_timeout(3000 + extra_wait)

            # Final URL (after any redirects)
            print("URL after nav:", page.url[:100])
            print("Title:", page.title())

            # Screenshot
            shot_path = f"C:/Automation/TikTok/scripts/debug_{label.lower().replace(' ', '_')}.png"
            page.screenshot(path=shot_path, full_page=False)
            print("Screenshot:", shot_path)

            # Count alicdn images with meaningful size
            imgs = page.evaluate("""() =>
                Array.from(document.querySelectorAll('img'))
                    .map(i => ({
                        src: i.src || i.getAttribute('data-src') || '',
                        nw: i.naturalWidth,
                        nh: i.naturalHeight
                    }))
                    .filter(i => i.src.includes('alicdn') && i.nw > 200 && i.nh > 200)
            """)
            print(f"Large alicdn images (>200px): {len(imgs)}")
            for im in imgs[:8]:
                print(f"  {im['nw']}x{im['nh']}  ...{im['src'][-80:]}")

            # Check for CAPTCHA / slider
            captcha = page.evaluate("""() =>
                !!(document.querySelector('[class*="captcha"]') ||
                   document.querySelector('[class*="slider"]') ||
                   document.querySelector('[id*="captcha"]') ||
                   document.querySelector('iframe[src*="captcha"]'))
            """)
            print("CAPTCHA detected:", captcha)

            # Page HTML size
            html_len = page.evaluate("() => document.body ? document.body.innerHTML.length : 0")
            print("Body HTML length:", html_len)

            # First 1000 chars of body text
            body_text = page.evaluate("() => document.body ? document.body.innerText.substring(0, 500) : ''")
            print("Body text sample:")
            print(body_text)

        except Exception as e:
            print("ERROR:", e)
        browser.close()


# Test 1: mobile UA (current approach)
probe("mobile_ua", UA_MOBILE, {"width": 390, "height": 844})

# Test 2: desktop UA, desktop viewport
probe("desktop_ua", UA_DESKTOP, {"width": 1280, "height": 800}, extra_wait=2000)

# Test 3: desktop UA with longer wait
probe("desktop_slow", UA_DESKTOP, {"width": 1280, "height": 800}, extra_wait=5000)
