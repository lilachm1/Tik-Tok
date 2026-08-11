# Analyzer v3 — 10-Layer TikTok Affiliate Diagnosis System

**Status: PARTIALLY IMPLEMENTED (corrected 2026-08-11 — this line was previously stale, and briefly overstated Product 008's status; see `PROJECT_STATUS.md`'s 2026-08-11 checkpoint-audit entries for what happened).** Layers 3 (Hook Diagnosis) and 7 (Pacing/Retention) are implemented and run across all 16/16 CONFIRMED variants. Layer 5 (Video/Creative Execution + competitor benchmark) is implemented and, as of session 24 (2026-08-11), genuinely run and QA-verified on all 4 products (002 session 21, 003 session 22, 007 session 23, 008 session 24 — re-run from scratch after an audit found its earlier "confirmed" status had been asserted without ever re-running it) — see this section's own "CATEGORY-BASED BENCHMARK RULE" and "CROSS-PRODUCT LEARNING ARCHITECTURE" below for the current, now-permanent methodology, and `PROJECT_STATUS.md` sessions 13-25 for the full implementation/validation history. The session-25 cross-product synthesis across all 4 products lives in `CREATIVE_GAP_ANALYSIS.md`. **Layers 1, 2, 4, 6, 8, 9, 10 remain SPEC ONLY — NOT IMPLEMENTED**; this document defines their architecture so a future session can build them without re-deriving the design. The Layer 5 "Same-Product Visual Identity Gate" subsection is spec-only and explicitly DEFERRED (not required for Layer 5's current category-based goal).

**Purpose.** The current analyzer (`tiktok-analyze.md` C.A–C.J, confirmed working as of 2026-07-02) answers "which variant performed best." Analyzer v3 must answer *why* — diagnosing product, offer, hook, creative asset, execution, angle, pacing, CTA, click-funnel, and competitive positioning as ten distinct, independently-diagnosable layers — and turn that diagnosis into a specific next action, not just a score.

**Relationship to the current analyzer.** v3 does not replace C.A–C.J; it wraps and extends them. Layer 7 (Pacing/Retention) is the current C.F, extended. Everything else is new. `data/video_results.csv`, `learning_report.json`, and `analyze_qa.py` remain the numeric backbone v3 reads from.

---

## Cross-cutting rules (apply to every layer)

### Israeli Market Context (mandatory lens — not a separate layer)

