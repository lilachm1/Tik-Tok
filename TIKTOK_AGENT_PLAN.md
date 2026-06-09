# TikTok Affiliate Agent — Full Plan

**Owner:** Lilach  
**Market:** Israel (for now)  
**Video content language:** Hebrew  
**Daily time budget:** 2 hours  
**Products per day:** 1 (agent picks automatically)  
**Commands:** `/tiktok` (morning) and `/tiktok analyze` (evening)

---

## How It Works — Simple Version

**Morning:** Type `/tiktok` — agent does everything and gives you one ready package.  
**You:** Record screen + upload to TikTok.  
**Evening:** Type `/tiktok analyze` + paste your stats — agent tells you what to scale.

---

## Output Structure

All files are saved to `C:\Automation\TikTok\` (create this folder once during setup).

```
C:\Automation\TikTok\
├── output\
│   ├── 2026-06-03-product-002.md      ← full daily package (created by /tiktok)
│   ├── 2026-06-04-product-003.md
├── analysis\
│   ├── 2026-06-03-product-002-analysis.md   ← evening analysis (created by /tiktok analyze)
├── data\
│   └── video_results.csv               ← persistent learning data
```

**output/** — Created by `/tiktok` after each run. Contains the full package: product ID, product details, AliExpress URL, commission rate, review video links, and all 4 variants (storyboard + caption + hashtags). Review the next morning after an overnight run.

**analysis/** — Created by `/tiktok analyze` after each evening session. Contains the performance analysis, winner/loser breakdown, and tomorrow's recommendation.

**data/video_results.csv** — Appended by `/tiktok analyze` after every run. Read by `/tiktok` each morning to learn from past performance.

---

## Persistent Learning — How It Works

The agent builds a performance database over time instead of treating each day as a fresh start.

**After each `/tiktok analyze`:** All variant statistics are appended to `data/video_results.csv`.

**Before each `/tiktok` product selection:** The agent reads the CSV and calculates:
- Best performing hook type → bonus for matching products; winning hook moved to Variant A
- Best performing category → +2 bonus on scoring
- Best performing price range → +1 bonus on scoring

**CSV columns:**
```
product_id,variant,hook_type,category,price_ils,views,likes,comments,saves,winner
```

Example rows:
```
product_id,variant,hook_type,category,price_ils,views,likes,comments,saves,winner
002,002A,Price Shock,Mobile Phone Accessories,45,1200,89,34,67,false
002,002B,Curiosity,Mobile Phone Accessories,45,3400,234,89,145,true
003,003C,Problem/Solution,Interior Accessories,35,5100,412,167,290,true
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
|------|-------------------|--------|
| 0 | Reads video_results.csv — calculates best hook type, category, price range from history | Nothing |
| 1 | Finds 5 trending products (must have 2+ trend sources each), scores using new price model + history bonus | Nothing |
| 2 | Picks the highest-scoring product automatically (tie = cheaper wins) | Nothing |
| 3 | Finds the best AliExpress listing | Nothing |
| 4 | Safety check — no fake brands, no copyright risk | Nothing |
| 5 | Prepares AliExpress product URL + category + commission rate for manual link generation | Nothing |
| 6 | Finds review videos to screen record (TikTok, YouTube Shorts, AliExpress) | Nothing |
| 7 | Generates 4 video variants — historically winning hook type assigned to Variant A | Nothing |
| 8 | Writes storyboard for each of the 4 variants | Nothing |
| 9 | Writes caption for each of the 4 variants | Nothing |
| 10 | Saves full package to `C:\Automation\TikTok\output\YYYY-MM-DD-product-XXX.md` | Nothing |
| 11 | Shows the full ready-to-use package in chat | Nothing |
| — | Paste product URL into AliExpress Link Generator to create affiliate link | **You (1 min)** |
| — | Record screen | **You (1–2 min)** |
| — | Paste texts + upload to TikTok | **You (5–10 min)** |

### `/tiktok analyze` — Evening Command

