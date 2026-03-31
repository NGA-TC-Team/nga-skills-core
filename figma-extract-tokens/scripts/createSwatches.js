/**
 * createSwatches
 *
 * Creates visual documentation frames on the current page showing
 * color palette swatches. Each hue group is a row of colored rectangles
 * with hex labels below.
 *
 * Call AFTER variables have been created. Pass the organized color groups
 * and their variable IDs so swatches can be bound to variables.
 *
 * @param {Array<{
 *   groupName: string,
 *   colors: Array<{
 *     step: string,
 *     hex: string,
 *     variableId: string
 *   }>
 * }>} colorGroups - Organized color palette groups
 *
 * @returns {Promise<{ frameId: string, createdNodeIds: string[] }>}
 */
async function createSwatches(colorGroups) {
  const SWATCH_SIZE = 64;
  const SWATCH_GAP = 8;
  const GROUP_GAP = 32;
  const LABEL_HEIGHT = 20;
  const createdNodeIds = [];

  await figma.loadFontAsync({ family: 'Inter', style: 'Regular' });

  // Find clear space
  let maxX = 0;
  for (const child of figma.currentPage.children) {
    maxX = Math.max(maxX, child.x + child.width);
  }

  // Main container
  const container = figma.createFrame();
  container.name = 'Color Palette';
  container.layoutMode = 'VERTICAL';
  container.itemSpacing = GROUP_GAP;
  container.paddingTop = 40;
  container.paddingRight = 40;
  container.paddingBottom = 40;
  container.paddingLeft = 40;
  container.fills = [{ type: 'SOLID', color: { r: 1, g: 1, b: 1 } }];
  container.x = maxX + 100;
  container.y = 0;
  createdNodeIds.push(container.id);

  // Title
  const title = figma.createText();
  title.characters = 'Color Palette';
  title.fontSize = 24;
  title.fontName = { family: 'Inter', style: 'Regular' };
  container.appendChild(title);
  createdNodeIds.push(title.id);

  for (const group of colorGroups) {
    // Group label
    const groupFrame = figma.createFrame();
    groupFrame.name = group.groupName;
    groupFrame.layoutMode = 'VERTICAL';
    groupFrame.itemSpacing = 8;
    groupFrame.fills = [];
    container.appendChild(groupFrame);
    groupFrame.layoutSizingHorizontal = 'HUG';
    groupFrame.layoutSizingVertical = 'HUG';
    createdNodeIds.push(groupFrame.id);

    const groupLabel = figma.createText();
    groupLabel.characters = group.groupName;
    groupLabel.fontSize = 14;
    groupLabel.fontName = { family: 'Inter', style: 'Regular' };
    groupLabel.fills = [{ type: 'SOLID', color: { r: 0.4, g: 0.4, b: 0.4 } }];
    groupFrame.appendChild(groupLabel);
    createdNodeIds.push(groupLabel.id);

    // Swatch row
    const row = figma.createFrame();
    row.name = `${group.groupName} swatches`;
    row.layoutMode = 'HORIZONTAL';
    row.itemSpacing = SWATCH_GAP;
    row.fills = [];
    groupFrame.appendChild(row);
    row.layoutSizingHorizontal = 'HUG';
    row.layoutSizingVertical = 'HUG';
    createdNodeIds.push(row.id);

    for (const color of group.colors) {
      // Swatch cell (vertical: rect + label)
      const cell = figma.createFrame();
      cell.name = `${group.groupName}/${color.step}`;
      cell.layoutMode = 'VERTICAL';
      cell.itemSpacing = 4;
      cell.fills = [];
      row.appendChild(cell);
      cell.layoutSizingHorizontal = 'HUG';
      cell.layoutSizingVertical = 'HUG';
      createdNodeIds.push(cell.id);

      // Color rectangle
      const rect = figma.createRectangle();
      rect.name = color.step;
      rect.resize(SWATCH_SIZE, SWATCH_SIZE);
      rect.cornerRadius = 8;

      // Bind to variable if available
      if (color.variableId) {
        const variable = await figma.variables.getVariableByIdAsync(color.variableId);
        if (variable) {
          const paint = figma.variables.setBoundVariableForPaint(
            { type: 'SOLID', color: { r: 0, g: 0, b: 0 } },
            'color',
            variable
          );
          rect.fills = [paint];
        }
      } else {
        // Fallback: use hex color
        const hex = color.hex.replace('#', '');
        const r = parseInt(hex.substring(0, 2), 16) / 255;
        const g = parseInt(hex.substring(2, 4), 16) / 255;
        const b = parseInt(hex.substring(4, 6), 16) / 255;
        rect.fills = [{ type: 'SOLID', color: { r, g, b } }];
      }

      cell.appendChild(rect);
      createdNodeIds.push(rect.id);

      // Label
      const label = figma.createText();
      label.characters = `${color.step}\n${color.hex}`;
      label.fontSize = 10;
      label.fontName = { family: 'Inter', style: 'Regular' };
      label.fills = [{ type: 'SOLID', color: { r: 0.3, g: 0.3, b: 0.3 } }];
      cell.appendChild(label);
      createdNodeIds.push(label.id);
    }
  }

  // Resize container to hug
  container.layoutSizingHorizontal = 'HUG';
  container.layoutSizingVertical = 'HUG';

  return { frameId: container.id, createdNodeIds };
}