This entire platform is scoped to the Israeli market, Hebrew-language content, ₪-denominated pricing (per `TIKTOK_AGENT_PLAN.md`'s own stated scope: "Market: Israel (for now)", "Video content language: Hebrew"). This is not a future extension — it must shape how every layer's evidence is read, not just which language the output is written in:

- **Hebrew-language quality is evidence, not presentation.** Layers 3 (Hook) and 6 (Marketing Angle) must evaluate hook/CTA/angle text against actual Hebrew idiom and register — not "is it grammatically valid Hebrew" but "does a native Israeli TikTok viewer read this as natural spoken Hebrew, not a translated ad." This extends the project's existing HEBREW TEXT QUALITY + GENERAL AUDIENCE COPY rules (`tiktok.md` STEP 6/7 — gender-neutral phrasing, no female-only verb forms) into a diagnostic check, not just a generation-time gate: if a variant underperforms, Layer 3/6 must check whether stilted or overly-literal Hebrew phrasing is a plausible cause before looking elsewhere.
- **Israeli price sensitivity is category-relative, not generic.** Layer 2 must apply the existing ₪ price-band system (`tiktok.md`'s 7-tier model: hard reject <₪15/>₪120, preferred ₪25–₪65) as the Israeli-calibrated baseline it already is — but must also check price against what Israeli buyers specifically expect for that category (e.g., ₪40 reads as "cheap gadget" for a phone stand but "expensive" for a kitchen tool), not a flat international norm.
- **Israeli buying behavior shapes Layer 1 and Layer 8.** Impulse-buy culture, trust signals Israeli shoppers specifically respond to (e.g., "אלפי לקוחות קנו," social proof phrased in Hebrew commerce idiom, not literal-translated "1000+ sold"), and the comment-to-buy culture specific to Israeli TikTok (commenting a code to request a DM'd link is itself a locally-established behavior pattern this whole CTA mechanic depends on) must inform Layer 1's demand read and Layer 8's CTA-clarity read — a CTA that would work on US TikTok but doesn't match how Israeli audiences actually request links is a Layer 8 failure mode, not a generic CTA problem.
- **Layer 6's angle taxonomy must be filtered through Israeli cultural context**, not applied as a generic Western list. Family/parenting angles, "status" framing, humor register, and directness norms differ from US/Western TikTok — an angle that reads as compelling in a generic sense may not land the same way for an Israeli audience (e.g., Israeli TikTok tends to reward directness and mild self-deprecating humor over aspirational/status framing that performs better elsewhere). Layer 6 should flag when a candidate angle is untested *specifically in the Israeli TikTok context*, even if it's a proven angle in global affiliate marketing generally.
- **Layer 10's competitor set must be TikTok Israel specifically, not global TikTok.** Searching for the product term in English, or pulling generic global Creative Center trends, is the wrong comparison set — Layer 10 must search/filter for Hebrew-language creator content and Israeli-audience engagement patterns. A competitor video that thrives on US TikTok with a given structure/angle is *weak* evidence for what will work here; a competitor thriving with Hebrew captions and Israeli-audience comments is strong evidence. This should be an explicit filter step in Layer 10's data collection, not an assumption.
- **Trend evidence (Layer 1) must be Israel-anchored.** The existing STEP 1 rule already requires 2+ trend-evidence sources — Layer 1 should specifically weight Hebrew-language TikTok search/comment evidence and Israeli Google Trends signal over AliExpress's global sold-count alone, since global demand does not reliably predict Israeli TikTok demand (this is exactly the gap the STEP 1-TODO "Trend Source Audit" in `TIKTOK_AGENT_PLAN.md` already flagged as a risk — Analyzer v3 should not inherit that same AliExpress-first bias).

### Evidence Requirement
No layer may emit a classification without at least one cited piece of evidence, in one of three forms:
- **Metric citation:** `[LAYER] verdict — evidence: first_2_second_retention=28% (002C, n=390 views)`
- **Asset citation:** `[LAYER] verdict — evidence: frame at 0.0s (videos/2026-06-17-product-008-C.mp4) shows flat catalog shot, no motion`
- **Comparison citation:** `[LAYER] verdict — evidence: competitor video [URL/ID] shows product in-hand at 0.3s vs. our hook-text-only opening`

An unsupported assumption is a spec violation, not a stylistic preference — this mirrors how every conclusion in the 2026-07-02 analysis was required to trace back to a specific CSV value or file.

### Confidence Rules (permanent, platform-wide)
These extend the small-sample handling already done ad hoc in the 2026-07-02 analysis (003C/003D/008A/008D) and in `analyze_qa.py`'s retention check into a standing rule every layer must follow:

1. **`MIN_CONFIDENT_VIEWS` threshold (proposed: 50 views).** Any variant below this is `LOW_CONFIDENCE` for every rate-based metric (retention %, watch-time %, engagement %) — the raw numbers are still shown, never hidden, but flagged inline: `84% (n=1 view — LOW CONFIDENCE, excluded from averages)`.
2. **Exclusion, not deletion.** A `LOW_CONFIDENCE` data point is never silently dropped from a report — it's shown, flagged, and excluded only from cross-variant/cross-hook *averages*. Any average that would materially change with vs. without it must show both numbers (exactly as this session's Problem/Solution retention average was recomputed 48.8% → 37% once the 1-view outlier was excluded).
3. **No average may be silently dominated by one low-confidence input.** If excluding all `LOW_CONFIDENCE` points from a group changes the group's average by more than a defined delta (proposed: 5 percentage points), the report must show the exclusion explicitly — this is a hard rule, not a judgment call left to the layer.
4. **Sample size travels with the number, always.** Every displayed rate must be immediately followed by its `n=`. A rate without a stated sample size is a spec violation.
5. **Implementation note (for later):** this logic should live in one shared module (e.g. `confidence.py`) that all 10 layers import — not reimplemented per layer, to avoid the 3 nearly-identical small-sample caveats that were written by hand across today's analysis.

### Operating Mode Rule (permanent, platform-wide)
Every layer must respect the two operating modes defined in `TIKTOK_AGENT_PLAN.md` → "Operating Modes — Permanent Production Requirement": in Daily Incremental Production Mode, no layer may re-diagnose a video that is already fully collected, validated, and diagnosed under the current diagnostic-logic version, and a diagnosis produced under a changed diagnostic version must be added alongside — never overwrite — prior evidence/versions. Approved 2026-08-03; not yet implemented in any layer script.

---

## Layer 1 — Product Demand

*Apply the Israeli Market Context lens (see Cross-cutting rules): weight Hebrew-language TikTok evidence and Israeli Google Trends over AliExpress global sold-count.*

**Core question:** Is this a product people currently want, right now, enough to stop scrolling and act on it?

**Data needed:** AliExpress listing sold-count/rating/review-count (already gathered at `/tiktok` STEP 1–2); the two logged trend-evidence sources from STEP 1; this account's own category-level performance history (C.I cross-product data) if 2+ products exist in the same category; buyer review text (mined for real demand language).

**Files/pages to inspect:** `output/[date]-product-[ID].md` (research package — trend evidence, AliExpress URL, sold count, rating); the AliExpress listing page itself (review section specifically, for buyer language); `data/video_results.csv` filtered to the product's category (via C.I).

**Metrics / qualitative signals:** AliExpress sold-count and rating vs. category norm; count and recency of the 2 required trend-evidence sources; this account's historical avg views+saves for the same category (if available — currently every category in this account has ≤2 products, so this signal is often `INSUFFICIENT DATA`, not absent — see Confidence Rules); review-text sentiment (does it describe solving a real problem, or just "cute/cheap"?).

**Failure modes:**
- `LOW_DEMAND_SIGNAL` — weak or single-source trend evidence, sold-count low for the category
- `SATURATED_CATEGORY` — many sellers/creators pushing an identical item with no differentiation
- `MISMATCHED_AUDIENCE` — demand evidenced in the source market (AliExpress global data) but not in Israeli/Hebrew TikTok specifically
- `STALE_TREND` — trend evidence is old; momentum already declining by the time of upload

**Output:** `Strong Product` / `Average Product` / `Weak Product` + 1–3 sentence justification citing specific evidence per the Evidence Requirement.

**How it changes the next action:** `Weak` → exclude this product/category from future STEP 1 shortlists (feeds STEP 0C's exclusion list). `Average` → one more test with a different angle before concluding. `Strong` → priority candidate for STEP 0B Winner Scaling (more variants of the same product). **Layer 1's verdict can be overridden by Layer 10** — see the cross-layer note at the end of Layer 10.

---

## Layer 2 — Offer / Deal Strength

*Apply the Israeli Market Context lens: the ₪ price bands are already Israel-calibrated — judge price against category-specific Israeli buyer expectations, not a flat international norm.*

**Core question:** Is the price/value/urgency combination compelling enough to trigger an impulse action at the moment of viewing — independent of whether the product itself is desirable?

**Data needed:** `price_ils` (CSV); STEP 3C's Final Listing Price + Final Listing Social Proof (the *actual* listing's numbers, not research-phase estimates — this project already had one real bug here, fixed 2026-06-14, where an estimated price leaked into a video overlay); any discount/urgency indicator on the AliExpress listing; the exact price/urgency language actually rendered in the video overlay.

**Files/pages to inspect:** `output/[date]-product-[ID]-upload_package.md` (the price and social-proof text actually used); `data/[pid]-video-config.json` (verbatim overlay text); the live AliExpress listing (strike-through price, discount %, stock-countdown UI if present).

**Metrics / qualitative signals:** the existing 7-tier price-band classification from `tiktok.md` (hard reject <₪15/>₪120, preferred ₪25–₪65); price positioned against *this specific category's* typical price (a generically "preferred-band" price can still be expensive for its category); presence/absence of a genuine urgency cue.

**Failure modes:**
- `PRICE_TOO_HIGH_FOR_CATEGORY` — acceptable by the generic band, expensive within its actual category
- `NO_URGENCY_SIGNAL` — no discount/scarcity cue anywhere in listing or video
- `VALUE_UNCLEAR` — video never explains what justifies the price
- `PRICE_INCONSISTENT` — research price ≠ final listing price ≠ video overlay price (a known prior bug class; this check makes it a standing diagnostic, not a one-off fix)

**Output:** `Strong Offer` / `Average Offer` / `Weak Offer` + justification.

**How it changes the next action:** `Weak` with Layer 1 = `Strong`/`Average` → re-source from a different listing of the same product (better discount/price) rather than abandoning the product or touching the creative at all. `PRICE_INCONSISTENT` → immediate fix in STEP 3C/STEP 6 enforcement, same category as the 2026-06-14 fix.

---

## Layer 3 — Hook Diagnosis

*Apply the Israeli Market Context lens: judge hook text as native spoken Hebrew a real Israeli viewer would say, not translated-ad phrasing — add cause (h) below.*

**Core question:** Did the first 2 seconds actually stop the scroll — and if not, which specific, identifiable cause is responsible?

**Data needed:** `first_2_second_retention` (CSV, populated as of 2026-07-02's collector fix); `hook_type` and `hook_text` (CSV); the actual 0–2s frames of the rendered video; the generation-time STEP 11D Criterion 1 (Scroll-Stopping Power) and Criterion 3 (Hook Effectiveness) scores already saved in the upload package.

**Files/pages to inspect:** `data/[pid]-video-config.json` segment 0 (exact text/position/asset); the rendered `videos/[...].mp4`'s first 2 seconds, re-extracted at finer granularity than generation-time QA if the retention data suggests a sub-second question; the upload package's already-recorded STEP 11D scores for this variant.

**Metrics / qualitative signals:** `first_2_second_retention` classified `STRONG` (>65%) / `MARGINAL` (40–65%) / `WEAK` (20–40%) / `CRITICAL` (<20%) — thresholds already defined in current C.F, reused here; **explicit comparison against the STEP 11D pre-launch prediction** — if STEP 11D scored this hook as PASS but real retention came back WEAK/CRITICAL, that divergence is itself a finding (the pre-launch visual QA has a blind spot worth escalating, not just a one-off miss).

**Failure modes (owns 5 of the current C.F 7-cause tree — a/b/c/d/e; f/g are shared with Layer 7; h is new, Israel-specific):**
- `(a)` Weak opening visual — flat catalog shot, no motion cue
- `(b)` Unclear product in first second
- `(c)` AliExpress catalog feel — reads as a marketplace thumbnail, not organic TikTok
- `(d)` Generic hook text — no specific number/problem/surprise
- `(e)` Hook–product mismatch — text promises something the image doesn't show
- `(h)` **Non-native Hebrew phrasing** — grammatically valid but reads as translated/stilted rather than natural spoken Hebrew a real Israeli viewer would use; distinct from (d) "generic" — text can be specific and still fail this way

**Output:** retention classification + LIKELY/POSSIBLE/UNLIKELY rating for each of causes a–e and h, each with a fresh visual/textual read of the actual frames and hook copy (not a re-quote of the generation-time score, which was a *prediction* made before any real data existed) + the STEP 11D-divergence note when applicable.

**How it changes the next action:** confirmed cause → regenerate this variant's hook segment with a different asset/text before reusing this product's creative elsewhere. Same cause recurring across ≥2 products → escalate to a permanent `tiktok.md` STEP 6/11B rule change — the exact pattern that already produced 3 permanent rules in this project's history (Safe Zone, Screenshot Evidence, Product Visibility).

---

## Layer 4 — Creative Asset Quality

**Core question:** Are the raw materials (images, screenshots, scroll capture) good enough to build a compelling video at all, independent of how they're edited together?

**Data needed:** `assets/[pid]/manifest.json` (count, dimensions, sizes — anomaly detection already exists via STEP 8B's Asset Identity Gate); the actual image/video files.

**Files/pages to inspect:** `assets/[pid]/images/*.jpg`, `assets/[pid]/screenshots/*.png`, `assets/[pid]/scroll/*.mp4` — visually inspected for resolution, lighting, in-use vs. flat-catalog framing, presence of lifestyle/human-context imagery, before/after or demonstration shots.

**Metrics / qualitative signals:** image count vs. the existing 5–12 target range; resolution (already in `manifest.json`); a new qualitative rubric this layer introduces — **catalog-shot ratio** (fraction of images that are flat product-only shots vs. in-use/lifestyle shots), which feeds directly into Layer 3's cause (c).

**Failure modes:**
- `INSUFFICIENT_VARIETY` — fewer than 5 usable images, or all one angle
- `NO_LIFESTYLE_CONTEXT` — zero in-use/human-context images available at all
- `LOW_RESOLUTION` — below a defined pixel threshold
- `STALE_SOURCE` — the listing's own images look identical to what many competing sellers use (ties to Layer 10)

**Output:** `PASS` / `REPLACE_ASSETS` + the specific missing asset type(s).

**How it changes the next action:** `REPLACE_ASSETS` → re-run `generate_assets.py` against a different listing, or source additional lifestyle imagery, **before** the next render of this product — this layer has both a pre-generation quick-check mode (gate before STEP 10) and a post-hoc retrospective mode (diagnosing an already-published underperformer), and the spec should preserve both entry points.

---

## Layer 5 — Video / Creative Execution

**Core question:** Given adequate raw assets (Layer 4 passed), was the finished edit itself well-constructed?

**Data needed:** the rendered MP4; `data/[pid]-video-config.json` segment timing; the already-computed STEP 11B (6 criteria)/11C (12 criteria)/11D (12 criteria) frame scores.

**Files/pages to inspect:** `videos/[date]-product-[pid]-[variant].mp4`, re-extracted at finer granularity specifically around whatever second Layer 7 identifies as the drop-off point; the upload package's existing STEP 11C/11D verdicts for this exact variant.

**Metrics / qualitative signals:** the existing STEP 11D 6-score baseline (Hook, Clarity, Flow, TikTok-Native, CTA, Overall), **plus** this layer's unique contribution: correlating the *exact second* Layer 7 identifies as the retention drop against the storyboard's segment boundaries — e.g., "the drop coincides with the 5s cut into the benefit segment; was that transition abrupt?"

**Failure modes:**
- `ABRUPT_TRANSITIONS`
- `TEXT_OVERLAY_TIMING_MISMATCH` — text on/off-screen out of sync with the content beat
- `INSUFFICIENT_MOTION` — Ken Burns pacing too slow/fast for the segment
- `NO_WOW_MOMENT` — no frame reads as a demonstration payoff
- `PRODUCT_OBSCURED` — ties to the existing Product Visibility Rule

**Output:** `PASS`, or a segment-numbered list of specific edit changes (e.g., "shorten segment 2 [5–9s benefit] — Layer 7's drop-off timestamp lands exactly here").

**How it changes the next action:** feeds directly into `generate_videos.py`'s segment-timing parameters for a re-render of this exact variant, or into `tiktok.md`'s STORYBOARD defaults if the same execution flaw recurs across products.

**COMPETITOR BENCHMARK REQUIREMENT (added 2026-07-02, mandatory part of Layer 5, not deferred to Layer 10):** a single competitor video is not a benchmark — it's one data point, and the first attempt at using one (008B, session 13/14) proved exactly why: measuring against one video answers "is this one video different from ours," not "are we below what actually works in this category." Layer 5 must compare against **multiple successful Israeli TikTok competitor videos in the same product/category — Top 5 minimum, Top 10 ideal** — and report an aggregate, not a single anecdote.

*Note this is Layer 5 scoping the SAME underlying competitor-comparison capability Layer 10 needs at full scale (market-wide, cross-category benchmarking, gap analysis, cross-layer override authority) — Layer 5's use of it here is scoped narrowly to "how does our opening's execution compare on these specific measurable dimensions," not the full Layer 10 system. Building this now is not redundant with Layer 10 — it's the first real implementation of the shared competitor-collection technique, which Layer 10 can and should reuse rather than rebuild.*

**For the competitor set, measure and report:**
- Average motion magnitude (consecutive-frame SSIM, same metric already validated on 008B — lower SSIM = more change)
- Scene/cut frequency (detected via sharp SSIM drops between consecutive frames, distinct from gradual Ken-Burns-style decay)
- Time until product reveal (agent-assessed from frames — when does the product become the clear visual focus, not just partially visible)
- Time until text appears (agent-assessed from frames)
- Presence of human motion (agent-assessed)
- Presence of camera movement (agent-assessed, cross-checked against the SSIM pattern — real camera movement should show a *sustained*, not one-off, elevated change rate)
- Type of motion: organic human/object/camera motion vs. simulated crop-pan on a static image (agent-assessed — this is the dimension a pure SSIM number cannot resolve alone, confirmed by the 008B vs. competitor comparison: both showed a "flat, sustained" SSIM pattern, but one was a mathematically linear pan on one photo and the other was real people/camera moving)
- First-frame strength (agent-assessed)
- Whether the product is shown in real use, not just displayed
- Whether the opening feels native to TikTok Israel or reads as marketplace/catalog content (ties directly to Layer 3's cause (c))

**Required output format** — comparative statements against the aggregate, not just our own numbers in isolation:
- "Our opening motion is at the Nth percentile of successful competitors" / "below the competitor benchmark"
- "Competitors reveal the product after X seconds; we reveal after Y seconds"
- "Our motion is simulated (single-photo crop-pan) while successful competitors use organic human/object/camera motion"
- "Our opening feels like AliExpress catalog material while competitors feel native to TikTok Israel"

**Confidence rule, per the platform-wide Confidence Rules section above:** do not rely on one competitor unless only one relevant competitor can be found after a genuine search. If only one is found, the entire benchmark for that product/category must be labeled `LOW_CONFIDENCE` and stated as such in the output — never presented with the same authority as a real Top-5/Top-10 aggregate.

**Scoping note:** the competitor benchmark is per PRODUCT/CATEGORY, not per variant — all 4 variants of the same product share one competitor set and one benchmark; searching separately per variant would be wasteful and wouldn't change the answer.

**STATISTICAL BENCHMARK ARCHITECTURE (added 2026-07-02, second refinement — supersedes a pairwise "compare to Top 5" framing).** The goal is not "is competitor X better than us" — it's **whether our creative sits above or below the normal standard for successful videos in this category**, established from a real distribution, not anecdotes.

**Collection procedure, per product/category:**
1. Find multiple successful competitor videos — 5–10 preferred, minimum viable smaller but explicitly confidence-reduced (see below).
2. **Market source is tracked, not assumed.** Prefer Israeli/Hebrew TikTok; if insufficient data exists in-market, expand gradually (e.g., to English-language/global content in the same category) — but every competitor's actual market origin (Israeli/Hebrew vs. global/other, judged from caption language, creator handle/bio, hashtags — not assumed from the search query language alone, since a Hebrew query can still surface non-Israeli accounts) is recorded per-competitor, and the benchmark's overall market composition is reported alongside the statistics, not hidden.
3. **Exclusion filter, applied before any video counts toward the benchmark:** exclude videos that are primarily entertainment, memes, or unrelated viral content that merely mention or show the product in passing. The benchmark is built only from videos whose *primary goal* is selling or demonstrating a similar product (checked via: is there a clear product-focused caption/CTA, a "Paid partnership" tag, sustained product focus in the frames reviewed — not just a product appearing incidentally in an unrelated video).
4. Every surviving competitor is measured on the **exact same metrics used for our own videos** — this is what makes the comparison valid, not just convenient.

**Full metric set (expanded 2026-07-02):**
- Motion magnitude (consecutive-frame SSIM)
- Motion type — organic human/object/camera motion vs. simulated crop-pan/zoom (agent-assessed; SSIM alone cannot distinguish these, confirmed by 008B vs. its first competitor both showing a "flat sustained" SSIM pattern for structurally different reasons)
- Scene/cut frequency
- Editing pace (cuts per second of runtime, or average shot length — a derived metric from cut frequency + duration, distinct from raw cut count alone)
- Time until first product reveal
- Time until first benefit demonstration (distinct from product reveal — reveal is "the product is visible," this is "the product is shown doing/solving something")
- Time until first text appears
- First-frame strength (agent-assessed)
- Amount of human presence (agent-assessed)
- Product demonstration quality (agent-assessed — is the product shown actually being used, not just displayed)
- Camera movement (agent-assessed, cross-checked against the SSIM pattern)
- Opening sequence style (a holistic categorization — e.g., "lifestyle/in-use," "studio product render," "screen-recorded listing," "talking-head demo" — not just a binary)
- Native-TikTok-Israel feel vs. marketplace/catalog feel (ties to Layer 3's cause (c))

**Statistics computed across the surviving competitor set, not just per-competitor values:**
- Mean, median, percentile range (e.g., 25th/50th/75th) for each *numeric* metric (motion magnitude, cut frequency, editing pace, reveal/benefit/text timing)
- **Our own variant's percentile placement within that distribution** for each numeric metric — this is the actual deliverable, not the raw competitor numbers in isolation
- For qualitative metrics (motion type, opening style, native-feel), report the **distribution of categories** across the competitor set (e.g., "4 of 5 competitors use organic human/camera motion; 1 uses a simulated pan") rather than forcing a single number

**Required output format:**
- "Our opening motion is at the Nth percentile of the competitor benchmark (n=X videos)"
- "Competitors reveal the product after a median of X seconds; we reveal after Y seconds"
- "X of Y benchmarked competitors use organic human/object/camera motion; we use a simulated crop-pan"
- "Our opening reads as catalog/marketplace style; 0 of Y benchmarked competitors do"

**Confidence rule (strict):** if the benchmark contains too few comparable videos (after exclusion filtering — a category that starts with 8 candidates but loses 5 to the entertainment/meme filter has an *effective* n of 3, not 8) — the output must explicitly reduce confidence rather than overstate a conclusion from a thin sample. Every Layer 5 recommendation must be grounded in this benchmark's actual sample size, stated plainly, not in a single competitor treated as representative.

**CATEGORY-BASED BENCHMARK RULE (added 2026-08-10, fourth refinement — PERMANENT, ACTIVE. Supersedes exact-SKU/exact-product matching as a goal for Layer 5.)** Layer 5 benchmarks successful TikTok videos from the **same narrow product category** as ours — not the identical AliExpress SKU. The purpose of the competitor benchmark is to learn what successful creatives in the same narrow category are doing differently from ours, not to prove a competitor sells the literal same listing. Examples of the narrow-category line: for a magnetic car phone mount, other magnetic car/dashboard/vent phone mounts are valid competitors regardless of brand/model, but phone cases, chargers, and unrelated car accessories are not; for a mini bag sealer, other handheld mini/portable bag or food-bag heat sealers are valid, but sealant paste, plain vacuum-storage bags with no sealing device, suitcases, and industrial sealing machinery are not; for a seat-back organizer, other hanging/multi-pocket car seat-back organizers are valid, but seat cushions, lumbar/back-support cushions, and unrelated car-storage products are not.

A competitor is admitted to the Layer 5 benchmark only if all three gates below hold — exact product/SKU identity is explicitly **not** a required gate:
- `CATEGORY_RELEVANCE_VERIFIED = true` — same narrow category as our product, confirmed by caption/visual content, not just incidental keyword overlap (this is what the 2026-07-02 exclusion filter and this rule's reject examples above are for).
- `FRAME_IDENTITY_VERIFIED = true` — the extracted frames genuinely belong to the claimed URL/creator (guards against the session 18 Bug 4 class of failure: frames captured from the wrong candidate/page).
- Reliable success/performance evidence — a real measured signal (like_count, and view_count/engagement/ranking where available and reliable) that positions the competitor as a genuine success within the candidate pool searched, not a random category-relevant video picked without regard to performance.

Given this, the **Same-Product Visual Identity Gate below is `DEFERRED — NOT REQUIRED FOR THE CURRENT LAYER 5 BENCHMARK GOAL`**: DINOv2/OpenCLIP/exact-SKU visual matching solve a narrower problem (proving identical-product identity) than what Layer 5 now actually needs (narrow-category relevance, already covered by the exclusion filter + `CATEGORY_RELEVANCE_VERIFIED` gate above). Nothing in this section has been installed or implemented; it remains available to revisit if a future need for exact-product matching (e.g. for Layer 10's full market-wide system) makes it worth building.

**CROSS-PRODUCT LEARNING ARCHITECTURE (added 2026-08-11, session 25 — PERMANENT, ACTIVE. Makes the per-product benchmark procedure above, and the cross-product synthesis it feeds, a standing methodology — not a one-off session procedure.)** First proven end-to-end across products 002/003/007/008 (sessions 21-25, see `PROJECT_STATUS.md` and `CREATIVE_GAP_ANALYSIS.md`). Every future product's Layer 5 work — and every future re-synthesis when a new product is added — follows this same pipeline.

**The system's core business question, permanent, unchanged by any single session's findings:**
> "What do successful TikTok videos consistently do that our videos consistently do not — and what should change in the next creative because of that?"

Every layer and every session in this pipeline exists to answer this question with evidence, not to produce diagnostics for their own sake.

**Per-product workflow (permanent):**
1. Identify the product's exact narrow category from its own existing research/config files (not guessed, not re-derived from scratch each time).
2. Find 5 successful, same-narrow-category TikTok videos.
3. `CATEGORY_RELEVANCE_VERIFIED` — per competitor, personally visually confirmed.
4. `FRAME_IDENTITY_VERIFIED` — per competitor, personally visually confirmed (no stale frames, no cross-candidate leakage).
5. Independent automated QA (`layer5_benchmark_qa.py --product-id <pid>`).
6. Full-video creative comparison (not only the opening hook) against our own variants, cross-referencing existing Layer 3 (opening/hook content) and Layer 7 (retention timing) evidence.
7. Identify what successful competitors consistently do that our own videos do not, for this specific product.

**Permanent operating rules for every future product's Layer 5 run:**
- Exact SKU matching is **not** required; same narrow product category **is** required (per the CATEGORY-BASED BENCHMARK RULE above).
- Reliable performance evidence (a real, fetched `like_count`/`view_count`/ranking) **is** required — a random category-relevant video with no success signal is not admissible.
- **`REJECT → NEXT CANDIDATE`** for any irrelevant or wrong-subcategory candidate. Do not perform lengthy forensic investigation on a rejected candidate unless there is direct evidence of a *systemic* bug (e.g. frame-identity contamination, an extraction/tooling failure) — not simple search noise, which is expected and cheap to reject.
- **QA-first workflow, permanent:** `SMALLEST TEST → QA → INSPECT EVIDENCE → SCALE`. Validate the live mechanism on a small scope (e.g. `--target 2`) before committing to a full 5-competitor run.
- **Compare the full video, not only the opening hook** — the opening alone under-counts real differences (e.g. a second creative beat or a payoff/reveal near the end, confirmed to matter in 3 of 4 products so far).
- **Preserve historical evidence permanently.** Never silently overwrite or mix an earlier (possibly pre-methodology or otherwise unverified) benchmark with a newly-QA-verified one — archive the old evidence intact under a clearly dated/labeled subfolder (`layer5_competitor_frames_archive/<date>_<label>/`) before running anything new. Done for all 4 products so far; required for every future re-run.
- **Personally inspect the extracted visual evidence for every admitted competitor.** Category relevance and frame identity are gates, not formalities — captions are frequently placeholder/unusable text across every product checked so far (`"TikTok - Make Your Day"` or empty), so caption-based filtering alone is never sufficient evidence of relevance.

**Cross-product learning pipeline (permanent):**
```
5 successful same-category videos per product
  → QA
  → full-video comparison
  → repeated cross-product differences
  → Permanent Creative Rules
  → combined Layer 3 + Layer 5 + Layer 7 review
  → only then feed approved conclusions into learning_report.json / the creative pipeline
```
A creative difference observed in a single product's benchmark is a **per-product finding**, not yet a rule. A difference that repeats independently across multiple products' benchmarks becomes eligible for classification as a **`PERMANENT CREATIVE RULE`** (unanimous across every product checked, no counter-example), a **`MODIFIED RULE`** (the underlying pattern holds everywhere, but the originally-stated mechanism was too narrow and a later product's evidence forced a broader wording — this is exactly what happened to the "no AliExpress screenshot" rule once product 008 showed the same underlying catalog/CGI-render defect by a different mechanism), or left **`INSUFFICIENT EVIDENCE`** / **`REJECTED`** if the cross-product data doesn't actually support it. **A rule's *revised* wording can itself reach `PERMANENT CREATIVE RULE — revised from the original` status once it has full, unanimous evidence of its own** — the "no AliExpress screenshot" example above was reclassified this way once its broadened wording ("avoid marketplace/catalog-style presentation in any form") gained unanimous 16/16-vs-0/20 evidence across all four products (session 25) — a rule's classification is not frozen at first assignment. `CREATIVE_GAP_ANALYSIS.md` holds the current rule set and its full evidentiary basis — that document's *content* changes as more products are added; this section defines the *architecture* that produces it, and does not change per-session.

**Causality discipline (permanent, platform-wide — extends the Confidence Rules above).** Every conclusion produced by this pipeline must be labeled as exactly one of three tiers, never blurred together:
1. **Direct evidence** — a directly measured/observed fact (a frame's actual content, a competitor's actual fetched `like_count`, a variant's actual retention curve).
2. **Repeated correlation** — a pattern that recurs across independent products/competitors but has not been isolated as a cause (e.g. "the single highest-performing competitor in most benchmarks shows some progression beyond a flat demo" is a repeated correlation across 3 of 4 products checked — not proof that adding such a beat *causes* higher performance).
3. **Hypothesis/recommendation, not yet causally tested** — a proposed creative change grounded in the above, but never validated by an actual before/after test on our own content. **No Creative Rule may be described as "proven to improve performance" until an actual causal test has been run** (e.g. producing and measuring a variant that follows the rule against one that doesn't, on the same product).

**Layer role definitions (permanent, do not conflate):**
- **Layer 3 = WHAT** viewers see in the opening — the actual visual/textual content of the hook, and what's wrong with it in isolation.
- **Layer 5 = HOW** our creative execution differs from real, successful competitors in the same narrow category — the comparative/benchmark layer.
- **Layer 7 = WHEN** viewers leave — the timing of retention loss.

A combined diagnosis reads these three together (what was shown, how it differs from what demonstrably works, and when viewers reacted to it). As of session 25, this combined reading is itself a repeated, four-product correlation — not a proven causal chain — until an actual creative test validates it.

**Future creative-testing requirement (permanent):** once any Permanent/Modified Creative Rule from this pipeline is adopted into the creative pipeline, a future session must design an actual causal test (e.g. producing and measuring a variant that follows the new rule against one that doesn't, holding everything else constant) before that rule may be described as validated rather than a repeated correlation. As of session 25, no rule in `CREATIVE_GAP_ANALYSIS.md` has been causally tested — this is the explicit next gap, not yet closed.

**SAME-PRODUCT VISUAL IDENTITY GATE (added 2026-08-10, third refinement — SPEC ONLY, NOT IMPLEMENTED, NOT INSTALLED. Status as of the same day, later: DEFERRED — NOT REQUIRED for Layer 5's current category-based goal; see the rule directly above.)** The exclusion filter above (2026-07-02) is caption/keyword-based and has a confirmed failure mode: same-*category* competitors pass it because they share incidental keywords, not because they show the same product. Real observed failures: Mini Bag Sealer → sealant-paste and mini-suitcase videos; Seat-Back Organizer → seat-cushion and back-support-cushion videos. This gate adds a mandatory visual check between frame extraction and benchmark admission, so category overlap alone can never be sufficient. Retained here as a deferred design, not required now that Layer 5's goal is explicitly narrow-category (not exact-SKU) benchmarking.

*Reference image set.* Per product, one-time curation (cached, not repeated per competitor): every `assets/{pid}/manifest.json` entry with `asset_type: "product_image"` is classified once by Claude Vision into `CLEAN_PRODUCT_PHOTO` / `INFOGRAPHIC_OR_BANNER` / `PACKAGING` / `SIZE_CHART` / `LIFESTYLE_SCENE`, written back as a new `reference_role` field on the manifest entry. Only `CLEAN_PRODUCT_PHOTO` (required) and `LIFESTYLE_SCENE` (optional secondary) feed the reference embedding set — never the raw gallery unfiltered (contaminated by banners/packaging/size charts), never the main image alone (misses angles a competitor might show).

*Competitor frame set.* Reuses the existing 10-timestamp extraction (`TIMESTAMPS = [0.1, 0.5, 1.0, 1.5, 2.0, 2.5, 3.5, 5.0, 6.5, 8.0]`) and `capture_frame_canvas`/`wait_for_video_ready` unchanged. Late product reveal is handled by scoring, not extra frames by default: the best-matching frame(s) drive the decision, so a talking-head intro before the reveal is simply ignored rather than diluting an average. Adaptive fallback (3 extra frames at `duration*0.5/0.75`, `duration-1s`) triggers only when the best score across the fixed grid lands in the ambiguous/likely band on a video longer than 8s — not on every candidate.

*Matching logic (DINOv2 embeddings, cosine similarity).* `per_frame_max = max(cosine(frame, ref) for ref in reference_set)` for each extracted frame; aggregate as `best_frame_score` (single highest) plus `corroborating_frame_count` (frames independently clearing a secondary threshold). Acceptance requires **both** a high peak **and** corroboration (≥2 independent frames) — never a single-frame spike alone, since that's exactly how a coincidentally similar shape (a sealant tube, a cushion silhouette) could pass by chance in one frame's lighting/angle.

*Identity classes:*
| Class | Assigned by | Meaning |
|---|---|---|
| `SAME_PRODUCT` | DINOv2, deterministic | High score + corroborated — auto-admit, no Claude Vision call |
| `LIKELY_SAME_PRODUCT` | DINOv2 → routed to Claude Vision | Probable match, evidence not conclusive alone |
| `AMBIGUOUS` | DINOv2 → routed to Claude Vision | Mid-band score — the exact zone the known false positives occupy |
| `SAME_CATEGORY_DIFFERENT_PRODUCT` | **Claude Vision only, never DINOv2 alone** | Visually/structurally similar but a different item — hard reject |
| `UNRELATED` | DINOv2, deterministic | Low score — auto-reject, no Claude Vision call |

DINOv2 alone cannot reliably distinguish "same category, structurally similar" from "same product" — that gap is precisely why `SAME_CATEGORY_DIFFERENT_PRODUCT` requires Claude Vision's semantic judgment rather than a score threshold.

*Claude Vision adjudication.* Invoked only for `LIKELY_SAME_PRODUCT`/`AMBIGUOUS` (never for the two deterministic classes — this is what keeps most candidates out of the expensive path). Input: top 1–3 reference images + top 2–3 competitor frames by score. Forced choice among the four non-`AMBIGUOUS` classes, plus confidence and short reasoning. Prompt is explicitly primed with the four known false-positive pairs as calibration examples. Fails closed to `SAME_CATEGORY_DIFFERENT_PRODUCT` on any error/timeout — never silently passes a failed adjudication.

*Product variation handling:* different color / different seller branding / same OEM item via another seller / minor bundled-accessory differences → still admitted (`SAME_PRODUCT`/`LIKELY_SAME_PRODUCT`), Claude Vision instructed to judge structure/function, not color or branding stickers. Newer/older revisions → admitted but flagged `revision_suspected: true`, always forced through Claude Vision regardless of DINOv2 score. Visually similar but structurally different, or same function/different design → `SAME_CATEGORY_DIFFERENT_PRODUCT`/`UNRELATED`, never admitted.

*Evidence schema addition* — new `product_identity` block per competitor (additive to the existing output schema, parallel to the currently-all-null `qualitative_review` block): reference images used, per-frame scores, `best_frame_score`, `corroborating_frame_count`, `classification`, `confidence`, `claude_vision {invoked, decision, confidence, reasoning}`, `frame_identity_verified`, `product_identity_verified`, `decision_reason`, `final_admitted_to_benchmark`. Output splits `competitors[]` (full evidence, every attempt including rejects — nothing silently dropped) from a new `competitors_admitted_to_benchmark[]` (the subset that passed both QA gates below).

*QA — two independent, mandatory gates (extends `layer5_benchmark_qa.py`'s existing 7 PASS/FAIL/WARN checks with two more):*
- **`FRAME_IDENTITY_VERIFIED`** — does this frame actually belong to this TikTok URL/creator? (Guards against session 18's Bug 4 class of failure — frames captured from the wrong candidate.)
- **`PRODUCT_IDENTITY_VERIFIED`** — does this frame actually show the same product being benchmarked?
- A competitor enters `competitors_admitted_to_benchmark[]` (and therefore the statistics above) only if `FRAME_IDENTITY_VERIFIED AND PRODUCT_IDENTITY_VERIFIED`. Both are independent booleans; failing either is a reject, logged with reason, not a silent drop.

*Performance funnel (cheapest first, so Claude Vision cost stays bounded):* keyword/caption filter (existing, free) → frame extraction (existing, unchanged) → DINOv2 local embeddings (new, free after model download, resolves the two deterministic classes for most candidates) → Claude Vision (new, API cost, only the `LIKELY_SAME_PRODUCT`/`AMBIGUOUS` minority, ≤6 images per call). Reference embeddings computed once per product and cached, never recomputed per competitor.

*Security, for whenever this is actually implemented (not yet — no installs performed):* DINOv2 via the official `facebookresearch/dinov2` repo (Meta AI Research) or Hugging Face's verified `facebook` org models, `.safetensors` weights only (pickle/`.bin` formats can execute arbitrary code on load — never accepted from an unverified source); `torch`/`torchvision` (official PyTorch) and `transformers` (official Hugging Face) as the only new dependencies; pinned exact versions, SHA256-verified against the published model-card hash, installed into an isolated venv. Inference runs 100% locally — no product/video data leaves the machine for the DINOv2 stage. The Claude Vision stage does send the selected reference/frame images to Anthropic's API, the same trust boundary already accepted for vision adjudication elsewhere in this pipeline. **Requires explicit user go-ahead before any `pip install` is run.**

---

## Layer 6 — Marketing Angle

*Apply the Israeli Market Context lens: the angle taxonomy below must be judged through Israeli cultural register (directness, self-deprecating humor tends to outperform aspirational/status framing) — a globally-proven angle is not assumed to transfer.*

**Core question:** Is the underlying emotional/practical selling angle — independent of which of the 4 hook *types* was used — the strongest one available for this product?

**Data needed:** full storyboard text (captures the angle actually used); AliExpress review text (mined for the angles real buyers themselves describe); Layer 10's competitor-angle findings.

**Files/pages to inspect:** `output/[date]-product-[pid]-upload_package.md` (all 4 variants' storyboard text); the AliExpress review section; Layer 10's output.

**Metrics / qualitative signals:** angle tagged per variant from a fixed taxonomy — Pain, Convenience, Time-saving, Money-saving, Organization, Status, Safety, Novelty, Parenting, Car-comfort; cross-referenced against CSV performance (currently `INSUFFICIENT DATA` account-wide — no angle has enough repeated samples yet to show a real winner, and this layer must say so rather than guess); match between the angle used and language real reviews use.

**Failure modes:**
- `ANGLE_MISMATCH_WITH_BUYER_LANGUAGE` — the video's angle doesn't match what real reviews describe as the value
- `SINGLE_ANGLE_ACROSS_ALL_4_VARIANTS` — the 4 hook types differ in phrasing but all lean on the same underlying angle, reducing the value of testing 4 variants at all
- `UNTESTED_STRONGER_ANGLE_AVAILABLE` — Layer 10 or review-mining surfaces an angle never tried
- `ANGLE_PROVEN_GLOBALLY_NOT_LOCALLY` — the angle has real evidence from global affiliate marketing or non-Israeli competitor data, but no evidence yet that it works specifically for an Israeli TikTok audience — flag as untested-locally rather than assuming transfer

**Output:** angle-per-variant tag + compelling/not-compelling verdict + a candidate stronger angle, if evidenced (never invented without a citation).

**How it changes the next action:** a stronger untested angle with real evidence → explicitly required as one of Product 009's 4 variant angles — a concrete STEP 6 input, not a vague suggestion.

---

## Layer 7 — Pacing / Retention Diagnosis (extends the current C.F)

**Core question:** Given that the hook worked well enough to get past 2 seconds (or didn't — Layer 3 owns that), *where exactly* does the video lose viewers, and which of four distinct problem types is that?

**Data needed:** `average_watch_time`, `watched_full_video_rate`, `first_2_second_retention` (all populated as of 2026-07-02); **a new collector capability this layer requires** — the retention *curve* sampled at every second, not just the single t=2s point. `tiktok_analytics_collect.py`'s `_extract_first_2_second_retention()` already proved the hover-and-read technique works on TikTok's retention chart; this is a natural, mechanical extension (loop the same hover logic across t=0..15 instead of locking to t=2) rather than new invention. Until that extension exists, Layer 7 must state plainly that it is inferring the drop location from two aggregate numbers, not observing it directly.

**Files/pages to inspect:** same TikTok Studio analytics detail page the collector already reaches, at every second instead of just t=2 (once the extension above exists).

**Metrics / qualitative signals:** the existing STRONG/MARGINAL/WEAK/CRITICAL (2s) and EXCELLENT/GOOD/AVERAGE/POOR (watch-time-rate) bands, unchanged — plus, once the curve exists, direct classification into:
- `OPENING_SEQUENCE_PROBLEM` — most of the total viewer loss happens by the opening window (default: first 3s)
- `MID_VIDEO_PACING_PROBLEM` — drop is spread through the middle of the video, matching neither of the others
- `ENDING_PROBLEM` — a disproportionate share of the loss happens only in the last few seconds
- `VIDEO_LENGTH_PROBLEM` — retention plateaus at a real value before the storyboard's own content even ends, per `data/{pid}-video-config.json` segment timings — the video is simply too long for the content density it has

**Naming correction (2026-07-02, from a real methodology challenge caught during implementation):** the first category was originally named `HOOK_PROBLEM`. That name smuggled in an unsupported causal claim — Layer 7's only input is the retention curve (WHEN viewers leave), never a single video frame, so it cannot and must not name a specific creative cause. Hook concept, product-reveal timing, first-frame quality, movement, editing, and text overlays all live inside the same opening seconds, and distinguishing between them is explicitly Layer 3's and Layer 5's job (they inspect actual frames; Layer 7 does not). Renamed to `OPENING_SEQUENCE_PROBLEM` — a temporal finding, not a diagnosis of which component failed. Layer 7's implementation carries an explicit `cause_unresolved_note` on every `OPENING_SEQUENCE_PROBLEM`/`ENDING_PROBLEM` result stating this in the output itself, not just in documentation — the tool cannot present its own temporal finding as a finished causal diagnosis.

**Failure modes:** the four above, plus the two causes shared with Layer 3 from the current C.F tree — `(f)` too-slow mid-video pacing, `(g)` price-anchoring-too-early (dismissed in the 2026-07-02 analysis for lack of a consistent pattern — this layer should keep re-testing it per product, not assume it's permanently ruled out).

**Output:** per-variant classification across the four problem types + supporting curve evidence (or the explicit "inferred from 2 aggregate points only" caveat until the collector extension ships).

**How it changes the next action:** directly parametrizes STORYBOARD segment lengths for the next video — this was the single most actionable finding in the 2026-07-02 analysis (13 of 16 variants POOR watch-time-rate) and is the most mature layer to implement first.

---

## Layer 8 — CTA / Buyer Intent

*Apply the Israeli Market Context lens: judge CTA clarity against the comment-to-request-a-DM'd-link pattern as it actually works on Israeli TikTok, not a generic international CTA norm.*

**Core question:** Do viewers understand exactly what action to take, and are they taking it?

**`cta_code_comments` is the load-bearing metric of this entire layer, and it has never been collected for a single row in this project's history.** Every product in the current C.G product-type analysis is stuck at `CONTINUE TESTING` — never reaching `SCALE NOW` or `PAUSE SIMILAR` — specifically because CTA activation is `UNKNOWN` for all of them. Analyzer v3 must treat this as the #1 standing data gap, not a minor field: **Layer 8 (and by extension Layer 9) must output `INSUFFICIENT DATA — cta_code_comments not collected` rather than fabricate a conclusion, and Analyzer v3's own QA gate should FAIL a product's diagnosis run if this field is blank**, mirroring how `analyze_qa.py` already fails on other missing-data conditions.

**Data needed:** `cta_code_comments` (manual count from TikTok's own comment section — searching for the CTA code string); the CTA's exact wording/timing/legibility from the video itself.

**Files/pages to inspect:** the video's TikTok Studio comment view, or the public video page's comment section, filtered/searched for the exact CTA code (e.g. "007A"); `data/[pid]-video-config.json`'s final segment (CTA text, timing, position).

**Metrics / qualitative signals:** `cta_comment_rate` = `cta_code_comments ÷ views` (already defined bands in current C.J: `STRONG` >0.5%, `AVERAGE` 0.1–0.5%, `WEAK` <0.1% — simply never populated); qualitative CTA legibility read (Safe Zone compliance, code readability, whether the instruction is unambiguous).

**Failure modes:**
- `CTA_NOT_COLLECTED` — the current universal state; report this explicitly rather than silently proceeding
- `CTA_ILLEGIBLE` — text too small/fast, or violates the Safe Zone rule
- `CTA_AMBIGUOUS_CODE` — bare code without a variant letter (the same identity-ambiguity class already solved for *collection* purposes with Product 002, but distinct here: can a *viewer* tell which variant to reference when commenting?)
- `CTA_TIMING_TOO_LATE` — CTA only appears in the final 1–2s, easy to miss

**Output:** `cta_comment_rate` classification, or the explicit `INSUFFICIENT DATA` state, + any CTA execution issues found independent of the rate.

**How it changes the next action:** `INSUFFICIENT DATA` is itself the action — mandatory manual collection of `cta_code_comments` for the product before Layers 8 and 9 can produce anything else. This should be treated as equal priority to running `/tiktok collect` itself, not an optional enrichment field.

---

## Layer 9 — Click Intent / Link Funnel

**Core question:** Once a viewer decides to act (comments the code), do they receive and click the affiliate link — and if the funnel breaks, where?

**Data needed:** `affiliate_clicks` (CSV column, currently always blank); `cta_code_comments` (from Layer 8, as the funnel's first stage); click data from the affiliate link platform itself — **this is a wholly external data source not currently wired into any script in this codebase.**

**Files/pages to inspect:** the AliExpress Affiliate/Portals dashboard (external — needs its own access/export process, not yet built); each upload package's REPLY REFERENCE TABLE (maps CTA code → `tracking_id` → affiliate link, which is what makes per-variant click attribution possible *if* the affiliate platform reports at the tracking-ID level).

**Metrics / qualitative signals:** comment→click conversion (`affiliate_clicks ÷ cta_code_comments`, bands already defined in current C.J: `HIGH` >50%, `AVERAGE` 20–50%, `LOW` <20%); full funnel staging (views → CTA comments → clicks), also already defined in C.J.

**Failure modes:**
- `LINK_NEVER_SENT` — operational failure: the human didn't reply with the link promptly after a CTA comment (a process failure, not a creative one)
- `LINK_SENT_BUT_NOT_CLICKED` — the reply/link itself didn't compel a click
- `TRACKING_GAP` — no attribution data exists because the affiliate platform's reporting isn't being checked at all (today's actual state)

**Output:** funnel-stage classification + whether the weakest link is upstream (creative/CTA, Layers 3–8's domain) or downstream (operational reply speed / link quality, outside this pipeline's creative scope entirely).

**How it changes the next action:** `TRACKING_GAP` → this becomes a required new manual process (check the affiliate dashboard, log clicks per `tracking_id`) parallel to Layer 8's CTA-counting gap — both are CSV columns that have existed since the v2 schema was introduced and neither has ever actually been populated.

**Sales extension (explicitly deferred, per instruction):** click→sale conversion (`affiliate_sales ÷ affiliate_clicks`, bands already defined in current C.J: `STRONG` >5%, `AVERAGE` 2–5%, `LOW` <2%) activates automatically once `affiliate_sales` exists for enough rows. Until then, this layer's output must state `sales stage: INSUFFICIENT DATA, deferred` explicitly — never fabricate a sales conclusion from zero real sales rows, per the Confidence Rules above.

---

## Layer 10 — Competition / Market Benchmark (mandatory)

*Apply the Israeli Market Context lens (this layer depends on it entirely — see Cross-cutting rules): the comparison set must be TikTok Israel / Hebrew-language creators, not global TikTok.*

**Core question:** Are competitors presenting the same or a similar product in a way that outperforms ours — and specifically how, structurally?

**This is the one layer with no existing data source in this codebase at all** — every other layer extends something that already exists (a CSV column, a QA gate, an output file). Layer 10 requires a new collection surface:

**Data needed:** a set of comparable competitor TikTok videos for the same/similar product (minimum 3–5), **prioritizing Hebrew-language search terms and Israeli creator accounts** (English/global search is a fallback only, and any global-only comparison must be labeled as weaker evidence per the Israeli Market Context rule); TikTok Creative Center (already referenced as a STEP 1 trend-evidence source, so there's precedent for using this account's access to it — filtered to Israel region if that filter is available); their view/like/comment/share/save-when-visible counts; frame-level structure of their first 2 seconds and overall video.

**Files/pages to inspect:** TikTok search results for the product term; TikTok Creative Center Top Ads/Trending (if accessible); individual competitor video pages — frame-extracted the same way this project's own STEP 11B/11D already extracts frames from its own MP4s (the exact same ffmpeg + multimodal-read technique, just pointed at a downloaded/screen-recorded competitor video instead of our own).

**Metrics / qualitative signals:**
- **First 2 seconds:** is the product visible immediately? Is there movement/demonstration?
- **Product presentation:** when is the product first shown; is it demonstrated; is a transformation/before-after shown?
- **Creative structure:** video length, cut frequency, camera angles, close-ups, text overlay style, "wow" moments
- **Marketing angle:** which emotional triggers recur across the competitor set (tagged against the same taxonomy as Layer 6)
- **CTA:** how competitors phrase and time their own call-to-action
- **Engagement:** views/likes/comments/shares/saves-when-visible, buyer-intent language in their comments, common audience reactions

**Failure modes / gap outputs:**
- `EARLIER_PRODUCT_REVEAL` — competitors show the product in frame 1 vs. our hook-text-first approach
- `MISSING_TRANSFORMATION_SHOT` — competitors use before/after and we don't
- `UNUSED_STRONGER_ANGLE` — ties directly to Layer 6
- `WEAK_PRODUCT_NOT_WEAK_PRESENTATION` — the critical differential diagnosis unique to this layer (see below)

**Output:** a structured comparison table (≥3 competitor videos) + an explicit verdict: is our weakness the **product**, the **presentation**, or **both** + a ranked list of specific, concrete gaps to close.

**Cross-layer authority — this is the important architectural point:** Layer 10's verdict can **override** Layer 1, 5, and 6's conclusions. If Layer 1 alone would call a product `Weak` based on our own low views, but Layer 10 shows competitors thriving on the identical product, the diagnosis must flip to "our presentation is weak, not the product" and the recommended action flips from `RETIRE_PRODUCT` to `IMPROVE_CREATIVE`. Conversely, if competitors *also* get mediocre engagement on the same product, that confirms the ceiling is genuinely low and supports `RETIRE_PRODUCT`. **No product should be marked for retirement without a Layer 10 check when competitor videos for it can be found at all.**

---

## Final Recommendation Engine

The output of all 10 layers maps to one action, always with a cited "why." This is a decision table, not a black box — each row names which layers drove it:

| Recommended Action | Triggering layer combination |
|---|---|
| `IMPROVE_CREATIVE` | Layer 1 ≥ Average **and** Layer 10 shows competitors thriving on the same product **and** any of Layers 3/5/6 are weak |
| `RETIRE_PRODUCT` | Layer 1 = Weak **and** Layer 10 shows competitors *also* struggling (or no competitor evidence contradicts it) |
| `REPLACE_CREATIVE_ASSETS` | Layer 4 = `REPLACE_ASSETS` (upstream of Layer 5 — fix this before touching execution) |
| `CHANGE_HOOK` | Layer 3 = CRITICAL/WEAK **and** Layers 4/5 = PASS (assets and execution are fine; the hook choice/text itself is the problem) |
| `CHANGE_MARKETING_ANGLE` | Layer 6 identifies an `UNTESTED_STRONGER_ANGLE_AVAILABLE` with real evidence |
| `IMPROVE_PACING` | Layer 7 pinpoints a `MID_VIDEO_PACING_PROBLEM` or `ENDING_PROBLEM`, other layers otherwise fine |
| `IMPROVE_OFFER` / `RE-SOURCE_LISTING` | Layer 2 = Weak **and** Layer 1 ≥ Average |
| `COLLECT_CTA_DATA` (blocking) | Layer 8 = `INSUFFICIENT DATA` — this must fire before any CTA/click recommendation can be trusted |
| `FIX_FUNNEL_OPERATIONS` | Layer 9 = `LINK_NEVER_SENT` or `TRACKING_GAP` (operational, not creative) |
| `BENCHMARK_COMPETITORS` | Layer 10 has not yet run for this product at all — a prerequisite gap, not a conclusion |
| `SCALE_CURRENT_CREATIVE` | Layers 1–8 all ≥ Average, one hook/angle winning consistently across ≥3 CONFIRMED runs |
| `CONTINUE_TESTING` | Insufficient CONFIRMED data across enough layers to conclude anything else (the default, honest fallback — this is what most current products land on today per C.G, mainly because of the Layer 8 data gap) |

Every recommendation emitted by the engine must restate which layer(s) triggered it and cite the specific evidence from those layers — the recommendation is a pointer back into the 10-layer diagnosis, never a standalone verdict.

---

## Known gaps this spec surfaces (for the record, not yet actioned)

1. **`cta_code_comments` has never been collected** — blocks Layer 8 and, downstream, Layer 9, entirely. Standing #1 priority.
2. **No affiliate click/sale tracking is wired into any script** — Layer 9 requires a new external data source (the affiliate platform's own dashboard) that doesn't connect to this codebase today.
3. **No competitor-video inspection tooling exists** — Layer 10 requires new collection work, though it can reuse this project's existing frame-extraction + multimodal-read technique from STEP 11B/11D once pointed at competitor videos.
4. ~~The retention curve is only sampled at t=2s~~ — **RESOLVED 2026-07-02.** Layer 7 implemented (`scripts/layer7_pacing_diagnosis.py`); the full per-second curve is now extracted and classified into the four problem types. Run across all 16 CONFIRMED variants: 13 of 13 statistically meaningful variants classified `OPENING_SEQUENCE_PROBLEM` (70–86% of total viewer loss concentrated in the first 3 seconds) — a materially different, more specific finding than the aggregate-based C.F analysis produced on the same data.
5. ~~`OPENING_SEQUENCE_PROBLEM` and `ENDING_PROBLEM` are temporal findings only — they cannot yet be causally resolved~~ — **PARTIALLY RESOLVED 2026-07-02.** Layer 3 (`scripts/layer3_hook_diagnosis.py`) implemented and run across all 16/16 CONFIRMED variants with sub-second frame-level cause rating (a/b/c/d/e/h). Layer 5 execution diagnosis (`scripts/layer5_execution_diagnosis.py`) and Layer 5 competitor benchmark (`scripts/layer5_competitor_benchmark.py`) implemented and run on **008B only** (1/16 variants) plus a 4-competitor statistical benchmark for product 008 (1/4 products). Combined findings synthesized in `CREATIVE_GAP_ANALYSIS.md`: cause (c) (catalog/marketplace feel) rated LIKELY in 16/16 variants — the single most universal finding — with zero organic motion and zero human presence confirmed in all 16 of our openings vs. all 4 of the one product's benchmarked competitors. Still open: Layer 5 (execution + competitor benchmark) has not yet run on the other 15 variants or the other 3 products, so the motion/human-presence/native-feel comparison is measured fact for product 008 only and an evidence-consistent hypothesis (not yet a measured fact) for products 002/003/007. `learning_report.json` has deliberately not been updated yet — held pending explicit review of `CREATIVE_GAP_ANALYSIS.md`.
6. **Every category in this account currently has ≤2 products** — several layers (1, 6) will legitimately report `INSUFFICIENT DATA` for cross-product patterns for a while yet; this is expected, not a bug in the spec.
7. **Layer 5's competitor benchmark (product 008) reached 4 of its 5-competitor target, not 10, and none of the 4 valid competitors are confirmed Israeli/Hebrew-market** despite every search query being run in Hebrew (3 English captions, 1 Spanish) — labeled MODERATE confidence and an expanded/global-market benchmark rather than an Israeli-market one, per the Israeli Market Context rule's own expansion clause. A 5th valid competitor's extracted frames were lost to an operator cleanup-script mistake (disclosed in `product008_layer5_competitor_benchmark.json`, not silently dropped). Full Layer 10 (dedicated competition/market benchmark, still not implemented) should eventually supersede this ad hoc Layer 5 benchmark with a purpose-built, larger-sample version.