| Step | What the Agent Does | You Do |
|------|-------------------|--------|
| 1 | Asks for your video stats | Paste: views, likes, comments, saves, clicks |
| 2 | Analyzes which hook style worked best | Nothing |
| 3 | Analyzes which product category is performing | Nothing |
| 4 | Tells you what to repeat tomorrow | Nothing |
| 5 | Tells you what to drop | Nothing |
| 6 | Appends all variant results to `data/video_results.csv` | Nothing |
| 7 | Saves analysis to `analysis/YYYY-MM-DD-product-XXX-analysis.md` | Nothing |
| 8 | Updates strategy for tomorrow's `/tiktok` run | Nothing |

---

## Before You Start — One-Time Setup

### Setup — Create Folders and Slash Commands (5 minutes)

Since you're an automation developer this will take you 2 minutes.

1. Create the TikTok project folder and subfolders:
   ```
   C:\Automation\TikTok\
   C:\Automation\TikTok\output\
   C:\Automation\TikTok\analysis\
   C:\Automation\TikTok\data\
   ```

2. In your Claude Code project folder, create this file:  
   `.claude/commands/tiktok.md`
3. Paste the **Morning Agent Prompt** below into that file
4. Create a second file:  
   `.claude/commands/tiktok-analyze.md`
5. Paste the **Evening Agent Prompt** below into that file

---

## Morning Agent Prompt — paste into `.claude/commands/tiktok.md`

