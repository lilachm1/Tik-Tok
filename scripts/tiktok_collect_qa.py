#!/usr/bin/env python3
"""
tiktok_collect_qa.py — Standalone 5-check QA suite for the TikTok collector.

Run this after tiktok_analytics_collect.py to verify the collector output
before handing off to /tiktok analyze.

Usage:
    python scripts/tiktok_collect_qa.py
    python scripts/tiktok_collect_qa.py --product-id 007,008  # scope to specific products
    python scripts/tiktok_collect_qa.py --strict               # fail on any NOT_FOUND

Checks:
  1. Login / Session    — session file exists, has TikTok cookies, not obviously expired
  2. Video Matching     — all expected variants have rows; none are NOT_FOUND
  3. Data Extraction    — views, saves, first_2_second_retention in valid ranges
  4. CSV Schema         — 33-column v2 header, correct types, no v1/mixed rows
  5. Analyzer Handoff   — all required analyzer input fields populated
"""

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR     = PROJECT_ROOT / "data"
SESSION_FILE = DATA_DIR / "tiktok-session.json"
CSV_FILE     = DATA_DIR / "video_results.csv"

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

# Fields the analyzer strictly requires to produce learning_report.json
ANALYZER_REQUIRED = [
    "product_id", "variant", "hook_type", "price_ils", "views",
    "likes", "saves", "variant_status", "tracking_id",
    "first_2_second_retention",
]

# ── Helpers ────────────────────────────────────────────────────────────────

PASS = "PASS"
FAIL = "FAIL"
WARN = "WARN"


def _status_line(check_num, label, status, detail=""):
    marker = "✓" if status == PASS else ("!" if status == WARN else "✗")
    line = f"  {marker}  Check {check_num}: {label:30s}  {status}"
    if detail:
        line += f"\n       {detail}"
    return line


