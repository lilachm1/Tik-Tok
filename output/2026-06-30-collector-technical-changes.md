# Collector Technical Changes — 2026-06-30

**Summary:** Caption-based search implementation + bare-code safety logic

---

## Quick Reference

### Problem
Product 002 has 4 variants with:
- ❌ Identical caption text
- ❌ Bare CTA code "002" (no variant letter)
- ❌ Identity unconfirmable → metrics NOT written

### Solution Implemented
1. ✅ Caption-based search (searches caption, not overlay)
2. ✅ Bare-code detection (refuses to confirm shared codes)
3. ✅ Unverified identity blocking (treats as NOT_FOUND)

### Result
- Product 002: All 4 → NOT_FOUND (safe)
- Product 003: All 4 → CONFIRMED ✅
- Product 007: 3/4 → CONFIRMED ✅
- Product 008: 4/4 → CONFIRMED ✅

---

## Code Changes

### 1. Caption Extraction Function (NEW)

**File:** `scripts/tiktok_analytics_collect.py`
**Lines:** ~74-107

```python
def extract_caption_from_upload_package(product_id, variant_letter):
    """
    Extract TikTok caption text for a specific variant from its upload package.
    Returns the caption string, or None if not found.
    """
    pkg_files = list(OUTPUT_DIR.glob(f"*-product-{product_id}-upload_package.md"))
    if not pkg_files:
        return None

    try:
        text = pkg_files[0].read_text(encoding="utf-8")
    except Exception:
        return None

    variant_pattern = f"## VARIANT {variant_letter}"
    if variant_pattern not in text:
        return None

    start = text.index(variant_pattern)
    section = text[start:start+2000]

    for line in section.split('\n'):
        if line.startswith('CAPTION:'):
            caption = line.replace('CAPTION:', '').strip()
            if caption:
                return caption
            lines = section.split('\n')
            idx = lines.index(line)
            if idx + 1 < len(lines):
                next_line = lines[idx + 1].strip()
                if next_line and not next_line.startswith('#'):
                    return next_line
    return None
```

**Purpose:** Read actual TikTok caption from upload package.

---

### 2. Product Detection — Add Caption Field

**File:** `scripts/tiktok_analytics_collect.py`
**Lines:** ~175-190

```python
# Extract TikTok caption from upload package for search
caption = extract_caption_from_upload_package(pid, letter)
caption_search_text = caption[:30].strip() if caption else ""

products[pid]["variants"][letter] = {
    "variant":     f"{pid}{letter}",
    "hook_type":   vcfg.get("hook_type", ""),
    "hook_text":   hook_text,
    "caption_search_text": caption_search_text,  # NEW
    "cta_code":    cta_code,
    "cta_style":   "comment",
    "tracking_id": f"product{pid}_{letter}",
    "bare_index":  bare_index,  # NEW
}
```

**Change:** Added `caption_search_text` field to variant metadata.

---

### 3. search_box_find() — Bare Code Safety

**File:** `scripts/tiktok_analytics_collect.py`
**Lines:** ~591-650

```python
def search_box_find(page, caption_search_text, cta_code):
    """
    Use TikTok Studio's 'Search post description' input to filter the content
    list by caption_search_text (first 20-30 chars of the TikTok caption),
    then confirm identity via CTA code or unique single result.
    """
    query = caption_search_text.strip() if caption_search_text else ""
    if not query:
        return False, {}

    # Type search query
    box = page.locator("input[placeholder*='Search']").first
    box.click()
    box.fill(query)
    time.sleep(2.5)

    # Detect bare code: 3 digits only (e.g., "002")
    is_bare_code = bool(re.match(r'^\d{3}$', cta_code))

    # 1. Try CTA code selector — ONLY if variant-level code
    if not is_bare_code:
        for sel in [f"text={cta_code}", f"[aria-label*='{cta_code}']"]:
            try:
                el = page.locator(sel).first
                if el.is_visible(timeout=2_000):
                    print(f"    search_box_find: CTA confirmed [{sel[:25]}]")
                    row_m = _scrape_row(el)
                    el.click()
                    return True, row_m
            except Exception:
                pass

    # For bare-code products, identity cannot be confirmed
    if is_bare_code:
        print(f"    search_box_find: NOT FOUND (bare code '{cta_code}' — identity unconfirmable via search)")
        return False, {}

    # ... rest of function ...
```

**Changes:**
1. Parameter changed from `hook_text` to `caption_search_text`
2. Added `is_bare_code` detection
3. Disabled CTA confirmation for bare codes

---

### 4. collect_one_variant() — Signature

**File:** `scripts/tiktok_analytics_collect.py`
**Line:** ~689

```python
def collect_one_variant(page, cta_code, skip_count=0, caption_search_text=""):
    # Changed from hook_text="" to caption_search_text=""

    if caption_search_text:
        found, row_metrics = search_box_find(page, caption_search_text, cta_code)
```

**Change:** Pass `caption_search_text` instead of `hook_text`.

---

### 5. Main Loop — Unverified Identity Blocking

**File:** `scripts/tiktok_analytics_collect.py`
**Lines:** ~965-973

```python
raw = collect_one_variant(page, cta_code, skip_count=skip_count,
                          caption_search_text=vinfo.get("caption_search_text", ""))

# Bare-code variants found via skip_count have UNVERIFIED identity
is_bare_code = bool(re.match(r'^\d{3}$', cta_code))
if not raw["not_found"] and is_bare_code and skip_count > 0:
    print(f"  WARNING: {label} found via order-based matching (skip_count={skip_count})")
    print(f"           Identity UNVERIFIED — bare code '{cta_code}' with shared caption")
    print(f"           Metrics NOT written (require variant-level CTA for confirmation)")
    raw["not_found"] = True  # Treat as NOT_FOUND for CSV
```

