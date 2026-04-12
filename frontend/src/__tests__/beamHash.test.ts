// frontend/src/__tests__/beamHash.test.ts
import { describe, it, expect } from 'vitest'
import { encodeBeamHash, decodeBeamHash } from '@/lib/beamHash'
import type { BeamInput } from '@/types/api'

const sampleInput: BeamInput = {
  length: 6, angle_deg: 0,
  supports: [{ x: 0, type: 1 }, { x: 6, type: 2 }],
  point_loads: [{ x: 3, fx: 0, fy: -10 }],
  distributed_load: 5, q_start: 0, q_end: 6,
  EI: 21000, EA: 2100000,
}

describe('beamHash — REQ-02-02', () => {
  it('round-trip encode then decode returns equivalent input', () => {
    const hash = encodeBeamHash(sampleInput)
    const decoded = decodeBeamHash(hash)
    expect(decoded).not.toBeNull()
    expect(decoded!.length).toBe(sampleInput.length)
    expect(decoded!.supports).toHaveLength(2)
    expect(decoded!.point_loads[0].fy).toBe(-10)
  })

  it('decodeBeamHash returns null for empty string', () => {
    expect(decodeBeamHash('')).toBeNull()
  })

  it('decodeBeamHash returns null for malformed base64', () => {
    expect(decodeBeamHash('!!!not-valid-base64!!!')).toBeNull()
  })

  it('decodeBeamHash returns null for valid base64 but invalid JSON', () => {
    const invalidJson = btoa('not json at all')
    expect(decodeBeamHash(invalidJson)).toBeNull()
  })
})