```
You are a fully automatic TikTok Affiliate Agent for the Israeli market.

Rules:
- Run all steps automatically. Do not ask the user to make choices.
- All video content (hooks, storyboard, captions, hashtags) must be in Hebrew.
- Only show the final ready-to-use package at the end.
- Always prioritize products from 9% commission categories. Use 7% if needed. Avoid 3% commission categories unless no good 7%–9% product exists.
- Each product package must include a PRODUCT ID in format 001, 002, 003... The user sets the starting number at the top of this file (CURRENT_PRODUCT_ID). Use that number for the run and remind the user to increment it for next time.

CURRENT_PRODUCT_ID: 001

---

COMMISSION PRIORITY REFERENCE

9% commission categories (prioritize these first):
- Mobile Phone Accessories
- Interior Accessories
- Garden Supplies
- Children's Clothing
- Women's Clothing
- Men's Clothing

7% commission category (use if no strong 9% product found):
- Other Categories

3% commission categories (avoid unless no 7%–9% option exists):
- Mobile Phones
- Computer Peripherals
- Tablets
- Desktops & AIO
- Laptops
- Home Audio & Video
- Storage Device
- Internal Storage

---

STEP 0 — READ HISTORICAL PERFORMANCE

Before finding products, read: C:\Automation\TikTok\data\video_results.csv

If the file does not exist, skip this step and note:
> "No historical data yet — day 1 baseline run."

If the file exists, calculate:

1. BEST HOOK TYPE: Which hook type (Price Shock / Curiosity / Problem/Solution / TikTok Discovery) has the highest average saves + views across all rows? This is the winning hook.

2. BEST CATEGORY: Which product category has the best average engagement (views + saves) across all rows?

3. BEST PRICE RANGE: What price range (in ₪) of past winning products got the best results?

Apply these findings to the scoring in STEP 1:
- +2 bonus points if a product's category matches the best performing category
- +1 bonus point if a product's price is in the best performing price range

Apply to STEP 6:
- Assign the historically winning hook type to VARIANT A (the lead variant)
- If no history exists, keep the default order: A = Price Shock, B = Curiosity, C = Problem/Solution, D = TikTok Discovery

Show a one-line summary before proceeding:
> Historical insights: Best hook: [type] | Best category: [category] | Best price range: [range]
> (or: "No history yet — treating as day 1")

---

STEP 1 — FIND TRENDING PRODUCTS

Search for 5 products trending on TikTok Israel right now.

Use ONLY these sources to find trends — do not invent or guess:
- TikTok Creative Center (trending products and ads)
- TikTok Search (search by category keywords)
- AliExpress Best Sellers
- AliExpress Trending Products
- Google Trends Israel

TREND VALIDATION RULE — MANDATORY:
A product is only valid if it appears in at least 2 of the above sources.
Do NOT shortlist any product that appears in only 1 source.

For each of the 5 products, show:
- Source 1: [source name + specific evidence]
- Source 2: [source name + specific evidence]
- AliExpress demand proof: orders count, rating, reviews count
- TikTok content proof: videos found, comment themes, repeated appearances

If you cannot confirm a product in 2 sources, skip it and search for another.

Search FIRST inside the 9% commission categories (Mobile Phone Accessories, Interior Accessories, Garden Supplies, Children's Clothing, Women's Clothing, Men's Clothing).
If no strong trending product is found in 9% categories, search the 7% (Other Categories).
Only search 3% categories as a last resort, and note the lower commission in the final package.

SCORING — score each product on all criteria:

PRICE SCORE (Israeli impulse-buy market):
- Under 30₪ = 10 points + 3 bonus = 13 total
- 30–50₪ = 9 points + 2 bonus = 11 total
- 50–75₪ = 7 points
- 75–100₪ = 5 points
- Over 100₪ = 2 points

PRICE RULES:
- Preferred range: 20₪–50₪
- Acceptable range: 50₪–79₪
- Avoid products over 80₪ unless exceptional trend evidence AND strong problem/solution angle
- When comparing two similar products within 1 point of each other, always choose the cheaper one
- Goal: maximum conversions and impulse purchases — not maximum commission per sale

OTHER SCORING CRITERIA:
- Visual appeal (1–10): looks great in a 2-second video
- AliExpress availability (1–10): easy to find, many sellers, fast ship
- Safety (1–10): no fake brand logos, no copyright risk
- Israeli audience fit (1–10): practical, relatable, solves a real problem

BONUSES:
- Commission tier: 9% = +2, 7% = +1, 3% = -2
- Impulse-buy category (small home gadgets, mobile accessories, organization, pet, beauty, children's accessories) = +1
- Historical best category match (from STEP 0) = +2
- Historical best price range match (from STEP 0) = +1

PREFERRED PRODUCT TYPES (impulse-buy friendly):
- Small home gadgets
- Mobile accessories
- Organization products
- Pet accessories
- Beauty accessories
- Children's accessories

Pick the product with the highest total score automatically.
If two products are tied or within 1 point, pick the cheaper one.

---

STEP 2 — FIND BEST ALIEXPRESS LISTING

For the chosen product find the best listing:
- Over 1,000 sales
- Rating above 4.5 stars
- Good photos (at least 5 images)
- Ships to Israel
- Lowest price
- No fake brand logos

If no safe listing exists, pick the second-highest scored product and repeat.

---

STEP 3 — SAFETY CHECK

Confirm:
- No recognizable brand logo on the product
- No trademark names in the listing title
- Product is a generic item safe to promote

If it fails safety check, go back to Step 1 and pick next product.

---

STEP 4 — MANUAL AFFILIATE LINK STEP

Do NOT call any API. Do NOT generate an affiliate link automatically.

Provide:
- The standard AliExpress product URL (the regular product page URL)
- The product category
- The expected commission rate based on that category

The user will manually paste this URL into the AliExpress Link Generator to create their affiliate link.

Output a Comment CTA Strategy using the PRODUCT ID assigned for this run:

"כתבי [PRODUCT ID] בתגובות ואשלח לך את הקישור"
or
"שלחי הודעה עם [PRODUCT ID] ואשלח לך את הקישור"

This lets the user manage many products without confusion.

---

STEP 5 — FIND REVIEW VIDEOS

Search for existing videos of this product to use for screen recording.

Search on:
- TikTok (search the product name)
- YouTube Shorts
- AliExpress product page videos
- Amazon reviews

For each video found, check:
- No large watermark covering the product
- No fake brand logos visible
- Video looks natural and authentic
- Product is clearly visible

Show the top 3 best videos with:
- Link to the video
- Why it is good for screen recording
- Best moment to capture (e.g. "0:05–0:12 shows the product clearly")

---

STEP 6 — GENERATE 4 VIDEO VARIANTS

For the selected product, generate 4 video variants. Each variant has a unique hook, a full storyboard, and a caption. All text must be in Hebrew.

IMPORTANT: If historical data exists and there is a winning hook type (from STEP 0), assign that hook type to VARIANT A — the first and lead variant. Reorder the remaining variants accordingly. If no history, use the default order below.

---

VARIANT A — [Historically winning hook, or Price Shock if no history]
Default hook: "לא תאמיני כמה זה עולה בעלי אקספרס... 😱"
Angle: Lead with the price. Shock with the value.

VARIANT B — Curiosity Hook
Hook: "ראיתי את זה בטיקטוק ולא האמנתי שזה קיים..."
Angle: Tease the product without revealing it immediately.

VARIANT C — Problem/Solution Hook
Hook: "מצאתי את הפתרון לבעיה שכולנו מכירות 🔥"
Angle: Open with a pain point the product solves.

VARIANT D — TikTok Discovery Hook
Hook: "כולן מדברות על זה ואני סוף סוף הזמנתי..."
Angle: Social proof — others are already using or talking about it.

---

For EACH variant generate:

STORYBOARD:
| Seconds | What to record | Text on screen (Hebrew) | Color | Position |
|---------|---------------|------------------------|-------|----------|
| 0–2     | Best review video clip or first product photo | [variant hook] | White | Top center |
| 2–5     | Price photo or product close-up | "רק [price]₪ בעלי אקספרס" | Yellow | Center |
| 5–9     | Product in use / detail shots | "[main benefit in Hebrew]" | White | Center |
| 9–13    | Sales count or review snippet | "[number] אנשים כבר הזמינו!" | White | Center |
| 13–15   | First image again | "כתבי [PRODUCT ID] בתגובות 💬" | Red | Bottom |

CAPTION (one line):
"מצאתי [product name] בעלי אקספרס ב-[price]₪ ואני לא מאמינה שזה קיים 😱 כתבי [PRODUCT ID] בתגובות ואשלח לך את הקישור!"

HASHTAGS (same for all variants):
Always include: #מציאות #אליאקספרס #טיקטוקישראל
Add 5–7 hashtags specific to this product category.

---

STEP 7 — SAVE OUTPUT FILE

Save the complete package to:
C:\Automation\TikTok\output\[YYYY-MM-DD]-product-[PRODUCT_ID].md

Example filename: 2026-06-03-product-002.md

The file must contain:
- Product ID
- Product name and description
- Why chosen (one sentence)
- Trend evidence: Source 1 + Source 2 (with specifics)
- AliExpress product URL
- Category and commission rate
- Review video links (all 3, with timestamps)
- Variant A: hook type label + hook + full storyboard table + caption
- Variant B: hook type label + hook + full storyboard table + caption
- Variant C: hook type label + hook + full storyboard table + caption
- Variant D: hook type label + hook + full storyboard table + caption
- Hashtags

After saving, confirm: "✅ Package saved to output/[filename]"

---

STEP 8 — SHOW FINAL PACKAGE

Present everything in one clean block:

================================================
TODAY'S TIKTOK PACKAGE
================================================

PRODUCT ID: [e.g. 002]
PRODUCT: [name]
WHY CHOSEN: [one sentence — what makes it trend-worthy]
TREND SOURCES: [Source 1] + [Source 2]
ALIEXPRESS DEMAND: [orders] orders | [rating]★ | [reviews] reviews
TIKTOK PROOF: [videos found] videos found | [comment theme]

ALIEXPRESS PRODUCT URL: [standard product URL]
CATEGORY: [category name]
EXPECTED COMMISSION: [7% or 9% — based on category]
→ Paste into AliExpress Link Generator manually to create your affiliate link.

CTA:
"כתבי [PRODUCT ID] בתגובות ואשלח לך את הקישור"
or
"שלחי הודעה עם [PRODUCT ID] ואשלח לך את הקישור"

---

REVIEW VIDEOS TO SCREEN RECORD:
1. [link] — [why it's good] — Best moment: [timestamp]
2. [link] — [why it's good] — Best moment: [timestamp]
3. [link] — [why it's good] — Best moment: [timestamp]

Or record the AliExpress product page directly (scroll slowly, 2–3 sec per photo).

---

VIDEO VARIANT [PRODUCT ID]A — [Hook Type]
HOOK: [hook in Hebrew]
STORYBOARD: [full table]
CAPTION: [caption in Hebrew]

---

VIDEO VARIANT [PRODUCT ID]B — Curiosity
HOOK: [hook in Hebrew]
STORYBOARD: [full table]
CAPTION: [caption in Hebrew]

---

VIDEO VARIANT [PRODUCT ID]C — Problem/Solution
HOOK: [hook in Hebrew]
STORYBOARD: [full table]
CAPTION: [caption in Hebrew]

---

VIDEO VARIANT [PRODUCT ID]D — TikTok Discovery
HOOK: [hook in Hebrew]
STORYBOARD: [full table]
CAPTION: [caption in Hebrew]

---

HASHTAGS (use for all variants):
[hashtags from Step 6]

---

UPLOAD CHECKLIST:
[ ] Paste the AliExpress product URL into AliExpress Link Generator → copy your affiliate link
[ ] Record 4 versions — one per variant hook (or start with 2 and test)
[ ] Open TikTok → tap + → Upload → pick your recording
[ ] Add a trending sound (tap Sounds → Trending)
[ ] Add the storyboard texts at the right timestamps
[ ] Paste caption + hashtags in the description
[ ] Upload between 19:00–21:00 Israel time
[ ] Note which variant is which (002A, 002B...) so you can track in the evening

⚠️ After this run: update CURRENT_PRODUCT_ID in the prompt file to the next number.
⚠️ Package saved to: C:\Automation\TikTok\output\[filename]

================================================
```

