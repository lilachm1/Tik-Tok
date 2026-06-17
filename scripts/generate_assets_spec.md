# Specification: generate_assets.py
# Unique Asset Generation Agent

**Status:** Specification — not yet implemented  
**Script:** `C:\Automation\TikTok\scripts\generate_assets.py`  
**Called by:** `/tiktok` command, Step 8  
**Purpose:** Collect all product visuals from a single AliExpress product page so the video generator has original footage. No third-party review footage. No paid tools.

---

## 1. Script Responsibilities

The script owns exactly one job per phase. Phases run in order. Each phase may retry independently.

| Phase | Responsibility |
|---|---|
| 0 — Setup | Parse CLI args. Validate inputs. Create output directories. |
| 1 — Browser | Launch Playwright headless Chromium. Navigate to URL. Dismiss popups. |
| 2 — Images | Extract full-size product image URLs from the gallery. Download min 5, max 12. |
| 3 — Screenshots | Screenshot four page sections: main image, price, rating/reviews, top reviews. |
| 4 — Scroll | Capture slow page scroll as video (preferred) or as sequential frames (fallback). |
| 5 — Manifest | Write `manifest.json` with metadata for every collected asset. |
| 6 — QA | Verify minimum requirements. Retry failed phases. Exit with appropriate code. |

**What the script does NOT do:**
- Download or touch any review videos (TikTok, YouTube, AliExpress video reviews)
- Use any paid API or tool
- Navigate to any URL other than the provided AliExpress product URL
- Generate, edit, or compose video — that belongs to `generate_videos.py`

---

## 2. CLI Arguments

```
python generate_assets.py --product-id <ID> --url "<URL>" [options]
```

### Required arguments

| Argument | Type | Description | Example |
|---|---|---|---|
| `--product-id` | string | Product ID used for output folder naming | `003` |
| `--url` | string | Full AliExpress product page URL (quoted) | `"https://www.aliexpress.com/item/1234567890.html"` |

### Optional arguments

| Argument | Type | Default | Description |
|---|---|---|---|
| `--output-dir` | path | `C:\Automation\TikTok\assets\` | Override base output directory |
| `--max-images` | int | `12` | Maximum product images to download |
| `--headless` | bool | `True` | Run browser headlessly |
| `--timeout` | int | `30` | Page load timeout in seconds |
| `--no-scroll-video` | flag | off | Skip video capture and go straight to scroll frames |

### Validation rules (Phase 0, before browser launches)
- `--product-id` must be a non-empty string matching `[0-9A-Za-z_-]+`
- `--url` must start with `https://www.aliexpress.com/item/` or `https://aliexpress.com/item/`
- If either fails: print error message and exit with code 2 immediately (no retry)

---

## 3. Exact Folder Structure

```
C:\Automation\TikTok\assets\[PRODUCT_ID]\
├── images\
│   ├── 001_main.jpg        ← first image from listing gallery
│   ├── 002_detail.jpg
│   ├── 003_detail.jpg
│   ├── ...
│   └── 012_last.jpg        ← maximum 12 images
├── screenshots\
│   ├── main.png            ← hero product image area (full viewport)
│   ├── price.png           ← price section clipped to element
│   ├── rating.png          ← star rating + review count section
│   ├── review1.png         ← first visible written review (optional)
│   └── review2.png         ← second visible written review (optional)
├── scroll\
│   ├── scroll.mp4          ← preferred: 3–4 sec scroll video at 4fps
│   │                          (only if ffmpeg is available)
│   ├── scroll_001.png      ← fallback: sequential frames if video fails
│   ├── scroll_002.png
│   └── ...                    (8–12 frames, one per scroll step)
└── manifest.json
```

### Naming rules
- Image files: zero-padded 3-digit index + underscore + descriptor. Descriptor = `main` for the first image, `detail` for all subsequent ones.
- Screenshot files: fixed names as shown above. Do not use dynamic names.
- Scroll files: `scroll.mp4` if video, or `scroll_NNN.png` (zero-padded) if frames.
- All filenames lowercase, no spaces.

