---
name: card-news-maker
description: "Thread/Instagram card news generator. Creates editorial-quality card news slides (1080×1350) with brand-aware color palettes, typography, and one-click image export. Uses theme.json for brand/neutral color grading, docs/news.md or user prompt for content, assets/ folder for user-provided images, and souls/ folder for brand voice, logo, and slide templates. Leverages ui-ux-pro-max skill for design system intelligence. Actions: create, design, export card news. Formats: Instagram post, Thread carousel."
---

# Card News Maker — Thread / Instagram Carousel Skill

Generate professional card news slides (1080×1350) for Instagram and Threads, powered by the `ui-ux-pro-max` design skill.

## When to Apply

This skill should be used when the task involves **creating card news, Instagram carousels, Threads posts, or slide-based visual content**.

### Must Use

- User asks to create card news / carousel / slide content
- User wants to generate Instagram or Threads visual posts
- User says "카드뉴스", "carousel", "card news", "슬라이드"

### Skip

- General web page design (use ui-ux-pro-max directly)
- Non-visual content creation
- Video or animation-only projects

---

## Prerequisites

This skill depends on:

- `ui-ux-pro-max` skill (for design system recommendations)
- Working directory already created by the user (Claude Code assumes it is running inside the target folder)

---

## Workflow

### Step 0: Confirm Working Directory

The user has already created the card news project folder and launched Claude Code from within it. All files will be created in the current working directory (`./`).

### Step 0.5: Scaffold Missing Optional Folders

Before asking the user for any content or color inputs, scan the working directory for the presence of optional folders and files:

| Check Target      | Path               |
| ----------------- | ------------------ |
| Content document  | `docs/news.md`     |
| User assets       | `assets/`          |
| Brand identity    | `souls/`           |
| Brand voice guide | `souls/hearts.md`  |
| Brand logo        | `souls/logo.*`     |
| Slide templates   | `souls/templates/` |

#### If any optional folders/files are missing:

Present a summary of what's missing and offer to scaffold them:

```
현재 프로젝트 폴더를 확인했습니다.

✅ theme.json
❌ docs/news.md         — 카드뉴스 콘텐츠 (마크다운)
❌ assets/              — 슬라이드 이미지 에셋
❌ souls/hearts.md      — 브랜드 보이스 가이드 (말투, 표현, 가치관)
❌ souls/logo.png       — 브랜드 로고
❌ souls/templates/     — 슬라이드 레이아웃 템플릿

빠진 항목들의 기본 틀(폴더 + 샘플 파일)을 생성해드릴까요? (y/n)
```

#### If the user says yes (전체 생성):

Create all missing folders and starter files:

**`docs/news.md`** — Starter content template:

```markdown
# 카드뉴스 제목을 입력하세요

여기에 카드뉴스의 전체 주제나 소개 문구를 작성하세요.

## 슬라이드 2 제목

슬라이드 2의 내용을 작성하세요. 통계, 팁, 설명 등을 자유롭게 적어주세요.

## 슬라이드 3 제목

슬라이드 3의 내용을 작성하세요.

## 슬라이드 4 제목

슬라이드 4의 내용을 작성하세요.

## CTA

마지막 슬라이드에 들어갈 행동 유도 문구를 작성하세요.
```

**`souls/hearts.md`** — Starter voice guide:

```markdown
# Brand Voice

## Tone

- 여기에 원하는 말투/어조를 적어주세요
- 예: 친근한 ~해요 체, 전문적이지만 쉬운 설명

## Key Expressions

- 자주 사용할 표현을 적어주세요
- 예: "쉽게 말해서...", "핵심만 정리하면"

## Values

- 콘텐츠에서 중시하는 가치를 적어주세요
- 예: 실용성, 정확성, 포용

## Avoid

- 피해야 할 표현이나 스타일을 적어주세요
- 예: 과도한 과장, 딱딱한 격식체
```

**`assets/`** — Empty folder (with a `.gitkeep` or note):

```
assets/ 폴더를 생성했습니다.
슬라이드에 사용할 이미지를 여기에 넣어주세요.
- 커버 배경: cover.png, bg.png
- 콘텐츠 이미지: 1.png, 2.png... 또는 a.png, b.png... (순서대로 슬라이드에 매핑)
```

**`souls/templates/`** — Empty folder:

