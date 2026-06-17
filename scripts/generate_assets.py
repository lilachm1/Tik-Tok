#!/usr/bin/env python3
"""
generate_assets.py -- Unique Asset Generation Agent
TikTok Affiliate Agent | C:/Automation/TikTok/scripts/

Collects product visuals from a single AliExpress product page.
Called by /tiktok command, Step 8.

Usage:
    python generate_assets.py --product-id 003 --url "https://www.aliexpress.com/item/1234567890.html"
"""

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Force UTF-8 stdout/stderr on Windows consoles (cp1252/cp1255 can't render ✅ ⚠ ❌)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
elif hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import requests
from PIL import Image
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


# ── Constants ─────────────────────────────────────────────────────────────────

# Desktop Chrome UA — AliExpress Israel (he.aliexpress.com) serves full product
# pages reliably with a desktop UA, whereas mobile UA triggers bot-detection.
DESKTOP_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# AliExpress CDN domains (as of 2026 the new CDN is aliexpress-media.com)
ALIEXPRESS_CDN_DOMAINS = ("alicdn.com", "aliexpress-media.com")

# Generic AliExpress template images served to bots/headless browsers.
# These appear on every product page regardless of the actual product.
# Filtered out so only real product images are used.
GENERIC_TEMPLATE_IMAGE_FRAGMENTS = (
    "Sb7f6dd6f36ab431db1c9c1904ba9791eP",
    "See3545d5c8384e4c8b8fcbd9510d9f99q",
    "Sf3272e722c5a4b2bbffd17cb1958eaaaH",
    "S136cdd91e1b740c898a1fc931f5176ada",
    "S01523ef93482448d8c33d410344d6a9eI",
)

# Gallery img selectors — innermost <img> children of slider wrapper divs
# (AliExpress desktop layout: slider--img--XXXX > <img src="...">)
GALLERY_SELECTORS = [
    "[class*='slider--img'] img",
    "[class*='slider--item'] img",
    "[class*='magnifier--image']",
    "[class*='image-view-v2'] img",
    "[class*='pdp-image'] img",
    "[class*='gallery'] img",
]

HERO_SELECTORS = [
    "[class*='magnifier--wrap']",
    "[class*='magnifier--image']",
    "[class*='main-image--wrap']",
    "[class*='image-view-v2--wrap']",
    "[class*='image-view']",
    "[class*='pdp-image']",
    "[class*='slider--img']",
]

PRICE_SELECTORS = [
    "[class*='price--current']",
    "[class*='currentPrice']",
    "[class*='priceText']",
    "[class*='product-price-current']",
    "[class*='price-current']",
    "[class*='uniform-banner-box-price']",
    "[class*='price']",
]

RATING_SELECTORS = [
    "[class*='review--wrap']",
    "[class*='reviewer--rating']",
    "[class*='rating--wrap']",
    "[class*='review--count']",
    "[class*='average-star']",
    "[class*='starView']",
    "[class*='star-view']",
]

REVIEW_SELECTORS = [
    "[class*='review--item']",
    "[class*='reviewItem']",
    "[class*='feedback--item']",
    "[class*='feedbackItem']",
    "[class*='comet-review-item']",
]

POPUP_CLOSE_SELECTORS = [
    "[class*='accept'] button",
    "button[data-spm-click*='accept']",
    "[class*='cookie'] button",
    "[id*='gdpr'] button",
    "[class*='country'] [class*='confirm']",
    "[class*='language'] [class*='confirm']",
    "[class*='switcher'] [class*='confirm']",
    "[class*='app-guide'] [class*='close']",
    "[class*='appGuide'] [class*='close']",
    "[class*='login'] [class*='close']",
    "[class*='dialog--close']",
    "[class*='dialog-close']",
    ".next-dialog-close",
    "[aria-label='Close']",
    "[data-role='close']",
    "[class*='close-btn']",
    "[class*='closeBtn']",
    "[class*='close-icon']",
]

# ── Check-only mode constants ─────────────────────────────────────────────────

TITLE_SELECTORS = [
    "h1[data-pl='product-title']",
    "h1.product-title-text",
    "[class*='title--wrap'] h1",
    "div[class*='product-title'] h1",
    ".product-title",
    "h1",
]

SOLD_SELECTORS = [
    "[class*='trade--wrap']",
    "[class*='sold--wrap']",
    "[class*='tradeCount']",
    "[class*='trade-count']",
    "[class*='reviewer--wrap']",       # text lives directly in the wrap, not a child span
    "[class*='reviewer--wrap'] span",  # fallback in case layout varies
]

STOCK_SELECTORS = [
    "button[data-pl='add-to-cart']",
    "[data-pl='add-to-cart']",
    "button[class*='add-to-cart']",
    "button[class*='addCart']",
    "button[aria-label*='cart' i]",
    "[class*='add-to-cart']",
]

DEAD_PAGE_PHRASES = [
    "page you requested can not be found",
    "sorry, the page",
    "this item is no longer available",
    "item is removed",
    "no longer available",
    "page not found",
    "can not be found",
]


# ── Logging ───────────────────────────────────────────────────────────────────

def phase_log(phase: int, msg: str) -> None:
    print(f"[generate_assets] Phase {phase} — {msg}", flush=True)


def retry_log(phase: int, attempt: int, reason: str) -> None:
    print(f"[generate_assets] Phase {phase} retry {attempt}/3 — {reason}", flush=True)


def warn(msg: str) -> None:
    print(f"[generate_assets] ⚠  {msg}", flush=True)


def fail_exit(reason: str, suggestion: str = "") -> None:
    print("\n❌ FAILED — REQUIRES HUMAN REVIEW", flush=True)
    print(f"Reason: {reason}", flush=True)
    if suggestion:
        print(f"Suggestion: {suggestion}", flush=True)
    sys.exit(2)


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Collect AliExpress product assets for TikTok video generation"
    )
    parser.add_argument(
        "--product-id", required=False, default=None,
        help="Product ID, e.g. 003 (required for asset collection; not needed with --check-only)",
    )
    parser.add_argument("--url", required=True, help="AliExpress product page URL")
    parser.add_argument(
        "--check-only", action="store_true",
        help="Liveness check only — render page, detect dead/live, extract data. "
             "Outputs JSON to stdout. No asset collection, no --product-id required.",
    )
    parser.add_argument(
        "--output-dir",
        default=r"C:\Automation\TikTok\assets",
        help="Base assets output directory",
    )
    parser.add_argument(
        "--max-images", type=int, default=12,
        help="Maximum product images to download (default: 12)",
    )
    parser.add_argument(
        "--headless",
        type=lambda x: x.lower() not in ("false", "0", "no"),
        default=True,
        metavar="BOOL",
        help="Run browser headlessly (default: True)",
    )
    parser.add_argument(
        "--timeout", type=int, default=30,
        help="Page load timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--no-scroll-video", action="store_true",
        help="Skip scroll video and use PNG frames instead",
    )
    return parser.parse_args()


