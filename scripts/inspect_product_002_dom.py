"""
DOM Inspector for Product 002 Variants
Extracts ALL unique properties from each Product 002 row in TikTok Studio
to determine if caption edits are truly required.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
import re

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
SESSION_FILE = DATA_DIR / "tiktok-session.json"
DESKTOP_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def extract_all_properties(element):
    """Extract every possible property from a DOM element."""
    props = {}

    # Basic attributes
    try:
        props['id'] = element.get_attribute('id') or ''
        props['class'] = element.get_attribute('class') or ''
        props['data-e2e'] = element.get_attribute('data-e2e') or ''
        props['role'] = element.get_attribute('role') or ''
        props['aria-label'] = element.get_attribute('aria-label') or ''
        props['href'] = element.get_attribute('href') or ''
        props['title'] = element.get_attribute('title') or ''
    except:
        pass

    # All data-* attributes
    try:
        all_attrs = element.evaluate("el => Array.from(el.attributes).map(a => [a.name, a.value])")
        for name, value in all_attrs:
            if name.startswith('data-'):
                props[name] = value
    except:
        pass

    # Text content
    try:
        props['text_content'] = element.text_content()[:200]  # First 200 chars
        props['inner_text'] = element.inner_text()[:200]
    except:
        pass

    return props

def inspect_video_row(row_element, index):
    """Extract all unique identifiers from a video row."""
    print(f"\n{'='*70}")
    print(f"INSPECTING ROW #{index}")
    print(f"{'='*70}")

    data = {
        'row_index': index,
        'row_props': {},
        'links': [],
        'images': [],
        'text_elements': [],
        'aria_elements': [],
        'data_attributes': [],
        'video_metadata': {}
    }

    # Extract row-level properties
    data['row_props'] = extract_all_properties(row_element)
    print(f"\nRow properties:")
    for k, v in data['row_props'].items():
        if v:
            print(f"  {k}: {v[:100] if isinstance(v, str) else v}")

    # Find all links in the row
    try:
        links = row_element.locator('a').all()
        print(f"\nFound {len(links)} link(s):")
        for i, link in enumerate(links):
            link_data = {
                'index': i,
                'href': link.get_attribute('href') or '',
                'aria-label': link.get_attribute('aria-label') or '',
                'text': (link.text_content() or '')[:100]
            }
            data['links'].append(link_data)
            print(f"  Link {i}: href={link_data['href'][:80] if link_data['href'] else 'none'}")
            if link_data['aria-label']:
                print(f"           aria-label={link_data['aria-label'][:80]}")
    except Exception as e:
        print(f"  Error extracting links: {e}")

    # Find all images/thumbnails
    try:
        images = row_element.locator('img').all()
        print(f"\nFound {len(images)} image(s):")
        for i, img in enumerate(images):
            img_data = {
                'index': i,
                'src': img.get_attribute('src') or '',
                'alt': img.get_attribute('alt') or '',
                'data-poster': img.get_attribute('data-poster') or ''
            }
            data['images'].append(img_data)
            print(f"  Image {i}: src={img_data['src'][:80] if img_data['src'] else 'none'}")
    except Exception as e:
        print(f"  Error extracting images: {e}")

    # Find elements with aria-* attributes
    try:
        aria_elements = row_element.locator('[aria-label], [aria-describedby], [role]').all()
        print(f"\nFound {len(aria_elements)} aria element(s):")
        for i, elem in enumerate(aria_elements):
            aria_data = {
                'index': i,
                'aria-label': elem.get_attribute('aria-label') or '',
                'role': elem.get_attribute('role') or '',
                'text': (elem.text_content() or '')[:50]
            }
            data['aria_elements'].append(aria_data)
            if aria_data['aria-label']:
                print(f"  Aria {i}: {aria_data['aria-label'][:80]}")
    except Exception as e:
        print(f"  Error extracting aria elements: {e}")

    # Find all elements with data-* attributes
    try:
        data_elements = row_element.locator('[data-e2e], [data-video-id], [data-item-id]').all()
        print(f"\nFound {len(data_elements)} data-* element(s):")
        for i, elem in enumerate(data_elements):
            data_attr = {
                'index': i,
                'data-e2e': elem.get_attribute('data-e2e') or '',
                'data-video-id': elem.get_attribute('data-video-id') or '',
                'data-item-id': elem.get_attribute('data-item-id') or ''
            }
            data['data_attributes'].append(data_attr)
            if any(data_attr.values()):
                print(f"  Data {i}: {data_attr}")
    except Exception as e:
        print(f"  Error extracting data attributes: {e}")

    # Try to extract video ID from any href
    for link in data['links']:
        if link['href']:
            # TikTok video URLs often contain /video/123456789
            match = re.search(r'/video/(\d+)', link['href'])
            if match:
                data['video_metadata']['video_id_from_url'] = match.group(1)
                print(f"\nExtracted video ID: {match.group(1)}")
                break

    # Try to extract timestamp/date
    try:
        # Look for time elements or date strings
        time_elements = row_element.locator('time, [datetime], [data-timestamp]').all()
        if time_elements:
            for elem in time_elements:
                datetime_attr = elem.get_attribute('datetime') or elem.get_attribute('data-timestamp')
                if datetime_attr:
                    data['video_metadata']['timestamp'] = datetime_attr
                    print(f"\nFound timestamp: {datetime_attr}")
                    break
    except:
        pass

    return data

def compare_rows(all_data):
    """Compare all rows and identify which fields are identical vs unique."""
    print(f"\n\n{'='*70}")
    print("COMPARISON: IDENTICAL vs UNIQUE FIELDS")
    print(f"{'='*70}\n")

    if len(all_data) < 2:
        print("Not enough rows to compare.")
        return

    # Compare video IDs
    video_ids = [d['video_metadata'].get('video_id_from_url', 'N/A') for d in all_data]
    print(f"Video IDs from URLs:")
    for i, vid in enumerate(video_ids):
        print(f"  Row {i}: {vid}")
    if len(set(video_ids)) == len(video_ids):
        print("  ✓ UNIQUE - Can be used for identification!")
    else:
        print("  ✗ NOT UNIQUE - Cannot distinguish variants")

    # Compare timestamps
    timestamps = [d['video_metadata'].get('timestamp', 'N/A') for d in all_data]
    print(f"\nTimestamps:")
    for i, ts in enumerate(timestamps):
        print(f"  Row {i}: {ts}")
    if len(set(timestamps)) == len(timestamps):
        print("  ✓ UNIQUE - Can be used for identification!")
    else:
        print("  ✗ NOT UNIQUE - Cannot distinguish variants")

    # Compare href links
    print(f"\nPrimary link hrefs:")
    for i, d in enumerate(all_data):
        primary_href = d['links'][0]['href'] if d['links'] else 'N/A'
        print(f"  Row {i}: {primary_href[:80] if primary_href != 'N/A' else 'N/A'}")
    hrefs = [d['links'][0]['href'] if d['links'] else '' for d in all_data]
    if len(set(hrefs)) == len(hrefs) and all(hrefs):
        print("  ✓ UNIQUE - Can be used for identification!")
    else:
        print("  ✗ NOT UNIQUE or missing - Cannot distinguish variants")

    # Compare image sources
    print(f"\nThumbnail image sources:")
    for i, d in enumerate(all_data):
        primary_img = d['images'][0]['src'] if d['images'] else 'N/A'
        print(f"  Row {i}: {primary_img[:80] if primary_img != 'N/A' else 'N/A'}")
    img_srcs = [d['images'][0]['src'] if d['images'] else '' for d in all_data]
    if len(set(img_srcs)) == len(img_srcs) and all(img_srcs):
        print("  ✓ UNIQUE - Can be used for identification!")
    else:
        print("  ✗ NOT UNIQUE or missing - Cannot distinguish variants")

    # Compare text content
    print(f"\nRow text content (first 100 chars):")
    for i, d in enumerate(all_data):
        text = d['row_props'].get('text_content', 'N/A')[:100]
        print(f"  Row {i}: {text}")
    texts = [d['row_props'].get('text_content', '') for d in all_data]
    if len(set(texts)) == len(texts):
        print("  ✓ UNIQUE - Different text in each row")
    else:
        print("  ✗ IDENTICAL - All rows have same text")

    print(f"\n{'='*70}")
    print("CONCLUSION:")
    print(f"{'='*70}")

    # Determine if any unique identifier exists
    unique_identifiers = []
    if len(set(video_ids)) == len(video_ids) and all(v != 'N/A' for v in video_ids):
        unique_identifiers.append("Video ID (from URL)")
    if len(set(timestamps)) == len(timestamps) and all(t != 'N/A' for t in timestamps):
        unique_identifiers.append("Timestamp")
    if len(set(hrefs)) == len(hrefs) and all(hrefs):
        unique_identifiers.append("Link href")
    if len(set(img_srcs)) == len(img_srcs) and all(img_srcs):
        unique_identifiers.append("Thumbnail URL")

    if unique_identifiers:
        print(f"\n✓ UNIQUE IDENTIFIERS FOUND:")
        for uid in unique_identifiers:
            print(f"  - {uid}")
        print(f"\nCONCLUSION: Caption edits are NOT required.")
        print(f"The collector can use the above identifier(s) to distinguish variants.")
    else:
        print(f"\n✗ NO UNIQUE IDENTIFIERS FOUND")
        print(f"\nCONCLUSION: Caption edits ARE required.")
        print(f"All 4 Product 002 variants share identical identifying properties.")
        print(f"The only way to reliably distinguish them is to add variant-level")
        print(f"CTA codes (002A, 002B, 002C, 002D) to each video's caption.")

def main():
    print("="*70)
    print("DOM INSPECTOR FOR PRODUCT 002")
    print("="*70)

    with sync_playwright() as p:
        # Load session
        if not SESSION_FILE.exists():
            print(f"ERROR: Session file not found: {SESSION_FILE}")
            print("Run: python scripts/tiktok_session_login.py")
            return

        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            storage_state=str(SESSION_FILE),
            viewport=None,
            user_agent=DESKTOP_UA
        )
        page = context.new_page()

        print("\nNavigating to TikTok Studio...")
        page.goto("https://www.tiktok.com/tiktokstudio/content", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)

        # Close any popup notifications first
        try:
            close_btn = page.locator('[aria-label="Close"], button:has-text("Close")').first
            if close_btn.is_visible(timeout=2000):
                close_btn.click()
                print("  Closed popup notification")
                page.wait_for_timeout(500)
        except:
            pass

        # Search for Product 002 using FULL shared caption
        print("\nSearching for Product 002 using full caption...")
        search_caption = "מצאתי מחזיק טלפון לרכב בעלי אקספרס ב-23₪ ואני לא מאמינה שזה קיים"

        try:
            search_input = page.locator('[placeholder*="Search"], input[placeholder*="search" i]').first
            if search_input.is_visible(timeout=3000):
                search_input.click()
                search_input.fill("")
                page.wait_for_timeout(300)
                search_input.type(search_caption, delay=30)
                print(f"  Typed search query")
                page.wait_for_timeout(3000)  # Wait for results to filter
            else:
                print("  WARNING: Search box not visible")
        except Exception as e:
            print(f"  ERROR: Could not search: {e}")

        # Now find visible video rows
        print("\nFinding visible video rows...")
        visible_videos = []

        # Look for table rows or list items with video content
        try:
            # Try finding by caption text that should be visible
            caption_elements = page.locator('[class*="caption"], [class*="content"], [class*="description"]').all()
            print(f"  Found {len(caption_elements)} potential caption/content elements")

            for el in caption_elements[:20]:
                try:
                    if el.is_visible(timeout=300):
                        text = el.text_content() or ""
                        if len(text) > 20 and ("מצאתי" in text or "טלפון" in text or "רכב" in text):
                            visible_videos.append(el)
                            print(f"    Video {len(visible_videos)}: {text[:80]}")
                except:
                    pass
        except:
            pass

        # If no luck, try finding ANY visible row-like element in the content area
        if len(visible_videos) == 0:
            print("\n  Fallback: Looking for ANY visible rows...")
            try:
                row_elements = page.locator('[role="row"], tr, li').all()
                for el in row_elements:
                    try:
                        if el.is_visible(timeout=300):
                            bbox = el.bounding_box()
                            if bbox and bbox["x"] > 200 and bbox["width"] > 400:
                                text = (el.text_content() or "")[:100]
                                if len(text) > 10:
                                    visible_videos.append(el)
                                    print(f"    Row {len(visible_videos)}: {text}")
                                    if len(visible_videos) >= 4:  # Stop after 4 rows
                                        break
                    except:
                        pass
            except Exception as e:
                print(f"  Error finding rows: {e}")

        print(f"\n  Total visible video elements found: {len(visible_videos)}")

        if len(visible_videos) == 0:
            print("\nERROR: No video links found. Check if search results are visible.")
            print("Taking screenshot for debugging...")
            page.screenshot(path="debug_no_rows.png")
            browser.close()
            return

        # Inspect up to 4 video links (all Product 002 variants)
        all_data = []
        for i, link in enumerate(visible_videos[:4]):
            # Inspect the link and its parent row container
            # The link is typically inside a table row or list item
            try:
                # Try to find parent row/container
                parent = link.locator('xpath=ancestor::tr | ancestor::li | ancestor::div[@role="row"]').first
                row_element = parent if parent else link
            except:
                row_element = link

            row_data = inspect_video_row(row_element, i)
            all_data.append(row_data)

        # Compare all rows
        if len(all_data) >= 2:
            compare_rows(all_data)

        # Save raw data to JSON
        output_file = OUTPUT_DIR / "product_002_dom_inspection.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        print(f"\nRaw data saved to: {output_file}")

        print("\nClosing browser...")
        browser.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERROR during inspection: {e}")
        import traceback
        traceback.print_exc()
