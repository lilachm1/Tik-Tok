# Specification: generate_videos.py
# Silent Video Generator Agent

**Status:** Specification — not yet implemented  
**Script:** `C:\Automation\TikTok\scripts\generate_videos.py`  
**Called by:** `/tiktok` command, Step 9  
**Purpose:** Compose 4 silent TikTok-ready MP4 files from collected AliExpress product assets and Hebrew text overlay specs. No third-party footage. No AI video. No CapCut. No voiceover.

---

## 1. Script Responsibilities

Seven phases, each owning one job. Phases 0–3 are setup and validation. Phase 4 runs once per variant (4×). Phases 5–6 are QA and reporting.

| Phase | Responsibility |
|---|---|
| 0 — Setup | Parse CLI args. Validate inputs. Create `videos/` directory. |
| 1 — Font | Locate a Hebrew-compatible TTF font. Verify it renders Hebrew glyphs. |
| 2 — Load config | Read and validate `data/[PRODUCT_ID]-video-config.json`. |
| 3 — Load manifest | Read `assets/[PRODUCT_ID]/manifest.json`. Build typed asset index. |
| 4 — Generate variants | For each of A/B/C/D: select assets, compose 5 segments, apply text overlays, encode MP4. |
| 5 — QA | Verify each MP4 meets all output requirements. Retry failed variants up to 3×. |
| 6 — Report | Print final success/partial/failed status with file paths and QA results. |

**What the script does NOT do:**
- Download assets (that is `generate_assets.py`)
- Use any review video footage as input
- Add audio, voiceover, or music tracks
- Upload to TikTok or any external service
- Use AI video generation tools

---

## 2. CLI Arguments

```
python generate_videos.py --product-id <ID> --date <YYYY-MM-DD> [options]
```

### Required arguments

| Argument | Type | Description | Example |
|---|---|---|---|
| `--product-id` | string | Product ID used to locate input files and name output files | `003` |
| `--date` | string | Date in YYYY-MM-DD format used in output filenames | `2026-06-10` |

### Optional arguments