def validate_inputs(args) -> None:
    if getattr(args, "check_only", False):
        return  # check-only validation is handled inside run_check_only()
    if not args.product_id or not re.match(r"^[0-9A-Za-z_-]+$", args.product_id):
        print("❌ Error: --product-id cannot be empty and must match [0-9A-Za-z_-]+")
        sys.exit(2)
    # Strip query params before checking — ?algo_pvid=... must not block validation
    url_path = args.url.split("?")[0]
    valid_prefixes = (
        "https://www.aliexpress.com/item/",
        "https://aliexpress.com/item/",
        "https://he.aliexpress.com/item/",
        "https://m.aliexpress.com/item/",
    )
    if not any(url_path.startswith(p) for p in valid_prefixes):
        print(
            "❌ Error: --url must be an AliExpress product URL "
            "(https://www.aliexpress.com/item/... or https://he.aliexpress.com/item/...)"
        )
        sys.exit(2)


# ── File/directory helpers ────────────────────────────────────────────────────

def create_dirs(product_dir: Path) -> None:
    for sub in ("images", "screenshots", "scroll"):
        (product_dir / sub).mkdir(parents=True, exist_ok=True)


def get_image_dims(path: Path):
    """Return (width, height) or (0, 0) on error."""
    try:
        with Image.open(path) as img:
            return img.size
    except Exception:
        return (0, 0)


def get_video_dims(path: Path):
    """Return (width, height) via ffprobe, or (0, 0) on error."""
    try:
        r = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "json",
                str(path),
            ],
            capture_output=True, text=True, timeout=15,
        )
        streams = json.loads(r.stdout).get("streams", [])
        if streams:
            return (streams[0].get("width", 0), streams[0].get("height", 0))
    except Exception:
        pass
    return (0, 0)


def file_kb(path: Path) -> int:
    try:
        return round(os.path.getsize(path) / 1024)
    except Exception:
        return 0


# ── Phase 1 helpers ───────────────────────────────────────────────────────────

def dismiss_popups(page) -> None:
    for sel in POPUP_CLOSE_SELECTORS:
        try:
            el = page.query_selector(sel)
            if el and el.is_visible():
                el.click(timeout=2000)
                page.wait_for_timeout(400)
        except Exception:
            pass


# ── Phase 2 ───────────────────────────────────────────────────────────────────

def transform_to_full_size(url: str) -> str:
    """Return the highest-quality downloadable URL for an AliExpress CDN image.

    New CDN (ae-pic-a1.aliexpress-media.com):
        Pattern: .../HASH.jpg_220x220q75.jpg_.avif
        Strip everything from the first '_NNNxNNN' suffix onward to get the
        original JPEG: .../HASH.jpg

    Old CDN (ae01.alicdn.com):
        Replace _NNxNN size suffix with _800x800.jpg.
    """
    # Remove query string entirely (handles ?has_lang=1&ver=2_220x220... edge case)
    base = url.split("?")[0]

    # New CDN: strip _WxH... transform suffix to get the original file
    m = re.match(
        r"(https?://ae-pic-a1\.aliexpress-media\.com/kf/\S+?\.(jpg|jpeg|png))",
        base,
        re.IGNORECASE,
    )
    if m:
        return m.group(1)

    # Old CDN: replace thumbnail size with 800x800
    result = re.sub(
        r"_(\d+x\d+)(Q\d+)?\.(jpg|jpeg|webp|png)",
        "_800x800.jpg",
        base,
        flags=re.IGNORECASE,
    )
    if result == base and base.lower().endswith(".webp"):
        result = base[:-5] + ".jpg"
    return result


def is_aliexpress_cdn(url: str) -> bool:
    return any(d in url for d in ALIEXPRESS_CDN_DOMAINS)


def is_generic_template(url: str) -> bool:
    """Return True if the URL is a known AliExpress generic template image."""
    return any(frag in url for frag in GENERIC_TEMPLATE_IMAGE_FRAGMENTS)


