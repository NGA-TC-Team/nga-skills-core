/**
 * scanSpacing
 *
 * Scans all Auto Layout frames across all pages to collect padding
 * and gap (itemSpacing) values. Skips values already bound to variables.
 * Returns unique values with frequency counts.
 *
 * @returns {Promise<{
 *   values: Array<{
 *     value: number,
 *     count: number,
 *     sources: { padding: number, gap: number }
 *   }>,
 *   totalAutoLayoutFrames: number
 * }>}
 */
async function scanSpacing() {
  const spacingMap = new Map(); // value → { count, sources }
  let totalAutoLayoutFrames = 0;

  function addValue(val, source) {
    if (val === 0 || val === undefined || val === null) return;
    val = Math.round(val); // normalize to integer
    if (!spacingMap.has(val)) {
      spacingMap.set(val, { value: val, count: 0, sources: { padding: 0, gap: 0 } });
    }
    const entry = spacingMap.get(val);
    entry.count++;
    entry.sources[source]++;
  }

  for (const page of figma.root.children) {
    await figma.setCurrentPageAsync(page);

    page.findAll(node => {
      if (!('layoutMode' in node) || node.layoutMode === 'NONE') return false;
      if (!node.visible) return false;
      totalAutoLayoutFrames++;

      // Padding values (skip if bound to variables)
      const bv = node.boundVariables || {};
      if (!bv.paddingTop) addValue(node.paddingTop, 'padding');
      if (!bv.paddingRight) addValue(node.paddingRight, 'padding');
      if (!bv.paddingBottom) addValue(node.paddingBottom, 'padding');
      if (!bv.paddingLeft) addValue(node.paddingLeft, 'padding');

      // Gap (itemSpacing)
      if (!bv.itemSpacing) addValue(node.itemSpacing, 'gap');

      return false;
    });
  }

  const values = [...spacingMap.values()].sort((a, b) => a.value - b.value);

  return { values, totalAutoLayoutFrames };
}