| Argument | Type | Default | Description |
|---|---|---|---|
| `--output-dir` | path | `C:\Automation\TikTok\videos\` | Override output directory |
| `--assets-dir` | path | `C:\Automation\TikTok\assets\` | Override assets base directory |
| `--data-dir` | path | `C:\Automation\TikTok\data\` | Override data directory for config JSON |
| `--font-path` | path | auto-detect | Override Hebrew font TTF path |
| `--font-size` | int | `72` | Base font size in pixels |
| `--variant` | string | all | Generate only a specific variant: `A`, `B`, `C`, or `D` |

### Validation rules (Phase 0, before any file is read)
- `--product-id` must match `[0-9A-Za-z_-]+`
- `--date` must match `^\d{4}-\d{2}-\d{2}$`
- If either fails: print error and exit code 2 immediately, no retry
- `data/[PRODUCT_ID]-video-config.json` must exist — exit code 2 if missing
- `assets/[PRODUCT_ID]/manifest.json` must exist — exit code 2 if missing

---

## 3. Input Contracts

### 3.1 video-config.json

Expected path: `C:\Automation\TikTok\data\[PRODUCT_ID]-video-config.json`  
Written by: `/tiktok` agent, Step 6

The script validates these fields at Phase 2. Any missing or malformed field → exit code 2 with a specific error message (no retry — config errors require agent re-run).

**Required top-level fields:**

| Field | Type | Validation |
|---|---|---|
| `product_id` | string | Must match `--product-id` argument |
| `date` | string | Must be a valid date string |
| `price_ils` | number | Must be > 0 |
| `sales_count` | string | Non-empty string |
| `cta_id` | string | Non-empty string |
| `aliexpress_url` | string | Non-empty string |
| `variants` | array | Must contain exactly 4 objects with ids "A", "B", "C", "D" |

**Required per variant:**

| Field | Type | Validation |
|---|---|---|
| `id` | string | One of "A", "B", "C", "D" |
| `hook_type` | string | One of the 4 defined hook types |
| `segments` | array | Exactly 5 objects |

**Required per segment:**

| Field | Type | Validation |
|---|---|---|
| `start` | number | >= 0, < `end` |
| `end` | number | <= 17 |
| `text` | string | Non-empty Hebrew string |
| `color` | string | One of: `"white"`, `"yellow"`, `"red"` |
| `position` | string | One of: `"top-center"`, `"center"`, `"bottom"` |

**Validation: segment 0 must have `start == 0`** (hook must be first)  
**Validation: segment 4 must contain `cta_id` in its text** (CTA must reference product ID)  
**Validation: total duration = segment[4].end must be between 13 and 17** (inclusive)

### 3.2 manifest.json

Expected path: `C:\Automation\TikTok\assets\[PRODUCT_ID]\manifest.json`  
Written by: `generate_assets.py`

The script reads this at Phase 3 and builds a typed asset index (see Section 5 — Asset Selection Logic).

**Minimum requirements for this script to proceed:**
- `summary.qa_passed` must be `true`
- `summary.image_count` must be >= 5
- At least 1 entry with `asset_type == "screenshot_main"` OR at least 5 `product_image` entries

If manifest requirements not met: exit code 2 with message "Asset manifest does not meet minimum requirements. Re-run generate_assets.py first."

---

## 4. Output Contracts

### 4.1 Output file paths

```
C:\Automation\TikTok\videos\[YYYY-MM-DD]-product-[PRODUCT_ID]-A.mp4
C:\Automation\TikTok\videos\[YYYY-MM-DD]-product-[PRODUCT_ID]-B.mp4
C:\Automation\TikTok\videos\[YYYY-MM-DD]-product-[PRODUCT_ID]-C.mp4
C:\Automation\TikTok\videos\[YYYY-MM-DD]-product-[PRODUCT_ID]-D.mp4
```

Example:
```
C:\Automation\TikTok\videos\2026-06-10-product-003-A.mp4
```

### 4.2 Output file specification

| Property | Value |
|---|---|
| Container | MP4 |
| Video codec | H.264 (libx264) |
| Color space | yuv420p — required for TikTok compatibility |
| Resolution | 1080×1920 (9:16 vertical) |
| Frame rate | 30fps |
| CRF | 23 |
| Preset | `slow` (better compression, acceptable render time) |
| Audio | None — no audio track |
| Duration | 13–17 seconds |
| File size | 500 KB – 50 MB |

A second run with the same product ID and date overwrites existing output files without error.

---

## 5. Asset Selection Logic

### 5.1 Build the asset index (Phase 3)

After loading the manifest, categorize every entry into these named buckets:

| Bucket name | Source: asset_type values | Description |
|---|---|---|
| `main_image` | `product_image` where `is_main == true` | First gallery image |
| `product_images` | All `product_image` entries, sorted by `index` | Full gallery |
| `detail_images` | `product_image` where `is_main == false` | All non-main gallery images |
| `screenshot_main` | `screenshot_main` | Hero image area screenshot |
| `screenshot_price` | `screenshot_price` | Price section screenshot |
| `screenshot_rating` | `screenshot_rating` | Star rating + review count screenshot |
| `screenshot_reviews` | `screenshot_review` (index 1 and 2) | Written review screenshots |
| `scroll_asset` | `scroll_video` or `scroll_frame` entries | Scroll capture (reserved for future use) |

### 5.2 Segment-to-asset mapping

Each variant uses the same segment structure but may use different assets to visually differentiate variants. Assets are selected from the index buckets using the priority order below.

**Segment 0 — Hook (0–2s):**  
Use the primary product image for maximum product visibility in the first frame.

| Priority | Asset | Condition |
|---|---|---|
| 1 | `main_image` | Always available if manifest QA passed |
| 2 | `product_images[0]` | Fallback if `is_main` not set |

**Segment 1 — Price (2–5s):**  
Price screenshot is preferred because it shows the real AliExpress price visually.

| Priority | Asset | Condition |
|---|---|---|
| 1 | `screenshot_price` | If present in manifest |
| 2 | `product_images[1]` | Second gallery image |
| 3 | `product_images[0]` | Last resort |

**Segment 2 — Benefit (5–9s):**  
A detail image different from the main image shows the product's value.

| Priority | Asset | Condition |
|---|---|---|
| 1 | `detail_images[variant_offset]` | Variant A uses index 0, B uses 1, C uses 2, D uses 3. Wraps if list is shorter. |
| 2 | `product_images[2]` | Third gallery image |
| 3 | `product_images[1]` | Second gallery image |

The `variant_offset` ensures that Variant A, B, C, D each start with a different detail image, producing visual differentiation even when text differs only by hook.

**Segment 3 — Social proof (9–13s):**  
Rating/review screenshot reinforces credibility with real numbers.

| Priority | Asset | Condition |
|---|---|---|
| 1 | `screenshot_rating` | If present |
| 2 | `screenshot_reviews[0]` | First written review screenshot |
| 3 | `product_images[3]` | Fourth gallery image |
| 4 | `product_images[-1]` | Last gallery image |

**Segment 4 — CTA (13–15s):**  
Return to the main product image — clean close and visual bookend.

| Priority | Asset | Condition |
|---|---|---|
| 1 | `main_image` | Same as segment 0 — deliberate repetition |
| 2 | `product_images[0]` | Fallback |

### 5.3 Variant differentiation rule

Before generating: verify that not all 4 variants will use identical image sequences. If all 4 would use the same 5 images in the same order (e.g., only 1 product image exists in manifest), log a warning: "⚠️  Limited assets — variants will share images. Visual differentiation relies on hook text only." Then proceed. This is not a failure condition for MVP.

---

## 6. Hebrew / RTL Text Rendering Plan

Hebrew text has two requirements that standard rendering ignores: right-to-left character order (RTL) and correct Unicode bidirectional rendering when Hebrew and numbers/symbols are mixed.

### 6.1 Required libraries

| Library | Purpose |
|---|---|
| `Pillow` | Draw text onto RGBA image frames |
| `python-bidi` | Convert Hebrew logical order to visual display order for RTL rendering |

`arabic-reshaper` is NOT required — reshaping is needed only for Arabic script, not Hebrew.

Install:
```
pip install python-bidi Pillow
```

### 6.2 Hebrew text rendering pipeline (per text segment)

For every segment that has a text overlay, the script follows this exact pipeline:

**Step 1 — BiDi reordering**
```
from bidi.algorithm import get_display
visual_text = get_display(logical_text)
```
This converts the logical (storage) order of Hebrew characters to the correct visual (display) order that Pillow will render left-to-right. Without this step, Hebrew text appears reversed.

**Step 2 — Word wrapping**
Measure the visual width of the full text using `font.getbbox(visual_text)`. If width exceeds the safe text width (see Section 7.3), split the text at word boundaries and wrap to multiple lines. Each wrapped line must individually pass through the BiDi pipeline.

**Step 3 — Create text layer**
Create a 1080×1920 RGBA image with full transparency (alpha = 0). This is the text overlay layer.

**Step 4 — Draw outline (for readability)**
For every text character position, draw the text 8 times in the outline color at ±3px offsets: (x-3,y), (x+3,y), (x,y-3), (x,y+3), (x-3,y-3), (x+3,y-3), (x-3,y+3), (x+3,y+3). Outline color: black for white/yellow text, white for red text.

**Step 5 — Draw main text**
Draw the BiDi-reordered text in the specified color at the computed position. For multi-line text, draw each line separately with standard line spacing (font_size × 1.2).

**Step 6 — Composite onto frame**
The text layer (RGBA) is composited over the video frame using alpha compositing. In MoviePy this is done via `CompositeVideoClip`.

### 6.3 Font selection (Phase 1)

The script checks for a usable Hebrew font in this priority order:

| Priority | Path | Notes |
|---|---|---|
| 1 | `--font-path` CLI argument | User override — highest priority |
| 2 | `C:\Windows\Fonts\ArialUni.ttf` | Arial Unicode MS — best Hebrew coverage, requires Office |
| 3 | `C:\Windows\Fonts\tahoma.ttf` | Tahoma — has Hebrew, ships with Windows |
| 4 | `C:\Windows\Fonts\arial.ttf` | Arial — has Hebrew on most Windows installs |
| 5 | `C:\Windows\Fonts\David.ttf` | Hebrew-specific Windows font |
| 6 | First `.ttf` found in `C:\Windows\Fonts\` matching `*Noto*Hebrew*.ttf` | Downloaded Noto Sans Hebrew |

**Font verification test:** attempt to render the Hebrew character `ש` (shin) with the candidate font using Pillow. If the result is a replacement character (tofu box) or the render raises an exception, skip to the next priority. If no font passes: exit code 2 with message: "No Hebrew-compatible font found. Install Noto Sans Hebrew or set --font-path."

---

## 7. Visual Layout Rules

### 7.1 Canvas and frame spec

| Property | Value |
|---|---|
| Output canvas | 1080×1920 px |
| Background | Black (`#000000`) — used for padding only, should not be visible after image fill |
| Frame rate | 30fps |
| All measurements | In pixels at 1080×1920 |