def collect_image_urls_from_page_data(page) -> list:
    """Extract product image URLs from JSON-LD and window.runParams.

    AliExpress embeds product data in JSON-LD and window.runParams even
    on bot-detected page loads. These sources bypass the gallery JS wall.
    """
    try:
        results = page.evaluate("""
            () => {
                const cdnOk = u => u && (u.includes('aliexpress-media.com') || u.includes('alicdn.com'));
                const imgs = [];

                // 1. JSON-LD structured data (most reliable)
                for (const el of document.querySelectorAll('script[type="application/ld+json"]')) {
                    try {
                        const d = JSON.parse(el.textContent);
                        const items = Array.isArray(d) ? d : [d];
                        for (const item of items) {
                            if (item['@type'] === 'Product' && item.image) {
                                const raw = Array.isArray(item.image) ? item.image : [item.image];
                                imgs.push(...raw.filter(cdnOk));
                            }
                        }
                    } catch(e) {}
                }
                if (imgs.length >= 3) return imgs;

                // 2. window.runParams (AliExpress product page data)
                try {
                    const rp = window.runParams || {};
                    const paths = (rp.data && rp.data.imageModule && rp.data.imageModule.imagePathList) || [];
                    imgs.push(...paths.filter(cdnOk));
                } catch(e) {}
                if (imgs.length >= 3) return imgs;

                // 3. __INIT_DATA__ (newer AliExpress layout)
                try {
                    const id = window.__INIT_DATA__ || {};
                    const paths = (id.data && id.data.imageModule && id.data.imageModule.imagePathList) || [];
                    imgs.push(...paths.filter(cdnOk));
                } catch(e) {}

                return imgs;
            }
        """)
        seen = set()
        unique = []
        for url in (results or []):
            full = transform_to_full_size(url)
            if full not in seen and not is_generic_template(full):
                seen.add(full)
                unique.append(full)
        return unique
    except Exception:
        return []


def collect_image_urls(page, max_images: int) -> list:
    seen = set()
    urls = []

    def add(src: str) -> bool:
        if not src or not is_aliexpress_cdn(src):
            return False
        m = re.search(r"[/_](\d+)x(\d+)", src)
        if m and int(m.group(1)) <= 60 and int(m.group(2)) <= 60:
            return False
        full = transform_to_full_size(src)
        if is_generic_template(full):
            return False
        if full not in seen:
            seen.add(full)
            urls.append(full)
        return len(urls) >= max_images

    # Priority 1: JSON-LD / window.runParams (bypass JS wall)
    for u in collect_image_urls_from_page_data(page):
        if u not in seen:
            seen.add(u)
            urls.append(u)
        if len(urls) >= max_images:
            return urls[:max_images]

    if len(urls) >= 5:
        return urls[:max_images]

    # Priority 2: CSS gallery selectors
    for sel in GALLERY_SELECTORS:
        try:
            for el in page.query_selector_all(sel):
                src = (
                    el.get_attribute("src")
                    or el.get_attribute("data-src")
                    or el.get_attribute("data-lazy-src")
                    or ""
                )
                if add(src):
                    return urls[:max_images]
        except Exception:
            pass
        if len(urls) >= 5:
            break

    # Priority 3: JS fallback — grab all img srcs (excluding generic templates)
    if len(urls) < 5:
        try:
            js_srcs = page.evaluate(
                "() => Array.from(document.querySelectorAll('img'))"
                ".flatMap(img => ["
                "  img.src || '',"
                "  img.getAttribute('data-src') || '',"
                "  img.getAttribute('data-lazy-src') || ''"
                "])"
                ".filter(s => s.includes('aliexpress-media.com') || s.includes('alicdn.com'))"
            )
            for src in js_srcs:
                if add(src):
                    return urls[:max_images]
        except Exception:
            pass

    return urls[:max_images]


def download_images(image_urls: list, images_dir: Path) -> list:
    """Download URLs. Returns list of (filepath, source_url) for successes.

    Handles both JPEG and AVIF responses: AVIF is converted to JPEG via PIL.
    If the base URL returns a non-image, the thumbnail URL is tried as fallback.
    """
    downloaded = []
    session = requests.Session()
    session.headers.update({
        "Referer": "https://he.aliexpress.com/",
        "User-Agent": DESKTOP_USER_AGENT,
        "Accept": "image/jpeg,image/png,image/*,*/*;q=0.8",
    })

    for i, url in enumerate(image_urls, start=1):
        desc = "main" if i == 1 else "detail"
        fpath = images_dir / f"{i:03d}_{desc}.jpg"
        success = False
        try_urls = [url]
        # If we stripped a suffix, also try the 800x800 version as fallback
        if "aliexpress-media.com" in url and not re.search(r"_\d+x\d+", url):
            try_urls.append(url + "_960x960q75.jpg_.avif")

        for try_url in try_urls:
            try:
                resp = session.get(try_url, timeout=15)
                resp.raise_for_status()
                ct = resp.headers.get("content-type", "")
                data = resp.content
                if len(data) < 500:
                    continue  # Too small, probably a redirect page

                # Convert AVIF/WebP → JPEG via PIL if needed
                if "avif" in ct or "webp" in ct or try_url.endswith(".avif"):
                    try:
                        img_buf = io.BytesIO(data)
                        with Image.open(img_buf) as img:
                            rgb = img.convert("RGB")
                            rgb.save(fpath, "JPEG", quality=90)
                    except Exception:
                        fpath.write_bytes(data)  # Save raw as fallback
                else:
                    fpath.write_bytes(data)

                w, h = get_image_dims(fpath)
                if w < 100 or h < 100:
                    warn(f"Image {fpath.name} too small ({w}x{h}) - skipping")
                    fpath.unlink(missing_ok=True)
                    continue
                downloaded.append((fpath, try_url))
                success = True
                break
            except Exception as e:
                warn(f"Image {i} download attempt failed ({try_url[-60:]}): {e}")

        if not success:
            warn(f"Image {i} — all download attempts failed")

    return downloaded


