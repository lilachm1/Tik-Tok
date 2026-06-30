#!/usr/bin/env python3
"""
tiktok_analytics_collect.py — Automated TikTok Creator Center analytics collector.

Detects ALL uploaded products from project files (data/*-video-config.json),
opens TikTok Creator Center using saved session cookies, collects per-video
analytics for every variant, and writes data/video_results.csv (33-col v2).

No username/password stored. No 2FA bypass. Read-only access only.
The browser window stays visible so you can intervene if TikTok challenges you.

Usage:
    python scripts/tiktok_analytics_collect.py
    python scripts/tiktok_analytics_collect.py --product-id 007
    python scripts/tiktok_analytics_collect.py --product-id 007,008
    python scripts/tiktok_analytics_collect.py --update    # re-collect existing rows
"""

import argparse
import csv
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright, Page, TimeoutError as PWTimeout

# ── Paths ──────────────────────────────────────────────────────────────────

PROJECT_ROOT  = Path(__file__).resolve().parent.parent
DATA_DIR      = PROJECT_ROOT / "data"
OUTPUT_DIR    = PROJECT_ROOT / "output"
SESSION_FILE  = DATA_DIR / "tiktok-session.json"
CSV_FILE      = DATA_DIR / "video_results.csv"
ANALYTICS_DIR = DATA_DIR / "tiktok-analytics"

# ── CSV Schema ─────────────────────────────────────────────────────────────
# 33-column v2 — must match tiktok-collect.md exactly

CSV_HEADER = [
    "product_id", "variant", "hook_type", "category", "price_ils",
    "views", "likes", "comments", "saves", "winner", "cta_style",
    "asset_source", "best_segment", "upload_date", "upload_time",
    "age_hours", "variant_status", "tracking_id", "affiliate_clicks",
    "affiliate_sales", "affiliate_commission", "hook_text", "shares",
    "average_watch_time", "retention_rate", "watched_full_video_rate",
    "first_2_second_retention", "cta_code_comments", "engagement_rate",
    "save_rate", "comment_rate", "share_rate", "cta_comment_rate",
]

DESKTOP_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

CONTENT_TAB_URL = "https://www.tiktok.com/tiktokstudio/content"

# Partial URL fragments that appear in TikTok analytics XHR responses
ANALYTICS_URL_FRAGMENTS = [
    "/api/item/",
    "item_id",
    "retain_user",
    "video_analytics",
    "creator/analytics",
    "video_detail",
    "play_data",
]

# ── Virtualized-list scrolling + Hebrew-safe row matching ──────────────────
#
# Root cause (PROJECT_STATUS.md, 2026-06-30 Product 002 investigation):
# TikTok Studio's content list lives in a nested overflow:auto div
# (scrollHeight ~1610 vs clientHeight ~528) — it is virtualized, so rows far
# from the current scroll position aren't even in the DOM yet. `window.
# scrollBy` / `window.scrollY` never reach this container (confirmed stuck at
# ~30px no matter how many times it's called). This silently affected any
# product far enough down the list (older uploads pushed down by newer ones)
# — it just went unnoticed for 007/008 because they're recent enough to sit
# within the list's initial render window.
#
# Separately, Playwright's `text=` locator engine returned 0 matches for a
# known-present Hebrew caption substring even after correctly scrolling —
# confirmed unreliable for Hebrew/RTL text. Raw JS `textContent.includes()`
# scanning works immediately and is used below instead.

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

JS_SCAN_SUBSTRING = """(substr) => {
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
        if (seenRows.some(sr => Math.abs(sr.y - rr.y) < 10)) continue;
        seenRows.push({y: rr.y});
        let href = '';
        const a = rowNode.querySelector('a') || rowNode.closest('a');
        if (a) href = a.getAttribute('href') || '';
        found.push({x: rr.x, y: rr.y, width: rr.width, height: rr.height, text: t.slice(0, 200), href});
    }
    return found;
}"""


def get_scroll_top(page):
    try:
        return page.evaluate(JS_GET_SCROLLTOP) or 0
    except Exception:
        return 0


def scroll_container(page, frac=0.7):
    """Scroll the real virtualized content-list container (not window)."""
    try:
        return page.evaluate(JS_SCROLL_CONTAINER, frac)
    except Exception:
        return None


def find_all_caption_matches(page, substring, max_scrolls=30):
    """
    Scroll the real content-list container and collect every row whose
    caption contains `substring`, returning each row's href/video ID. Used
    for bare-CTA products where the CTA code alone can't disambiguate
    variants. Returns a list of {href, video_id, text}, deduped by absolute
    row position. Stops early once scrolling stagnates (reached the bottom).
    """
    seen_y = []
    results = []
    last_scroll_top = -1
    stagnant = 0

    for _ in range(max_scrolls):
        try:
            candidates = page.evaluate(JS_SCAN_SUBSTRING, substring)
        except Exception:
            candidates = []
        scroll_y = get_scroll_top(page)

        for cand in candidates:
            abs_y = round(cand["y"] + scroll_y)
            if any(abs(abs_y - y) < 50 for y in seen_y):
                continue
            seen_y.append(abs_y)
            href = cand.get("href", "")
            video_id = href.rstrip("/").split("/")[-1] if href else ""
            results.append({"href": href, "video_id": video_id, "text": cand["text"], "abs_y": abs_y})

        moved = scroll_container(page, 0.7)
        if moved is not None and moved == last_scroll_top:
            stagnant += 1
            if stagnant >= 3:
                break
        else:
            stagnant = 0
        last_scroll_top = moved
        time.sleep(1.2)

    return results


