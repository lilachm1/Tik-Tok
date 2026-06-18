# TikTok Affiliate Agent — Full Plan

**Owner:** Lilach  
**Market:** Israel (for now)  
**Video content language:** Hebrew  
**Daily time budget:** 2 hours  
**Products per day:** 1 (agent picks automatically)  
**Commands:** `/tiktok` (morning), `/tiktok collect` (data entry), `/tiktok analyze` (evening analysis + Product 009 decision)

---

## How It Works — Simple Version

**Morning:** Type `/tiktok` — agent researches the product, scores it, generates storyboards, collects AliExpress assets, and outputs 4 silent ready-to-upload MP4 files.  
**You:** Generate your affiliate link (1 min) → open the `videos\` folder → upload the MP4s to TikTok manually.  
**Evening:** Type `/tiktok analyze` + paste your stats — agent tells you what to scale.

**What the agent outputs every morning:**
- 4 silent MP4 files ready to upload (1080×1920, text overlays baked in, no voiceover)
- 4 captions in Hebrew
- Hashtag set
- Your affiliate link instructions
- Full research package saved to `output\`

**What you do manually:**
1. Paste the AliExpress product URL into the AliExpress Link Generator → copy affiliate link
2. Open `C:\Automation\TikTok\videos\` — 4 MP4 files are waiting
3. Upload each to TikTok, add a trending sound, paste the caption + hashtags

---

## MVP Constraints

These apply to the current build. Do not work around them.

| Constraint | Status |
|---|---|
| Voiceover | ❌ Not in MVP |
| AI video generation | ❌ Not in MVP |
| CapCut automation | ❌ Not in MVP |
| Automated TikTok upload | ❌ Not in MVP — TikTok detects bots and bans accounts |
| Review videos as final footage | ❌ Not allowed — research reference only |
| Unique product footage (AliExpress images + screenshots) | ✅ Required |
| Silent MP4 output (4 per run) | ✅ Required |

---

## Output Structure

All files saved to `C:\Automation\TikTok\` (create once during setup).

```
C:\Automation\TikTok\
├── output\                         ← daily research package MD (created by /tiktok)
│   ├── 2026-06-10-product-003.md
│   └── 2026-06-11-product-004.md
├── analysis\                       ← evening analysis MD (created by /tiktok analyze)
│   └── 2026-06-10-product-003-analysis.md
├── data\                           ← persistent data files
│   ├── video_results.csv           ← learning database (appended by /tiktok analyze)
│   └── [PRODUCT_ID]-video-config.json  ← video overlay spec (written by /tiktok Step 6)
├── state\                          ← pipeline resume state (one JSON per product ID)
│   └── [PRODUCT_ID]-pipeline-state.json  ← active run state; deleted/ignored when COMPLETED
├── assets\                         ← collected product assets per run
│   └── [product-id]\
│       ├── images\                 ← downloaded AliExpress product images (min 5)
│       ├── screenshots\            ← price, rating, review count screenshots
│       ├── scroll\                 ← slow page scroll capture (3–4 sec video)
│       └── manifest.json           ← asset index with file list + dimensions
├── videos\                         ← generated silent MP4 files (4 per run)
│   ├── 2026-06-10-product-003-A.mp4
│   ├── 2026-06-10-product-003-B.mp4
│   ├── 2026-06-10-product-003-C.mp4
│   └── 2026-06-10-product-003-D.mp4
├── qa\                             ← QA reports per run
│   └── 2026-06-10-product-003-qa.md
└── scripts\                        ← Python automation scripts
    ├── generate_assets.py          ← Playwright: collect AliExpress assets
    └── generate_videos.py          ← MoviePy/FFmpeg: compose silent MP4s
