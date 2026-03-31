# Extract Design Tokens from Figma File

Scan an existing Figma project file to discover all design tokens in use — colors, typography, spacing, border radii, and effects — then organize them into proper Variable Collections, Text Styles, and Effect Styles within the same file. **No codebase required.** Designed for designers who have projects but no formal design system yet.

**MANDATORY**: You MUST also load [figma-use](../figma-use/SKILL.md) before any `use_figma` call. That skill contains critical Plugin API rules (color ranges, font loading, page switching, etc.) that apply to every script you write.

**Always pass `skillNames: "figma-extract-tokens"` when calling `use_figma` as part of this skill.** This is a logging parameter — it does not affect execution.

---

## Skill Boundaries

| Use this skill | Switch to another skill |
|----------------|------------------------|
| Extract tokens from an existing Figma file | Build DS from codebase → [figma-generate-library](../figma-generate-library/SKILL.md) |
| Analyze colors/typography/spacing in a Figma file | Implement Figma design as code → [figma-implement-design](../figma-implement-design/SKILL.md) |
| Create variables/styles from extracted tokens | Build screens from DS components → [figma-generate-design](../figma-generate-design/SKILL.md) |
| | Create components/variants → [figma-use](../figma-use/SKILL.md) directly |

---

## Prerequisites

- Figma MCP server must be connected
- User must provide a Figma file URL (format: `https://figma.com/design/:fileKey/:fileName`)
- The file should contain design work with real content (not empty)

---

## Required Workflow

**Follow these steps in order. Do not skip steps.**

### Step 1: Inspect Existing File

Before scanning, understand what already exists. Run a read-only `use_figma` call:

```js
const result = {
  pages: [],
  existingCollections: [],
  existingTextStyles: [],
  existingEffectStyles: []
};

// Pages
for (const page of figma.root.children) {
  result.pages.push({ id: page.id, name: page.name, childCount: page.children.length });
}

// Existing variable collections
const collections = await figma.variables.getLocalVariableCollectionsAsync();
for (const c of collections) {
  result.existingCollections.push({
    name: c.name, id: c.id,
    variableCount: c.variableIds.length,
    modes: c.modes.map(m => m.name)
  });
}

// Existing styles
const ts = figma.getLocalTextStyles();
result.existingTextStyles = ts.map(s => ({ name: s.name, fontSize: s.fontSize }));
const es = figma.getLocalEffectStyles();
result.existingEffectStyles = es.map(s => ({ name: s.name, effectCount: s.effects.length }));

return result;
```

**If the file already has variable collections or styles**, inform the user and ask whether to:
- Skip those categories (preserve existing)
- Merge (add missing tokens only)
- Replace (overwrite with extracted tokens)

### Step 2: Scan — Collect Raw Values

Scan all pages to collect every design value in use. Run each scanner in a separate `use_figma` call to avoid script size limits. Use the helper scripts from the `scripts/` directory.

**Important scanning rules:**
- Skip nodes that are already bound to variables (`boundVariables` is set) — these are part of an existing system
- Track usage frequency for every value — more frequent = more important
- Return structured data, not just counts

#### 2a: Scan Colors

Embed [scanColors.js](scripts/scanColors.js). Collects all unique solid fill and stroke colors with frequency counts.

#### 2b: Scan Typography

Embed [scanTypography.js](scripts/scanTypography.js). Collects all unique font family + size + weight + lineHeight + letterSpacing combinations.

#### 2c: Scan Spacing

Embed [scanSpacing.js](scripts/scanSpacing.js). Collects all Auto Layout padding and gap values.

#### 2d: Scan Border Radius

Embed [scanBorderRadius.js](scripts/scanBorderRadius.js). Collects all cornerRadius values.

#### 2e: Scan Effects

Embed [scanEffects.js](scripts/scanEffects.js). Collects all drop shadows, inner shadows, blurs.

#### Present Summary

After all scans complete, present the raw findings to the user:

