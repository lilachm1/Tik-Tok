# Creative Gap Analysis — What Successful Competitors Do That We Don't

**Date:** 2026-07-02 — **updated 2026-08-10 (sessions 21-23)** — **corrected 2026-08-11 (checkpoint audit)** — **FINAL FOUR-PRODUCT SYNTHESIS: 2026-08-11 (session 25)**

**Question:** What do successful TikTok competitor videos consistently do that our videos consistently do not — across all four products — and what should change in the next creative because of that?

**Status:** Cross-product synthesis complete across **all four products (002, 003, 007, 008)**, all four now genuinely `QA_PASSED` under the current Layer 5 category-based methodology (`QA_PASSED_PRODUCT002` session 21, `QA_PASSED_PRODUCT003` session 22, `QA_PASSED_PRODUCT007` session 23, `QA_PASSED_PRODUCT008` session 24). The combined Layer 3+5+7 diagnosis below was reviewed and approved (with the two corrections noted below), and **`learning_report.json` was updated accordingly in session 26 (2026-08-11)** — see its `creative_rules` block. **Still not reflected: the creative pipeline and Product 009 — those remain a separate, real decision, held pending human review of the `learning_report.json` update itself.**

**Prior versions of this document (superseded):** the 2026-07-02 original was a single-product (008-only, 4 competitors, pre-current-methodology) hypothesis. The 2026-08-10 update extended it to 002/003/007 (15 QA-verified competitors) but *incorrectly* rolled Product 008's old, unverified benchmark into a false "confirmed on all 4 products" claim — corrected 2026-08-11 to `PRODUCT008_RECHECK_PENDING`, then closed the same day (session 24) by re-running Product 008 from scratch under the current methodology. This version supersedes all of that: all four products now carry equal-rigor, QA-verified evidence.

**APPROVED WITH TWO CORRECTIONS (2026-08-11, same session):** the combined Layer 3+5+7 diagnosis below was approved subject to (1) removing any implication that competitor retention was measured or that competitors "decline less fast" than we do — Layer 5's evidence is about creative presentation, not competitor retention, which was never collected; and (2) reclassifying the revised Rule 2 from `MODIFIED RULE` to **`PERMANENT CREATIVE RULE — revised from the original Rule 2`**, since the revised wording itself now has full, unanimous, portfolio-wide evidence (16/16 vs. 0/20), even though the original narrow wording did not. Both corrections are applied throughout this document.

---

## Evidence base (what this document is actually built on)

| Layer | Coverage | What it measured |
|---|---|---|
| 7 (pacing/retention) | 16/16 our variants | WHEN viewers leave (temporal only) |
| 3 (hook diagnosis) | 16/16 our variants | Frame-level cause rating (a/b/c/d/e/h) at sub-second resolution vs. the actual hook text |
| 5 (execution diagnosis) | 1/16 our variants (008B only) | Whether the rendered video matches its own configured motion plan — not repeated for other variants, see gap note below |
| 5 (competitor benchmark) | **4/4 products, `QA_PASSED`, n=20 competitors total** (5+5+5+5: 002, 003, 007, 008) | Statistical, full-video comparison against real, successful competitor videos in the same narrow category (exact SKU not required) |

**Portfolio scope:** 16 of our own variants (4 products × 4 variants each) and 20 verified competitors (4 products × 5 each). All 20 competitors passed `CATEGORY_RELEVANCE_VERIFIED` and `FRAME_IDENTITY_VERIFIED`, both personally visually inspected (opening, standard 0–8s grid, and mid/late/near-end full-video frames), plus automated `layer5_benchmark_qa.py` (0 FAIL on all 4 products; 1 non-blocking caption-placeholder WARN on each — TikTok gives no usable caption for most of these candidates, resolved every time by direct visual/on-screen-text confirmation, never by trusting the caption).

