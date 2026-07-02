#!/usr/bin/env python3
"""
analyze_qa.py — Standalone QA suite for /tiktok analyze output.

Run this after /tiktok analyze to verify the analysis and learning_report.json
before treating a PROCEED/PAUSE/CHANGE STRATEGY decision as final.

There is no prompt-file equivalent of this script — "Analyze QA" exists only
as a milestone name in PROJECT_STATUS.md's stated order (Collector Enhancement
-> Collector QA -> re-run Analyze -> Analyze QA -> Analyzer v3); it was never
actually specified. This script formalizes the ad-hoc verification done by
hand on 2026-07-02 (independently recomputing winners/averages/confidence
score/decision logic straight from video_results.csv and diffing them against
what the analysis actually produced) so it doesn't have to be reinvented by
hand every time.

Usage:
    python scripts/analyze_qa.py
    python scripts/analyze_qa.py --product-id 002,003,007,008

Checks:
  1. Learning Report Exists & Valid   — data/learning_report.json present, parses as JSON
  2. Learning Report Schema           — decision-dependent field rules from tiktok-analyze.md Step F
  3. Winner Consistency               — winners/hook_type_wins recomputed from the raw CSV match learning_report.json
  4. Retention Consistency            — avg first_2_second_retention recomputed from CONFIRMED rows matches learning_report.json
  5. Decision Logic Consistency       — the stated PROCEED/PAUSE/CHANGE STRATEGY decision isn't contradicted by what's actually in the CSV
  6. Analysis File Present            — at least one analysis/*-analysis.md file exists, dated on or after the newest CONFIRMED upload
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT     = Path(__file__).resolve().parent.parent
DATA_DIR         = PROJECT_ROOT / "data"
ANALYSIS_DIR     = PROJECT_ROOT / "analysis"
CSV_FILE         = DATA_DIR / "video_results.csv"
LEARNING_REPORT  = DATA_DIR / "learning_report.json"

EXPECTED_HOOK_TYPES = {"Price Shock", "Curiosity", "Problem/Solution", "TikTok Discovery"}

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
        return None
    try:
        with open(CSV_FILE, encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))
    except Exception:
        return None


def _load_learning_report():
    if not LEARNING_REPORT.exists():
        return None, "learning_report.json not found"
    try:
        return json.loads(LEARNING_REPORT.read_text(encoding="utf-8")), None
    except Exception as exc:
        return None, f"Cannot parse learning_report.json: {exc}"


def _confirmed_rows(rows, filter_ids=None):
    confirmed = [r for r in rows if r.get("variant_status") == "CONFIRMED"]
    if filter_ids:
        confirmed = [r for r in confirmed if r.get("product_id") in filter_ids]
    return confirmed


def _recompute_winners(confirmed):
    """Per-product winner = highest views (engagement basis — this project has
    never had affiliate_sales data to override). Returns {pid: variant} and a
    hook_type_wins tally across those winners, matching the same win-
    determination logic used throughout tiktok-analyze.md's C.A/C.I."""
    by_product = defaultdict(list)
    for r in confirmed:
        by_product[r.get("product_id", "")].append(r)

    winners = {}
    hook_wins = {h: 0 for h in EXPECTED_HOOK_TYPES}
    for pid, items in by_product.items():
        numeric_items = [r for r in items if _is_numeric(r.get("views"))]
        if not numeric_items:
            continue
        winner = max(numeric_items, key=lambda r: float(r["views"]))
        winners[pid] = winner.get("variant", "")
        hook = winner.get("hook_type", "")
        if hook in hook_wins:
            hook_wins[hook] += 1
    return winners, hook_wins


def _is_numeric(val):
    try:
        float(val)
        return True
    except (ValueError, TypeError):
        return False


# ── Check 1 — Learning Report Exists & Valid ────────────────────────────────

def check_1_learning_report_exists():
    report, err = _load_learning_report()
    if err:
        return FAIL, [err, "Run /tiktok analyze — Step F writes this file."]
    return PASS, [f"data/learning_report.json parses as valid JSON ({len(report)} top-level keys)"]


