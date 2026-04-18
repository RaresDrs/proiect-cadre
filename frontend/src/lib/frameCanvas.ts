import type { FrameNode, FrameBar } from '@/types/api'

export interface BBox {
  minX: number
  minY: number
  maxX: number
  maxY: number
}

export interface SvgDims {
  width: number
  height: number
  margin: number
}

export interface SvgPoint {
  sx: number
  sy: number
  scale: number
}

/**
 * Converts world (engineering) coordinates to SVG pixel coordinates.
 * Y axis is inverted: higher world Y → lower SVG y (SVG Y grows downward).
 * Preserves aspect ratio using min of x-scale and y-scale.
 * Consistent with BeamPreview.tsx toSvgX() — uses 40px margin.
 */
export function worldToSvg(wx: number, wy: number, bbox: BBox, dims: SvgDims): SvgPoint {
  const rangeX = (bbox.maxX - bbox.minX) || 1
  const rangeY = (bbox.maxY - bbox.minY) || 1
  const scale = Math.min(
    (dims.width - 2 * dims.margin) / rangeX,
    (dims.height - 2 * dims.margin) / rangeY
  )
  const sx = dims.margin + (wx - bbox.minX) * scale
  const sy = dims.height - dims.margin - (wy - bbox.minY) * scale  // Y inverted
  return { sx, sy, scale }
}

/**
 * Converts SVG pixel coordinates back to world (engineering) coordinates.
 * Inverse of worldToSvg. Used to determine where user clicked in world space.
 */
export function svgToWorld(sx: number, sy: number, bbox: BBox, dims: SvgDims): { wx: number; wy: number } {
  const rangeX = (bbox.maxX - bbox.minX) || 1
  const rangeY = (bbox.maxY - bbox.minY) || 1
  const scale = Math.min(
    (dims.width - 2 * dims.margin) / rangeX,
    (dims.height - 2 * dims.margin) / rangeY
  )
  const wx = bbox.minX + (sx - dims.margin) / scale
  const wy = bbox.minY + (dims.height - dims.margin - sy) / scale
  return { wx, wy }
}

/**
 * Computes bounding box of all nodes with padding.
 * Falls back to [0,5]×[0,5] when no nodes exist.
 */
export function computeBBox(nodes: FrameNode[], padding = 1): BBox {
  if (nodes.length === 0) {
    return { minX: 0, minY: 0, maxX: 5, maxY: 5 }
  }
  const xs = nodes.map(n => n.x)
  const ys = nodes.map(n => n.y)
  return {
    minX: Math.min(...xs) - padding,
    minY: Math.min(...ys) - padding,
    maxX: Math.max(...xs) + padding,
    maxY: Math.max(...ys) + padding,
  }
}

/**
 * Snaps a world coordinate to the nearest grid multiple.
 * snapToGrid(0.3, 0.5) → 0.5, snapToGrid(0.8, 0.5) → 1.0
 */
export function snapToGrid(value: number, gridSize = 0.5): number {
  return Math.round(value / gridSize) * gridSize
}

/**
 * Hit test: returns the node.id of the first node whose SVG position is within
 * `threshold` pixels of (clickSx, clickSy). Returns null if no match.
 */
export function hitTestNode(
  clickSx: number,
  clickSy: number,
  nodes: FrameNode[],
  bbox: BBox,
  dims: SvgDims,
  threshold = 10
): string | null {
  for (const node of nodes) {
    const { sx, sy } = worldToSvg(node.x, node.y, bbox, dims)
    const dist = Math.hypot(clickSx - sx, clickSy - sy)
    if (dist <= threshold) return node.id
  }
  return null
}

/**
 * Hit test: returns the bar.id of the first bar whose SVG line segment is within
 * `threshold` pixels of (clickSx, clickSy). Uses point-to-segment distance.
 * Returns null if no match.
 */
export function hitTestBar(
  clickSx: number,
  clickSy: number,
  bars: FrameBar[],
  nodes: FrameNode[],
  bbox: BBox,
  dims: SvgDims,
  threshold = 8
): string | null {
  const nodeMap = new Map(nodes.map(n => [n.id, n]))
  for (const bar of bars) {
    const ni = nodeMap.get(bar.node_i)
    const nj = nodeMap.get(bar.node_j)
    if (!ni || !nj) continue
    const pi = worldToSvg(ni.x, ni.y, bbox, dims)
    const pj = worldToSvg(nj.x, nj.y, bbox, dims)
    const dist = pointToSegmentDistance(
      clickSx, clickSy,
      pi.sx, pi.sy,
      pj.sx, pj.sy
    )
    if (dist <= threshold) return bar.id
  }
  return null
}

/** Returns perpendicular distance from point (px,py) to segment (ax,ay)→(bx,by). */
function pointToSegmentDistance(
  px: number, py: number,
  ax: number, ay: number,
  bx: number, by: number
): number {
  const dx = bx - ax
  const dy = by - ay
  const lenSq = dx * dx + dy * dy
  if (lenSq < 1e-10) return Math.hypot(px - ax, py - ay)
  const t = Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / lenSq))
  const nearX = ax + t * dx
  const nearY = ay + t * dy
  return Math.hypot(px - nearX, py - nearY)
}