### 7.2 Image scaling — aspect ratio handling

Product images from AliExpress are typically square (800×800 or 1:1). Screenshots are 390px wide. Neither matches 9:16. Use the **scale-to-fill with blur background** approach:

**Foreground layer:**
- Scale the image to fit within 1080px width OR 1920px height (whichever is smaller after scaling), preserving aspect ratio
- Center the scaled image on the 1080×1920 canvas

**Background layer:**
- Scale the same image to 1920px height (or until it fills the canvas in both dimensions), preserving aspect ratio
- Center-crop to 1080×1920
- Apply a heavy Gaussian blur (radius 30–40px) using Pillow's `ImageFilter.GaussianBlur`
- Reduce opacity to 70% (darken for text readability): multiply all RGB values by 0.7

**Composite:**
- Draw background layer first
- Draw foreground layer on top, centered
- This produces a clean, professional look standard in TikTok product content

**Aspect ratio exceptions:**
- If source image is already close to 9:16 (height > width × 1.5): scale to fill directly without blur background
- If screenshot image (already full-width 390px): scale to 1080px width, center vertically, blur-background fill for remaining height

### 7.3 Text positioning and safe margins

**Safe zone:** Text must remain inside a 900×1760 px inner frame, leaving 90px margin on all sides.

| Position value | Vertical anchor | Horizontal | Y coordinate |
|---|---|---|---|
| `top-center` | Top of text block | Centered in 900px safe width | 100px from top (80px margin + 20px padding) |
| `center` | Middle of text block | Centered in 900px safe width | 960px (vertical center), adjusted for multi-line |
| `bottom` | Bottom of text block | Centered in 900px safe width | Bottom of last line at 1820px from top |