---

## Evening Agent Prompt — paste into `.claude/commands/tiktok-analyze.md`

```
You are a TikTok Performance Analyzer for the Israeli market.

Ask the user to paste their stats for each video variant they uploaded.

Format to request (repeat for each variant):

PRODUCT VARIANT: [e.g. 002A]
Views:
Likes:
Comments:
Saves:

Also ask for (needed to save to CSV):
- Product category: [e.g. Mobile Phone Accessories]
- Product price in ₪: [e.g. 45]

After receiving all variant stats, analyze:

1. WINNING VARIANT
   - Compare all variants by views, saves, and comments.
   - Identify the single winning variant (e.g. 002B).
   - State clearly: Winner: [variant ID]

2. WINNING HOOK TYPE
   - A = Price Shock (or historically reassigned hook)
   - B = Curiosity
   - C = Problem/Solution
   - D = TikTok Discovery
   - Name the winning hook type and explain in one sentence why it likely worked for this product.

3. LOSING VARIANTS
   - List the losing variant IDs.
   - For each, give one specific reason it underperformed (low views = hook didn't stop scroll / low saves = product didn't feel valuable / etc.)

4. RECOMMENDATION FOR TOMORROW
   - Be specific. Reference exact variant IDs.
   - Example: "002B won with Curiosity hook. For tomorrow's product, lead with Curiosity as Variant A."

5. VERDICT

   ✅ WINNER: [variant ID] — [hook type] — [why it worked]
   ❌ LOSERS: [variant IDs] — [why]
   🔄 TOMORROW: [exact instruction for the /tiktok agent]

Do not give generic advice. Always reference exact PRODUCT VARIANT IDs (002A, 002B, etc.).

---

STEP A — SAVE TO video_results.csv

After analysis, append results to: C:\Automation\TikTok\data\video_results.csv

If the file does not exist, create it with this header first:
product_id,variant,hook_type,category,price_ils,views,likes,comments,saves,winner

Then append one row per variant submitted by the user:
[product_id],[variant_id],[hook_type],[category],[price_ils],[views],[likes],[comments],[saves],[true/false]

Hook type values to use (exact, for consistency):
- Price Shock
- Curiosity
- Problem/Solution
- TikTok Discovery

Winner column: true only for the single winning variant. All others: false.

Example rows:
002,002A,Price Shock,Mobile Phone Accessories,45,1200,89,34,67,false
002,002B,Curiosity,Mobile Phone Accessories,45,3400,234,89,145,true

After saving, confirm: "✅ Results saved to data/video_results.csv ([X] total rows now)"

---

STEP B — SAVE ANALYSIS FILE

Save the full analysis to:
C:\Automation\TikTok\analysis\[YYYY-MM-DD]-product-[PRODUCT_ID]-analysis.md

The file must contain:
- Product ID and date
- All variant stats submitted by the user (in a table)
- Winning variant and hook type — with explanation
- Losing variants — with reason per variant
- Recommendation for tomorrow (exact instruction)
- Full verdict block

After saving, confirm: "✅ Analysis saved to analysis/[filename]"

---

FINAL OUTPUT FORMAT:

Show the full analysis in chat, then close with:

---
📁 Files saved:
- data/video_results.csv — updated ([X] total rows)
- analysis/[YYYY-MM-DD]-product-[PRODUCT_ID]-analysis.md — created
```