```
Scan complete. Found:
- Colors: {N} unique values (top 5: #FFFFFF ×234, #1A1A1A ×189, ...)
- Typography: {N} combinations (Inter 14/400 ×89, Inter 16/600 ×67, ...)
- Spacing: {N} values (8 ×156, 16 ×134, 24 ×98, ...)
- Border Radius: {N} values (8 ×201, 4 ×156, ...)
- Effects: {N} shadow/blur definitions
```

### Step 3: Analyze — Auto-Group and Name

Process the raw values into organized token groups.

#### Color Grouping

1. Convert all colors to HSL color space
2. Group by Hue (±15° tolerance) and Saturation (±20% tolerance)
3. Within each hue group, sort by Lightness → assign scale steps (50, 100, 200, ..., 900)
4. Achromatic colors (S < 5%) → `gray` group
5. Name hue groups by closest named color: red, orange, yellow, green, teal, blue, indigo, purple, pink
6. Suggest primary/secondary candidates based on usage frequency (excluding gray/black/white)

**Output example:**
```
Proposed color palette:
  gray:   50(#F9FAFB) 100(#F3F4F6) ... 900(#111827)
  blue:   50(#EFF6FF) 100(#DBEAFE) ... 900(#1E3A8A)
  green:  50(#F0FDF4) 100(#DCFCE7) ... 500(#22C55E)

  Suggested primary: blue (used 342 times)
  Suggested secondary: green (used 87 times)

  Standalone colors (not fitting any group):
  #FF6B35 (used 12 times) — suggest name?
```

#### Typography Grouping

1. Sort by fontSize ascending
2. Assign scale names based on relative size:
   - fontSize ≤ 12: `text/xs`
   - fontSize 13-14: `text/sm`
   - fontSize 15-16: `text/base`
   - fontSize 17-20: `text/lg`
   - fontSize 21-24: `text/xl`
   - fontSize 25-32: `heading/sm`
   - fontSize 33-40: `heading/md`
   - fontSize 41-48: `heading/lg`
   - fontSize 49+: `heading/xl`
3. If multiple weights exist for the same size, append weight: `text/base/regular`, `text/base/bold`

#### Spacing Grouping

1. Snap values to nearest 4px grid (if within 1px tolerance)
2. Assign t-shirt sizes: xs(4), sm(8), md(16), lg(24), xl(32), 2xl(48), 3xl(64)
3. Values not fitting the scale → keep as-is with numeric name: `spacing/6`, `spacing/10`

#### Border Radius Grouping

Assign names: none(0), sm(2-4), md(6-8), lg(10-16), xl(18-24), full(999+)

#### Effects Grouping

Group similar shadows by offset/radius proximity. Name: shadow/sm, shadow/md, shadow/lg.

### Step 4: User Checkpoint

Present the full organized token map and ask for approval:

```
Here's the proposed design token structure:

COLORS ({N} primitives → {M} semantic aliases)
  Collections: "Primitives" (1 mode), "Color" (1 mode: Default)
  Palette: gray(10 steps), blue(8 steps), green(5 steps)
  Semantic: bg/primary, bg/secondary, text/primary, text/secondary, border/default

TYPOGRAPHY ({N} text styles)
  text/xs (12/16 Inter Regular) ... heading/xl (48/56 Inter Bold)

SPACING ({N} values)
  xs(4) sm(8) md(16) lg(24) xl(32) 2xl(48)

BORDER RADIUS ({N} values)
  none(0) sm(4) md(8) lg(12) full(999)

EFFECTS ({N} styles)
  shadow/sm, shadow/md, shadow/lg

Shall I create these in the file?
```

**Wait for explicit approval before proceeding.**

### Step 5: Generate — Create Variables and Styles

After approval, create everything incrementally. Each category is a separate `use_figma` call.

#### 5a: Create "Design Tokens" Page