# ── Phase 3 ───────────────────────────────────────────────────────────────────

def screenshot_element(page, selectors: list, save_path: Path, label: str) -> bool:
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el and el.is_visible():
                el.screenshot(path=str(save_path))
                return True
        except Exception:
            pass
    warn(f"Element not found for {label} — skipping")
    return False


def capture_screenshots(page, screenshots_dir: Path) -> dict:
    results = {}

    try:
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(600)
    except Exception:
        pass

    results["main"] = screenshot_element(
        page, HERO_SELECTORS, screenshots_dir / "main.png", "main image"
    )
    results["price"] = screenshot_element(
        page, PRICE_SELECTORS, screenshots_dir / "price.png", "price section"
    )
    results["rating"] = screenshot_element(
        page, RATING_SELECTORS, screenshots_dir / "rating.png", "rating section"
    )

    results["review1"] = False
    results["review2"] = False
    try:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.65)")
        page.wait_for_timeout(1000)
        cards = []
        for sel in REVIEW_SELECTORS:
            try:
                found = page.query_selector_all(sel)
                if found:
                    cards = found
                    break
            except Exception:
                pass
        if len(cards) >= 1:
            cards[0].screenshot(path=str(screenshots_dir / "review1.png"))
            results["review1"] = True
        if len(cards) >= 2:
            cards[1].screenshot(path=str(screenshots_dir / "review2.png"))
            results["review2"] = True
    except Exception as e:
        warn(f"Review screenshots failed: {e}")

    return results


# ── Phase 4 ───────────────────────────────────────────────────────────────────

def capture_scroll(page, scroll_dir: Path, no_scroll_video: bool) -> dict:
    try:
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(500)
    except Exception:
        return {"scroll_type": "none", "scroll_frame_count": 0}

    frame_paths = []
    try:
        step = 0
        target_frames = 12
        while len(frame_paths) < target_frames:
            page.evaluate("window.scrollBy(0, 200)")
            page.wait_for_timeout(250)
            step += 1
            if step % 2 == 0:
                fn = len(frame_paths) + 1
                fp = scroll_dir / f"frame_{fn:03d}.png"
                page.screenshot(path=str(fp))
                frame_paths.append(fp)
            at_bottom = page.evaluate(
                "window.scrollY + window.innerHeight >= document.body.scrollHeight - 100"
            )
            if at_bottom and len(frame_paths) >= 6:
                break
            if step > 50:
                break
    except Exception as e:
        warn(f"Scroll frame capture error: {e}")

    if len(frame_paths) < 4:
        for fp in frame_paths:
            fp.unlink(missing_ok=True)
        return {"scroll_type": "none", "scroll_frame_count": 0}

    has_ffmpeg = shutil.which("ffmpeg") is not None
    if has_ffmpeg and not no_scroll_video:
        try:
            out_mp4 = scroll_dir / "scroll.mp4"
            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-r", "4",
                    "-i", str(scroll_dir / "frame_%03d.png"),
                    "-c:v", "libx264",
                    "-preset", "fast",
                    "-crf", "28",
                    "-pix_fmt", "yuv420p",
                    str(out_mp4),
                ],
                check=True, capture_output=True, timeout=60,
            )
            if out_mp4.exists() and out_mp4.stat().st_size > 0:
                for fp in frame_paths:
                    fp.unlink(missing_ok=True)
                return {"scroll_type": "video", "scroll_frame_count": 0}
            raise RuntimeError("scroll.mp4 empty after composition")
        except Exception as e:
            warn(f"ffmpeg scroll video failed ({e}) — falling back to frames")

    # Fallback: rename frame_NNN.png → scroll_NNN.png
    scroll_frames = []
    for i, fp in enumerate(sorted(frame_paths), start=1):
        dest = scroll_dir / f"scroll_{i:03d}.png"
        try:
            fp.rename(dest)
            scroll_frames.append(dest)
        except Exception:
            pass
    return {"scroll_type": "frames", "scroll_frame_count": len(scroll_frames)}


# ── Phase 5 ───────────────────────────────────────────────────────────────────

def build_manifest(
    product_id: str,
    source_url: str,
    product_dir: Path,
    downloaded: list,
    shot_results: dict,
    scroll_result: dict,
    retry_count: int,
    qa_passed: bool = False,
) -> dict:
    assets = []

    # Product images
    for i, (fpath, src_url) in enumerate(downloaded, start=1):
        w, h = get_image_dims(fpath)
        assets.append({
            "file_path": f"images/{fpath.name}",
            "asset_type": "product_image",
            "width": w,
            "height": h,
            "source_url": src_url,
            "index": i,
            "is_main": i == 1,
            "file_size_kb": file_kb(fpath),
        })

    image_count = len(assets)

    # Screenshots
    shot_map = [
        ("main",    "screenshot_main",   None),
        ("price",   "screenshot_price",  None),
        ("rating",  "screenshot_rating", None),
        ("review1", "screenshot_review", 1),
        ("review2", "screenshot_review", 2),
    ]
    screenshot_count = 0
    for name, atype, idx in shot_map:
        fpath = product_dir / "screenshots" / f"{name}.png"
        if shot_results.get(name) and fpath.exists():
            w, h = get_image_dims(fpath)
            assets.append({
                "file_path": f"screenshots/{name}.png",
                "asset_type": atype,
                "width": w,
                "height": h,
                "source_url": None,
                "index": idx,
                "is_main": False,
                "file_size_kb": file_kb(fpath),
            })
            screenshot_count += 1

    # Scroll assets
    scroll_type = scroll_result["scroll_type"]
    scroll_frame_count = scroll_result["scroll_frame_count"]
    scroll_dir = product_dir / "scroll"

    if scroll_type == "video":
        fpath = scroll_dir / "scroll.mp4"
        w, h = get_video_dims(fpath)
        assets.append({
            "file_path": "scroll/scroll.mp4",
            "asset_type": "scroll_video",
            "width": w,
            "height": h,
            "source_url": None,
            "index": None,
            "is_main": False,
            "file_size_kb": file_kb(fpath),
        })
    elif scroll_type == "frames":
        for fpath in sorted(scroll_dir.glob("scroll_*.png")):
            w, h = get_image_dims(fpath)
            assets.append({
                "file_path": f"scroll/{fpath.name}",
                "asset_type": "scroll_frame",
                "width": w,
                "height": h,
                "source_url": None,
                "index": None,
                "is_main": False,
                "file_size_kb": file_kb(fpath),
            })

    return {
        "product_id": product_id,
        "source_url": source_url,
        "collected_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "summary": {
            "total_assets": len(assets),
            "image_count": image_count,
            "screenshot_count": screenshot_count,
            "scroll_type": scroll_type,
            "scroll_frame_count": scroll_frame_count if scroll_type == "frames" else 0,
            "qa_passed": qa_passed,
            "retry_count": retry_count,
        },
        "assets": assets,
    }