---

## Your Daily Routine

```
MORNING (~15 minutes):
  1. Open Claude Code
  2. Type /tiktok
  3. Wait 2–3 minutes for the agent to finish
  4. Read the package in chat (also saved to output\ folder)
  5. Paste the AliExpress product URL into AliExpress Link Generator → copy affiliate link
  6. Screen record the review video OR scroll through AliExpress photos (1–2 min)
  7. Paste all texts into TikTok (5 min)
  8. Schedule upload for 19:00–21:00

EVENING (~5 minutes):
  1. Open TikTok analytics
  2. Copy your stats (views, likes, comments, saves, clicks)
  3. Open Claude Code
  4. Type /tiktok analyze
  5. Paste your stats + product category + price
  6. Read what to do tomorrow
  7. Check analysis\ folder the next morning to review any overnight output
```

---

## Week-by-Week Plan

### Week 1 — Setup and First Videos

| Day | Goal |
|-----|------|
| Day 1 | Create `C:\Automation\TikTok\` + subfolders. Create both slash commands. Do one test run. |
| Day 2 | First real `/tiktok` run. Record and upload your first video. |
| Day 3 | First `/tiktok analyze`. First rows written to video_results.csv. |
| Day 4–7 | One video per day. Agent starts accumulating history. |

### Week 2 — Learn What Works

- Agent reads video_results.csv each morning — patterns emerge after 5–7 data points
- You know which hook style works for your audience
- You know which product categories get engagement
- Price scoring is calibrated to Israeli impulse-buy behavior

### Week 3+ — Start Scaling

- Agent's recommendations are history-informed, not generic
- Consider 2 products per day if the 15-minute routine feels easy
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
- Do the evening analysis every day — this is how the agent learns
- Upload every day — consistency beats perfection

**Never:**
- Fake brand logos (ALO, Nike, etc.) → ban + legal risk
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
- [ ] At least 10 rows in video_results.csv showing a clear pattern
- [ ] The agent's analysis pointing clearly at a winning hook + category combo

Then duplicate the same system in English.

---

## The Secret

> It is not about finding a perfect product.  
> It is about finding the right ANGLE — and then running experiments fast.

The agent gives you one strong experiment every morning.  
The analyzer tells you each evening what to double down on.  
You record and upload. The system learns. Results compound.

---

*Created: 2026-05-27*  
*Updated: 2026-06-03 — Added output file structure (output\ + analysis\ + data\ folders under C:\Automation\TikTok\), persistent learning via video_results.csv, updated price scoring for Israeli impulse-buy market (preferred 20₪–50₪, bonuses for cheap products), trend validation rule (2+ sources required per product), history-informed hook ordering, and scoring bonuses for impulse-buy categories.*  
*Based on: sumery.txt, מוצרים טרנדיים בטיקטוק.txt, מוצרי טרנדים בטיקטוק 2.txt, פרסום_מוצר_יוגה_טיקטוק.md*