```js
// Find clear space on the first page, or create a new page
const page = figma.createPage();
page.name = "Design Tokens";
// Move to end
figma.root.appendChild(page);
await figma.setCurrentPageAsync(page);
return { pageId: page.id };
```

#### 5b: Create Primitives Collection

Create variable collection "Primitives" with mode "Value". Add all raw color values, spacing values, and radius values. Set scopes to `[]` (hidden from pickers — primitives are not used directly).

Use [createVariableCollection.js](../figma-generate-library/scripts/createVariableCollection.js) and [createSemanticTokens.js](../figma-generate-library/scripts/createSemanticTokens.js) from the generate-library skill as helpers.

#### 5c: Create Semantic Color Collection

Create variable collection "Color" with mode "Default". Create semantic aliases that reference Primitives:

```js
// Example: color/bg/primary → alias to Primitives/blue/500
variable.setValueForMode(modeId, {
  type: 'VARIABLE_ALIAS',
  id: primitivesMap['blue/500'].id
});
```

**Scope assignments:**
- `color/bg/*`: `["FRAME_FILL", "SHAPE_FILL"]`
- `color/text/*`: `["TEXT_FILL"]`
- `color/border/*`: `["STROKE_COLOR"]`
- `spacing/*`: `["GAP"]` (in Primitives collection)
- `radius/*`: `["CORNER_RADIUS"]` (in Primitives collection)

#### 5d: Create Text Styles

For each typography combination:

```js
await figma.loadFontAsync({ family: "Inter", style: "Regular" });
const style = figma.createTextStyle();
style.name = "text/base";
style.fontSize = 16;
style.fontName = { family: "Inter", style: "Regular" };
style.lineHeight = { value: 24, unit: "PIXELS" };
```

#### 5e: Create Effect Styles

For each shadow/blur group:

```js
const style = figma.createEffectStyle();
style.name = "shadow/md";
style.effects = [{
  type: "DROP_SHADOW",
  color: { r: 0, g: 0, b: 0, a: 0.1 },
  offset: { x: 0, y: 4 },
  radius: 6,
  spread: -1,
  visible: true,
  blendMode: "NORMAL"
}];
```

#### 5f: Create Visual Swatches

Embed [createSwatches.js](scripts/createSwatches.js) to build visual documentation on the Design Tokens page:

- **Color palette grid**: Rows per hue group, columns per lightness step. Each cell is a rectangle filled with the color variable + label below.
- **Typography specimens**: Each text style applied to a sample sentence with size/weight annotation.
- **Spacing scale**: Horizontal bars of increasing width representing each spacing value.
- **Radius preview**: Rounded rectangles showing each radius value.

### Step 6: Validate

1. Call `get_screenshot` on the "Design Tokens" page to verify visual output
2. Check for:
   - All swatches visible and readable
   - No overlapping elements
   - Color labels matching actual fills
   - Typography samples rendering correctly (fonts loaded)
3. Fix any issues with targeted `use_figma` calls

Present the final screenshot to the user for sign-off.

---

## Scanning Rules

### What to Skip

