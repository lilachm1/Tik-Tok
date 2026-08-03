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


def fetch_like_count_for_url(page, url, out_dir, label):
    """
    Navigate to a single competitor video page and extract its real
    like_count, so seed competitors get a measured value instead of the
    placeholder `None` this used to leave in place. Returns an int, or None
    if it genuinely could not be determined (navigation failure, selector
    not found, unsolved CAPTCHA) -- `None` here is a real "unavailable"
    signal, never assumed to mean zero (see select_top_candidates()).
    """
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
    except Exception:
        return None
    time.sleep(2)
    dismiss_popups(page)
    if not wait_for_manual_captcha_solve(page, out_dir, label):
        return None

    try:
        el = page.locator('[data-e2e="like-count"]').first
        if el.is_visible(timeout=5000):
            text = el.text_content()
            if text and text.strip():
                return parse_like_count(text)
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
            return parse_like_count(text)
    except Exception:
        pass

    return None


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


def search_candidates(page, query, out_dir):
    """Returns [{href, like_count}] sorted by like_count desc, deduped by href."""
    url = f"https://www.tiktok.com/search/video?q={query}"
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    dismiss_popups(page)
    wait_for_manual_captcha_solve(page, out_dir, f"search_{query[:12]}")

    results = page.evaluate("""() => {
        const anchors = [...document.querySelectorAll('a[href*="/video/"]')];
        const out = [];
        for (const a of anchors) {
            let likeText = null;
            let node = a;
            for (let i = 0; i < 6 && node; i++) {
                const svgHeart = node.querySelector && node.querySelector('svg');
                const candidate = node.textContent || '';
                const m = candidate.match(/^\\s*([\\d.]+[KMkm]?)\\s*$/);
                if (m) { likeText = m[1]; }
                node = node.parentElement;
            }
            out.push({href: a.getAttribute('href'), likeText});
        }
        return out;
    }""")

    seen = set()
    candidates = []
    for r in results:
        href = r.get("href")
        if not href or href in seen:
            continue
        seen.add(href)
        like_count = parse_like_count(r.get("likeText") or "0")
        candidates.append({"href": href, "like_count": like_count, "source": "search"})

    candidates.sort(key=lambda c: c["like_count"], reverse=True)
    return candidates


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


def extract_competitor_frames(page, video_url, out_dir, label):
    page.goto(video_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)
    dismiss_popups(page)

    if not wait_for_manual_captcha_solve(page, out_dir, label):
        return None

    video_el = page.locator("video").first
    try:
        if not video_el.is_visible(timeout=5000):
            return None
    except Exception:
        return None

    duration = None
    try:
        duration = page.evaluate("() => { const v = document.querySelector('video'); return v ? v.duration : null; }")
    except Exception:
        pass

    frame_paths = []
    for t in TIMESTAMPS:
        if duration and t >= duration:
            break
        dismiss_popups(page)  # check before EVERY capture -- the exact thing that got missed before
        if not wait_for_manual_captcha_solve(page, out_dir, f"{label}_t{t}"):
            break  # captcha appeared mid-sequence and wasn't solved in time -- stop this video, keep frames gathered so far
        try:
            page.evaluate(f"""() => {{
                const v = document.querySelector('video');
                if (v) {{ v.pause(); v.currentTime = {t}; }}
            }}""")
        except Exception:
            continue
        time.sleep(0.4)
        out_path = out_dir / f"{label}_t{t}.png"
        try:
            video_el.screenshot(path=str(out_path))
            frame_paths.append({"t": t, "path": str(out_path)})
        except Exception:
            continue

    return {"duration": duration, "frames": frame_paths}


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

        all_candidates = []
        for q in [args.query] + ([args.query2] if args.query2 else []):
            print(f"Searching: {q}")
            cands = search_candidates(page, q, out_dir)
            print(f"  found {len(cands)} candidates")
            all_candidates.extend(cands)

        if args.seed_urls:
            for url in args.seed_urls.split(","):
                url = url.strip()
                if not url:
                    continue
                full_url = url if url.startswith("http") else f"https://www.tiktok.com{url}"
                print(f"Fetching real like_count for seed competitor: {full_url}")
                like_count = fetch_like_count_for_url(page, full_url, out_dir, "seed_precheck")
                if like_count is None:
                    print("  like_count unavailable -- included anyway (seed competitors are never excluded for a missing metric)")
                else:
                    print(f"  like_count = {like_count}")
                all_candidates.append({"href": url, "like_count": like_count, "source": "seed"})

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
                "source": c.get("source", "search"),
                "duration_s": result["duration"],
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
