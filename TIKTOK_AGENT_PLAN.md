# TikTok Affiliate Agent — Full Plan

**Owner:** Lilach  
**Market:** Israel (for now)  
**Video content language:** Hebrew  
**Daily time budget:** 2 hours  
**Products per day:** 1 (agent picks automatically)  
**Commands:** `/tiktok` (morning) and `/tiktok analyze` (evening)

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

| Price | Score | Bonus | Total |
|-------|-------|-------|-------|
| Under 30₪ | 10 | +3 | 13 |
| 30–50₪ | 9 | +2 | 11 |
| 50–75₪ | 7 | — | 7 |
| 75–100₪ | 5 | — | 5 |
| Over 100₪ | 2 | — | 2 |

### Price Rules
- **Preferred range:** 20₪–50₪
- **Acceptable range:** 50₪–79₪
- **Avoid:** Products over 80₪ unless there is exceptional trend evidence AND a very strong problem/solution angle
- When comparing two similar products with similar total scores, always choose the cheaper one
- Goal: maximum conversions and impulse purchases — not maximum commission per sale

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
| 0 | Reads `video_results.csv` — calculates best hook type, category, price range from CONFIRMED rows only (72h+ rule) | Nothing |
| 0B | **Winner Scaling Check** — if a WINNING PRODUCT exists (2+ CONFIRMED variants, 20%+ above account average), shows 3–5 scaling variant ideas before proceeding to new product search | Nothing |
| 1 | Finds 5 trending products (must have 2+ trend sources each), scores using price model + history bonuses | Nothing |
| 2 | Picks highest-scoring product automatically (tie = cheaper wins) | Nothing |
| 3 | Finds best AliExpress listing (1,000+ sales, 4.5★+, 5+ images, ships to Israel) | Nothing |
| 4 | Safety check — no fake brands, no copyright risk | Nothing |
| 3B | **Product Validation Check (mandatory)** — uses WebFetch on the exact product URL: verifies page loads with product title and price present in fetched content, no "page not found" or removal message, affiliate eligible, ships to Israel, purchasable now. Search evidence alone is not sufficient. Auto-rejects and retries next candidate if any check fails. | Nothing |
| 5 | Prepares AliExpress product URL + category + commission rate for manual link generation | Nothing |
| 6 | Finds review videos for **research reference only** — not used as footage | Nothing |
| 7 | Generates 4 video variants — winning hook assigned to Variant A | Nothing |
| 7b | Writes storyboard + caption + hashtags for each of the 4 variants (Hebrew) | Nothing |
| 7c | Writes `data/[PRODUCT_ID]-video-config.json` (text overlay interface for scripts) | Nothing |
| 8 | **Pre-generation QA** — 4 checks (image count, storyboard completeness, hook distinctiveness, config integrity), up to 3 retries each | Nothing |
| 9 | **Unique asset generation** — runs `generate_assets.py`: downloads AliExpress product images, price/rating screenshots, slow scroll capture → `assets/[PRODUCT_ID]/` | Nothing |
| 10 | **Silent video generation** — runs `generate_videos.py`: composes 4 MP4s from assets + text overlays via MoviePy/FFmpeg | Nothing |
| 11 | **Post-generation QA** — verifies all 4 MP4s (existence, duration 13–17s, file size, resolution), up to 3 retries per variant | Nothing |
| 12 | Saves full package to `output/YYYY-MM-DD-product-XXX.md` | Nothing |
| 13 | Shows complete ready-to-use package in chat with MP4 file paths and QA status | Nothing |
| — | Paste AliExpress product URL into AliExpress Link Generator → copy affiliate link | **You (1 min)** |
| — | Open `C:\Automation\TikTok\videos\` — 4 MP4 files ready | **You (30 sec)** |
| — | Upload each MP4 to TikTok, add trending sound, paste caption + hashtags | **You (5–10 min)** |

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

---

## Command Reference

The full agent prompts live in the slash command files. Do not maintain a second copy here.

| Command | File | Steps |
|---------|------|-------|
| `/tiktok` | `.claude/commands/tiktok.md` | Steps 0–12 (research → QA → asset gen → video gen → output) |
| `/tiktok analyze` | `.claude/commands/tiktok-analyze.md` | Steps 1–5 + A–C (analysis → CSV → learning) |

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

*Created: 2026-05-27*  
*Updated: 2026-06-10 — MVP video generation upgrade. Added: Unique Asset Generation Agent, Silent Video Generator Agent, Quality & Learning Agent. Added new folders: assets\, videos\, qa\, scripts\. Review videos repurposed as research reference only — final footage now comes from AliExpress product images, page screenshots, and scroll captures. Agent outputs 4 silent MP4 files per run (1080×1920, H.264, text overlays baked in, no voiceover). Added pre-generation QA (4 checks) and post-generation QA with 3-retry logic and FAILED — REQUIRES HUMAN REVIEW escalation path. Updated daily routine: screen recording removed, user only generates affiliate link and uploads ready MP4s. Updated video_results.csv schema: added optional asset_source and best_segment columns. Replaced inline agent prompts with command file references.*  
*Updated: 2026-06-14 — Performance intelligence upgrade. Added 72-hour rule: only CONFIRMED variants (72h+ since upload) influence long-term learning (hook type, category, price range, confidence score). Added variant_status field (NEW/TESTING/CONFIRMED) and 4 new CSV columns (upload_date, upload_time, age_hours, variant_status). Added product status system (NEW/TESTING/WINNING/RETIRED PRODUCT). Added STEP 0B Winner Scaling Check to /tiktok. Added Weekly Audit Report to /tiktok analyze. CURRENT_PRODUCT_ID updated to 003.*
*Updated: 2026-06-14 — Auto product ID. CURRENT_PRODUCT_ID removed. PRODUCT ID now auto-assigned each run by scanning output/, data/, videos/ for the highest existing ID and adding 1 (zero-padded to 3 digits). Manual update reminders removed from both commands.*
*Updated: 2026-06-14 — Product validation upgrade. Added mandatory STEP 3B: 5-check product validation (page active, affiliate eligible, ships to Israel, purchasable now, no blocking warnings) before tracking IDs, assets, or video generation. Auto-rejects failed products and retries next candidate automatically.*
*Updated: 2026-06-14 — STEP 3B validation bug fix. Bug: STEP 3B passed a URL (item 1005009207029480) that returns "page not found" when opened manually. Root cause: validation relied on search evidence and redirect presence instead of live page content. Fix: STEP 3B now requires WebFetch on the exact product URL; product title and price must be present in the fetched content; immediate reject on any "page not found", "can not be found", "item is removed", or equivalent message; immediate reject if WebFetch returns only navigation/footer with no product content.*
*Updated: 2026-06-14 — Tracking ID upgrade. Added per-variant tracking IDs (product[ID]_A/B/C/D). Upload package format updated: AFFILIATE LINK moved from global header into each variant block. STEP 4 in /tiktok now generates 4 tracking IDs and instructs user to create 4 affiliate links. Added 4 new CSV columns: tracking_id (always filled), affiliate_clicks, affiliate_sales, affiliate_commission (optional). Affiliate sales override engagement metrics when choosing the winner in /tiktok analyze.*
