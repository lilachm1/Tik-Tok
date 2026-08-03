#!/usr/bin/env python3
"""
layer5_competitor_benchmark.py — ANALYZER_V3_SPEC.md Layer 5's mandatory
multi-competitor benchmark requirement (added 2026-07-02, after a single-
competitor comparison was correctly flagged as insufficient).

Searches TikTok (using the account's own authenticated session -- anonymous
search triggers a CAPTCHA, confirmed 2026-07-02, not attempted here) for a
product category, ranks results by engagement (likes), and for the top N
(target 5, minimum viable 1 -- flagged LOW_CONFIDENCE if fewer than 5 are
found) extracts a comparable frame sequence and computes the same
consecutive-frame SSIM motion-magnitude metric already validated against
008B, with popup-dismissal checked before EVERY capture (a real "Create a
passkey" popup contaminated an earlier single-competitor attempt and was
caught and corrected -- this script builds that lesson in from the start
rather than repeating the mistake).

**Two-stage ranking (fixed 2026-08-03 -- see `search_candidates()` and
`shortlist_by_real_likes()`):** TikTok's search-results cards expose a VIEW
count (`data-e2e="video-views"`) in the DOM, not a like count -- there is no
like-count element anywhere in a search card's markup. Earlier versions of
this script tried to scrape a "like count" from search cards via a generic
bare-number text match, which actually captured the view count (mislabeled
as likes whenever it worked) and returned nothing/0 whenever the async
number hadn't finished rendering within a fixed sleep (a render-timing race,
not a selector bug) -- confirmed via live DOM inspection when product 003's
run came back with 0 likes on every single candidate. Fix: `search_candidates()`
now honestly extracts `view_count` (polling for hydration instead of a fixed
sleep, and excluding the header inbox/notifications panel's own video-link
thumbnails, which also match a naive `a[href*="/video/"]` selector but are
relative-path links to unrelated liked/notified videos, not search results).
View count is then used ONLY as a cheap pre-filter to shortlist the most
promising candidates; each shortlisted candidate's REAL like_count is then
fetched from its own video page via `fetch_like_count_for_url()` (the same
reliable per-video fetch already used for `--seed-urls`) before the actual
Top-N ranking in `select_top_candidates()`, which has always ranked by
`like_count`, never `view_count`.

**Note on `view_count` itself (confirmed 2026-08-03, product 003 re-run):**
despite its `data-e2e="video-views"` attribute name, this number turned out
to exactly match the same video's real `like-count` on its own detail page
for all 5 competitors checked (12, 131, 209, 1019, 2474 -- verified via
direct DOM inspection of two of them, @bpatent and @max_stock_israel, each
showing distinct/non-matching like/comment/share/favorite counts, so this
isn't every-field-aliased-together). TikTok's search-card test-id name
appears to be a mislabeled legacy name, not what it actually renders. This
does NOT change anything about the two-stage design above -- the real
like_count is still fetched fresh per-candidate rather than trusted from the
search card, since a mislabeled attribute is not a guarantee it holds for
every query/account, and the fetch cost is cheap for a shortlist of ~15.

Does NOT render the qualitative judgments itself (product-reveal timing,
text-appearance timing, human-motion presence, camera-movement type,
first-frame strength, real-use demonstration, TikTok-native-vs-catalog feel)
-- those require actually looking at the frames, same division of labor as
Layer 3 and Layer 5's own execution analysis. This script gathers the
evidence; the agent (or a set of parallel agents) fills in judgment.

Does NOT write to data/video_results.csv.

Usage:
    python scripts/layer5_competitor_benchmark.py --product-id 008 --query "מעמד לטאבלט מסתובב" --target 5
    python scripts/layer5_competitor_benchmark.py --product-id 008 --query "מעמד לטאבלט מסתובב" --query2 "מעמד לנייד מסתובב 360"
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tiktok_analytics_collect import sync_playwright, launch_with_session, check_session_valid

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ANALYTICS_DIR = PROJECT_ROOT / "data" / "tiktok-analytics"

TIMESTAMPS = [0.1, 0.5, 1.0, 1.5, 2.0, 2.5, 3.5, 5.0, 6.5, 8.0]
POPUP_LABELS = ["Maybe later", "Skip", "Not now", "Close", "לא כרגע", "דלג"]


def select_top_candidates(candidates, target):
    """
    Dedup by href and pick the Top-N (`target`) competitors to extract
    frames for.

    Policy (fixed 2026-08-03 -- was previously broken, see below):
    - `like_count` is either a real measured int, or `None` if it genuinely
      could not be determined. `None` must never be treated as a real zero.
    - Search-discovered candidates (`source: "search"`) are ranked by
      `like_count` descending, same as before.
    - Seed candidates (`source: "seed"`, passed via `--seed-urls`) are
      manually vetted by a human and are ALWAYS included, regardless of
      their `like_count` or whether it could be measured at all. They fill
      the Top-N first; search results fill any remaining slots up to
      `target`. If there are more seeds than `target`, all seeds are still
      kept -- `target` is a floor on search-filled slots, not a cap on
      manually-vetted ones.

    The bug this replaces: seed competitors were given `like_count: None`
    and then ranked with everyone else using `like_count or 0`, so an
    unmeasured value silently became a real zero and lost to every search
    result with any positive like count -- which is exactly what dropped
    @yeuunnt.22 (78.3K likes) and @goussve.km from product 008's benchmark
    (session 15, 2026-07-02) before they were manually re-added.
    """
    by_href = {}
    for c in candidates:
        href = c["href"]
        existing = by_href.get(href)
        if existing is None:
            by_href[href] = dict(c)
            continue
        if c["like_count"] is not None and (
            existing["like_count"] is None or c["like_count"] > existing["like_count"]
        ):
            existing["like_count"] = c["like_count"]
        if c.get("source") == "seed":
            existing["source"] = "seed"

    seeds = [c for c in by_href.values() if c.get("source") == "seed"]
    searched = [c for c in by_href.values() if c.get("source") != "seed"]
    searched.sort(key=lambda c: c["like_count"] if c["like_count"] is not None else -1, reverse=True)

    top = list(seeds)
    for c in searched:
        if len(top) >= target:
            break
        top.append(c)
    return top


NUMERIC_LIKE_TEXT_RE = re.compile(r"^[\d.]+[KMkm]?$")


def fetch_like_count_and_caption_for_url(page, url, out_dir, label):
    """
    Navigate to a single competitor video page and extract its real
    like_count AND its caption/description, in the same page visit --
    the caption is what `passes_relevance_filter()` checks BEFORE frame
    extraction runs, so a wrong-category match (confirmed 2026-08-03: seat
    CUSHIONS surfacing in a seat-back ORGANIZER search, a sealant-paste video
    surfacing in a bag-SEALER search) doesn't burn a frame-extraction slot on
    a video that was never going to be usable evidence. Getting the caption
    here is free -- no extra navigation -- since we're already on the page
    to read the like count.

    Returns (like_count, caption). like_count is an int, or None if it
    genuinely could not be determined (navigation failure, selector not
    found, unsolved CAPTCHA, or the number never hydrates within the poll
    window) -- `None` here is a real "unavailable" signal, never assumed to
    mean zero (see select_top_candidates()). caption is the page title
    (TikTok renders it as "<caption> | TikTok"), or "" if unavailable.

    Polls for hydration instead of a fixed sleep (fixed 2026-08-03, product
    007 run): confirmed via live DOM inspection that `[data-e2e="like-count"]`
    is present and visible well before its text becomes the real number --
    it shows the static button label ("Like") until the count hydrates
    asynchronously, so a single early read after a fixed sleep silently
    returns 0 (parse_like_count("Like") has no digits to match) or, worse,
    reads a stale/wrong value if a second video's stats block (e.g. an
    autoplaying next-video preview) happens to be first in DOM order at that
    moment. This is the same class of race already fixed in
    `search_candidates()` -- the fix here is the same technique: wait for
    the actual text to look like a number before trusting it.
    """
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
    except Exception:
        return None, ""
    time.sleep(1)
    dismiss_popups(page)
    if not wait_for_manual_captcha_solve(page, out_dir, label):
        return None, ""

    caption = ""
    try:
        title = page.title() or ""
        caption = re.sub(r"\s*\|\s*TikTok\s*$", "", title).strip()
    except Exception:
        pass

    try:
        el = page.locator('[data-e2e="like-count"]').first
        for _ in range(16):  # poll up to ~8s for the real number to hydrate
            if el.is_visible(timeout=1000):
                text = (el.text_content() or "").strip()
                if text and NUMERIC_LIKE_TEXT_RE.match(text):
                    return parse_like_count(text), caption
            time.sleep(0.5)
    except Exception:
        pass

    # Fallback if TikTok's data-e2e attribute isn't present: first short
    # K/M-style number in the action bar (the like count is the first of
    # the like/comment/share counters in DOM order on a video page).
    try:
        text = page.evaluate("""() => {
            const nodes = [...document.querySelectorAll('strong, span, button')];
            for (const n of nodes) {
                const t = (n.textContent || '').trim();
                if (/^[\\d.]+[KMkm]?$/.test(t)) return t;
            }
            return null;
        }""")
        if text:
            return parse_like_count(text), caption
    except Exception:
        pass

    return None, caption


# TikTok's own placeholder page title when a video's real caption/description
# is empty or didn't render -- NOT evidence of anything, must never count as
# a caption match OR a mismatch (confirmed 2026-08-03, product 007: several
# genuinely-relevant videos have no caption at all and must not be excluded
# just because there's nothing to match against).
UNINFORMATIVE_CAPTIONS = {"", "tiktok - make your day"}


def passes_relevance_filter(caption, include_keywords, exclude_keywords):
    """
    A candidate passes if its caption contains at least one include_keyword
    (when a list is given) AND none of exclude_keywords. Empty
    include_keywords means "no positive filter" (pass by default); this is
    deliberately a coarse pre-filter, not a substitute for later human/agent
    review of the actual frames -- but it's what stops an obviously
    wrong-category video (confirmed cases: seat cushions in a seat-back
    ORGANIZER search, sealant paste / mini suitcases in a bag-SEALER search)
    from burning a frame-extraction slot at all.

    An uninformative caption (empty, or TikTok's own placeholder title) can
    neither confirm nor rule out relevance -- confirmed 2026-08-03 that a
    naive "no caption == no keyword match == excluded" rule wrongly dropped
    real product007 competitors (e.g. an "Automotive Seat Back Storage Bag"
    listing whose search-result caption never rendered). These are passed
    through undecided rather than excluded, deferring the actual call to
    visual frame review, which is the authoritative check for a mismatch
    text can't settle either way.
    """
    text = (caption or "").strip().lower()
    if text in UNINFORMATIVE_CAPTIONS:
        return True
    if exclude_keywords and any(kw.lower() in text for kw in exclude_keywords):
        return False
    if include_keywords and not any(kw.lower() in text for kw in include_keywords):
        return False
    return True


def parse_like_count(text):
    """'78.3K' -> 78300, '883' -> 883. Empty on failure."""
    text = text.strip().upper()
    m = re.match(r"([\d.]+)([KM]?)", text)
    if not m:
        return 0
    num, suffix = m.groups()
    try:
        val = float(num)
    except ValueError:
        return 0
    if suffix == "K":
        val *= 1_000
    elif suffix == "M":
        val *= 1_000_000
    return int(val)


def dismiss_popups(page):
    for label in POPUP_LABELS:
        try:
            btn = page.locator(f"text={label}").first
            if btn.is_visible(timeout=400):
                btn.click()
                time.sleep(0.5)
                return True
        except Exception:
            pass
    return False


def _real_video_card_anchors_js():
    """Shared JS predicate: a search-result video anchor, not one of the
    header inbox/notifications panel's own video-thumbnail links (which also
    match `a[href*="/video/"]` but carry a relative href, e.g.
    "/@123/video/456", vs. a search card's absolute "https://www.tiktok.com/..."
    href) -- confirmed via live DOM inspection 2026-08-03: the inbox panel
    renders in the header regardless of whether it's visibly open, and its
    "X liked your video" entries are unrelated to the search query entirely."""
    return """
        [...document.querySelectorAll('a[href*="/video/"]')]
            .filter(a => (a.getAttribute('href') || '').startsWith('http'))
    """


def search_candidates(page, query, out_dir):
    """
    Returns [{href, view_count, source: "search"}], deduped by href, sorted
    by view_count desc. `view_count` (data-e2e="video-views") is the only
    engagement number a search card's DOM actually exposes -- there is no
    like-count element on this page at all (confirmed 2026-08-03). This is
    NOT the final ranking metric (see `shortlist_by_real_likes()` below,
    which fetches each shortlisted candidate's real like_count from its own
    video page) -- it's a cheap pre-filter only, kept honestly labeled as
    what it is instead of masquerading as `like_count`.
    """
    url = f"https://www.tiktok.com/search/video?q={query}"
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(2)
    dismiss_popups(page)
    wait_for_manual_captcha_solve(page, out_dir, f"search_{query[:12]}")

    # Poll for hydration instead of a fixed sleep -- confirmed 2026-08-03 that
    # a fixed 4s sleep sometimes ran before the async view-count numbers had
    # rendered at all, silently producing candidates with no usable metric.
    hydrated = False
    for _ in range(16):  # ~8s max
        any_view_count = page.evaluate(f"""() => {{
            const anchors = {_real_video_card_anchors_js()};
            return anchors.some(a => {{
                const el = a.querySelector('[data-e2e="video-views"]');
                return el && el.textContent && el.textContent.trim().length > 0;
            }});
        }}""")
        if any_view_count:
            hydrated = True
            break
        time.sleep(0.5)
    if not hydrated:
        print(f"  WARNING: view-count numbers never hydrated for query '{query}' after 8s -- "
              f"candidates from this query may have view_count=None")

    results = page.evaluate(f"""() => {{
        const anchors = {_real_video_card_anchors_js()};
        const out = [];
        for (const a of anchors) {{
            const el = a.querySelector('[data-e2e="video-views"]');
            const text = el ? (el.textContent || '').trim() : null;
            out.push({{href: a.getAttribute('href'), viewsText: text || null}});
        }}
        return out;
    }}""")

    seen = set()
    candidates = []
    for r in results:
        href = r.get("href")
        if not href or href in seen:
            continue
        seen.add(href)
        views_text = r.get("viewsText")
        view_count = parse_like_count(views_text) if views_text else None
        candidates.append({"href": href, "view_count": view_count, "source": "search"})

    candidates.sort(key=lambda c: c["view_count"] if c["view_count"] is not None else -1, reverse=True)
    return candidates


def merge_search_candidates(candidate_lists):
    """Dedup by href across multiple queries' results, keeping the first-seen
    entry per href, then sort by view_count desc (None treated as lowest,
    never coerced to 0 -- an unmeasured view_count is not evidence of zero
    views, same principle as the like_count fix above)."""
    seen = set()
    merged = []
    for cands in candidate_lists:
        for c in cands:
            if c["href"] not in seen:
                seen.add(c["href"])
                merged.append(c)
    merged.sort(key=lambda c: c["view_count"] if c["view_count"] is not None else -1, reverse=True)
    return merged


def shortlist_by_real_likes(page, candidates, out_dir, top_k, include_keywords=None, exclude_keywords=None):
    """
    Takes view_count-ranked search candidates, keeps the top `top_k` by
    view_count as a cheap pre-filter, then fetches each one's REAL like_count
    AND caption from its own video page via
    `fetch_like_count_and_caption_for_url()` -- the actual ranking metric
    `select_top_candidates()` uses. Candidates beyond the pre-filter cutoff
    are dropped rather than passed through with a fake/zero like_count,
    since we genuinely have no like-count evidence for them.

    Relevance filtering happens HERE, immediately after the caption is known
    and BEFORE frame extraction -- not as an after-the-fact QA check --
    specifically so a wrong-category video never burns a frame-extraction
    slot (confirmed 2026-08-03: seat cushions surfacing in a seat-back
    ORGANIZER search, a sealant-paste video in a bag-SEALER search).
    Excluded candidates are dropped from the returned list but always
    printed with their caption and the exclusion reason, so a run's own log
    shows what was skipped and why rather than hiding it.
    """
    shortlist = candidates[:top_k]
    enriched = []
    for c in shortlist:
        href = c["href"]
        url = href if href.startswith("http") else f"https://www.tiktok.com{href}"
        like_count, caption = fetch_like_count_and_caption_for_url(page, url, out_dir, "prescreen")
        relevant = passes_relevance_filter(caption, include_keywords, exclude_keywords)
        if not relevant:
            status = "  <- EXCLUDED: caption doesn't match product category"
        elif caption.strip().lower() in UNINFORMATIVE_CAPTIONS:
            status = "  <- KEPT, UNDECIDED: no usable caption, needs visual frame review"
        else:
            status = ""
        print(f"  {url} (view_count={c['view_count']}, like_count={like_count}) '{caption[:60]}'{status}")
        if not relevant:
            continue
        enriched.append({
            "href": href,
            "like_count": like_count,
            "caption": caption,
            "view_count_at_search": c["view_count"],
            "source": "search",
        })
    return enriched


CAPTCHA_MARKERS = ["Drag the slider to fit the puzzle", "Verify to continue", "Select 2 objects"]


def captcha_present(page):
    for marker in CAPTCHA_MARKERS:
        try:
            if page.locator(f"text={marker}").first.is_visible(timeout=500):
                return marker
        except Exception:
            pass
    return None


def wait_for_manual_captcha_solve(page, out_dir, label, timeout_s=300, poll_s=3):
    """
    NEVER solves the CAPTCHA itself -- per explicit instruction, this is
    manual-only. Detects it, prints a clear action-needed message + saves a
    screenshot so the user can see exactly what to solve, then polls until
    the marker text disappears (i.e. the user solved it in the visible
    browser window) or the timeout is reached. Returns True if solved,
    False if it timed out unsolved.
    """
    marker = captcha_present(page)
    if not marker:
        return True

    shot_path = out_dir / f"{label}_captcha_needs_solving.png"
    try:
        page.screenshot(path=str(shot_path))
    except Exception:
        pass

    print(f"\n{'!'*62}")
    print(f"ACTION NEEDED: CAPTCHA detected on {label} ('{marker}').")
    print(f"Please solve it manually in the visible browser window now.")
    print(f"Screenshot saved to: {shot_path}")
    print(f"Waiting up to {timeout_s}s -- will continue automatically once solved.")
    print(f"{'!'*62}\n")

    waited = 0
    while waited < timeout_s:
        time.sleep(poll_s)
        waited += poll_s
        if not captcha_present(page):
            print(f"  CAPTCHA cleared after {waited}s -- continuing.")
            return True
    print(f"  Timed out after {timeout_s}s waiting for manual solve -- skipping {label}.")
    return False


def download_video_bytes(page, timeout_s=15):
    """
    Triggers real playback and downloads the actual decoded video bytes via
    its blob URL, returning (bytes, content_type) or (None, None).

    Root cause fixed 2026-08-03 (a real, confirmed bug, not a hypothesis):
    live DOM inspection showed a competitor page's <video> element sitting at
    readyState=0 (HAVE_NOTHING) for 4+ seconds after navigation -- TikTok
    defers actually loading video data until playback is triggered. The
    previous version of `extract_competitor_frames()` never called .play(),
    only set `currentTime` (a no-op on an unloaded video) and screenshotted
    the live element -- which, in a page object reused across many
    sequential navigations, silently captured a PREVIOUS candidate's still-
    painted frame instead. Confirmed in production: 2 of 5 product-007
    competitors' "extracted frames" were entirely different videos by
    different creators. Explicitly calling `.play()` (muted, to satisfy
    autoplay policy) reliably brings readyState to 4 within ~0.5s in manual
    testing.

    Downloading the actual bytes (rather than continuing to screenshot the
    live element even after this fix) removes the whole class of live-DOM
    timing risk permanently and lets ffmpeg do the frame extraction the same
    way this project already does for its OWN rendered videos (Layer 3) --
    operating on real file bytes, not a race-prone in-browser paint.
    """
    try:
        page.evaluate("""() => {
            const v = document.querySelector('video');
            if (v) { v.muted = true; v.play().catch(() => {}); }
        }""")
    except Exception:
        return None, None

    for _ in range(int(timeout_s / 0.5)):
        try:
            ready = page.evaluate("""() => {
                const v = document.querySelector('video');
                return v ? {readyState: v.readyState, src: v.currentSrc || ''} : null;
            }""")
        except Exception:
            return None, None
        if ready and ready["readyState"] >= 3 and ready["src"]:
            break
        time.sleep(0.5)
    else:
        return None, None  # never loaded -- do NOT fall back to screenshotting an unloaded element

    try:
        result = page.evaluate("""async () => {
            const v = document.querySelector('video');
            const resp = await fetch(v.currentSrc);
            const buf = await resp.arrayBuffer();
            const bytes = new Uint8Array(buf);
            let binary = '';
            const CHUNK = 8192;
            for (let i = 0; i < bytes.length; i += CHUNK) {
                binary += String.fromCharCode.apply(null, bytes.subarray(i, i + CHUNK));
            }
            return {b64: btoa(binary), contentType: resp.headers.get('content-type') || 'video/mp4'};
        }""")
    except Exception:
        return None, None

    if not result or not result.get("b64"):
        return None, None
    import base64
    return base64.b64decode(result["b64"]), result.get("contentType", "video/mp4")


def extract_competitor_frames(page, video_url, out_dir, label):
    import shutil
    import subprocess

    page.goto(video_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(2)
    dismiss_popups(page)

    if not wait_for_manual_captcha_solve(page, out_dir, label):
        return None

    video_bytes, content_type = download_video_bytes(page)
    if not video_bytes:
        return None

    ext = "webm" if content_type and "webm" in content_type else "mp4"
    video_path = out_dir / f"{label}_source.{ext}"
    video_path.write_bytes(video_bytes)

    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        return None

    try:
        probe = subprocess.run(
            [ffprobe, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
            capture_output=True, timeout=15, text=True,
        )
        duration = float(probe.stdout.strip()) if probe.stdout.strip() else None
    except Exception:
        duration = None

    frame_paths = []
    for t in TIMESTAMPS:
        if duration and t >= duration:
            break
        out_path = out_dir / f"{label}_t{t}.png"
        try:
            subprocess.run(
                [ffmpeg, "-y", "-ss", str(t), "-i", str(video_path), "-frames:v", "1", str(out_path)],
                capture_output=True, timeout=20,
            )
        except Exception:
            continue
        if out_path.exists():
            frame_paths.append({"t": t, "path": str(out_path)})

    return {"duration": duration, "frames": frame_paths, "source_video_path": str(video_path)}


def compute_motion_metrics(frame_paths):
    """Consecutive-frame SSIM via ffmpeg, plus simple cut detection (a sharp
    drop well below the surrounding trend)."""
    import shutil
    import subprocess

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg or len(frame_paths) < 2:
        return {"error": "ffmpeg unavailable or too few frames"}

    ssim_values = []
    for i in range(len(frame_paths) - 1):
        a, b = frame_paths[i]["path"], frame_paths[i + 1]["path"]
        try:
            result = subprocess.run(
                [ffmpeg, "-i", a, "-i", b, "-lavfi", "ssim", "-f", "null", "-"],
                capture_output=True, timeout=30, text=True,
            )
            m = re.search(r"All:([\d.]+)", result.stderr)
            s = float(m.group(1)) if m else None
        except Exception:
            s = None
        ssim_values.append({
            "from_t": frame_paths[i]["t"], "to_t": frame_paths[i + 1]["t"], "ssim": s,
        })

    valid = [v["ssim"] for v in ssim_values if v["ssim"] is not None]
    avg_ssim = sum(valid) / len(valid) if valid else None

    # crude cut detection: any interval whose ssim is much lower than the
    # median of the others suggests a hard cut rather than gradual motion
    cuts = []
    if len(valid) >= 3:
        sorted_vals = sorted(valid)
        median = sorted_vals[len(sorted_vals) // 2]
        for v in ssim_values:
            if v["ssim"] is not None and v["ssim"] < median - 0.25:
                cuts.append(v["from_t"])

    return {
        "consecutive_ssim": ssim_values,
        "avg_consecutive_ssim": avg_ssim,
        "likely_cut_points_s": cuts,
    }


def main():
    parser = argparse.ArgumentParser(description="Layer 5 multi-competitor benchmark collection")
    parser.add_argument("--product-id", required=True)
    parser.add_argument("--query", required=True, help="Primary Hebrew search query")
    parser.add_argument("--query2", help="Optional second query to widen the candidate pool")
    parser.add_argument("--target", type=int, default=5, help="Target number of competitors (default 5)")
    parser.add_argument("--seed-urls", help="Comma-separated known competitor URLs to include regardless of search")
    parser.add_argument("--relevance-keywords",
                         help="Comma-separated keywords -- a search candidate's caption must contain at least "
                              "one of these to be kept (checked BEFORE frame extraction). Seeds are exempt "
                              "(manually vetted already). Omit to skip positive filtering.")
    parser.add_argument("--exclude-keywords",
                         help="Comma-separated keywords -- a search candidate's caption containing ANY of "
                              "these is dropped regardless of relevance-keywords (e.g. 'cushion,כרית' to keep "
                              "seat cushions out of a seat-back-organizer benchmark). Seeds are exempt.")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    pid = args.product_id.strip().zfill(3)
    out_dir = ANALYTICS_DIR / f"product{pid}" / "layer5_competitor_frames"
    out_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser, context = launch_with_session(pw)
        page = context.new_page()
        print("Verifying session...")
        if not check_session_valid(page):
            print("ERROR: session expired")
            sys.exit(1)
        print("Session valid.\n")

        candidate_lists = []
        for q in [args.query] + ([args.query2] if args.query2 else []):
            print(f"Searching: {q}")
            cands = search_candidates(page, q, out_dir)
            print(f"  found {len(cands)} candidates")
            candidate_lists.append(cands)
        view_ranked = merge_search_candidates(candidate_lists)

        include_kw = [k.strip() for k in args.relevance_keywords.split(",")] if args.relevance_keywords else None
        exclude_kw = [k.strip() for k in args.exclude_keywords.split(",")] if args.exclude_keywords else None

        prescreen_k = max(args.target * 3, 15)
        print(f"\nPre-filtered to top {min(prescreen_k, len(view_ranked))} by view_count "
              f"(of {len(view_ranked)} total) -- fetching real like_count + caption for each, "
              f"filtering by relevance before any frame extraction:")
        all_candidates = shortlist_by_real_likes(page, view_ranked, out_dir, prescreen_k, include_kw, exclude_kw)

        if args.seed_urls:
            for url in args.seed_urls.split(","):
                url = url.strip()
                if not url:
                    continue
                full_url = url if url.startswith("http") else f"https://www.tiktok.com{url}"
                print(f"Fetching real like_count for seed competitor: {full_url}")
                like_count, caption = fetch_like_count_and_caption_for_url(page, full_url, out_dir, "seed_precheck")
                if like_count is None:
                    print("  like_count unavailable -- included anyway (seed competitors are never excluded for a missing metric)")
                else:
                    print(f"  like_count = {like_count}")
                all_candidates.append({"href": url, "like_count": like_count, "caption": caption, "source": "seed"})

        top = select_top_candidates(all_candidates, args.target)

        print(f"\nTop {len(top)} candidates selected:")
        for c in top:
            like_str = f"{c['like_count']} likes" if c["like_count"] is not None else "likes unavailable"
            print(f"  {like_str} ({c.get('source', 'search')}) -- {c['href']}")

        competitors = []
        for i, c in enumerate(top):
            href = c["href"]
            url = href if href.startswith("http") else f"https://www.tiktok.com{href}"
            label = f"comp{i}"
            print(f"\nExtracting frames for {label}: {url}")
            result = extract_competitor_frames(page, url, out_dir, label)
            if not result or not result["frames"]:
                print("  FAILED to extract frames -- skipping")
                continue
            motion = compute_motion_metrics(result["frames"])
            competitors.append({
                "label": label,
                "url": url,
                "like_count": c["like_count"],
                "like_count_unavailable": c["like_count"] is None,
                "caption": c.get("caption", ""),
                "view_count_at_search": c.get("view_count_at_search"),
                "source": c.get("source", "search"),
                "duration_s": result["duration"],
                "source_video_path": result.get("source_video_path"),
                "frame_paths": result["frames"],
                "motion_metrics": motion,
                "qualitative_review": {
                    "product_reveal_time_s": None,
                    "text_appears_time_s": None,
                    "human_motion_present": None,
                    "camera_movement_present": None,
                    "motion_type": None,  # "organic" | "simulated_crop_pan" | "mixed"
                    "first_frame_strength": None,
                    "product_shown_in_real_use": None,
                    "feels_native_to_tiktok_israel": None,
                    "notes": None,
                },
            })

        browser.close()

    low_confidence = len(competitors) < 5
    benchmark = {
        "product_id": pid,
        "search_queries": [args.query] + ([args.query2] if args.query2 else []),
        "target_competitor_count": args.target,
        "actual_competitor_count": len(competitors),
        "low_confidence": low_confidence,
        "low_confidence_reason": (
            f"Only {len(competitors)} competitor(s) found/extracted -- below the target of {args.target}. "
            "Per ANALYZER_V3_SPEC.md's Confidence Rules, this benchmark must be treated as LOW_CONFIDENCE, "
            "not a reliable Top-5/Top-10 aggregate." if low_confidence else None
        ),
        "competitors": competitors,
    }

    out_path = ANALYTICS_DIR / f"product{pid}" / f"product{pid}_layer5_competitor_benchmark.json"
    out_path.write_text(json.dumps(benchmark, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    print(f"\n{'='*62}")
    print(f"Competitor benchmark for product {pid}: {len(competitors)}/{args.target} found "
          f"{'-- LOW_CONFIDENCE' if low_confidence else ''}")
    print(f"Saved to: {out_path}")
    print("Qualitative review fields left null -- require agent visual review of the extracted frames.")
    print("NOTE: nothing was written to data/video_results.csv.")


if __name__ == "__main__":
    main()