```
souls/templates/ 폴더를 생성했습니다.
슬라이드 템플릿(HTML 또는 이미지)을 여기에 넣어주세요.
- HTML: cover.html, content.html, cta.html 등 (플레이스홀더 토큰 사용)
- 이미지: cover.png, content.png 등 (풀블리드 배경으로 사용)
```

#### If the user says no:

Skip scaffolding and proceed to Step 1. Missing items will be handled by their respective fallback logic (ask user for colors, topic, etc.).

#### If the user wants partial scaffolding:

The user may say "docs랑 souls만 만들어줘" — in that case, create only the requested folders/files.

#### After scaffolding:

If starter files were created, inform the user:

```
기본 틀을 생성했습니다! 파일을 채워넣은 후 다시 실행하거나,
지금 바로 진행하려면 말씀해주세요 (빈 파일은 건너뛰고 직접 질문드립니다).
```

The user can either:

1. **Fill in the files** and re-run → Step 1 picks up the completed files
2. **Proceed immediately** → Empty/starter files are ignored, fallback to conversation-based input

### Step 1: Read or Create `theme.json`

Check if `theme.json` exists in the current working directory.

#### If `theme.json` exists:

Read the file and extract colors:

```json
{
  "brandColor": "#FF3D00",
  "neutralBaseColor": "#1A1A1A"
}
```

#### If `theme.json` does NOT exist:

Ask the user two questions:

1. **"브랜드 컬러(메인 컬러)를 알려주세요."** — Brand/primary color (hex value)
2. **"뉴트럴 컬러(배경/텍스트 기조 컬러)를 알려주세요."** — Neutral base color (hex value)

Then create `theme.json` with the user's answers.

### Step 2: Generate Color Grade Palettes

From the two base colors in `theme.json`, generate a **10-step color grade palette** for each:

#### Brand Color Palette

From `brandColor`, generate shades `50` through `950`:

| Token       | Method                          | Usage                       |
| ----------- | ------------------------------- | --------------------------- |
| `brand-50`  | Lightest tint (mix 95% white)   | Subtle backgrounds          |
| `brand-100` | Very light tint (mix 90% white) | Hover states, light fills   |
| `brand-200` | Light tint (mix 75% white)      | Borders, secondary elements |
| `brand-300` | Medium-light (mix 55% white)    | Icons, decorative           |
| `brand-400` | Medium (mix 30% white)          | Secondary buttons           |
| `brand-500` | **Base** = `brandColor` as-is   | Primary CTA, key accents    |
| `brand-600` | Medium-dark (mix 15% black)     | Hover on primary            |
| `brand-700` | Dark (mix 30% black)            | Active/pressed state        |
| `brand-800` | Very dark (mix 50% black)       | Dark mode accent            |
| `brand-900` | Darkest (mix 70% black)         | Dark mode backgrounds       |
| `brand-950` | Near-black (mix 85% black)      | Ultra-dark surfaces         |

#### Neutral Color Palette

From `neutralBaseColor`, generate the same `50–950` scale. Used for:

- Backgrounds (50–100)
- Borders & dividers (200–300)
- Secondary text (400–500)
- Body text (600–700)
- Headings (800–900)
- Pure dark surfaces (950)

#### Implementation

Generate these palettes as CSS custom properties inside the output `index.html`:

```css
:root {
  --brand-50: #...;
  --brand-100: #...;
  /* ... through 950 */
  --neutral-50: #...;
  --neutral-100: #...;
  /* ... through 950 */
}
```

The palette generation logic should use **HSL manipulation**:

1. Convert the base hex to HSL
2. For lighter shades: increase lightness, slightly decrease saturation
3. For darker shades: decrease lightness, slightly increase saturation
4. Clamp all values to valid ranges

### Step 3: Load `souls/` — Brand Voice & Templates (Optional)

Check if the `souls/` folder exists. This folder provides **brand personality, logo, and reusable slide templates**. It is entirely optional — if it does not exist, skip this step and proceed normally.

#### 3-A: `souls/hearts.md` — Brand Voice Guide

If `souls/hearts.md` exists, read it and apply its directives to **all generated text content**.

**Expected `hearts.md` format:**

```markdown
# Brand Voice

## Tone

- 친근하고 유머러스한 말투 (casual, witty)
- ~해요 체 사용
- 전문 용어는 쉽게 풀어서 설명

## Key Expressions

- "쉽게 말해서..."
- "이거 모르면 손해예요"
- "딱 3분이면 됩니다"

## Values

- 실용성 우선: 이론보다 바로 쓸 수 있는 팁
- 포용: 초보자도 이해할 수 있는 난이도
- 솔직함: 과장 없이 사실 기반

## Avoid

- 딱딱한 격식체
- 과도한 영어 남용
- 근거 없는 과장 ("혁신적인", "게임 체인저")
```