def scroll_until_row_visible(page, video_id, max_scrolls=30):
    """
    Scroll the real content-list container until the row linking to
    `video_id` is rendered, then return its Locator. href is plain ASCII
    (no Hebrew/RTL matching issues), so a normal CSS attribute selector is
    safe and reliable here, unlike Hebrew caption/CTA text matching.
    """
    selector = f"a[href*='{video_id}']"
    last_scroll_top = -1
    stagnant = 0
    for _ in range(max_scrolls):
        try:
            el = page.locator(selector).first
            if el.is_visible(timeout=500):
                return el
        except Exception:
            pass
        moved = scroll_container(page, 0.7)
        if moved is not None and moved == last_scroll_top:
            stagnant += 1
            if stagnant >= 3:
                break
        else:
            stagnant = 0
        last_scroll_top = moved
        time.sleep(1.2)
    return None


def load_identity_map(pid):
    """
    Load data/{pid}-identity-map.json if present: {video_id: variant_letter}.
    Required for bare-CTA products (e.g. Product 002) where every variant
    shares an identical caption and CTA code, so neither can disambiguate
    them. Built once via visual hook-text confirmation (each variant's
    video-config bakes a unique hook overlay into the video pixels at 0-2s,
    independent of the shared caption — see PROJECT_STATUS.md, 2026-06-30),
    then reused automatically on every future run.
    """
    path = DATA_DIR / f"{pid}-identity-map.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"  WARNING: could not read {path.name}: {exc}")
        return {}


def gather_visual_evidence(page, pid, caption_search_text, out_dir):
    """
    For a bare-CTA product with NO identity map yet: enumerate all matching
    video rows by caption substring, open each video directly, and
    force-seek its <video> element to t=0.15s (the hook-text overlay window,
    0-2s) so a human/agent can visually match it against the per-variant
    hook strings in data/{pid}-video-config.json. Does NOT guess identity —
    only gathers evidence. Pair with load_identity_map(): once confirmed,
    save data/{pid}-identity-map.json and rerun with --update.
    """
    matches = find_all_caption_matches(page, caption_search_text)
    out_dir.mkdir(parents=True, exist_ok=True)
    evidence = []
    for m in matches:
        vid = m["video_id"]
        href = m["href"]
        if not vid or not href:
            continue
        url = f"https://www.tiktok.com{href}" if href.startswith("/") else href
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30_000)
            time.sleep(3)
        except Exception as exc:
            print(f"    evidence nav error for {vid}: {exc}")
            continue

        state = {"found": False}
        for _ in range(5):
            try:
                state = page.evaluate("""() => {
                    const v = document.querySelector('video');
                    if (!v) return {found: false};
                    v.pause();
                    v.currentTime = 0.15;
                    return {found: true};
                }""")
            except Exception:
                pass
            time.sleep(0.4)
            if state.get("found"):
                break

        shot_path = out_dir / f"hook_{vid}.png"
        try:
            page.screenshot(path=str(shot_path))
        except Exception as exc:
            print(f"    screenshot failed for {vid}: {exc}")
            shot_path = None

        evidence.append({"video_id": vid, "href": href, "screenshot": str(shot_path) if shot_path else None})

        try:
            page.goto(CONTENT_TAB_URL, wait_until="domcontentloaded", timeout=30_000)
            time.sleep(2)
        except Exception:
            pass

    return evidence


# ── Product auto-detection ─────────────────────────────────────────────────

def extract_caption_from_upload_package(product_id, variant_letter):
    """
    Extract TikTok caption text for a specific variant from its upload package.
    Returns the caption string, or None if not found.
    """
    pkg_files = list(OUTPUT_DIR.glob(f"*-product-{product_id}-upload_package.md"))
    if not pkg_files:
        return None

    try:
        text = pkg_files[0].read_text(encoding="utf-8")
    except Exception:
        return None

    # Find the variant section header
    variant_pattern = f"## VARIANT {variant_letter}"
    if variant_pattern not in text:
        return None

    # Extract text after the variant header
    start = text.index(variant_pattern)
    section = text[start:start+2000]  # Look ahead 2000 chars

    # Find CAPTION: line
    for line in section.split('\n'):
        if line.startswith('CAPTION:'):
            caption = line.replace('CAPTION:', '').strip()
            if caption:  # Not empty
                return caption
            # Caption might be on next line
            lines = section.split('\n')
            idx = lines.index(line)
            if idx + 1 < len(lines):
                next_line = lines[idx + 1].strip()
                if next_line and not next_line.startswith('#'):
                    return next_line

    return None


