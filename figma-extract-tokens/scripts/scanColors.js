/**
 * scanColors
 *
 * Scans all visible nodes across all pages to collect unique solid fill
 * and stroke colors. Skips nodes that are already bound to variables.
 * Returns colors as hex strings with usage frequency counts.
 *
 * @returns {Promise<{
 *   colors: Array<{
 *     hex: string,
 *     r: number, g: number, b: number, a: number,
 *     h: number, s: number, l: number,
 *     count: number,
 *     sources: { fills: number, strokes: number }
 *   }>,
 *   totalNodes: number,
 *   skippedBound: number
 * }>}
 */
async function scanColors() {
  const colorMap = new Map(); // hex → { r, g, b, a, count, sources }
  let totalNodes = 0;
  let skippedBound = 0;

  function rgbToHex(r, g, b, a) {
    const toHex = (v) => Math.round(v * 255).toString(16).padStart(2, '0');
    const hex = `#${toHex(r)}${toHex(g)}${toHex(b)}`;
    return a < 1 ? `${hex}${toHex(a)}` : hex;
  }

  function rgbToHsl(r, g, b) {
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    const l = (max + min) / 2;
    if (max === min) return { h: 0, s: 0, l: Math.round(l * 100) };
    const d = max - min;
    const s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    let h;
    if (max === r) h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
    else if (max === g) h = ((b - r) / d + 2) / 6;
    else h = ((r - g) / d + 4) / 6;
    return { h: Math.round(h * 360), s: Math.round(s * 100), l: Math.round(l * 100) };
  }

  function addColor(r, g, b, a, source) {
    const hex = rgbToHex(r, g, b, a);
    if (!colorMap.has(hex)) {
      const hsl = rgbToHsl(r, g, b);
      colorMap.set(hex, {
        hex, r, g, b, a,
        h: hsl.h, s: hsl.s, l: hsl.l,
        count: 0,
        sources: { fills: 0, strokes: 0 }
      });
    }
    const entry = colorMap.get(hex);
    entry.count++;
    entry.sources[source]++;
  }

  for (const page of figma.root.children) {
    await figma.setCurrentPageAsync(page);

    page.findAll(node => {
      totalNodes++;

      // Scan fills
      if ('fills' in node && Array.isArray(node.fills)) {
        for (let i = 0; i < node.fills.length; i++) {
          const fill = node.fills[i];
          if (fill.type !== 'SOLID' || !fill.visible) continue;
          // Skip if bound to variable
          if (node.boundVariables?.fills?.[i]?.id) {
            skippedBound++;
            continue;
          }
          const a = fill.opacity !== undefined ? fill.opacity : 1;
          addColor(fill.color.r, fill.color.g, fill.color.b, a, 'fills');
        }
      }

      // Scan strokes
      if ('strokes' in node && Array.isArray(node.strokes)) {
        for (let i = 0; i < node.strokes.length; i++) {
          const stroke = node.strokes[i];
          if (stroke.type !== 'SOLID' || !stroke.visible) continue;
          if (node.boundVariables?.strokes?.[i]?.id) {
            skippedBound++;
            continue;
          }
          const a = stroke.opacity !== undefined ? stroke.opacity : 1;
          addColor(stroke.color.r, stroke.color.g, stroke.color.b, a, 'strokes');
        }
      }

      return false; // findAll requires return
    });
  }

  // Sort by frequency descending
  const colors = [...colorMap.values()].sort((a, b) => b.count - a.count);

  return { colors, totalNodes, skippedBound };
}