```

**output/** — Created by `/tiktok`. Contains the full research package: product ID, trend evidence, AliExpress URL, commission rate, research video references, all 4 storyboards, captions, hashtags, and MP4 output paths with QA status.

**assets/** — Created by `/tiktok` Step 8. All footage comes from here. Never from third-party review videos.

**videos/** — Created by `/tiktok` Step 9. The 4 files the user uploads to TikTok.

**qa/** — Created by pre-generation and post-generation QA steps. Contains check results, retry counts, and any FAILED flags.

**data/** — `video_results.csv` is the learning database. `[PRODUCT_ID]-video-config.json` is the interface between the agent and the video scripts.

---

## Persistent Learning — How It Works

The agent builds a performance database over time instead of treating each day as a fresh start.

**After each `/tiktok analyze`:** All variant statistics are appended to `data/video_results.csv`.

**Before each `/tiktok` product selection:** The agent reads the CSV and calculates — using CONFIRMED rows only (72h+):
- Best performing hook type → bonus for matching products; winning hook moved to Variant A
- Best performing category → +2 bonus on scoring
- Best performing price range → +1 bonus on scoring

**72-hour rule:** Only rows where `variant_status = CONFIRMED` (uploaded 72+ hours ago) influence long-term learning. NEW and TESTING rows are saved and shown as early signals but do not affect recommendations or confidence scores.

**CSV columns:**
```
product_id,variant,hook_type,category,price_ils,views,likes,comments,saves,winner,cta_style,asset_source,best_segment,upload_date,upload_time,age_hours,variant_status,tracking_id,affiliate_clicks,affiliate_sales,affiliate_commission
```

`cta_style`, `asset_source`, `best_segment`, `affiliate_clicks`, `affiliate_sales`, and `affiliate_commission` are optional. `upload_date` and `upload_time` are required at analysis time. `age_hours`, `variant_status`, and `tracking_id` are computed/generated automatically.

`variant_status` values: `NEW` (0–23h) / `TESTING` (24–71h) / `CONFIRMED` (72h+)

`tracking_id` format: `product[product_id]_[variant letter]` — always filled, never blank.

**Winner override rule:** If `affiliate_sales` data exists for any variant, sales override engagement metrics when choosing the winner. If no sales data, engagement (views + saves + comments) decides as normal.

Example rows:
```
product_id,variant,hook_type,category,price_ils,views,likes,comments,saves,winner,cta_style,asset_source,best_segment,upload_date,upload_time,age_hours,variant_status,tracking_id,affiliate_clicks,affiliate_sales,affiliate_commission
002,002A,Price Shock,Mobile Phone Accessories,45,1200,89,34,67,false,comment,,,2026-06-10,19:30,96,CONFIRMED,product002_A,45,0,0
002,002B,Curiosity,Mobile Phone Accessories,45,3400,234,89,145,true,comment,main product image,0-2s hook,2026-06-10,19:30,96,CONFIRMED,product002_B,120,3,12.5
003,003C,Problem/Solution,Interior Accessories,35,5100,412,167,290,true,dm,,,2026-06-13,20:00,18,NEW,product003_C,,,
```

---

## Product Scoring — Israeli Impulse-Buy Market

Target: products that make people say **"That's cheap, I'll try it."** — not "I need to think about it."

### Price Scoring

| Price | Score | Notes |
|-------|-------|-------|
| Under ₪15 | **HARD REJECT** | Commission/sale below ₪1.05 — not commercially viable |
| ₪15–₪24 | 6 | Acceptable only with 9% commission category |
| ₪25–₪40 | 10 | Good balance of impulse + commission |
| ₪40–₪65 | **12 (PREFERRED)** | Best commission-to-impulse balance |
| ₪65–₪80 | 9 | Viable with strong problem/solution angle |
| ₪80–₪120 | 5 | Exceptional trend evidence required |
| Over ₪120 | **HARD REJECT** | Too high for TikTok impulse behavior |

### Minimum Commission Screen
Before scoring any candidate, compute: expected_commission_per_sale = price × commission_rate ÷ 100
- If < ₪1.50 → remove from shortlist (COMMISSION TOO LOW)
- If all 5 candidates fail → relax to ₪1.00 minimum

### Price Rules
- **Preferred range:** ₪25–₪65 (best commission per sale while remaining impulse-friendly)
- **Acceptable range:** ₪20–₪80
- **Hard reject below ₪15** — commission per sale below commercial viability threshold
- **Hard reject above ₪120** — too high for impulse purchase behavior
- Tie-breaking: when two products are within 1 point, pick the one with higher expected commission per sale; if equal, pick the cheaper one
- Goal: maximize profitable affiliate revenue while preserving impulse-buy behavior — NOT maximum conversions at any price point

### Preferred Product Types (impulse-buy friendly, +1 bonus)
- Small home gadgets
- Mobile accessories
- Organization products
- Pet accessories
- Beauty accessories
- Children's accessories

---

## Trend Validation Rule

**A product is only valid if it appears in at least 2 evidence sources.**

Valid source combinations (examples):
- TikTok Search + AliExpress Best Sellers
- TikTok Creative Center + AliExpress Trending
- Google Trends Israel + TikTok Search
- AliExpress Best Sellers + TikTok Creative Center

**Do not recommend a product that appears in only one source.**

For each product, the agent must show:
1. Trend evidence source 1 — with specific evidence
2. Trend evidence source 2 — with specific evidence
3. AliExpress demand proof — orders count, rating, reviews count
4. TikTok content proof — number of videos found, comment themes, repeated appearances

---

## What the Agent Does Automatically

### `/tiktok` — Morning Command

| Step | What the Agent Does | You Do |
|------|---------------------|--------|
| 0A | **Auto-assign PRODUCT ID** — scans output/, data/, videos/ for highest existing ID, sets next run to highest + 1 (zero-padded to 3 digits). No manual update needed. | Nothing |
| 0A-R | **Resume Check** — immediately after PRODUCT ID is assigned, checks for `state/[PRODUCT_ID]-pipeline-state.json`. If found with status IN_PROGRESS: shows resume banner, skips STEP 0/0B/0C/1, restores shortlist from state, jumps directly to the saved step. If found COMPLETED/FAILED: starts fresh. If not found: starts fresh, state file will be created at end of STEP 1. | Nothing |
| 0 | Reads `video_results.csv` — calculates best hook type, category, price range from CONFIRMED rows only (72h+ rule) | Nothing |
| 0B | **Winner Scaling Check** — if a WINNING PRODUCT exists (2+ CONFIRMED variants, 20%+ above account average), shows 3–5 scaling variant ideas before proceeding to new product search | Nothing |
| 0C | **Product Exclusion Check** — scans all upload packages to build exclusion list. HARD REJECT on item ID / URL / name match. SOFT REJECT on same product type + same price tier. Skipped for explicit scale/retry runs. | Nothing |
| 1 | Finds 5 trending products (must have 2+ trend sources each), scores using price model + history bonuses. Writes state file after shortlist is finalised. | Nothing |
| 1 — TODO | **Trend Source Audit** (pending — run after Product 006 completes): verify TikTok evidence is the primary driver of candidate selection and AliExpress bestseller data is secondary validation only. Per-candidate record required: TikTok search terms used, number of TikTok videos found, common comment themes, trend evidence sources, AliExpress evidence sources, final scoring breakdown. Risk: pipeline may be drifting toward AliExpress-first discovery. | Manual review |
| 3C — REVERTED | **Tier 2C experimental rule REVERTED (2026-06-16):** 1-domain rule produced a false positive immediately (item 1005006288564334 on de.aliexpress.com = dead page). Post-mortem conclusion: regional domain indexing is stale cache same as main .com. ALL Google-based liveness signals (Tier 1, 2A, 2B, 2C) are unreliable. Tier 2C restored to 2-domain rule and marked pending replacement. | Resolved |
| 3A — ACTIVE | **Playwright Liveness Check (STEP 3A, implemented 2026-06-16):** New step between STEP 3 (safety) and STEP 3B (validation). Runs `generate_assets.py --check-only`. DEAD → reject immediately, no HVM. LIVE + hard blocks all pass → skip STEP 3B/3C entirely, proceed to STEP 4. LIVE + sold count UNCONFIRMED → fall through to STEP 3B for confirmation. UNKNOWN (script error/timeout) → fall back to STEP 3B. Dead page detection: renders page, checks body text + URL redirect. Data extraction: JS globals → CSS selectors → regex text scan. Phase 2 validated: DEAD test ✅, LIVE test ✅ (sold/rating/price all correct). | Nothing |
| 2 | Finds best AliExpress listing. **LISTING SELECTION PRIORITY:** 1. Highest confirmed sales 2. Highest rating 3. Verified live listing 4. Price 5. Feature set. Features (LED, USB, premium version etc.) are tie-breakers only — never choose lower sales for more features. | Nothing |
| 3 | Safety check — no fake brands, no copyright risk | Nothing |
| 3B | **Product Validation Check (mandatory)** — two-path validation: Path A uses WebFetch to confirm product title + price; Path B (AliExpress JS wall) runs fallback Google search. Flags fallback candidates (non-#1 picks) for stricter validation in STEP 3C. **AUTOMATED VALIDATION LIMITS:** 10 searches / 5 fetches / 3 item IDs / 5 min per candidate — first limit reached triggers HVM immediately. Auto-rejects on any critical check failure. | Nothing |
| 3C | **Final Listing Consistency Check (mandatory)** — automated validation (5 sources); if any field UNCONFIRMED → **HVM URL VALIDATION GATE** (confirm listing is live on AliExpress before showing URL) → **Human Verification Mode** (user opens URL, provides 4 fields). Verifies sales ≥ 1,000, rating ≥ 4.5★, images ≥ 5. **UNCONFIRMED sales = HARD BLOCK.** Dual UNCONFIRMED escalation: 2+ fields → reject. Fallback candidates require ALL fields confirmed. Ends with CONFIRMATION COMPLETENESS EVALUATION. State file updated at each listing outcome and at HVM trigger. | Open URL if prompted for HVM |
| 5 | Prepares AliExpress product URL + category + commission rate for manual link generation | Nothing |
| 6 | Finds review videos for **research reference only** — not used as footage | Nothing |
| 7 | Generates 4 video variants — winning hook assigned to Variant A | Nothing |
| 7b | Writes storyboard + caption + hashtags for each of the 4 variants (Hebrew) | Nothing |
| 7c | Writes `data/[PRODUCT_ID]-video-config.json` (text overlay interface for scripts) | Nothing |
| 8 | **Pre-generation QA — Technical + Content + Thumbnail (9 checks total)** — Technical (1–4): image count, storyboard completeness (incl. canonical product term consistency, benefit coherence, variant-level CTA codes + gender-neutral Hebrew), hook distinctiveness, config integrity. Content (5–8): price consistency + confirmation status check (unconfirmed → replace with "מחיר מפתיע"), social proof accuracy, Hebrew text quality + product noun consistency, output package consistency + caption product noun match. Thumbnail (9): hook readable in profile crop. VIDEO QA PASS requires all 9. | Nothing |
| 8B | **Asset Identity Gate (new)** — 5-check gate after asset collection: main image present (001_main.jpg), minimum 4 usable images, anomalous file size detection, non-sequential numbering detection, screenshot coverage. Warnings written to upload package UPLOAD STATUS. FAILED on < 4 usable images → stop run. | Nothing |
| 9 | **Unique asset generation** — runs `generate_assets.py`: downloads AliExpress product images, price/rating screenshots, slow scroll capture → `assets/[PRODUCT_ID]/` | Nothing |
| 10 | **Silent video generation** — runs `generate_videos.py`: composes 4 MP4s from assets + text overlays via MoviePy/FFmpeg | Nothing |
| 11 | **Post-generation QA** — verifies all 4 MP4s (existence, duration 13–17s, file size, resolution), up to 3 retries per variant | Nothing |
| 11B | **Visual Composition QA** — extracts 8 frames per variant (0s, 1s, 3s, 5s, 7s, 9s, 11s, 14s) via ffmpeg, opens each with Read tool, evaluates 6 criteria: Hook Power, Visual Composition, Product Dominance, Screenshot Evidence Quality, English Contamination, TikTok Native Feel. PASS/WARNING/FAIL per frame and per variant. FAIL = upload blocked + re-render required; WARNING = CEO review required before upload. | Nothing |
| 11C | **Frame Sequence Visual QA** — evaluates the 8 frames extracted in STEP 11B as a sequence proxy for the video's story structure and conversion logic. NOT a motion review — does not assess timing feel, pacing, or transition smoothness in real playback. 12 criteria: First-Second Clarity, Scroll-Stopping Power, Hook-to-Product Match, Story Flow, Text Timing (estimated from config), Transition Feel (from boundary frames), Product Clarity, Benefit Clarity, Trust/Proof Clarity, CTA Strength, Mobile-View Realism, Overall Upload Judgment. Outputs per variant: PASS/WARNING/FAIL per criterion + 7 scores (Hook, Clarity, Flow, TikTok-native, CTA, Trust, Overall 1–10) + upload priority ranking #1–#4. FAIL or WARNING with score < 6 = upload BLOCKED; WARNING with score ≥ 6 = CEO review. Precedes STEP 11D. | Nothing |
| 11D | **Full Motion Video Review (Automated)** — Agent-executed Gate 5 using 1fps frame extraction from the actual MP4 files. Extracts 15 frames per variant (ffmpeg fps=1), reads all 60 frames via multimodal image analysis, evaluates 12 criteria: Scroll-Stopping Power, Product Clarity within 1s, Hook Effectiveness, Story Flow, Text Readability in Motion, Text Timing, Transition Quality (consecutive frame comparison), Product Dominance Throughout, Trust/Proof Clarity, CTA Effectiveness, TikTok-Native Feel, Final Upload Judgment. Outputs per variant: PASS/WARNING/FAIL per criterion + 6 scores (Hook, Clarity, Flow, TikTok-Native, CTA, Overall 1-10) + revised upload priority ranking. FAIL (any FAIL criterion OR WARNING + Overall < 6) = upload BLOCKED. WARNING + Overall ≥ 6 = CEO review. PASS = proceed to STEP 11. Honest scope: strongest automated review an agent can perform; cannot replicate real-time pacing feel; human phone review available as optional supplement for WARNING on criteria 1, 6, or 7. | Nothing |
| 12 | Saves full package to `output/YYYY-MM-DD-product-XXX.md` | Nothing |
| 13 | Shows complete ready-to-use package in chat with MP4 file paths and QA status | Nothing |
| — | Paste AliExpress product URL into AliExpress Link Generator → generate 4 tracking-ID links (TikTok[ID]A/B/C/D) → fill REPLY REFERENCE TABLE in upload package | **You (1 min)** |
| PRE-UPLOAD | **Pre-Upload Human Review Agent** — mandatory final gate triggered when user declares readiness to upload. Reads upload package + all QA gate results. 12 checks: affiliate links complete, CTA/link match, caption quality, hashtag relevance, STEP 11B/11C status, upload order, video files present, product data accuracy, upload timing advisory, CEO judgment, completeness. Verdict: APPROVED TO UPLOAD ✅ / BLOCKED ❌ / NEEDS CEO REVIEW ⚠️. BLOCKED if: affiliate links missing, STEP 11C not run or any FAIL, CTA mismatch, video files missing. APPROVED TO UPLOAD is the only verdict that unambiguously permits publishing. | Type "ready to upload Product [ID]" |
| — | Open `C:\Automation\TikTok\videos\` — 4 MP4 files ready | **You (30 sec)** |
| — | Upload each MP4 to TikTok in STEP 11C priority order, add trending sound, paste caption + hashtags | **You (5–10 min)** |

### `/tiktok analyze` — Evening Command

| Step | What the Agent Does | You Do |
|------|---------------------|--------|
| 1 | Asks for your video stats + upload date/time + optional affiliate data | Paste: views, likes, comments, saves, upload date, upload time (per variant). Optionally: affiliate clicks, sales, commission per variant. |
| 2 | Analyzes performance — uses affiliate sales as winner if available, otherwise engagement | Nothing |
| 3 | Analyzes which product category is performing | Nothing |
| 4 | Tells you what to repeat tomorrow | Nothing |
| 5 | Tells you what to drop | Nothing |
| A | Appends all variant results to `data/video_results.csv` — auto-fills tracking_id; computes age_hours + variant_status | Nothing |
| B | Saves analysis to `analysis/YYYY-MM-DD-product-XXX-analysis.md` | Nothing |
| C | **Quality & Learning Agent** — runs CONFIRMED-only pattern analysis, asset/segment learning, product status table, confidence score | Nothing |
| C.E | **Product Status** — classifies each product as NEW / TESTING / WINNING / RETIRED based on CONFIRMED data vs account average | Nothing |
| D | **Weekly Audit** — if 7+ CONFIRMED rows exist and 7 days since last audit: saves `analysis/weekly-audit-YYYY-MM-DD.md` with top products, variants, patterns, and what to scale/stop | Nothing |

---

## Agent Components

### Unique Asset Generation Agent (Step 9)

**Purpose:** Collect all product visuals from AliExpress so every video uses original footage — never borrowed from review clips.

**Tool:** `scripts/generate_assets.py` (Python + Playwright + headless Chromium)

**What it collects:**
- All product images from the listing (min 5, max 12) → `assets/[PRODUCT_ID]/images/`
- Screenshot of main product image area → `screenshots/main.png`
- Screenshot of price section → `screenshots/price.png`
- Screenshot of star rating + review count → `screenshots/rating.png`
- Top 2 written reviews if visible → `screenshots/review1.png`, `review2.png`
- Slow page scroll capture (3–4 sec) → `scroll/scroll.mp4`
- Asset manifest → `manifest.json`

**Failure threshold:** If fewer than 5 images are collected after 3 retries → `FAILED — REQUIRES HUMAN REVIEW`

---

### Silent Video Generator Agent (Step 10)

**Purpose:** Compose 4 silent MP4 files from collected assets and storyboard text specs.

**Tool:** `scripts/generate_videos.py` (Python + MoviePy + FFmpeg)

**Inputs:**
- `data/[PRODUCT_ID]-video-config.json` — text overlay spec (segment timing, Hebrew text, color, position)
- `assets/[PRODUCT_ID]/manifest.json` — available asset files and dimensions

**Output per variant:**
- 5 segments assembled per storyboard timing
- Hebrew text overlays baked into video (color + position from config)
- No audio track
- Format: 1080×1920 px, H.264, 30fps, `.mp4`

**Output files:** `videos/[YYYY-MM-DD]-product-[PRODUCT_ID]-A/B/C/D.mp4`

**Font requirement (one-time setup):** A Hebrew-compatible `.ttf` font must be installed and its path set in `generate_videos.py` (see Setup section below).

---

### Quality & Learning Agent (Step C in `/tiktok analyze`)

**Purpose:** Close the feedback loop between video generation approach and TikTok performance over time.

**What it does:** After performance stats are entered, optionally asks:
- "Which asset type felt most engaging? (main product image / in-use shot / close-up detail / price screenshot)"
- "Which segment do you think drove the most saves? (0–2s hook / 2–5s price / 5–9s benefit / 9–13s social proof / 13–15s CTA)"

**Both questions are optional.** The user can skip them. If answered, the agent writes the values to the `asset_source` and `best_segment` columns in `video_results.csv`.

**Over time:** The agent reads these columns and can recommend which image type and segment style to lead with for similar products.

---

## Retry Logic

All QA checks and script-based steps follow the same retry pattern:

1. Run the check or script
2. If it fails: note the specific failure, attempt a fix, and rerun
3. Retry up to **3 times total** per individual check
4. If still failing after 3 attempts: mark as **FAILED — REQUIRES HUMAN REVIEW** and:
   - If it is a single variant: flag it, continue with remaining variants
   - If it is a blocking step (asset generation, fewer than 3 videos generated): stop the entire run

**Pass thresholds for post-generation QA:**
- 4/4 variants pass → full run success
- 3/4 variants pass → partial success, flag the failed variant
- Fewer than 3 pass → entire run marked FAILED — REQUIRES HUMAN REVIEW

---

## Before You Start — One-Time Setup

### Folder and Command Setup (5 minutes)

1. Create the project folder structure:
   ```
   C:\Automation\TikTok\
   C:\Automation\TikTok\output\
   C:\Automation\TikTok\analysis\
   C:\Automation\TikTok\data\
   C:\Automation\TikTok\assets\
   C:\Automation\TikTok\videos\
   C:\Automation\TikTok\qa\
   C:\Automation\TikTok\scripts\
   ```

2. Verify both slash commands exist:
   - `.claude/commands/tiktok.md` ← Morning agent prompt
   - `.claude/commands/tiktok-analyze.md` ← Evening agent prompt

### Technical Setup for Video Generation (15–20 minutes)

These are required before Steps 9–10 of `/tiktok` will work.

```
# Python dependencies
pip install moviepy playwright requests