def detect_all_products(filter_ids=None):
    """
    Scan data/*-video-config.json to build manifest of all products.

    Returns dict: {product_id_str → {product_id, upload_date, price_ils,
                                      category, variants: {letter → {...}}}}
    """
    products = {}

    for cfg_path in sorted(DATA_DIR.glob("*-video-config.json")):
        stem = cfg_path.stem.lower()
        if any(x in stem for x in ("test", "legacy", "temp", "backup")):
            continue

        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"  WARNING: cannot read {cfg_path.name}: {exc}")
            continue

        raw_id = str(cfg.get("product_id", "")).strip()
        if not raw_id:
            continue
        pid = raw_id.zfill(3)

        if filter_ids and pid not in filter_ids:
            continue

        products[pid] = {
            "product_id":  pid,
            "upload_date": cfg.get("date", ""),
            "price_ils":   cfg.get("price_ils", ""),
            "category":    cfg.get("category", ""),
            "variants":    {},
        }

        for vcfg in cfg.get("variants", []):
            letter = vcfg.get("id", "")
            if not letter:
                continue

            segs = vcfg.get("segments", [])

            # CTA code: last segment containing a NNNx pattern, e.g. "007A"
            # Bare-code fallback: "002" without variant letter (pre-June-14 products)
            cta_code = None
            bare_index = None
            for seg in reversed(segs):
                text = seg.get("text", "")
                m = re.search(r"\b(\d{3}[A-D])\b", text)
                if m:
                    cta_code = m.group(1)
                    break
                if cta_code is None:
                    m_bare = re.search(r"\b(\d{3})\b", text)
                    if m_bare:
                        cta_code = m_bare.group(1)  # e.g. "002"
                        bare_index = "ABCD".index(letter) if letter in "ABCD" else 0
            if not cta_code:
                cta_code = pid

            hook_text = segs[0]["text"] if segs else ""

            # Extract TikTok caption from upload package for search
            caption = extract_caption_from_upload_package(pid, letter)
            caption_search_text = caption[:30].strip() if caption else ""

            products[pid]["variants"][letter] = {
                "variant":     f"{pid}{letter}",
                "hook_type":   vcfg.get("hook_type", ""),
                "hook_text":   hook_text,
                "caption_search_text": caption_search_text,
                "cta_code":    cta_code,
                "cta_style":   "comment",
                "tracking_id": f"product{pid}_{letter}",
                "bare_index":  bare_index,  # None = per-variant code; 0-3 = bare code
            }

    # Attach confirmed video IDs from a manually-curated identity map, if any
    # (required for bare-CTA products where caption/CTA cannot disambiguate
    # variants — see load_identity_map() docstring).
    for pid, prod in products.items():
        identity_map = load_identity_map(pid)
        if not identity_map:
            continue
        reverse_map = {letter: vid for vid, letter in identity_map.items()}
        for letter, vinfo in prod["variants"].items():
            vid = reverse_map.get(letter)
            if vid:
                vinfo["video_id"] = vid

    return products


# ── CSV helpers ────────────────────────────────────────────────────────────