def write_manifest(manifest: dict, manifest_path: Path) -> bool:
    try:
        text = json.dumps(manifest, indent=2, ensure_ascii=False)
        manifest_path.write_text(text, encoding="utf-8")
        json.loads(manifest_path.read_text(encoding="utf-8"))  # round-trip validate
        return True
    except Exception as e:
        warn(f"Manifest write error: {e}")
        return False


# ── Phase 6 ───────────────────────────────────────────────────────────────────

def run_qa(manifest_path: Path, product_dir: Path, manifest: dict) -> list:
    failures = []

    # QA-1: manifest exists and is valid JSON
    try:
        assert manifest_path.exists()
        json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        failures.append("QA-1: manifest.json missing or invalid JSON")
        return failures  # remaining checks require valid manifest

    # QA-2: minimum image count
    img_count = manifest["summary"]["image_count"]
    if img_count < 5:
        failures.append(
            f"QA-2: only {img_count} product images found (minimum 5 required)"
        )

    # QA-3: each product_image is readable by Pillow
    for entry in manifest["assets"]:
        if entry["asset_type"] == "product_image":
            fp = product_dir / entry["file_path"]
            try:
                with Image.open(fp) as img:
                    img.verify()
            except Exception:
                failures.append(f"QA-3: unreadable product image — {entry['file_path']}")
                break

    # QA-4: every entry has positive dimensions
    for entry in manifest["assets"]:
        if entry.get("width", 0) <= 0 or entry.get("height", 0) <= 0:
            failures.append(
                f"QA-4: zero/missing dimensions on {entry.get('file_path', '?')}"
            )
            break

    # QA-5: every entry has required fields
    required_fields = {"file_path", "asset_type", "width", "height"}
    for entry in manifest["assets"]:
        missing = required_fields - set(entry.keys())
        if missing:
            failures.append(f"QA-5: entry missing required fields: {missing}")
            break

    # QA-6: at least one screenshot entry
    has_screenshot = any(
        e["asset_type"].startswith("screenshot_") for e in manifest["assets"]
    )
    if not has_screenshot:
        failures.append("QA-6: no screenshot entries found in manifest")

    return failures


# ── Check-only mode: liveness check functions ─────────────────────────────────

def try_selector_text(page, selectors: list):
    """Return inner_text of the first matching selector, or None."""
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el:
                text = el.inner_text().strip()
                if text:
                    return text
        except Exception:
            pass
    return None


def find_text_by_pattern(page, pattern: str):
    """Scan all leaf-element text on the page for a regex pattern. Returns first match or None."""
    try:
        result = page.evaluate(
            "(pattern) => {"
            "  const re = new RegExp(pattern, 'i');"
            "  for (const el of document.querySelectorAll('*')) {"
            "    if (el.children.length === 0) {"
            "      const t = (el.textContent || '').trim();"
            "      if (re.test(t)) return t;"
            "    }"
            "  }"
            "  return null;"
            "}",
            pattern,
        )
        return result
    except Exception:
        return None


def extract_from_js_data(page) -> dict:
    """Extract product data from window.runParams or window.__INIT_DATA__.

    These JS globals are embedded in the page HTML and survive the JS wall.
    Returns a dict with keys: source, title, price_raw, sold_count_numeric,
    rating_numeric. All values may be None.
    """
    try:
        result = page.evaluate("""
            () => {
                // Method 1: window.runParams (current / older AliExpress layout)
                try {
                    const data = ((window.runParams || {}).data) || {};
                    const tm = data.titleModule || {};
                    const pm = data.priceModule || {};
                    const title = tm.subject || null;
                    const tradeCount = (typeof tm.tradeCount === 'number') ? tm.tradeCount : null;
                    const ratingVal = (tm.feedbackRating && typeof tm.feedbackRating.averageStar === 'number')
                        ? tm.feedbackRating.averageStar : null;
                    const priceAmt = pm.minActivityAmount || pm.minAmount || null;
                    const priceVal = priceAmt ? (priceAmt.formattedPrice || String(priceAmt.value) || null) : null;
                    if (title || tradeCount !== null || ratingVal !== null || priceVal) {
                        return { source: 'runParams', title, price_raw: priceVal,
                                 sold_count_numeric: tradeCount, rating_numeric: ratingVal };
                    }
                } catch(e) {}

                // Method 2: window.__INIT_DATA__ (newer AliExpress layout)
                try {
                    const data = (window.__INIT_DATA__ || {}).data || {};
                    const pic = data.productInfoComponent || {};
                    const prc = data.priceComponent || {};
                    const title = pic.subject || null;
                    const discPrice = prc.discountPrice || prc.originalPrice || null;
                    const priceVal = discPrice
                        ? (discPrice.formattedPrice || String(discPrice.value) || null)
                        : null;
                    if (title || priceVal) {
                        return { source: '__INIT_DATA__', title, price_raw: priceVal,
                                 sold_count_numeric: null, rating_numeric: null };
                    }
                } catch(e) {}

                return null;
            }
        """)
        return result or {}
    except Exception:
        return {}


