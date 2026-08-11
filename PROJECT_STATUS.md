# TikTok Affiliate Agent — Project Status

**Last updated:** 2026-08-11 (session 26 — **Incorporated the approved Layer 3+5+7 creative-rules synthesis into `learning_report.json`.** Added a new `creative_rules` top-level block: Permanent Creative Rules 1-3 (open on real hand/person; avoid marketplace/catalog-style presentation; show the actual mechanism), each with its exact evidence (0/16 vs. 20/20 for Rules 1/3; 16/16 vs. 0/20 for Rule 2) and `classification: PERMANENT_CREATIVE_RULE`; Rule 4 recorded as `classification: MODIFIED_RULE`, `permanent: false`, `evidence_scope: EVIDENCE_3_OF_4_PRODUCTS`, with an explicit `do_not_promote_to_permanent: true` flag. Added the combined Layer 3+5+7 diagnosis with a `causality` sub-block listing what direct evidence exists vs. what doesn't (no competitor retention curves, no causal proof) and a `forbidden_claims` array explicitly ruling out "competitors retain better/decline slower" framing. Added the sub-10-view data-quality finding (003C n=1, 008A n=4) tagged `DATA_QUALITY_SAMPLE_SIZE`, `not_a_creative_rule: true`. Added a `next_causal_test` scaffold (OLD vs. NEW creative pattern, `test_status: NOT_YET_RUN`, `results: null` — no fabricated outcome) so a future variant can serve as the causal test the synthesis itself says is still missing. **One existing field flagged as superseded, not rewritten:** `product_009_brief.first_frame_requirement` ("standard approach") predates and is now in tension with Permanent Rules 1-3 — added a `creative_rules_compliance_note` pointing to the new block rather than editing the brief's historical text/numbers, since regenerating Product 009 guidance is out of scope. Validated the change against the existing `analyze_qa.py` suite (still 6/6 PASS, unchanged). Did not touch the creative pipeline, Product 009, Daily Incremental Mode, or any other Analyzer v3 layer, and ran no new TikTok research. Session 25's cross-product synthesis (recapped below) is unchanged by this session.)
**Owner:** Lilach
**Working directory:** `C:\Automation\TikTok\`

---

## Current Status

**Phase:** Collector Enhancement → analyzed → Analyze QA tool built → Analyzer v3 spec'd → Layer 7 implemented+corrected → ffmpeg fixed → **Layer 3 run on all 16/16 CONFIRMED variants** → Layer 5 execution diagnosis implemented+validated on 008B → **Layer 5 competitor benchmark escalated to a full statistical, multi-competitor architecture and run for product 008 (4/5 target)** → **findings synthesized in `CREATIVE_GAP_ANALYSIS.md`.** `data/video_results.csv` holds correct, verified, complete data for all 16 variants across products 002/003/007/008 — unchanged by any Layer 3/5/7 work, which write only to `data/tiktok-analytics/product*/`. Collector QA and Analyze QA both pass cleanly for this scope. **PRODUCT 009 DECISION: PROCEED ✅** (see session 5), independently re-verified by `scripts/analyze_qa.py` (session 6) — session 5's pacing recommendation is known to be misdirected (sessions 8/9) and now has a much more precise, evidence-backed picture (sessions 10-15) than a single cause. **Per explicit instruction, `learning_report.json` is deliberately NOT updated yet — holding until Layers 7, 3, and 5 are all complete (across all variants/products) and reviewed together; `CREATIVE_GAP_ANALYSIS.md` is the interim synthesis for that review.** Layer 5 (execution + competitor benchmark) has only run on 008B / product 008 so far — not yet extended to the other 15 variants or 3 products. Layers 1, 2, 4, 6, 8, 9, 10 of Analyzer v3 remain spec-only, not implemented. Products 001/004/005 remain a separate, pre-existing, documented gap — out of scope, not blocking. **2026-08-03: architectural decision approved — the platform must support two operating modes, Historical Backfill Mode and Daily Incremental Production Mode (full permanent requirement in `TIKTOK_AGENT_PLAN.md` → "Operating Modes — Permanent Production Requirement"). Approved as architecture only — NOT implemented; no scripts or workflow changed.** Next approved technical direction, in order: (1) ~~fix the `--seed-urls` `like_count: None` ranking bug in `scripts/layer5_competitor_benchmark.py`~~ — **DONE, session 17, regression-tested.** (1b) ~~fix the blob-fetch frame-identity bug (session 18's Bug 4) that blocked broadening to 002/003/007~~ — **DONE, session 19** (canvas-capture rewrite, regression-tested, NOT yet validated live). (2) broaden the Layer 5 competitor benchmark to products 002, 003, and 007 — **not yet run to completion, resume here this evening.** (3) review that expanded evidence before touching `learning_report.json` or the creative pipeline — before generalizing product 008's findings to the rest of the portfolio or generating Product 009. **2026-08-10 (session 20): additional architecture decision approved — a new Layer 5 Same-Product Visual Identity Gate (DINOv2 local-embedding corroborated-match filter + Claude Vision adjudication for ambiguous cases, replacing keyword/caption filtering as the sole safeguard against category-only false positives) is now spec'd in `ANALYZER_V3_SPEC.md`. Approved as architecture only — NOT implemented, NOT installed; no packages added, no scripts changed.** **2026-08-10 (session 21): superseded by a permanent rule change — Layer 5's actual goal is narrow-CATEGORY benchmarking, not exact-SKU matching, so the Visual Identity Gate above is DEFERRED, not required right now (kept as a design for later, e.g. Layer 10).** **CATEGORY-BASED BENCHMARK RULE (permanent, active, session 21):** a Layer 5 competitor is admitted if `CATEGORY_RELEVANCE_VERIFIED = true` (same narrow product category — e.g. any magnetic car phone mount for product 002, not the identical listing) AND `FRAME_IDENTITY_VERIFIED = true` (frames genuinely belong to the claimed URL/creator) AND it has reliable success/performance evidence (real like_count/view_count/ranking, not a random category-relevant video). Exact product/SKU identity is explicitly not a required gate. **Product 002 is now `QA_PASSED_PRODUCT002` under this rule** (5/5 competitors: `@baseus.us` 19.4K likes, `@mpowerautospk` 3.7K, `@max_stock_israel` 2.3K, `@lufeshop4` 1.2K, `@mengdan41` 915 — all visually frame-identity-verified, all genuinely magnetic-car-phone-mount category, automated QA 0 FAIL/1 non-blocking WARN). **2026-08-10 (session 22): Product 003 is now also `QA_PASSED_PRODUCT003` under this rule** (5/5 competitors: `@dustyshops` 133.1K likes, `@dem.poptarts` 74.8K, `@deshopido` 62.6K, `@elnazhamai` 39K, `@bullseyeonthebargain` 34.4K — all category-relevance PASS on a real "mini bag sealer clip" gadget in 3 distinct device models, all frame-identity PASS including full-video spot checks, automated QA 0 FAIL/1 non-blocking WARN). **2026-08-10 (session 23): Product 007 is now also `QA_PASSED_PRODUCT007` under this rule** (5/5 competitors: `@phoebeyuee` 110.5K likes, `@phoebeyuee` (2nd video) 20.6K, `@tidytravelshop` 63.7K, `@tidytravelshop` (2nd video) 5.6K, `@ejanne0` 2.3K — all category-relevance PASS on genuine hanging seat-back organizers, one initially-selected candidate rejected mid-batch for being a center-console organizer instead and replaced, all frame-identity PASS including full-video spot checks, automated QA 0 FAIL/1 non-blocking WARN). Exact-SKU matching remains **DEFERRED — NOT REQUIRED** for this goal across all three products. **All three planned products (002, 003, 007) are now QA_PASSED, and the cross-product synthesis has now been written into `CREATIVE_GAP_ANALYSIS.md` (documentation-sync pass, same session 23).** `TIKTOK_AGENT_PLAN.md`'s changelog and `ANALYZER_V3_SPEC.md`'s stale top-of-file status line (previously still said "SPEC ONLY — NOT IMPLEMENTED" despite Layers 3/5/7 being implemented) were corrected in the same pass. **The only thing NOT done in this documentation sync, deliberately: `learning_report.json` and Product 009 remain untouched — that is the next real decision, not a documentation task.** **CORRECTION (2026-08-11, session 26 documentation sync): the "`learning_report.json` is deliberately NOT updated yet" statement earlier in this same paragraph is now stale. Session 26 (below) incorporated the approved Layer 3+5+7 creative-rules synthesis into `learning_report.json` — see the CHECKPOINT line above for current, authoritative status. Product 009 and the creative pipeline remain untouched.**

**CHECKPOINT (updated 2026-08-11, session 26): the approved Layer 3+5+7 creative-rules synthesis is now incorporated into `learning_report.json`.** `data/learning_report.json` has a new `creative_rules` block: 3 `PERMANENT_CREATIVE_RULE`s (open on real hand/person; avoid marketplace/catalog-style presentation; show the actual mechanism) with their exact evidence counts, Rule 4 kept `MODIFIED_RULE`/non-permanent with `do_not_promote_to_permanent: true`, the combined Layer 3+5+7 diagnosis with an explicit causality guardrail (no competitor retention curves, no causal proof, forbidden overclaims listed), the sub-10-view data-quality finding, and a `next_causal_test` scaffold with `test_status: NOT_YET_RUN` (no fabricated results). No pre-existing field was deleted or overwritten; `product_009_brief.first_frame_requirement` was flagged as superseded (via a new `creative_rules_compliance_note`) rather than rewritten. Re-ran `scripts/analyze_qa.py --product-id 002,003,007,008` against the updated file — still 6/6 PASS, unchanged. **NEXT: awaiting human review of this `learning_report.json` update before touching the creative pipeline or generating Product 009.** The creative pipeline, Product 009, and Daily Incremental Mode remain untouched. All 4 products remain `QA_PASSED_PRODUCT002/003/007/008` (sessions 21-24) and the cross-product synthesis in `CREATIVE_GAP_ANALYSIS.md` (session 25) is unchanged.

**RESUMED 2026-08-10 (session 23).** Next action, in order — updated to reflect session 23's progress. The "broaden Layer 5 to 002/003/007" task is now fully complete:
1. ~~Fix the blob-fetch bug~~ — **DONE, session 19.** ~~Validate the canvas-capture approach live~~ — **DONE for products 002 (session 21), 003 (session 22), and 007 (session 23).**
2. ~~Re-run products 003 and 007 under the category-based rule~~ — **DONE for both.** 003: `QA_PASSED_PRODUCT003` (session 22). 007: `QA_PASSED_PRODUCT007` (session 23) — one category-relevance failure (a center-console organizer mistaken for a seat-back organizer) caught mid-batch and replaced via the same multi-query-triage method used for 003.
3. ~~Personally open and visually inspect every extracted frame~~ — **DONE for all 5 competitors × 3 products (002/003/007)**, including full-video spot checks beyond the 0-8s grid for all three.
4. ~~Run `layer5_benchmark_qa.py` as an independent second check~~ — **DONE for all three: 0 FAIL, 1 non-blocking WARN each.**
5. ~~The `qualitative_review`/full-video creative-comparison pass~~ — **DONE for all three products** in chat output. The CREATIVE RULES list is now confirmed consistent across all three (4 rules, each backed by 0/12 of our variants vs. 15/15 verified competitors doing the opposite). Not yet written to a file.
6. ~~Update `CREATIVE_GAP_ANALYSIS.md` with the cross-product synthesis~~ — **DONE for 002/003/007, same session (documentation-sync pass).** Findings 1-5 upgraded from "008-only, hypothesized for the rest" to "independently confirmed by QA-verified benchmarks on 002/003/007 (15 competitors)." New finding #8 added (the "second beat" pattern from session 22-23), based on 002/003/007 evidence only. `TIKTOK_AGENT_PLAN.md` and `ANALYZER_V3_SPEC.md`'s stale status lines corrected in the same pass — see below. **CORRECTION (2026-08-11 checkpoint audit): that same documentation-sync pass incorrectly rolled Product 008 into this as "confirmed on all 4 products, 19 real competitors total" and implied `QA_PASSED`-equivalent status for 008. Product 008's Layer 5 benchmark was created 2026-07-02 (commit `f003a7b`) — before `layer5_benchmark_qa.py` existed (session 19), before the category-based rule (session 21), and before the canvas-capture frame-identity fix (session 19/21). It has never been re-run under any of those, and no `QA_PASSED_PRODUCT008` result exists anywhere in the repo. This overclaim has been corrected in `CREATIVE_GAP_ANALYSIS.md` and here.**
7. ~~CORRECTED CHECKPOINT (2026-08-11): `PRODUCT008_RECHECK_PENDING` → Product 008 re-check → QA → full-video comparison~~ — **DONE, session 24.** Re-ran Product 008's Layer 5 competitor benchmark from scratch under the current methodology (archived pre-methodology evidence, 5 genuine competitors, canvas-capture extraction, category-relevance + frame-identity PASS on all 5, `layer5_benchmark_qa.py` 0 FAIL/1 non-blocking WARN). Reached `QA_PASSED_PRODUCT008`. Full detail in session 24 below.
8. **Commit the canvas-capture rewrite to git** — `scripts/layer5_competitor_benchmark.py` is still uncommitted (session 17's earlier fix, commit `26bc876`, and session 18's ranking/relevance-filter fixes, commit `b49dbcf`, were already committed). No further code changes were needed in sessions 22, 23, or 24 — the script itself remains exactly as of session 19's canvas-capture rewrite.
9. ~~Apply the new Layer 5 Same-Product Visual Identity Gate...~~ — **SUPERSEDED, session 21.** Layer 5's goal is explicitly narrow-category benchmarking, not exact-SKU matching (see "CATEGORY-BASED BENCHMARK RULE" above and in `ANALYZER_V3_SPEC.md`). DEFERRED — NOT REQUIRED for this goal; nothing installed.
10. ~~NEW OPEN NEXT STEP (session 24): cross-product synthesis across all 4 products (002, 003, 007, 008)~~ — **DONE, session 25.** `CREATIVE_GAP_ANALYSIS.md` rewritten as the final four-product synthesis; `ANALYZER_V3_SPEC.md` updated with a permanent cross-product learning architecture section. Full detail in session 25 below.
11. ~~OPEN NEXT STEP (session 25): combined human review of Layers 3 + 5 + 7 together~~ — **DONE.** Approved, with the authoritative conclusions (3 Permanent Creative Rules, Rule 4 kept non-permanent, the causality guardrail, and the sub-10-view data-quality finding) supplied directly and used verbatim as the basis for session 26's `learning_report.json` update below.
12. ~~Touch `learning_report.json` to reflect the approved synthesis~~ — **DONE, session 26.** New `creative_rules` block added; full detail below.
13. **OPEN NEXT STEP (session 26), not started: human review of the `learning_report.json` update itself.** Only after that: touch the creative pipeline or generate Product 009. This is a real decision, not a documentation task.

### 2026-08-11 (session 26) — Incorporated the approved Layer 3+5+7 creative-rules synthesis into `learning_report.json`

**Scope, per explicit instruction and approved conclusions supplied directly: update `learning_report.json` only (plus this file, to record the change). Did not modify the creative generation pipeline, did not generate Product 009, did not implement Daily Incremental Mode, did not start any other Analyzer v3 layer, ran no new TikTok searches or competitor benchmarking, did not alter the approved Layer 3/5/7 findings, and did not promote Rule 4 to permanent.**

**Inspected the existing file first, as instructed.** `data/learning_report.json` (generated 2026-07-02) is a flat JSON file from an earlier hook-type/pricing analysis, predating the creative-rules work entirely: top-level `generated`, `decision` (`PROCEED`), `products_analyzed`, `data_vintage`, `learning` (hook-type win counts, best category/price range, `retention_avg_2s: 0.45`), `product_009_brief` (hook/price/pacing recommendations for a future product), `pause_reason`, `change_strategy_issue`. Confirmed via `scripts/analyze_qa.py`'s Check 2 (`check_2_learning_report_schema`) exactly which fields are schema-checked (`decision`, `pause_reason`/`change_strategy_issue`, 5 named `product_009_brief` fields, `learning.hook_type_wins`, `data_vintage.confirmed_rows`) so the new additions wouldn't collide with it. Preserved the existing structure and every existing value unchanged; added new top-level sections rather than redesigning the file.

**Added a new `creative_rules` top-level block**, containing:
- `permanent_rules`: Rules 1-3, each with its title, `classification: PERMANENT_CREATIVE_RULE`, exact evidence counts (0/16 vs. 20/20 for Rules 1 and 3; 16/16 vs. 0/20 for Rule 2), and `supported_across_products: [002, 003, 007, 008]`. Rule 2 carries its `revised_from` note (the original narrow "no AliExpress screenshot" wording vs. the broader promoted wording) and Product 008's CGI-render mechanism distinction.
- `modified_rules`: Rule 4 with `classification: MODIFIED_RULE`, `permanent: false`, `evidence_scope: EVIDENCE_3_OF_4_PRODUCTS`, the explicit list of products it's supported in (003/007/008) vs. not yet evaluated (002), and a `do_not_promote_to_permanent: true` flag.
- `combined_layer_3_5_7_diagnosis`: the WHAT/WHEN/HOW summary plus a `causality` sub-block that explicitly lists what we have (direct creative/retention evidence, repeated correlation) vs. what we do not have (competitor retention curves, causal proof), and a `forbidden_claims` array naming the two specific overclaims the synthesis ruled out ("competitors retain viewers better at 2 seconds", "competitors decline more slowly").
- `data_quality_findings`: the sub-10-view artifact (003C n=1, 008A n=4), tagged `DATA_QUALITY_SAMPLE_SIZE`, `not_a_creative_rule: true`, with the 12/16 usable-variant outcome attached (all WEAK/MARGINAL, none STRONG, 0.25-0.45 range).
- `status_for_creative_pipeline`: states plainly that the 3 permanent rules are requirements for the next creative test, not causally proven wins, and that the pipeline has not been touched.
- `next_causal_test`: the OLD-pattern vs. NEW-pattern comparison scaffold, `test_status: NOT_YET_RUN`, `results: null` — no fabricated outcome.
- `source_documents` was omitted from the summary above but is present in the file, pointing to `CREATIVE_GAP_ANALYSIS.md`, `ANALYZER_V3_SPEC.md`, and this file's session 25 entry.

**Added `last_updated` and `checkpoint` top-level fields** (`2026-08-11`, and a short status string) alongside the untouched original `generated` field, so the file records both when the hook-analysis data was generated and when the creative-rules synthesis was folded in.

**One existing field flagged as superseded, not rewritten:** `product_009_brief.first_frame_requirement` says "standard approach" is acceptable, reasoning that 2s retention isn't CRITICAL — that predates and is now in tension with Permanent Rules 1-3, which identify our static/catalog opening itself as the unanimous defect. Added a `creative_rules_compliance_note` field directly on `product_009_brief` pointing to the new `creative_rules` block, rather than editing the brief's own historical numbers/text, since regenerating Product 009 guidance is out of scope this session. Also noted, not fixed: `learning.retention_avg_2s` (0.45, a single figure from the older hook-type analysis, computed across all 16 CONFIRMED rows) doesn't exactly match the newly-stated 0.25-0.45 range for the 12 statistically-usable (>=10 view) variants — a different underlying calculation/scope (all rows vs. only the statistically-usable subset), left untouched as it belongs to the pre-existing hook-analysis section, not the creative-rules synthesis this task covers.

**Validated the change.** `python -c "json.load(...)"` confirms the file is still valid JSON. Re-ran `scripts/analyze_qa.py --product-id 002,003,007,008` against the updated file: still **6/6 PASS** (Learning Report Exists & Valid, Learning Report Schema, Winner Consistency, Retention Consistency, Decision Logic Consistency, Analysis File Present) — identical result to before the edit, confirming none of the additions collided with the existing schema checks.

**Committed to git this session:** pending — `data/learning_report.json` and this file are updated in the working tree, not yet committed.

**The creative pipeline, Product 009, and Daily Incremental Mode remain untouched. Awaiting human review of this `learning_report.json` update before either is touched.**

### 2026-08-11 (session 25) — Cross-product synthesis across all four products; made the methodology a permanent architecture requirement

**Scope, per explicit instruction: cross-product synthesis only, using already-validated evidence (existing Layer 3/5/7 files for all 16 variants and 20 competitors). No new TikTok searches, benchmarks, or browser research performed — none were needed. Did not touch `learning_report.json`, the creative pipeline, Product 009, or Daily Incremental Mode.**

**Aggregated Layer 3 + Layer 7 evidence across all 16 variants (script-computed, not hand-tallied):** cause **a** (weak/static opening, no motion) and cause **c** (AliExpress/catalog feel) are both LIKELY in **16/16 variants — unanimous across all four products**. Cause **b** (unclear product) and cause **h** (non-native Hebrew) are both 0/16 — confirmed strengths, not defects. Cause **e** (hook-product mismatch) is 5/16; cause **d** (generic hook) is 6/16. Retention: only 12/16 variants have ≥10 views (statistically usable); among those, first-2-second retention ranges 0.25–0.45 (avg 0.38) and **none reach `STRONG`**. The portfolio's only two `STRONG`/high-`MARGINAL` results (003C 0.84, 008A 0.75) both come from variants with 1 and 4 total views respectively — a new finding, surfaced only by lining up all 16 side by side: every "good-looking" number in the dataset is a sample-size artifact.

**Aggregated Layer 5 evidence across all 20 QA-verified competitors (5 per product):** all carry real fetched `like_count` (176–133,100). Personally re-confirmed this session, by directly viewing frames rather than trusting prior session prose: `002B`, `003A`, and `007A` each cut to a **literal scraped AliExpress listing screenshot** with real marketplace UI chrome (delivery dates, discount banners, security/returns badges) — confirming Rule 2's original "screenshot" framing is accurate for those three products, and confirming by contrast that 008's two-CGI-render pattern (already established session 24) is a genuinely different mechanism producing the same cause-c defect.

**Rule-by-rule reclassification, with numeric evidence (full detail and per-competitor citations in `CREATIVE_GAP_ANALYSIS.md`):**
1. **Open on real hand/person engagement, not a static render — `PERMANENT CREATIVE RULE`.** 0/16 our variants vs. 20/20 verified competitors (18/20 immediate, 2/20 — both product 008's two lowest performers — briefly delayed but still ahead of anything ours ever shows). Unanimous, all 4 products.
2. **Avoid marketplace/catalog-style presentation (screenshot OR static render) — `PERMANENT CREATIVE RULE — revised from the original Rule 2`.** Literal "no screenshot" wording: true for 12/16 (002/003/007), false for 008's 4/16 — that original narrow wording was correctly `MODIFIED`. But the revised wording (broader cause-c framing) itself has full unanimous evidence: 16/16 our variants, 0/20 competitors, across all four products — so the revised rule is promoted to `PERMANENT CREATIVE RULE`, with the revision history kept visible. **Approval correction (2026-08-11): reclassified from `MODIFIED RULE` to this permanent status, since the revised wording — unlike the original — has full portfolio-wide evidence.**
3. **Show the actual mechanism/action — `PERMANENT CREATIVE RULE`.** 0/16 vs. 20/20, unanimous. Sharpest instance: 008D's "360° rotation" hook paid off by a static arrow icon, never real rotation.
4. **Meaningful progression beyond the plain demo, in the top-performing competitor — `MODIFIED RULE`.** Confirmed for 003 (comparison + multi-bag showcase), 007 (fully-loaded reveal ending), 008 (sustained 35.4s engagement in the top performer, a discrete 2-cut payoff structure in the runner-up). **Not separately checked for 002** — reported as an evidence gap, not filled in with new research per explicit instruction. Rewritten to allow "sustained engagement" as an alternative to a discrete added segment, since 008's top performer doesn't have one.

No rule was `REJECTED`. No fifth rule was forced — the only additional cross-product finding (the sub-10-view retention artifact) is a data-reliability caveat, not a creative-content pattern, and is documented as such rather than shoehorned into the rule list.

**Combined Layer 3 + Layer 5 + Layer 7 diagnosis, with explicit causality tiers:** Layer 3 = WHAT (static, catalog-feeling opening, 16/16 direct evidence) is shown Layer 7 = WHEN our own viewers leave (already down to 0.25–0.45 retention by 2s, 12/16 direct evidence) while Layer 5 = HOW real successful competitors in the same categories present their creative differently on screen (20/20 direct evidence — real human/product interaction and real mechanism demonstration instead of static/catalog presentation). **Approval correction (2026-08-11): competitor retention was never measured, so Layer 5's contribution here is strictly about creative presentation — this document does not claim, and must not be read as claiming, that competitors "decline less fast" or retain viewers better than we do.** This three-layer convergence, repeated independently across 4 product categories, is labeled explicitly as a **repeated correlation** in `CREATIVE_GAP_ANALYSIS.md` — not a proven causal chain. No variant of ours has ever been produced that follows the competitor pattern and had its own retention measured, so no rule in this document may yet be described as "proven to improve performance."

**Made the methodology permanent (`ANALYZER_V3_SPEC.md`):** added a new "CROSS-PRODUCT LEARNING ARCHITECTURE" section under Layer 5, codifying: the per-product 7-step workflow (identify category → find 5 competitors → category-relevance verify → frame-identity verify → QA → full-video comparison → identify differences); the permanent operating rules (exact-SKU not required, category required, performance evidence required, `REJECT → NEXT CANDIDATE`, QA-first `SMALLEST TEST → QA → INSPECT → SCALE`, full-video not just opening, preserve historical evidence, personally inspect every competitor); the cross-product learning pipeline (5-per-product → QA → full-video comparison → repeated differences → Permanent Creative Rules → combined Layer 3+5+7 review → only then `learning_report.json`/creative pipeline); the three-tier causality discipline (direct evidence / repeated correlation / untested hypothesis); the permanent Layer 3=WHAT / Layer 5=HOW / Layer 7=WHEN role definitions; and a standing requirement that any rule adopted into the creative pipeline must eventually be causally tested, not just correlationally supported. Updated the document's top-of-file status line to match.

**Committed to git this session:** pending (this session's edits to `CREATIVE_GAP_ANALYSIS.md`, `ANALYZER_V3_SPEC.md`, and this file are in the working tree, not yet committed).

**`learning_report.json`, the creative pipeline, Product 009, and Daily Incremental Mode were not touched — the next step is a human review of the combined Layer 3+5+7 diagnosis, not another automated pass.**

### 2026-08-11 (session 24) — Corrected the checkpoint, then re-ran Product 008's Layer 5 competitor benchmark from scratch under the current methodology, reaching `QA_PASSED_PRODUCT008`

**Checkpoint audit (before any new work): confirmed Product 008 had never actually been re-run.** User-requested audit of `PROJECT_STATUS.md` against the underlying git history and evidence files found that session 23's documentation-sync pass had incorrectly rolled Product 008 into "confirmed on all 4 products, 19 real competitors total" by simple arithmetic (5+5+5+4=19), without Product 008 ever passing `layer5_benchmark_qa.py` (which didn't exist until session 19, five weeks after Product 008's original 2026-07-02 benchmark), the category-based rule (session 21), or the canvas-capture frame-identity fix (session 19/21). Corrected both this file and `CREATIVE_GAP_ANALYSIS.md` to `PRODUCT008_RECHECK_PENDING` before doing any new work — see the 2026-08-11 correction notes above and below.

**Scope, per explicit instruction: Product 008 only. Did not touch `learning_report.json`, Product 009, the creative pipeline, Daily Incremental Mode, or DINOv2/OpenCLIP work. Did not perform cross-product synthesis.**

**Archived pre-methodology evidence intact before running anything new.** Moved Product 008's entire 2026-07-02 Layer 5 competitor benchmark (`product008_layer5_competitor_benchmark.json`, `layer5_competitor_frames/`, and stray single-competitor frames from an even earlier pre-statistical-benchmark attempt) into `product008/layer5_competitor_frames_archive/2026-07-02_pre_methodology/`. Nothing deleted.

**Small-scope live validation (target 2) confirmed the pipeline works for this category.** Query `מעמד לטאבלט מסתובב` surfaced `@xyxzq1sfe1` (7,027 likes — genuine rotating tablet stand, hand demo) and `@anjbbln` (6,172 likes — an unrelated cooking video). Rejected `@anjbbln` per the REJECT → NEXT CANDIDATE rule; no systemic bug, just an empty-caption search false-positive.

**Full run: seeded the 4 previously-identified genuine competitors from the old (pre-methodology) benchmark + the newly-confirmed 5th, re-extracted fresh under the current canvas-capture method rather than trusted from old data.** Final 5: `@unboxingexpert` (2,869 likes), `@toptech.mx` (1,211), `@yeuunnt.22` (78,300 — a gooseneck bed-clamp mount, within product 008's own "arm-mount or desk stand" category definition), `@xyxzq1sfe1` (7,027), `@digitalnexus1` (176 — a floor-standing telescopic arm variant, also within category). One natural CAPTCHA on `@xyxzq1sfe1`'s frame extraction, cleared after 6s. Extended beyond the standard 0-8s grid with a disposable ad hoc script (reusing `wait_for_video_ready()`/`capture_frame_canvas()` unmodified, same convention as sessions 22-23) to capture mid/late/near-end frames per competitor for the full-video comparison.

**Frame identity + category relevance: 5/5 PASS.** All 5 personally inspected across opening/grid/mid/late/near-end frames: genuine, internally coherent, no cross-candidate leakage, no wrong-subcategory product. The previously-flagged wrong-category `@eacoswgx` (bendable phone grip) resurfaced in fresh search and was correctly excluded again.

**Automated QA:** `layer5_benchmark_qa.py --product-id 008` → 0 FAIL, 1 non-blocking WARN (same caption-placeholder limitation as 002/003/007, resolved by direct visual confirmation). **Status: `QA_PASSED_PRODUCT008`.**

**Full-video creative comparison** (cross-referenced `008A`-`008D_layer3_evidence.json` + `data/008-video-config.json`; directly re-inspected 008B's own opening frames to confirm): all 4 of our variants open on a static, glossy 3D-CGI product render (no photography, no hand, no human, zero motion for the full hook window) hard-cutting at 3s to a *second, different* static CGI render — notably, NOT a literal AliExpress screenshot, unlike 002/003/007. Retention: 008B MARGINAL 42%@2s (n=114, reliable), 008C WEAK 39%@2s (n=133, reliable); 008A/008D are n=4/n=2 views and not statistically meaningful.

**CREATIVE RULES verdict for Product 008:**
1. Open on a hand/person, not a static render — **SUPPORTED.** 4/5 competitors open hand/person-first; the 5th (top performer) opens on a child already mid-use. 0/4 of our variants do.
2. Never cut to an AliExpress/marketplace screenshot — **MODIFIED.** Unlike 002/003/007, our variants don't cut to a literal screenshot — they cut between two different static CGI renders instead. The literal rule is technically satisfied; the catalog/marketplace *feel* it targets is still fully present via a different mechanism.
3. Show the actual mechanism/action, not just display — **SUPPORTED, sharper example.** All 5 competitors show real hands rotating/adjusting/mounting the product. 008D's hook promises a wordless visual reveal of the 360° rotation, but the frame shown is a static arrow graphic — the product's own core feature depicted by an icon, never demonstrated.
4. Distinct second beat correlates with top performer — **SUPPORTED, new nuance.** Top performer (`@yeuunnt.22`, 78.3K likes) is 35.4s, roughly 2-3x the other competitors' length, driven by sustained real interaction rather than a discrete added segment. `@xyxzq1sfe1` (7,027 likes) shows a clearer discrete second beat (2 detected hard cuts, demo → payoff shot). The two weakest competitors are single continuous takes.

**New Product-008-specific finding:** the single most concrete instance across all 4 products of Rule 3's violation — the product's entire premise is "360° rotation," and the pipeline depicts that rotation with a static arrow icon instead of ever actually rotating it on camera, while every verified competitor shows a real hand physically rotating it.

**Committed to git this session:** nothing yet. `data/tiktok-analytics/product008/product008_layer5_competitor_benchmark.json` is updated in the working tree (tracked file, not yet committed). New untracked evidence: `product008/layer5_competitor_frames_archive/2026-07-02_pre_methodology/` (old evidence, preserved) and the now-trustworthy `layer5_competitor_frames/` (gitignored, like the other products).

**`CREATIVE_GAP_ANALYSIS.md` and `learning_report.json` deliberately NOT updated with this — cross-product synthesis across all 4 products, and the standing review-before-touching rule, still apply.**

### 2026-08-10 (session 23) — Applied the category-based Layer 5 rule to Product 007: caught and replaced a wrong-subcategory competitor mid-batch, reached `QA_PASSED_PRODUCT007`, and confirmed the Creative Rules across all three products

**Scope, per explicit instruction: Product 007 only, same fast method as session 22, no code changes unless a real blocking bug proven. Did not update `CREATIVE_GAP_ANALYSIS.md` or `learning_report.json`, did not touch the creative pipeline, did not generate Product 009.**

**First attempt: 2 of 5 category FAIL, both a different failure mode than 003's.** Ran `layer5_competitor_benchmark.py --product-id 007 --query "מארגן גב מושב לרכב" --target 5 --relevance-keywords "מארגן,מושב,רכב,organizer,seat,car,back" --exclude-keywords "כרית,cushion"` as planned. Visual inspection found: `@gapbuddyofficial`'s two videos (113.8K and 48.6K likes, the top 2 by engagement) were actually about a **seat-GAP filler** (a wedge product solving "things falling into the crack between seat and console"), not a seat-BACK organizer — a different sub-product entirely, correctly excluded by the reject list's "unrelated car storage products" clause even though it's superficially car-storage-adjacent. `@cicipetshop01.my` (6.1K likes) was a completely unrelated Dubai hotel travel ad. Only `@ostliqzxozv` (97.7K) and `@phoebeyuee` (20.6K) were genuine matches.

**Fix: same multi-query-triage method as session 22.** Searched 5 phrases (`תיק תלייה למושב רכב`, `ארגונית לגב הכיסא ברכב`, `car seat back organizer`, `hanging car organizer`, `car backseat organizer with hooks`), merged to a 45-candidate pool, shortlisted 20, triaged with one quick frame each. Surfaced `@phoebeyuee`'s second, higher-performing video (110.5K likes) and two `@tidytravelshop` videos (63.7K, 5.6K) as clear, strong matches. Re-ran the official script with the 5 highest-confidence candidates as `--seed-urls`.

**Caught mid-batch: the seeded #2 performer was also wrong-subcategory.** Visual inspection of the seeded run found `@ostliqzxozv` (97.8K likes) was actually a **center-console/armrest organizer** (mounted between the front seats, not hanging off a seat-back for rear passengers) — a genuinely different product placement, not caught by the triage's single early frame. Per the stop-the-batch rule, did not accept it. Checked several more triage candidates and replaced it with `@ejanne0` (2,271 likes, explicit "Organise back seat of my car" on-screen caption, a real headrest-mounted tablet/mesh-pocket organizer) — re-ran the official script a second time with the corrected 5 seeds.

**Frame identity + category relevance: 5/5 PASS (final set).** `@phoebeyuee` ×2 (110.5K, 20.6K), `@tidytravelshop` ×2 (63.7K, 5.6K — the "Prototype → Final Product → TidyTravel"-branded template, same structure across both), `@ejanne0` (2.3K) — all visually confirmed genuine hanging seat-back/headrest organizers, internally coherent across full-video spot checks (mid/late/near-end timestamps beyond the standard 0-8s grid), no cross-candidate leakage.

**Automated QA:** `layer5_benchmark_qa.py --product-id 007` → 0 FAIL, 1 non-blocking WARN (same caption-placeholder limitation as 002/003, resolved by direct visual/on-screen-text confirmation). **Status: `QA_PASSED_PRODUCT007`.**

**Full-video creative comparison:** cross-referenced the 5 verified competitors against our own 4 Product 007 variants' existing Layer 3 evidence (`007A_layer3_evidence.json`) + `data/007-video-config.json`. Same pattern as 002/003: our variants show one static, glossy AliExpress-style hero photo (0-2.5s, tablet playing a stock clip, a visibly composited fake sunset through the windshield) hard-cutting at 3s to a literal AliExpress price screenshot. Retention 41% (MARGINAL — the best of the three products so far, but the same underlying visual pattern). Every competitor shows real hands mounting/loading the organizer with continuous motion; the two highest performers both end on a "fully loaded reveal" shot across both rear seats — a distinct ending beat the lower performers lack.

**CREATIVE RULES FOR NEXT PRODUCT — now confirmed consistent across all three products (002, 003, 007), delivered in chat, not yet written to `CREATIVE_GAP_ANALYSIS.md`:**
1. Open on a hand already using the product, not a static render — 15/15 verified competitors across all three products do this; 0/12 of our variants do.
2. Never cut to an AliExpress/marketplace screenshot inside the video — 12/12 of our variants do this; 0/15 verified competitors do.
3. Show the actual mechanism/action, not just the product on display.
4. A distinct second beat beyond the plain demo (comparison, multi-product showcase, or a "fully loaded reveal" ending) is present in the highest-like-count competitor in all three products, absent from the lower performers.

**Committed to git this session:** nothing. `scripts/layer5_competitor_benchmark.py` remains unmodified — no blocking bug was found in either session 22 or 23; both fixes were search/seed-selection, not code. New untracked evidence: `product007/layer5_competitor_frames_archive/` (session-18 known-bad evidence, preserved), `product007/layer5_triage_multiquery/` (the discarded fast triage, kept for transparency), and the now-trustworthy `product007_layer5_competitor_benchmark.json`.

**All three planned products (002, 003, 007) are now `QA_PASSED` under the category-based rule. This phase of Layer 5 broadening is complete.**

**Documentation-sync addendum (same session, explicit instruction to update all project documentation so tomorrow's resume point is unambiguous):** wrote the cross-product synthesis into `CREATIVE_GAP_ANALYSIS.md` — findings 1-5 upgraded from "008-only, hypothesized for 002/003/007" to "confirmed on all 4 products, 19 real competitors total, full-video not just opening"; added new finding #8 (the "second creative beat" pattern observed in sessions 22-23); revised the closing caveat section to remove the now-outdated "002/003/007 not yet measured" note. Added a dated changelog entry to `TIKTOK_AGENT_PLAN.md` per that file's own "summary only, detail lives in `PROJECT_STATUS.md`" convention. Corrected `ANALYZER_V3_SPEC.md`'s top-of-file status line, which had been stale since before session 7 (it said "SPEC ONLY — NOT IMPLEMENTED" for the whole document even after Layers 3/5/7 were implemented) — now correctly scopes that label to only the layers that are actually still spec-only (1, 2, 4, 6, 8, 9, 10). **Not touched in this sync, deliberately: `learning_report.json` and Product 009 — those remain a real pipeline decision, not a documentation-completeness task, and the standing review-before-touching rule still applies (item 7 above).**

**⚠️ CORRECTION (2026-08-11, checkpoint audit): the "confirmed on all 4 products, 19 real competitors total" phrasing quoted above was the error.** Product 008 was never re-run under the methodology this same session had just finished validating (canvas-capture fix, category-based rule, `layer5_benchmark_qa.py`) — it was rolled into the count by simple arithmetic (5+5+5+4=19), not by re-verification. Corrected to scope the "confirmed" claim to 002/003/007 (15 competitors) only, in both this file (see checkpoint banner and item 6 above) and `CREATIVE_GAP_ANALYSIS.md`. Product 008 status restored to `PRODUCT008_RECHECK_PENDING`.

### 2026-08-10 (session 22) — Applied the category-based Layer 5 rule to Product 003: fixed a too-broad search query, reached `QA_PASSED_PRODUCT003`, and completed the first full-video creative comparison

**Scope, per explicit instruction: Product 003 only, fast method, no code changes unless a real blocking bug proven. Did not start Product 007, did not update `CREATIVE_GAP_ANALYSIS.md` or `learning_report.json`, did not touch the creative pipeline.**

**First attempt failed on category relevance, not on Layer 5 itself.** Ran `layer5_competitor_benchmark.py --product-id 003 --query "אוטם שקיות מיני" --target 5` as originally planned. Visual inspection of all 5 selected candidates found only 1 genuinely relevant (`@max_stock_israel`, a real mini vacuum sealer) — the other 4 were a Sephora makeup haul, a delivery-bag unboxing, a perfume-miniatures collection video, and a travel/toiletry pouch video, all pulled in because the query's word "bag" is generically common and most candidates had no real caption to filter against (TikTok's placeholder title, not a parsing bug). Diagnosed and stopped rather than trusting the batch.

**Fix: broadened to several narrow query variants + a fast, disposable single-frame triage, then re-verified through the real script.** Searched 5 phrases (`אוטם שקיות מיני`, `מלחם שקיות מיני`, `מכשיר לסגירת שקיות`, `mini bag sealer`, `handheld heat sealer`), merged to a 93-candidate pool, shortlisted 20 by real likes, and captured one quick triage frame per candidate (ad hoc script reusing `layer5_competitor_benchmark.py`'s existing functions unmodified, written to a throwaway `layer5_triage_multiquery/` folder, never trusted as final evidence). This surfaced a real, recurring "mini bag sealer clip" gadget (3 distinct device models) appearing across 8+ creators. Picked the 5 highest-`like_count` category-plausible candidates and re-ran the official `layer5_competitor_benchmark.py` with them as `--seed-urls` — the same unmodified script, guaranteeing the final benchmark JSON has the correct schema, real fetched `like_count`, and full 10-frame extraction. (One triage frame briefly looked wrong for `@max_stock_israel` — traced to the ad hoc triage script's own shorter per-navigation wait, not the production script; not investigated further since that URL wasn't needed for the final 5, per explicit instruction not to chase edge cases that don't affect the result.)

**Frame identity + category relevance: 5/5 PASS.** All 5 seeded competitors (`@dustyshops` 133.1K likes, `@dem.poptarts` 74.8K, `@deshopido` 62.6K, `@elnazhamai` 39K, `@bullseyeonthebargain` 34.4K) visually confirmed as a real physical bag-sealer clip actually clamped onto real snack bags (Lay's, PopCorners, Trolli, Jet-Puffed, shredded cheese), consistent per-candidate, visually distinct between candidates (3 device models), zero cross-leakage. Extended the check beyond the standard 0-8s frame grid with 3 extra frames per competitor (mid/late/near-end, same reused functions) specifically to support the full-video creative comparison below.

**Automated QA:** `layer5_benchmark_qa.py --product-id 003` → 0 FAIL, 1 non-blocking WARN (same caption-placeholder limitation as product 002, already resolved by direct visual/on-screen-text confirmation — e.g. `@elnazhamai`'s own on-screen caption literally reads "Amazon / Mini Bag Sealer"). **Status: `QA_PASSED_PRODUCT003`.** Exact-SKU matching remains `DEFERRED — NOT REQUIRED`, per the session-21 rule.

**Full-video creative comparison (first time this has been done at full-video scope, not just the 0-3s hook):** cross-referenced the 5 verified competitors' full runtimes against our own 4 Product 003 variants' existing Layer 3 evidence (`003A_layer3_evidence.json`) + `data/003-video-config.json`'s segment plan. Finding: all 4 of our variants share one identical, static 0-3s asset (lifestyle product photo → hard cut to a literal AliExpress screenshot) and, per the video-config, the remaining 12s is text-overlays-only (price, benefit line, social proof, CTA) with no footage of an actual sealing action anywhere in the full video — consistent with the pipeline's AliExpress-photos-only asset source. Every one of the 5 competitors, across their full runtimes, shows a hand actually clamping the device onto a real bag, and the two highest performers additionally include a second beat (a comparison vs. traditional chip clips, or a multi-product showcase) — not just a plain demo. All 4 of our variants: WEAK retention (25-39%), unchanged from prior findings.

**`CREATIVE RULES FOR NEXT PRODUCT` (delivered in chat, not yet written to `CREATIVE_GAP_ANALYSIS.md`):**
1. Open on a hand already using the product, not a static render — confirmed 5/5 in both products 002 and 003; 0/8 of our variants across both products do this.
2. Never cut to an AliExpress/marketplace screenshot inside the video — 8/8 of our variants do this; 0/10 verified competitors across both products do.
3. Show the actual mechanism/action, not just the product on display.
4. A second beat beyond the plain demo (comparison or multi-product showcase) correlates with the highest-performing competitors in both products.

**Committed to git this session:** nothing. `scripts/layer5_competitor_benchmark.py` remains unmodified (no bug required a fix). New untracked evidence: `product003/layer5_competitor_frames_archive/` (session-18 known-bad evidence, preserved not deleted), `product003/layer5_triage_multiquery/` (the discarded fast triage, kept for transparency), and the now-trustworthy `product003_layer5_competitor_benchmark.json`.

### 2026-08-10 (session 21) — Resumed the paused product 002 live trial, validated the canvas-capture fix live, diagnosed one visual anomaly, reached `QA_PASSED_PRODUCT002`, and adopted a permanent category-based Layer 5 rule

**Scope, per explicit instruction: Product 002 only. Did not run 003/007, did not install DINOv2/OpenCLIP, did not update `CREATIVE_GAP_ANALYSIS.md` or `learning_report.json`, did not touch the creative pipeline, did not generate Product 009, did not work on any other Analyzer v3 backlog item.**

**Step 1 — small-scope live validation (2 candidates, `--target 2`).** Ran `layer5_competitor_benchmark.py` for product 002 live, headed Chromium, real TikTok session (no CAPTCHA this run). 2/2 candidates (`@pixoloom`, `@mpowerautospk`) extracted 10/10 frames each. Every one of the 20 frames was opened and visually inspected: each candidate's frames form one coherent sequence matching its own URL/creator, zero cross-candidate leakage, zero readyState/seek failures. Recorded status: `LIVE_VALIDATED_SMALL_SCOPE` (deliberately not `PRODUCTION_VALIDATED` — one clean run, CAPTCHA path unexercised, only 2/5 target width).

**Evidence hygiene before scaling up:** archived all pre-existing frame evidence (today's 2-candidate run + session 18's stale `comp2`-`comp4` leftovers) into labeled, untouched folders under `layer5_competitor_frames_archive/` before running the full-target test, so the next run's output couldn't silently mix with old evidence. Nothing historical was deleted.

**Step 2 — full-target live validation (5 candidates, `--target 5`).** Same query/keywords. A real slider CAPTCHA appeared naturally on comp4 (`@mengdan41`) and cleared after 9s — confirmed genuine (not a false-positive detector trigger) via the saved screenshot, which showed the correct caption behind the puzzle overlay. Visually inspected all 10 of comp4's frames afterward: fully coherent, matching the expected content, zero contamination from the CAPTCHA interruption. Recorded: `CAPTCHA_PATH_LIVE_EXERCISED = true` (occurred naturally, not forced).

All 50 frames (5 candidates × 10) were opened and visually inspected. 4 of 5 candidates (`@baseus.us`, `@mpowerautospk`, `@lufeshop4`, `@mengdan41`) were immediately coherent. **comp2 (`@max_stock_israel`) showed an anomaly:** 2 of its 10 frames (t1.5, t2.0) depicted a completely different scene (a male hand, a car dashboard, a shade-sail canopy) sandwiched inside an otherwise-consistent marble-countertop unboxing sequence. Per the stop-the-batch rule, did not declare the batch passed — diagnosed before proceeding.

**Diagnosis of the comp2 anomaly.** Ran a minimal, isolated single-URL reproduction (fresh page load, same URL only, not the batch) that (a) re-captured frames at the same 4 timestamps and (b) logged a full DOM `<video>`-element census (count, `currentSrc`, `readyState`, `currentTime`, duration, dimensions, visibility, bounding box, ancestor path, and whether `querySelector('video')` matched each one) before and after every capture. Findings: the page does have 2-3 `<video>` elements at once (the main player, a muted 50×50px branding-loop background video, and a transient unloaded next-video preload slot), but `document.querySelector('video')` returned the *same* main-player element every single time across all 4 captures — its blob `currentSrc` never changed and its `currentTime` advanced monotonically. The re-capture independently reproduced the same car/shade-sail content at ~1.5s. Conclusion: the source video itself contains a brief cutaway from the marble-countertop scene to a car-demo shot and back — legitimate in-video editing, not a wrong-element capture bug. **No change made to `capture_frame_canvas()`/`wait_for_video_ready()`** — the fix rule (only modify on proof of ambiguity) was not triggered; evidence pointed the other way. comp2 reclassified `FRAME_IDENTITY_PASS`. comp3 (also not yet fully checked at the point the batch paused) was then finished: 10/10 frames coherent, no leakage.

**Independent QA gate.** With all 5/5 candidates visually PASS, ran `scripts/layer5_benchmark_qa.py --product-id 002`: **0 FAIL, 1 WARN** (non-blocking caption-relevance warning on candidates with no/placeholder captions — already resolved by the direct visual inspection above, which confirmed all 5 are genuinely magnetic-car-phone-mount content). **Status: `QA_PASSED_PRODUCT002`.**

**Permanent rule change adopted this session: Layer 5 now benchmarks by narrow product category, not exact SKU.** Full rule recorded in `ANALYZER_V3_SPEC.md`'s Layer 5 section under "CATEGORY-BASED BENCHMARK RULE" (and summarized in the Current Status section above). A competitor is admitted if `CATEGORY_RELEVANCE_VERIFIED = true` + `FRAME_IDENTITY_VERIFIED = true` + reliable success/performance evidence — exact product/SKU identity is explicitly not required. This means the session-20 Same-Product Visual Identity Gate (DINOv2/OpenCLIP) is **`DEFERRED — NOT REQUIRED FOR THE CURRENT LAYER 5 BENCHMARK GOAL`** (not deleted from the spec — kept as a design for a future exact-product-identity need, e.g. Layer 10's full market-wide system). Nothing was installed; no code was written for it.

**Informal creative comparison (product 002, not yet written to `CREATIVE_GAP_ANALYSIS.md`):** cross-referenced the 5 now-verified competitors against our own 4 variants' existing Layer 3 evidence (`002A`-`002D_layer3_evidence.json`). Finding: all 4 of our variants share one identical, static 0-3s asset — a motionless CGI-style product render (0-1.5s) hard-cutting into a literal AliExpress listing-page screenshot (2-3s, price/delivery-date UI chrome visible) — zero human presence, zero motion, zero real-use demonstration in any variant's hook window; only the hook text differs across A/B/C/D. Every one of the 5 successful competitors, by contrast, shows a real hand actively demonstrating the product in genuine use from the first frame, with continuous motion and zero marketplace branding. This is consistent with the four variants' uniformly WEAK retention (25-39% at 2s) being driven by the visual, not the copy. This comparison lives in this session's chat output only — not yet persisted to `CREATIVE_GAP_ANALYSIS.md` per explicit instruction to hold.

**Committed to git this session:** nothing. `scripts/layer5_competitor_benchmark.py` remains uncommitted (unchanged from session 19 — no code edits were needed). New untracked evidence: `layer5_competitor_frames_archive/`, `layer5_diagnosis_comp2_probe1/`, and the now-trustworthy `product002_layer5_competitor_benchmark.json`.

### 2026-08-10 (session 20) — Investigated existing Skills/MCP tools for Layer 5's category-vs-product false-positive problem (none fit); designed the Same-Product Visual Identity Gate architecture

**Scope:** purely research and design, requested explicitly as "design only, no implementation yet." Did not touch the paused product 002 live-trial item (session 19) at all — that remains the first thing to do on the next working session.

**Part 1 — Skill/MCP/package investigation, with security review (per explicit instruction: no installs, no downloads, no execution, no MCP added, no project files touched during this part).**
- Searched this session's connected tool index for image-similarity/visual-product-matching/reverse-image-search/CLIP-DINO-SigLIP/TikTok-competitor-intelligence capability — **no existing Claude Skill or connected MCP server does this.**
- Broadened to public GitHub/vendor options and security-reviewed each: **recommended** — Claude's own native vision (already available, zero install, zero credential risk) as the adjudication layer; **OpenCLIP** (`mlfoundations/open_clip`, 14.1k★, ML Foundations/LAION-affiliated, actively maintained) and **Meta's DINOv2** (`facebookresearch/dinov2`, official Meta AI Research repo) as the self-hosted embedding layer, DINOv2 preferred since it's tuned for instance-level "same object" retrieval rather than CLIP's category-level semantic similarity — directly relevant to the category-vs-product problem. **Rejected**: `deepghs-mcp` (1★, single unknown maintainer, ships a bash `install.sh`, requests HuggingFace + Pixiv tokens, wrong domain — anime datasets, not e-commerce) and `huuthangntk/claude-vision-mcp-server` (0★, single unknown maintainer, requires handing over an `ANTHROPIC_API_KEY` to third-party code for something Claude already does natively) — both flagged `DO NOT INSTALL — SECURITY REVIEW REQUIRED`. Commercial options considered and set aside for this specific step: Google Cloud Vision Product Search, TinEye (reputable vendors but weak fit), WinningHunter/EchoTik/Virlo (real TikTok product-intelligence SaaS, but built for market-wide discovery, not verifying one specific AliExpress SKU's photo against one specific extracted frame).
- **Conclusion:** building a thin visual-matching layer on DINOv2/OpenCLIP, with Claude Vision as the ambiguous-case adjudicator, is safer than installing any third-party MCP server found — explicitly stated as the recommendation.

**Part 2 — Same-Product Visual Identity Gate architecture (design only).** Full spec written into `ANALYZER_V3_SPEC.md`'s Layer 5 section as a new subsection, **SPEC ONLY — NOT IMPLEMENTED.** Summary:
- **Reference images:** one-time-per-product curated subset of the AliExpress gallery (Claude Vision tags each gallery image `CLEAN_PRODUCT_PHOTO`/`INFOGRAPHIC_OR_BANNER`/`PACKAGING`/`SIZE_CHART`/`LIFESTYLE_SCENE`; only the first and last feed the reference set), cached in `assets/{pid}/manifest.json` as a new `reference_role` field — not the main image alone, not the raw gallery unfiltered.
- **Competitor frames:** reuses the existing 10-timestamp extraction unchanged; scores every frame, aggregates by best-frame + corroboration count (≥2 independent frames above a secondary threshold), not a single peak and not a plain average — specifically to survive a late product reveal and to resist a single coincidental frame match.
- **Identity classes:** `SAME_PRODUCT` / `LIKELY_SAME_PRODUCT` / `AMBIGUOUS` / `SAME_CATEGORY_DIFFERENT_PRODUCT` / `UNRELATED` — critically, `SAME_CATEGORY_DIFFERENT_PRODUCT` can only be assigned by Claude Vision, never by embedding score alone, since that's the exact class the sealant-paste/mini-suitcase/seat-cushion/back-support-cushion false positives belong to.
- **Claude Vision adjudication** fires only on `LIKELY_SAME_PRODUCT`/`AMBIGUOUS` (not on deterministic `SAME_PRODUCT` or `UNRELATED`), is primed with the four known false-positive pairs as calibration, and fails closed to `SAME_CATEGORY_DIFFERENT_PRODUCT` on any error.
- **QA:** two independent, mandatory gates — `FRAME_IDENTITY_VERIFIED` (does this frame belong to this URL/creator — extends the existing frame-identity concern from session 18's Bug 4) and `PRODUCT_IDENTITY_VERIFIED` (does this frame show the same product) — a competitor is admitted to the benchmark statistics only if both are true; rejects stay in the evidence file with a reason, nothing is silently dropped.
- **Evidence schema:** new `product_identity` block per competitor (reference images used, frame scores, classification, confidence, Claude Vision decision if invoked, admit/reject reason) — additive, does not break the existing schema.
- **Security, if/when implemented:** DINOv2 via Hugging Face's verified `facebook` org, `.safetensors` weights only (never pickle/`.bin`), pinned package versions, hash-verified before install, isolated venv — **none of this has been done; explicit approval required before any `pip install` runs.**

**Committed to git this session:** nothing — no files in the repo were modified except the two documentation files updated by this same instruction (`PROJECT_STATUS.md`, `ANALYZER_V3_SPEC.md`). No code, no scripts, no dependencies.

### 2026-08-04 (session 19) — Fixed session 18's blob-fetch bug (canvas-capture rewrite); trial re-run started then intentionally stopped mid-run

**Scope, per session 18's pause plan: fix the blob-fetch bug first, then re-run 002/003/007.** Only the fix was completed this session; the live re-runs were started (product 002) and then deliberately stopped by user request before completion, to resume this evening.

**The fix (`scripts/layer5_competitor_benchmark.py`):** Session 18 confirmed `fetch(video.currentSrc)` throws `TypeError: Failed to fetch` on TikTok's competitor-page `<video>` blob: URL, and left it unresolved. Root cause, now identified: TikTok's `<video src>` is a `blob:` URL backed by a `MediaSource` object (used for adaptive/segmented streaming), not a plain `Blob` — `fetch()` on a MediaSource-backed blob: URL is a hard, unconditional browser restriction (only a `<video>` element can consume it), not a timing race, so no amount of extra waiting after `.play()` would have fixed it.

**Replaced the whole download-bytes-then-ffmpeg path with an in-page `<canvas>` capture:**
- `download_video_bytes()` removed entirely (the confirmed-broken blob-fetch code).
- New `wait_for_video_ready()` keeps the (already-confirmed-working) `.play()` + readyState-polling half of session 18's fix, but now returns `(is_ready, duration)` explicitly instead of overloading `None` for two different meanings ("never became ready" vs. "ready but no duration").
- New `capture_frame_canvas(page, t, out_path)` seeks the live `<video>` element to timestamp `t`, waits for the `seeked` event (with a 4s safety timeout), draws the current decoded frame onto an off-screen `<canvas>` via `drawImage()`, and writes the `canvas.toDataURL('image/png')` bytes straight to disk. This operates on the pixel buffer the browser has already decoded and is displaying, regardless of how the underlying bytes were sourced or whether they're independently fetchable — sidesteps the MediaSource restriction entirely rather than working around it.
- Added a seek-timeout guard: if the `seeked` event never fires within 4s (e.g. an unbuffered timestamp late in a long clip) AND `currentTime` didn't land within 0.35s of the requested `t`, the frame is rejected rather than captured — a timed-out seek leaving `currentTime` adrift is exactly the same failure shape as session 18's Bug 4 (capturing the wrong moment/video), so it gets the same "don't trust it" treatment rather than silently reusing whatever's on screen.
- `extract_competitor_frames()` simplified accordingly — no more temp video file, no ffmpeg `-ss`/`-frames:v` subprocess calls for extraction (ffmpeg is still used downstream, unchanged, for `compute_motion_metrics()`'s consecutive-frame SSIM on the saved PNGs).
- `source_video_path` in the output schema is now always `None` (there's no longer a downloaded source file) — confirmed no other script (`layer5_benchmark_qa.py`, `layer5_execution_diagnosis.py`) reads that field.

**Validation done this session:** `python -m py_compile` passes; `scripts/test_layer5_competitor_benchmark.py` — 21/21 unit tests pass unchanged (none of them exercised the removed/replaced browser-facing functions, all are pure-Python ranking/filtering logic). **Explicitly NOT done this session:** no live end-to-end validation against a real TikTok session. A trial run for product 002 was started specifically to get that validation, using:
```
python scripts/layer5_competitor_benchmark.py --product-id 002 --query "מחזיק טלפון מגנטי לרכב" --target 5 --relevance-keywords "מחזיק,טלפון,רכב,מגנט,phone,mount,car,magnet"
```
but was stopped by explicit user request (end-of-session, not a bug/CAPTCHA/failure) before it reached the frame-extraction step — **so the canvas-capture approach itself is still unproven against a live page as of this update.** This is the very first thing to do on resume.

**Also agreed with the user this session (not yet executed):** the exact `--query`/`--relevance-keywords`/`--exclude-keywords` to use for the 003 and 007 re-runs, recorded in the PAUSED banner above — 003 gets no exclude-keywords (no safe term found that wouldn't risk excluding real sealer competitors given "seal" is a substring of "sealant"), relying instead on the mandatory visual-frame check; 007 gets `--exclude-keywords "כרית,cushion"` to filter the known seat-cushion mismatch category directly.

**Committed to git this session:** nothing yet — the canvas-capture rewrite is uncommitted, per the PAUSED banner's step 8.

### 2026-08-03 (session 18) — Broadening the Layer 5 competitor benchmark to products 002/003/007: found and fixed 4 real bugs, none of the 3 products verified trustworthy yet

**Scope, as planned at session 17's pause:** broaden `scripts/layer5_competitor_benchmark.py` (bug-fixed session 17) from product 008 only to products 002, 003, and 007, using Hebrew search queries derived from each product's own real hook/caption text (`output/*-upload_package.md`): 002 = "מחזיק טלפון מגנטי לרכב" (magnetic car phone mount), 003 = "אוטם שקיות מיני" (mini bag sealer), 007 = "מארגן גב מושב לרכב" (car seat-back organizer). Session 17's committed fix (commit `26bc876`) was the starting point. What actually happened: four more real, previously-unknown bugs were found and fixed along the way — each one caught by direct evidence (a spot-check, a live DOM inspection, or literally opening the extracted frame images), not assumed — and by the end of the session none of the three products' benchmarks had survived a clean, fully-fixed run all the way through.

**Bug 1 — search-results like-count extraction was structurally unreliable, not just buggy for `--seed-urls`.** Product 003's first broadened run came back with **every single one of its 5 selected competitors showing 0 likes.** Investigated rather than accepted: live DOM inspection showed TikTok's search-result cards expose their one visible engagement number via `data-e2e="video-views"` (a misleadingly-named attribute — direct cross-check against two videos' own detail pages, `@bpatent` and `@max_stock_israel`, confirmed this number exactly equals the real like-count, not a view/play count), and that number renders asynchronously — the old heuristic's fixed sleep often read the DOM before it hydrated, defaulting to 0. Separately, the old heuristic's ancestor-walking bare-number-match could also pick up TikTok's own header inbox/notifications panel (its "X liked your video" entries also match a naive `a[href*="/video/"]` selector). **Fix:** rewrote `search_candidates()` to poll for hydration and read the DOM cleanly (labeled honestly as `view_count`, never trusted as the real metric on its own), added `merge_search_candidates()` for cross-query dedup, and a new `shortlist_by_real_likes()` that uses `view_count` only as a cheap pre-filter, then fetches each shortlisted candidate's REAL like_count from its own video page.

**Bug 2 — the per-video like-count fetch (`fetch_like_count_for_url`, used for both `--seed-urls` and the new shortlist step) had the identical hydration-race bug.** Product 007's first broadened run: 10 of 12 shortlisted candidates came back with an unusable 0/None like_count — including the two highest-viewed ones (47.1K and 24.8K views). Live DOM inspection confirmed the cause directly: the like-count element was still showing its static placeholder button label ("Like"), not a number, several seconds after navigation — TikTok's own real number hydrates later. **Fix:** rewrote to `fetch_like_count_and_caption_for_url()`, which polls up to ~8s for the element's text to become genuinely numeric before trusting it, and grabs the video's caption/title in the same page visit (needed for Bug 3's fix, at no extra navigation cost). Re-running product 007 afterward: both previously-broken top candidates now correctly show 47,100 and 24,800 real likes.

**Bug 3 — wrong-category competitors were passing straight through into the benchmark (the concern raised repeatedly during this session).** Confirmed by reading actual captions: product 003 pulled in a leak-sealant-paste video (`@popai283`) and a mini-suitcases video (`@uptrend.tt`) — unrelated to a bag sealer. Product 007 pulled in multiple seat-**cushion** videos (`@kk560977`, `@weraqq3`, `@malcolm.gregory6`, `@magpiefinds8`) that are a different product from a seat-**back organizer with a folding tray**, but share enough incidental keywords ("seat"/"car"/"back") to rank highly by engagement. **Fix:** added `passes_relevance_filter()` plus `--relevance-keywords`/`--exclude-keywords` CLI args, applied immediately after each candidate's caption is fetched and BEFORE any frame extraction runs — so a wrong-category video never burns a frame-extraction slot, addressing the "not wasting time/resources" requirement directly. Iterated twice more after the first attempt: an initial narrow keyword list (`מארגן`,`organizer`) wrongly excluded genuinely-relevant competitors worded differently (`storage`, `pocket` — e.g. "Automotive Seat Back Storage Bag", "Car Seat Back Multi-Pocket Storage"), and both that attempt and the broadened one were wrongly treating an uninformative caption (empty, or TikTok's own generic placeholder title "TikTok - Make Your Day") as a rejection. Fixed by adding `UNINFORMATIVE_CAPTIONS` handling: a candidate with no real caption to check is kept UNDECIDED (not excluded), deferring the actual call to visual frame review rather than a keyword match that has nothing to work with.

**Bug 4 — the most serious, and only caught by opening the actual frame images and looking, exactly as requested repeatedly during this session.** Even after Bugs 1–3 were fixed, direct visual inspection of product 007's 5 selected competitors' extracted frames (not just their captions) showed **2 of the 5 were frames from a completely unrelated video by a different creator** — one was a welding/aluminum-cutting tutorial (`@iding.welder786`, not the expected `@cicipetshop01.my`), the other a lunchbox-packing video (`@tyler.yan`, not the expected `@liu24140ujf`). This was not a search-relevance problem — it was a frame-*identity* problem: the wrong video's content was being screenshotted under the right competitor's label. Root cause, confirmed by live DOM inspection rather than assumed: a competitor's `<video>` element sits at `readyState: 0` (HAVE_NOTHING) for 4+ seconds after navigation — TikTok defers actually loading video data until playback is triggered — so the old code's `video.currentTime = t` assignment was a silent no-op on an unloaded element, and `video_el.screenshot()` simply captured whatever was already painted on screen, which in a browser page object reused sequentially across a dozen+ candidate navigations was sometimes the *previous* candidate's still-lingering frame. Verified the `.play()` half of the fix in isolation before touching the pipeline: explicitly calling `video.play()` (muted) reliably brought `readyState` from 0 to 4 (with a real, correct `duration`) within about half a second — this part works and is confirmed. **Attempted fix (largest rewrite this session, NOT YET WORKING end-to-end):** rewrote `extract_competitor_frames()` to trigger real playback, poll for `readyState >= 3`, then download the actual decoded video bytes via its blob URL (in-page `fetch()` + `arrayBuffer()`, base64-transferred to Python) and extract frames via ffmpeg directly from the downloaded file — the same file-based technique this project already uses for its own rendered videos in Layer 3, intended to eliminate the entire class of live-DOM timing risk rather than just patch around one symptom of it. **Confirmed broken in a live re-run:** product 007's re-run with this fix came back 0/5 — every single frame extraction failed. Isolated the exact failure point afterward: `readyState` does reach 4 correctly, but `fetch(video.currentSrc)` on the `blob:` URL throws `TypeError: Failed to fetch` (a browser-level restriction, not a timing issue — see the PAUSED banner above for two candidate fix directions). The `.play()`/readyState-polling half of this fix is sound and should be kept; the blob-download half needs a different technique before this is usable.

**New standalone QA script, `scripts/layer5_benchmark_qa.py`** — same PASS/WARN/FAIL convention as `tiktok_collect_qa.py`/`analyze_qa.py`, built specifically because this session's own manual spot-checking (exactly the checks below) is what caught Bugs 1–3 and shouldn't have to be reinvented by hand for every future product. 7 checks: (1) benchmark file exists & valid JSON, (2) schema/count consistency, (3) URL dedup, (4) like_count/like_count_unavailable flag consistency, (5) frame completeness (files actually exist on disk), (6) view/like divergence (informational — flags >3x gaps for a human look), (7) caption relevance (reads each competitor's now-stored `caption` field — instant, no browser needed unless `--fetch-captions` is passed for data collected before that field existed). Does not yet have an automated equivalent of Bug 4's frame-identity check (visual creator/content confirmation) — that remains a manual/agent step, deliberately, since it requires actually looking at the image.

**Current state per product — none are trustworthy yet, precisely why:**
- **003:** saved benchmark (5/5, `low_confidence: false`) predates Bug 3's fix (relevance filtering) and Bug 4's fix (frame-identity). `layer5_benchmark_qa.py`'s caption check already flags 2 of its 5 competitors (`@popai283` = sealant paste, `@uptrend.tt` = mini suitcases) as category mismatches that were never actually replaced. **Known to contain wrong-category competitors — needs a full re-run with all 4 fixes, then fresh visual verification.**
- **007:** re-run repeatedly today. The version saved just before Bug 4's fix has 5/5 selected via the (by-then-correct) relevance filter, but direct visual inspection confirmed 2 of those 5 have frames from entirely unrelated videos (Bug 4) — **that saved JSON is known-bad, do not use.** The subsequent re-run with the (currently broken) ffmpeg-extraction attempt finished with **0/5** — every extraction failed at the blob-download step (see PAUSED banner above); the file currently on disk for product 007 reflects this 0/5 result. **Needs the blob-fetch bug fixed first, then a clean re-run.**
- **002:** only re-run with Bugs 1+2's fixes (like/view mislabeling), **not yet** re-run with Bug 3's relevance filter or Bug 4's frame-identity fix. Its saved benchmark (4/5, `low_confidence: true`) has had zero visual frame verification and must be treated as unverified, not just "probably fine because the numbers look plausible."

None of the three products' `qualitative_review` fields (product-reveal timing, motion type, native-feel, etc.) have been touched — still all `null` — correctly, since that visual-judgment pass shouldn't start until the underlying frame data itself is confirmed trustworthy. `CREATIVE_GAP_ANALYSIS.md` and `learning_report.json` are both untouched today, per the standing rule from session 15/16.

**Explicitly not done:** Product 008's original benchmark (session 15) was never re-run with any of today's 4 fixes — it predates all of them, including the ffmpeg frame-identity fix, and should be treated as unverified by the same standard now being applied to 002/003/007, though re-checking it was not part of today's approved scope. All of `scripts/layer5_competitor_benchmark.py`'s changes today are covered by regression tests in `scripts/test_layer5_competitor_benchmark.py` (grew from 9 tests at session 17's end to 25 by end of today, all passing) — but the tests only cover the pure-Python logic (selection, filtering, merging); they cannot and do not substitute for the live visual frame verification described above.

### 2026-08-03 (session 17) — Fixed the `--seed-urls` `like_count: None` ranking bug in `scripts/layer5_competitor_benchmark.py`; regression tests added and passing

**Scope, per explicit instruction: this bug fix and its validation only.** Did not broaden the Layer 5 benchmark to products 002/003/007, did not touch `learning_report.json`, did not change the creative pipeline, did not start Product 009, did not implement Daily Incremental Production Mode.

**Root cause:** seed competitors passed via `--seed-urls` were appended with `like_count: None`, then ranked alongside search results using `c["like_count"] or 0` — coercing an unmeasured value into a real zero and losing to any search result with a positive like count once there were `target`-or-more of them. This is exactly what dropped `@yeuunnt.22` (78.3K likes) and `@goussve.km` from product 008's benchmark in session 15.

**Fix (`scripts/layer5_competitor_benchmark.py`):**
- New `fetch_like_count_for_url()` navigates to each seed URL and extracts its real `like_count` via `[data-e2e="like-count"]`, falling back to a DOM-text heuristic; returns `None` (not 0) if genuinely unavailable.
- New `select_top_candidates()` replaces the old inline dedup/sort: search-discovered candidates still rank by `like_count` descending; seed candidates are now **always included** regardless of `like_count` or whether it could be measured, filling the Top-N first, with search results filling any remaining slots up to `target` (seeds beyond `target` are kept, not truncated).
- Dedup across sources now prefers a known `like_count` over an unavailable one, and the higher of two known values, while still preserving the seed inclusion-guarantee.
- Per-competitor benchmark JSON now records `like_count_unavailable` (bool) and `source` (`seed`/`search`) so a genuinely-unmeasured value is visible and excludable from numeric averages downstream, per the spec's existing Confidence Rules — never silently hidden or treated as data.

**Validation:** new `scripts/test_layer5_competitor_benchmark.py` (9 unit tests, pure Python `unittest`, no Playwright/network) — all pass, including a direct regression test reproducing the session-15 incident (`@yeuunnt.22` + `@goussve.km` as seeds with unmeasured like counts, competing against 6 real search results, target=5 → both seeds survive selection). `python -m py_compile` confirms the edited script is syntactically valid. Not yet re-run against a live TikTok session — that will happen naturally when the Layer 5 benchmark is broadened to products 002/003/007, the next approved step, still pending separate go-ahead.

### 2026-08-03 (session 16) — Premise correction on Analyzer v3 completeness; Daily Incremental Learning Mode approved as a permanent architectural requirement (not implemented); next technical direction confirmed

**Premise correction, recorded explicitly per instruction:** Analyzer v3 is NOT complete. Layers 3 (Hook Diagnosis) and 7 (Pacing/Retention) are done, run across all 16/16 CONFIRMED variants. Layer 5 (Video/Creative Execution + competitor benchmark) is only partially covered — implemented and run on 008B / product 008 only (4 of 5 target competitors). Layers 1, 2, 4, 6, 8, 9, and 10 remain spec-only. The Analyzer v3 QA suite and the Final Recommendation Engine (`ANALYZER_V3_SPEC.md` → "Final Recommendation Engine") have not been built either. This corrects any prior framing that implied the diagnostic system as a whole was further along than this.

**New permanent architectural requirement approved: Daily Incremental Learning Mode.** The platform must support two distinct operating modes — Historical Backfill Mode (development / explicitly forced rebuild) and Daily Incremental Production Mode (the default once historical development is complete: 7-day rolling window by default, no re-collection/re-diagnosis of already-validated videos, idempotent upserts with no duplicate rows, no overwriting validated values without a documented refresh policy or explicit force option, per-video collection/validation/diagnosis/refresh status tracking, skip unnecessary browser work when nothing is eligible, continuous learning from newly validated videos, and preservation of prior diagnosis evidence/versions when diagnostic logic changes). Full requirement text recorded in `TIKTOK_AGENT_PLAN.md` → "Operating Modes — Permanent Production Requirement," with a cross-reference in `ANALYZER_V3_SPEC.md`. **This is a documentation-only, architecture-level decision — explicitly approved, explicitly NOT implemented. No script or workflow was modified in this session.**

**Next approved technical direction (not yet started), in order:** (1) fix the known `--seed-urls` `like_count: None` ranking bug in `scripts/layer5_competitor_benchmark.py` (identified session 15) — `None` currently sorts as 0 and can wrongly exclude known-good competitors from the Top-N; (2) broaden the Layer 5 competitor benchmark to products 002, 003, and 007; (3) review that expanded evidence before updating `learning_report.json` or changing the creative pipeline. Product 008's catalog-feel finding is not to be generalized to the rest of the portfolio, and Product 009 is not to be generated, before that review.

### 2026-07-02 (session 15) — Layer 3 completed on all 16 variants; Layer 5 competitor benchmark escalated to a statistical, multi-competitor architecture with manual-CAPTCHA support; cross-layer synthesis written

**Layer 3 (Hook Diagnosis) run to completion across all 16/16 CONFIRMED variants** (previously validated on 008B only, session 10). Headline cross-variant finding: cause (a) "weak/static opening visual" and cause (c) "AliExpress catalog feel" were both rated **LIKELY in 16 of 16 variants** — the single most universal result of this entire diagnostic pass. For products 002/003/007 (12 of the 16 variants), this is not just catalog *styling* — Layer 3 found literal scraped AliExpress/marketplace screenshots (visible page chrome: "אבטחה ופרטיות", "החזרות חינם", delivery dates, discount banners) appearing *inside the measured 2–3s hook window itself*. Cause (b) "unclear product" was UNLIKELY in all 16 — product legibility is a genuine strength, not a gap. Cause (e) "hook–product mismatch" recurred in 7 of 16 variants, specifically whenever hook copy promised a before/after, reveal, or transformation that the static opening frame never delivers (003A/C/D, 007C, 008B/C/D).

STEP 11D pre-launch QA (only exists for product 008) was shown to be unreliable in this pass, not just incomplete: 008B and 008D show **confirmed divergence** — STEP 11D scored PASS 9/10 citing "motion lines"/"rotation animation cohesive throughout," but fresh sub-second frame extraction shows zero motion in either variant's hook window; the credited animation was a static compositing graphic. 008C shows a **divergence of omission** — STEP 11D flagged a minor cosmetic CTA text-color bug (score 8/10, "conversion impact minor") while missing the more consequential hook-visual/text mismatch Layer 3 found (cause e, LIKELY). Only 008A shows genuine agreement between STEP 11D's pre-launch call and the frame evidence.

**Layer 5's competitor benchmark was escalated twice more during this session, per explicit instruction, beyond session 13/14's single-competitor comparison:** first to a "Top 5–10 competitors, statistics not one-to-one comparison" requirement, then to a full architecture requiring market-source tracking, exclusion filtering (drop entertainment/meme/wrong-category videos), an expanded metric list, and category-level statistics (mean/median/range/percentile) rather than pairwise claims. `scripts/layer5_competitor_benchmark.py` rebuilt accordingly, including `wait_for_manual_captcha_solve()` — detects TikTok's CAPTCHA markers, screenshots, and polls for the marker to disappear, **never attempts to solve it**, per explicit instruction. This function is now called both at page load and before every single frame capture, a discipline learned the hard way after session 14's popup-contamination incident.

**Product 008 benchmark result: 4 of 5 target competitors, confidence MODERATE.** Excluded 1 wrong-category candidate (a bendable phone-grip accessory surfaced by search-term overlap, not a rotating stand) and lost 1 previously-valid competitor (@goussve.km, 58 likes) to an operator mistake — a blanket cleanup command aimed at a different CAPTCHA-contaminated batch reused the same generic filenames and deleted its frames. **Disclosed directly in `product008_layer5_competitor_benchmark.json` rather than silently omitted or re-collected to hide the gap.** Statistics across the 4 valid competitors: motion-magnitude SSIM mean=0.5155, median=0.496, range=[0.4609, 0.6087] — our own 008B value (0.927) sits at the **0th percentile**, outside the competitor range entirely, below every single one of them. All 4 competitors show organic motion, real human presence, real product-in-use, and native TikTok feel; 008B shows none of the four.

**Market-composition finding, not previously expected:** despite every search query being run in Hebrew, none of the 4 valid competitors are confirmed Israeli/Hebrew-market (3 English captions, 1 Spanish). Labeled explicitly as an expanded/global-market benchmark rather than an Israeli-market one, per the spec's own Israeli Market Context expansion clause ("if insufficient in-market data exists, expand gradually while recording the market source") — a methodology-consistent outcome, not a failure, but one that must be stated plainly rather than assumed away.

**Known bug identified, not yet fixed:** seed URLs passed via `--seed-urls` are recorded with `like_count: None`, which sorts as 0 in the Top-N ranking and can push known-good competitors out of the selection entirely — this is what caused `@yeuunnt.22` (78.3K likes) and `@goussve.km` to be dropped from the latest automated search round before being manually re-added. Left unfixed pending explicit approval to touch the script again.

**This session's follow-up work (after the above):** found and fixed a stray trailing `}` in `008B_layer5_evidence.json` that made the file invalid JSON (confirmed via `json.load` before and after). Wrote `CREATIVE_GAP_ANALYSIS.md` — a structured, evidence-graded synthesis answering "what do successful competitor videos consistently do that our videos consistently do not," ranked by evidence strength and explicit about which claims are 16/16-variant fact (Layer 3) versus which are measured on 1 of 4 products only (the Layer 5 competitor benchmark) so the product-008-specific findings aren't silently generalized to 002/003/007. Explicitly does not propose pipeline changes yet and does not touch `learning_report.json` — held for review per standing instruction.

### 2026-07-02 (session 14) — Layer 5 follow-up: motion magnitude measured directly against the competitor, not just described

Explicit follow-up requested before generalizing session 13's finding: session 13's competitor comparison only showed a single static opening-frame screenshot — no actual motion measurement, so "insufficient motion" vs. "something else about the opening" couldn't yet be distinguished with evidence. Redid it properly: extracted a comparable frame sequence (0.1/0.5/1.0/1.5/2.0/2.5s) from the competitor video and ran the exact same SSIM methodology used on 008B's own segments.

**Caught and corrected a real methodology error before reporting anything, not after:** the first attempt produced a misleading signal (flat SSIM ~0.22-0.24, which read like continuous erratic motion) that turned out to be a **TikTok "Create a passkey" login-security popup** that had appeared over the video between the t=0.1s and t=0.5s captures and stayed there through t=2.5s — every frame after the first was measuring a static UI dialog, not the video. Caught by visually inspecting the actual frames before trusting the numbers (same discipline as every other measurement this session), redone with popup-dismissal logic checked before every single capture, and re-verified visually clean before recomputing.

**Clean result:** 008B's own consecutive-frame SSIM is remarkably flat at ~0.927 every 0.5s (mathematically expected — a linear Ken Burns pan has constant velocity, so constant similarity-delta). The competitor's clean, corrected consecutive-frame SSIM is also flat, but at ~0.46 every 0.5s — ruling out "one early hard cut" as the explanation (that would show one big drop then near-1.0 stability, not a sustained flat-low pattern) and confirming genuine, sustained, continuous visual change through the whole measured window, corroborated by direct visual inspection (framing genuinely shifts — tighter on the blanket, different composition — from 0.1s to 2.5s, consistent with real handheld camera movement plus real subject/child movement).

**Direct answer to "is it truly insufficient motion, or something else":** insufficient motion magnitude is now a real, measured factor — the competitor's sustained frame-to-frame change rate is roughly double ours (SSIM ~0.46 vs ~0.927 per 0.5s; lower SSIM = more change). This is not a false lead. But magnitude is very unlikely to be the whole story: the TYPE of motion also differs — ours is a smooth, deterministic, single-static-photo crop-pan with no discrete moments; theirs is real, organic camera-and-subject movement. Recorded as "both magnitude and type matter" rather than picking one from a single data point. Full numbers in `data/tiktok-analytics/product008/008B_layer5_evidence.json`'s `competitor_comparison.motion_magnitude_comparison` field, including the methodology-correction note.

**Still holding:** only 008B has this comparison. `learning_report.json` and the saved analysis file remain untouched, per instruction, until Layers 7/3/5 are reviewed together as a complete diagnosis.

### 2026-07-02 (session 13) — Layer 5 (Video/Creative Execution) implemented and validated on 008B

Approved scope: Layer 5 only, per explicit instruction, with three specific asks: (1) inspect the MP4/storyboard/video-config, (2) compare against real Israeli competitors, (3) distinguish planning/execution/editing/pacing/reveal-timing/first-frame-quality/movement/text-timing/overall-quality. Only after Layers 7, 3, and 5 are all done should `learning_report.json` be touched — explicitly not done yet.

**`scripts/layer5_execution_diagnosis.py` built with a genuinely new capability this project didn't have before: real pixel-difference measurement (SSIM via ffmpeg's own filter) instead of visual "look and compare."** The Ken Burns motion table is parsed directly out of `generate_videos.py`'s source text via `ast.literal_eval` (not hand-copied, not imported — that module needs numpy/PIL/moviepy, none of which are installed in this environment, a second dependency gap beyond the ffmpeg one already fixed, flagged but not fixed since out of scope here).

**Real correction to Layer 3, confirmed with rigor, not asserted:** Layer 3's agents visually compared 008B's opening frames and called them "pixel-identical," rating cause (a) "no motion cue" LIKELY. Measuring the SAME frames with ffmpeg's SSIM filter instead of eyes shows a clean, monotonically decreasing trend relative to 0s (0.927 @0.5s → 0.843 @2.5s) — exactly the signature of a real, continuous pan, matching `generate_videos.py`'s own Ken Burns table for variant B segment 0 (`pan_left, -30px over 3s`). **Every one of 008B's 5 segments shows this same confirmed real-motion signature** — Ken Burns is executing correctly throughout the entire video, not just segment 0. The eye test missed real (but subtle) motion a pixel diff caught.

**This does not mean the opening is fine — it changes WHICH problem it is.** 30px of pan over 3s on a 1080px canvas (~2.8% of frame width, ~0px displacement at t=0, only ~10px by t=1s) is real motion that is plausibly too subtle to register as a scroll-stopping visual cue in the exact window (0-2s) where Layer 7 shows the steepest drop. Diagnosis reclassified from an **EXECUTION failure** (motion wasn't rendered) to a **PLANNING/CALIBRATION question** (motion was rendered exactly as planned; the planned magnitude may be inadequate for its purpose).

**Precise correlation finding, not previously available:** Layer 7's cached retention curve shows the single steepest per-second drop (32%) happens at second 2 — solidly mid-segment-0, not at the segment 0→1 cut (3s, only a 14% drop). This argues against "abrupt transitions" as the driver (`EDITING` dimension: clean, by-design hard cuts, not implicated) and points squarely at segment 0's own content/motion-magnitude (`PACING`/`PLANNING` dimensions) as where the real problem lives.

**Per-dimension findings for 008B** (full detail in `data/tiktok-analytics/product008/008B_layer5_evidence.json`): `PLANNING` — mostly reasonable, one calibration issue (segment 0's pan too subtle for its purpose). `EXECUTION` — confirmed correct in all 5 segments via SSIM, not an execution bug. `EDITING` — clean cuts, not implicated by the retention data. `PACING` — segment 0's motion magnitude is the actionable lever, not segment length. `Product reveal timing` — stand is visible from frame 0 but partially obscured; a clean unobstructed shot only arrives at 3s. `First-frame quality` — technically competent (sharp, well-lit, correct resolution) — the issue is style/content (Layer 3's catalog-feel finding), not technical execution. `Text timing` — confirmed correct at the one boundary directly checked, matches config exactly. `Overall creative quality` — competently executed against its own plan; the plan's two core creative choices (asset style, motion magnitude) are what limit it, not the execution of that plan.

**Competitor comparison (explicitly best-effort, not full Layer 10):** searched TikTok for the Hebrew term "מעמד לטאבלט מסתובב" (rotating tablet stand). Anonymous search triggered a CAPTCHA — abandoned rather than solved (would be circumventing anti-bot protection); retried successfully using the account's own existing authenticated session, which was not challenged. **The top-performing real result (78.3K likes, 12.6K saves, 17.1K shares — vastly beyond anything in this account) opens on a real child lying in bed under a blanket, with the device mounted overhead** — genuine, low-fi, human-context footage, not a studio product render. This is one real data point directly corroborating Layer 3's cause (c) finding, not a comprehensive benchmark (Layer 10's job, not yet built). Frame saved to `data/tiktok-analytics/product008/layer5_frames/competitor_top_opening.png`.

**Explicitly not done yet:** only 008B has Layer 5 evidence. Not run across the other 15 variants — holding for explicit approval. `learning_report.json` and the saved analysis file remain untouched, per instruction, until Layers 7/3/5 are reviewed together as a complete diagnosis.

Session 10 (below) flagged that ffmpeg was unavailable in this session's environment and fell back to reusing 008B's pre-existing integer-second QA frames (0/1/3s). Before running Layer 3 on more variants, per instruction, the gap itself was fixed rather than left as a standing workaround.

**Root cause investigated, not just patched:** confirmed via direct checks (not assumed) that this Python 3.12 environment (`C:\Users\LilachMor\AppData\Local\Programs\Python\Python312\`) has only `playwright` installed — `moviepy`, `requests`, and ffmpeg are all absent, and there is no project-local venv. This means the video-generation half of the pipeline (`generate_assets.py`/`generate_videos.py`) would fail today too, not just Layer 3's frame extraction — flagged for awareness, not fixed (out of scope for this instruction, which was specifically about the ffmpeg gap).

**Fix:** installed ffmpeg via `winget install Gyan.FFmpeg` (succeeded, version 8.1.2). Discovered this session's shell processes hold a stale environment snapshot from before the install — neither a fresh Bash nor a fresh PowerShell call picked up the PATH change winget made, even though winget itself reported success. Rather than rely on a full host-process restart (outside of what I can trigger), copied `ffmpeg.exe`/`ffprobe.exe` directly into the Python directory already confirmed on this session's PATH. Verified working from all three angles that matter: bare `ffmpeg`/`ffprobe` in Bash, in PowerShell, and via Python's own `shutil.which()` (what `layer3_hook_diagnosis.py` actually checks).

**Re-ran Layer 3 on 008B — this time `frame_source: ffmpeg_fresh_subsecond`, not the fallback.** Extracted real frames at 0/0.5/1/1.5/2/2.5/3s directly from the rendered MP4. Result: **the "no motion" finding is confirmed, not just an artifact of the earlier coarse 1-second fallback** — all five frames from 0s through 2s are pixel-identical. This also strengthens the STEP 11D-divergence finding: it rules out "STEP 11D just sampled too coarsely to catch a quick sub-second animation" as an innocent explanation, since there is no animation anywhere in that window to catch at any sampling rate. `data/tiktok-analytics/product008/008B_layer3_evidence.json` updated with the confirmed ratings.

**Next action:** Layer 3 is now ready to run across the remaining 15 variants with genuine fresh extraction (no more fallback-frame caveat). Not yet done — holding for explicit approval, same pattern as every other collector/analyzer-touching step this session.

### 2026-07-02 (session 10) — Layer 3 (Hook Diagnosis) implemented and validated on 008B

Approved scope: Layer 3 only, per explicit instruction ("Implement Layer 3 first").

**Architecture note, deliberately different from Layer 7:** Layer 3's core question (which of causes a/b/c/d/e/h is responsible) requires actually looking at frames and reading hook text — not something to fake with a rule-based heuristic. `scripts/layer3_hook_diagnosis.py` does only the mechanical half (reads `first_2_second_retention` and classifies it, reads the hook segment from `data/{pid}-video-config.json`, parses the upload package for the STEP 11D pre-launch score/verdict, extracts opening frames) and leaves the actual visual/textual judgment to the agent — the same division of labor this project's own pipeline already uses for STEP 11B/11C/11D (ffmpeg extracts, Claude reads and scores).

**Real environment gap hit and worked around, not hidden:** ffmpeg is not available in this session's environment (`shutil.which("ffmpeg")` returns `None`) — confirmed via a direct search, not assumed. Fresh sub-second frame extraction (0/0.5/1/1.5/2/2.5/3s, per spec) isn't currently possible. Fallback: the script reuses this product's own pre-launch STEP 11B/11D QA frames already on disk (`scripts/qa_008_B_0s.png`, `_1s.png`, `_3s.png`) — integer-second granularity only, explicitly logged as a fallback rather than silently presented as equivalent to fresh extraction.

**Result on 008B — a real, confirmed divergence, not just a rating exercise:**
- `first_2_second_retention` = 42% (MARGINAL).
- STEP 11D's pre-launch prediction: **PASS 9/10**, explicitly citing *"strongest hook (curiosity + motion lines), vivid WOW MOMENT"* — this was the single highest-scored hook across all of Product 008's variants.
- Direct frame comparison (0s vs 1s, both pulled from the actual rendered MP4): **the two frames are visually identical.** The "motion" STEP 11D credited is a static light-ray graphic baked into a single still AliExpress-style product photo — there is no real movement in that interval at all.
- Cause ratings: **(a) Weak opening visual/no motion cue — LIKELY** (confirmed by the identical-frames comparison); **(c) AliExpress catalog feel — LIKELY** (glossy CGI-style render, no organic/handheld quality); **(e) Hook–product mismatch — POSSIBLE** (hook text promises "transformed my desk," image shows no visible transformation/demo); **(b) unclear product, (d) generic hook text, (h) non-native Hebrew — all UNLIKELY**, each with cited evidence in `data/tiktok-analytics/product008/008B_layer3_evidence.json`.

**This is exactly the STEP 11D-divergence check the spec calls for, and it found a real one:** the pre-launch visual QA's 1-second-interval frame sampling appears to have mistaken a static compositing effect for actual motion when scoring "motion lines" as a strength. Worth checking whether other products' STEP 11D "PASS ... motion" citations have the same issue — not yet checked beyond 008B.

**Explicitly not done yet:** only 008B has been diagnosed. The ffmpeg gap should be fixed (or an explicit alternative decided) before running Layer 3 across more variants, since the fallback frames are only available where a variant happened to go through the original STEP 11B/11D QA with frames still on disk — that won't hold for every future variant.

### 2026-07-02 (session 9) — Layer 7 corrected: `HOOK_PROBLEM` → `OPENING_SEQUENCE_PROBLEM`, after a real methodology challenge

Session 8 (below) ran Layer 7 across all 16 variants and reported the result using the classification name `HOOK_PROBLEM`. Before that result was used to update `learning_report.json` or replace session 5's recommendation, the classification's own validity was challenged: **Layer 7's only input is the retention curve — WHEN viewers stop watching. It has never looked at a single video frame.** Naming a category "HOOK_PROBLEM" claimed a specific creative cause (the hook concept/wording) that Layer 7 has no evidence for. Hook concept, product-reveal timing, first-frame visual quality, movement, editing, and text overlays all live inside the same opening seconds, and distinguishing between them requires Layer 3 (Hook Diagnosis) and Layer 5 (Video/Creative Execution) to actually inspect the frames — neither is implemented.

**Fix, in both `scripts/layer7_pacing_diagnosis.py` and `ANALYZER_V3_SPEC.md`:** the classification is renamed `OPENING_SEQUENCE_PROBLEM` (a temporal finding: most loss is concentrated in the opening window) — no longer a causal claim about which component failed. Internal field names renamed to match (`hook_share_of_total_drop` → `opening_window_share_of_total_drop`, etc.). Every `OPENING_SEQUENCE_PROBLEM`/`ENDING_PROBLEM` result now carries an explicit `cause_unresolved_note` in its own output — e.g. *"WHICH component is responsible... is not determined by this layer. Requires Layer 3 and Layer 5."* — so the tool itself cannot present a temporal finding as a finished diagnosis, not just documentation saying so on the side. `ENDING_PROBLEM` was left named as-is (a location descriptor, not a specific creative device the way "hook" names one) but also got a `cause_unresolved_note`, for the same reason.

**Re-ran across all 16 variants using the already-cached curve data (no new live session needed — this only changes classification labels, not extracted data).** Result, with corrected terminology: **13 of 13 statistically meaningful variants (n≥91 views) classified `OPENING_SEQUENCE_PROBLEM`** — 65–86% of total viewer loss concentrated in the first 3 seconds, on every product, regardless of hook type. 003C (1 view) is the sole exception, already flagged `LOW_CONFIDENCE`. This is the same underlying finding as session 8 — most loss really is concentrated early — but now correctly scoped as "loss happens early, cause unknown" rather than "the hook is broken."

**Session 5's Product 009 pacing recommendation ("shorten the mid-video 5–13s segments") is still very likely misdirected** — the evidence clearly says the drop is concentrated in the opening 3 seconds, not the middle — but the *specific* fix (rewrite the hook text? change the first frame? tighten the opening edit?) cannot be determined until Layer 3 and/or Layer 5 exist. **`learning_report.json` and the saved analysis file have deliberately NOT been updated** — holding for explicit direction now that this methodology question is resolved.

**Next action:** decide whether to (a) update `learning_report.json`'s `pacing_adjustment` with the correctly-scoped opening-sequence finding now, flagged as cause-unresolved, or (b) implement Layer 3 and/or Layer 5 first so the next update can name an actual fix rather than just a temporal location.

### 2026-07-02 (session 8) — Layer 7 (Pacing/Retention Diagnosis) implemented and validated on 008B

Approved scope: Layer 7 only, per explicit instruction ("start implementing Layer 7 first") — Layers 1–6/8–10 remain spec-only in `ANALYZER_V3_SPEC.md`.

**New collector capability, in `scripts/tiktok_analytics_collect.py`:** the retention-hover technique that already extracts `first_2_second_retention` (validated 2026-07-02 session 1/2) has been generalized to sample the *entire* retention curve, one point per second, not just t=2s. Refactored the original monolithic function into three pieces — `_detect_video_duration()`, `_hover_retention_at_second()` (shared low-level hover+nudge, generalized from "lock onto t=2" to "lock onto any target second"), and two callers: `_extract_first_2_second_retention()` (unchanged behavior, regression-tested against the known 008B baseline — identical output, zero regression) and the new `_extract_full_retention_curve()`. Live-tested on 008B: full 15-point curve extracted in 13 seconds.

**New standalone script `scripts/layer7_pacing_diagnosis.py`** (does not touch `video_results.csv` or the collector's own `collect_one_variant()` flow — a diagnostic tool, same pattern as `tiktok_collect_qa.py`/`analyze_qa.py` standing apart from what they check). Classifies each variant into one of four problem types per `ANALYZER_V3_SPEC.md`: `HOOK_PROBLEM` (most of the total drop happens by the hook window, default first 3s — matches the existing STEP 11B/3A 0/1/3s frame-sampling convention), `ENDING_PROBLEM` (disproportionate drop only in the last 3s), `VIDEO_LENGTH_PROBLEM` (retention plateaus at a real value at/before where the storyboard's own content ends, per `data/{pid}-video-config.json` segment timings — cross-referenced, not inferred from the curve alone), or `MID_VIDEO_PACING_PROBLEM` (the default). Curves are cached to `data/tiktok-analytics/product{pid}/{cta_code}_retention_curve.json` — the live extraction only needs to run once per variant; re-runs reuse the cache (confirmed: a cache-only run skips launching a browser entirely).

**Caught and fixed a real bug during this session's own testing:** JSON round-trips integer dict keys as strings, so a cached curve's `curve` dict has string second-keys while a fresh live extraction has int keys — `classify_curve()` crashed with a `TypeError` comparing `str` to `int` the first time a cached curve was loaded (never hit during the initial live run, which is exactly why it slipped through the first pass). Fixed by normalizing keys to `int` on load.

**First real result — and it already refines the earlier hand-written analysis, not just confirms it:** 008B's full curve is `100,74,42,28,20,14,12,10,9,8,7,4,4,4,4,4` (seconds 0–15). 75% of the *entire* viewer loss for this video happens by second 3 alone. **Classification: `HOOK_PROBLEM`.** This is a genuinely different verdict than session 5's aggregate-based analysis, which — working from only `first_2_second_retention=42%` (MARGINAL, not CRITICAL) and `average_watch_time` — concluded the hook was *not* the primary issue and pointed at generic mid-video pacing instead. The full curve shows the drop is real and concentrated right at the hook/opening-content boundary (seconds 1–3), which the two-number aggregate view was structurally unable to see. **This is exactly the refinement Layer 7 was specified to deliver — the session 5 analysis's pacing conclusion should be treated as provisional until Layer 7 has been run across more than one variant.**

**Explicitly not done yet:** only 008B has been diagnosed. Have not run this across the other 15 variants — that's a live-session cost of roughly 13s × 15 ≈ 3–4 more minutes plus the extraction overhead already proven per-variant, and re-opens the real TikTok session repeatedly again, so it's being held for explicit approval before running broadly, consistent with how every other collector-touching step this project has been gated this session.

### 2026-07-02 (session 7) — Wrote `ANALYZER_V3_SPEC.md` — full 10-layer diagnostic architecture (SPEC ONLY, NOT IMPLEMENTED)

The current analyzer (C.A–C.J) answers "which variant performed best." Analyzer v3 is specified to answer *why* — a 10-layer diagnostic system: (1) Product Demand, (2) Offer/Deal Strength, (3) Hook Diagnosis, (4) Creative Asset Quality, (5) Video/Creative Execution, (6) Marketing Angle, (7) Pacing/Retention Diagnosis (extends the current C.F), (8) CTA/Buyer Intent, (9) Click Intent/Link Funnel, (10) Competition/Market Benchmark (mandatory — has cross-layer authority to override Layers 1/5/6's verdicts when competitor data shows the product itself isn't the problem).

Each layer's spec defines: core question, data needed, exact files/pages/assets to inspect (grounded in this project's real file structure — `output/*.md`, `data/*-video-config.json`, `assets/*/manifest.json`, TikTok Studio pages — not abstract), metrics/qualitative signals, named failure modes, required output, and how the diagnosis changes the next concrete action.

**Explicitly made Israel-specific per instruction, not left generic:** added a mandatory "Israeli Market Context" cross-cutting section plus pointer notes inside Layers 1/2/3/6/8/10 — Hebrew hook/CTA/angle text judged as native spoken Hebrew (not translated-ad phrasing, extending the existing HEBREW TEXT QUALITY rule into a diagnostic check), ₪ price bands judged against category-specific Israeli buyer expectations, Layer 6's angle taxonomy filtered through Israeli cultural register rather than assumed to transfer from global affiliate marketing, and — most structurally — **Layer 10's competitor set must be TikTok Israel / Hebrew-language creators specifically, not global TikTok**, since a competitor thriving on US TikTok is weak evidence for what works here.

**Also specified, permanently, cross-platform:** a Confidence Rules block (extends the small-sample handling already done ad hoc for 003C/003D/008A/008D — a `MIN_CONFIDENT_VIEWS` threshold, mandatory `n=` display next to every rate, no average silently dominated by one low-sample point) and an Evidence Requirement (every conclusion must cite a specific metric, file/frame, or competitor comparison — no unsupported assumptions).

**Named gaps the spec itself surfaces, not yet actioned:** `cta_code_comments` still never collected (blocks Layer 8, and by extension Layer 9 — standing #1 priority, already known from session 5); no affiliate click/sale tracking wired into any script (Layer 9 needs a new external data source); no competitor-video inspection tooling exists yet (Layer 10 needs new collection work, though it can reuse the existing STEP 11B/11D frame-extraction technique); the retention curve is only ever sampled at t=2s today (Layer 7's full hook/mid/ending/length classification needs the collector's existing hover-read technique generalized across the whole curve — a mechanical extension of `_extract_first_2_second_retention()`, not new invention).

**Next action:** review and approve (or revise) `ANALYZER_V3_SPEC.md` before any implementation begins. Do not generate Product 009 in the meantime unless separately approved — this session's work was architecture only.

### 2026-07-02 (session 6) — Built `scripts/analyze_qa.py`, a permanent Analyze QA suite

"Analyze QA" existed only as a milestone *name* in this file's stated PM order (Collector Enhancement → Collector QA → re-run Analyze → **Analyze QA** → Analyzer v3) — it was never actually specified or built, unlike Collector QA (`tiktok_collect_qa.py`, which already existed). Rather than invent a check with no basis, this formalizes the ad-hoc independent verification done by hand immediately after session 5's `/tiktok analyze` run (recomputing winners/averages/confidence-score inputs/decision logic straight from `video_results.csv` and diffing them against what the analysis actually produced) into a standalone, reusable script — same conventions as `tiktok_collect_qa.py` (PASS/WARN/FAIL, `--product-id` scoping, same summary/exit-code pattern).

**6 checks:**
1. Learning Report Exists & Valid — `data/learning_report.json` present, parses as JSON
2. Learning Report Schema — validates the decision-dependent field rules straight from `tiktok-analyze.md`'s own STEP F spec (e.g. `decision=PROCEED` requires `product_009_brief` fully filled and `pause_reason`/`change_strategy_issue` both null; `hook_type_wins` must have all 4 hook types as ints, never null)
3. Winner Consistency — recomputes `hook_type_wins` directly from the CSV (same win-by-highest-views logic used throughout `tiktok-analyze.md`) and diffs it against `learning_report.json`
4. Retention Consistency — recomputes the average `first_2_second_retention` across CONFIRMED rows and diffs it against `learning_report.json`'s `retention_avg_2s`
5. Decision Logic Consistency — checks the stated PROCEED/PAUSE/CHANGE STRATEGY decision isn't contradicted by facts directly computable from the CSV (e.g. PROCEED with fewer than 2 CONFIRMED rows would FAIL) — does not re-run the full C.G/C.H-dependent decision tree, which this script can't see
6. Analysis File Present — confirms an `analysis/*-analysis.md` file exists and isn't older than the newest CONFIRMED upload

**Validated two ways before trusting it:**
- Ran it against today's real session-5 output, scoped to `--product-id 002,003,007,008`: **6/6 PASS — ANALYZE APPROVED.** It also correctly surfaced an informational note (not a failure) that `best_hook_type=Curiosity` differs from the raw win-count leader (Problem/Solution) — expected and correct, since that's exactly the small-sample-outlier-exclusion reasoning from session 5's analysis, not an error.
- Deliberately broke 5 things with synthetic data (schema violation, a `null` inside `hook_type_wins`, a wrong win tally, a wrong retention average, a `PROCEED` with only 1 CONFIRMED row) and confirmed all 5 correctly came back FAIL — the checks discriminate real problems rather than rubber-stamping.

**Next action:** run `scripts/analyze_qa.py` after every future `/tiktok analyze` run, before treating its PROCEED/PAUSE/CHANGE STRATEGY decision as final.

### 2026-07-02 (session 5) — `/tiktok analyze` run: first analysis backed by complete data

Ran the full Performance Analysis + Quality & Learning pipeline (`.claude/commands/tiktok-analyze.md`) against all 16 CONFIRMED rows across products 002/003/007/008. This is the first time this pipeline has ever run with `saves`/`shares`/`average_watch_time`/`watched_full_video_rate`/`first_2_second_retention` actually populated — every previous analysis, including 2026-07-01's, was working from a dataset with those 5 columns blank (see the 2026-07-01 section below, which explicitly says its own recommendations should not be treated as final).

**Per-product winners (computed from performance data, not read from the CSV's `winner` column — that column is blank on all 16 rows; the v2 collector flow's STEP A intentionally skips writing back to existing rows, and no separate backfill of it was requested this session):**
- 002 (Car Phone Mount, ₪23): **002C** (Problem/Solution) — 390 views, highest in the account
- 003 (Mini Bag Sealer, ₪8): **003B** (Curiosity) — 360 views
- 007 (Seat-Back Organizer, ₪39): **007D** (TikTok Discovery) — 145 views
- 008 (Phone/Tablet Stand, ₪40.29): **008C** (Problem/Solution) — 133 views

These 4 winners exactly match the ones already on record in this file's 2026-07-01 section (002C/003B/007D/008C) — a useful cross-check that the underlying win-determination logic is consistent even though the CSV's `winner` column itself was never touched.

**Product status (account avg 165.25 views / 0 saves across all 16 rows):** 002 = **WINNING** (+83.2% vs account avg — the clear account leader), 003 = TESTING (+8.6%, not clearly above the 20% WINNING bar), 007 = TESTING (−30.1%), 008 = **RETIRED** (−61.7%, well under the 50%-of-average retirement threshold — do not generate more 360°-stand-style variants without a different angle).

**The single biggest new finding, only visible because retention data now exists:** 2-second retention across every statistically meaningful variant is WEAK-to-MARGINAL (25–45%) but never CRITICAL — meaning the hook itself is not the main problem. But average watch-time-rate is POOR (<25% of the 15s runtime) on 13 of 16 variants, including several high-view variants (e.g. 002C: 390 views, only 13% watch rate). **Viewers are getting past the hook and then leaving well before the video ends, regardless of which hook opened it.** Root-cause diagnosis: [LIKELY] too-slow mid-video pacing (cause f in `tiktok-analyze.md`'s C.F diagnosis tree). One notable positive outlier worth investigating further: 003A (Price Shock, 355 views — a statistically meaningful sample) has by far the best watch time in the dataset, 7.5s of 15s (50%, GOOD) — roughly double every other reliable-sample variant.

**Hook-type finding refined by today's retention data:** Problem/Solution has the higher raw win count (2/4), matching yesterday's finding — but its apparent retention edge (48.8% avg) is mostly an artifact of one 1-view outlier (003C, 84%). Excluding that outlier, Problem/Solution's 3 real samples average 37% (WEAK) — actually *below* Curiosity's fully-reliable 42.8% average (all 4 Curiosity samples come from statistically meaningful view counts). **Curiosity remains the recommended lead hook for Product 009's Variant A** — same conclusion as 2026-07-01's analysis, but now backed by real retention data instead of engagement alone.

**Confidence score: 35/100** (base 65 for 16 CONFIRMED rows, minus 30 in penalties — the winning hook has changed on every single one of the 4 products tested so far, with no repeatable pattern yet). Notably lower than a pure row-count-based score would suggest, specifically because of that inconsistency — not a data-quality problem, a genuine "we don't have a proven pattern yet" signal.

**Biggest remaining data gap, called out explicitly in the brief:** `cta_code_comments` has never been collected for any product across any run. Every product in the C.G product-type analysis is stuck at CONTINUE TESTING (rather than reaching SCALE NOW or PAUSE SIMILAR) specifically because CTA activation is UNKNOWN for all of them. This is now the top priority for the next `/tiktok collect` pass, ahead of anything else.

**PRODUCT 009 DECISION: PROCEED ✅.** Lead hook for Variant A: Curiosity. Category: Mobile Phone Accessories (proven ceiling via 002, but also contains the account's worst result via 008 — high-variance, not automatically safe). Price target: ₪15–24. Pacing adjustment (new, most actionable item): shorten/tighten the mid-video benefit/proof section — the pacing problem matters more than hook choice this time. Files written: `analysis/2026-07-02-products-002-003-007-008-analysis.md`, `data/learning_report.json` (both `winner`/CSV untouched per STEP A's skip rule). Weekly audit not due (last one was 2026-07-01, needs 7+ days).

**Next action:** run `/tiktok` to generate Product 009 using this brief, or collect `cta_code_comments` first to close the biggest data gap before scaling further.

### 2026-07-02 (session 4) — Collector QA run; Check 1 false positive found and fixed

**Backfill re-run (session 3, immediately prior) succeeded cleanly:** re-ran `--product-id 002,003,007,008 --update` with the direct-video-ID-navigation fix from session 2. Result: 16/16 collected, 0 NOT_FOUND, every variant via `Found via direct video-ID navigation`. Independently verified (not just the script's own PASS summary, given what happened in session 1): cross-checked each Product 002 variant's video_id against `data/002-identity-map.json` (002A/B/C/D each used their own distinct, correctly-mapped ID — no repeat of the wrong-identity write), and cross-checked all 16 rows' views/likes/comments against the pre-backfill baseline (15 exact matches, 003A +1 view from natural growth). All 5 target fields populated on all 16 rows with plausible values.

**Then ran `scripts/tiktok_collect_qa.py --strict`:** 3 PASS / 2 FAIL (Video Matching, Login/Session). Investigated both rather than accepting the verdict at face value:
- **Video Matching FAIL is real but out of scope** — 12 variants missing (001A-D, 004A-D, 005A-D), entirely the pre-existing 001/004/005 gap already documented above, unrelated to today's work. Re-ran scoped to `--product-id 002,003,007,008`: Video Matching **PASSES 16/16** — today's actual work is clean on its own.
- **Login/Session FAIL was a false positive in the QA script itself.** Dumped every cookie's real expiry from `data/tiktok-session.json`: the actual auth cookies (`sessionid`, `sid_guard`, `uid_tt`) were valid for months. The failing check was flagging an expired `msToken` entry — TikTok's short-lived, auto-rotating anti-bot/telemetry token, not a login credential. The file actually contains *two* `msToken` entries (one expired the day before, one valid until September) because TikTok re-saves it under the same name as it rotates during normal use — a naive "any expired cookie by name" scan will always eventually catch a stale copy of a token like this even while the session is perfectly usable. Confirmed the session was genuinely fine independently: it had just driven the real account through the full 16-variant backfill minutes earlier.

**Fix (in `scripts/tiktok_collect_qa.py`, Check 1 / `check_1_session()`):** now validates ONLY `REQUIRED_AUTH_COOKIES = {"sessionid", "sid_guard", "uid_tt"}` — the exact same set `tiktok_session_login.py` itself already polls for as proof of successful login, reused here instead of inventing a second, inconsistent definition of "logged in." Handles repeated cookie names correctly (valid if *any* entry under that name is unexpired, not just the first one found). Transient/telemetry cookies like `msToken` are no longer inspected for expiry at all, by design. Still strict: FAILs if any required cookie is missing entirely, or if every entry under that name is expired. This is narrower, not weaker — no other check was touched.

**Re-ran Collector QA after the fix — full result below (see next section for the literal output).**

### 2026-07-02 (session 2) — "Your top posts" is a ranked leaderboard, not an exhaustive list. PERMANENT FIX: direct video-ID URL navigation.

**What triggered this:** the first backfill attempt (session 1, same day) was approved and run scoped to products 002/003/007/008 (`--update`). Result: only 7/16 variants collected; 9 came back `NOT_FOUND`; and **002A was written with 002B's real data (353 views)** — a genuine wrong-identity write, not just a missing-data gap. Caught before it could do lasting damage because the CSV had been backed up to `data/video_results.csv.backup-2026-07-02` immediately before the run; restored from that backup and diffed byte-for-byte identical to confirm.

**Root cause, proven with evidence, not assumed:**
- The page at `CONTENT_TAB_URL` is titled **"Your top posts"**. Hovering its info icon shows TikTok's own description: *"Your top performing posts in the last 28 days, ranked according to the views, likes, new viewers, and new followers gained."*
- Confirmed rigorously that this is a real cap, not a scrolling/patience issue: "Last 28 days" was already the active selection (checkmark verified by opening the actual dropdown, not just reading a label), and the list's own scrollable container was walked to a verified stable end — `scrollTop` plateaued at exactly `scrollHeight − clientHeight` (the mathematical bottom) for 4+ consecutive attempts with a 1.5s settle delay each, and `scrollHeight` itself never grew during the entire walk (the real tell for "more is lazy-loading somewhere"). Only 10 of the account's 16 posted variants ever render on this page, no matter how it's scrolled or which date range is picked.
- The separate plain **"Posts"** tab (left sidebar) does list all 15-16 posts and has a working search box — but clicking a post there opens its public-facing page (`tiktok.com/@handle/video/{id}`), never analytics. Confirmed by direct test on 007B. Dead end on its own.
- **The fix:** the analytics detail page is directly addressable by video ID — `https://www.tiktok.com/tiktokstudio/analytics/{video_id}/overview` — and a completely fresh page navigation to that URL (no prior click, no dependency on "Your top posts") works identically whether or not the video ranks in that leaderboard. Confirmed on 007B specifically, a video absent from "Your top posts" at every date range tried: loaded full real analytics (91 views, 2 likes, 3.1s avg watch time, 4.4% watched-full) with zero dependency on the leaderboard.

**Fix implemented in `scripts/tiktok_analytics_collect.py`:**
- New `POSTS_TAB_URL` / `ANALYTICS_DETAIL_URL_TMPL` constants and a large permanent comment block above `CONTENT_TAB_URL` recording all of the above — written there specifically so this doesn't get silently re-investigated or re-broken in a future session.
- New `_find_video_id_via_posts_tab(page, cta_code)` — looks up a video's ID via the full "Posts" tab's search box. **Safe only for unique per-variant CTA codes** (e.g. "007B"); never used for bare 3-digit codes (e.g. "002"), which still require the existing visual-evidence + identity-map flow (unrelated to this fix, unaffected by it).
- New `_open_video_detail_direct(page, video_id)` — navigates straight to the analytics URL and verifies a real detail-page marker is visible before reporting success (never assumes).
- `collect_one_variant()` restructured: PRIMARY path now resolves a video ID (from `data/{pid}-identity-map.json` when given, or freshly via `_find_video_id_via_posts_tab` for non-bare codes) and calls `_open_video_detail_direct()`. The entire old find-row-in-"Your top posts"-then-click-"View Data" flow is kept, unchanged, only as a fallback for bare-CTA products with no identity map yet. Shared tail logic (scroll for lazy-loaded sections, DOM extraction, screenshot, metrics assembly) factored into a new `_finish_collection()` helper used by both paths.
- **Separately fixed the actual bug that let 002A's wrong data through:** the existing bare-CTA safety guard in `main()` (`if not raw["not_found"] and is_bare_code and skip_count > 0 and not video_id: ... raw["not_found"] = True`) only ever checked `skip_count > 0` — variant A always has `skip_count == 0` and so was **never covered by this guard**, even though its "first match wins" lookup is exactly as unverified as any other skip_count value when no video_id is confirmed. Condition changed to drop `skip_count > 0` entirely — now applies to any bare-code match without a confirmed video_id, including variant A.

**Validated (read-only, no CSV writes, three separate scenarios):**
1. 008B (per-variant CTA, ranks in "Your top posts") — still resolves correctly via the new direct path: `views=114, likes=1, comments=0, saves=0, shares=0, average_watch_time=2.85, watched_full_video_rate=0.0310, first_2_second_retention=0.4200`. No regression.
2. 007B (per-variant CTA, **absent** from "Your top posts" at every date range) — previously came back `NOT_FOUND` during the failed backfill; now resolves correctly via `_find_video_id_via_posts_tab` + direct navigation: `views=91, likes=2, comments=0, saves=0, shares=0, average_watch_time=3.1, watched_full_video_rate=0.0440, first_2_second_retention=0.4500` — matches the existing CSV baseline exactly.
3. All 4 of Product 002 (bare-CTA, identity-map-based) — each variant now resolves via its own distinct `video_id` from `data/002-identity-map.json` to its own correct, distinct result: 002A=153/1/0, 002B=353/2/0, 002C=390/1/0, 002D=315/2/0 — all matching baseline exactly. This is the specific scenario that produced the wrong-identity write; confirmed it can no longer happen via this path.

**Explicitly NOT done yet:** the historical backfill has not been re-attempted since this fix. `data/video_results.csv` is still in its pre-backfill state (restored from the pre-backfill backup). Next step, when approved: re-run the backfill (`--product-id 002,003,007,008 --update`) and verify all 16 rows populate correctly and distinctly before proceeding to Collector QA / `/tiktok analyze`.

### 2026-07-02 (session 1) — DOM text-label extraction implemented + validated (VALIDATED ON 1 VARIANT ONLY)

Picked up from the 2026-07-01 "remaining gap" below: `parse_captures()`'s XHR-key guessing has been superseded by direct DOM reading for these 5 fields, added to `scripts/tiktok_analytics_collect.py` as a new "DOM text-label extraction" section (`extract_dom_metrics()` and helpers, called from `collect_one_variant()` once `_open_video_detail()` confirms the detail page was reached; DOM values take priority, XHR guessing kept only as a fallback).

**Confirmed field locations (live, on 008B):**
- `average_watch_time` / `watched_full_video_rate` — plain text labels ("Average watch time" / "Watched full video") with the value on the next line of the same stat card. Read via `_read_stat_card_value()`.
- `saves` / `shares` — no text label at all; two of 5 bare numbers next to icons (views/likes/comments/shares/saves, in that left-to-right order, confirmed by matching each icon's SVG path shape against the screenshot). Read via `_read_engagement_icons()` — note the query must filter to numeric-only text; the caption text shares the same `data-tt` attribute as the 5 stat numbers and will silently break an exact-length-5 check otherwise.
- `first_2_second_retention` — no text anywhere; it's a point on a line chart with no accessible underlying data (checked for an ECharts instance on `window` — not present) and no SVG/circle data points. Only reachable by simulating a mouse hover over the chart canvas and reading the floating tooltip that appears (format confirmed: time + value concatenated with no separator, e.g. `"0:0242%"` = 0:02 at 42%). Read via `_extract_first_2_second_retention()`, which nudges the hover position by whole-second increments — verified against the tooltip's own displayed timestamp each time, never assumed — until it lands exactly on the 2-second bucket.
  - **Important gotcha, already fixed in code:** there are TWO identically-classed `.echarts-for-react` charts on the detail page (a 7-day trend chart above, and this retention curve below). Naively grabbing "the first chart on the page" grabs the wrong one — it sits permanently off-screen (negative Y) after the page's own scroll, which is why early hover attempts silently did nothing. `_find_retention_canvas()` scopes strictly from the exact "Retention rate" heading text instead of querying charts globally.

**Validated result on 008B (live, 2026-07-02):** `saves=0`, `shares=0`, `average_watch_time=2.85`, `watched_full_video_rate=0.0310`, `first_2_second_retention=0.4200` — all matching the account's real analytics page exactly. Validated via `scripts/validate_click_fix.py` (unchanged — still explicitly does not write to `video_results.csv`).

**Known pre-existing gaps, NOT fixed today (out of scope for this pass):**
- `retention_rate` (a different field from `first_2_second_retention`) is still blank — still relies on XHR guessing, never addressed.
- `_scrape_row()` (the content-list-page row scraper, used for a fallback views/likes/comments read before the detail page even opens) returned `likes=114, comments=''` on this same 008B run instead of the correct `likes=1, comments=0` — a pre-existing bug unrelated to today's fix (it runs before any of today's new code and was not touched). Worth a look before the full backfill, since a wrong fallback value would only surface if the DOM-icon-row read (which got these three fields correct) somehow fails.

### 2026-07-01 — Collector click-target / wrong-page bug: root cause + fix (VALIDATED ON 1 VARIANT ONLY)

**Root cause:** `CONTENT_TAB_URL` in `tiktok_analytics_collect.py` pointed at `https://www.tiktok.com/tiktokstudio/content` — TikTok Studio's **Posts management list** (edit/share/comment/"..." action icons only, no analytics link of any kind). The page that actually has per-video analytics is a *different* URL entirely: `https://www.tiktok.com/tiktokstudio/analytics/content` (Analytics → Content tab), which has a clearly labeled **"View data"** button per row in an "Action" column. The collector has never once navigated to the right page — every blank saves/shares/watch-time/retention value traces back to this single wrong URL, not to a TikTok API change or a wrong JSON key guess (those guesses were never even given a chance to be tested against real data).

Two compounding bugs on top of the wrong URL, found via direct evidence (real screenshots from actual collection runs, not guessing):
1. Every row-click target (`text={cta_code}` matching the caption) opened a **new browser tab** showing the public-facing video page — confirmed via screenshot (For You/Explore sidebar, public like/comment/save icons) — which the old code never looked at; it kept screenshotting the stale original tab.
2. Even after correctly following the new tab, grabbing the *first* "View data" button anywhere on the page (rather than the one belonging to the matched row) opened the wrong video's analytics entirely.

**Fix (in `scripts/tiktok_analytics_collect.py`):**
- `CONTENT_TAB_URL` corrected to the Analytics → Content URL (with the `pastDay: 28` date-range query param, matching "Last 28 Days").
- New `_open_video_detail(page, el)` — replaces every bare `el.click()` row-opener. Verifies navigation actually happened (URL change, new-tab detection via `context.expect_page()`, or a detail-page marker becoming visible) instead of assuming a click worked. Prints an explicit WARNING when it can't verify, rather than silently producing another blank result.
- New `_find_view_data_button(page, el)` — finds the "View data" button in the **same row** as the matched video (by Y-coordinate proximity, tolerance 50px), not just the first one on the page. The button sits past the right edge of the default viewport; `scroll_container_horizontal()` / `JS_SCROLL_CONTAINER_HORIZONTAL` (new) scrolls the table right to reveal it, using the same "find the real `overflow:auto` element" technique already established for vertical scrolling in this file.
- `collect_one_variant()` now scrolls the detail page (via the existing `scroll_container()`, not `window.scrollBy` — this page also uses a nested scrollable container) **after** opening it, because the Retention rate and Traffic source sections sit below the fold and do not render/populate until scrolled into view.
- `scroll_and_find_video()` and `search_box_find()` no longer click internally — they return the matched element so `_open_video_detail()` can handle opening + verification in one place instead of 5 duplicated, unverified click sites.

**Validation (single variant, 008B, via new throwaway script `scripts/validate_click_fix.py` — explicitly does NOT write to `video_results.csv`):**
Reached the **correct** video's real TikTok Studio analytics page — confirmed by exact match to the known CSV baseline (114 views / 1 like / 0 comments / posted 6/18). Screenshot evidence (`data/tiktok-analytics/product008/008B_analytics.png`) shows, for the first time ever in this project:
- Average watch time: 2.85s
- Watched full video: 3.1%
- Retention rate: "Most viewers stopped watching at 0:02" + a full interactive 0:00–0:15 retention curve
- Traffic source: For You 92.7%, Personal profile 7.3%, Following/Search/Other/Sound all <0.1%

**Remaining gap — do not skip this before backfilling:** the automated field-extraction (`parse_captures()`, which guesses XHR endpoint URL fragments and JSON key names) still returns blank for all 5 target fields even though the data is now correctly visible on the page. The most likely next step is switching from XHR-guessing to **direct DOM text-label extraction** (reading the visible "Average watch time" / "Watched full video" / "Most viewers stopped watching at" / Traffic source percentage labels as text) — now that the exact rendered labels are known from the screenshot evidence, this should be far more reliable than continuing to guess network internals that were never verified against a real response.

**Explicitly NOT done today (per PM scope directive):** no full historical backfill, no CSV rows modified, no Collector QA re-run, no `/tiktok analyze` re-run. `scripts/diagnose_view_data_button.py` was created as a diagnostic aid but superseded by direct screenshot review before being run.

**Next action (start here):**
1. ~~Build the DOM text-label extraction for saves/shares/average_watch_time/watched_full_video_rate/first_2_second_retention.~~ Done 2026-07-02, see above.
2. ~~Re-validate on 008B with `scripts/validate_click_fix.py`.~~ Done 2026-07-02 — all 5 fields populate correctly, still without writing to the CSV.
3. **Start here:** run a full historical backfill across all variants, re-run `tiktok_collect_qa.py` (note: it was NOT_APPROVED as of the last real run — 12 variants from Products 001/004/005 are still missing from the CSV entirely, a separate pre-existing gap unrelated to today's fix), then re-run `/tiktok analyze` and Analyze QA. Consider fixing the `_scrape_row()` likes/comments bug (see 2026-07-02 section above) before or during the backfill, since it's a fallback path the backfill will exercise. Also consider adding a Traffic Source schema column — confirmed available and populated on the real analytics page (For You / Personal profile / Following / Search / Other / Sound breakdown), but not currently part of the 33-column CSV schema at all.
4. Product 009 / Analyzer v3 remain paused until the above completes, per the PM's stated milestone order (Collector Enhancement → Collector QA → re-run Analyze → Analyze QA → Analyzer v3).

---

## 2026-06-30 — Product 002 identity blocker (RESOLVED, historical)

**Phase (as of 2026-06-30):** Analytics collector — Product 002 RESOLVED via visual hook-text identity confirmation. All uploaded products (002/003/007/008) now have confirmed metrics, 16/16 variants.

**RESOLVED (2026-06-30): Product 002 identity blocker.**
Option C (DOM investigation) succeeded once the underlying tooling bugs were fixed — unique identifiers DID exist all along; the prior "no unique identifiers found" conclusion was caused by two script bugs, not a DOM/data limitation:
1. The inspector script scrolled `window`, but TikTok Studio's content list is a nested virtualized `overflow:auto` div (`scrollHeight` 1610 vs `clientHeight` 528) — `window.scrollBy`/`scrollY` never moved past ~30px, so the list never actually advanced to where Product 002's rows (uploaded 2026-06-14, older than 007/008) live.
2. Playwright's `text=` locator engine returned 0 matches for the Hebrew caption substring even after scrolling — confirmed unreliable for this RTL text (consistent with the prior note in `search_box_find()`'s docstring). Switched to raw JS `element.textContent.includes()` scanning, which worked immediately.

Once scrolling targeted the real container and matching used JS substring scan, each of the 4 Product 002 rows resolved to a **distinct href / video ID** — i.e., a real, stable, per-variant unique identifier was present in the DOM the whole time:
| Video ID | href suffix | Variant | Confirmation method |
|---|---|---|---|
| 7651320643010514197 | …514197 | **A** | Exact visual match: hook overlay "לא תאמיני כמה זה עולה בעלי אקספרס..." |
| 7651327807460642068 | …642068 | **B** | Exact visual match: hook overlay "ראיתי את זה בטיקטוק ולא האמנתי שזה קיים..." |
| 7651330347824696596 | …696596 | **C** | Exact visual match: hook overlay "מצאתי את הפתרון לבעיה שכולנו מכירות" |
| 7651330918107385109 | …385109 | **D** | Partial visual match (popup-obscured) "כולן מדברות על זה ואני..." + elimination (A/B/C already uniquely assigned) |

Method: each variant's video-config (`data/002-video-config.json`) bakes a UNIQUE hook-text overlay into the video pixels at 0–2s ("top-center"). This text is independent of the (identical) caption/CTA and survives in the video itself. Opened each of the 4 video URLs directly, force-seeked the `<video>` element to t=0.15s via JS (`v.currentTime = 0.15; v.pause()`), screenshotted, and visually read the overlay text against the known per-variant hook strings — an unambiguous 1:1 match for 3 of 4, with the 4th forced by elimination.

**Metrics collected and written to `data/video_results.csv` (CONFIRMED):**
| Variant | Views | Likes | Comments |
|---|---|---|---|
| 002A | 153 | 1 | 0 |
| 002B | 353 | 2 | 0 |
| 002C | 390 | 1 | 0 |
| 002D | 315 | 2 | 0 |

Scripts written this session (kept in `scripts/`, read-only / diagnostic — not wired into the production collector):
- `identify_product_002_visual.py` — scrolls the real list container, JS-scans for the shared caption substring, screenshots each matched row by raw viewport clip.
- `identify_002_open_each.py` / `identify_002_seek_start.py` — opens each confirmed video URL directly and force-seeks to the hook segment for visual confirmation.
- `collect_002_confirmed.py`, `get_002C_views.py` — collect likes/comments/views for the confirmed mapping.

**PORTED (2026-06-30, later same session): all three fixes are now in `tiktok_analytics_collect.py` itself**, not just one-off scripts:
1. `scroll_container()` (real virtualized-list scrolling) replaces `window.scrollBy` in both paths of `scroll_and_find_video()`.
2. `find_all_caption_matches()` / `JS_SCAN_SUBSTRING` (raw JS `textContent.includes()`) available for any future Hebrew caption matching.
3. `load_identity_map(pid)` reads `data/{pid}-identity-map.json` ({video_id: letter}); `detect_all_products()` attaches the matching `video_id` to each variant; `collect_one_variant()` tries `scroll_until_row_visible()` (CSS href match, ASCII-safe) first when a `video_id` is known. Seeded `data/002-identity-map.json` with today's confirmed mapping.
4. For any *future* bare-CTA product with no identity map yet: `gather_visual_evidence()` runs automatically (enumerates rows by caption substring, opens each video, force-seeks to t=0.15s, screenshots into `output/identify_{pid}/`) instead of guessing via the old unsafe `skip_count` order-matching. Those variants are written to the CSV as `variant_status = PENDING_VISUAL_CONFIRMATION` (not `NOT_FOUND` — the row is known to exist, just not yet assigned to a letter) and excluded from the QA report's "found" stats.

**Verified end-to-end:** ran `python scripts/tiktok_analytics_collect.py --product-id 002 --update` — the production script (no manual scripts) found all 4 variants automatically via the identity map and reproduced the exact same metrics (002A 153/1/0, 002B 353/2/0, 002C 390/1/0, 002D 315/2/0). No more standalone `identify_*` scripts needed for this product going forward.

**REGRESSION TEST (2026-06-30): ran `--product-id 007,008 --update` after the port — no regressions, plus a bonus fix.**
All previously-CONFIRMED values reproduced exactly: 007A=120, 007B=91, 007D=145, 008B=114, 008C=133, 008D=2 (008A ticked 3→4, expected natural growth, same likes). CSV (16 rows) intact, all CONFIRMED, no corruption.

Bonus: **007C is now resolved automatically** (106 views, 1 like) — found after 1 extra scroll step. The earlier diagnosis ("007C caption missing CTA code, needs manual edit") was actually the SAME root cause as Product 002: the old `window.scrollBy` never reached far enough down the virtualized list. No caption edit was ever needed. `scroll_container()` reaching one step further than `window.scrollBy` used to is what fixed it — the 007C item in PROJECT_STATUS's "Next action" list is now WRONG and should not be acted on.

**Next action (SUPERSEDED 2026-07-01 — see the "Next action" list at the top of this file instead):**
1. ~~007C caption edit~~ — not needed, see regression test above. Resolved.
2. ~~Product 009 remains paused...run `/tiktok analyze` when ready~~ — `/tiktok analyze` WAS run on 2026-07-01, but its output is now known to be built on an incomplete dataset (saves/shares/watch-time/retention were blank for the reasons documented in the 2026-07-01 section above). Do not treat that analyze run's product/hook recommendations as final until the collector fix is fully backfilled and analyze is re-run.
3. If a future product is uploaded with a bare/shared CTA again, just run the collector normally — it will auto-detect the missing identity map, gather hook-frame screenshots into `output/identify_{pid}/`, and print exact instructions for creating `data/{pid}-identity-map.json`. (This item is still valid, unrelated to the 2026-07-01 fix.)

Steps 1–4 below (ARCHIVED 2026-06-30 — all superseded by the RESOLVED section above):
   Step 1 (window-scroll/search-box patch idea), Step 2 (manual 007C caption check), Step 3
   (rerun 002,003 --update), and Step 4 (manually de-duplicate the 002B/003B shared hook
   text) were the pre-investigation plan. None of them were needed in the end — the real
   root cause was the container-scroll + Hebrew text= bugs fixed and ported into
   `tiktok_analytics_collect.py` (see above). 007C did NOT need a caption edit. 002B/003B's
   shared hook text did NOT need to be de-duplicated — 003 was already collecting fine, and
   002 now uses the href identity map, which doesn't depend on hook-text search at all.
   Kept here only as historical record of what was once believed necessary; do not act on it.

Step 5 — Future (out of current scope): Fix XHR capture for watch_time / retention / 2s_ret.
   Open TikTok Creator Center in browser with DevTools → Network tab → filter XHR/fetch.
   Record actual URL patterns that fire when video analytics loads.
   Update `ANALYTICS_URL_FRAGMENTS` in `tiktok_analytics_collect.py`.

**Products:**
| ID | Product | Status |
|----|---------|--------|
| 001 | Astronaut Galaxy Projector | ✅ UPLOADED — analytics NOT YET COLLECTED |
| 002 | 360° Magnetic Car Phone Mount (₪23, 10,000+ sold) | ✅ UPLOADED — analytics CONFIRMED (resolved 2026-06-30 via visual hook-text ID) — 002A: 153 views ✅ \| 002B: 353 ✅ \| 002C: 390 ✅ \| 002D: 315 ✅ |
| 003 | Mini Bag Sealer (₪8, 100,000+ sold) | ✅ UPLOADED — 003A: 354 views ✅ \| 003B: 360 ✅ \| 003C: 1 ✅ \| 003D: 2 ✅ |
| 004 | Mini Mist Fan | ❌ BLOCKED (unconfirmed sales/price) |
| 005 | Electric Lint Remover | ❌ BLOCKED (unconfirmed sales/rating/price) |
| 006 | — | ❌ FAILED — all 5 candidates rejected at STEP 3A |
| 007 | מארגן גב המושב עם שולחן מתקפל (Car Seat Back Organizer, ₪39) | ✅ UPLOADED — analytics CONFIRMED (4/4) — 007A: 120 views ✅ \| 007B: 91 ✅ \| 007C: 106 ✅ (resolved 2026-06-30, same scroll-depth bug as 002) \| 007D: 145 ✅ |
| 008 | מעמד שולחני 360° (360° Phone/Tablet Stand, ₪40.29) | ✅ UPLOADED — 008A: 3 views ✅ \| 008B: 114 ✅ \| 008C: 133 ✅ \| 008D: 2 ✅ |
| 009 | — | ⏸️ PAUSED — waiting for analytics data from 002/007/008 |

```
	— 2026-06-30 Product 002 Identity Investigation Session —

📌 SESSION OBJECTIVE:
   Fix collector to correctly identify Product 002 variants after caption-based search implementation.
   PM rule: Prove all possible unique identifiers exhausted before requiring caption edits.

✅ FIXES COMPLETED TODAY (2026-06-30):
   1. Caption-based search implemented — collector now searches TikTok Studio using caption text
      (first 30 chars) instead of video overlay hook_text. Root cause fixed: TikTok Studio search
      box searches caption, not overlay text.
   2. Bare-code safety added — collector detects bare 3-digit codes (e.g., "002") and refuses to
      confirm identity via CTA match. Prevents scraping same video multiple times for all variants.
   3. Search clearing reverted — attempted to clear search filter between variants but caused
      regression (even 002A became NOT_FOUND). Reverted to working state.
   4. Skip_count logic validated — 002A successfully scraped via skip_count=0 (first "002" found).
   5. Bare-code unverified detection added — bare codes found via skip_count have UNVERIFIED
      identity; metrics NOT written to CSV (treated as NOT_FOUND).

⚠️ REMAINING BLOCKER — Product 002 Identity Confirmation Failure:
   STATUS: All 4 Product 002 variants uploaded to TikTok but collector returns NOT_FOUND for all.
   ROOT CAUSE: Identity unconfirmable via current methods.

   EVIDENCE:
   - All 4 variants share identical caption: "מצאתי מחזיק טלפון לרכב בעלי אקספרס ב-23₪..."
   - All 4 use bare CTA code: "כתבי 002 בתגובות" (no variant letter A/B/C/D)
   - Caption-based search filters to Product 002 videos correctly
   - CTA confirmation cannot distinguish between variants (all match "002")
   - Skip_count order-based matching is unsafe (no confirmation which variant is which)

   COLLECTOR BEHAVIOR (last run 2026-06-29 23:40):
   - 002A: search found "002", scraped views=315 via skip_count=0 → IDENTITY UNVERIFIED → NOT_FOUND
   - 002B/C/D: search found "002" but skip_count logic failed → NOT_FOUND

   CSV STATUS: All 4 Product 002 rows safely marked NOT_FOUND (no incorrect data written).

🔍 DOM INVESTIGATION ATTEMPTED (2026-06-30):
   OBJECTIVE: Inspect Product 002 video rows in TikTok Studio to find unique identifiers before
   requiring caption edits. Check: href, video ID, timestamp, thumbnail URL, data-* attributes,
   aria-* attributes, parent container IDs, etc.

   SCRIPT CREATED: scripts/inspect_product_002_dom.py
   - Playwright-based inspector
   - Strategy: navigate to TikTok Studio, find Product 002 videos, extract all DOM properties
   - Compare all 4 variants to identify unique vs shared fields

   RESULT: INCOMPLETE
   - Script could not reliably locate Product 002 videos on page
   - Issues: scrolling to find older videos (June 14), search filtering, link detection
   - Multiple strategies attempted (text locator, XPath, position filtering) — all failed
   - Last screenshot shows Products 007/008 (June 18), not Product 002 (June 14)

   CONCLUSION: DOM investigation blocked by script issues, not by DOM structure.
   Cannot conclude whether unique identifiers exist until script successfully finds and inspects all 4 rows.

📋 CURRENT SAFE CSV STATE (2026-06-30):
   Product 002: ALL variants NOT_FOUND ✅ (safe — no incorrect data)
   - 002A: NOT_FOUND (was views=315 in previous run, marked unverified, reset to NOT_FOUND)
   - 002B: NOT_FOUND
   - 002C: NOT_FOUND
   - 002D: NOT_FOUND

   Product 003: ALL variants CONFIRMED ✅
   - 003A: views=354, likes=0
   - 003B: views=360, likes=1
   - 003C: views=1, likes=1
   - 003D: views=2, likes=0

   Product 007: 3/4 CONFIRMED ✅
   - 007A: views=120, likes=0
   - 007B: views=91, likes=2
   - 007C: NOT_FOUND (caption edit needed — CTA code missing)
   - 007D: views=145, likes=1

   Product 008: 4/4 CONFIRMED ✅
   - 008A: views=3, likes=1
   - 008B: views=114, likes=1
   - 008C: views=133, likes=1
   - 008D: views=2, likes=1

📋 COLLECTOR QA REPORT (2026-06-29 23:40):
   Products scanned: 2 (002, 003)
   Expected variants: 8
   Collected: 4 (003A/B/C/D)
   Not found: 4 (002A/B/C/D)
   Skipped: 0

   Data quality:
   - Views extracted: 4/4 ✅
   - 2-sec retention data: 0/4 ❌ (XHR capture issue, out of scope)

   QA Gates:
   1. Login / session: PASS ✅
   2. Video matching: PARTIAL — 4 variants not found
   3. Data extraction: FAIL — no retention data captured
   4. CSV schema (33-col): PASS ✅
   5. Analyzer handoff: PASS ✅

   Overall: PARTIAL — Product 002 identity blocker

📋 NEXT EXACT ACTION FOR TOMORROW (2026-07-01):

   OPTION A — USER DECISION (RECOMMENDED):
   User decides: caption edits acceptable? If YES → edit 4 TikTok captions to add variant letters.
   If NO → continue DOM investigation (Option B) or accept data loss (mark Product 002 UNCOLLECTABLE).

   OPTION B — COMPLETE DOM INVESTIGATION:
   1. Fix scripts/inspect_product_002_dom.py:
      - Add explicit scroll to June 14 date range
      - Use search box with full Product 002 caption
      - Find all visible video rows after search completes
      - Extract href, video ID from URL, data-e2e, aria-label, timestamp, thumbnail src
   2. Run inspection against live TikTok Studio
   3. Create comparison table: which fields differ across 002A/B/C/D?
   4. If unique identifiers found → update collector to use them
   5. If NO unique identifiers found → caption edits required (return to Option A)

   OPTION C — ACCEPT DATA LOSS:
   Mark Product 002 as UNCOLLECTABLE (legacy product with shared identity markers).
   Proceed to Product 009. Learning from 002 will be incomplete.

   BLOCKER SEVERITY: LOW — Products 003/007/008 collecting successfully (12/16 variants).
   Product 002 is 4-year-old test product; data loss acceptable if caption edits rejected.

```
	— 2026-06-28/29 Analytics Collector Fix Session —

✅ Fix 1 — elementFromPoint DOM scraping (complete):
   Root cause: TikTok Studio uses split-column layout — title <A> and numeric cells (Views/Likes/Comments)
   live in separate DOM subtrees. Ancestor-walking never reaches the data cells.
   Fix: _scrape_row(el) now scans across the viewport at rowY using elementFromPoint(x, rowY).
   Deduplication by DOM element reference (Set). scrollIntoView({block: 'center'}) called first.
   Helper _parse_tiktok_count() added: converts "1.2K"→"1200", "133"→"133".

✅ URL fix — tiktokstudio vs creator-center:
   TikTok changed content URL from creator-center/content to tiktokstudio/content.
   Updated CONTENT_TAB_URL in tiktok_analytics_collect.py. Added exception handling for redirect.

✅ Fix 2a — Sticky header clamp (complete):
   After scrollIntoView, elements could land at rowY < 180 (inside fixed sticky header).
   elementFromPoint at low rowY returns header overlay elements, not data cells.
   Fix: second evaluate checks rect.top < 180 → window.scrollBy(0, -(200 - t)) to clear the header.

✅ Fix 2b — search_box_find() added (partial — identity confirmation fix still needed):
   Root cause: TikTok Studio content list truncates captions. CTA codes at the end
   ("003A", "002") are cut off — text= selectors fail.
   search_box_find(page, hook_text, cta_code) added: types first 20 chars of hook_text
   into TikTok Studio search box to filter the list before CTA match.
   Integrated as primary finder in collect_one_variant() when hook_text is set.
   scroll_and_find_video() is now fallback when hook_text is empty.

⚠️ BLOCKER — search_box_find fallback rejected by PM (2026-06-29):
   Fallback "first visible anchor with x > 300" found sidebar nav element (x=209) for all
   002B-D and 003A-D variants. Scraped metrics from wrong element — all showed "views=3, likes=1".
   PM rule: Incorrect data is worse than missing data.
   Fix required: remove fallback entirely; confirm identity by CTA match OR unique single result.

📋 Run results as of 2026-06-29:
   007A: 120 views ✅ | 007B: 91 ✅ | 007C: NOT FOUND ❌ | 007D: 145 ✅
   008A: 3 ✅ | 008B: 114 ✅ | 008C: 133 ✅ | 008D: 2 ✅
   002A: 315 views ✅ (CTA "002" matched after search filter)
   002B-D: IDENTITY UNCONFIRMED ❌ (sidebar element scraped — data must be reset to NOT_FOUND)
   003A-D: IDENTITY UNCONFIRMED ❌ (sidebar element scraped — data must be reset to NOT_FOUND)

📋 CSV status: data/video_results.csv — 16 rows, 33-col v2 schema ✅
   007/008: views confirmed, engagement rates computed
   002A: views=315 confirmed | 002B-D and 003A-D: pending data reset + re-collection
   watch_time, retention, 2s_ret: ALL blank (Blocker D — XHR, separate fix, out of current scope)
```

```
✅ Architecture designed
✅ /tiktok command updated (Steps 0–12)
✅ /tiktok analyze updated (Quality & Learning Agent)
✅ TIKTOK_AGENT_PLAN.md updated
✅ generate_assets_spec.md written and approved
✅ generate_videos_spec.md written and approved
✅ generate_assets.py   — IMPLEMENTED and TESTED (2026-06-11)
✅ generate_videos.py   — IMPLEMENTED and TESTED (2026-06-11)
✅ End-to-end /tiktok pipeline test — COMPLETE (2026-06-11, product 001)
✅ TIKTOK_AGENT_PLAN.md script status table — UPDATED (2026-06-11)
✅ CURRENT_PRODUCT_ID — updated to 002 in tiktok.md (2026-06-11)

— 2026-06-14 upgrades —
✅ 72-hour rule added — only CONFIRMED variants (72h+) affect long-term learning
✅ video_results.csv schema updated — 4 new columns: upload_date, upload_time, age_hours, variant_status
✅ Variant status system added — NEW / TESTING / CONFIRMED per variant
✅ Product status system added — NEW / TESTING / WINNING / RETIRED PRODUCT
✅ STEP 0B added to /tiktok — Winner Scaling Check before new product search
✅ Weekly Audit Report added to /tiktok analyze — triggers when 7+ CONFIRMED rows exist or 7 days since last audit
✅ CURRENT_PRODUCT_ID — updated to 003 in tiktok.md (2026-06-14)

— 2026-06-14 auto product ID —
✅ CURRENT_PRODUCT_ID removed — PRODUCT ID now auto-assigned by scanning output/, data/, videos/ for highest existing ID + 1
✅ Manual "update CURRENT_PRODUCT_ID" reminder removed from /tiktok and /tiktok analyze

— 2026-06-14 product validation upgrade —
✅ STEP 3B added to /tiktok — mandatory 5-check product validation before tracking IDs, assets, or video generation
✅ Validation checks: page active, affiliate eligible, ships to Israel, purchasable now, no blocking warnings
✅ Auto-reject on any failed check — moves to next candidate automatically; stops run if all 5 candidates fail

— 2026-06-14 STEP 3B validation bug fix (round 1) —
✅ Bug: STEP 3B passed item 1005009207029480 which returns "page not found" when opened manually
✅ Root cause: validation was based on search evidence and redirect presence, not live page content
✅ Fix: STEP 3B now requires WebFetch on the exact product URL — search evidence is no longer sufficient
✅ CHECK 1 now requires product title present in fetched content (not just "page loaded")
✅ CHECK 2 added: price must be present in fetched content
✅ Immediate reject if fetched content contains "page not found", "can not be found", "item is removed", or equivalent
✅ Immediate reject if WebFetch returns only navigation/footer with no product title or price visible

— 2026-06-14 STEP 3B fallback validation (round 2) —
✅ Bug: WebFetch returns footer-only HTML for ALL AliExpress pages (JS-rendered) — both valid and removed listings — making WebFetch-only validation impossible to distinguish live vs dead listings
✅ Fix: STEP 3B now uses a two-path procedure
✅ Path A: WebFetch returns real content → check title + price + no error messages (unchanged from round 1)
✅ Path B: WebFetch returns footer-only (AliExpress JS wall) → run fallback search validation
✅ Fallback rule: search exact item ID / URL; item must appear as a Google-indexed product listing with a title in the snippet
✅ Reject rule: item appearing only in wiki-ssr articles, blog posts, guides, or no results → REJECT (signals removed/invalid listing)
✅ Prefer rule: item confirmed in multiple AliExpress regional domains (.com + .de etc.) = stronger pass signal
✅ CHECK 4 (ships to Israel): confirmed by redirect to he.aliexpress.com; flagged UNCONFIRMED if no Israeli redirect
✅ CHECK 5 (affiliate eligible): flagged UNCONFIRMED when JS-rendered; defaults to eligible for generic categories

— 2026-06-14 critical logic + content QA bugs —
✅ BUG 1 — Final listing metrics mismatch: agent used category-level/research-phase metrics (sales, rating, price) as if they belonged to the specific final URL; the final listing for product 002 showed 1 sold / 2 reviews — failing the 1,000+ sales requirement
✅ BUG 2 — Price consistency: research estimated ~25₪ but final listing shows ₪60.66; estimated price leaked into video overlays, output package, upload package, and WHY CHOSEN without reconciliation against actual URL
✅ BUG 3 — False social proof: videos claimed "1,200 אנשים כבר הזמינו!" when final listing had only 1 sold and 2 reviews; category-level aggregated counts must never be used as overlay social proof
✅ Root cause: STEP 3B validated URL existence only; no step verified the specific listing's metrics; estimated research values carried forward unchecked
✅ Fix: Added STEP 3C — Final Listing Consistency Check between STEP 3B and STEP 4
✅ STEP 3C verifies: sales ≥ 1,000, rating ≥ 4.5★, images ≥ 5 for the SPECIFIC final URL; records FINAL LISTING PRICE and FINAL LISTING SOCIAL PROOF; rejects listing/product if any critical check fails
✅ Fix: Added PRICE RULE and SOCIAL PROOF RULE to STEP 6 — FINAL LISTING PRICE is mandatory for all overlays/captions; social proof must match actual listing (< 1,000 sales → benefit/trust line, never fabricated count)
✅ Fix: Added HEBREW TEXT QUALITY RULE to STEP 6 — natural conversational Hebrew required; mechanical phrasing prohibited
✅ Fix: Added Content QA checks 5–8 to STEP 7 (price consistency, social proof accuracy, Hebrew text quality, output package consistency)
✅ Fix: VIDEO QA PASS now requires both Technical QA (checks 1–4) AND Content QA (checks 5–8)
✅ Product 002 status: LISTING REJECTED — final URL shows 1 sold / 2 reviews, fails 1,000+ sales requirement; must find new listing or new product

— 2026-06-14 emoji root cause fix —
✅ Bug: Emoji (😱 🔥 💬 💪) rendered as broken squares in video text overlays — same issue appeared in both product 001 and 002, meaning prior fix was product-level only
✅ Root cause 1: tiktok.md hook/CTA/JSON templates contained hardcoded emoji — agent copies them verbatim into video-config JSON every run
✅ Root cause 2: generate_videos.py build_text_layer() had no sanitization — Tahoma has no glyphs for non-BMP characters (codepoints > U+FFFF), renders them as broken squares
✅ Fix 1: strip_unsupported_chars() added to generate_videos.py — strips all non-BMP chars (including emoji U+1F000+) before any text reaches Pillow, called at entry point of build_text_layer()
✅ Fix 2: Removed emoji from 4 video-overlay templates in tiktok.md (Variant A hook 😱, Variant C hook 🔥, storyboard CTA cell 💬, JSON config template 💬) — caption templates unchanged (TikTok captions support emoji fine)
✅ Defence-in-depth: generator-level sanitization means future products can never produce broken squares regardless of what the agent writes into video configs

— 2026-06-14 tracking ID upgrade —
✅ Per-variant tracking IDs added — format: product[ID]_A / _B / _C / _D
✅ Upload package format updated — AFFILIATE LINK moved from global header into each variant block
✅ STEP 4 in /tiktok updated — generates 4 tracking IDs, instructs user to create 4 affiliate links
✅ video_results.csv schema updated — 4 new columns: tracking_id, affiliate_clicks, affiliate_sales, affiliate_commission
✅ /tiktok analyze updated — collects optional affiliate data per variant; affiliate_sales override engagement when choosing winner

— 2026-06-14 content rules + pipeline standards + product completions —
✅ GENERAL AUDIENCE COPY RULE added to tiktok.md — all Hebrew copy gender-neutral throughout ("כתבו", "הגיבו", "ואשלח לכם"); no female-only verb forms in any template
✅ PRODUCT NUMBER CONSISTENCY RULE updated — CTAs now variant-level: "[PRODUCT_ID][VARIANT]" format (e.g. "כתבו 003A בתגובות"); shared codes across variants permanently prohibited
✅ REPLY MANAGEMENT RULE added — REPLY REFERENCE TABLE (CTA code → tracking ID → affiliate link) required at top of every upload package
✅ CHECK 9 (Thumbnail QA) added — hook text must be readable in TikTok profile thumbnail crop; first 3–4 words must convey the full message without truncation
✅ CHECK 7 expanded — now covers HEBREW TEXT QUALITY + AUDIENCE: natural conversational Hebrew, gender-neutral language, no mechanical phrasing
✅ FINAL QA CHECKLIST expanded — VIDEO QA PASS now requires 9 checks: Technical (1–4) + Content (5–8) + Thumbnail (9)
✅ Product 002 COMPLETE — Plug Adapter (item 1005010033519251), ₪23, 10,000+ sold; 4 affiliate links assigned (product002_A/B/C/D); READY TO UPLOAD
✅ Product 003 COMPLETE — Mini Bag Sealer (item 1005006860946828), ₪8, 100,000+ sold; 4 affiliate links assigned (product003_A/B/C/D); READY TO UPLOAD
⚠️ Product 004 — Mist Fan — BLOCKED (sales UNCONFIRMED, price research-estimated; videos generated under prior rules; do not upload without manual validation)
⚠️ Product 005 — Fabric Shaver — BLOCKED (sales UNCONFIRMED, rating UNCONFIRMED, price research-estimated; videos generated under prior rules; do not upload without manual validation)

— 2026-06-15 QA architecture audit + full system fixes —
✅ QA RULE 1: SALES UNCONFIRMED = HARD BLOCK — added to STEP 3C FAIL CONDITIONS
✅ QA RULE 2: Unconfirmed price blocks numeric overlays — CHECK 5 rewritten with PRICE CONFIRMATION sub-check
✅ QA RULE 3: Dual UNCONFIRMED escalation — 2+ unconfirmed fields = reject listing
✅ QA RULE 4: Fallback candidate strict validation — all fields must be confirmed; added to STEP 3B + STEP 3C
✅ QA RULE 5 + GATE C: Asset Identity Gate (STEP 8B) added — 5 checks: main image, usable count, anomalous size, sequential numbering, screenshot coverage
✅ QA RULE 6: Screenshot failure = explicit ASSET DEGRADATION WARNING in upload package (no silent PASS)
✅ QA RULE 7: Canonical Product Term established at start of STEP 6; enforced in CHECK 2 (benefit coherence, term consistency) and CHECK 7 (product noun consistency)
✅ QA RULE 8: Minimum commission viability screen — ₪1.50/sale floor added to STEP 1 before shortlist
✅ Pricing table overhauled — preferred range now ₪25–₪65; hard reject below ₪15 and above ₪120; PREFERRED band at ₪40–₪65 (12 pts)
✅ Tie-breaking rule updated — favor higher expected commission/sale, not cheaper price
✅ CONFIRMATION COMPLETENESS EVALUATION added at end of STEP 3C (new STEP 3C gate before STEP 4)
✅ CHECK 2 expanded — canonical term consistency + benefit coherence checks added
✅ CHECK 5 rewritten — price confirmation status checked before currency symbol check
✅ CHECK 7 expanded — product noun consistency check added
✅ CHECK 8 expanded — caption product noun consistency check added
✅ Upload package VALIDATION SUMMARY block added (sales, rating, price, screenshot status at a glance)
✅ Upload package UPLOAD STATUS now a conditional system: PENDING AFFILIATE LINKS / ⚠️ ASSET WARNING / ⚠️ ASSET DEGRADATION WARNING / ❌ BLOCKED
✅ TIKTOK_AGENT_PLAN.md updated — pricing table, step table (STEP 8B added), validation descriptions
✅ tiktok-analyze.md updated — price bands aligned to new tiers; female-gendered CTA example corrected
✅ Products 004 and 005 status corrected to BLOCKED (generated under prior rules; require manual review before upload)

— 2026-06-15 Product 006 attempt 1 —
⚠️ Product 006 run failed after 20+ minutes — no confirmed orders/rating found for car seat gap filler (AliExpress JS wall blocked all fetches; alitools.io returned 404)
✅ Fix: AUTOMATED VALIDATION LIMITS added — 10 searches / 5 fetches / 3 item IDs / 5 min; first limit hit → HVM triggered immediately
✅ Fix: HUMAN VERIFICATION MODE (HVM) added to STEP 3C — user opens URL, provides 4 fields; treated as CONFIRMED
✅ Fix: STEP 0C Product Exclusion Check added

— 2026-06-15 Product 006 attempt 2 —
✅ HVM triggered for item 1005005879520048 (SEAMETAL car seat gap organizer, atmosphere light + USB)
✅ HVM result: 322 sold, 4.6★, ₪63.91, In Stock → HARD BLOCK (322 < 1,000)
⚠️ Alternative listing item 4001293078470 shown to user via HVM → URL non-working (dead listing shown to user)

— 2026-06-16 Validation + Resume Mode —
✅ Bug root cause: item 4001293078470 found only on alitools.io + seametalco.com — no direct aliexpress.com listing result; pipeline incorrectly treated third-party cache as live listing signal
✅ Fix: HVM URL VALIDATION GATE — direct aliexpress.com/item/[ID] result required before any URL shown to user
✅ Fix: LISTING SELECTION PRIORITY in STEP 2 — highest confirmed sales first; features are tie-breakers only
✅ Fix: RESUME MODE (STEP 0A-R) — pipeline checks state/[PRODUCT_ID]-pipeline-state.json on startup; restores shortlist; skips STEP 0/1; STATE FILE hooks at 5 pipeline points
✅ state\ directory added to project structure
✅ TIKTOK_AGENT_PLAN.md + PROJECT_STATUS.md updated
⚠️ state/006-pipeline-state.json NOT YET WRITTEN — must create state\ dir and write file before next run (content in Downloads/tiktok-session-2026-06-16.md)

	— 2026-06-17 Product 007 Complete + Bug Fix + New Learning —
✅ Product 007 APPROVED — מארגן גב המושב עם שולחן מתקפל (Car Seat Back Organizer, item 4001145808790)
✅ ₪39.05 | 4,000+ sold | 5.0★ | Interior Accessories | 9% commission (₪3.51/sale)
✅ Candidate 1 (Wireless Charger) rejected — 3 listings all DEAD via STEP 3A (category heavily delisted)
✅ Candidate 2 (Car Organizer) passed — listing 4001145808790 confirmed via STEP 3A + HVM
✅ Bug fixed in generate_assets.py: Hebrew thousands-separator parsing bug (sold_count "4,000+" → "000+" → 0)
   → Guard added in extract_product_data_from_page(): sold_count_numeric=0 with raw starting "0" → set to None (unconfirmed)
✅ 10 images collected, 3 screenshots, 1 scroll video — manifest QA 5/5 ✅
✅ 4 variants generated (A=Price Shock, B=Curiosity, C=Problem/Solution, D=TikTok Discovery) + RTL audit ✅
✅ Videos: 4/4 generated (1080×1920, H.264, 30fps, 15s) | ffprobe QA 7/7 | human-frame QA 12/12 frames reviewed
✅ Affiliate links generated and filled; upload package complete
⚠️ QA finding: Variants C and D contain AliExpress infographic images (English text baked into photo) as segment backgrounds
   → Not a blocker (CEO approved); future fix: infographic filter in generate_assets.py

📌 NEW LEARNING — WOW MOMENT RULE:
   Future videos should include at least one REAL USAGE MOMENT or WOW MOMENT when suitable product assets exist.
   Examples: before/after, product in use, installation moment, transformation moment, unexpected benefit reveal.
   Strong variants (C and B) demonstrated that showing a problem being SOLVED outperforms pure product description.
   This is a soft guideline — apply during hook and segment generation to improve watch time and engagement.

	— 2026-06-18 Product 008 Complete + Three-Gate QA Architecture Validated —
✅ Product 008 shortlist complete: Candidates 1 (Solar Garden Lights) and 2 (Neck Fan) rejected (no viable live listings)
✅ Candidate 3: Adjustable 360° Phone/Tablet Stand (item 1005006285768946) — ₪40.29, 2,000+ sold, 4.9★ — SELECTED
✅ Videos A/B/C/D generated (1080×1920, 15s each), re-rendered with config v2 after STEP 11B gate caught English contamination

📌 NEW PERMANENT RULE — TIKTOK UI SAFE ZONE:
   generate_videos.py "top-center" position fixed: y_start was 100 (inside 288px danger zone); now y_start=320 (below 15% TikTok UI zone).
   Rule: no critical text in top 15% of frame (top 288px on 1920px). QA at 0s/1s/3s.
   This is a GENERATOR-LEVEL fix — applies to all future products automatically.

📌 NEW PERMANENT RULE — SCREENSHOT EVIDENCE:
   Overlay text must not cover the proof elements the screenshot is meant to show.
   Price screenshot (thin band at y≈836–1084): overlay must use "top-center" — text floats above the strip.
   Rating screenshot (full canvas): overlay must use "bottom" — rating breakdown at top remains visible.
   QA check: extract 4s frame (price) and 11s frame (rating); proof elements must be readable without overlay.
   Added to tiktok.md STORYBOARD defaults and FRAME SAMPLING QA checklist.

📌 NEW PERMANENT RULE — PRODUCT VISIBILITY:
   Text readability alone is not sufficient. Overlay text must not obscure the primary product subject.
   The product must remain visually dominant in every product-image frame.
   Avoid "center" position for benefit segments (6–9s) when product occupies center of image — use "bottom" instead.
   Screenshot frames (price, rating) are exempt — overlay reinforces screenshot data by design.
   QA check: extract 7s frame for all variants; product must be clearly visible and dominant.
   Both rules added to tiktok.md STORYBOARD section and FRAME SAMPLING QA checklist.

✅ Generator fix (2026-06-18) — 4 permanent improvements to generate_videos.py for Product 008:
   1. Screenshot composition: added `or iw > ih * 2` to scale-to-fill path in make_frame() — prevents
      extreme-landscape screenshots (price.png, 535×123, 4.35:1) from letterboxing as a thin gray strip.
   2. Asset override: added "asset" key support per segment in video-config.json — bypasses auto-selection
      for specific segments (zero side-effects on existing products; graceful fallback if file missing).
   3. Bottom safe zone: fixed y_start from 1820 to 1520 in build_text_layer() bottom branch —
      bottom text now ends at y=1520 (400px above frame bottom), safely above TikTok UI controls.
   4. Glyph integrity: added REPLACEMENTS = {'★': '', '☆': ''} to strip_unsupported_chars() —
      prevents ★ (U+2605 BMP, not caught by prior non-BMP strip) from rendering as □ in Tahoma.
   Config: data/008-video-config.json written — ★ replaced with "כוכבים" in A/B/C segments;
   asset overrides set for price segment (seg 1) in all 4 variants using clean detail images.

📌 NEW PERMANENT ARCHITECTURE — STEP 11B VISUAL COMPOSITION QA (2026-06-18):
   New pipeline gate running after STEP 10 (technical QA) and before STEP 11 (save output file).
   Extracts 8 frames per variant (0s, 1s, 3s, 5s, 7s, 9s, 11s, 14s) via ffmpeg and evaluates each on
   6 criteria: Hook Power, Visual Composition, Product Dominance, Screenshot Evidence Quality,
   English Contamination, TikTok Native Feel. Outputs PASS/WARNING/FAIL per frame and per variant.
   FAIL = upload BLOCKED + config/generator fix + re-render required.
   WARNING = CEO review required before upload.
   UPLOAD STATUS now requires STEP 11B 4/4 PASS for a clean PENDING AFFILIATE LINKS ✅ result.
   What this gate would have caught in Product 008 (pre-fix render):
   - Frame 5s (price segment): price.png as a 248px strip on 1920px canvas → COMPOSITION FAIL
   - Frame 9–11s (social proof): "4.9★" text rendering as "4.9□" → GLYPH FAIL
   - Frame 0s/14s: potential English infographic from AliExpress detail images → English Contamination WARNING
   All three issues were corrected in the generator + config before re-render; STEP 11B would have
   blocked upload automatically rather than requiring a separate human QA session.
   Added to tiktok.md (full step spec), TIKTOK_AGENT_PLAN.md (step table), PROJECT_STATUS.md (this entry).

📌 NEW PERMANENT ARCHITECTURE — STEP 11C MOTION + CONVERSION QA (2026-06-18):
   New pipeline gate running after STEP 11B (Visual Composition QA) and before STEP 11 (save output file).
   Evaluates the full 15-second video as a continuous TikTok viewing experience — not just sampled frames.
   12 criteria: First-Second Clarity, Scroll-Stopping Power, Hook-to-Product Match, Story Flow, Text Timing,
   Transition Feel, Product Clarity, Benefit Clarity, Trust/Proof Clarity, CTA Strength, Mobile-View Realism,
   Overall Upload Judgment.
   Outputs per variant: PASS/WARNING/FAIL per criterion + 7 scores (Hook, Clarity, Flow, TikTok-native, CTA, Trust,
   Overall 1–10) + upload priority ranking #1–#4 + final recommendation (Upload / Upload with warning / Do not upload).
   FAIL or WARNING with overall score < 6 = upload BLOCKED. WARNING with score ≥ 6 = CEO review required.
   Uses the 8 STEP 11B QA frames already extracted — no new frame extraction required.
   What this gate catches that STEP 11B misses: weak hooks that are frame-clean but not scroll-stopping;
   disjointed story flow; text too long for its segment duration; CTAs with wrong variant codes; videos that
   look technically fine but would not perform on TikTok.
   Added to tiktok.md (full step spec), TIKTOK_AGENT_PLAN.md (step table), PROJECT_STATUS.md (this entry).

📌 NEW PERMANENT ARCHITECTURE — PRE-UPLOAD HUMAN REVIEW AGENT (2026-06-18):
   Mandatory final gate triggered when user declares readiness to upload (after affiliate links generated).
   No product may be published on TikTok without an APPROVED TO UPLOAD verdict from this agent.
   12 checks: affiliate links complete (BLOCKED if any missing), CTA/link match (BLOCKED if mismatch),
   caption quality, hashtag relevance, STEP 11B status, STEP 11C status (BLOCKED if not run or any FAIL),
   upload order, video files present (BLOCKED if missing), product data accuracy, upload timing advisory,
   CEO upload judgment, completeness.
   Verdict: APPROVED TO UPLOAD ✅ / BLOCKED ❌ / NEEDS CEO REVIEW ⚠️.
   APPROVED TO UPLOAD is the only verdict that unambiguously permits publishing.
   What this gate catches that QA gates miss: unfilled affiliate links; CTA codes that don't match the
   REPLY REFERENCE TABLE; caption errors that survived automated checks; missing video files;
   administrative gaps that would break attribution or affiliate delivery after upload.
   Trigger: user types "ready to upload Product [ID]" — agent reads upload package and runs all 12 checks.
   Added to tiktok.md (full spec), TIKTOK_AGENT_PLAN.md (step table + You Do rows), PROJECT_STATUS.md (this entry).

📌 STEP 11C AUDIT FINDING (2026-06-18):
   Original name "Motion + Conversion QA" was inaccurate. Renamed to "Frame Sequence Visual QA."
   What STEP 11C actually does: reads 8 static frames from STEP 11B in sequence; evaluates story logic,
   composition quality, and conversion criteria against those 8 stills. Does NOT open the MP4. Does NOT
   assess timing, pacing, transition smoothness, or hook strength in real playback.
   What motion review actually requires: watching the MP4 play at normal speed on a phone screen.
   Gap: frame analysis misses text that changes too fast to read in motion; hooks that are frame-clean
   but fail to stop a real scroll; transitions that feel jarring at normal speed but look fine as two stills.

📌 NEW PERMANENT ARCHITECTURE — STEP 11D FULL MOTION VIDEO REVIEW (2026-06-18, CEO OVERRIDE):
   Automated agent-executed gate (CEO Override — replaces human-conducted design).
   Runs after STEP 11C (Frame Sequence Visual QA), before STEP 11 (save output).
   Method: ffmpeg extracts 1fps frames (15 frames per variant) from the actual MP4 file.
   Agent reads all 60 frames via multimodal image analysis. 12 criteria evaluated.
   6 scores per variant: Hook / Clarity / Flow / TikTok-Native / CTA / Overall (1-10).
   Verdict: PASS / WARNING (CEO review) / FAIL (upload BLOCKED).
   Honest scope: strongest automated review possible. Cannot replicate real-time pacing feel.
   Human phone review available as optional supplement for WARNINGs on criteria 1, 6, 7.
   Gate 5 of 5. Full five-gate architecture:
   Gate 1 Technical QA | Gate 2 Content QA | Gate 3 Visual Composition QA (STEP 11B) |
   Gate 4 Frame Sequence Visual QA (STEP 11C renamed) | Gate 5 Full Motion Video Review (STEP 11D automated).
   Added to tiktok.md (full spec), TIKTOK_AGENT_PLAN.md (step table), PROJECT_STATUS.md (this entry).

	— 2026-06-18 Product 008 — APPROVED TO UPLOAD —
✅ Product 008 APPROVED — מעמד שולחני מסתובב 360° (item 1005006285768946) | ₪40.29 | 2,000+ sold | 4.9★ | 9% commission
✅ Approved date: 2026-06-18
✅ Gate 1 — Technical QA: PASS — 4/4 variants (1080×1920, H.264, 30fps, 15s, 1.9–2.9MB)
✅ Gate 2 — Content QA: PASS — price ₪40.29 confirmed, social proof 2,000+/4.9 כוכבים confirmed, Hebrew text natural, glyph integrity verified
✅ Gate 3 — Visual Composition QA (STEP 11B): WARNING → CEO APPROVED (2026-06-18)
   WARNING details: 11s by-design (product small in AliExpress rating screenshot — structural to all products);
   Variant A 7s composite image (002_detail.jpg with orange feature callout insets) — accepted by CEO
✅ Gate 4 — Frame Sequence Visual QA (STEP 11C): WARNING → CEO APPROVED (2026-06-18)
   Scores: B=9/10, C=8/10, D=8/10, A=7/10 | STEP 11C order: B→C→D→A (revised to B→D→C→A by STEP 11D)
   WARNING details: rating screenshot trust criterion (by-design, structural to all products);
   studio-render scroll-stopping power for A/C/D (creative characteristic, not a defect) — accepted by CEO
✅ All 4 generator-level fixes verified in production render:
   1. Screenshot composition — price.png now scale-to-fills frame (no more thin gray strip)
   2. Asset override — "asset" key in config bypasses auto-selection per segment
   3. Bottom safe zone — text ends at y=1520 (above TikTok UI controls)
   4. Glyph integrity — ★ stripped from Tahoma; "כוכבים" used instead

📌 MILESTONE: Product 008 is the first product to expose the STEP 11C audit gap and drive the five-gate architecture.
   Gate 1 — Technical QA (ffprobe: resolution, codec, duration, size) ✅ PASS
   Gate 2 — Content QA (price, social proof, Hebrew text, output package consistency) ✅ PASS
   Gate 3 — Visual Composition QA — STEP 11B (8 frames × 4 variants × 6 criteria) ✅ CEO APPROVED
   Gate 4 — Frame Sequence Visual QA — STEP 11C renamed (12 criteria, 7 scores, upload priority ranking) ✅ CEO APPROVED
   Gate 5 — Full Motion Video Review — STEP 11D automated (CEO Override 2026-06-18) ✅ CEO APPROVED
      B=PASS 9/10 | D=PASS 9/10 | C=WARNING→APPROVED 8/10 | A=WARNING→APPROVED 7/10
      Revised upload order: B→D→C→A (D promoted from 3rd to 2nd based on TikTok-native 9/10)
   Pre-Upload Human Review Agent — APPROVED TO UPLOAD ✅ (12/12 checks pass)

📌 ROOT-CAUSE FINDINGS THAT LED TO STEP 11B:
   1. English contamination in hook/CTA assets — 001_main.jpg (AliExpress listing main image) contained
      baked-in English labels ("Tablet Holder", "360°Free Rotation"); auto-selected for hook and CTA frames
      in all 4 variants; not detectable by ffprobe Technical QA; only caught by visual frame review
   2. Visual composition failures not detectable by Technical QA alone — thin-strip screenshots (price.png
      at 13% frame coverage), glyph corruption (★→□), and English-contaminated images all produced valid
      MP4 files that passed ffprobe; STEP 11B added to catch composition-level failures before upload

📋 Status: ✅ APPROVED TO UPLOAD — all 5 gates complete, all WARNINGs CEO-approved (2026-06-18)
📋 Affiliate links: FILLED ✅ (TikTok008A/B/C/D in REPLY REFERENCE TABLE)
📋 Gate 3 (STEP 11B Visual Composition QA): CEO APPROVED 2026-06-18 ✅
📋 Gate 4 (STEP 11C Frame Sequence QA): CEO APPROVED 2026-06-18 ✅
📋 Gate 5 (STEP 11D Full Motion Video Review): CEO APPROVED 2026-06-18 ✅
   B=PASS (9/10) ✅ | D=PASS (9/10) ✅ | C=WARNING→APPROVED (8/10) ✅ | A=WARNING→APPROVED (7/10) ✅
   New finding: C CTA frame 14 yellow text (minor — code correct, readable) — accepted
   Upload order: B→D→C→A (D promoted from 3rd based on TikTok-native 9/10)
📋 Pre-Upload Review Agent: APPROVED TO UPLOAD ✅ (all 12 checks pass)
📋 Next: Upload B→D→C→A at 19:00–21:00 Israel time. Add trending sound per video in TikTok editor.

	— 2026-06-18 STEP 11D v2 — Enhanced Automated MP4 Review —
📌 NEW PERMANENT ARCHITECTURE — STEP 11D v2 FULL MOTION VIDEO REVIEW (2026-06-18, CEO PRIORITY):
   Upgrade from v1 (1fps, 12 criteria, 6 scores) to v2 (3fps, 14 criteria, 10 scores, remediation output).
   Key v2 changes: 45 frames/video (3× coverage), dead-frame detection (5+ consecutive = dead moment),
   CTA exposure measurement (≥5/6 frames required for PASS), TikTok mobile simulation (safe content zone),
   product dominance full-timeline scoring, stricter TikTok-native penalty model (−1/violation, max −5),
   mandatory REMEDIATION OUTPUT block for every WARNING/FAIL finding, 10-category scoring.
   Product 008 v2 result: B=WARNING 9/10 | D=WARNING 8/10 | C=WARNING 7/10 | A=WARNING 7/10
   v2 new findings over v1: all 4 variants — proof screenshot (rating.png) shows competing prices ₪20–₪57
   in similar-products carousel (12 proof frames at 3fps vs 1 frame at 1fps reveals this clearly);
   Variant C CTA uses lifestyle image; Variant D has silver→black stand color inconsistency between segments.
   All WARNINGs CEO-approved (carry-forward from v1 approvals). Upload order unchanged: B→D→C→A.
   Priority fix (non-blocking): re-capture rating.png to crop out similar-products carousel.
   tiktok.md Gate 5 updated to reference STEP 11D v2 spec.
   Added to tiktok.md (full v2 spec replacing v1), project memory (project_step11d_automated.md updated).

	— 2026-06-18 Performance Learning Layer — CEO PRIORITY —
📌 NEW ARCHITECTURE — PERFORMANCE LEARNING LAYER (2026-06-18):
   Built before Product 009. Architecture: /tiktok collect → video_results.csv v2 → upgraded /tiktok analyze.

   NEW COMMAND: /tiktok collect (tiktok-collect.md)
   Purpose: Performance Data Collector Agent — data entry only, no analysis.
   Inputs: TikTok Analytics stats per uploaded variant (views, likes, comments, saves + enrichment metrics).
   Enrichment metrics: shares, average_watch_time, watched_full_video_rate, first_2_second_retention,
   cta_code_comments, affiliate data.
   Behavior: normalizes, validates, computes derived fields, appends to video_results.csv v2.
   Schema migration: v1 (21 cols) → v2 (33 cols); existing rows get blanks in columns 22–33.
   Key new field: first_2_second_retention (% watching at 2s mark) — CRITICAL for retention diagnosis.
   Overwrite protection: never overwrites without explicit user confirmation.

   CSV SCHEMA: upgraded to v2 (33 columns — 21 original + 12 new: hook_text, shares, average_watch_time,
   retention_rate, watched_full_video_rate, first_2_second_retention, cta_code_comments,
   engagement_rate, save_rate, comment_rate, share_rate, cta_comment_rate).

   UPGRADED: /tiktok analyze (tiktok-analyze.md)
   5 new modules added (C.F–C.J):
   C.F — First 2-Second / Retention Diagnosis (conditional — runs when retention data exists)
          8 root causes, each classified LIKELY/POSSIBLE/UNLIKELY with specific fix
   C.G — Product Type Analysis (scroll-stop, CTA activation, engagement, affiliate classification)
          SCALE NOW / CONTINUE TESTING / PAUSE SIMILAR / AVOID / NOT ENOUGH DATA
   C.H — Variant Root Cause Analysis (winner/underperformer classification + root cause decision tree)
   C.I — Cross-Product Analysis (strongest/weakest product, category, hook type ranking)
   C.J — CTA Effectiveness Analysis (CTA comment rate, funnel drop-off, weakest link)
   NEW STEP E: Product 009 Decision Layer (PROCEED / PAUSE / CHANGE STRATEGY)
          When PROCEED: outputs concrete Product 009 Creative Brief (category, hook, first-frame, pacing, CTA)

   PRODUCT 009 STATUS: PAUSED — pending performance data from Products 001, 007, 008.
   Reason: early evidence of viewer retention collapse around first 2 seconds; root cause unknown.
   Required data: first_2_second_retention for Products 001, 007, 008 via /tiktok collect.
   Required sequence: upload 007/008 → /tiktok collect → /tiktok analyze → check Step E decision → /tiktok.

	— 2026-06-19 CEO Final Audit + Automated Collector Scripts —

📌 CEO FINAL AUDIT — PERFORMANCE LEARNING LOOP (2026-06-19):
   Full audit of: /tiktok collect v2 → video_results.csv → /tiktok analyze → learning_report.json → STEP 0
   Scope: Products 001, 002, 007, 008.

✅ BUG 1 FIXED — tiktok-analyze.md Phase 1 (CRITICAL):
   Phase 1 asked for manual data input even after /tiktok collect v2 had already written video_results.csv.
   Fix: Added CSV-FIRST CHECK at top of Phase 1.
   If rows exist for the requested products → skip Phase 1 entirely, proceed to Phase 2 using CSV rows.
   If no rows exist → prompt to run /tiktok collect first; manual entry only if user explicitly requests it.

✅ BUG 2 FIXED — tiktok-analyze.md STEP A (CRITICAL):
   STEP A wrote a v1 CSV header (21 columns) into a v2 file (33 columns) when doing fallback write.
   Fix: Added SKIP CHECK at top of STEP A.
   If matching rows already exist from /tiktok collect v2 → skip entirely, do not append duplicate rows.
   When fallback write IS needed → write v2 header (33 columns), not v1 (21 columns).

✅ BUG 3 FIXED — tiktok-collect.md field 18 tracking_id example (LOW):
   Example showed "TikTok007A" but actual format is "product007_A".
   Fix: Updated example in schema and COLLECTOR → ANALYZER FIELD MAP comment.

📌 AUTOMATED TIKTOK ANALYTICS COLLECTOR — BUILT 2026-06-19:
   Three new scripts built. Syntax-verified. Product detection smoke-tested. NOT tested against live TikTok.

   scripts/tiktok_session_login.py (120 lines):
   One-time login helper. Opens visible Chrome. User logs in manually (any method, 2FA OK).
   Saves session to data/tiktok-session.json (gitignored). Run once, valid ~30 days.

   scripts/tiktok_analytics_collect.py (744 lines):
   Main collector. Auto-detects ALL products from data/*-video-config.json.
   Detected: 001/002/003/004/005/007/008 (28 variants total).
   Matches videos on TikTok by CTA code (007A, 008B, etc.) via text-based Playwright selector.
   Intercepts XHR analytics responses — extracts views, likes, comments, saves, shares,
   average_watch_time, retention_rate, watched_full_video_rate, first_2_second_retention.
   Prompts manually for 4 fields: cta_code_comments + 3 affiliate fields.
   Writes/merges data/video_results.csv (33-column v2). No duplicate rows. NOT_FOUND for missing variants.
   Saves screenshots to data/tiktok-analytics/product[NNN]/ per variant.
   Usage: python scripts/tiktok_analytics_collect.py
          python scripts/tiktok_analytics_collect.py --product-id 007
          python scripts/tiktok_analytics_collect.py --update

   scripts/tiktok_collect_qa.py (518 lines):
   Standalone 5-check PASS/WARN/FAIL QA suite. No Playwright required.
   Check 1: Session file — cookies present, TikTok domain, not expired
   Check 2: Video matching — all expected variants in CSV, none NOT_FOUND
   Check 3: Data extraction — views/saves in range, first_2_second_retention 0–1
   Check 4: CSV schema — exact 33-column v2 header, type validation
   Check 5: Analyzer handoff — all required fields populated on CONFIRMED/PENDING rows
   Usage: python scripts/tiktok_collect_qa.py
          python scripts/tiktok_collect_qa.py --product-id 007 --strict

📌 CEO CHECKPOINT AUDIT RESULT (2026-06-19):
   CURRENT SYSTEM STATUS: FAIL
   Products audited: 001, 002, 007, 008 — ALL FAIL (same systemic blockers)

   BLOCKER 1 — data/tiktok-session.json: MISSING. Login script was not completed.
               Fix: Run tiktok_session_login.py to completion. Time: 5 min.
   BLOCKER 2 — XHR analytics capture: UNTESTED against live TikTok.
               URL patterns (retain_user_ratio, /api/item/, etc.) are assumed, not confirmed.
               Risk: all 9 metrics write as empty strings if patterns don't match.
               Fix: Run collector, inspect captured URLs, adjust patterns. Time: 30–120 min.
   BLOCKER 3 — Video matching by CTA code: UNTESTED.
               page.locator("text=007A") may not match TikTok's Creator Center DOM.
               Fix: Test, inspect DOM, adjust selector. Time: 30–60 min.
   BLOCKER 4 — first_2_second_retention: HIGH RISK.
               TikTok renders retention curve as HTML Canvas. XHR source unconfirmed.
               If canvas-only: this field is always empty; analyzer cannot diagnose 2-sec drop-off.
               Fix: Test. If canvas-only, requires separate extraction strategy. Time: 60–180 min.

   METRIC COLLECTION STATUS (all 9 metrics): UNCONFIRMED — code written, not tested.
   data/video_results.csv: MISSING (not yet created).
   data/learning_report.json: MISSING (analyzer not yet run).
   Product 009: BLOCKED until analyzer outputs PROCEED with real data.

	— 2026-06-19 /tiktok collect v2 + Full Learning Feedback Loop —
📌 /tiktok collect UPGRADED TO v2 (2026-06-19):
   Collection method changed from manual-entry-only to screenshot-based extraction.
   User saves screenshots + optional CSV export to data/tiktok-analytics/[PRODUCT_ID]/.
   Agent reads files with multimodal vision and text parsing — no typing required.
   Manual input reduced to 4 fields maximum: cta_code_comments + 3 affiliate fields.
   29 of 33 CSV fields: auto-populated, screenshot-extracted, or computed.
   New STEP 7 — HANDOFF AUDIT (8 checks): formal pre-write confirmation that all analyzer fields are present, correctly named, not zero-instead-of-blank, and that first_2_second_retention status is reported.
   New STEP 9 — POST-WRITE SUMMARY + ANALYZE TRIGGER: prompts /tiktok analyze immediately after writing.
   New COLLECTOR → ANALYZER FIELD MAP: every analyzer-required field traced to its v2 collection source.
   Safety: no TikTok credentials, no browser automation, no API calls, zero account ban risk.

📌 FULL LEARNING FEEDBACK LOOP CLOSED (2026-06-19):
   Gap fixed: analyzer learning was displayed in chat only; /tiktok STEP 0 had no way to read it.
   Fix 1 — /tiktok analyze STEP F (NEW): writes data/learning_report.json after Step E.
     Contains: decision (PROCEED/PAUSE/CHANGE STRATEGY), best hook/category/price/CTA from CONFIRMED data,
     retention diagnosis, Product 009 Creative Brief (hook type, category, first-frame requirement,
     pacing, CTA adjustment, price target, product types to avoid).
   Fix 2 — /tiktok STEP 0 SUPPLEMENT (NEW): reads data/learning_report.json at startup.
     If PAUSE: stops the run immediately with reason.
     If CHANGE STRATEGY: stops the run immediately with issue.
     If PROCEED: overrides all CSV-computed insights with analyzer recommendations; applies Creative Brief
     constraints to STEP 1 scoring (+3 bonus for recommended category, −5 penalty for types to avoid);
     assigns analyzer-recommended hook to Variant A in STEP 6; carries first_frame_requirement to STEP 6 storyboard.
   Result: collected TikTok data now directly changes every future /tiktok product selection, hook assignment,
   price targeting, and first-frame storyboard requirement.

	— 2026-06-21 First Live Collector Test —

📌 FIRST LIVE COLLECTOR RUN (2026-06-21):
   Scope: Products 002, 003, 007, 008 — 16 variants.
   Result: 8/16 found. 0/16 metrics extracted.

✅ LOGIN SCRIPT FIXED (tiktok_session_login.py):
   Bug 1: input() caused EOFError when run from Claude Code (non-interactive stdin).
   Bug 2: URL-polling fired a false positive immediately — URL contained "creator-center" before
          TikTok JS could redirect to login page. Saved unauthenticated session (3 cookies).
   Fix: Cookie-based auth detection. Polls context.cookies() every 5s for sessionid/sid_guard/uid_tt.
        Only fires when real auth cookies appear. Session now saves 73 cookies with full auth.

✅ COLLECTOR STDIN BLOCKING FIXED (tiktok_analytics_collect.py):
   Bug: prompt_manual_fields() called input() for 4 fields — blocked in non-interactive mode.
   Fix: prompt_manual_fields() now returns blank strings unconditionally. No prompting.
        Manual queue block removed. All optional fields (cta_code_comments, affiliate data) = blank.

✅ BARE-CODE MATCHING ADDED (tiktok_analytics_collect.py):
   Product 002 CTA: "כתבי 002 בתגובות" — no variant letter suffix (pre-June-14 product).
   Fix: detect_all_products() now detects bare codes via regex; adds bare_index (A=0, B=1, C=2, D=3).
        scroll_and_find_video() has new skip_count parameter for bare-code products.
        002A found correctly (skip_count=0 fast path). 002B/C/D still NOT FOUND (skip path bug, see below).

✅ SCROLL TIMING INCREASED: 0.7s → 2.0s between scrolls.

❌ OPEN BLOCKER A — 002B/C/D skip logic broken:
   el.evaluate() in skip path likely throws on stale/restricted elements → exception silently caught →
   skipped counter never increments → target never found.
   Additional issue: page.locator("text=002").all() returns multiple DOM elements per video card
   (card div + caption div + text span), each at different Y positions, inflating the skip counter.
   Fix needed: replace el.evaluate() with el.bounding_box()["y"] + page.evaluate("() => window.scrollY").
   Add height filter: skip elements where bbox["height"] > 100px (container divs).
   File: tiktok_analytics_collect.py → scroll_and_find_video() skip path.

❌ OPEN BLOCKER B — 003A/B/C/D NOT FOUND:
   Captions are correct (003A/B/C/D confirmed in upload package). 2.0s timing had no effect.
   Root cause unknown. Hypotheses: (1) TikTok content tab date filter excludes June 14 videos,
   (2) pagination limit reached before 003 videos, (3) 003 videos not in published state.
   Fix needed: open browser manually while collector runs, observe what happens at scroll 10–20.
   Also: confirm 003 videos are published (not draft/private) in TikTok Creator Center.

❌ OPEN BLOCKER C — 007C NOT FOUND (user action required):
   007A/B/D all found correctly. 007C caption likely typed without "007C" during manual upload.
   Fix: open TikTok Creator Center → find 007C video → verify caption → edit if missing.
   No code fix needed.

❌ OPEN BLOCKER D — XHR capture returns no data:
   All 8 found videos show views=-, 2s_ret=-. ANALYTICS_URL_FRAGMENTS not matching real endpoints.
   Fix: open TikTok video analytics in browser with DevTools Network tab open.
   Record actual XHR/fetch URL patterns that fire. Update ANALYTICS_URL_FRAGMENTS in collector.

   Current ANALYTICS_URL_FRAGMENTS (lines 61–69, unconfirmed):
   "/api/item/", "item_id", "retain_user", "video_analytics", "creator/analytics",
   "video_detail", "play_data"

📋 CSV status: data/video_results.csv written — 16 rows, 33-col v2 schema ✅, all metrics blank.
📋 data/learning_report.json: MISSING — analyzer not yet run.
📋 Product 009: BLOCKED — requires analyzer PROCEED output with real data.

	— 2026-06-17 TODO — Trend Source Audit —
⚠️ RISK: STEP 1 shortlist may be drifting from TikTok trend discovery toward AliExpress bestseller discovery
📋 After uploading Product 007: audit STEP 1 trend discovery across all past products
📋 Audit must record per candidate: TikTok search terms used, number of TikTok videos found, comment themes, trend evidence sources, final scoring breakdown
📋 Goal: Ensure the system is TikTok-first — AliExpress confirms demand, it does not discover trends

	— 2026-06-16 Trend Discovery Audit (TODO — after Product 006 completes) —
⚠️ RISK: STEP 1 shortlist may be drifting from TikTok trend discovery toward AliExpress bestseller discovery
⚠️ Observation: Product 006 shortlist appears strongly driven by AliExpress bestseller data and commission categories; TikTok evidence may be secondary in practice
📋 TODO: After Product 006 completes, audit STEP 1 trend discovery across all past products
📋 Audit must record per candidate: TikTok search terms used, number of TikTok videos found, common comment themes, trend evidence source(s), AliExpress evidence source(s), final scoring breakdown
📋 Goal: Ensure the system is TikTok-first — AliExpress confirms demand, it does not discover trends

	— 2026-06-16 Product 006 Post-Mortem + Architecture Decision —
❌ Product 006 FAILED — all 5 candidates rejected; no listing passed liveness validation
❌ Experimental Tier 2C (1-domain rule) REVERTED — item 1005006288564334 (de.aliexpress.com) passed but user confirmed dead page
📋 POST-MORTEM FINDING 1: ALL Google-index-based signals are unreliable — stale cache affects main domain AND regional domains equally
📋 POST-MORTEM FINDING 2: Tier 2A (sold count in snippet) and Tier 2B (Google Shopping) were unavailable for every listing tested
📋 POST-MORTEM FINDING 3: Tier 2C (regional domain) proved unreliable — regional domain indexing is stale cache just like .com
📋 POST-MORTEM FINDING 4: Only reliable liveness signal is rendering the actual page (Playwright or user HVM)
📋 POST-MORTEM FINDING 5: HVM is 100% reliable but fires too late — after 10+ wasted WebSearch calls per listing
✅ Architecture decision: Playwright-first validation (STEP 3A) — IMPLEMENTED 2026-06-16
✅ generate_assets.py --check-only: renders page via headless Chromium; detects dead pages; extracts price/sold/rating from DOM
✅ Phase 2 validated: DEAD ✅ (item 1005006288564334 → DEAD in 12.8s) | LIVE ✅ (item 1005006860946828 → sold 100,000+, rating 4.9★)
✅ Phase 3 complete: STEP 3A integrated into tiktok.md; STEP 3B demoted to fallback-only; Tier 2 gate marked REPLACED
✅ Tier 2 gate in tiktok.md: marked REPLACED by STEP 3A (no longer pending)
```

---

## Completed Architecture Decisions

| Decision | Choice | Reason |
|---|---|---|
| Video output | 4 silent MP4 files per run | No voiceover, no AI video, no CapCut |
| Final footage source | AliExpress product images + page screenshots + scroll capture | Unique assets, no third-party review footage |
| Review videos | Research reference only — not downloaded, not used as footage | Avoid copyright issues |
| Aspect ratio handling | Scale-to-fill with blurred darkened background | Handles 1:1 images on 9:16 canvas cleanly |
| Hebrew text | python-bidi BiDi reordering + Pillow draw + 8-direction outline | Most reliable RTL approach |
| Image animation | Ken Burns (subtle zoom/pan per variant × segment) | Makes still-image videos feel dynamic |
| Transitions | Hard cuts only | Standard for high-performing TikTok product videos |
| QA | Pre-gen (9 checks, exit fast) + post-gen (10 checks, retry up to 3×) | Catch errors before upload |
| Retry logic | 3 retries per failed check → FAILED — REQUIRES HUMAN REVIEW | Automated recovery with human escalation |
| Pass threshold | 4/4 = exit 0, 3/4 = exit 1, <3 = exit 2 FAILED | 3 uploadable variants is acceptable for MVP |
| Interface contract | `data/[PRODUCT_ID]-video-config.json` | Agent writes it; scripts read it |
| No TikTok auto-upload | Manual upload always | TikTok detects bots and bans accounts |
| Tools | Python + FFmpeg + MoviePy + Playwright + Pillow + python-bidi | Free, local, no paid APIs |

---

## Completed Files

| File | Status | Description |
|---|---|---|
| `TIKTOK_AGENT_PLAN.md` | ✅ Approved | Full project plan. Updated to reflect MP4 output, new folders, new flow, no screen recording. |
| `.claude/commands/tiktok.md` | ✅ Approved | Morning agent prompt. Steps 0–12. STEP 11D v2 (3fps, 14 criteria, remediation output). |
| `.claude/commands/tiktok-analyze.md` | ✅ Approved | Evening analyzer. Phase 2 + 5 new modules (C.F–C.J) + Step E Product 009 Decision Layer. |
| `.claude/commands/tiktok-collect.md` | ✅ Approved | Performance Data Collector Agent. v2: screenshot-based extraction. Bugs 1–3 patched 2026-06-19. |
| `scripts/tiktok_session_login.py` | ✅ Written — NOT YET RUN | One-time login. Opens Chrome, saves data/tiktok-session.json. Run once per ~30 days. |
| `scripts/tiktok_analytics_collect.py` | ✅ Written — NOT YET TESTED | Auto-collector. 28 variants / 7 products. XHR capture + CSV write. Test tomorrow. |
| `scripts/tiktok_collect_qa.py` | ✅ Written — NOT YET TESTED | 5-check PASS/FAIL QA suite. Run after collector. |
| `scripts/generate_assets_spec.md` | ✅ Approved | Complete spec for asset collection script. |
| `scripts/generate_videos_spec.md` | ✅ Approved | Complete spec for video generator script. |

---

## Approved Specifications

### generate_assets_spec.md
**Purpose:** Collect product assets from AliExpress using Playwright.  
**Input:** `--product-id`, `--url`  
**Output:** `assets/[PRODUCT_ID]/images/`, `screenshots/`, `scroll/`, `manifest.json`  
**Key rules:**
- Min 5, max 12 product images downloaded
- 4 named screenshots: `main.png`, `price.png`, `rating.png`, `review1.png`/`review2.png`
- Scroll video via ffmpeg frames-to-mp4 (fallback: PNG frames if ffmpeg missing)
- manifest.json: 13-field schema with `asset_type` enum of 7 values
- 6 QA checks, 3-retry each, exit codes 0/1/2

### generate_videos_spec.md
**Purpose:** Compose 4 silent 9:16 MP4 files from assets + text config.  
**Input:** `data/[PRODUCT_ID]-video-config.json`, `assets/[PRODUCT_ID]/manifest.json`  
**Output:** `videos/[YYYY-MM-DD]-product-[PRODUCT_ID]-A/B/C/D.mp4`  
**Key rules:**
- 1080×1920, H.264, yuv420p, 30fps, no audio, 13–17s, CRF 23
- 5 segments per variant with asset priority tables
- `variant_offset` ensures each variant (A/B/C/D) uses different detail image → visual differentiation
- Hebrew BiDi pipeline: `python-bidi get_display()` → word-wrap → Pillow outline → Pillow draw → MoviePy composite
- Font search order: 6 candidates, verified by rendering `ש`
- Ken Burns: 16-cell motion table (4 variants × 5 segments × unique zoom/pan)
- 9 pre-gen checks (exit fast) + 10 post-gen ffprobe checks (retry 3×)

---

## MVP Constraints (do not work around these)

| Constraint | Rule |
|---|---|
| Voiceover | ❌ Not in MVP |
| AI video generation | ❌ Not in MVP |
| CapCut automation | ❌ Not in MVP |
| TikTok auto-upload | ❌ Never — TikTok bans bot accounts |
| Review footage as video content | ❌ Never — research reference only |
| Silent MP4 output | ✅ Required |
| AliExpress assets only | ✅ Required for final video footage |
| Hebrew text + RTL | ✅ Required — all overlays in Hebrew |
| 4 variants per run | ✅ Required |

---

## Folder Structure (target state)

```
C:\Automation\TikTok\
├── TIKTOK_AGENT_PLAN.md          ✅
├── PROJECT_STATUS.md             ✅ (this file)
├── output\                       ✅ (exists — daily MD packages)
├── analysis\                     ✅ (exists — evening analysis files)
├── data\                         ✅ (exists — video_results.csv + video-config JSON)
├── state\                        📁 create before Product 006 resume (see next action above)
├── assets\                       📁 create before first run
│   └── [product-id]\
│       ├── images\
│       ├── screenshots\
│       ├── scroll\
│       └── manifest.json
├── videos\                       📁 create before first run
├── qa\                           📁 create before first run
├── scripts\                      📁 create before first run
│   ├── generate_assets_spec.md   ✅
│   ├── generate_videos_spec.md   ✅
│   ├── generate_assets.py        ✅ implemented + tested
│   └── generate_videos.py        ✅ implemented
└── .claude\
    └── commands\
        ├── tiktok.md             ✅
        └── tiktok-analyze.md     ✅
```

---

## Implementation Tasks — All Complete

All tasks complete as of 2026-06-11. The end-to-end `/tiktok` pipeline has been operational since product 001.

| # | Task | Status |
|---|---|---|
| 1 | Implement `generate_assets.py` | ✅ Complete (2026-06-11) |
| 2 | Test asset collection on a real AliExpress product URL | ✅ Complete (2026-06-11) |
| 3 | Implement `generate_videos.py` | ✅ Complete (2026-06-11) |
| 4 | Test video generation end-to-end | ✅ Complete (2026-06-11) |
| 5 | Run full `/tiktok` pipeline test (all 12 steps) | ✅ Complete (2026-06-11, product 001) |
| 6 | Update `TIKTOK_AGENT_PLAN.md` script status table | ✅ Complete (2026-06-11) |

---

## One-Time Setup Required Before Testing

```bash
pip install moviepy playwright requests Pillow python-bidi numpy
playwright install chromium

# FFmpeg — download from ffmpeg.org, add to PATH
# Verify:
ffmpeg -version
ffprobe -version

# Hebrew font — verify one of these exists:
# C:\Windows\Fonts\tahoma.ttf    (most Windows machines)
# C:\Windows\Fonts\arial.ttf
# Or download Noto Sans Hebrew .ttf and set --font-path
```

---

## Key File Paths to Know

| What | Path |
|---|---|
| Morning agent prompt | `C:\Automation\TikTok\.claude\commands\tiktok.md` |
| Data collector | `C:\Automation\TikTok\.claude\commands\tiktok-collect.md` |
| Evening agent prompt | `C:\Automation\TikTok\.claude\commands\tiktok-analyze.md` |
| Asset generation spec | `C:\Automation\TikTok\scripts\generate_assets_spec.md` |
| Video generation spec | `C:\Automation\TikTok\scripts\generate_videos_spec.md` |
| Learning database | `C:\Automation\TikTok\data\video_results.csv` |
| Video config (per run) | `C:\Automation\TikTok\data\[PRODUCT_ID]-video-config.json` |
| Generated videos | `C:\Automation\TikTok\videos\[YYYY-MM-DD]-product-[ID]-[A/B/C/D].mp4` |

---

## Resuming the Pipeline

**CURRENT STATUS: Product 009 is PAUSED until performance data is collected and analyzed.**

Required sequence before Product 009:
1. Upload Products 007 and 008 (if not yet done) — B→D→C→A for each
2. Run `/tiktok collect` — enter TikTok Analytics stats for Products 001, 007, and 008
   - Must include: views, saves, comments per variant
   - Critical to include: first_2_second_retention from TikTok → Analytics → Audience Retention curve
3. Run `/tiktok analyze` — will produce Quality & Learning Report + Product 009 Decision Layer (Step E)
4. If Step E outputs PROCEED: run `/tiktok` for Product 009
   The Product 009 Creative Brief from Step E informs product selection and storyboard

The `/tiktok` pipeline is fully operational. To run the next product after the above steps:

Products to date: 001 (Galaxy Projector ✅), 002 (Car Phone Mount ✅), 003 (Bag Sealer ✅), 004 (Mist Fan ❌ BLOCKED), 005 (Lint Remover ❌ BLOCKED), 006 (❌ FAILED), 007 (Car Seat Back Organizer ✅ — pending affiliate links), 008 (360° Stand ✅ — pending affiliate links).

**Before uploading Products 007 and 008:**

Product 007:
1. Go to portals.aliexpress.com → generate 4 affiliate links for item 4001145808790 with tracking IDs TikTok007A / TikTok007B / TikTok007C / TikTok007D
2. Fill in the REPLY REFERENCE TABLE in `output/2026-06-17-product-007-upload_package.md`
3. Upload Variant A first

Product 008:
1. Go to portals.aliexpress.com → generate 4 affiliate links for item 1005006285768946 with tracking IDs TikTok008A / TikTok008B / TikTok008C / TikTok008D
2. Fill in the REPLY REFERENCE TABLE in `output/2026-06-17-product-008-upload_package.md`
3. Upload Variant A first (Price Shock hook — lead variant)

---

*This file was created at the end of the architecture session on 2026-06-10.*  
*Do not delete — it is the single source of truth for resuming this project.*