def load_existing_csv():
    """Return dict: {(product_id, variant) → row_dict}"""
    if not CSV_FILE.exists():
        return {}
    rows = {}
    try:
        with open(CSV_FILE, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                key = (row.get("product_id", ""), row.get("variant", ""))
                rows[key] = dict(row)
    except Exception as exc:
        print(f"  WARNING: could not read {CSV_FILE.name}: {exc}")
    return rows


def verify_csv_header():
    """Return True if CSV has the correct 33-column v2 header."""
    try:
        with open(CSV_FILE, encoding="utf-8", newline="") as f:
            header = next(csv.reader(f), [])
        return header == CSV_HEADER
    except Exception:
        return False


def write_csv(new_rows, existing):
    """
    Merge new_rows into existing rows and write video_results.csv.
    new_rows overrides matching (product_id, variant) keys in existing.
    """
    merged = dict(existing)
    for row in new_rows:
        key = (row.get("product_id", ""), row.get("variant", ""))
        merged[key] = {k: row.get(k, "") for k in CSV_HEADER}

    sorted_rows = sorted(
        merged.values(),
        key=lambda r: (r.get("product_id", ""), r.get("variant", "")),
    )

    CSV_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(sorted_rows)

    print(f"\n  CSV written: {CSV_FILE.relative_to(PROJECT_ROOT)}  ({len(sorted_rows)} total rows)")


# ── Playwright session ─────────────────────────────────────────────────────

def launch_with_session(playwright):
    """Load session cookies and return (browser, context)."""
    if not SESSION_FILE.exists():
        print(f"\nERROR: Session file not found: {SESSION_FILE}")
        print("Run: python scripts/tiktok_session_login.py")
        sys.exit(1)

    browser = playwright.chromium.launch(
        headless=False,
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
    )
    context = browser.new_context(
        storage_state=str(SESSION_FILE),
        viewport=None,
        user_agent=DESKTOP_UA,
    )
    return browser, context


def check_session_valid(page):
    """Navigate to Creator Center; return True if session is still active."""
    try:
        page.goto(CONTENT_TAB_URL, wait_until="domcontentloaded", timeout=30_000)
        time.sleep(3)
        url = page.url
        if "login" in url.lower() or "passport" in url.lower():
            return False
        return True
    except Exception:
        return False


# ── Network response interception ──────────────────────────────────────────

def install_capture(page):
    """
    Install a response listener. Returns the shared captures list that fills
    as TikTok's analytics XHR responses arrive.
    """
    captures = []

    def _on_response(resp):
        if resp.status not in (200, 201):
            return
        url = resp.url
        if not any(frag in url for frag in ANALYTICS_URL_FRAGMENTS):
            return
        ct = resp.headers.get("content-type", "")
        if "json" not in ct and "javascript" not in ct:
            return
        try:
            body = resp.json()
            captures.append({"url": url, "body": body})
        except Exception:
            try:
                raw = resp.text()
                if len(raw) > 30:
                    captures.append({"url": url, "body": raw})
            except Exception:
                pass

    page.on("response", _on_response)
    return captures


def _try_int(data, keys):
    for k in keys:
        v = data.get(k)
        if v is not None:
            try:
                return str(int(float(v)))
            except (ValueError, TypeError):
                pass
    return ""


def _try_rate(data, keys):
    """Extract a 0–1 float (normalise from 0–100 if needed)."""
    for k in keys:
        v = data.get(k)
        if v is not None:
            try:
                f = float(v)
                if f > 1.0:
                    f = f / 100.0
                return f"{f:.4f}"
            except (ValueError, TypeError):
                pass
    return ""


def parse_captures(captures):
    """
    Walk all captured JSON blobs and extract engagement + retention metrics.
    Returns a dict of metric field names → string values (empty if not found).
    """
    m = {
        "views": "", "likes": "", "comments": "", "saves": "", "shares": "",
        "average_watch_time": "", "retention_rate": "", "watched_full_video_rate": "",
        "first_2_second_retention": "",
    }

    for cap in captures:
        body = cap["body"]
        if not isinstance(body, dict):
            continue
        # TikTok wraps response under "data", sometimes nested further
        data = body.get("data", body)
        if not isinstance(data, dict):
            continue

        if not m["views"]:
            m["views"] = _try_int(data, ["play_count", "vv", "views", "view_count", "video_views"])
        if not m["likes"]:
            m["likes"] = _try_int(data, ["like_count", "digg_count", "likes", "heart"])
        if not m["comments"]:
            m["comments"] = _try_int(data, ["comment_count", "comments"])
        if not m["saves"]:
            m["saves"] = _try_int(data, ["collect_count", "favorite_count", "saves", "bookmark"])
        if not m["shares"]:
            m["shares"] = _try_int(data, ["share_count", "forward_count", "shares"])

        if not m["average_watch_time"]:
            m["average_watch_time"] = _try_rate(
                data, ["average_watch_time", "avg_watch_duration", "avg_time_watched"]
            )
        if not m["retention_rate"]:
            m["retention_rate"] = _try_rate(
                data, ["video_completion_rate", "complete_rate", "completion_rate"]
            )
        if not m["watched_full_video_rate"]:
            m["watched_full_video_rate"] = _try_rate(
                data, ["watched_full_video_rate", "finish_rate", "full_play_rate"]
            )

        # Retention curve: array where index 2 = 2-second retention
        if not m["first_2_second_retention"]:
            for key in ("retain_user_ratio", "retention_curve", "audience_retention",
                        "audience_active", "video_retention_curve"):
                arr = data.get(key)
                if isinstance(arr, list) and len(arr) >= 3:
                    try:
                        val = float(arr[2])
                        if val > 1.0:
                            val = val / 100.0
                        m["first_2_second_retention"] = f"{val:.4f}"
                    except (ValueError, TypeError):
                        pass
                    break

    return m


# ── TikTok navigation ──────────────────────────────────────────────────────

def _parse_tiktok_count(text):
    """'1.2K' → '1200', '133' → '133'. Empty string on failure."""
    text = text.strip().replace(",", "")
    if text.endswith(("K", "k")):
        try:
            return str(int(float(text[:-1]) * 1_000))
        except ValueError:
            return ""
    if text.endswith(("M", "m")):
        try:
            return str(int(float(text[:-1]) * 1_000_000))
        except ValueError:
            return ""
    try:
        return str(int(float(text)))
    except ValueError:
        return ""


def _scrape_row(el):
    """
    Extract Views/Likes/Comments from the content-list row containing el.

    TikTok Creator Center uses a split-column layout: the title <A> and the
    numeric cells are in separate DOM subtrees, so ancestor-walking fails.
    Strategy: scroll el into the center of the viewport, then scan elements
    across the viewport width at el's Y using elementFromPoint(). Deduplicates
    by DOM element reference (not proximity) to avoid double-counting.
    The first three unique numeric elements found (left-to-right) are
    Views, Likes, Comments.
    Returns {"views", "likes", "comments"} as strings; empty strings on failure.
    """
    try:
        # Ensure el is in viewport center; then nudge if it landed in the
        # fixed sticky-header zone (< 180px from top), which causes
        # elementFromPoint to hit the header overlay instead of data cells.
        try:
            el.evaluate("el => el.scrollIntoView({block: 'center', inline: 'nearest'})")
            time.sleep(0.4)
            el.evaluate("""el => {
                const t = el.getBoundingClientRect().top;
                if (t < 180) window.scrollBy(0, -(200 - Math.round(t)));
            }""")
            time.sleep(0.3)
        except Exception:
            pass

        raw = el.evaluate(r"""el => {
            const rect = el.getBoundingClientRect();
            const rowY = rect.top + rect.height / 2;
            const W = window.innerWidth;
            const H = window.innerHeight;

            // Scan right half of viewport at the row's Y position.
            // Deduplicate by DOM element reference so the same element
            // is only counted once regardless of how many scan steps hit it.
            const seenEls = new Set();
            const nums = [];
            for (let x = Math.round(W * 0.35); x < W - 30; x += 20) {
                const target = document.elementFromPoint(x, rowY);
                if (!target || seenEls.has(target)) continue;
                const text = target.innerText.trim().split('\n')[0].trim();
                if (!/^\d[\d,\.]*[KkMm]?$/.test(text) || text.length > 10) {
                    seenEls.add(target);
                    continue;
                }
                seenEls.add(target);
                nums.push({x: Math.round(x), text});
            }
            return {rowY: Math.round(rowY), H, W, nums};
        }""")

        found = raw.get("nums", [])
        texts = [s["text"] for s in found]
        print(f"    _scrape_row: rowY={raw.get('rowY')} H={raw.get('H')} W={raw.get('W')}  raw_nums={texts}")

        nums = [_parse_tiktok_count(t) for t in texts]
        result = {
            "views":    nums[0] if len(nums) > 0 else "",
            "likes":    nums[1] if len(nums) > 1 else "",
            "comments": nums[2] if len(nums) > 2 else "",
        }
        print(f"    _scrape_row: → views={result['views']} likes={result['likes']} comments={result['comments']}")
        return result
    except Exception as exc:
        print(f"    _scrape_row: exception — {exc}")
        return {"views": "", "likes": "", "comments": ""}


def scroll_and_find_video(page, cta_code, max_scrolls=25, skip_count=0, hook_text=""):
    """
    Scroll through Creator Center Content tab searching for a video by CTA code.

    skip_count: how many matching elements to skip before clicking.
      0  = click the first match (per-variant codes like "007A").
      N  = skip N matches, then click the (N+1)th — used for bare-code products
           where all variants share the same search term (e.g. "002").
           A=0, B=1, C=2, D=3.

    hook_text: unused in this function (used by search_box_find). Kept for
      signature compatibility with collect_one_variant.

    Returns (True, row_metrics_dict) on success, (False, {}) if not found.
    row_metrics_dict has keys: views, likes, comments (scraped from the list row).
    """
    selectors = [
        f"text={cta_code}",
        f"[aria-label*='{cta_code}']",
        f"[title*='{cta_code}']",
    ]

    if skip_count == 0:
        # Fast path — first visible match wins (per-variant codes, no ambiguity)
        for scroll_i in range(max_scrolls):
            for sel in selectors:
                try:
                    el = page.locator(sel).first
                    if el.is_visible(timeout=800):
                        print(f"    Found after {scroll_i} scroll(s)")
                        row_m = _scrape_row(el)
                        el.click()
                        return True, row_m
                except Exception:
                    pass
            scroll_container(page, 0.8)
            time.sleep(2.0)
        return False, {}

    # Skip path — count unique video cards by absolute page Y, skip first N (bare codes)
    # Uses el.bounding_box() instead of el.evaluate() to avoid cross-frame JS exceptions.
    # Height filter (< 100px) targets leaf text elements, not container divs.
    # 50px Y tolerance to group elements within the same video card.
    seen_y = []   # absolute-Y positions of video cards already counted
    skipped = 0

    for scroll_i in range(max_scrolls):
        try:
            scroll_y = page.evaluate("() => window.scrollY")
        except Exception:
            scroll_y = 0
        for sel in selectors:
            try:
                for el in page.locator(sel).all():
                    try:
                        if not el.is_visible(timeout=400):
                            continue
                        bbox = el.bounding_box()
                        if bbox is None:
                            continue
                        # Skip container divs — only count leaf text nodes
                        if bbox["height"] > 100:
                            continue
                        abs_y = round(bbox["y"] + scroll_y)
                        if any(abs(abs_y - y) < 50 for y in seen_y):
                            continue  # same video card seen already
                        seen_y.append(abs_y)
                        if skipped < skip_count:
                            skipped += 1
                            continue
                        print(f"    Found after {scroll_i} scroll(s) (skipped {skipped})")
                        row_m = _scrape_row(el)
                        el.click()
                        return True, row_m
                    except Exception:
                        pass
            except Exception:
                pass
        scroll_container(page, 0.8)
        time.sleep(2.0)
    return False, {}


def click_analytics_tab(page):
    """Try to click the Analytics/Insights tab within a video detail view."""
    for sel in (
        "text=Analytics", "text=analytics",
        "[class*='analytics'][role='tab']", "[href*='analytics']",
    ):
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=2_000):
                el.click()
                time.sleep(2)
                return
        except Exception:
            pass


