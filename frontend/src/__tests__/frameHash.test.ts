// REQ-03-01, REQ-03-10
import { describe, it, expect } from 'vitest'
// encodeFrameHash and decodeFrameHash will be created in 03-02-PLAN.md
// import { encodeFrameHash, decodeFrameHash } from '@/lib/frameHash'
import type { FrameInput } from '@/types/api'

const sample: FrameInput = {
  nodes: [
    { id: 'n1', x: 0, y: 0, constraint: 'pin' },
    { id: 'n2', x: 0, y: 3, constraint: 'free' },
    { id: 'n3', x: 4, y: 3, constraint: 'free' },
    { id: 'n4', x: 4, y: 0, constraint: 'roller' },
  ],
  bars: [
    { id: 'b1', node_i: 'n1', node_j: 'n2', EI: 21000, EA: 2100000 },
    { id: 'b2', node_i: 'n2', node_j: 'n3', EI: 21000, EA: 2100000 },
    { id: 'b3', node_i: 'n4', node_j: 'n3', EI: 21000, EA: 2100000 },
  ],
  node_loads: [{ node_id: 'n2', Fx: 10, Fy: 0, Mz: 0 }],
  bar_loads: [],
}

describe('frameHash — REQ-03-01, REQ-03-10', () => {
  it.todo('round-trip encode then decode returns equivalent FrameInput')
  it.todo('decodeFrameHash returns null for empty string')
  it.todo('decodeFrameHash returns null for malformed base64')
  it.todo('decodeFrameHash returns null when nodes or bars array is missing')
})
