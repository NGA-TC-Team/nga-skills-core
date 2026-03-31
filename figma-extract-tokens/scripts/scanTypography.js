/**
 * scanTypography
 *
 * Scans all visible TEXT nodes across all pages to collect unique
 * typography combinations (fontFamily, fontSize, fontWeight/style,
 * lineHeight, letterSpacing). Returns combinations with frequency.
 *
 * @returns {Promise<{
 *   styles: Array<{
 *     fontFamily: string,
 *     fontStyle: string,
 *     fontSize: number,
 *     lineHeight: { value: number, unit: string } | null,
 *     letterSpacing: { value: number, unit: string } | null,
 *     count: number,
 *     key: string
 *   }>,
 *   totalTextNodes: number
 * }>}
 */
async function scanTypography() {
  const styleMap = new Map(); // key → { ...props, count }
  let totalTextNodes = 0;

  function lineHeightToObj(lh) {
    if (!lh || lh === figma.mixed) return null;
    if (lh.unit === 'AUTO') return null;
    return { value: lh.value, unit: lh.unit };
  }

  function letterSpacingToObj(ls) {
    if (!ls || ls === figma.mixed) return null;
    if (ls.value === 0) return null;
    return { value: ls.value, unit: ls.unit };
  }

  for (const page of figma.root.children) {
    await figma.setCurrentPageAsync(page);

    const textNodes = page.findAllWithCriteria({ types: ['TEXT'] });

    for (const node of textNodes) {
      if (!node.visible) continue;
      totalTextNodes++;

      // Skip mixed fonts (multiple styles in one text node)
      if (node.fontName === figma.mixed || node.fontSize === figma.mixed) continue;

      const fontFamily = node.fontName.family;
      const fontStyle = node.fontName.style;
      const fontSize = node.fontSize;
      const lineHeight = lineHeightToObj(node.lineHeight);
      const letterSpacing = letterSpacingToObj(node.letterSpacing);

      const key = `${fontFamily}|${fontStyle}|${fontSize}|${JSON.stringify(lineHeight)}|${JSON.stringify(letterSpacing)}`;

      if (!styleMap.has(key)) {
        styleMap.set(key, {
          fontFamily,
          fontStyle,
          fontSize,
          lineHeight,
          letterSpacing,
          count: 0,
          key
        });
      }
      styleMap.get(key).count++;
    }
  }

  const styles = [...styleMap.values()].sort((a, b) => a.fontSize - b.fontSize);

  return { styles, totalTextNodes };
}