**Parsing rules:**

- `## Tone` → 전체 슬라이드 텍스트의 말투/어조 결정
- `## Key Expressions` → 콘텐츠 작성 시 이 표현들을 자연스럽게 활용
- `## Values` → 콘텐츠 방향성과 우선순위 가이드
- `## Avoid` → 이 항목에 해당하는 표현/스타일 금지

**적용 방식:**

- `docs/news.md`가 있을 때: 원본 내용의 팩트는 유지하되, `hearts.md`의 톤/표현에 맞게 **표현을 다듬어** 슬라이드에 반영
- `docs/news.md`가 없을 때 (유저 프롬프트 기반): 콘텐츠를 **처음부터 hearts.md의 보이스로 생성**
- 커버 타이틀, CTA 문구에도 보이스 가이드 반영

#### 3-B: `souls/logo.png` (or `logo.svg`) — Brand Logo

If a logo file exists (`souls/logo.png`, `souls/logo.svg`, `souls/logo.jpg`), apply it to slides:

| Slide   | Logo Placement                                      |
| ------- | --------------------------------------------------- |
| Cover   | Top-left or top area, paired with brand tag         |
| CTA     | Top-left or bottom area, reinforces brand identity  |
| Content | Not placed (keeps slides clean and content-focused) |

**Logo CSS rules:**

```css
.slide-logo {
  height: 40px; /* constrain by height, auto width */
  width: auto;
  object-fit: contain;
  display: block;
}
```

**Logo reference in HTML:**

```html
<img src="souls/logo.png" alt="Brand logo" class="slide-logo" />
```

- If no logo file exists, use text-based brand tag (same as current behavior)
- Logo should never be distorted — always use `object-fit: contain`
- Maintain clear space around the logo (minimum 16px padding from edges)

#### 3-C: `souls/templates/` — Slide Templates

If `souls/templates/` exists, it can contain two types of template files:

1. **HTML templates** (`.html`) — Dynamic layouts with placeholder tokens for content injection
2. **Image templates** (`.png`, `.jpg`, `.jpeg`, `.webp`, `.svg`) — Static background/frame images used as-is

**Expected template structure:**

```
souls/templates/
├── cover.html          # HTML: Cover slide layout with placeholders
├── cover.png           # Image: Cover slide background/frame
├── content.html        # HTML: Default content slide layout
├── content.png         # Image: Content slide background/frame
├── stats.html          # HTML: Statistics/numbers slide layout
├── tips.html           # HTML: Tips/list slide layout
├── quote.png           # Image: Quote slide background/frame
├── cta.html            # HTML: CTA/ending slide layout
└── ...                 # Additional custom templates
```

#### HTML Templates (`.html`)

Each HTML template is a standalone snippet representing one slide's inner structure. It uses **placeholder tokens** that get replaced with actual content:

```html
<!-- souls/templates/cover.html -->
<div class="slide cover-slide">
  <div class="cover-top">
    {{LOGO}}
    <span class="cover-tag">{{BRAND_TAG}}</span>
  </div>
  <div class="cover-hero">
    <h1 class="cover-title">{{TITLE}}</h1>
    <div class="cover-line"></div>
    <p class="cover-subtitle">{{SUBTITLE}}</p>
  </div>
  <div class="cover-bottom">
    <span class="cover-issue">{{ISSUE}}</span>
    <span class="slide-num">{{SLIDE_NUM}}</span>
  </div>
</div>
```

**Available placeholder tokens:**

| Token           | Replaced With                                  |
| --------------- | ---------------------------------------------- |
| `{{LOGO}}`      | `<img>` tag with logo from `souls/`, or empty  |
| `{{BRAND_TAG}}` | Brand name or tag text                         |
| `{{TITLE}}`     | Slide title (from `docs/news.md` or generated) |
| `{{SUBTITLE}}`  | Slide subtitle/description                     |
| `{{BODY}}`      | Main body content text                         |
| `{{ITEMS}}`     | Repeated list items (tips, features, stats)    |
| `{{IMAGE}}`     | `<img>` tag from `assets/`, or empty           |
| `{{SLIDE_NUM}}` | Formatted slide number (e.g., "01 / 07")       |
| `{{ISSUE}}`     | Issue date/number string                       |
| `{{COVER_BG}}`  | Cover background image `<img>` or empty        |