# ── Check 2 — Learning Report Schema ────────────────────────────────────────

def check_2_learning_report_schema(report):
    """Validates the decision-dependent field rules documented in
    .claude/commands/tiktok-analyze.md's STEP F "JSON FIELD RULES"."""
    if report is None:
        return FAIL, ["learning_report.json not loaded — see Check 1"]

    issues = []
    warnings = []

    decision = report.get("decision")
    if decision not in ("PROCEED", "PAUSE", "CHANGE STRATEGY"):
        issues.append(f"decision={decision!r} is not one of PROCEED/PAUSE/CHANGE STRATEGY")

    pause_reason = report.get("pause_reason")
    change_issue = report.get("change_strategy_issue")
    brief = report.get("product_009_brief") or {}

    if decision == "PROCEED":
        if pause_reason is not None:
            issues.append("decision=PROCEED but pause_reason is not null")
        if change_issue is not None:
            issues.append("decision=PROCEED but change_strategy_issue is not null")
        for field in ("recommended_category", "lead_hook_for_variant_A",
                       "lead_hook_reason", "first_frame_requirement", "pacing_adjustment"):
            if not brief.get(field):
                issues.append(f"decision=PROCEED but product_009_brief.{field} is empty/null")
    elif decision == "PAUSE":
        if not pause_reason:
            issues.append("decision=PAUSE but pause_reason is empty/null")
    elif decision == "CHANGE STRATEGY":
        if not change_issue:
            issues.append("decision=CHANGE STRATEGY but change_strategy_issue is empty/null")

    # hook_type_wins: all 4 hook types present, each an int (0 valid, null is NOT)
    wins = (report.get("learning") or {}).get("hook_type_wins") or {}
    if set(wins.keys()) != EXPECTED_HOOK_TYPES:
        issues.append(
            f"hook_type_wins keys {set(wins.keys())} != expected {EXPECTED_HOOK_TYPES}"
        )
    for k, v in wins.items():
        if v is None:
            issues.append(f"hook_type_wins[{k}] is null — must be an int (0 is valid, null is not)")
        elif not isinstance(v, int):
            issues.append(f"hook_type_wins[{k}]={v!r} is not an int")

    if "confirmed_rows" not in (report.get("data_vintage") or {}):
        issues.append("data_vintage.confirmed_rows missing")

    if issues:
        return FAIL, issues + warnings
    if warnings:
        return WARN, warnings
    return PASS, [f"All decision-dependent field rules satisfied for decision={decision!r}"]


# ── Check 3 — Winner Consistency ────────────────────────────────────────────

def check_3_winner_consistency(rows, report, filter_ids):
    if rows is None:
        return FAIL, ["CSV not readable"]
    if report is None:
        return FAIL, ["learning_report.json not loaded — see Check 1"]

    confirmed = _confirmed_rows(rows, filter_ids)
    if not confirmed:
        return WARN, ["No CONFIRMED rows to check winners against"]

    _, recomputed_wins = _recompute_winners(confirmed)
    stated_wins = (report.get("learning") or {}).get("hook_type_wins") or {}

    mismatches = []
    for hook in EXPECTED_HOOK_TYPES:
        recomputed = recomputed_wins.get(hook, 0)
        stated = stated_wins.get(hook)
        if stated is not None and stated != recomputed:
            mismatches.append(f"{hook}: recomputed={recomputed} vs stated={stated}")

    stated_best_hook = (report.get("learning") or {}).get("best_hook_type")
    if stated_best_hook and recomputed_wins:
        top_by_wins = max(recomputed_wins, key=recomputed_wins.get)
        # best_hook_type is allowed to differ from the raw win-count leader —
        # tiktok-analyze.md explicitly picks by highest average engagement,
        # not just win count — so this is informational, not a FAIL.
        note = None
        if stated_best_hook != top_by_wins and recomputed_wins[top_by_wins] > 0:
            note = (
                f"best_hook_type={stated_best_hook!r} differs from the raw win-count "
                f"leader ({top_by_wins}, {recomputed_wins[top_by_wins]} wins) — expected "
                f"if best_hook_type was chosen by average engagement instead of win "
                f"count (see tiktok-analyze.md C.A); not a failure on its own."
            )

    if mismatches:
        return FAIL, [f"hook_type_wins mismatch: {m}" for m in mismatches]

    detail = [f"hook_type_wins recomputed from CSV matches learning_report.json: {recomputed_wins}"]
    if stated_best_hook and recomputed_wins:
        top_by_wins = max(recomputed_wins, key=recomputed_wins.get)
        if stated_best_hook != top_by_wins and recomputed_wins[top_by_wins] > 0:
            detail.append(
                f"Note: best_hook_type={stated_best_hook!r} differs from the raw win-count "
                f"leader ({top_by_wins}) — fine if chosen by avg engagement per C.A, "
                f"flagging for a human to confirm the reasoning still holds."
            )
    return PASS, detail