**Purpose:** Block writing metrics when identity cannot be confirmed.

---

## Behavior Changes

### Before (Wrong)
```
002A: searches "לא תאמיני כמה..." (hook_text) → 0 results → NOT FOUND
002B: searches "ראיתי את זה..." (hook_text) → 0 results → NOT FOUND
```

### After (Correct)
```
002A: searches "מצאתי מחזיק טלפון..." (caption) → found but bare code "002" → UNVERIFIED → NOT_FOUND
002B: searches "מצאתי מחזיק טלפון..." (caption) → found but bare code "002" → UNVERIFIED → NOT_FOUND
```

---

## Testing Results

### Product 003 (Variant-Level CTAs) ✅
```
003A: search "מצאתי אונס..." → CTA "003A" confirmed → views=354 ✅
003B: search "מצאתי אונס..." → CTA "003B" confirmed → views=360 ✅
003C: search "מצאתי אונס..." → CTA "003C" confirmed → views=1 ✅
003D: search "מצאתי אונס..." → CTA "003D" confirmed → views=2 ✅
```

### Product 002 (Bare Code) ⚠️
```
002A: search "מצאתי מחזיק..." → bare code "002" → UNVERIFIED → NOT_FOUND
002B: search "מצאתי מחזיק..." → bare code "002" → UNVERIFIED → NOT_FOUND
002C: search "מצאתי מחזיק..." → bare code "002" → UNVERIFIED → NOT_FOUND
002D: search "מצאתי מחזיק..." → bare code "002" → UNVERIFIED → NOT_FOUND
```

All marked NOT_FOUND (safe — no incorrect data written).

---

## Resolution Options

### Option A: Edit Captions (5 min)
Edit 4 TikTok captions to add variant letters:
- "כתבי 002 בתגובות" → "כתבי 002A בתגובות"
- "כתבי 002 בתגובות" → "כתבי 002B בתגובות"
- "כתבי 002 בתגובות" → "כתבי 002C בתגובות"
- "כתבי 002 בתגובות" → "כתבי 002D בתגובות"

Then rerun: `python scripts/tiktok_analytics_collect.py --product-id 002 --update`

### Option B: DOM Investigation (1-2 hrs)
Complete `scripts/inspect_product_002_dom.py` to find unique identifiers (video ID, timestamp, href).

### Option C: Accept Loss
Mark Product 002 UNCOLLECTABLE, proceed with Products 003/007/008 only.

---

## Files Changed

| File | Lines | Status |
|------|-------|--------|
| `scripts/tiktok_analytics_collect.py` | 74-107 | ✅ Caption extraction function |
| `scripts/tiktok_analytics_collect.py` | 175-190 | ✅ Add caption field to variants |
| `scripts/tiktok_analytics_collect.py` | 591-668 | ✅ Bare-code safety in search |
| `scripts/tiktok_analytics_collect.py` | 689 | ✅ Signature change |
| `scripts/tiktok_analytics_collect.py` | 965-973 | ✅ Unverified blocking |
| `scripts/inspect_product_002_dom.py` | All | ⚠️ Created but incomplete |

---

## Quick Git Diff

```diff
@@ detect_all_products()
+    caption = extract_caption_from_upload_package(pid, letter)
+    caption_search_text = caption[:30].strip() if caption else ""

     products[pid]["variants"][letter] = {
         "variant":     f"{pid}{letter}",
         "hook_type":   vcfg.get("hook_type", ""),
         "hook_text":   hook_text,
+        "caption_search_text": caption_search_text,
         "cta_code":    cta_code,
         "cta_style":   "comment",
         "tracking_id": f"product{pid}_{letter}",
+        "bare_index":  bare_index,
     }

@@ search_box_find()
-def search_box_find(page, hook_text, cta_code):
+def search_box_find(page, caption_search_text, cta_code):

+    # Detect bare code
+    is_bare_code = bool(re.match(r'^\d{3}$', cta_code))

     # Try CTA code selector
+    if not is_bare_code:
         for sel in [f"text={cta_code}", ...]:
             ...

+    # For bare-code products, identity cannot be confirmed
+    if is_bare_code:
+        print("NOT FOUND (bare code — identity unconfirmable)")
+        return False, {}

@@ collect_one_variant()
-def collect_one_variant(page, cta_code, skip_count=0, hook_text=""):
+def collect_one_variant(page, cta_code, skip_count=0, caption_search_text=""):

-    if hook_text:
-        found, row_metrics = search_box_find(page, hook_text, cta_code)
+    if caption_search_text:
+        found, row_metrics = search_box_find(page, caption_search_text, cta_code)

@@ main() collection loop
     raw = collect_one_variant(page, cta_code, skip_count=skip_count,
-                               hook_text=vinfo.get("hook_text", ""))
+                               caption_search_text=vinfo.get("caption_search_text", ""))

+    # Bare-code variants found via skip_count have UNVERIFIED identity
+    is_bare_code = bool(re.match(r'^\d{3}$', cta_code))
+    if not raw["not_found"] and is_bare_code and skip_count > 0:
+        print("WARNING: Identity UNVERIFIED")
+        raw["not_found"] = True
```

---

**Reference Date:** 2026-06-30
**Status:** Caption search ✅ | Bare-code safety ✅ | Product 002 BLOCKED (awaiting user decision)