def search_box_find(page, caption_search_text, cta_code):
    """
    Use TikTok Studio's 'Search post description' input to filter the content
    list by caption_search_text (first 20-30 chars of the TikTok caption),
    then confirm identity via CTA code or unique single result.

    Avoids Playwright text= locators with Hebrew/RTL text, which are unreliable.
    Returns (True, row_metrics) or (False, {}).
    """
    query = caption_search_text.strip() if caption_search_text else ""
    if not query:
        return False, {}

    try:
        box = page.locator("input[placeholder*='Search']").first
        if not box.is_visible(timeout=3_000):
            print("    search_box_find: search input not visible")
            return False, {}

        box.click()
        box.fill(query)
        time.sleep(2.5)  # wait for TikTok to filter results

        # Detect bare code: 3 digits only (e.g., "002"), not variant-level (e.g., "002A")
        is_bare_code = bool(re.match(r'^\d{3}$', cta_code))

        # 1. Try CTA code selector — ONLY if variant-level code
        #    Bare codes shared across variants cannot confirm identity.
        if not is_bare_code:
            for sel in [f"text={cta_code}", f"[aria-label*='{cta_code}']"]:
                try:
                    el = page.locator(sel).first
                    if el.is_visible(timeout=2_000):
                        print(f"    search_box_find: CTA confirmed [{sel[:25]}]")
                        row_m = _scrape_row(el)
                        el.click()
                        return True, row_m
                except Exception:
                    pass

        # 2. CTA truncated OR bare code: count visible video-row links.
        #    TikTok Studio sidebar ends at ~x=250; content list starts beyond that.
        #    Require x > 300 to skip sidebar nav links; width > 80 to skip icon buttons.
        visible_videos = []
        for el in page.locator("a").all():
            try:
                if not el.is_visible(timeout=300):
                    continue
                bbox = el.bounding_box()
                if bbox and bbox["x"] > 300 and bbox["width"] > 80:
                    visible_videos.append(el)
            except Exception:
                pass

        # For bare-code products with shared captions, identity cannot be confirmed
        # via search because we can't distinguish between variants.
        if is_bare_code:
            print(f"    search_box_find: NOT FOUND (bare code '{cta_code}' — identity unconfirmable via search)")
            return False, {}

        # For variant-level codes: exactly 1 visible row confirms identity
        if len(visible_videos) == 1:
            el = visible_videos[0]
            print(f"    search_box_find: unique result confirmed (1 video visible)")
            row_m = _scrape_row(el)
            el.click()
            return True, row_m
        elif len(visible_videos) == 0:
            print("    search_box_find: NOT FOUND (0 videos visible)")
            return False, {}
        else:
            print(f"    search_box_find: NOT FOUND ({len(visible_videos)} videos visible — identity unconfirmed)")
            return False, {}
    except Exception as exc:
        print(f"    search_box_find: exception — {exc}")
        return False, {}


# ── Per-variant collection ─────────────────────────────────────────────────