def detect_dead_page(page):
    """Return dead_reason string if the page is a dead/removed listing, else None."""
    # Check 1: body text contains known dead-page phrases
    try:
        body_text = page.inner_text("body").lower()
        for phrase in DEAD_PAGE_PHRASES:
            if phrase in body_text:
                return "page_not_found"
    except Exception:
        pass

    # Check 2: URL after redirect no longer contains /item/ path
    try:
        url_path = page.url.split("?")[0].split("#")[0]
        if "/item/" not in url_path:
            return "redirect_to_homepage"
    except Exception:
        pass

    return None


def extract_listing_data(page) -> dict:
    """Extract title, price, sold count, rating, and stock status from a live page.

    Uses three layers: JS data globals → CSS selectors → regex text scan.
    Returns None for any field that cannot be found (LIVE with partial data).
    """
    result = {
        "title": None,
        "price_raw": None,
        "price_usd": None,
        "sold_count_raw": None,
        "sold_count_numeric": None,
        "rating_raw": None,
        "rating_numeric": None,
        "in_stock": None,
    }

    # Layer 1: JS data globals (most reliable — bypasses DOM/CSS changes)
    js = extract_from_js_data(page)
    if js.get("title"):
        result["title"] = js["title"]
    if js.get("price_raw"):
        result["price_raw"] = js["price_raw"]
        try:
            result["price_usd"] = float(re.sub(r"[^\d.]", "", js["price_raw"]))
        except Exception:
            pass
    if js.get("sold_count_numeric") is not None:
        cnt = js["sold_count_numeric"]
        result["sold_count_numeric"] = cnt
        result["sold_count_raw"] = f"{cnt:,}+ sold"
    if js.get("rating_numeric") is not None:
        result["rating_numeric"] = js["rating_numeric"]
        result["rating_raw"] = str(js["rating_numeric"])

    # Layer 2: CSS selectors for still-missing fields
    if not result["title"]:
        result["title"] = try_selector_text(page, TITLE_SELECTORS)

    if not result["price_raw"]:
        pt = try_selector_text(page, PRICE_SELECTORS)
        if pt:
            result["price_raw"] = pt
            try:
                result["price_usd"] = float(re.sub(r"[^\d.]", "", pt))
            except Exception:
                pass

    if not result["rating_raw"]:
        rt = try_selector_text(page, RATING_SELECTORS)
        if rt:
            m = re.search(r"\b([45]\.\d)\b", rt)
            if m:
                result["rating_raw"] = m.group(1)
                try:
                    result["rating_numeric"] = float(m.group(1))
                except Exception:
                    pass

    if not result["sold_count_raw"]:
        st = try_selector_text(page, SOLD_SELECTORS)
        if st and re.search(r"\d", st):
            # The reviewer--wrap element may contain rating + review count + sold count
            # concatenated. Target specifically the "number+ sold/נמכר" substring.
            m_sold = re.search(r"([\d,]+)\+?\s*(sold|נמכר)", st, re.IGNORECASE)
            if m_sold:
                count_str = m_sold.group(1)
                label = m_sold.group(2)
                try:
                    result["sold_count_numeric"] = int(count_str.replace(",", ""))
                    result["sold_count_raw"] = f"{count_str}+ {label}"
                except Exception:
                    pass
            else:
                # Fallback: first number sequence (may be inaccurate for compound text)
                m = re.search(r"([\d,]+)", st.replace(" ", ""))
                if m:
                    try:
                        result["sold_count_numeric"] = int(m.group(1).replace(",", ""))
                        result["sold_count_raw"] = st
                    except Exception:
                        pass

    # Layer 3: Regex text scan for any still-missing fields
    if not result["sold_count_raw"]:
        # Pattern covers English "sold" and Hebrew "נמכרו" / "נמכר"
        st = find_text_by_pattern(page, r"\d[\d,]*\+?\s*(sold|נמכר)")
        if st:
            result["sold_count_raw"] = st
            m = re.search(r"([\d,]+)", st.replace(" ", ""))
            if m:
                try:
                    result["sold_count_numeric"] = int(m.group(1).replace(",", ""))
                except Exception:
                    pass

    if not result["rating_raw"]:
        rt = find_text_by_pattern(page, r"[45]\.\d")
        if rt:
            m = re.search(r"\b([45]\.\d)\b", rt)
            if m:
                result["rating_raw"] = m.group(1)
                try:
                    result["rating_numeric"] = float(m.group(1))
                except Exception:
                    pass

    # In-stock: Add to Cart button presence
    for sel in STOCK_SELECTORS:
        try:
            if page.query_selector(sel):
                result["in_stock"] = True
                break
        except Exception:
            pass

    return result