# ── Check 4 — Retention Consistency ─────────────────────────────────────────

def check_4_retention_consistency(rows, report, filter_ids):
    if rows is None:
        return FAIL, ["CSV not readable"]
    if report is None:
        return FAIL, ["learning_report.json not loaded — see Check 1"]

    confirmed = _confirmed_rows(rows, filter_ids)
    r2s_vals = [
        float(r["first_2_second_retention"]) for r in confirmed
        if _is_numeric(r.get("first_2_second_retention"))
    ]

    stated_avg = (report.get("learning") or {}).get("retention_avg_2s")

    if not r2s_vals:
        if stated_avg is not None:
            return FAIL, [
                "No first_2_second_retention data exists in the CSV at all, "
                f"but learning_report.json states retention_avg_2s={stated_avg} "
                "(should be null per Step F's rule: 'no data = null, not 0')"
            ]
        return WARN, ["No first_2_second_retention data in CSV — retention_avg_2s correctly null"]

    recomputed_avg = sum(r2s_vals) / len(r2s_vals)

    if stated_avg is None:
        return FAIL, [
            f"CSV has {len(r2s_vals)} first_2_second_retention value(s) "
            f"(recomputed avg={recomputed_avg:.4f}) but learning_report.json's "
            "retention_avg_2s is null — should have been filled in"
        ]

    if abs(float(stated_avg) - recomputed_avg) > 0.01:
        return FAIL, [
            f"retention_avg_2s mismatch: recomputed={recomputed_avg:.4f} "
            f"vs stated={stated_avg}"
        ]

    return PASS, [
        f"retention_avg_2s recomputed from {len(r2s_vals)} CONFIRMED rows "
        f"({recomputed_avg:.4f}) matches learning_report.json exactly"
    ]


# ── Check 5 — Decision Logic Consistency ────────────────────────────────────

def check_5_decision_logic(rows, report, filter_ids):
    """Does NOT re-run the full PROCEED/PAUSE/CHANGE STRATEGY decision tree
    (that requires C.G/C.H product-type classifications this script can't
    see) — checks only that the stated decision isn't contradicted by facts
    directly computable from the CSV, per tiktok-analyze.md STEP E's own
    PAUSE trigger conditions."""
    if rows is None:
        return FAIL, ["CSV not readable"]
    if report is None:
        return FAIL, ["learning_report.json not loaded — see Check 1"]

    confirmed = _confirmed_rows(rows, filter_ids)
    decision = report.get("decision")
    issues = []
    warnings = []

    if decision == "PROCEED":
        if len(confirmed) < 2:
            issues.append(
                f"decision=PROCEED but only {len(confirmed)} CONFIRMED row(s) exist "
                "(STEP E requires at least 2)"
            )
        has_retention = any(
            _is_numeric(r.get("first_2_second_retention")) for r in confirmed
        )
        # PROCEED's retention condition also allows "no early evidence of
        # retention collapse" even without data — this script can't judge
        # that qualitative CEO-flagged condition, so absence of retention
        # data is a WARN, not a FAIL, unless there are zero CONFIRMED rows
        # at all (which is already caught above).
        if not has_retention and confirmed:
            warnings.append(
                "decision=PROCEED with no first_2_second_retention data in any "
                "CONFIRMED row — only valid if there's no CEO-flagged retention "
                "concern (this script can't verify that qualitative condition)"
            )

    if decision == "PAUSE" and len(confirmed) >= 2:
        has_retention = any(
            _is_numeric(r.get("first_2_second_retention")) for r in confirmed
        )
        if has_retention:
            warnings.append(
                f"decision=PAUSE despite {len(confirmed)} CONFIRMED rows WITH retention "
                "data present — confirm this is genuinely a CHANGE-STRATEGY-adjacent "
                "call and not a stale decision from before retention data existed"
            )

    if issues:
        return FAIL, issues + warnings
    if warnings:
        return WARN, warnings
    return PASS, [f"decision={decision!r} is not contradicted by CSV-computable facts "
                  f"({len(confirmed)} CONFIRMED rows)"]


