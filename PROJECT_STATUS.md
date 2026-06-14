# TikTok Affiliate Agent — Project Status

**Last updated:** 2026-06-14  
**Owner:** Lilach  
**Working directory:** `C:\Automation\TikTok\`

---

## Current Status

**Phase:** ALL TASKS COMPLETE. Full /tiktok pipeline operational end-to-end.  
**Blocker:** None.

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
| `.claude/commands/tiktok.md` | ✅ Approved | Morning agent prompt. Steps 0–12. Includes pre-gen QA, asset gen, video gen, post-gen QA. |
| `.claude/commands/tiktok-analyze.md` | ✅ Approved | Evening analyzer. Includes full Quality & Learning Agent (4 areas, confidence score). |
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
| Evening agent prompt | `C:\Automation\TikTok\.claude\commands\tiktok-analyze.md` |
| Asset generation spec | `C:\Automation\TikTok\scripts\generate_assets_spec.md` |
| Video generation spec | `C:\Automation\TikTok\scripts\generate_videos_spec.md` |
| Learning database | `C:\Automation\TikTok\data\video_results.csv` |
| Video config (per run) | `C:\Automation\TikTok\data\[PRODUCT_ID]-video-config.json` |
| Generated videos | `C:\Automation\TikTok\videos\[YYYY-MM-DD]-product-[ID]-[A/B/C/D].mp4` |

---

## Resuming the Pipeline

The `/tiktok` pipeline is fully operational. To run the next product:

1. Open Claude Code in `C:\Automation\TikTok\`
2. Type `/tiktok`
3. The agent auto-assigns the next product ID, runs all Steps 0–13, and outputs 4 MP4 files ready to upload

Products completed to date: 001 (Astronaut Galaxy Projector), 002 (Plug Adapter ₪23), 003 (Mini Bag Sealer ₪8). Next run will auto-assign 004.

---

*This file was created at the end of the architecture session on 2026-06-10.*  
*Do not delete — it is the single source of truth for resuming this project.*