**Font sizes:**

| Segment | Default size | Notes |
|---|---|---|
| Segment 0 — hook | 78px | Largest — must stop the scroll |
| Segment 1 — price | 72px | Large — price is the CTA |
| Segment 2 — benefit | 66px | Medium — supporting information |
| Segment 3 — social proof | 66px | Medium — supporting information |
| Segment 4 — CTA | 72px | Large — drive action |

Override via `--font-size` scales all sizes proportionally from the base.

**Multi-line rules:**
- Max width per line: 900px (safe zone width)
- If text exceeds 900px when measured at the segment's font size: wrap at the last word boundary before the limit
- Line spacing: `font_size × 1.25`
- For multi-line text, the `center` position centers the entire text block (not just the first line)
- Maximum lines: 3. If text wraps beyond 3 lines after word wrap, reduce font size by 6px and retry

**Text colors and their outline colors:**

| Color value | Rendered color | Outline color |
|---|---|---|
| `white` | `#FFFFFF` | `#000000` (black outline, 3px) |
| `yellow` | `#FFE600` | `#000000` (black outline, 3px) |
| `red` | `#FF2D2D` | `#FFFFFF` (white outline, 3px) |

### 7.4 Ken Burns motion (still image animation)

All still image segments use a subtle Ken Burns effect to add motion and prevent the video from feeling static.

**Scale and direction by segment and variant:**

| Variant | Segment 0 | Segment 1 | Segment 2 | Segment 3 | Segment 4 |
|---|---|---|---|---|---|
| A | Zoom in 100→108% | Zoom in 100→106% | Pan right 0→30px | Zoom in 100→108% | Zoom out 108→100% |
| B | Pan left 0→-30px | Zoom in 100→106% | Zoom in 100→110% | Pan right 0→20px | Zoom in 100→105% |
| C | Zoom out 108→100% | Pan left 0→-20px | Pan right 0→30px | Zoom in 100→108% | Zoom out 108→100% |
| D | Pan right 0→30px | Zoom in 100→108% | Zoom out 108→100% | Zoom in 100→106% | Pan left 0→-20px |

**Pan direction convention:** positive x = pan right (image moves left on screen, revealing right side), negative x = pan left.

**Implementation approach:**
- Use MoviePy's `clip.resize(lambda t: scale_at_t)` for zoom
- Use `clip.set_position(lambda t: (x_at_t, y_at_t))` for pan
- Set `clip.duration` to the segment's duration from the config
- All motion is linear (no easing for MVP)

**Why this matters:** All 4 variants share the hook segment asset (main product image). Different zoom/pan directions on that shared image ensure Variant A visually differs from B, C, D even at the first frame.

### 7.5 Transitions

**MVP: hard cuts only.** No dissolves, cross-fades, or wipes. The 5 segments are concatenated using MoviePy's `concatenate_videoclips` with `method="compose"`.