# Playwright browser (headless Chromium)
playwright install chromium

# FFmpeg — download from ffmpeg.org and add to PATH
# Verify with: ffmpeg -version

# Hebrew font — needed for text overlays
# Option A: Use a system font that supports Hebrew (e.g. Arial, David, Tahoma)
# Option B: Download a free Hebrew TTF (e.g. Noto Sans Hebrew from Google Fonts)
# Set the font path inside scripts/generate_videos.py after it is created
```

**Verify the setup works:**
```
python -c "import moviepy; print('MoviePy OK')"
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
ffmpeg -version
```

### Script Status

| Script | Status |
|--------|--------|
| `scripts/generate_assets.py` | ✅ Implemented and tested (2026-06-11) |
| `scripts/generate_videos.py` | ✅ Implemented and tested (2026-06-11) |

Both scripts are operational. Full end-to-end `/tiktok` pipeline (Steps 0–12) tested successfully on 2026-06-11 (product 001 — Astronaut Galaxy Projector). 4/4 MP4 variants generated, 1080×1920 H.264, 15s, no audio.

**2026-06-14 — Critical logic + Content QA bugs fixed:** Three bugs found during product 002 run. (1) STEP 3B validated URL existence only — never verified the specific listing's own sales/rating metrics; product 002 final listing had 1 sold / 2 reviews, failing the 1,000+ requirement. (2) Research-phase estimated price (~25₪) leaked into video overlays without reconciliation; actual price was ₪60.66. (3) False social proof: "1,200 אנשים" from category research used in overlay when listing had 1 sold. Fixes: STEP 3C added (Final Listing Consistency Check), PRICE RULE + SOCIAL PROOF RULE + HEBREW TEXT QUALITY RULE added to STEP 6, Content QA checks 5–8 added to STEP 7, VIDEO QA PASS now requires both Technical QA and Content QA.

**2026-06-14 — Emoji root cause fix:** `generate_videos.py` now strips all non-BMP Unicode characters (codepoints > U+FFFF, i.e. all emoji) from text before rendering via `strip_unsupported_chars()` called at entry of `build_text_layer()`. Tahoma has no glyphs above U+FFFF — this was causing broken-square artefacts. Hook/CTA/JSON templates in `tiktok.md` also cleaned (emoji removed from video-overlay text; caption templates unchanged — TikTok captions support emoji natively).

**2026-06-14 — Content rules + pipeline standards (7 new permanent rules):** (1) GENERAL AUDIENCE COPY RULE — all Hebrew copy gender-neutral throughout; no female-only forms in any template. (2) PRODUCT NUMBER CONSISTENCY RULE updated — CTAs now variant-level "[PRODUCT_ID][VARIANT]" (e.g. "כתבו 003A בתגובות"); shared codes across variants permanently prohibited. (3) REPLY MANAGEMENT RULE — REPLY REFERENCE TABLE (CTA code → tracking ID → affiliate link) required at top of every upload package. (4) CHECK 9 (Thumbnail QA) added — hook text must be readable in TikTok profile thumbnail crop; first 3–4 words must convey the full message. (5) CHECK 7 expanded — full HEBREW TEXT QUALITY + AUDIENCE check (natural conversational Hebrew, gender-neutral). (6) Final QA checklist expanded to 9 checks. (7) REPLY REFERENCE TABLE format standardised in upload package template.

**2026-06-14 — Products 002 and 003 complete:** Product 002 — Plug Adapter (item 1005010033519251), ₪23, 10,000+ sold, 4 variants generated, 4 affiliate links assigned (product002_A/B/C/D), READY TO UPLOAD. Product 003 — Mini Bag Sealer (item 1005006860946828), ₪8, 100,000+ sold, 4 variants generated, 4 affiliate links assigned (product003_A/B/C/D), READY TO UPLOAD.

**2026-06-18 — Three new permanent QA rules:**

**TIKTOK UI SAFE ZONE RULE (generator-level fix + permanent QA):** `generate_videos.py` "top-center" position was rendering at `y_start=100`, placing hook text inside the top 15% of the 1920px frame (danger zone = top 288px, covered by TikTok's search bar and tab UI). Fixed to `y_start=320`. Rule: no critical text may appear in the top 288px. QA check: extract frames at 0s, 1s, 3s; hook text must be fully below y=288. Violation = FAIL → re-render. This is a global generator fix — applies to all future products automatically.

**SCREENSHOT EVIDENCE RULE (permanent storyboard + QA rule):** Overlay text must not cover the key proof elements a screenshot is meant to prove. Root cause: "center" position at y≈960 lands directly on the price screenshot band (y≈836–1084 on 1920px canvas) and covers written reviews in the rating screenshot. Fix applied globally to STORYBOARD defaults: price screenshot segments use "top-center" (text above strip); rating screenshot segments use "bottom" (text below reviews, rating breakdown visible at top). QA check added at 4s (price) and 11s (rating) — if overlay covers price, star rating, or review content → FAIL → reposition → re-render. Added to `tiktok.md` STORYBOARD position column and FRAME SAMPLING checklist.

**PRODUCT VISIBILITY RULE (permanent storyboard + QA rule):** Overlay text must not obscure the primary product subject. The product must remain visually dominant in every product-image frame. Root cause: "center" position at y≈960 places text dead-center where most products sit. Rule: use "bottom" for benefit/detail segments (6–9s) when product occupies the center of the image. Screenshot frames (price, rating) are exempt — overlay reinforcing screenshot data is by design. QA check: extract 7s frame for all variants; if overlay covers the product → FAIL → move to "bottom" → re-render. Added to STORYBOARD section and FRAME SAMPLING QA checklist in `tiktok.md`.

---

## Command Reference

The full agent prompts live in the slash command files. Do not maintain a second copy here.

| Command | File | Steps |
|---------|------|-------|
| `/tiktok` | `.claude/commands/tiktok.md` | Steps 0–12 (research → QA → asset gen → video gen → output). STEP 11D v2 active. |
| `/tiktok collect` | `.claude/commands/tiktok-collect.md` | NEW: Performance Data Collector. Enters TikTok Analytics stats → video_results.csv v2 (33 cols). |
| `/tiktok analyze` | `.claude/commands/tiktok-analyze.md` | Analysis → CSV → Quality & Learning (C.A–C.J) + Step E Product 009 Decision Layer. |

---

## Your Daily Routine

```
MORNING (~15 minutes total):
  1. Open Claude Code
  2. Type /tiktok
  3. Wait 3–5 minutes for the agent to finish all steps
  4. Read the package in chat (also saved to output\ folder)
  5. Paste the AliExpress product URL into AliExpress Link Generator → copy affiliate link
  6. Open C:\Automation\TikTok\videos\ — 4 MP4 files are waiting
  7. Upload each MP4 to TikTok → add trending sound → paste caption + hashtags
  8. Schedule uploads between 19:00–21:00 Israel time