#### Image Templates (`.png`, `.jpg`, `.svg`, etc.)

Image templates are **static visual frames** — pre-designed slide backgrounds or decorative frames created externally (e.g., Figma, Photoshop, Canva).

**How image templates work:**

1. The image is placed as the **full-bleed background** of the slide (1080×1350)
2. Text content is **overlaid on top** of the image
3. A text-safe zone is used to avoid placing text over critical visual areas

**Image template CSS:**

```css
.slide-template-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 0;
}

.slide-template-content {
  position: relative;
  z-index: 1;
  padding: 80px; /* default safe zone */
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
```

**Image reference in HTML:**

```html
<div class="slide">
  <img src="souls/templates/cover.png" alt="" class="slide-template-bg" />
  <div class="slide-template-content">
    <!-- Text content overlaid here -->
    <h1>{{TITLE}}</h1>
    <p>{{SUBTITLE}}</p>
  </div>
</div>
```

**Text readability on image templates:**

- If the image template is **dark** (detected or assumed): use light text (`--neutral-50`)
- If the image template is **light**: use dark text (`--neutral-900`)
- If readability is uncertain: apply a semi-transparent overlay between the image and text:

```css
.slide-template-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.35); /* or rgba(255,255,255,0.4) for light */
  z-index: 0;
}
```

#### When Both HTML and Image Exist for Same Type

If both `cover.html` and `cover.png` exist for the same slide type:

| Priority | Format | Behavior                                           |
| -------- | ------ | -------------------------------------------------- |
| 1st      | HTML   | HTML template takes priority (more flexible)       |
| 2nd      | Image  | Used only if no HTML template exists for this type |

#### Template Matching Rules

1. For each slide, determine its **type** (cover, content, stats, tips, quote, cta)
2. Check if a matching template exists in `souls/templates/`
3. Check in order: `.html` first, then image formats (`.png`, `.jpg`, `.svg`)
4. If HTML found → use the template, replace tokens with actual data
5. If image found → use as background, overlay text content on top
6. If nothing found → fall back to the default generated layout (current behavior)
7. HTML templates **inherit** the global CSS (palette, fonts, spacing) — they define structure only, not style overrides

**Template priority:**

```
Slide type has matching template in souls/templates/?
  ├─ YES → Use template, inject content via tokens
  └─ NO  → Generate layout using default skill logic
```

#### `souls/` Decision Flowchart

```
souls/ folder exists?
  ├─ YES
  │   ├─ hearts.md exists? → Read & apply voice guide to all text
  │   ├─ logo.png/svg exists? → Place on Cover + CTA slides
  │   └─ templates/ exists?
  │       ├─ Matching template for slide type? → Use template
  │       └─ No match? → Use default layout
  │
  └─ NO → Skip entirely. Use default voice, no logo, default layouts.
```

### Step 4: Determine Content & Slide Count

Content for the card news comes from one of two sources, checked in this order:

#### Source A: `docs/news.md` (File-based)

Check if `docs/news.md` exists. If it does, read it and use its content as the card news material.

**Expected `docs/news.md` format:**

```markdown
# Card News Title

Overall topic or headline for the card news.

## Slide 2 Title

Content for slide 2. Can include paragraphs, bullet points, statistics, etc.

## Slide 3 Title

Content for slide 3.

## Slide 4 Title

Content for slide 4.

<!-- Add more ## sections for more slides -->
```

**Parsing rules:**

- `# H1` → Cover slide title (Slide 1)
- The paragraph directly under `# H1` (before the first `## H2`) → Cover subtitle/description
- Each `## H2` → One content slide (Slide 2, 3, 4, ...)
- The last `## H2` section can optionally be tagged `## CTA` or `## Ending` to be treated as the final CTA slide
- If no explicit CTA slide exists, auto-generate one based on the overall topic
- **Slide count** = 1 (cover) + number of `## H2` sections + 1 (CTA if not already included)
- Supported inline formats: `**bold**`, `*italic*`, `> blockquote` (for pull quotes), `- list items` (for tip lists)

**When `souls/hearts.md` is also present:**

- Keep the factual content from `docs/news.md` intact
- Adjust **tone, expressions, and wording** to match the voice guide
- Example: if `news.md` says "Claude Code는 터미널 기반 AI 코딩 도구입니다" and `hearts.md` specifies casual tone → output becomes "쉽게 말해서, 터미널에서 바로 쓸 수 있는 AI 코딩 도구예요"