Hard cuts are standard on high-performing TikTok product videos. Do not add transition effects in MVP.

### 7.6 Segment composition pipeline (per segment)

For each of the 5 segments in a variant:

1. Load the selected asset as a Pillow RGBA image
2. Apply scale-to-fill with blur background (Section 7.2) → produce 1080×1920 RGBA frame
3. Convert to MoviePy `ImageClip` with duration = `segment.end - segment.start`
4. Apply Ken Burns motion per variant/segment table (Section 7.4)
5. Create text overlay RGBA image using Hebrew/RTL pipeline (Section 6.2)
6. Convert text overlay to MoviePy `ImageClip` (same duration)
7. `CompositeVideoClip([image_clip, text_clip])` at 1080×1920

After composing all 5 segment clips: `concatenate_videoclips(segments, method="compose")`

---

## 8. QA Rules

### 8.1 Pre-generation checks (Phase 2 and 3 — run before rendering)

These checks fail fast. On failure: exit code 2 (config/manifest problems require agent re-run, not retry).

| Check | Rule | On failure |
|---|---|---|
| PG-1 | Config has exactly 4 variants with ids A, B, C, D | Exit 2 |
| PG-2 | Each variant has exactly 5 segments | Exit 2 |
| PG-3 | Segment 0 of every variant has `start == 0` (hook first) | Exit 2 |
| PG-4 | Segment 4 of every variant has text containing the `cta_id` value (CTA present) | Exit 2 |
| PG-5 | Total duration (segment[4].end) is between 13 and 17 for every variant | Exit 2 |
| PG-6 | All 4 text colors are valid (`white`, `yellow`, `red`) | Exit 2 |
| PG-7 | All 4 position values are valid (`top-center`, `center`, `bottom`) | Exit 2 |
| PG-8 | Manifest `qa_passed == true` | Exit 2 |
| PG-9 | Manifest has >= 5 product images | Exit 2 |

### 8.2 Post-generation checks (Phase 5 — run after each MP4 is written)

These checks use `ffprobe` for file inspection. On failure: retry variant generation (up to 3×).

Run ffprobe with:
```
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,codec_name,duration -show_entries format=size -of json <filepath>
```

| Check | Rule | Retry behavior |
|---|---|---|
| PG-A | File exists at expected path | Retry generation |
| PG-B | File size between 500 KB and 50 MB | Retry generation |
| PG-C | Duration between 13.0s and 17.0s | Retry generation |
| PG-D | Resolution exactly 1080×1920 | Retry generation |
| PG-E | Video codec is h264 | Retry generation |
| PG-F | Frame rate is 30fps (r_frame_rate = "30/1") | Retry generation |
| PG-G | No audio stream present | Retry generation |
| PG-H | First frame is not all-black — sample frame at t=0.5s using ffprobe, check mean brightness > 5 | Retry generation |
| PG-I | No two variant files are identical — compare SHA-256 hashes of all 4 files | Log warning only (not a retry trigger — identical hashes mean config error, not generation error) |
| PG-J | Text is confirmed present in config for segments 0 and 4 (re-check PG-3 and PG-4 before retry) | Verify config before retry |

**Black frame detection (PG-H) detail:**  
Use ffprobe to extract one frame at t=0.5s:
```
ffprobe -v error -select_streams v:0 -show_entries frame=pkt_pts_time,pix_fmt -skip_frame nokey -read_intervals "%+#1" -of json <filepath>
```
If this cannot be read, use ffmpeg to extract the frame as a PNG, then check mean pixel value with Pillow. If mean < 5 across all channels: the frame is effectively black → retry.

### 8.3 Pass thresholds

| Result | Condition | What happens |
|---|---|---|
| Full success | All 4 variants pass all PG-A through PG-J checks | Exit code 0. Print all 4 file paths with ✅. |
| Partial success | 3 variants pass, 1 fails after 3 retries | Exit code 1. Print 3 ✅ paths, 1 ⚠️ FAILED path. |
| Failed | Fewer than 3 variants pass after retries | Exit code 2. Print FAILED — REQUIRES HUMAN REVIEW. |

---

## 9. Retry / Failure Behavior

### 9.1 Per-variant retry logic

```
for variant in [A, B, C, D]:
    for attempt in range(1, 4):  # attempts 1, 2, 3
        generate variant
        run QA checks for variant
        if all checks pass:
            break  # success, move on
        else:
            log "[generate_videos] Variant [ID] attempt [N]/3 failed: [check name]. Retrying..."
            delete partial output file if exists
    else:
        mark variant as FAILED
        log "[generate_videos] Variant [ID] FAILED after 3 attempts — REQUIRES HUMAN REVIEW"
```