**Known evidence gaps in this synthesis (reported, not silently filled in):**
- **Layer 5 execution diagnosis (our own motion measurement)** exists only for 008B (avg SSIM 0.927, 0th percentile vs. its own competitor set). It was never run on the other 15 variants. Everywhere else in this document, "our opening is static" is Layer 3's direct evidence (pixel-identical frames via fresh sub-second ffmpeg extraction), not a computed SSIM number — this is still direct evidence, just a different metric than 008B's.
- **The "second creative beat" pattern (Rule 4, below) is explicitly documented for products 003, 007, and 008's top competitor, but not for 002.** Session 21's product 002 notes describe all 5 competitors similarly ("real hand actively demonstrating... continuous motion") without singling out a structural difference between the top and bottom performer the way sessions 22/23/24 did. This is an absence of a specific observation, not contrary evidence — Rule 4 below is stated as 3-of-4-products-confirmed, not 4-of-4, until someone goes back and checks 002's competitor set with that specific question in mind.
- **Competitors' market origin is not confirmed Israeli/Hebrew for the large majority of the 20** (captions are mostly English/Spanish or unusable placeholders; a few handles are Israeli-sounding, e.g. `@max_stock_israel`). Per `ANALYZER_V3_SPEC.md`'s own expansion rule, this is an accepted global-market expansion, not a methodology failure — but it means every claim below is about "successful TikTok content in this narrow category," not proven to be about the Israeli market specifically.

---

## Portfolio-wide facts (direct evidence, not correlation)

From Layer 3's frame-level cause ratings across all 16 variants (agent-rated LIKELY/POSSIBLE/UNLIKELY against fresh, sub-second ffmpeg-extracted frames — not estimated):

| Cause | Meaning | LIKELY in |
|---|---|---|
| **a** | weak/static opening visual, no motion cue | **16/16 (100%)** |
| **c** | AliExpress/marketplace catalog feel | **16/16 (100%)** |
| e | hook text promises something the frame doesn't show | 5/16 (31%) |
| d | generic hook text | 6/16 (38%) |
| b | unclear product in first second | **0/16 (0%)** — a real strength, not a defect |
| h | non-native Hebrew phrasing | **0/16 (0%)** — a real strength, not a defect |

Causes **a** and **c** are unanimous across every single variant in the portfolio, in all four product categories. This is the strongest, most direct fact in this document.

**Retention (Layer 7), statistically-meaningful variants only (views ≥ 10 — 12 of 16 qualify):** first-2-second retention ranges **0.25–0.45** (avg 0.38) across all four products. **Zero of the 12 statistically meaningful variants reach `STRONG`.** Every `STRONG` classification in the portfolio (003C at 0.84, 008A at 0.75) comes from a variant with **1 and 4 total views respectively** — the only "good-looking" numbers in the entire 16-variant dataset are both statistically meaningless. This is a new, cross-product finding in its own right (see below) — it is not a creative-content pattern, so it is not proposed as a fifth Creative Rule, but it materially affects how confidently anything in this document can be read against actual performance.

**Competitor side:** all 20 verified competitors (5 per product) carry real, fetched `like_count` values ranging from 176 to 133,100 — every one is a genuinely successful video in its narrow category, not a random sample.

---

## The final Creative Rules

Each rule below is classified as **`PERMANENT CREATIVE RULE`** (unanimous across all 4 products, no counter-example on either side), **`MODIFIED RULE`** (the underlying pattern holds everywhere, but the originally-stated mechanism was too narrow, and the broader wording that replaces it does not yet have full portfolio-wide evidence behind it), or **`INSUFFICIENT EVIDENCE`** (gap noted, not filled in). No rule was `REJECTED` — all four held up under four-product scrutiny. **A rule whose wording was revised can still reach `PERMANENT CREATIVE RULE` status if the *revised* wording itself has full, unanimous evidence across all 4 products** — labeled `PERMANENT CREATIVE RULE — revised from the original Rule N` to keep the revision history visible (see Rule 2).

### Rule 1 — Open on real human/hand engagement, not an untouched product render
**Classification: `PERMANENT CREATIVE RULE`**