#### Source B: User Prompt (Conversation-based)

If `docs/news.md` does NOT exist, ask the user:

1. **"어떤 주제로 카드뉴스를 만들까요?"** — Topic/subject
2. **"슬라이드는 몇 장으로 구성할까요? (기본: 5장, 3~10장)"** — Slide count (default: 5, range: 3–10)
3. **"톤을 선택해주세요: professional / casual / playful / editorial (기본: editorial)"** — Tone (if `hearts.md` exists, this question is skipped — voice guide takes priority)

Then generate the slide content based on the user's answers (+ `hearts.md` voice if available).

#### Content Decision Flowchart

```
docs/news.md exists?
  ├─ YES → Read & parse. Slide count = parsed sections.
  │         hearts.md exists? → Adjust tone/expressions.
  │         Ask: "docs/news.md를 읽었습니다. {N}장 슬라이드로 제작합니다. 진행할까요?"
  │
  └─ NO  → hearts.md exists? → Skip tone question (use voice guide).
            Ask user for topic, slide count, (tone if no hearts.md).
            Generate content from user's answers + voice guide.
```

### Step 5: Scan `assets/` for User-Provided Images

Check if the `assets/` folder exists and contains image files.

#### Asset Discovery Rules

1. Scan `assets/` for image files (`*.png`, `*.jpg`, `*.jpeg`, `*.webp`, `*.svg`)
2. Sort files **alphanumerically** by filename (so `1.png` < `2.png` < `10.png`, or `a.png` < `b.png` < `c.png`)
3. Separate **cover background** images from **content** images (see naming convention below)

#### Cover Background Image

A special asset can be designated as the **cover slide's background image** using a naming convention:

| Filename Pattern               | Behavior                                 |
| ------------------------------ | ---------------------------------------- |
| `cover.png`, `cover.jpg`, etc. | Used as Cover (Slide 1) background image |
| `bg.png`, `bg.jpg`, etc.       | Used as Cover (Slide 1) background image |
| `cover-bg.png`, `cover-bg.jpg` | Used as Cover (Slide 1) background image |

- Only **one** cover background image is used (first match wins in the order above)
- The image is placed as a **full-bleed background** with a dimmed overlay to ensure text readability:

```css
.cover-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 0;
}

.cover-bg-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.3) 0%,
    rgba(0, 0, 0, 0.7) 100%
  );
  z-index: 1;
}

.cover-content {
  position: relative;
  z-index: 2;
}
```

- If no cover background image exists, the cover uses the default solid-color/typography-only design
- Cover background images are **excluded** from the sequential content mapping

#### Content Image Mapping

All remaining images (not matching cover patterns) are mapped to content slides:

| Asset (sorted) | Target Slide | Notes                                                  |
| -------------- | ------------ | ------------------------------------------------------ |
| 1st image file | Slide 2      | First content slide after cover                        |
| 2nd image file | Slide 3      | Second content slide                                   |
| 3rd image file | Slide 4      | Third content slide                                    |
| ...            | ...          | Continues sequentially                                 |
| Nth image file | Slide N+1    | If more images than content slides, extras are ignored |

- **Last Slide (CTA)**: Does not receive an asset image — CTA uses typography-only design
- If there are **fewer images** than content slides, remaining slides render without images (text-only layout)
- If there are **more images** than content slides, extra images are ignored with a warning message

#### Image Placement in Slides

When an image is assigned to a slide, it can be placed in one of these layout modes (choose based on content length):

| Layout Mode        | Image Size                 | Text Position    | Best When                      |
| ------------------ | -------------------------- | ---------------- | ------------------------------ |
| `hero-image`       | Full width, 60% height     | Below image, 40% | Short text, impactful visual   |
| `split-horizontal` | Left 50%, full height      | Right 50%        | Medium text + image            |
| `background-cover` | Full slide, dimmed overlay | Centered on top  | Minimal text, strong visual    |
| `top-caption`      | Full width, 50% height     | Above image, 50% | Title-heavy + supporting image |

Default layout mode: `hero-image`

**Image CSS rules:**

```css
.slide-image {
  width: 100%;
  height: auto;
  object-fit: cover;
  display: block;
}
```

**Image reference in HTML:**

```html
<img src="assets/1.png" alt="Slide visual" class="slide-image" />
```

#### No `assets/` Folder

If `assets/` does not exist or is empty, all slides use **text-only layouts**. No error or warning needed.

