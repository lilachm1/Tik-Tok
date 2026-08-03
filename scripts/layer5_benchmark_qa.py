#!/usr/bin/env python3
"""
layer5_benchmark_qa.py — Standalone QA suite for
scripts/layer5_competitor_benchmark.py's output.

Same convention as tiktok_collect_qa.py / analyze_qa.py: an independent
script that re-checks the benchmark's own claims rather than trusting its
PASS-looking summary line at face value. Built 2026-08-03 after two real
bugs were found by hand while broadening the Layer 5 benchmark to products
002/003/007 (search cards showing a mislabeled-but-usable engagement number,
and a hydration-timing race in the per-video like-count fetch that silently
returned 0/None for the two highest-viewed candidates in product 007's first
attempt) -- this formalizes that manual spot-checking so it doesn't have to
be reinvented by hand for every future product.

Usage:
    python scripts/layer5_benchmark_qa.py --product-id 002,003,007
    python scripts/layer5_benchmark_qa.py --product-id 007 --fetch-captions

Checks 1-7 all run by default, with no browser/session needed (Check 7 reads
each competitor's caption from what the benchmark script already stored --
see layer5_competitor_benchmark.py's relevance filter, fixed 2026-08-03 to
run BEFORE frame extraction so a wrong-category match never burns a
frame-extraction slot). --fetch-captions only matters for benchmark data
collected before that field existed, where it live-fetches the missing
caption (requires a TikTok session):
  1. Benchmark File Exists & Valid JSON
  2. Schema / Count Consistency        — actual_competitor_count matches len(competitors); low_confidence flag matches target vs actual
  3. URL Dedup Integrity               — no two competitors share a URL
  4. Like-Count / Unavailable-Flag Consistency — like_count is None iff like_count_unavailable is True
  5. Frame Completeness                — every competitor has frame_paths, and every referenced file actually exists on disk
  6. View/Like Divergence (informational) — flags competitors where view_count_at_search and like_count differ by more than 3x, since every case checked by hand so far (2026-08-03) showed them matching closely or exactly
  7. Caption Relevance                 — independently re-checks each competitor's caption against the product's expected keywords (WARN, not FAIL — keyword lists are inherently imperfect), same "re-verify independently, don't trust the producer's own summary" principle as analyze_qa.py
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ANALYTICS_DIR = PROJECT_ROOT / "data" / "tiktok-analytics"

PASS = "PASS"
FAIL = "FAIL"
WARN = "WARN"

# Best-effort relevance keywords per product, drawn from each product's own
# real Hebrew hook/caption text in output/*-upload_package.md — not guessed.
PRODUCT_KEYWORDS = {
    "002": ["מחזיק", "טלפון", "רכב", "מגנט", "phone", "mount", "car", "magnet"],
    "003": ["שקי", "אוטם", "ואקום", "bag", "seal", "vacuum"],
    "007": ["מארגן", "מושב", "רכב", "organizer", "seat", "car", "back"],
    "008": ["מעמד", "טאבלט", "נייד", "מסתובב", "stand", "tablet", "phone", "rotat"],
}


def _status_line(check_num, label, status, detail=""):
    marker = "✓" if status == PASS else ("!" if status == WARN else "✗")
    line = f"  {marker}  Check {check_num}: {label:38s}  {status}"
    if detail:
        line += f"\n       {detail}"
    return line


def _load_benchmark(pid):
    path = ANALYTICS_DIR / f"product{pid}" / f"product{pid}_layer5_competitor_benchmark.json"
    if not path.exists():
        return None, f"{path} not found"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        return None, f"Cannot parse {path.name}: {exc}"


def check_1_file_valid(pid):
    data, err = _load_benchmark(pid)
    if err:
        return FAIL, err, None
    return PASS, "", data


def check_2_schema_counts(data):
    actual = data.get("actual_competitor_count")
    real = len(data.get("competitors", []))
    target = data.get("target_competitor_count")
    low_conf = data.get("low_confidence")
    problems = []
    if actual != real:
        problems.append(f"actual_competitor_count={actual} but competitors list has {real}")
    expected_low_conf = real < target if target is not None else None
    if expected_low_conf is not None and low_conf != expected_low_conf:
        problems.append(f"low_confidence={low_conf} but {real}/{target} found (expected {expected_low_conf})")
    if problems:
        return FAIL, "; ".join(problems)
    return PASS, f"{real}/{target} competitors, low_confidence={low_conf} (consistent)"


def check_3_dedup(data):
    urls = [c.get("url") for c in data.get("competitors", [])]
    dupes = {u for u in urls if urls.count(u) > 1}
    if dupes:
        return FAIL, f"duplicate competitor URL(s): {dupes}"
    return PASS, f"{len(urls)} unique URLs"


def check_4_like_count_flag_consistency(data):
    problems = []
    for c in data.get("competitors", []):
        lc = c.get("like_count")
        unavailable = c.get("like_count_unavailable")
        if (lc is None) != bool(unavailable):
            problems.append(f"{c.get('label')}: like_count={lc} but like_count_unavailable={unavailable}")
    if problems:
        return FAIL, "; ".join(problems)
    return PASS, "like_count/like_count_unavailable agree for every competitor"


def check_5_frame_completeness(data):
    problems = []
    for c in data.get("competitors", []):
        frames = c.get("frame_paths", [])
        if not frames:
            problems.append(f"{c.get('label')}: no frames recorded")
            continue
        missing = [f["path"] for f in frames if not Path(f["path"]).exists()]
        if missing:
            problems.append(f"{c.get('label')}: {len(missing)} frame file(s) missing on disk")
    if problems:
        return FAIL, "; ".join(problems)
    total = sum(len(c.get("frame_paths", [])) for c in data.get("competitors", []))
    return PASS, f"{total} frame files present across {len(data.get('competitors', []))} competitors"


def check_6_view_like_divergence(data):
    """Informational, not a hard failure -- but every case checked by hand
    while building this benchmark (product 003 and 007, 2026-08-03) showed
    view_count_at_search and the real like_count matching exactly or very
    closely, so a large divergence is worth a human look, not silent trust."""
    flags = []
    for c in data.get("competitors", []):
        lc, vc = c.get("like_count"), c.get("view_count_at_search")
        if lc is None or vc is None or lc == 0 or vc == 0:
            continue
        ratio = max(lc, vc) / max(min(lc, vc), 1)
        if ratio > 3:
            flags.append(f"{c.get('label')}: like_count={lc} vs view_count_at_search={vc} ({ratio:.1f}x apart)")
    if flags:
        return WARN, "; ".join(flags)
    return PASS, "no competitor's like_count/view_count_at_search diverge by more than 3x"


def check_7_caption_relevance(pid, data, out_dir, live_fetch=False):
    """
    Re-verifies relevance independently of whatever filtering
    layer5_competitor_benchmark.py already applied at collection time (fixed
    2026-08-03 to filter by caption BEFORE frame extraction) -- this is the
    QA layer's own separate check, same principle as analyze_qa.py
    recomputing winners from the raw CSV instead of trusting
    learning_report.json's own summary.

    Default (no --fetch-captions): reads the `caption` field the benchmark
    script already stored per competitor -- instant, no browser/session
    needed. Falls back to a live fetch per competitor ONLY when a stored
    caption is missing (e.g. benchmark data collected before this field
    existed) and live_fetch=True was requested.
    """
    keywords = PRODUCT_KEYWORDS.get(pid, [])
    if not keywords:
        return WARN, f"no keyword list defined for product {pid} -- add one to PRODUCT_KEYWORDS"

    competitors = data.get("competitors", [])
    missing_caption = [c for c in competitors if not c.get("caption")]
    if missing_caption and live_fetch:
        from tiktok_analytics_collect import sync_playwright, launch_with_session, check_session_valid
        with sync_playwright() as pw:
            browser, context = launch_with_session(pw)
            page = context.new_page()
            if not check_session_valid(page):
                browser.close()
                return FAIL, "TikTok session invalid -- cannot fetch captions"
            for c in missing_caption:
                try:
                    page.goto(c["url"], wait_until="domcontentloaded", timeout=30000)
                    time.sleep(2)
                    c["caption"] = page.title() or ""
                except Exception as exc:
                    c["caption"] = ""
            browser.close()

    mismatches = []
    for c in competitors:
        caption = c.get("caption") or ""
        if not caption:
            mismatches.append(f"{c.get('label')} ({c['url']}): no caption available to check "
                               f"(pass --fetch-captions for a live re-fetch)")
            continue
        if not any(kw in caption for kw in keywords):
            mismatches.append(f"{c.get('label')} ({c['url']}): caption has none of {keywords} -- '{caption[:80]}'")

    if mismatches:
        return WARN, "; ".join(mismatches)
    return PASS, f"all {len(competitors)} competitors' captions contain an expected keyword"


def run_for_product(pid, fetch_captions):
    print(f"\n{'='*70}\nLayer 5 Benchmark QA — product {pid}\n{'='*70}")
    results = []

    status, detail, data = check_1_file_valid(pid)
    results.append((1, "Benchmark File Exists & Valid", status, detail))
    print(_status_line(1, "Benchmark File Exists & Valid", status, detail))
    if status == FAIL:
        return results

    for i, fn in enumerate(
        [check_2_schema_counts, check_3_dedup, check_4_like_count_flag_consistency,
         check_5_frame_completeness, check_6_view_like_divergence],
        start=2,
    ):
        status, detail = fn(data)
        label = re.sub(r"^check_\d+_", "", fn.__name__).replace("_", " ")
        results.append((i, fn.__name__, status, detail))
        print(_status_line(i, label, status, detail))

    status, detail = check_7_caption_relevance(pid, data, ANALYTICS_DIR / f"product{pid}", live_fetch=fetch_captions)
    results.append((7, "caption_relevance", status, detail))
    print(_status_line(7, "caption relevance", status, detail))

    return results


def main():
    parser = argparse.ArgumentParser(description="QA suite for Layer 5 competitor benchmark output")
    parser.add_argument("--product-id", required=True, help="Comma-separated product IDs, e.g. 002,003,007")
    parser.add_argument("--fetch-captions", action="store_true",
                         help="Check 7 always runs using each competitor's already-stored caption "
                              "(instant, no session needed); this flag additionally live-fetches a caption "
                              "for any competitor missing one (requires a TikTok session)")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    pids = [p.strip().zfill(3) for p in args.product_id.split(",") if p.strip()]
    all_results = {}
    for pid in pids:
        all_results[pid] = run_for_product(pid, args.fetch_captions)

    print(f"\n{'='*70}\nSummary\n{'='*70}")
    overall_ok = True
    for pid, results in all_results.items():
        fails = [r for r in results if r[2] == FAIL]
        warns = [r for r in results if r[2] == WARN]
        if fails:
            overall_ok = False
            print(f"  product {pid}: {len(fails)} FAIL, {len(warns)} WARN")
        elif warns:
            print(f"  product {pid}: 0 FAIL, {len(warns)} WARN")
        else:
            print(f"  product {pid}: all checks PASS")

    sys.exit(0 if overall_ok else 1)


if __name__ == "__main__":
    main()