def check_listing_liveness(url: str, timeout_seconds: int = 30, headless: bool = True) -> dict:
    """Render an AliExpress URL via Playwright and determine if the listing is live.

    Returns a dict with:
      status        — "LIVE" | "DEAD" | "UNKNOWN"
      dead_reason   — None, or a short reason string
      title/price_raw/price_usd/sold_count_raw/sold_count_numeric/
      rating_raw/rating_numeric/in_stock  — extracted product data (None if unavailable)
      url_final     — final URL after redirects
      elapsed_seconds
    """
    import time
    start = time.time()

    output = {
        "status": "UNKNOWN",
        "dead_reason": None,
        "title": None,
        "price_raw": None,
        "price_usd": None,
        "sold_count_raw": None,
        "sold_count_numeric": None,
        "rating_raw": None,
        "rating_numeric": None,
        "in_stock": None,
        "url_final": url,
        "elapsed_seconds": 0.0,
    }

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=headless)
            ctx = browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent=DESKTOP_USER_AGENT,
                locale="en-US",
            )
            page = ctx.new_page()

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=timeout_seconds * 1000)
                page.wait_for_timeout(3000)
            except PlaywrightTimeoutError:
                output["dead_reason"] = "timeout"
                output["elapsed_seconds"] = round(time.time() - start, 1)
                browser.close()
                return output
            except Exception as e:
                output["dead_reason"] = f"navigation_error: {str(e)[:120]}"
                output["elapsed_seconds"] = round(time.time() - start, 1)
                browser.close()
                return output

            output["url_final"] = page.url

            # Step 1: detect dead page
            dead_reason = detect_dead_page(page)
            if dead_reason:
                output["status"] = "DEAD"
                output["dead_reason"] = dead_reason
                output["elapsed_seconds"] = round(time.time() - start, 1)
                browser.close()
                return output

            # Step 2: extract product data
            data = extract_listing_data(page)
            output.update(data)

            # LIVE if any product signal found; UNKNOWN if page loaded but nothing extracted
            has_signal = any([output.get("title"), output.get("price_raw"), output.get("sold_count_raw")])
            output["status"] = "LIVE" if has_signal else "UNKNOWN"

            browser.close()

    except Exception as e:
        output["dead_reason"] = f"playwright_error: {str(e)[:120]}"

    output["elapsed_seconds"] = round(time.time() - start, 1)
    return output