# ── Check 6 — Analysis File Present ─────────────────────────────────────────

def check_6_analysis_file_present(rows, filter_ids):
    if not ANALYSIS_DIR.exists():
        return FAIL, ["analysis/ directory does not exist"]

    analysis_files = sorted(ANALYSIS_DIR.glob("*-analysis.md"))
    if not analysis_files:
        return FAIL, ["No analysis/*-analysis.md file found — /tiktok analyze Step B never ran"]

    newest_analysis = max(analysis_files, key=lambda p: p.stat().st_mtime)

    if rows is not None:
        confirmed = _confirmed_rows(rows, filter_ids)
        upload_dates = [r.get("upload_date", "") for r in confirmed if r.get("upload_date")]
        if upload_dates:
            newest_upload = max(upload_dates)
            analysis_mtime = datetime.fromtimestamp(
                newest_analysis.stat().st_mtime, tz=timezone.utc
            ).strftime("%Y-%m-%d")
            if analysis_mtime < newest_upload:
                return WARN, [
                    f"Newest analysis file ({newest_analysis.name}, saved {analysis_mtime}) "
                    f"predates the newest CONFIRMED upload ({newest_upload}) — "
                    "may be analyzing stale data"
                ]

    return PASS, [f"Newest analysis file: {newest_analysis.name}"]


# ── Runner ─────────────────────────────────────────────────────────────────

def run_all_checks(filter_ids=None):
    print()
    print("=" * 62)
    print("TikTok Analyze QA Suite")
    print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 62)

    rows = _load_csv()
    report, report_err = _load_learning_report()

    results = []

    checks = [
        (1, "Learning Report Exists & Valid", lambda: check_1_learning_report_exists()),
        (2, "Learning Report Schema", lambda: check_2_learning_report_schema(report)),
        (3, "Winner Consistency", lambda: check_3_winner_consistency(rows, report, filter_ids)),
        (4, "Retention Consistency", lambda: check_4_retention_consistency(rows, report, filter_ids)),
        (5, "Decision Logic Consistency", lambda: check_5_decision_logic(rows, report, filter_ids)),
        (6, "Analysis File Present", lambda: check_6_analysis_file_present(rows, filter_ids)),
    ]

    for num, label, fn in checks:
        status, detail = fn()
        results.append(status)
        print(_status_line(num, label, status))
        for d in detail:
            print(f"       {d}")

    print()
    fail_count = results.count(FAIL)
    warn_count = results.count(WARN)
    pass_count = results.count(PASS)

    print(f"Summary:  {pass_count} PASS  |  {warn_count} WARN  |  {fail_count} FAIL")
    print()

    if fail_count == 0 and warn_count == 0:
        print("ANALYZE APPROVED — all checks PASS.")
        outcome = 0
    elif fail_count == 0:
        print("ANALYZE CONDITIONALLY APPROVED — warnings present (see above).")
        outcome = 0
    else:
        print("ANALYZE NOT APPROVED — fix FAIL issues before trusting this decision.")
        outcome = 1

    print("=" * 62)
    print()
    return outcome


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="TikTok /tiktok analyze QA suite")
    parser.add_argument(
        "--product-id",
        help="Comma-separated product IDs to scope check (e.g. 002,003,007,008)",
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

    sys.exit(run_all_checks(filter_ids=filter_ids))


if __name__ == "__main__":
    main()