- Nodes with `visible === false` — hidden layers are often deprecated
- Nodes inside components marked as `_` prefix (private components)
- Colors that are already bound to variables (`node.boundVariables.fills` exists)
- Pure black (#000000) and pure white (#FFFFFF) with opacity 1 — track but don't auto-include in palette (ask user)
- Image fills (`type === 'IMAGE'`) — not extractable as tokens

### What to Include

- All visible SOLID fills and strokes
- All Text node typography properties
- All Auto Layout padding and gap values
- All cornerRadius values on frames and rectangles
- All effect arrays (shadows, blurs)

### Frequency Threshold

After scanning, apply a minimum frequency threshold:
- Colors used fewer than 2 times → flag as "one-off" and exclude by default
- Spacing/radius values used fewer than 3 times → flag as "one-off"
- User can override and include any flagged values

---

## Color Grouping Algorithm

### HSL Distance Function

Two colors are in the same hue group if:
```
|hue1 - hue2| ≤ 15° (or |hue1 - hue2| ≥ 345° for wrap-around)
AND |saturation1 - saturation2| ≤ 20%
```

### Scale Step Assignment

Within a hue group, sort by lightness (L) descending and assign:

| Lightness Range | Scale Step |
|----------------|------------|
| 95-100% | 50 |
| 88-94% | 100 |
| 78-87% | 200 |
| 65-77% | 300 |
| 50-64% | 400 |
| 38-49% | 500 |
| 28-37% | 600 |
| 18-27% | 700 |
| 10-17% | 800 |
| 0-9% | 900 |

If multiple colors fall in the same step, keep the one with higher usage frequency and flag the other as a "near-duplicate" for user review.

### Hue-to-Name Mapping

| Hue Range | Name |
|-----------|------|
| 0-15° | red |
| 16-45° | orange |
| 46-65° | yellow |
| 66-150° | green |
| 151-180° | teal |
| 181-240° | blue |
| 241-270° | indigo |
| 271-300° | purple |
| 301-345° | pink |
| 346-360° | red |

---

## Error Recovery

Follow the error recovery process from [figma-use](../figma-use/SKILL.md#6-error-recovery--self-correction):

1. **STOP** on error — do not retry immediately
2. **Read the error message** carefully
3. If unclear, call `get_metadata` or `get_screenshot` to inspect current state
4. **Fix the script** based on the error
5. **Retry** — safe because failed scripts are atomic (no partial changes)

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Font not loaded | Text style creation without `loadFontAsync` | Add `await figma.loadFontAsync(...)` before text operations |
| Variable name conflict | Extracted token name matches existing variable | Check existing variables first, skip or rename |
| Too many variables | Free plan limit (< 4 modes, limited variables) | Reduce scope, create Primitives only |

---

## Incremental Execution Strategy

Every operation is a separate `use_figma` call. Never combine scan + create in one call.

```
Call 1:  inspectFileStructure (read-only)
Call 2:  scanColors (read-only)
Call 3:  scanTypography (read-only)
Call 4:  scanSpacing (read-only)
Call 5:  scanBorderRadius (read-only)
Call 6:  scanEffects (read-only)
         → Present analysis + User Checkpoint
Call 7:  Create "Design Tokens" page
Call 8:  Create Primitives collection + variables
Call 9:  Create Color semantic collection + aliases
Call 10: Create Text Styles
Call 11: Create Effect Styles
Call 12: Create visual swatches (color grid)
Call 13: Create visual swatches (typography + spacing + radius)
Call 14: get_screenshot → final validation
```

---

## Reference Docs

Load these from [figma-use](../figma-use/SKILL.md) references as needed:

| Doc | When to load |
|-----|-------------|
| [variable-patterns.md](../figma-use/references/variable-patterns.md) | Creating variables, collections, binding |
| [text-style-patterns.md](../figma-use/references/text-style-patterns.md) | Creating text styles |
| [effect-style-patterns.md](../figma-use/references/effect-style-patterns.md) | Creating effect styles |
| [gotchas.md](../figma-use/references/gotchas.md) | Before any `use_figma` call |
| [common-patterns.md](../figma-use/references/common-patterns.md) | Auto-layout, shapes, text creation |

---

## Scripts

Reusable helper functions. Embed in `use_figma` calls:

| Script | Purpose |
|--------|---------|
| [scanColors.js](scripts/scanColors.js) | Collect all unique solid colors with frequency |
| [scanTypography.js](scripts/scanTypography.js) | Collect all text style combinations with frequency |
| [scanSpacing.js](scripts/scanSpacing.js) | Collect all Auto Layout spacing values with frequency |
| [scanBorderRadius.js](scripts/scanBorderRadius.js) | Collect all border radius values with frequency |
| [scanEffects.js](scripts/scanEffects.js) | Collect all shadow/blur effect definitions |
| [createSwatches.js](scripts/createSwatches.js) | Build visual documentation frames |