EVENING (~5 minutes):
  1. Open TikTok analytics
  2. Copy your stats (views, likes, comments, saves) for each variant
  3. Open Claude Code
  4. Type /tiktok analyze
  5. Paste your stats + product category + price
  6. Optionally answer the asset/segment observation questions (or skip)
  7. Read what to do tomorrow
```

---

## Week-by-Week Plan

### Week 1 — Setup and First Videos

| Day | Goal |
|-----|------|
| Day 1 | Create folder structure. Verify slash commands exist. Complete technical setup (Python, FFmpeg, Playwright, font). |
| Day 2 | First real `/tiktok` run. Scripts may not be ready — agent outputs research + storyboards. Upload manually using AliExpress images. |
| Day 3 | First `/tiktok analyze`. First rows written to `video_results.csv`. |
| Day 4 | Implement `generate_assets.py`. Test asset collection on a live AliExpress listing. |
| Day 5 | Implement `generate_videos.py`. Test MP4 output for one variant. |
| Day 6–7 | Full pipeline end-to-end. Agent outputs 4 MP4s per run. |

### Week 2 — Learn What Works

- Agent reads `video_results.csv` each morning — patterns emerge after 5–7 data points
- You know which hook style works for your audience
- You know which product categories get engagement
- Price scoring is calibrated to Israeli impulse-buy behavior
- Optional asset/segment observations from `/tiktok analyze` start surfacing visual patterns

### Week 3+ — Start Scaling

- Agent's recommendations are history-informed, not generic
- Consider 2 products per day if the routine feels easy
- Agent starts recommending similar products to historical winners
- Prepare for English version

---

## The Rules

**Always:**
- Generic products only — no brand logos
- 1,000+ sales on AliExpress before promoting
- Prioritize 9% commission categories — more earnings per sale
- Prioritize products under 50₪ — impulse-buy zone
- Validate trend in 2+ sources before selecting any product
- Final videos must use unique product assets (AliExpress images, screenshots, scroll capture) — do not use third-party review footage as the main video footage
- Do the evening analysis every day — this is how the agent learns
- Upload every day — consistency beats perfection

**Never:**
- Fake brand logos (ALO, Nike, etc.) → ban + legal risk
- Use review video footage as final video content → use AliExpress product images instead
- Automate the TikTok upload → TikTok detects bots and bans accounts
- Skip the evening analysis — without it the agent cannot learn
- Suggest 3% commission products when a good 7%–9% option exists
- Recommend a product from only 1 trend source
- Select a product over 80₪ without exceptional evidence

---

## When to Scale to English

Only after you have in Israel:
- [ ] At least one video with 1,000+ views
- [ ] Comments asking "מאיפה קונים?" or "שלחי לינק"
- [ ] At least one confirmed affiliate click
- [ ] One hook style that worked more than once
- [ ] At least 10 rows in `video_results.csv` showing a clear pattern
- [ ] The agent's analysis pointing clearly at a winning hook + category combo

Then duplicate the same system in English.

---

## The Secret

> It is not about finding a perfect product.  
> It is about finding the right ANGLE — and then running experiments fast.

The agent gives you one strong experiment every morning.  
The analyzer tells you each evening what to double down on.  
You upload. The system learns. Results compound.

---

*Updated: 2026-06-16 — Validation reliability + Resume Mode. (1) HVM URL VALIDATION GATE added: before triggering Human Verification Mode the pipeline must confirm a direct aliexpress.com/item/[ID] result appears in Google search — alitools.io or brand-website-only results = FAIL, listing silently rejected, return to STEP 2, URL never shown to user. Root cause: Product 006 showed user a dead URL (item 4001293078470) that existed only in third-party caches. (2) LISTING SELECTION PRIORITY added to STEP 2: when multiple variants/listings exist, selection order is Highest Sales → Rating → Verified Live → Price → Feature set. Features (LED, USB, cup holder, premium versions) are tie-breakers only — lower-sales listing must not win over higher-sales listing due to extra features. (3) STEP 0A-R RESUME MODE added: pipeline checks for state/[PRODUCT_ID]-pipeline-state.json immediately after product ID is assigned. If IN_PROGRESS: restores full shortlist, skips STEP 0/1, jumps to saved step (including HVM_PENDING). STATE FILE WRITE/UPDATE hooks added at: end of STEP 1 (create), HVM trigger (update step=HVM_PENDING), STEP 3C listing rejection, STEP 3C candidate rejection, STEP 3C pass (→STEP_4). State directory: state\. (4) STEP 0C Product Exclusion Check documented in step table. (5) output structure updated: state\ directory added.*

*Created: 2026-05-27*  
*Updated: 2026-06-10 — MVP video generation upgrade. Added: Unique Asset Generation Agent, Silent Video Generator Agent, Quality & Learning Agent. Added new folders: assets\, videos\, qa\, scripts\. Review videos repurposed as research reference only — final footage now comes from AliExpress product images, page screenshots, and scroll captures. Agent outputs 4 silent MP4 files per run (1080×1920, H.264, text overlays baked in, no voiceover). Added pre-generation QA (4 checks) and post-generation QA with 3-retry logic and FAILED — REQUIRES HUMAN REVIEW escalation path. Updated daily routine: screen recording removed, user only generates affiliate link and uploads ready MP4s. Updated video_results.csv schema: added optional asset_source and best_segment columns. Replaced inline agent prompts with command file references.*  
*Updated: 2026-06-14 — Performance intelligence upgrade. Added 72-hour rule: only CONFIRMED variants (72h+ since upload) influence long-term learning (hook type, category, price range, confidence score). Added variant_status field (NEW/TESTING/CONFIRMED) and 4 new CSV columns (upload_date, upload_time, age_hours, variant_status). Added product status system (NEW/TESTING/WINNING/RETIRED PRODUCT). Added STEP 0B Winner Scaling Check to /tiktok. Added Weekly Audit Report to /tiktok analyze. CURRENT_PRODUCT_ID updated to 003.*
*Updated: 2026-06-14 — Auto product ID. CURRENT_PRODUCT_ID removed. PRODUCT ID now auto-assigned each run by scanning output/, data/, videos/ for the highest existing ID and adding 1 (zero-padded to 3 digits). Manual update reminders removed from both commands.*
*Updated: 2026-06-14 — Product validation upgrade. Added mandatory STEP 3B: 5-check product validation (page active, affiliate eligible, ships to Israel, purchasable now, no blocking warnings) before tracking IDs, assets, or video generation. Auto-rejects failed products and retries next candidate automatically.*
*Updated: 2026-06-14 — STEP 3B validation bug fix (round 1). Bug: STEP 3B passed a URL (item 1005009207029480) that returns "page not found" when opened manually. Root cause: validation relied on search evidence and redirect presence instead of live page content. Fix: STEP 3B now requires WebFetch on the exact product URL; product title and price must be present in the fetched content; immediate reject on any "page not found", "can not be found", "item is removed", or equivalent message; immediate reject if WebFetch returns only navigation/footer with no product content.*
*Updated: 2026-06-14 — STEP 3B fallback validation (round 2). Bug: WebFetch returns footer-only HTML for ALL AliExpress pages due to JS rendering — WebFetch cannot distinguish a live listing from a removed one. Fix: added two-path validation. Path A (WebFetch gets real content) unchanged from round 1. Path B (footer-only): fallback Google search on exact item ID/URL; item must appear as a Google-indexed product listing with a title in the snippet; reject if item appears only in wiki/article pages or returns no results; prefer items confirmed across multiple AliExpress regional domains; ships-to-Israel confirmed by redirect to he.aliexpress.com; affiliate eligibility flagged UNCONFIRMED when JS-rendered (defaults to eligible for generic categories).*
*Updated: 2026-06-14 — Tracking ID upgrade. Added per-variant tracking IDs (product[ID]_A/B/C/D). Upload package format updated: AFFILIATE LINK moved from global header into each variant block. STEP 4 in /tiktok now generates 4 tracking IDs and instructs user to create 4 affiliate links. Added 4 new CSV columns: tracking_id (always filled), affiliate_clicks, affiliate_sales, affiliate_commission (optional). Affiliate sales override engagement metrics when choosing the winner in /tiktok analyze.*  
*Updated: 2026-06-14 — Content rules + QA expansion + product completions. 7 new permanent rules added to tiktok.md: GENERAL AUDIENCE COPY RULE (gender-neutral Hebrew throughout), PRODUCT NUMBER CONSISTENCY RULE updated (variant-level CTAs: [PRODUCT_ID][VARIANT]), REPLY MANAGEMENT RULE (REPLY REFERENCE TABLE required in every upload package), CHECK 9 added (Thumbnail QA: hook readable in profile crop), CHECK 7 expanded (Hebrew text quality + gender-neutral audience), 9-item FINAL QA CHECKLIST, REPLY REFERENCE TABLE format standardised. Step 8 pre-gen QA updated: 9 checks total (was 8). Products 002 and 003 complete and READY TO UPLOAD.*