### 9.2 Exit codes

| Code | Meaning | When |
|---|---|---|
| 0 | All 4 variants generated and passed QA | Full success |
| 1 | 3 variants passed, 1 failed after 3 retries | Partial success — usable for upload |
| 2 | Pre-generation check failed (config/manifest invalid) OR fewer than 3 variants passed | FAILED — REQUIRES HUMAN REVIEW |

### 9.3 stdout output (consumed by /tiktok agent)

Phase progress:
```
[generate_videos] Phase 1 — Font: using C:\Windows\Fonts\tahoma.ttf (Hebrew verified)
[generate_videos] Phase 2 — Config loaded: 4 variants, 5 segments each
[generate_videos] Phase 3 — Manifest loaded: 8 product images, 4 screenshots
[generate_videos] Phase 4 — Generating variant A...
[generate_videos] Phase 4 — Generating variant B...
[generate_videos] Phase 4 — Generating variant C...
[generate_videos] Phase 4 — Generating variant D...
```

Retry:
```
[generate_videos] Variant C attempt 2/3 failed: PG-D resolution mismatch (got 1080x1080). Retrying...
```

Full success (exit 0):
```
✅ Videos generated — 4/4 variants ready
C:\Automation\TikTok\videos\2026-06-10-product-003-A.mp4 ✅  (15s, 4.2MB)
C:\Automation\TikTok\videos\2026-06-10-product-003-B.mp4 ✅  (15s, 3.9MB)
C:\Automation\TikTok\videos\2026-06-10-product-003-C.mp4 ✅  (15s, 4.1MB)
C:\Automation\TikTok\videos\2026-06-10-product-003-D.mp4 ✅  (15s, 4.0MB)
```

Partial success (exit 1):
```
⚠️  Videos generated — 3/4 variants ready
C:\Automation\TikTok\videos\2026-06-10-product-003-A.mp4 ✅  (15s, 4.2MB)
C:\Automation\TikTok\videos\2026-06-10-product-003-B.mp4 ✅  (15s, 3.9MB)
C:\Automation\TikTok\videos\2026-06-10-product-003-C.mp4 ⚠️  FAILED — REQUIRES HUMAN REVIEW
C:\Automation\TikTok\videos\2026-06-10-product-003-D.mp4 ✅  (15s, 4.0MB)
Reason for C failure: PG-D — resolution mismatch after 3 retries.
```

Failed (exit 2):
```
❌ FAILED — REQUIRES HUMAN REVIEW
Reason: PG-2 — Variant B has only 4 segments (expected 5). Re-run /tiktok to regenerate video-config.json.
```

---

## 10. Test Plan

All tests are manual for MVP. Run in order before declaring the script production-ready.

### Group A — Happy Path

| Test | Input | Expected result |
|---|---|---|
| A1 | Valid config + manifest with 8 images, 5 screenshots | Exit 0. 4 MP4 files in `videos/`. All pass QA. Duration ≈15s. |
| A2 | Same inputs, run twice | Second run overwrites first cleanly. No partial files. |
| A3 | `--variant A` only | Only `...-A.mp4` is generated. B, C, D are untouched. |

### Group B — Hebrew Text

| Test | Input | Expected result |
|---|---|---|
| B1 | Config with Hebrew hook "לא תאמיני כמה זה עולה" | Text visible in first frame of output MP4. Characters in correct RTL order. No reversed text. |
| B2 | Long Hebrew hook that exceeds 900px when rendered | Text wraps to 2 lines. Both lines within safe margins. |
| B3 | Text with mixed Hebrew + numbers ("רק 45₪ בעלי אקספרס") | Numbers and ₪ symbol appear on the left (correct BiDi rendering for Hebrew-dominant text). |
| B4 | Hook type `white` on a bright product image | Black outline is visible. Text is readable. |

### Group C — Asset Selection

| Test | Condition | Expected result |
|---|---|---|
| C1 | Manifest has screenshot_price | Segment 1 uses `price.png`, not a product image. |
| C2 | Manifest has no screenshot_price | Segment 1 falls back to `product_images[1]`. |
| C3 | Manifest has only 5 product images | Benefit segment `variant_offset` wraps: D uses `detail_images[3 % 4]` = `detail_images[3 % 4]`. No index error. |
| C4 | Manifest has screenshot_rating | Segment 3 uses `rating.png`. |
| C5 | Manifest has no screenshot_rating but has screenshot_review | Segment 3 falls back to `review1.png`. |

