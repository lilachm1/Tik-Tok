================================================
WEEKLY AUDIT REPORT — 2026-07-01
================================================

**Revision note:** Regenerated after the `winner` column was backfilled (data-enrichment task, collector/data-layer scope). Each of the 4 products now has exactly one real `winner=true` row (002C, 003B, 007D, 008C), chosen by views+saves+comments (no affiliate_sales data exists). Hook/category win data below is now genuinely computed from the CSV, not derived from raw views the way an earlier version of this audit had done.

DATA RANGE: 2026-06-14 → 2026-06-17
CONFIRMED ROWS: 16 (4 marked winner=true)
PRODUCTS TESTED: 002, 003, 007, 008

TOP 5 PRODUCTS (by average views + saves across CONFIRMED variants)
1. Product 002 — Avg views: 302.75 | Avg saves: 0 | Status: WINNING
2. Product 003 — Avg views: 179.25 | Avg saves: 0 | Status: TESTING
3. Product 007 — Avg views: 115.50 | Avg saves: 0 | Status: TESTING
4. Product 008 — Avg views: 63.25 | Avg saves: 0 | Status: RETIRED (candidate)

TOP 5 VARIANTS (by views + saves — CONFIRMED only)
1. 002C — Problem/Solution — Views: 390 | Saves: 0 — winner=true
2. 003B — Curiosity — Views: 360 | Saves: 0 — winner=true
3. 003A — Price Shock — Views: 354 | Saves: 0
4. 002B — Curiosity — Views: 353 | Saves: 0
5. 002D — TikTok Discovery — Views: 315 | Saves: 0

BEST HOOK TYPES (ranked by average views + saves across all CONFIRMED wins)
1. Problem/Solution — 2 wins (002C, 008C) — Avg views (all instances): 157.50
2. Curiosity — 1 win (003B) — Avg views (all instances): 229.50 — highest raw average despite fewer wins
3. TikTok Discovery — 1 win (007D) — Avg views (all instances): 116.00
4. Price Shock — 0 wins — Avg views (all instances): 157.75 — flag: 0 wins across 4 CONFIRMED runs, candidate to deprioritize

BEST CATEGORIES (ranked by average views + saves across all CONFIRMED wins)
1. Home & Garden (Kitchen/Food Storage) — 1 win (003B) — Avg views among winners: 360.00 (n=1, low confidence despite ranking first)
2. Mobile Phone Accessories — 2 wins (002C, 008C) — Avg views among winners: 261.50 (n=2, more supporting data)
3. Interior Accessories — 1 win (007D) — Avg views among winners: 145.00

Separately (not winner-gated — C.I's all-CONFIRMED-rows average, used for the Product 009 brief's category recommendation): Mobile Phone Accessories is strongest overall at 183.0 avg views across all 8 of its variants (2 products) — this is a different calculation from the winner-based ranking above and the two are not expected to match.

BEST PRICE RANGES (ranked by saves/views ratio across CONFIRMED winners)
Saves data does not exist for any row, so saves/views ratio cannot be computed. Ranking winning rows by views instead:
1. ₪15–24 (002C) — 390 views — ⚠️ this is the recommended band going forward
2. under ₪15 (003B) — 360 views — ⚠️ flagged hard-reject zone per spec; a winning row here doesn't override that
3. ₪25–40 (007D) — 145 views
4. ₪40–65 (008C) — 133 views

BIGGEST FAILURES (lowest average views + saves, CONFIRMED only)
1. 003C — Avg views: 1 | Avg saves: 0 — near-zero views alongside its winning sibling (003B, 360 views) suggests non-delivery by TikTok's algorithm rather than a genuinely bad hook.
2. 003D — Avg views: 2 | Avg saves: 0 — same pattern.
3. 008D — Avg views: 2 | Avg saves: 0 — same pattern.
4. 008A — Avg views: 4 | Avg saves: 0 — same pattern.
5. Product 008 (aggregate) — Avg views: 63.25 — 38.3% of account average — RETIRED candidate despite 008C being that product's own winner=true row.

WHAT TO SCALE NEXT WEEK
- Problem/Solution + Mobile Phone Accessories — the one hook+category combination with a real, repeated winner=true signal (002C, 008C). Worth testing again if Product 009 lands in this category.
- No product yet qualifies for "generate 3-5 more variants" outright — only Product 002 is WINNING (product-status sense), and it's a single data cycle.

WHAT TO STOP TESTING
- Product 008 (360° Stand) — RETIRED candidate, aggregate 38.3% of account average, despite having its own winner.
- Price Shock — 0 wins across 4 CONFIRMED runs (meets the spec's "3+ runs" threshold for a deprioritization flag). Not yet a hard "stop" (spec's hard-stop bar is 5+ runs with 0 wins), but a real, data-backed watch item now — not an artifact of missing data the way it was in an earlier version of this audit.
- All 4 products remain CONTINUE TESTING (C.G product-type classification, driven by save_rate/engagement/CTA data, unaffected by the winner backfill) — none should be paused on that basis yet.

CONFIDENCE SCORE THIS WEEK: 50

================================================
