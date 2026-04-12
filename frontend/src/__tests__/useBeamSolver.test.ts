// frontend/src/__tests__/useBeamSolver.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useBeamSolver } from '@/hooks/useBeamSolver'
import type { BeamInput, BeamResult } from '@/types/api'

const mockInput: BeamInput = {
  length: 6, angle_deg: 0,
  supports: [{ x: 0, type: 1 }, { x: 6, type: 2 }],
  point_loads: [], distributed_load: 0,
  q_start: 0, q_end: 6, EI: 21000, EA: 2100000,
}

const mockResult: BeamResult = {
  reactions: { 'x=0.0_Fy': 50, 'x=6.0_Fy': 50 },
  diagrams: [{ x: 0, N: 0, V: 50, M: 0 }, { x: 6, N: 0, V: -50, M: 0 }],
  max_M: 75, max_V: 50,
  deflection: [{ x: 0, ux: 0, uy: 0 }, { x: 6, ux: 0, uy: 0 }],
}

beforeEach(() => { vi.restoreAllMocks() })

describe('useBeamSolver — REQ-02-02', () => {
  it('success: sets result from 200 response', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockResult,
    }))
    const { result } = renderHook(() => useBeamSolver())
    await act(async () => { await result.current.solve(mockInput) })
    expect(result.current.result).toEqual(mockResult)
    expect(result.current.error).toBeNull()
  })

  it('422: sets error message from detail', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false,
      status: 422,
      json: async () => ({ detail: 'Structura instabilă' }),
    }))
    const { result } = renderHook(() => useBeamSolver())
    await act(async () => { await result.current.solve(mockInput) })
    expect(result.current.result).toBeNull()
    expect(result.current.error).toBeTruthy()
    expect(typeof result.current.error).toBe('string')
  })

  it('network error: sets error message', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('Network failure')))
    const { result } = renderHook(() => useBeamSolver())
    await act(async () => { await result.current.solve(mockInput) })
    expect(result.current.result).toBeNull()
    expect(result.current.error).toBeTruthy()
  })
})
