/**
 * scanBorderRadius
 *
 * Scans all frames, rectangles, and components across all pages
 * to collect cornerRadius values. Skips values already bound to variables.
 * Returns unique values with frequency counts.
 *
 * @returns {Promise<{
 *   values: Array<{
 *     value: number,
 *     count: number
 *   }>,
 *   totalNodesWithRadius: number
 * }>}
 */
async function scanBorderRadius() {
  const radiusMap = new Map(); // value → count
  let totalNodesWithRadius = 0;

  for (const page of figma.root.children) {
    await figma.setCurrentPageAsync(page);

    page.findAll(node => {
      if (!node.visible) return false;
      if (!('cornerRadius' in node)) return false;

      // Skip if bound to variable
      if (node.boundVariables?.topLeftRadius || node.boundVariables?.cornerRadius) return false;

      const cr = node.cornerRadius;
      if (cr === figma.mixed) {
        // Individual corners
        for (const prop of ['topLeftRadius', 'topRightRadius', 'bottomLeftRadius', 'bottomRightRadius']) {
          const val = node[prop];
          if (val !== undefined && val > 0) {
            totalNodesWithRadius++;
            const rounded = Math.round(val);
            radiusMap.set(rounded, (radiusMap.get(rounded) || 0) + 1);
          }
        }
      } else if (cr !== undefined && cr > 0) {
        totalNodesWithRadius++;
        const rounded = Math.round(cr);
        radiusMap.set(rounded, (radiusMap.get(rounded) || 0) + 1);
      }

      return false;
    });
  }

  const values = [...radiusMap.entries()]
    .map(([value, count]) => ({ value, count }))
    .sort((a, b) => a.value - b.value);

  return { values, totalNodesWithRadius };
}