### Directory creation
All four directories (`images\`, `screenshots\`, `scroll\`, and the product root) must be created by Phase 0 if they do not already exist. A second run on the same product ID overwrites existing files.

---

## 4. Manifest Schema

File: `C:\Automation\TikTok\assets\[PRODUCT_ID]\manifest.json`

```json
{
  "product_id": "003",
  "source_url": "https://www.aliexpress.com/item/1234567890.html",
  "collected_at": "2026-06-10T09:15:32",
  "summary": {
    "total_assets": 15,
    "image_count": 8,
    "screenshot_count": 5,
    "scroll_type": "video",
    "scroll_frame_count": 0,
    "qa_passed": true,
    "retry_count": 0
  },
  "assets": [
    {
      "file_path": "images/001_main.jpg",
      "asset_type": "product_image",
      "width": 800,
      "height": 800,
      "source_url": "https://ae01.alicdn.com/kf/abc123_800x800.jpg",
      "index": 1,
      "is_main": true,
      "file_size_kb": 85
    },
    {
      "file_path": "images/002_detail.jpg",
      "asset_type": "product_image",
      "width": 800,
      "height": 800,
      "source_url": "https://ae01.alicdn.com/kf/def456_800x800.jpg",
      "index": 2,
      "is_main": false,
      "file_size_kb": 72
    },
    {
      "file_path": "screenshots/main.png",
      "asset_type": "screenshot_main",
      "width": 1080,
      "height": 1080,
      "source_url": null,
      "index": null,
      "is_main": false,
      "file_size_kb": 210
    },
    {
      "file_path": "screenshots/price.png",
      "asset_type": "screenshot_price",
      "width": 1080,
      "height": 320,
      "source_url": null,
      "index": null,
      "is_main": false,
      "file_size_kb": 48
    },
    {
      "file_path": "screenshots/rating.png",
      "asset_type": "screenshot_rating",
      "width": 1080,
      "height": 200,
      "source_url": null,
      "index": null,
      "is_main": false,
      "file_size_kb": 35
    },
    {
      "file_path": "screenshots/review1.png",
      "asset_type": "screenshot_review",
      "width": 1080,
      "height": 400,
      "source_url": null,
      "index": 1,
      "is_main": false,
      "file_size_kb": 62
    },
    {
      "file_path": "scroll/scroll.mp4",
      "asset_type": "scroll_video",
      "width": 390,
      "height": 844,
      "source_url": null,
      "index": null,
      "is_main": false,
      "file_size_kb": 1240
    }
  ]
}
```

### Field definitions

| Field | Required | Type | Description |
|---|---|---|---|
| `product_id` | yes | string | Matches `--product-id` argument |
| `source_url` | yes | string | The AliExpress URL the script was given |
| `collected_at` | yes | string | ISO 8601 datetime when script ran |
| `summary.total_assets` | yes | int | Total entries in `assets` array |
| `summary.image_count` | yes | int | Count of `asset_type = "product_image"` |
| `summary.screenshot_count` | yes | int | Count of `asset_type = "screenshot_*"` |
| `summary.scroll_type` | yes | string | `"video"` or `"frames"` or `"none"` |
| `summary.scroll_frame_count` | yes | int | Count of scroll frame PNGs (0 if video) |
| `summary.qa_passed` | yes | bool | True only if QA Phase 6 passed all checks |
| `summary.retry_count` | yes | int | Total retries across all phases this run |
| `assets[].file_path` | yes | string | Relative path from product root folder |
| `assets[].asset_type` | yes | string | See asset type enum below |
| `assets[].width` | yes | int | Pixel width of the file |
| `assets[].height` | yes | int | Pixel height of the file |
| `assets[].source_url` | yes | string or null | Original URL if downloaded; null for screenshots |
| `assets[].index` | yes | int or null | Position in gallery sequence; null for screenshots |
| `assets[].is_main` | yes | bool | True only for `001_main.jpg` |
| `assets[].file_size_kb` | yes | int | File size rounded to nearest KB |

### Asset type enum (exact strings, lowercase)

| Value | Meaning |
|---|---|
| `product_image` | Full-size image downloaded from AliExpress listing gallery |
| `screenshot_main` | Full-viewport screenshot of the hero product image area |
| `screenshot_price` | Clipped screenshot of the price element |
| `screenshot_rating` | Clipped screenshot of the star rating + review count row |
| `screenshot_review` | Clipped screenshot of a single written review |
| `scroll_video` | Composed MP4 of the slow page scroll |
| `scroll_frame` | Single PNG frame captured during scroll (fallback) |

---

## 5. Phase-by-Phase Technical Behavior

### Phase 1 — Browser Setup

- Launch Playwright headless Chromium
- Viewport: **390×844** (iPhone 14 equivalent) — AliExpress mobile layout loads a simpler gallery that is easier to parse and more consistent
- User agent: a current real iOS Safari UA string (hardcoded in script, not randomized)
- Navigate to URL with configurable timeout (default 30s)
- Wait condition: `networkidle` — wait until no network requests for 500ms
- Popup dismissal sequence (attempt each in order, skip if not found):
  1. Cookie consent / GDPR banner — click accept button
  2. Country/language selector — click "Continue" or close
  3. App install prompt — click close
  4. Login prompt — click close or "Continue as guest"
- After popup dismissal: wait 1.5s for layout to stabilize before proceeding

### Phase 2 — Image Extraction

**Finding image URLs:**
- AliExpress gallery thumbnails are rendered in a horizontally scrollable strip
- Locate the gallery container (CSS selector approach, with fallback selectors)
- Extract all `src` or `data-src` attributes from `<img>` tags inside the gallery
- Full-size URL transformation: AliExpress thumbnails follow the pattern `_NNxNN.jpg` or `_NNxNN.webp` at the end of the filename. Replace that suffix with `_800x800.jpg` to get the full-size version.
- Filter out:
  - Duplicate URLs
  - Images smaller than 200px in either dimension (icons, badges)
  - URLs that do not contain `alicdn.com` (third-party injections)
- Limit to first 12 unique valid URLs

**Downloading images:**
- Use `requests` with a timeout of 15s per image
- Set a referrer header to `https://www.aliexpress.com/` on each request
- Save with zero-padded sequential filename: `001_main.jpg`, `002_detail.jpg`, etc.
- Read actual dimensions after save using `Pillow` (`Image.open`)
- If a download fails for a single image: skip it and continue (do not retry individual images)
- After all downloads: count successfully saved images
- If count < 5: trigger Phase 2 retry (up to 3 attempts total across all retries)

### Phase 3 — Screenshots

All screenshots use Playwright's `page.screenshot()` and element-level clipping where applicable. Viewport is kept at 390×844 throughout.

| Screenshot | Method | Clip strategy |
|---|---|---|
| `main.png` | Scroll page to top. Screenshot the hero image container element. | Element clip — capture only the product image container, not the full page |
| `price.png` | Locate the price element (typically shows ₪ or $ amount). Scroll into view. Screenshot the price row. | Element clip |
| `rating.png` | Locate the star rating row (contains star icons + review count number). Scroll into view. Screenshot. | Element clip |
| `review1.png` | Scroll to the reviews section. Find the first written review card. Screenshot it. | Element clip |
| `review2.png` | Screenshot the second written review card if visible. | Element clip |

**Screenshot failure handling:**
- If the target element is not found after 3 attempts: skip that screenshot, note it in the manifest as absent (do not add an entry for it — absence is detectable by checking the manifest)
- `review1.png` and `review2.png` are fully optional — their absence does not affect QA
- `main.png`, `price.png`, and `rating.png` are expected — log a warning if missing but do not fail the run

### Phase 4 — Scroll Capture

**Preferred path — scroll video:**
1. Reset scroll to top of page
2. Use Playwright `page.evaluate()` to scroll the page incrementally in a loop (scroll 200px every 250ms for approximately 3–4 seconds total)
3. Capture 12–15 screenshots during the scroll at even intervals using Playwright's screenshot API
4. Save frames temporarily to `scroll/` as `frame_001.png` through `frame_015.png`
5. Run ffmpeg to compose frames into `scroll.mp4`:
   - Input: `scroll/frame_%03d.png`
   - Frame rate: 4fps
   - Output: `scroll/scroll.mp4`
   - Codec: H.264, preset fast, crf 28
6. Delete the temporary frame files after successful ffmpeg composition
7. Record `scroll_type: "video"` in manifest

**Fallback path — scroll frames (if ffmpeg not available or video composition fails):**
1. Same incremental scroll sequence as above
2. Keep the PNG frames — rename from `frame_NNN.png` to `scroll_NNN.png`
3. Do not attempt video composition
4. Record `scroll_type: "frames"` and `scroll_frame_count: N` in manifest

**If scroll capture fails entirely** (Playwright error, page crash, etc.):
- Record `scroll_type: "none"` in manifest
- Log a warning but do not fail the run — scroll capture is informational for the video generator

### Phase 5 — Manifest

1. Build the full manifest dict as defined in Section 4
2. For each file in `images/`, `screenshots/`, `scroll/`: read actual dimensions and file size
3. Set `collected_at` to current local datetime in ISO 8601 format
4. Set `summary.qa_passed` to `false` initially — Phase 6 will set it to `true` if checks pass
5. Write to `assets/[PRODUCT_ID]/manifest.json` with `json.dumps(indent=2, ensure_ascii=False)`
6. Validate round-trip: read the file back with `json.loads` to confirm it is valid JSON
7. If write or round-trip fails: retry up to 3 times, then exit code 2

### Phase 6 — QA

Run checks in this order. On any check failure: retry the responsible phase (not the entire script) up to 3 times.

| Check | Pass condition | On failure |
|---|---|---|
| QA-1: Manifest exists | `manifest.json` exists and is valid JSON | Retry Phase 5 |
| QA-2: Minimum images | `summary.image_count >= 5` | Retry Phase 2 |
| QA-3: Images readable | Each `product_image` entry opens without error via Pillow | Re-download specific failing images (up to 3 attempts) |
| QA-4: Dimensions populated | Every manifest entry has `width > 0` and `height > 0` | Re-read dimensions and rewrite manifest |
| QA-5: Required fields | Every entry has `file_path`, `asset_type`, `width`, `height` | Rewrite manifest |
| QA-6: At least 1 screenshot | At least 1 entry with `asset_type = "screenshot_*"` | Retry Phase 3 |

After all checks pass: set `summary.qa_passed = true` and rewrite manifest.

If any check still fails after 3 retries: output `FAILED — REQUIRES HUMAN REVIEW` with the specific failing check name, then exit code 2.

---

## 6. Failure and Retry Behavior

### Retry matrix

| Phase | Retryable? | Max retries | What triggers retry | What "FAILED" means |
|---|---|---|---|---|
| 0 — Setup | No | — | — | Exit immediately, no retry |
| 1 — Browser | Yes | 3 | Navigation timeout or crash | Can't load page |
| 2 — Images | Yes | 3 | Fewer than 5 valid images collected | Not enough product images found |
| 3 — Screenshots | Per screenshot | 3 each | Element not found / screenshot error | Screenshot skipped (not fatal unless all 3 expected fail) |
| 4 — Scroll | Yes (fallback first) | 1 video → frames | ffmpeg fails | Falls back to frames; only FAILED if frames also fail |
| 5 — Manifest | Yes | 3 | Write error / invalid JSON | Can't write manifest |
| 6 — QA | Per check | 3 | Specific check fails | FAILED — REQUIRES HUMAN REVIEW |

### Exit codes

| Code | Meaning | When |
|---|---|---|
| 0 | Full success | QA passed, manifest written, 5+ images, all expected screenshots |
| 1 | Partial success | Images and manifest OK, some optional screenshots missing (review1/review2, scroll) |
| 2 | FAILED | Fewer than 5 images after 3 retries, or manifest unwritable, or QA blocking check failed after 3 retries |

### stdout output (consumed by the /tiktok agent)

On every phase start:
```
[generate_assets] Phase 2 — Image extraction starting...
```

On retry:
```
[generate_assets] Phase 2 retry 1/3 — only 3 images collected, retrying...
```

On phase success:
```
[generate_assets] Phase 2 — 8 images collected.
```

On partial success (exit 1):
```
✅ Assets collected — 8 images, 3 screenshots saved to assets/003/
⚠️  Optional assets missing: review2.png, scroll video (frames captured instead)
```

On full success (exit 0):
```
✅ Assets collected — 8 images, 5 screenshots, scroll video saved to assets/003/
```

On failure (exit 2):
```
❌ FAILED — REQUIRES HUMAN REVIEW
Reason: QA-2 failed after 3 retries — only 3 product images found on this listing.
Suggestion: Find an alternative listing with 5+ product images and rerun.
```

---

## 7. Test Plan

Tests are manual for the MVP. Run them in order before declaring the script production-ready.

### Group A — Happy Path

| Test | Input | Expected result |
|---|---|---|
| A1 | Valid AliExpress URL for a product with 8+ images | Exit 0. `images/` contains 8 files. `manifest.json` has `image_count: 8`, `qa_passed: true`. |
| A2 | Same URL run twice | Second run overwrites first. No duplicate files. Manifest reflects second run timestamp. |
| A3 | URL for product with exactly 5 images | Exit 0. QA-2 passes with count = 5. |

### Group B — Edge Cases

| Test | Input | Expected result |
|---|---|---|
| B1 | URL for product with 4 images | Phase 2 retries 3 times. Exit 2 with QA-2 failure message. |
| B2 | Valid URL but page shows cookie consent popup | Popup dismissed. Remaining phases continue normally. |
| B3 | Valid URL but login prompt appears | Login prompt closed. Remaining phases continue normally. |
| B4 | Valid URL but reviews section not present | `review1.png` and `review2.png` absent from manifest. Exit 1 (not exit 2). |
| B5 | Valid URL but price element not found | `price.png` absent. Warning logged. Exit 1. |

### Group C — Input Validation

| Test | Input | Expected result |
|---|---|---|
| C1 | `--product-id ""` (empty) | Exit 2 immediately. Error: "product-id cannot be empty" |
| C2 | `--url "https://amazon.com/..."` | Exit 2 immediately. Error: "URL must be an AliExpress product URL" |
| C3 | Missing `--product-id` | Exit 2 immediately. Argparse error. |
| C4 | Missing `--url` | Exit 2 immediately. Argparse error. |

### Group D — Manifest Integrity

| Test | Action | Expected result |
|---|---|---|
| D1 | Run A1, then parse manifest.json | Valid JSON. Every entry has file_path, asset_type, width > 0, height > 0. |
| D2 | Run A1, then open each image listed in manifest | All files open without error. |
| D3 | Run A1, then check `summary.image_count` | Matches actual count of files in `images/` directory. |

### Group E — Scroll Capture

| Test | Setup | Expected result |
|---|---|---|
| E1 | ffmpeg available on PATH | `scroll.mp4` exists. Manifest has `scroll_type: "video"`. Temporary frame PNGs deleted. |
| E2 | ffmpeg NOT on PATH (or `--no-scroll-video` flag) | `scroll_001.png` through `scroll_NNN.png` exist. Manifest has `scroll_type: "frames"`. No `.mp4` created. |

### Group F — Network / Timeout

| Test | Simulation | Expected result |
|---|---|---|
| F1 | Set `--timeout 1` (too short) | Phase 1 retries 3 times. Exits 2 with timeout failure message. |
| F2 | Valid URL, one image URL returns 404 | That image skipped. Remaining images downloaded. Count still meets minimum if 5+ remain. |

---

## 8. Implementation Checklist

Use this checklist when building the script. Check off each item as implemented and verified.

### Phase 0 — Setup
- [ ] `argparse` for `--product-id`, `--url`, `--output-dir`, `--max-images`, `--headless`, `--timeout`, `--no-scroll-video`
- [ ] Validate `--product-id` matches `[0-9A-Za-z_-]+`
- [ ] Validate `--url` starts with `https://www.aliexpress.com/item/` or `https://aliexpress.com/item/`
- [ ] Exit code 2 immediately on validation failure
- [ ] Create `assets/[PRODUCT_ID]/images/`, `screenshots/`, `scroll/` (using `pathlib.Path.mkdir(parents=True, exist_ok=True)`)
- [ ] Initialize a retry counter (shared across all phases for the summary)

### Phase 1 — Browser
- [ ] `playwright.sync_api.sync_playwright()` context manager
- [ ] Launch `chromium.launch(headless=True)` (or `False` if `--headless False`)
- [ ] `browser.new_context(viewport={"width": 390, "height": 844}, user_agent="...")`
- [ ] Hardcode a real current iOS Safari user agent string
- [ ] `page.goto(url, timeout=timeout*1000, wait_until="networkidle")`
- [ ] Wrap in retry loop (3 attempts)
- [ ] After navigation: attempt to dismiss each popup type in sequence using `page.query_selector()` + `.click()`
- [ ] Wait 1.5s after popup handling: `page.wait_for_timeout(1500)`

### Phase 2 — Image Extraction
- [ ] Select gallery image elements using CSS selectors with at least 2 fallback selectors
- [ ] Extract `src` and `data-src` attributes
- [ ] Apply full-size URL transformation (replace `_NNxNN.jpg` suffix with `_800x800.jpg`)
- [ ] Filter: dedup, require `alicdn.com` in URL, require image dimensions > 200×200
- [ ] Limit to `max_images` (default 12)
- [ ] Download each with `requests.get(url, headers={"Referer": "https://www.aliexpress.com/"}, timeout=15)`
- [ ] Save to `images/NNN_descriptor.jpg`
- [ ] Read dimensions with `PIL.Image.open(filepath).size`
- [ ] Skip failed individual downloads (log warning, continue)
- [ ] After all downloads: count files in `images/`. If < 5 → trigger retry (up to 3 total)
- [ ] On retry: clear `images/` folder before retrying

### Phase 3 — Screenshots
- [ ] `page.evaluate("window.scrollTo(0, 0)")` before first screenshot
- [ ] `main.png`: find hero image container, `element.screenshot(path="screenshots/main.png")`
- [ ] `price.png`: `page.query_selector("[class*='price']")` (use multiple fallback selectors), scroll into view, element screenshot
- [ ] `rating.png`: find rating row, scroll into view, element screenshot
- [ ] `review1.png`: scroll to reviews section, find first review card, element screenshot
- [ ] `review2.png`: find second review card if present, element screenshot
- [ ] Wrap each screenshot in try/except — log warning and continue if element not found
- [ ] Each element screenshot at existing 390px viewport (no viewport change needed)

### Phase 4 — Scroll Capture
- [ ] Check if ffmpeg is on PATH: `shutil.which("ffmpeg")`
- [ ] If ffmpeg available and `--no-scroll-video` not set:
  - [ ] `page.evaluate("window.scrollTo(0, 0)")`
  - [ ] Loop: scroll 200px every 250ms using `page.evaluate("window.scrollBy(0, 200)")` + `page.wait_for_timeout(250)`
  - [ ] During loop: screenshot every 2nd iteration → save as `scroll/frame_NNN.png` (12–15 frames)
  - [ ] Run ffmpeg: `ffmpeg -r 4 -i scroll/frame_%03d.png -c:v libx264 -preset fast -crf 28 scroll/scroll.mp4`
  - [ ] Verify `scroll.mp4` exists and size > 0
  - [ ] Delete `frame_NNN.png` files
  - [ ] Set `scroll_type = "video"`
- [ ] If ffmpeg not available OR video composition fails:
  - [ ] Keep frame PNGs, rename to `scroll_NNN.png`
  - [ ] Set `scroll_type = "frames"`, `scroll_frame_count = N`
- [ ] If scroll page interaction fails entirely: set `scroll_type = "none"`, log warning, continue

### Phase 5 — Manifest
- [ ] Build manifest dict
- [ ] For each file in `images/`, `screenshots/`, `scroll/`: read size with `os.path.getsize()` and dimensions with PIL or ffprobe for .mp4
- [ ] For .mp4 dimensions: use `subprocess` to run `ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of json` — parse result
- [ ] `json.dumps(manifest, indent=2, ensure_ascii=False)` → write to `manifest.json`
- [ ] Round-trip validate: `json.loads(open("manifest.json").read())`
- [ ] Retry up to 3 times on write error
- [ ] Exit code 2 if still failing

### Phase 6 — QA
- [ ] QA-1: `manifest.json` exists + valid JSON
- [ ] QA-2: `summary.image_count >= 5`
- [ ] QA-3: Each `product_image` file opens with `PIL.Image.open()` without exception
- [ ] QA-4: Every entry has `width > 0` and `height > 0`
- [ ] QA-5: Every entry has all required fields (`file_path`, `asset_type`, `width`, `height`)
- [ ] QA-6: At least 1 entry with `asset_type` starting with `"screenshot_"`
- [ ] Each check wrapped in retry logic targeting the responsible phase
- [ ] On all checks pass: set `summary.qa_passed = true`, rewrite manifest
- [ ] On any check fails after 3 retries: print `FAILED — REQUIRES HUMAN REVIEW\nReason: [check name] — [detail]`, exit code 2

### Output / Logging
- [ ] Print `[generate_assets] Phase N — ...` at each phase start
- [ ] Print retry notices: `[generate_assets] Phase N retry X/3 — reason`
- [ ] Print final success or failure line (consumed by /tiktok agent)
- [ ] Exit with correct code: `sys.exit(0)`, `sys.exit(1)`, or `sys.exit(2)`

---

## 9. Dependencies

| Package | Version constraint | Purpose |
|---|---|---|
| `playwright` | >= 1.40 | Browser automation |
| `requests` | >= 2.28 | Image downloads |
| `Pillow` | >= 10.0 | Image dimension reading + readability check |
| `ffmpeg` | Any, on PATH | Scroll video composition (optional — fallback exists) |
| Standard library | — | `argparse`, `json`, `pathlib`, `shutil`, `subprocess`, `sys`, `os` |

Install:
```
pip install playwright requests Pillow
playwright install chromium
```

---

*Specification version: 1.0*  
*Created: 2026-06-10*  
*Status: Ready for implementation*  
*Next step: Implement generate_assets.py from this spec, then write generate_videos_spec.md*