def collect_one_variant(page, cta_code, skip_count=0, caption_search_text="", video_id=None):
    """
    Navigate to and collect metrics for the video identified by cta_code.

    caption_search_text: TikTok caption prefix for search filtering.
    skip_count: passed through for bare-code products (legacy fallback only
      — superseded by video_id when a confirmed identity map exists).
    video_id: confirmed TikTok video ID from data/{pid}-identity-map.json.
      When present, this is the ONLY safe way to find the right row for a
      bare-CTA variant (href is plain ASCII, unambiguous, and unique per
      variant even though caption/CTA are shared — see load_identity_map()).
      Tried first; falls back to caption/CTA matching if not found.

    Returns a dict:
      {"not_found": True}               — video not found on TikTok
      {"not_found": False, <metrics>}   — metrics extracted (may be partial)
    """
    captures = install_capture(page)

    # Reset to content list — TikTok may redirect creator-center → tiktokstudio
    try:
        page.goto(CONTENT_TAB_URL, wait_until="domcontentloaded", timeout=30_000)
    except Exception as nav_err:
        err_str = str(nav_err)
        if "interrupted" in err_str and "tiktokstudio" in err_str:
            time.sleep(2)  # let the redirect complete
        elif "Timeout" in err_str or "timeout" in err_str:
            print(f"    Timeout navigating to content tab")
            return {"not_found": True}
        else:
            print(f"    Nav error: {err_str[:120]}")
            return {"not_found": True}
    time.sleep(3)

    found, row_metrics = False, {}

    if video_id:
        el = scroll_until_row_visible(page, video_id)
        if el is not None:
            print(f"    Found by confirmed video ID {video_id}")
            row_metrics = _scrape_row(el)
            el.click()
            found = True

    if not found and caption_search_text:
        found, row_metrics = search_box_find(page, caption_search_text, cta_code)
        if not found:
            found, row_metrics = scroll_and_find_video(page, cta_code, skip_count=skip_count)
    elif not found:
        found, row_metrics = scroll_and_find_video(page, cta_code, skip_count=skip_count)
    if not found:
        return {"not_found": True}

    # Wait for video detail to load and analytics XHR to fire
    time.sleep(3)
    click_analytics_tab(page)

    # Allow up to 12 seconds for API captures to accumulate
    for _ in range(12):
        if captures:
            time.sleep(2)
            break
        time.sleep(1)

    # Screenshot for QA evidence
    try:
        ss_dir = ANALYTICS_DIR / f"product{cta_code[:3]}"
        ss_dir.mkdir(parents=True, exist_ok=True)
        page.screenshot(
            path=str(ss_dir / f"{cta_code}_analytics.png"),
            full_page=False,
        )
    except Exception:
        pass

    metrics = parse_captures(captures)
    # Fill views/likes/comments from DOM row scrape where XHR returned nothing
    for field in ("views", "likes", "comments"):
        if not metrics.get(field):
            metrics[field] = row_metrics.get(field, "")
    metrics["not_found"] = False
    return metrics


# ── Row assembly and derived fields ────────────────────────────────────────