**Evidence:** 0/16 of our variants open on a hand or person already engaging with the product — every opening frame across all 16 is a motionless product photograph or render, confirmed directly via fresh sub-second frame extraction. 20/20 verified competitors show a real hand or person engaging with the product within their opening seconds (18/20 immediately at t≈0; 2/20 — `@toptech.mx` and `@digitalnexus1`, both product 008, both also the two lowest-performing competitors in that benchmark — have a briefly ambiguous ~1–2s open before the hand becomes legible, but no competitor across any product opens on an untouched, human-absent render the way all 16 of our variants do).

**Per-product support:** 002 (5/5 competitors), 003 (5/5), 007 (5/5), 008 (5/5). Unanimous, zero exceptions.

**Product 008's contribution:** confirms and extends Rule 1 unchanged — no modification needed. (The two "slower reveal" competitors above are the closest thing to a counter-example, and even they show human engagement well before ours ever does.)

### Rule 2 — Avoid marketplace/catalog-style presentation; use native, real-world demonstration
**Classification: `PERMANENT CREATIVE RULE — revised from the original Rule 2`.** The original narrow wording ("never show an AliExpress screenshot") was correctly `MODIFIED` by Product 008's evidence. The revised wording below now has full, unanimous, portfolio-wide evidence of its own — 16/16 our variants vs. 0/20 verified competitors, across all four products — so the *revised* rule itself is promoted to `PERMANENT CREATIVE RULE`, with the revision history kept visible rather than erased.

**Original wording tested:** "Do not show AliExpress/marketplace-style content inside the video." **Evidence for the original, narrow wording:** true for 12/16 of our variants (002, 003, 007) — personally re-confirmed this session by directly viewing `002B`, `003A`, and `007A`'s cut frames: all three show literal scraped AliExpress listing pages, with real UI chrome ("Express Choice" badge, delivery-date text, discount banners with struck-through prices, "אבטחה ופרטיות" security badges, "החזרות חינם" free-returns text). **But false for the remaining 4/16 (008):** 008's variants cut between two different static CGI product renders — no literal screenshot, no marketplace UI chrome, confirmed by direct visual inspection this session and last.

**Why this is `MODIFIED`, not `REJECTED` or left as-is:** cause **c** (catalog/marketplace feel) is rated LIKELY in **16/16 of our variants — including all 4 of 008's**, even though 008 has no literal screenshot. The literal "no screenshot" rule would incorrectly mark 008 as compliant when it exhibits the exact same underlying defect by a different mechanism. **0/20 verified competitors, across all four products, show ANY marketplace/catalog content in any form** — no screenshots, no plain studio product renders, no infographic-style compositing — anywhere in their full videos.

**Revised permanent wording:** *"Avoid any marketplace/catalog-style product presentation — a literal scraped listing screenshot, product-page UI chrome, OR a static studio/CGI product render — in favor of native, real-world, camera-captured demonstration."*

**Per-product support:** literal-screenshot version of the defect: 002 (4/4 variants), 003 (4/4), 007 (4/4), 008 (0/4). Broader catalog/render-feel defect (cause c): 002 (4/4), 003 (4/4), 007 (4/4), 008 (4/4) — unanimous. 0/20 competitors show either form, in any of the 4 products.

**Product 008's contribution:** this is the one rule Product 008 materially changed. Without 008, the rule would have stayed narrowly scoped to "no screenshots" — technically true but under-general, and would have let a future product "comply" by switching to a glossy render instead of fixing the underlying problem.

### Rule 3 — Show the actual mechanism/action, not merely the product on display
**Classification: `PERMANENT CREATIVE RULE`**

**Evidence:** 0/16 of our variants demonstrate the product's actual function within the measured window — every opening (and, per the video-configs, every full video) shows the product sitting still, never performing its function on camera. 20/20 verified competitors show the product's real mechanism/action in use — mounting, sealing, organizing, or rotating, by a real hand.

**Sharpest instance found (session 24):** Product 008's core marketed feature is "360° rotation" — variant 008D's hook explicitly promises a wordless visual reveal of that rotation ("מסתובב 360° — מסביר בלי מילים" / "rotates 360° — explains itself without words"), but the frame shown for the entire hook window is a static product photo with a superimposed **orange arrow graphic** standing in for the rotation — the product's own headline feature is depicted by an icon, never actually demonstrated on camera. This is corroborated by cause **e** (hook-product mismatch, LIKELY/POSSIBLE in 5/16 variants) — several of those 5 instances are exactly this failure mode (a hook promises an action/transformation/reveal the frame never shows).