def _load_csv():
    if not CSV_FILE.exists():
        return None, "CSV file not found"
    rows = []
    try:
        with open(CSV_FILE, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            header = reader.fieldnames or []
            for row in reader:
                rows.append(dict(row))
    except Exception as exc:
        return None, str(exc)
    return rows, header


def _detect_expected_variants(filter_ids=None):
    """Scan data/*-video-config.json and return set of expected (pid, variant_str)."""
    expected = {}
    for cfg_path in sorted(DATA_DIR.glob("*-video-config.json")):
        stem = cfg_path.stem.lower()
        if any(x in stem for x in ("test", "legacy", "temp", "backup")):
            continue
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        pid = str(cfg.get("product_id", "")).strip().zfill(3)
        if not pid or pid == "000":
            continue
        if filter_ids and pid not in filter_ids:
            continue
        for vcfg in cfg.get("variants", []):
            letter = vcfg.get("id", "")
            if letter:
                cta_code = None
                for seg in reversed(vcfg.get("segments", [])):
                    m = re.search(r"\b(\d{3}[A-D])\b", seg.get("text", ""))
                    if m:
                        cta_code = m.group(1)
                        break
                expected[(pid, f"{pid}{letter}")] = cta_code or f"{pid}{letter}"
    return expected


def _is_numeric(val):
    try:
        float(val)
        return True
    except (ValueError, TypeError):
        return False


# ── Check 1 — Login / Session ──────────────────────────────────────────────

def check_1_session():
    issues = []
    warnings = []

    if not SESSION_FILE.exists():
        return FAIL, ["Session file not found: data/tiktok-session.json",
                      "Run: python scripts/tiktok_session_login.py"]

    try:
        session = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
    except Exception as exc:
        return FAIL, [f"Cannot parse session file: {exc}"]

    cookies = session.get("cookies", [])
    if not cookies:
        issues.append("Session file has no cookies")

    # Look for TikTok authentication cookies
    tiktok_domains = [c for c in cookies if "tiktok.com" in c.get("domain", "")]
    if not tiktok_domains:
        issues.append("No tiktok.com cookies found in session")
    else:
        # Check for key auth cookies
        names = {c["name"] for c in tiktok_domains}
        auth_cookies = {"sessionid", "sid_tt", "tt_chain_token", "s_v_web_id"}
        found_auth = names & auth_cookies
        if not found_auth:
            warnings.append(
                f"No known auth cookies found (expected one of: {', '.join(sorted(auth_cookies))}). "
                "Session may be incomplete."
            )

        # Check expiry
        now_epoch = datetime.now(tz=timezone.utc).timestamp()
        expired = [
            c["name"] for c in tiktok_domains
            if c.get("expires", -1) > 0 and c["expires"] < now_epoch
        ]
        if expired:
            issues.append(f"Expired cookies: {', '.join(expired[:5])}")

    # Check file modification time as a rough staleness indicator
    mtime = datetime.fromtimestamp(SESSION_FILE.stat().st_mtime, tz=timezone.utc)
    age_days = (datetime.now(tz=timezone.utc) - mtime).days
    if age_days > 25:
        warnings.append(
            f"Session file is {age_days} days old. "
            "TikTok sessions typically last ~30 days. Consider refreshing."
        )

    if issues:
        return FAIL, issues + warnings
    if warnings:
        return WARN, warnings
    return PASS, [
        f"Session file present ({len(cookies)} cookies, {len(tiktok_domains)} tiktok.com)",
        f"File age: {age_days} day(s)",
    ]


# ── Check 2 — Video Matching ───────────────────────────────────────────────

def check_2_video_matching(rows, expected_variants, strict):
    if rows is None:
        return FAIL, ["CSV not readable — run collector first"]
    if not expected_variants:
        return WARN, ["No products detected from project files"]

    issues = []
    warnings = []

    csv_keys = {(r.get("product_id", ""), r.get("variant", "")): r for r in rows}

    not_found_in_csv   = []
    not_found_in_tiktok = []
    found_ok           = []

    for (pid, variant), cta_code in sorted(expected_variants.items()):
        if (pid, variant) not in csv_keys:
            not_found_in_csv.append(cta_code)
        else:
            row = csv_keys[(pid, variant)]
            vs = row.get("variant_status", "")
            views = row.get("views", "")
            if vs == "NOT_FOUND" or views == "NOT_FOUND":
                not_found_in_tiktok.append(cta_code)
            else:
                found_ok.append(cta_code)

    if not_found_in_csv:
        issues.append(
            f"{len(not_found_in_csv)} variant(s) missing from CSV entirely: "
            + ", ".join(not_found_in_csv)
        )
    if not_found_in_tiktok:
        msg = (
            f"{len(not_found_in_tiktok)} variant(s) NOT_FOUND on TikTok: "
            + ", ".join(not_found_in_tiktok)
        )
        if strict:
            issues.append(msg)
        else:
            warnings.append(msg + " (may not be uploaded yet)")

    if issues:
        return FAIL, issues + warnings
    if warnings:
        return WARN, warnings + [f"{len(found_ok)} variant(s) matched correctly"]
    return PASS, [
        f"{len(found_ok)}/{len(expected_variants)} variants matched",
        f"CTA codes: {', '.join(sorted(expected_variants.values()))}",
    ]


# ── Check 3 — Data Extraction Accuracy ────────────────────────────────────

def check_3_data_extraction(rows):
    if rows is None:
        return FAIL, ["CSV not readable"]

    live_rows = [r for r in rows if r.get("variant_status") not in ("NOT_FOUND", "")]
    if not live_rows:
        return FAIL, ["No live (non-NOT_FOUND) rows in CSV"]

    issues = []
    warnings = []
    retention_missing = []
    views_zero        = []
    views_missing     = []
    retention_invalid = []

    for r in live_rows:
        cta_code = r.get("variant", r.get("tracking_id", "?"))
        views = r.get("views", "")
        ret   = r.get("first_2_second_retention", "")

        if not views or views == "NOT_FOUND":
            views_missing.append(cta_code)
        elif _is_numeric(views) and float(views) == 0:
            views_zero.append(cta_code)

        if not ret or ret == "NOT_FOUND":
            retention_missing.append(cta_code)
        elif _is_numeric(ret):
            val = float(ret)
            if not (0.0 <= val <= 1.0):
                retention_invalid.append(f"{cta_code}={val:.4f}")

    if views_missing:
        issues.append(f"Views missing for: {', '.join(views_missing)}")
    if views_zero:
        warnings.append(f"Views = 0 (no data yet?) for: {', '.join(views_zero)}")
    if retention_missing:
        warnings.append(
            f"first_2_second_retention empty for: {', '.join(retention_missing)}. "
            "TikTok XHR capture may have missed the analytics response. "
            "Open the video analytics page manually and re-collect."
        )
    if retention_invalid:
        issues.append(f"Retention values out of 0-1 range: {', '.join(retention_invalid)}")

    detail = [
        f"Live rows: {len(live_rows)}",
        f"With views: {len(live_rows) - len(views_missing)}",
        f"With 2s retention: {len(live_rows) - len(retention_missing)}",
    ]

    if issues:
        return FAIL, issues + warnings + detail
    if warnings:
        return WARN, warnings + detail
    return PASS, detail


# ── Check 4 — CSV Schema ──────────────────────────────────────────────────

def check_4_csv_schema(rows_raw):
    """Verify 33-column v2 header and data types."""
    if not CSV_FILE.exists():
        return FAIL, ["CSV file not found"]

    issues = []
    warnings = []

    # Read raw header
    try:
        with open(CSV_FILE, encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            header = next(reader, [])
    except Exception as exc:
        return FAIL, [f"Cannot read CSV: {exc}"]

    if header != CSV_HEADER:
        missing = set(CSV_HEADER) - set(header)
        extra   = set(header) - set(CSV_HEADER)
        order_ok = sorted(header) == sorted(CSV_HEADER)
        col_count_msg = f"Got {len(header)} columns, expected {len(CSV_HEADER)}"
        if missing:
            issues.append(f"Missing columns: {', '.join(sorted(missing))}")
        if extra:
            issues.append(f"Extra columns: {', '.join(sorted(extra))}")
        if header != CSV_HEADER and not missing and not extra:
            issues.append(f"Column ORDER is wrong (all 33 present but in wrong order)")
        issues.insert(0, col_count_msg)

    if issues:
        return FAIL, issues

    # Type checks on data rows
    if rows_raw:
        int_fields   = ["views", "likes", "comments", "saves", "shares"]
        float_fields = ["engagement_rate", "save_rate", "comment_rate", "share_rate",
                        "first_2_second_retention", "retention_rate"]
        type_errors = []

        for r in rows_raw:
            if r.get("variant_status") == "NOT_FOUND":
                continue
            for f in int_fields:
                v = r.get(f, "")
                if v and not _is_numeric(v):
                    type_errors.append(f"{r.get('variant','?')}.{f}={v!r}")
            for f in float_fields:
                v = r.get(f, "")
                if v and not _is_numeric(v):
                    type_errors.append(f"{r.get('variant','?')}.{f}={v!r}")

        if type_errors:
            issues.append(f"Type errors in data rows: {'; '.join(type_errors[:10])}")

    if issues:
        return FAIL, issues

    return PASS, [
        f"33-column v2 header verified",
        f"Data rows: {len(rows_raw) if rows_raw else 0}",
    ]


# ── Check 5 — Analyzer Handoff ────────────────────────────────────────────

def check_5_analyzer_handoff(rows):
    """Verify that /tiktok analyze will have all the fields it needs."""
    if rows is None:
        return FAIL, ["CSV not readable"]

    confirmed = [r for r in rows if r.get("variant_status") == "CONFIRMED"]
    pending   = [r for r in rows if r.get("variant_status") == "PENDING"]
    not_found = [r for r in rows if r.get("variant_status") == "NOT_FOUND"]

    issues   = []
    warnings = []

    if not confirmed and not pending:
        issues.append("No CONFIRMED or PENDING rows — analyzer has nothing to work with")

    # Check required fields are populated on at least the confirmed rows
    usable = confirmed if confirmed else pending
    for r in usable:
        missing_fields = [
            f for f in ANALYZER_REQUIRED
            if not r.get(f) or r.get(f) in ("NOT_FOUND", "")
        ]
        if missing_fields:
            warnings.append(
                f"{r.get('variant','?')} missing analyzer fields: "
                + ", ".join(missing_fields)
            )

    # first_2_second_retention check (CEO's critical diagnostic metric)
    no_ret = [
        r.get("variant", "?") for r in usable
        if not r.get("first_2_second_retention")
        or r.get("first_2_second_retention") in ("NOT_FOUND", "")
    ]
    if no_ret:
        warnings.append(
            f"first_2_second_retention empty on: {', '.join(no_ret)}. "
            "Analyzer will flag these as INSUFFICIENT_DATA."
        )

    detail = [
        f"CONFIRMED rows: {len(confirmed)}",
        f"PENDING rows  : {len(pending)}",
        f"NOT_FOUND rows: {len(not_found)}",
    ]

    if issues:
        return FAIL, issues + warnings + detail
    if warnings:
        return WARN, warnings + detail
    return PASS, detail


# ── Runner ─────────────────────────────────────────────────────────────────

def run_all_checks(filter_ids=None, strict=False):
    print()
    print("=" * 62)
    print("TikTok Collector QA Suite")
    print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 62)

    rows, header = _load_csv()  # rows may be None on error; header is list or str-error
    expected = _detect_expected_variants(filter_ids)

    results = []

    # Check 1
    status, detail = check_1_session()
    results.append(status)
    print(_status_line(1, "Login / Session", status))
    for d in detail:
        print(f"       {d}")

    # Check 2
    status, detail = check_2_video_matching(rows, expected, strict)
    results.append(status)
    print(_status_line(2, "Video Matching", status))
    for d in detail:
        print(f"       {d}")

    # Check 3
    status, detail = check_3_data_extraction(rows)
    results.append(status)
    print(_status_line(3, "Data Extraction Accuracy", status))
    for d in detail:
        print(f"       {d}")

    # Check 4
    status, detail = check_4_csv_schema(rows)
    results.append(status)
    print(_status_line(4, "CSV Schema (33-col v2)", status))
    for d in detail:
        print(f"       {d}")

    # Check 5
    status, detail = check_5_analyzer_handoff(rows)
    results.append(status)
    print(_status_line(5, "Analyzer Handoff", status))
    for d in detail:
        print(f"       {d}")

    print()
    fail_count = results.count(FAIL)
    warn_count = results.count(WARN)
    pass_count = results.count(PASS)

    print(f"Summary:  {pass_count} PASS  |  {warn_count} WARN  |  {fail_count} FAIL")
    print()

    if fail_count == 0 and warn_count == 0:
        print("COLLECTOR APPROVED — all 5 checks PASS.")
        print("Run /tiktok analyze when ready.")
        outcome = 0
    elif fail_count == 0:
        print("COLLECTOR CONDITIONALLY APPROVED — warnings present (see above).")
        print("Review warnings, then run /tiktok analyze.")
        outcome = 0
    else:
        print("COLLECTOR NOT APPROVED — fix FAIL issues before running /tiktok analyze.")
        outcome = 1

    print("=" * 62)
    print()
    return outcome


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="TikTok collector QA suite")
    parser.add_argument(
        "--product-id",
        help="Comma-separated product IDs to scope check (e.g. 007,008)",
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Treat NOT_FOUND variants as FAIL instead of WARN",
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

    sys.exit(run_all_checks(filter_ids=filter_ids, strict=args.strict))


if __name__ == "__main__":
    main()
