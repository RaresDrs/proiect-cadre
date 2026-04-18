// REQ-03-04, REQ-03-05
import { describe, it, expect } from 'vitest'
import {
  worldToSvg, svgToWorld, snapToGrid, hitTestNode, hitTestBar, computeBBox
} from '@/lib/frameCanvas'
import type { FrameNode, FrameBar } from '@/types/api'

const dims = { width: 600, height: 400, margin: 40 }

const nodes: FrameNode[] = [
  { id: 'n1', x: 0, y: 0, constraint: 'pin' },
  { id: 'n2', x: 0, y: 3, constraint: 'free' },
  { id: 'n3', x: 4, y: 3, constraint: 'free' },
  { id: 'n4', x: 4, y: 0, constraint: 'roller' },
]

const bbox = computeBBox(nodes, 0)  // no extra padding for precise tests

describe('worldToSvg — REQ-03-04', () => {
  it('Y axis is inverted: higher world Y → lower SVG y value', () => {
    const lower = worldToSvg(0, 0, bbox, dims)
    const higher = worldToSvg(0, 3, bbox, dims)
    expect(higher.sy).toBeLessThan(lower.sy)
  })

  it('preserves aspect ratio using min of x-scale and y-scale', () => {
    const p00 = worldToSvg(0, 0, bbox, dims)
    const p40 = worldToSvg(4, 0, bbox, dims)
    const p03 = worldToSvg(0, 3, bbox, dims)
    const scaleX = (p40.sx - p00.sx) / 4
    const scaleY = (p00.sy - p03.sy) / 3
    expect(Math.abs(scaleX - scaleY)).toBeLessThan(0.01)
  })

  it('maps origin node to margin area (sx >= margin)', () => {
    const p = worldToSvg(nodes[0].x, nodes[0].y, bbox, dims)
    expect(p.sx).toBeGreaterThanOrEqual(dims.margin)
  })
})

describe('snapToGrid — REQ-03-05', () => {
  it('snaps 0.3 to 0.5 (nearest 0.5 grid)', () => {
    expect(snapToGrid(0.3, 0.5)).toBe(0.5)
  })

  it('snaps 0.8 to 1.0', () => {
    expect(snapToGrid(0.8, 0.5)).toBe(1.0)
  })

  it('snaps negative value correctly: -0.3 → -0.5', () => {
    expect(snapToGrid(-0.3, 0.5)).toBe(-0.5)
  })

  it('snaps 0.0 to 0.0', () => {
    expect(snapToGrid(0.0, 0.5)).toBe(0.0)
  })
})

describe('hitTestNode — REQ-03-04', () => {
  it('returns node id when click is within 10px of node SVG position', () => {
    const { sx, sy } = worldToSvg(nodes[0].x, nodes[0].y, bbox, dims)
    const found = hitTestNode(sx + 5, sy + 5, nodes, bbox, dims, 10)
    expect(found).toBe('n1')
  })

  it('returns null when click is far from all nodes', () => {
    const foundFar = hitTestNode(-500, -500, nodes, bbox, dims, 10)
    expect(foundFar).toBeNull()
  })
})

describe('hitTestBar — REQ-03-04', () => {
  const bars: FrameBar[] = [
    { id: 'b1', node_i: 'n1', node_j: 'n2', EI: 21000, EA: 2100000 },
  ]

  it('returns bar id when click is on bar midpoint', () => {
    const midWorld = { x: 0, y: 1.5 }
    const { sx, sy } = worldToSvg(midWorld.x, midWorld.y, bbox, dims)
    const found = hitTestBar(sx, sy, bars, nodes, bbox, dims, 8)
    expect(found).toBe('b1')
  })

  it('returns null when click misses all bars', () => {
    const found = hitTestBar(-500, -500, bars, nodes, bbox, dims, 8)
    expect(found).toBeNull()
  })
})