**Per-product support:** 002 (5/5 competitors demonstrate real use vs. 0/4 our variants), 003 (5/5 vs. 0/4), 007 (5/5 vs. 0/4), 008 (5/5 vs. 0/4). Unanimous.

**Product 008's contribution:** strengthens the rule with its single most concrete example across the whole portfolio (the rotation-as-arrow-icon case) — no change to the rule's wording, just its strongest piece of evidence.

### Rule 4 — The top-performing competitor shows a meaningful progression beyond the plain demo
**Classification: `MODIFIED RULE`** (broadened per Product 008's evidence; confirmed in 3 of 4 products — see evidence gap note)

**Original wording tested:** "Include a distinct second beat beyond the plain demo (comparison, multi-product showcase, or a reveal ending)." **Evidence, by product:**
- **003:** top performer (`@dustyshops`, 133.1K likes) adds a direct comparison against a worse alternative ("ditch these dumb chip clips"); the two highest performers include a multi-bag showcase. Lower performers are plain single-take demos.
- **007:** the two highest performers (`@phoebeyuee` 110.5K, `@tidytravelshop` 63.7K) both end on a "fully loaded reveal" shot across both rear seats; lower performers lack it.
- **008:** the top performer (`@yeuunnt.22`, 78.3K likes) is **35.4 seconds** — roughly 2–3× the other four competitors' length (10.2–16.4s) — driven by sustained real human interaction over that whole runtime, not a discrete added segment. The second-highest (`@xyxzq1sfe1`, 7,027 likes) instead shows a clearer discrete structure: 2 detected hard cuts, a product-demo shot cutting to a payoff shot of the creator smiling while genuinely using it. The two lowest performers (`@toptech.mx` 1,211, `@digitalnexus1` 176) are single continuous takes with no such progression.
- **002:** **not separately documented** — session 21's notes describe all 5 competitors similarly without isolating a top-vs-bottom structural difference. Not contrary evidence, just an unasked question.

**Why this is `MODIFIED`:** 008 shows the "something more" doesn't have to be a discrete added segment (a comparison, a showcase, a reveal shot) — it can also be **sustained real engagement over a much longer runtime**. The common thread across 003/007/008 is not "a second beat" specifically, but a more general progression beyond one flat demonstration.

**Revised permanent wording:** *"The single highest-performing competitor in a benchmark consistently shows a meaningful progression beyond a single flat demo — via comparison, a payoff/reveal moment, multi-item/multi-context showcase, or sustained real engagement over a longer runtime — while the lower-performing competitors in the same benchmark are plain single-take demos."*

**Per-product support:** confirmed in 003, 007, 008 (3/4); not checked for 002 (evidence gap, reported per instructions rather than filled in with a new competitor review). Our own 16 variants have neither the plain demo nor any such progression.

---

## New cross-product finding (not a creative rule — a data-reliability finding)

**Every "good-looking" retention number in the 16-variant portfolio is a statistical artifact of a tiny sample.** Lining up all 16 variants side by side (only visible once all four products are in the same table) shows: of the 4 variants with fewer than 10 total views (003C n=1, 003D n=2, 008A n=4, 008D n=2), **all four** happen to show the portfolio's only `STRONG`/high-`MARGINAL` classifications (0.84, 0.45, 0.75, 0.60). Every variant with a statistically usable sample (≥10 views, 12 of 16) is `WEAK` or `MARGINAL` (0.25–0.45), and **none** reach `STRONG`. This is not a creative-content pattern, so it is not proposed as a fifth Creative Rule — but it means: **do not read any single "STRONG" result in this dataset as evidence the creative pipeline is working in some cases** — every one of them is a sample-size artifact, and the honest, load-bearing number for "how are we actually doing" is the 0.25–0.45 range from the 12 reliable variants.

---

## What we do NOT lack (don't over-fix these)

- **Product legibility.** Cause (b) — unclear product in the first second — 0/16. The product is always clearly visible immediately.
- **Editing/cut frequency.** Where measured (008B and its competitors, and 008's session-24 competitor set), 0 detected hard cuts in most openings; the one competitor with detected cuts (`@xyxzq1sfe1`) uses them for a payoff structure, not rapid editing. Cut frequency is not the differentiator — motion intensity and real engagement are.
- **Hebrew phrasing quality.** Cause (h) — 0/16 LIKELY, only occasional POSSIBLE flags (minor machine-translation-style calques). Real but minor, not in the same tier as the rules above.

---

## Combined Layer 3 + Layer 5 + Layer 7 diagnosis

**Layer 3 = WHAT viewers see in the opening.** Direct evidence, all 16 variants: a static, catalog/render-styled product image with no human presence and no functional demonstration (causes a, c both 16/16).

**Layer 7 = WHEN our viewers leave.** Direct evidence, 12 statistically-meaningful variants: retention is already down to 0.25–0.45 by the 2-second mark.

**Layer 5 = HOW successful competitor creative differs.** Direct evidence, all 20 competitors across 4 products: 20/20 use real human/product interaction and real mechanism demonstration, instead of our static/catalog presentation — and, in 3 of 4 products checked, some added progression beyond a flat demo in the top performer specifically. **We do not have competitor retention curves.** Layer 5's evidence here is about *creative presentation* — what the competitor videos show and how — not about how fast competitor viewers do or don't leave. No claim is made, or should be inferred, about competitor retention.

**Combined diagnosis:** these three findings converge on one coherent, repeated story across all four independent product categories: a static, catalog-feeling opening (Layer 3) is shown during precisely the window where *our own* viewers are already leaving fastest (Layer 7), and that same opening looks nothing like what 20/20 real successful competitors in the same narrow categories actually do on screen (Layer 5). This convergence is a **strong, repeated correlation** across four independent samples — meaningfully stronger than a single anecdote — but it is **not a proven causal chain**, and specifically: **because competitor retention was never measured, this document does not and must not claim that successful competitors retain viewers better or "decline less fast" than we do — only that their on-screen creative presentation differs from ours.** No variant of ours has ever been produced that follows the competitor pattern and had its own retention measured, so there is no before/after evidence that fixing these things would actually raise retention. The correlation is consistent and repeated; the causal claim is a hypothesis for the next creative test to validate, not a demonstrated fact.

---

## What remains unproven until future creative testing

- That opening on real human/hand engagement (Rule 1), avoiding marketplace/catalog presentation (Rule 2), demonstrating the real mechanism (Rule 3), or adding a meaningful second beat (Rule 4) will actually **increase** retention or performance for our own videos. This is a hypothesis grounded in a strong, repeated four-product correlation — not a causal fact.
- Whether the "second beat" pattern (Rule 4) holds for product 002's specific competitor set (evidence gap, not contrary evidence).
- Whether any of these findings are specific to the Israeli market — most of the 20 competitors' market origin is unconfirmed (see evidence base gaps above).

**Not done in this synthesis, deliberately:** `learning_report.json` is untouched, the creative pipeline is unmodified, and Product 009 has not been generated — this document is the input to that review, not the review's conclusion. `ANALYZER_V3_SPEC.md` has been separately updated (same session) to make the per-product Layer 5 methodology and this cross-product synthesis pipeline a permanent architecture requirement, not a one-off procedure.

**UPDATE (2026-08-11, session 26):** the review referenced above has since happened — the combined diagnosis was approved (with the two corrections already folded into this document) and `learning_report.json` now has a `creative_rules` block reflecting Rules 1-3 as `PERMANENT_CREATIVE_RULE`, Rule 4 as `MODIFIED_RULE`/non-permanent, the causality guardrail, and the sub-10-view data-quality finding. The creative pipeline and Product 009 remain untouched, pending a further human review of that `learning_report.json` update itself. Full detail in `PROJECT_STATUS.md` session 26.