### Group D — Video Output Properties

| Test | Check tool | Expected result |
|---|---|---|
| D1 | ffprobe on any output MP4 | width=1080, height=1920, codec=h264, r_frame_rate=30/1, duration between 13–17 |
| D2 | ffprobe audio streams | No audio stream present |
| D3 | Pillow open on frame extracted from MP4 | Image opens without error. Not all-black. |
| D4 | SHA-256 hash comparison of all 4 MP4s | All 4 hashes are different (variants are not identical) |

### Group E — Error Handling

| Test | Condition | Expected result |
|---|---|---|
| E1 | `--product-id` points to missing config | Exit 2. Error: "video-config.json not found." |
| E2 | Config has only 3 variants | Exit 2. PG-1 fails: "Expected 4 variants (A,B,C,D), found 3." |
| E3 | Manifest `qa_passed == false` | Exit 2. PG-8 fails. |
| E4 | Font not found at any search path | Exit 2. Error: "No Hebrew-compatible font found. Install Noto Sans Hebrew or set --font-path." |
| E5 | `--date 2026-13-01` (invalid month) | Exit 2. Validation error immediately. |

### Group F — Retry Behavior

| Test | Condition | Expected result |
|---|---|---|
| F1 | Simulate MoviePy encode failure on attempt 1 | Attempt 2 succeeds. Final MP4 ✅. retry_count = 1 in stdout. |
| F2 | Simulate failure on all 3 attempts for variant C | Variants A, B, D succeed. C marked FAILED. Exit 1 (3/4 pass). |
| F3 | Simulate failure on 4 variants | All 4 failed after 3 attempts each. Exit 2. |

### Group G — Ken Burns / Visual Differentiation

| Test | Action | Expected result |
|---|---|---|
| G1 | Extract frame at t=0.1s and t=1.9s from Variant A | Frame at 1.9s shows slightly more zoom than 0.1s (zoom-in confirmed). |
| G2 | Extract frame at t=0.1s from all 4 variants | Crop region differs between variants (different pan/zoom starting points). |

---

## 11. Implementation Checklist

### Phase 0 — Setup
- [ ] `argparse` for `--product-id`, `--date`, `--output-dir`, `--assets-dir`, `--data-dir`, `--font-path`, `--font-size`, `--variant`
- [ ] Validate `--product-id` matches `[0-9A-Za-z_-]+`
- [ ] Validate `--date` matches `^\d{4}-\d{2}-\d{2}$`
- [ ] Verify `data/[PRODUCT_ID]-video-config.json` exists — exit 2 if missing
- [ ] Verify `assets/[PRODUCT_ID]/manifest.json` exists — exit 2 if missing
- [ ] Create `videos/` directory with `pathlib.Path.mkdir(parents=True, exist_ok=True)`

### Phase 1 — Font
- [ ] Check font search order (see Section 6.3) stopping at first usable file
- [ ] For each candidate: attempt `PIL.ImageFont.truetype(path, 72)`, render `ש`, verify output is not tofu
- [ ] If no font passes: exit 2 with specific message
- [ ] Load selected font at all required sizes (78, 72, 66) upfront
- [ ] Log: `[generate_videos] Phase 1 — Font: using [path] (Hebrew verified)`

### Phase 2 — Load and validate config
- [ ] `json.load()` the config file
- [ ] Run all PG-1 through PG-7 pre-generation checks
- [ ] Exit 2 immediately on any failure with specific check name in message
- [ ] Build variant dict keyed by "A"/"B"/"C"/"D" for quick lookup

### Phase 3 — Load manifest and build asset index
- [ ] `json.load()` the manifest file
- [ ] Run PG-8 and PG-9 checks — exit 2 on failure
- [ ] Build typed buckets: `main_image`, `product_images`, `detail_images`, `screenshot_*`, `scroll_asset`
- [ ] Resolve absolute paths for all assets: `base_assets_dir / product_id / entry["file_path"]`
- [ ] Verify all resolved paths exist on disk — warn (not fail) for any missing optional screenshot

### Phase 4 — Per-variant generation loop
For each variant in [A, B, C, D] (or only the specified `--variant`):

- [ ] Select assets for all 5 segments using priority tables (Section 5.2)
- [ ] Log selected assets for traceability
- [ ] `retry_count = 0`; wrap in retry loop (max 3 attempts)