def compute_derived(row):
    """Compute age_hours, rates, engagement_rate, variant_status in place."""
    upload_date = row.get("upload_date", "")
    if upload_date:
        try:
            upload_dt = datetime.strptime(upload_date, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
            age_h = (datetime.now(tz=timezone.utc) - upload_dt).total_seconds() / 3600
            row["age_hours"] = f"{age_h:.1f}"
        except ValueError:
            pass

    try:
        v = float(row.get("views") or 0)
        if v > 0:
            likes        = float(row.get("likes")            or 0)
            saves        = float(row.get("saves")            or 0)
            comments     = float(row.get("comments")         or 0)
            shares       = float(row.get("shares")           or 0)
            cta_comments = float(row.get("cta_code_comments") or 0)

            row["engagement_rate"]  = f"{(likes + saves + comments + shares) / v:.4f}"
            row["save_rate"]        = f"{saves    / v:.4f}"
            row["comment_rate"]     = f"{comments / v:.4f}"
            row["share_rate"]       = f"{shares   / v:.4f}"
            row["cta_comment_rate"] = f"{cta_comments / v:.4f}"
    except (ValueError, TypeError):
        pass

    if not row.get("variant_status"):
        age_h = float(row.get("age_hours") or 0)
        row["variant_status"] = "CONFIRMED" if age_h >= 24 else "PENDING"

    return row


def prompt_manual_fields(cta_code):
    """Return blank values for all optional manual fields — no prompting."""
    return {
        "cta_code_comments":    "",
        "affiliate_clicks":     "",
        "affiliate_sales":      "",
        "affiliate_commission": "",
    }


# ── QA report ─────────────────────────────────────────────────────────────

def print_qa_report(products, result_records, existing_before):
    total_variants = sum(len(p["variants"]) for p in products.values())
    found    = [r for r in result_records if not r["not_found"] and not r.get("skipped") and not r.get("pending_visual")]
    missing  = [r for r in result_records if r["not_found"]]
    skipped  = [r for r in result_records if r.get("skipped")]
    pending  = [r for r in result_records if r.get("pending_visual")]
    has_ret  = [r for r in found if r.get("first_2_second_retention")]
    has_views = [r for r in found if r.get("views") and r["views"] != "NOT_FOUND"]

    csv_ok     = CSV_FILE.exists() and verify_csv_header()
    ret_ok     = len(has_ret) > 0
    session_ok = SESSION_FILE.exists()
    match_ok   = len(missing) == 0

    print()
    print("=" * 62)
    print("COLLECTOR QA REPORT")
    print(f"Run : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 62)
    print(f"Products  : {len(products)}  ({', '.join(sorted(products))})")
    print(f"Expected  : {total_variants} variants")
    print(f"Collected : {len(found)}")
    print(f"Not found : {len(missing)}")
    print(f"Skipped   : {len(skipped)}  (existing rows; use --update to re-collect)")
    if pending:
        print(f"Pending visual confirmation : {len(pending)}  (bare-CTA, no identity map yet — see output/identify_*/)")
    print()
    print("Data quality:")
    print(f"  Views extracted        : {len(has_views)}/{len(found)}")
    print(f"  2-sec retention data   : {len(has_ret)}/{len(found)}")
    print()
    print("Per-variant:")
    for r in sorted(result_records, key=lambda x: x.get("cta_code", "")):
        code = r.get("cta_code", "?")
        if r.get("pending_visual"):
            print(f"  {code:<8}  PENDING VISUAL CONFIRMATION — create data/{r.get('product_id')}-identity-map.json")
        elif r.get("skipped"):
            print(f"  {code:<8}  SKIPPED")
        elif r["not_found"]:
            print(f"  {code:<8}  NOT FOUND")
        else:
            v   = r.get("views") or "-"
            ret = r.get("first_2_second_retention") or "-"
            print(f"  {code:<8}  OK   views={v}  2s_ret={ret}")

    print()
    print("QA Gates:")
    print(f"  1. Login / session     : {'PASS' if session_ok else 'FAIL — run tiktok_session_login.py'}")
    print(f"  2. Video matching      : {'PASS' if match_ok else f'PARTIAL — {len(missing)} variant(s) not found'}")
    print(f"  3. Data extraction     : {'PASS' if ret_ok   else 'FAIL — no retention data captured (XHR may have missed)'}")
    print(f"  4. CSV schema (33-col) : {'PASS' if csv_ok   else 'FAIL'}")
    print(f"  5. Analyzer handoff    : {'PASS' if csv_ok   else 'FAIL'}")

    overall = session_ok and csv_ok and ret_ok
    print()
    print(f"Overall: {'PASS' if overall else 'PARTIAL — see issues above'}")
    print()
    print("Next steps:")
    print("  python scripts/tiktok_collect_qa.py   (full standalone QA suite)")
    print("  /tiktok analyze                        (in Claude Code when QA passes)")
    print("=" * 62)


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="TikTok Creator Center analytics collector")
    parser.add_argument(
        "--product-id",
        help="Comma-separated product IDs (e.g. 007,008). Default: all detected.",
    )
    parser.add_argument(
        "--update", action="store_true",
        help="Re-collect even if rows already exist in video_results.csv.",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    filter_ids = None
    if args.product_id:
        filter_ids = {pid.strip().zfill(3) for pid in args.product_id.split(",")}

    print()
    print("=" * 62)
    print("TikTok Analytics Collector  v2")
    print("=" * 62)

    # 1. Detect all products
    print("\nScanning project files for uploaded products...")
    products = detect_all_products(filter_ids)
    if not products:
        print("ERROR: No products found. Check data/*-video-config.json files.")
        sys.exit(1)

    total = sum(len(p["variants"]) for p in products.values())
    print(f"  Found: {len(products)} products  ({', '.join(sorted(products))})")
    print(f"  Total variants: {total}")

    # 2. Check existing CSV
    existing = load_existing_csv()
    print(f"  Existing CSV rows: {len(existing)}")

    # 3. Build work list
    to_collect = []
    to_skip    = []
    for pid, prod in sorted(products.items()):
        for letter, vinfo in sorted(prod["variants"].items()):
            key = (pid, f"{pid}{letter}")
            if key in existing and not args.update:
                to_skip.append(vinfo)
            else:
                to_collect.append((pid, letter, prod, vinfo))

    if to_skip:
        print(f"\nSkipping {len(to_skip)} variants already in CSV:")
        for v in to_skip:
            print(f"  {v['cta_code']}")

    if not to_collect:
        print("\nNothing to collect — CSV is up to date.")
        print("Use --update to re-collect all rows.")
        sys.exit(0)

    print(f"\nWill collect: {len(to_collect)} variant(s)")
    print()

    # 4. Collect via Playwright
    result_records = []

    # Mark skipped items in results for the QA report
    for vinfo in to_skip:
        result_records.append({"cta_code": vinfo["cta_code"], "skipped": True,
                                "not_found": False, **vinfo})

    manual_queue = []  # (cta_code, row) pairs awaiting manual field input

    with sync_playwright() as pw:
        browser, context = launch_with_session(pw)
        page = context.new_page()

        print("Verifying session...")
        if not check_session_valid(page):
            print("ERROR: Session expired. Run: python scripts/tiktok_session_login.py")
            browser.close()
            sys.exit(1)
        print("Session valid.\n")

        # Bare-CTA products with NO confirmed identity map cannot be safely
        # collected by guessing (order-based skip_count matching was proven
        # unsafe — see PROJECT_STATUS.md). Gather visual evidence instead of
        # guessing, and pull those variants out of the normal collection loop.
        unmapped_bare_pids = set()
        for pid, letter, prod, vinfo in to_collect:
            if vinfo.get("bare_index") is not None and not vinfo.get("video_id"):
                unmapped_bare_pids.add(pid)

        for pid in sorted(unmapped_bare_pids):
            prod = products[pid]
            sample_vinfo = next(iter(prod["variants"].values()))
            caption_search_text = sample_vinfo.get("caption_search_text", "")
            print(f"\n⚠ Product {pid} uses a bare CTA code with no confirmed identity map.")
            print(f"  All variants share an identical caption/CTA — cannot safely guess which")
            print(f"  row is which variant. Gathering visual evidence instead...")
            evidence_dir = OUTPUT_DIR / f"identify_{pid}"
            evidence = gather_visual_evidence(page, pid, caption_search_text, evidence_dir)
            print(f"  Captured {len(evidence)} candidate video(s) -> {evidence_dir}")
            if evidence:
                print(f"  ACTION REQUIRED: view the screenshots, match each video_id to its variant")
                print(f"  via the unique hook text in data/{pid}-video-config.json, then create")
                print(f"  data/{pid}-identity-map.json as {{\"<video_id>\": \"<letter>\", ...}} and")
                print(f"  rerun with --update.")
            else:
                print(f"  No matching rows found at all — product may not be uploaded yet, or the")
                print(f"  caption text has changed. Investigate before assuming data loss.")

            for letter, vinfo in prod["variants"].items():
                if vinfo.get("bare_index") is None:
                    continue
                to_collect = [t for t in to_collect if not (t[0] == pid and t[1] == letter)]
                result_records.append({
                    "product_id": pid, "variant": f"{pid}{letter}",
                    "hook_type": vinfo["hook_type"], "category": prod.get("category", ""),
                    "price_ils": prod["price_ils"], "winner": "", "cta_style": vinfo["cta_style"],
                    "asset_source": "", "best_segment": "", "upload_date": prod["upload_date"],
                    "upload_time": "", "age_hours": "",
                    "variant_status": "PENDING_VISUAL_CONFIRMATION",
                    "tracking_id": vinfo["tracking_id"], "affiliate_clicks": "",
                    "affiliate_sales": "", "affiliate_commission": "", "hook_text": vinfo["hook_text"],
                    "shares": "", "cta_code_comments": "", "engagement_rate": "", "save_rate": "",
                    "comment_rate": "", "share_rate": "", "cta_comment_rate": "",
                    "views": "PENDING_VISUAL_CONFIRMATION", "likes": "PENDING_VISUAL_CONFIRMATION",
                    "comments": "PENDING_VISUAL_CONFIRMATION", "saves": "PENDING_VISUAL_CONFIRMATION",
                    "average_watch_time": "", "retention_rate": "", "watched_full_video_rate": "",
                    "first_2_second_retention": "",
                    "cta_code": vinfo["cta_code"], "not_found": False, "pending_visual": True,
                })

        for pid, letter, prod, vinfo in to_collect:
            cta_code  = vinfo["cta_code"]
            skip_count = vinfo.get("bare_index") or 0
            label = f"{pid}{letter}" if vinfo.get("bare_index") is not None else cta_code
            print(f"[{label}] Collecting...")

            video_id = vinfo.get("video_id")
            raw = collect_one_variant(page, cta_code, skip_count=skip_count,
                                       caption_search_text=vinfo.get("caption_search_text", ""),
                                       video_id=video_id)

            # Bare-code variants found via skip_count (order-based guessing) have
            # UNVERIFIED identity — UNLESS video_id came from a confirmed identity
            # map, in which case identity was confirmed via unique href, not guessed.
            is_bare_code = bool(re.match(r'^\d{3}$', cta_code))
            if not raw["not_found"] and is_bare_code and skip_count > 0 and not video_id:
                print(f"  WARNING: {label} found via order-based matching (skip_count={skip_count})")
                print(f"           Identity UNVERIFIED — bare code '{cta_code}' with shared caption")
                print(f"           Metrics NOT written (require variant-level CTA for confirmation)")
                raw["not_found"] = True  # Treat as NOT_FOUND for CSV

            # Base row from project files
            row = {
                "product_id":     pid,
                "variant":        f"{pid}{letter}",
                "hook_type":      vinfo["hook_type"],
                "category":       prod.get("category", ""),
                "price_ils":      prod["price_ils"],
                "winner":         "",
                "cta_style":      vinfo["cta_style"],
                "asset_source":   "",
                "best_segment":   "",
                "upload_date":    prod["upload_date"],
                "upload_time":    "",
                "age_hours":      "",
                "variant_status": "",
                "tracking_id":    vinfo["tracking_id"],
                "affiliate_clicks":    "",
                "affiliate_sales":     "",
                "affiliate_commission": "",
                "hook_text":      vinfo["hook_text"],
                "shares":         "",
                "cta_code_comments": "",
                "engagement_rate": "",
                "save_rate":      "",
                "comment_rate":   "",
                "share_rate":     "",
                "cta_comment_rate": "",
            }

            if raw["not_found"]:
                not_found_val = "NOT_FOUND"
                row.update({
                    "views": not_found_val, "likes": not_found_val,
                    "comments": not_found_val, "saves": not_found_val,
                    "shares": not_found_val, "average_watch_time": not_found_val,
                    "retention_rate": not_found_val,
                    "watched_full_video_rate": not_found_val,
                    "first_2_second_retention": not_found_val,
                    "variant_status": "NOT_FOUND",
                })
                print(f"  WARNING: {cta_code} not found on TikTok")
            else:
                # Merge TikTok metrics
                for field in ("views", "likes", "comments", "saves", "shares",
                              "average_watch_time", "retention_rate",
                              "watched_full_video_rate", "first_2_second_retention"):
                    row[field] = raw.get(field, "")

                row = compute_derived(row)
                manual_queue.append((cta_code, row))
                print(f"  OK  views={row.get('views') or '?'}  "
                      f"2s_ret={row.get('first_2_second_retention') or '?'}")

            # Tag for QA report (stripped before CSV write)
            row["cta_code"]  = cta_code
            row["not_found"] = raw["not_found"]
            result_records.append(row)

        browser.close()

    # 5. Manual fields — all default to blank (no prompting)
    for cta_code, row in manual_queue:
        row.update(prompt_manual_fields(cta_code))

    # 6. Write CSV
    print()
    new_rows = []
    for r in result_records:
        if r.get("skipped"):
            key = (r.get("product_id", ""), r.get("variant", ""))
            if key in existing:
                new_rows.append(existing[key])
        else:
            new_rows.append(r)  # extrasaction="ignore" in writer strips internal keys

    write_csv(new_rows, existing)

    # 7. QA report
    print_qa_report(products, result_records, existing)


if __name__ == "__main__":
    main()