def run_check_only(args) -> None:
    """Entry point for --check-only mode. Prints JSON result and calls sys.exit."""
    url = args.url
    if "aliexpress" not in url.lower() or "/item/" not in url:
        result = {
            "status": "UNKNOWN",
            "dead_reason": "invalid_url: must be an AliExpress /item/ URL",
            "url_final": url,
            "elapsed_seconds": 0.0,
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(1)

    result = check_listing_liveness(
        url=url,
        timeout_seconds=getattr(args, "timeout", 30),
        headless=getattr(args, "headless", True),
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["status"] in ("LIVE", "DEAD") else 1)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    # Dispatch to check-only mode before any asset-collection logic
    if getattr(args, "check_only", False):
        run_check_only(args)
        return  # run_check_only calls sys.exit — this return is a safety net

    # Asset collection requires --product-id
    if not args.product_id:
        print("❌ Error: --product-id is required for asset collection mode.")
        print("   Use --check-only to run a liveness check without asset collection.")
        sys.exit(2)

    # ── Phase 0: Setup ────────────────────────────────────────────────────────
    phase_log(0, "Setup and validation starting...")
    validate_inputs(args)

    product_dir = Path(args.output_dir) / args.product_id
    images_dir = product_dir / "images"
    screenshots_dir = product_dir / "screenshots"
    scroll_dir = product_dir / "scroll"
    manifest_path = product_dir / "manifest.json"
    create_dirs(product_dir)
    phase_log(0, f"Output: {product_dir}")

    total_retries = 0
    downloaded: list = []
    shot_results: dict = {}
    scroll_result: dict = {"scroll_type": "none", "scroll_frame_count": 0}
    manifest: dict = {}

    # ── Phases 1–4: Browser session ───────────────────────────────────────────
    phase_log(1, "Browser launch starting...")
    browser_attempt = 0

    while True:
        if browser_attempt > 3:
            fail_exit(
                "Phase 1 failed after 3 retries — could not load the AliExpress page.",
                "Check network connection, verify the URL is accessible, and try again.",
            )

        if browser_attempt > 0:
            retry_log(1, browser_attempt, "retrying browser navigation...")
            total_retries += 1

        nav_error = None
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=args.headless)
                ctx = browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    user_agent=DESKTOP_USER_AGENT,
                    locale="en-US",
                )
                page = ctx.new_page()

                # Navigate — try networkidle first, fall back to domcontentloaded
                try:
                    page.goto(
                        args.url,
                        timeout=args.timeout * 1000,
                        wait_until="networkidle",
                    )
                except PlaywrightTimeoutError:
                    page.goto(
                        args.url,
                        timeout=args.timeout * 1000,
                        wait_until="domcontentloaded",
                    )
                    page.wait_for_timeout(3000)

                phase_log(1, "Page loaded. Dismissing popups...")
                dismiss_popups(page)
                page.wait_for_timeout(2000)
                # Scroll to trigger lazy-load of gallery images
                try:
                    page.evaluate("window.scrollTo(0, 400)")
                    page.wait_for_timeout(1200)
                    page.evaluate("window.scrollTo(0, 0)")
                    page.wait_for_timeout(800)
                except Exception:
                    pass
                phase_log(1, "Browser ready.")

                # ── Phase 2: Image extraction ──────────────────────────────────
                phase_log(2, "Image extraction starting...")
                image_attempt = 0
                downloaded = []

                while True:
                    if image_attempt > 3:
                        browser.close()
                        fail_exit(
                            f"QA-2 failed after 3 retries — only {len(downloaded)} product images found on this listing.",
                            "Find an alternative AliExpress listing with 5+ product images and rerun.",
                        )

                    if image_attempt > 0:
                        retry_log(2, image_attempt, f"only {len(downloaded)} images — scrolling to trigger lazy load...")
                        total_retries += 1
                        for f in images_dir.glob("*"):
                            f.unlink()
                        downloaded = []
                        try:
                            page.evaluate("window.scrollTo(0, 500)")
                            page.wait_for_timeout(1200)
                            page.evaluate("window.scrollTo(0, 0)")
                            page.wait_for_timeout(800)
                        except Exception:
                            pass

                    image_urls = collect_image_urls(page, args.max_images)
                    downloaded = download_images(image_urls, images_dir)

                    if len(downloaded) >= 5:
                        break
                    image_attempt += 1

                phase_log(2, f"{len(downloaded)} images collected.")

                # ── Phase 3: Screenshots ───────────────────────────────────────
                phase_log(3, "Screenshots starting...")
                shot_results = capture_screenshots(page, screenshots_dir)
                n_shots = sum(1 for v in shot_results.values() if v)
                phase_log(3, f"{n_shots} screenshots captured.")

                # ── Phase 4: Scroll capture ────────────────────────────────────
                phase_log(4, "Scroll capture starting...")
                scroll_result = capture_scroll(page, scroll_dir, args.no_scroll_video)
                st = scroll_result["scroll_type"]
                if st == "video":
                    phase_log(4, "Scroll video captured.")
                elif st == "frames":
                    phase_log(4, f"Scroll captured as {scroll_result['scroll_frame_count']} PNG frames.")
                else:
                    phase_log(4, "Scroll capture skipped or failed.")

                browser.close()
            # End sync_playwright — browser session complete
            break

        except (PlaywrightTimeoutError, Exception) as e:
            nav_error = str(e)
            warn(f"Browser error (attempt {browser_attempt + 1}): {nav_error}")
            browser_attempt += 1

    # ── Phase 5: Manifest ─────────────────────────────────────────────────────
    phase_log(5, "Writing manifest...")
    man_attempt = 0

    while True:
        if man_attempt > 3:
            fail_exit(
                "Phase 5 failed after 3 retries — unable to write manifest.json.",
                "Check disk space and permissions on the output directory.",
            )

        if man_attempt > 0:
            retry_log(5, man_attempt, "manifest write failed, retrying...")
            total_retries += 1

        manifest = build_manifest(
            product_id=args.product_id,
            source_url=args.url,
            product_dir=product_dir,
            downloaded=downloaded,
            shot_results=shot_results,
            scroll_result=scroll_result,
            retry_count=total_retries,
            qa_passed=False,
        )
        if write_manifest(manifest, manifest_path):
            break
        man_attempt += 1

    phase_log(5, "manifest.json written and validated.")

    # ── Phase 6: QA ───────────────────────────────────────────────────────────
    phase_log(6, "QA checks starting...")
    qa_attempt = 0
    qa_failures = []

    while True:
        if qa_attempt > 3:
            reason = qa_failures[0] if qa_failures else "unknown QA failure"
            suggestion = ""
            if "QA-2" in reason:
                suggestion = "Find an alternative listing with 5+ product images and rerun."
            elif "QA-6" in reason:
                suggestion = "AliExpress page layout may differ — verify the URL and retry."
            fail_exit(reason, suggestion)

        qa_failures = run_qa(manifest_path, product_dir, manifest)
        if not qa_failures:
            break

        for fail in qa_failures:
            retry_log(6, qa_attempt + 1, fail)

        # Targeted recovery per failure
        needs_manifest_rewrite = any(
            k in (qa_failures[0] if qa_failures else "") for k in ("QA-1", "QA-4", "QA-5")
        )
        if needs_manifest_rewrite:
            manifest = build_manifest(
                product_id=args.product_id,
                source_url=args.url,
                product_dir=product_dir,
                downloaded=downloaded,
                shot_results=shot_results,
                scroll_result=scroll_result,
                retry_count=total_retries + 1,
                qa_passed=False,
            )
            write_manifest(manifest, manifest_path)

        total_retries += 1
        qa_attempt += 1

    # All checks passed — write final manifest with qa_passed = True
    manifest["summary"]["qa_passed"] = True
    manifest["summary"]["retry_count"] = total_retries
    write_manifest(manifest, manifest_path)
    phase_log(6, "All QA checks passed.")

    # ── Final output ──────────────────────────────────────────────────────────
    img_c = manifest["summary"]["image_count"]
    shot_c = manifest["summary"]["screenshot_count"]
    s_type = manifest["summary"]["scroll_type"]
    pid = args.product_id

    missing_optional = []
    if not shot_results.get("review1") and not shot_results.get("review2"):
        missing_optional.append("review screenshots")
    elif not shot_results.get("review2"):
        missing_optional.append("review2.png")

    if s_type == "none":
        missing_optional.append("scroll capture")
    elif s_type == "frames":
        missing_optional.append("scroll video (frames captured instead)")

    if missing_optional:
        print(
            f"\n✅ Assets collected — {img_c} images, {shot_c} screenshots "
            f"saved to assets/{pid}/",
            flush=True,
        )
        print(f"⚠️  Optional assets missing: {', '.join(missing_optional)}", flush=True)
        sys.exit(1)
    else:
        print(
            f"\n✅ Assets collected — {img_c} images, {shot_c} screenshots, "
            f"scroll video saved to assets/{pid}/",
            flush=True,
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