Per segment (run 5 times per variant):
- [ ] Load asset image with `PIL.Image.open(path).convert("RGBA")`
- [ ] Apply scale-to-fill with blur background (Section 7.2):
  - [ ] Scale foreground to fit within 1080×1920 preserving aspect ratio
  - [ ] Scale background to fill 1080×1920, center-crop, apply `ImageFilter.GaussianBlur(radius=35)`, reduce brightness ×0.7
  - [ ] Composite foreground over background on a new 1080×1920 RGBA canvas
- [ ] Convert composite to MoviePy `ImageClip(np.array(pil_image)).set_duration(segment_duration)`
- [ ] Apply Ken Burns: look up motion type from table (Section 7.4), apply `clip.resize()` or `clip.set_position()` with lambda
- [ ] Build text overlay (Section 6.2):
  - [ ] `get_display(segment.text)` via python-bidi
  - [ ] Measure width at segment font size; word-wrap if > 900px
  - [ ] Create 1080×1920 RGBA transparent image
  - [ ] Draw black/white outline at ±3px offsets
  - [ ] Draw main text in segment color
  - [ ] Compute y-position from segment.position enum
  - [ ] Compute x-position: center of 1080px (safe-zone centered)
  - [ ] Convert to `ImageClip(np.array(text_pil)).set_duration(segment_duration)`
- [ ] `CompositeVideoClip([image_clip, text_clip], size=(1080, 1920))`

After all 5 segments:
- [ ] `concatenate_videoclips(all_5_segments, method="compose")`
- [ ] `.write_videofile(output_path, fps=30, codec="libx264", ffmpeg_params=["-crf","23","-preset","slow","-pix_fmt","yuv420p"], audio=False, logger=None)`
- [ ] On MoviePy exception: log retry, delete partial output file, increment retry_count, continue loop
- [ ] On success: break retry loop, proceed to QA

### Phase 5 — QA
- [ ] Construct ffprobe command (Section 8.2)
- [ ] Run via `subprocess.run()`, parse JSON output
- [ ] Check PG-A through PG-J in order
- [ ] For PG-H (black frame): run ffmpeg frame extraction, open with Pillow, compute mean
- [ ] For PG-I (duplicate hash): compute `hashlib.sha256()` for each of the 4 files, compare all pairs
- [ ] Log each check result
- [ ] On check failure: increment retry, re-enter Phase 4 loop for that variant
- [ ] After all variants: compute pass count
- [ ] Determine exit code: 0, 1, or 2

### Phase 6 — Report
- [ ] Print full summary block (Section 9.3 format)
- [ ] `sys.exit(code)`

---

## 12. Dependencies

| Package | Version | Purpose |
|---|---|---|
| `moviepy` | >= 1.0.3 | Video composition, clip concatenation, Ken Burns |
| `Pillow` | >= 10.0 | Image scaling, blur background, text rendering |
| `python-bidi` | >= 0.4.2 | Hebrew BiDi reordering for correct RTL display |
| `numpy` | >= 1.24 | MoviePy ↔ Pillow array conversion |
| `ffmpeg` | Any, on PATH | Video encoding (called by MoviePy) + ffprobe for QA |
| Standard library | — | `argparse`, `json`, `pathlib`, `hashlib`, `subprocess`, `sys`, `os` |

Install:
```
pip install moviepy Pillow python-bidi numpy
# ffmpeg must be installed separately and available on PATH
```

---

## 13. Notes — Future Enhancements (not in MVP)

| Enhancement | Description |
|---|---|
| Scroll video as hook footage | Use `scroll.mp4` asset as a video clip in the hook segment for variant D — adds real scroll motion instead of a still image |
| Cross-fade transitions | Replace hard cuts with 0.3s dissolves between segments |
| Dynamic font sizing | Auto-scale font size based on text length within each segment to maximize readability |
| Background music | Add a short royalty-free music loop at low volume; user still adds TikTok trending sound on upload |
| Thumbnail generation | Extract and save the best single frame as a JPEG thumbnail for A/B testing |
| Parallel variant rendering | Use `multiprocessing` to render all 4 variants simultaneously; reduces wall-clock time by ~75% |

---

*Specification version: 1.0*  
*Created: 2026-06-10*  
*Status: Ready for implementation*  
*Depends on: `generate_assets_spec.md` (asset collection must succeed before this script runs)*  
*Next step: Implement `generate_assets.py` first, verify assets are collected correctly, then implement `generate_videos.py` from this spec*