### Step 6: Consult ui-ux-pro-max for Design Direction

Run the design system search to get style, typography, and layout recommendations:

```bash
python3 ~/.agents/skills/ui-ux-pro-max/scripts/search.py "<topic> <tone> editorial card" --design-system -p "Card News"
```

Apply the returned recommendations for:

- Typography pairing (Google Fonts)
- Layout style (editorial grid, bold typography, minimalism, etc.)
- Effects and spacing guidelines

### Step 7: Generate `index.html`

Create a single `index.html` file containing all slides. Follow these specifications:

#### Slide Specifications

| Property      | Value               |
| ------------- | ------------------- |
| Width         | 1080px              |
| Height        | 1350px              |
| Aspect Ratio  | 4:5 (Instagram std) |
| Border Radius | 0px (editorial)     |
| Overflow      | hidden              |

#### Slide Structure Template

Each card news should include these slide types (adjust based on content):

| Slide | Type    | Purpose                              | Image                              | Logo                |
| ----- | ------- | ------------------------------------ | ---------------------------------- | ------------------- |
| 1     | Cover   | Title + brand tag + visual hook      | Cover BG from `assets/` (optional) | Yes (from `souls/`) |
| 2–N-1 | Content | Key points, stats, tips, quotes      | Yes (from `assets/` if available)  | No                  |
| N     | CTA/End | Call to action, follow, share prompt | No (typography-only)               | Yes (from `souls/`) |

#### Required Design Rules

1. **Typography**: Import Google Fonts from ui-ux-pro-max recommendation. Use oversized headlines (80px+), readable body (22–28px).
2. **Colors**: Use ONLY the generated palette tokens (`--brand-*`, `--neutral-*`). No hardcoded hex values in component styles.
3. **Contrast**: Ensure 4.5:1 minimum contrast ratio for all text. When using cover background images, overlay must guarantee readability.
4. **No Emojis as Icons**: Use SVG or pure CSS shapes for decorative elements.
5. **Spacing**: Use 8px grid system for all padding/margins.
6. **Slide Numbers**: Each slide shows its position (e.g., "01 / 07").
7. **Images**: Reference assets via relative path (`assets/filename.ext`). Apply `object-fit: cover`. Add dim overlay for `background-cover` mode.
8. **Logo**: Reference via `souls/logo.png` (or `.svg`). Use `object-fit: contain`, height-constrained.
9. **Voice**: If `souls/hearts.md` exists, all generated text must follow its tone, expressions, and values.

#### Responsive Preview

Include a media query for preview on smaller screens:

```css
@media (max-width: 1200px) {
  .slide {
    transform-origin: top center;
    transform: scale(0.45);
    margin-bottom: calc(-1350px * 0.55);
  }
}
```

#### Export Button — "압축 다운로드"

At the bottom of the page (after all slides), render a fixed-position or inline download button.

**Button behavior:**

1. User clicks **"압축 다운로드"** button
2. A modal appears with:
   - **Format selection**: PNG (lossless, larger) / JPG (lossy, smaller)
   - **Quality slider** (JPG only): 0.7–1.0 (default 0.92)
   - **File name prefix** input (default: "card-news")
   - **"다운로드" (Download)** button
   - **"취소" (Cancel)** button
3. On download:
   - Each slide is captured at **1080×1350** using `html2canvas`
   - Files are named `{prefix}-01.png`, `{prefix}-02.png`, etc.
   - All files are bundled into a `.zip` using `JSZip`
   - The `.zip` is downloaded to the user's machine via `FileSaver.js` / Blob URL

