# Creative Gap Analysis — What Successful Competitors Do That We Don't

**Date:** 2026-07-02 — **updated 2026-08-10 (sessions 21-23)** — **corrected 2026-08-11 (checkpoint audit)**
**Question:** What do successful competitor videos consistently do that our videos consistently do not?
**Status:** Synthesis of completed diagnostic work (Layers 7, 3, 5) for products 002, 003, and 007. Not yet reflected in `learning_report.json` — held per explicit instruction until this synthesis is reviewed. **`PRODUCT008_RECHECK_PENDING` — Product 008 has not been through this synthesis's current methodology; see correction below.**

**2026-08-10 update:** Layer 5's competitor benchmark, previously run on only product 008, has now also been run and QA-verified (frame identity + category relevance, both visually confirmed, full-video spot-checked) for products 002, 003, and 007 — see `PROJECT_STATUS.md` sessions 21-23 for the full run-by-run detail. **Layer 5's benchmark rule changed at the same time: a competitor now only needs to be from the same narrow product category (e.g. any magnetic car phone mount, not the identical AliExpress listing) — exact-SKU/product-identity matching is explicitly not required.** This means every finding below that was previously "confirmed on 008 only, hypothesized for the rest" is now independently confirmed on **products 002, 003, and 007** (15 real, QA-verified competitors).

**CORRECTION (2026-08-11):** the line above previously read "confirmed on all four products." That was incorrect. Product 008's original 4-competitor benchmark (created 2026-07-02, commit `f003a7b`) predates `layer5_benchmark_qa.py` (did not exist until session 19 / 2026-08-03), the category-based benchmark rule (session 21), and the canvas-capture frame-identity fix (session 19/21). It has never been re-run under any of those, and no `QA_PASSED_PRODUCT008` result exists anywhere in the repo. Product 008's evidence is preserved below and labeled **pre-current-methodology / unverified under the new standard** — directionally consistent with the newer findings, but not equivalent evidence. **`PRODUCT008_RECHECK_PENDING`. NEXT: Product 008 re-check → QA (`layer5_benchmark_qa.py --product-id 008`) → full-video comparison → THEN cross-product synthesis across 002/003/007/008.**

## Evidence base (read this before the findings — confidence varies by claim)

| Layer | Coverage | What it measured |
|---|---|---|
| 7 (pacing/retention) | 16/16 variants | WHEN viewers leave (temporal only — see naming correction in `ANALYZER_V3_SPEC.md`) |
| 3 (hook diagnosis) | 16/16 variants | Frame-level cause rating (a/b/c/d/e/h) at sub-second resolution vs. the actual hook text |
| 5 (execution diagnosis) | 1/16 variants (008B only) | Whether the rendered video matches its own Ken Burns plan |
| 5 (competitor benchmark) | **002/003/007: `QA_PASSED`, n=15 competitors** (5+5+5), verified under the current methodology (sessions 21-23). **008: n=4 competitors, but `PRODUCT008_RECHECK_PENDING`** — from the original pre-fix implementation (2026-07-02); predates `layer5_benchmark_qa.py`, the category-based rule, and the frame-identity fix; not equivalent evidence | Statistical comparison against real successful competitor videos in the same narrow category (exact SKU not required, see rule change above — confirmed for 002/003/007 only) |

**Findings below are labeled by how many variants/products actually support them.** A 16/16 finding is portfolio-wide fact. Findings #1-5 were originally a 4-competitors-on-product-008-only hypothesis, extended by inference to 002/003/007 — **as of session 23, they are now independently confirmed by real, QA-verified competitor benchmarks on products 002, 003, and 007** (15 competitors), not just inferred from our own footage. **Product 008's original 4-competitor sample is not part of that confirmation — `PRODUCT008_RECHECK_PENDING` (see correction above).**

---

## The answer, ranked by evidence strength

### 1. Zero organic motion in the opening — 16/16 our variants vs. 15/15 QA-verified competitors across products 002/003/007 (was 4/4 on product 008 only, pre-methodology; confirmed independently on 002/003/007 in sessions 21-23; `PRODUCT008_RECHECK_PENDING`)
Every single one of our 16 variants opens on a frame sequence that is pixel-identical for 1.5–3 seconds (confirmed via fresh sub-second ffmpeg extraction, not estimated). Every QA-verified competitor across products 002/003/007 (15 total) shows sustained, continuous frame-to-frame change throughout their opening and full runtime — real handheld camera/subject motion, not a static image. Product 008's earlier, pre-methodology 4-competitor sample showed the same qualitative pattern, but has not been re-verified under the current standard and is not counted in the 15/15 above. Where measured directly (008B vs. its competitors): our opening's motion magnitude sits at the **0th percentile** — below every single competitor, not just below average. Sessions 21-23 confirmed the same qualitative pattern (avg consecutive-frame SSIM 0.42-0.74 for every 002/003/007 competitor, vs. our own static 0-1.5s openings) via full-video frame captures, not just the opening.

