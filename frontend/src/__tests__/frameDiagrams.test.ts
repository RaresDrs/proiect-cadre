// REQ-03-11
import { describe, it, expect } from 'vitest'
import { buildDiagramPath } from '@/components/frame/FrameDiagrams'

const nodeI = { sx: 100, sy: 300 }
const nodeJ = { sx: 400, sy: 300 }  // horizontal bar left→right

describe('buildDiagramPath — REQ-03-11', () => {
  it('horizontal bar: positive M values produce perpendicular offset above bar (lower sy)', () => {
    // Horizontal bar going right (dx>0, dy=0), perpendicular CCW = up = lower sy in SVG
    const values = [0, 10, 0]
    const path = buildDiagramPath(nodeI, nodeJ, values, 10)
    expect(path).toMatch(/^M /)
    expect(path).toMatch(/Z$/)
    // Extract all numeric pairs and check that some y < nodeI.sy (300)
    const coords = path
      .replace(/[MLZ]/g, '')
      .trim()
      .split(/\s+/)
      .map(pair => pair.split(',').map(Number))
    const ys = coords.map(c => c[1])
    expect(Math.min(...ys)).toBeLessThan(nodeI.sy)
  })

  it('returns closed SVG path string starting with M and ending with Z', () => {
    const path = buildDiagramPath(nodeI, nodeJ, [0, 5, 10, 5, 0], 5)
    expect(path.startsWith('M ')).toBe(true)
    expect(path.endsWith(' Z')).toBe(true)
  })

  it('zero values produce path that lies on bar axis (all y coords equal to bar y)', () => {
    const path = buildDiagramPath(nodeI, nodeJ, [0, 0, 0], 10)
    const coords = path
      .replace(/[MLZ]/g, '')
      .trim()
      .split(/\s+/)
      .map(pair => pair.split(',').map(Number))
    const ys = coords.map(c => c[1])
    ys.forEach(y => expect(Math.abs(y - 300)).toBeLessThan(0.1))
  })

  it('returns empty string for fewer than 2 values', () => {
    expect(buildDiagramPath(nodeI, nodeJ, [], 10)).toBe('')
    expect(buildDiagramPath(nodeI, nodeJ, [5], 10)).toBe('')
  })
})