**Required Libraries (loaded via CDN):**

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
```

**Export Script Template:**

```javascript
async function exportSlides(format, quality, prefix) {
  const slides = document.querySelectorAll(".slide");
  const zip = new JSZip();

  for (let i = 0; i < slides.length; i++) {
    const slide = slides[i];

    // Reset any preview scaling before capture
    const originalTransform = slide.style.transform;
    slide.style.transform = "none";

    const canvas = await html2canvas(slide, {
      width: 1080,
      height: 1350,
      scale: 1,
      useCORS: true,
      backgroundColor: null,
    });

    slide.style.transform = originalTransform;

    const num = String(i + 1).padStart(2, "0");
    const ext = format === "png" ? "png" : "jpg";
    const mimeType = format === "png" ? "image/png" : "image/jpeg";

    const blob = await new Promise((resolve) =>
      canvas.toBlob(resolve, mimeType, quality),
    );

    zip.file(`${prefix}-${num}.${ext}`, blob);
  }

  const zipBlob = await zip.generateAsync({ type: "blob" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(zipBlob);
  link.download = `${prefix}.zip`;
  link.click();
  URL.revokeObjectURL(link.href);
}
```

**Modal HTML Template:**

```html
<div id="export-modal" class="export-modal" style="display:none">
  <div class="export-modal-backdrop"></div>
  <div class="export-modal-content">
    <h3>슬라이드 이미지 다운로드</h3>

    <label>포맷 선택</label>
    <div class="export-format-group">
      <button class="format-btn active" data-format="png">PNG</button>
      <button class="format-btn" data-format="jpg">JPG</button>
    </div>

    <div class="quality-section" style="display:none">
      <label>JPG 품질</label>
      <input type="range" min="70" max="100" value="92" />
      <span>92%</span>
    </div>

    <label>파일명 접두사</label>
    <input type="text" value="card-news" />

    <div class="export-actions">
      <button class="btn-cancel">취소</button>
      <button class="btn-download">다운로드</button>
    </div>
  </div>
</div>
```

**Modal Styling Rules:**

- Backdrop: `rgba(0,0,0,0.6)` with `backdrop-filter: blur(4px)`
- Content panel: Use `--neutral-50` background, `--neutral-900` text
- Buttons: Primary download button uses `--brand-500`, cancel uses `--neutral-200`
- Border radius: 0px (editorial consistency)
- Font: Same sans-serif from the card news design

---

## File Structure

The expected working directory structure:

```
./
├── theme.json              # Brand + neutral base colors (read or created)
├── docs/
│   └── news.md             # (Optional) Card news content in markdown
├── assets/                  # (Optional) User-provided images
│   ├── cover.png            #   (Optional) Cover slide background image
│   ├── 1.png (or a.png)    #   Mapped to Slide 2
│   ├── 2.png (or b.png)    #   Mapped to Slide 3
│   ├── 3.png (or c.png)    #   Mapped to Slide 4
│   └── ...                 #   Continues sequentially
├── souls/                   # (Optional) Brand identity & templates
│   ├── hearts.md            #   Brand voice: tone, expressions, values, avoids
│   ├── logo.png (or .svg)  #   Brand logo for Cover + CTA slides
│   └── templates/           #   (Optional) Slide templates (HTML or image)
│       ├── cover.html       #     HTML: Cover slide layout with placeholders
│       ├── cover.png        #     Image: Cover slide background/frame
│       ├── content.html     #     HTML: Default content slide layout
│       ├── content.png      #     Image: Content slide background/frame
│       ├── stats.html       #     HTML: Statistics slide layout
│       ├── quote.png        #     Image: Quote slide background/frame
│       └── cta.html         #     HTML: CTA/ending slide layout
└── index.html              # Generated: all slides + export functionality
```

---

## Input Sources Summary

| Source             | Location             | Required | Purpose                                                      |
| ------------------ | -------------------- | -------- | ------------------------------------------------------------ |
| `theme.json`       | `./theme.json`       | Yes\*    | Brand + neutral base colors (\*created if absent)            |
| `docs/news.md`     | `./docs/news.md`     | No       | Card news content in markdown                                |
| `assets/`          | `./assets/`          | No       | Slide images + cover background                              |
| `souls/hearts.md`  | `./souls/hearts.md`  | No       | Brand voice guide (tone, expressions, values)                |
| `souls/logo.png`   | `./souls/logo.*`     | No       | Brand logo for Cover + CTA                                   |
| `souls/templates/` | `./souls/templates/` | No       | Slide templates: HTML (dynamic) or image (static background) |
| User prompt        | Conversation         | Fallback | Topic, slide count, tone (if no news.md)                     |

## Content Source Priority

| Priority | Source         | Slide Count                    | Voice                                     |
| -------- | -------------- | ------------------------------ | ----------------------------------------- |
| 1st      | `docs/news.md` | Auto (parsed from ## headings) | `hearts.md` if exists, else editorial     |
| 2nd      | User prompt    | User chooses (default 5)       | `hearts.md` if exists, else user's choice |

## Asset Mapping Summary

| Condition                        | Behavior                                                  |
| -------------------------------- | --------------------------------------------------------- |
| `cover.png`/`bg.png` exists      | Used as Cover background with dimmed overlay              |
| `assets/` exists with images     | Map sequentially to Slide 2, 3, 4, ... (skip cover & CTA) |
| `assets/` exists but empty       | All slides use text-only layout                           |
| `assets/` does not exist         | All slides use text-only layout                           |
| More images than content slides  | Extra images ignored, show warning                        |
| Fewer images than content slides | Remaining content slides use text-only layout             |

## `souls/` Application Summary

| Component             | Effect When Present                                      | Effect When Absent        |
| --------------------- | -------------------------------------------------------- | ------------------------- |
| `hearts.md`           | All text follows its tone/expressions/values             | Default editorial tone    |
| `logo.png` / `.svg`   | Logo placed on Cover + CTA slides                        | Text-based brand tag only |
| `templates/*.html`    | Slide uses HTML layout, tokens replaced with content     | Default generated layout  |
| `templates/*.png/jpg` | Slide uses image as full-bleed background, text overlaid | Default generated layout  |
| HTML + Image both     | HTML takes priority; image used only if no HTML match    | Default generated layout  |

---

## Design Guidelines Summary

| Principle      | Rule                                                    |
| -------------- | ------------------------------------------------------- |
| Slide size     | 1080 × 1350px (4:5 Instagram)                           |
| Typography     | Oversized headlines, editorial serif + tight sans-serif |
| Colors         | Generated 10-step palette from theme.json only          |
| Icons          | SVG or CSS only — no emojis                             |
| Contrast       | WCAG AA minimum (4.5:1 text, 3:1 large text)            |
| Spacing        | 8px grid system                                         |
| Border radius  | 0px (editorial style default)                           |
| Image handling | `object-fit: cover`, relative path from `assets/`       |
| Cover BG       | Full-bleed with gradient overlay for text readability   |
| Logo           | `object-fit: contain`, height-constrained (40px)        |
| Voice          | `souls/hearts.md` overrides default tone                |
| Templates      | `souls/templates/` overrides default slide layouts      |
| Export         | html2canvas → JSZip → .zip download                     |
| Font loading   | Google Fonts with `display=swap`                        |

---

## Example Prompts

These are example user prompts this skill should handle:

- "카드뉴스 만들어줘" → checks `docs/news.md` first, if absent asks topic/count/tone
- "Claude Code에 대한 카드뉴스 5장 만들어줘" → topic: Claude Code, count: 5
- "Create a 7-slide card news about React hooks" → topic: React hooks, count: 7
- "인스타 카드뉴스 만들어줘, 주제는 AI 트렌드" → topic: AI trends
- "Thread 게시용 카드뉴스 8장 — 디자인 시스템 소개" → topic: design system, count: 8
- "docs/news.md에 내용 넣어뒀어, 카드뉴스 만들어줘" → read from file
- "souls 폴더 세팅해뒀어, 그에 맞춰 만들어줘" → apply voice + logo + templates

---

## Checklist Before Delivery

### Required

- [ ] `theme.json` exists and colors are valid hex
- [ ] All 10-step brand and neutral palettes generated as CSS variables
- [ ] Content sourced from `docs/news.md` or user prompt
- [ ] Slide count matches content sections (or user's request)
- [ ] All slides render at exactly 1080×1350px
- [ ] No emojis used as icons (SVG/CSS only)
- [ ] Text contrast meets 4.5:1 minimum
- [ ] "압축 다운로드" button is visible and functional
- [ ] Export modal shows format selection (PNG/JPG)
- [ ] Download produces correctly named zip with all slides
- [ ] Google Fonts loaded with `display=swap`
- [ ] Preview scales properly on smaller screens

### If `assets/` present

- [ ] Cover BG image (if named `cover.*`/`bg.*`) applied with dimmed overlay
- [ ] Content images correctly mapped to slides sequentially
- [ ] Images use `object-fit: cover` and relative paths
- [ ] Cover BG images excluded from content slide mapping

### If `souls/` present

- [ ] `hearts.md` voice guide applied to all generated text
- [ ] Tone, expressions, values, and avoids all reflected in content
- [ ] Logo placed on Cover + CTA with `object-fit: contain`
- [ ] Logo has minimum 16px clear space from slide edges
- [ ] Templates (if any) correctly matched to slide types (HTML first, then image)
- [ ] HTML template tokens (`{{TITLE}}`, `{{BODY}}`, etc.) all replaced
- [ ] Image templates rendered as full-bleed background with text overlay
- [ ] Text readability ensured on image templates (overlay applied if needed)
- [ ] Slides without matching templates fall back to default layout