Nuance worth keeping: for 008B/008D specifically, Layer 5 shows a Ken Burns pan *is* configured and *is* rendering correctly (SSIM decreasing monotonically) — the motion exists but is calibrated too subtly to register in the critical first 1–2 seconds. For 002/003/007, our own footage is a static photo + AliExpress screenshot with no Ken Burns pan configured for the openings checked (per Layer 3 evidence) — a stronger version of the same defect, not the same "configured but imperceptible" nuance. Either way, the viewer-facing result is identical across all 16: visually static.

### 2. Zero human presence in the opening — 16/16 vs. 15/15 QA-verified competitors (002/003/007; `PRODUCT008_RECHECK_PENDING`)
No variant across any product shows a person in its opening frame. Every QA-verified competitor across products 002/003/007 does — a real person, in a real moment (a hand actively demonstrating a car mount, a bag sealer, or a seat organizer). Product 008's earlier, pre-methodology sample (a child in bed) showed the same pattern but is not yet re-verified. This is the single sharpest visual contrast found: ours are product-only renders; theirs are person-first, from frame one.

### 3. Zero real product-in-use demonstration — 16/16 vs. 15/15 QA-verified competitors (002/003/007; `PRODUCT008_RECHECK_PENDING`)
Every one of our openings shows the product sitting motionless, alone, disconnected from any human action. Every QA-verified competitor across products 002/003/007 shows the product being actively handled, worn, mounted, sealed, or used by a real person — not just displayed — within the opening seconds, and continuing throughout the full video. Product 008's earlier sample is consistent with this but not yet re-verified under the current methodology.

### 4. Catalog/marketplace feel instead of native TikTok feel — 16/16 vs. 15/15 QA-verified competitors (002/003/007; `PRODUCT008_RECHECK_PENDING`)
This is the umbrella pattern, and it shows up in two different severities:
- **Products 002, 003, 007** (12/16 variants): the opening actually contains literal scraped AliExpress screenshots — visible marketplace page chrome ("אבטחה ופרטיות", "החזרות חינם", delivery dates, discount banners) *inside the measured 2–3s hook window itself*. Not catalog-*styled* — literally a screenshot of a shopping listing. **Confirmed zero competitors do this anywhere in their full video, across all 15 verified 002/003/007 competitors (sessions 21-23).**
- **Product 008** (4/16 variants): a glossy 3D product render on a plain studio background — the "softer" version of the same problem, and the version STEP 11D's own pre-launch review flagged in one variant as "6/10 TikTok-native (AliExpress infographic aesthetic)."

