/**
 * scanEffects
 *
 * Scans all visible nodes across all pages to collect unique effect
 * definitions (DROP_SHADOW, INNER_SHADOW, LAYER_BLUR, BACKGROUND_BLUR).
 * Skips nodes that already have an effectStyleId assigned.
 * Returns unique effects with frequency counts.
 *
 * @returns {Promise<{
 *   effects: Array<{
 *     key: string,
 *     type: string,
 *     color: { r: number, g: number, b: number, a: number } | null,
 *     offset: { x: number, y: number } | null,
 *     radius: number,
 *     spread: number | null,
 *     count: number
 *   }>,
 *   totalNodesWithEffects: number
 * }>}
 */
async function scanEffects() {
  const effectMap = new Map(); // key → { ...props, count }
  let totalNodesWithEffects = 0;

  function effectToKey(effect) {
    if (effect.type === 'DROP_SHADOW' || effect.type === 'INNER_SHADOW') {
      const c = effect.color;
      return `${effect.type}|${effect.offset.x},${effect.offset.y}|${effect.radius}|${effect.spread || 0}|${c.r.toFixed(2)},${c.g.toFixed(2)},${c.b.toFixed(2)},${c.a.toFixed(2)}`;
    }
    if (effect.type === 'LAYER_BLUR' || effect.type === 'BACKGROUND_BLUR') {
      return `${effect.type}|${effect.radius}`;
    }
    return `${effect.type}|unknown`;
  }

  for (const page of figma.root.children) {
    await figma.setCurrentPageAsync(page);

    page.findAll(node => {
      if (!node.visible) return false;
      if (!('effects' in node) || !Array.isArray(node.effects) || node.effects.length === 0) return false;

      // Skip if already has an effect style
      if ('effectStyleId' in node && node.effectStyleId) return false;

      totalNodesWithEffects++;

      for (const effect of node.effects) {
        if (!effect.visible) continue;

        const key = effectToKey(effect);

        if (!effectMap.has(key)) {
          const entry = {
            key,
            type: effect.type,
            color: effect.color ? {
              r: effect.color.r,
              g: effect.color.g,
              b: effect.color.b,
              a: effect.color.a
            } : null,
            offset: effect.offset ? { x: effect.offset.x, y: effect.offset.y } : null,
            radius: effect.radius,
            spread: effect.spread || null,
            count: 0
          };
          effectMap.set(key, entry);
        }
        effectMap.get(key).count++;
      }

      return false;
    });
  }

  const effects = [...effectMap.values()].sort((a, b) => b.count - a.count);

  return { effects, totalNodesWithEffects };
}
