// REQ-03-04, REQ-03-05
import { describe, it, expect } from 'vitest'
// worldToSvg, snapToGrid, hitTestNode, hitTestBar will be created in 03-02-PLAN.md
// import { worldToSvg, snapToGrid, hitTestNode, hitTestBar } from '@/lib/frameCanvas'

describe('frameCanvas utilities — REQ-03-04, REQ-03-05', () => {
  describe('worldToSvg', () => {
    it.todo('maps origin (0,0) to bottom-left margin area')
    it.todo('Y axis is inverted: higher world Y → lower SVG y')
    it.todo('preserves aspect ratio using min of x-scale and y-scale')
  })

  describe('snapToGrid', () => {
    it.todo('snaps 0.3 to 0.5 (nearest 0.5 grid)')
    it.todo('snaps 0.8 to 1.0')
    it.todo('snaps negative value correctly')
  })

  describe('hitTestNode', () => {
    it.todo('returns node id when click is within 10px of node SVG position')
    it.todo('returns null when click is far from all nodes')
  })

  describe('hitTestBar', () => {
    it.todo('returns bar id when click is within 8px of bar SVG midpoint segment')
    it.todo('returns null when click misses all bars')
  })
})