Every QA-verified competitor across products 002/003/007 reads as native/authentic UGC (product 008's earlier sample read the same way but is not yet re-verified). This is cause (c) in the Layer 3 rubric, and it was rated LIKELY in **all 16 of 16 variants** — the single most universal finding in this whole diagnostic pass.

### 5. No emotional/relatable context — 16/16 vs. 15/15 QA-verified competitors (002/003/007; `PRODUCT008_RECHECK_PENDING`)
Consequence of #2: with no human in frame, there's no face, no reaction, no relatable moment. Every one of our openings is emotionally neutral (a product photograph). The top QA-verified competitor's opening in each of 002/003/007 is a real person in a real moment — a chip-bag unboxing on a living-room floor (003, 133.1K likes), a car-mount install mid-drive (002, 19.4K likes), a full backseat reveal with real bags and water bottles (007, 110.5K likes) — inherently relatable before a single word of copy is read. Product 008's earlier, unverified sample showed the same pattern (a child in a real bedtime moment, 78.3K likes).

### 6. Hook text frequently promises a before/after or reveal that the static image never pays off — recurring across 7 of 16 variants
This is distinct from #1–5: it's not that the visual is weak in isolation, it's that the *copy actively sets up an expectation the frame contradicts*. Confirmed instances (cause e rated LIKELY or POSSIBLE):
- 003A/003C/003D: hook implies a transformation/solution; frame shows a static, undemonstrated product.
- 007C: hook explicitly promises a "before" (total mess); frame shows only the already-organized "after," with no before shown at all.
- 008B: hook says "transformed my desk"; frame shows the product simply sitting still.
- 008C: hook is about physical back pain from phone use; frame shows an empty stand with no phone in it.
- 008D: hook promises an unresolved mystery/reveal; frame shows nothing being revealed within the hook window.

This means: whenever a hook writer reaches for a before/after, mystery, or transformation angle, the current visual pipeline cannot currently deliver on it, because the opening is a single static shot. Hooks that stick to a plain price-question or plain product-naming (e.g. 007A, 007D, 008A) don't trigger this mismatch — but that's a narrower, lower-ceiling hook style.

### 7. Product reveal timing is comparable to the *slowest* competitor, not the norm
Where measured (008B vs. its 4 competitors): 3 of 4 competitors reveal the product near-instantly (~0s); one is slower (~2–5s). Our clean, unobstructed product view arrives at ~3s — in the range of the single slowest competitor in the sample, not the norm.

### 8. A distinct second creative beat correlates with the top performer in every product benchmarked — new finding, sessions 22-23
This is about competitors relative to each other, not just competitors vs. us. In products 002, 003, and 007 alike, the single highest-like-count competitor did not just demonstrate the product — it added one more beat: a direct comparison against a worse alternative ("ditch these dumb chip clips that only seal one point," 003's top performer, 133.1K likes), a multi-product/multi-bag showcase in one continuous take (002 and 003's top performers), or a "fully loaded reveal" ending shot across both rear seats (007's top performer, 110.5K likes). The lower-performing competitors in each product's benchmark were plain single-take demos only. Our own videos have neither the plain demo nor the second beat — but if/when the plain-demo gap above is fixed, this is the next lever worth testing, not yet acted on.

---

## What we do NOT lack (don't over-fix these)

- **Product legibility.** Cause (b) — "unclear product in first second" — was rated UNLIKELY in all 16 variants. The product is always clearly visible and identifiable immediately. This is a real strength; nothing here needs fixing.
- **Editing/cut frequency.** The one benchmark we have shows 0 detected hard cuts in either 008B's opening *or* any of its 4 competitors' openings. Editing pace is not the differentiator — sustained motion *intensity* is. Don't chase "add more cuts" as a fix.
- **Text overlay timing.** Verified correct/on-schedule where checked (008B). Not a pattern that emerged as a defect anywhere in Layer 3's 16-variant pass.
- **Hebrew phrasing quality.** Cause (h) was mostly UNLIKELY, with occasional POSSIBLE flags (a few machine-translation-style calques in price phrasing, one missing personal-voice framing). Real but minor — not in the same tier as #1–7.

---

## The core pattern, stated once

Across every product we've launched, the opening is built as a **static product photograph with copy layered on top**, in a category where the demonstrated successful format is a **person actively using the product in a real, relatable moment, captured with continuous camera/subject motion**. Every dimension the competitors share and we lack — human presence, organic motion, real use, emotional context, native feel — is downstream of that one structural choice. Cause (c) (catalog feel) at 16/16 is not one defect among several; it's the name for this same root pattern viewed from the "does it look native" angle, while causes (a) and the competitor motion-percentile data are the same pattern viewed from the "does it move" angle.

## What this report deliberately does not do

It does not propose pipeline changes yet — that's the next step, and the user asked to hold this as a foundation first.

**Superseded by sessions 21-23:** this section previously noted that products 002/003/007 lacked a real competitor benchmark and their findings were inferred from our own footage only. That gap is closed — all three now have real, visually-verified, QA-passed competitor benchmarks (5 competitors each), confirming the same pattern independently rather than by inference. See `PROJECT_STATUS.md` sessions 21-23 for the full run-by-run evidence (exact URLs, like counts, and per-candidate frame-identity verification) behind the findings above. **Product 008 is not part of this closed gap — its benchmark predates the current methodology and remains `PRODUCT008_RECHECK_PENDING` (see correction near the top of this document).**

Two things this report still does not do, as of this update:
- **Does not yet reflect in `learning_report.json`** — still deliberately held per standing instruction, now with 002/003/007's QA-verified evidence available for that review. Product 008 must be re-checked under the current methodology before it can be included in that review.
- **Does not yet fold finding #8 (the "second beat" pattern) into a concrete pipeline recommendation** — it's recorded as an observed correlation across three products, not yet tested as a causal fix.
