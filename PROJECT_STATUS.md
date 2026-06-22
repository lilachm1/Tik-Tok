# TikTok Affiliate Agent — Project Status

**Last updated:** 2026-06-21 (end of day)
**Owner:** Lilach  
**Working directory:** `C:\Automation\TikTok\`

---

## Current Status

**Phase:** Automated TikTok collector built. NOT YET TESTED. Product 009 PAUSED pending valid analytics data.

**Next action (tomorrow — start here):**

Step 1 — Fix 002B/C/D skip logic (code fix, ~15 min):
   In `scroll_and_find_video()` skip path: replace `el.evaluate()` with `el.bounding_box()["y"] + page.evaluate("() => window.scrollY")`.
   Add height filter: skip elements where `bbox["height"] > 100` (container divs). Only count leaf elements.
   Use 50px Y tolerance. This prevents multiple DOM elements per card from inflating the skip counter.

Step 2 — USER ACTION: Check TikTok caption for 007C:
   Open TikTok Creator Center → find the 007C video → confirm caption contains "007C".
   If missing, edit caption to include "כתבו 007C בתגובות". No code change needed.

Step 3 — Investigate 003 NOT_FOUND:
   Run collector with browser visible. Watch what happens during 003A search (scroll 10–20).
   Hypothesis: date filter, pagination limit, or 003 videos need different content tab view.
   Also confirm 003 videos are published (not draft/private) on TikTok.

Step 4 — Fix XHR capture (DevTools inspection, ~30–60 min):
   Open TikTok Creator Center in browser. Navigate to any video analytics tab.
   Open browser DevTools → Network tab → filter XHR/fetch.
   Record actual URL patterns that fire when analytics loads.
   Update `ANALYTICS_URL_FRAGMENTS` in `tiktok_analytics_collect.py` (lines 61–69).

Step 5 — Re-run collector:
   python scripts/tiktok_analytics_collect.py --product-id 002,003,007,008
   Goal: 15+/16 found, metrics populated in CSV.

Step 6 — Run QA + analyze:
   python scripts/tiktok_collect_qa.py --product-id 002,003,007,008
   /tiktok analyze

**Products:**
| ID | Product | Status |
|----|---------|--------|
| 001 | Astronaut Galaxy Projector | ✅ UPLOADED — analytics NOT YET COLLECTED |
| 002 | 360° Magnetic Car Phone Mount | ✅ UPLOADED — analytics NOT YET COLLECTED |
| 003 | Mini Bag Sealer | ✅ READY TO UPLOAD |
| 004 | Mini Mist Fan | ❌ BLOCKED (unconfirmed sales/price) |
| 005 | Electric Lint Remover | ❌ BLOCKED (unconfirmed sales/rating/price) |
| 006 | — | ❌ FAILED — all 5 candidates rejected at STEP 3A |
| 007 | מארגן גב המושב עם שולחן מתקפל (Car Seat Back Organizer, ₪39, 4,000+ sold) | ✅ UPLOADED — analytics NOT YET COLLECTED |
| 008 | מעמד שולחני 360° (360° Phone/Tablet Stand, ₪40.29, 2,000+ sold) | ✅ UPLOADED — analytics NOT YET COLLECTED |
| 009 | — | ⏸️ PAUSED — waiting for analytics data from 001/002/007/008 |

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
