// REQ-03-02, REQ-03-03
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useFrameSolver } from '@/hooks/useFrameSolver'
import type { FrameInput, FrameResult } from '@/types/api'

const mockInput: FrameInput = {
  nodes: [
    { id: 'n1', x: 0, y: 0, constraint: 'pin' },
    { id: 'n2', x: 4, y: 0, constraint: 'roller' },
  ],
  bars: [{ id: 'b1', node_i: 'n1', node_j: 'n2', EI: 21000, EA: 2100000 }],
  node_loads: [],
  bar_loads: [{ bar_id: 'b1', q: 10, q_start: 0, q_end: 1 }],
}

const mockResult: FrameResult = {
  bar_diagrams: [{ bar_id: 'b1', M: [0, 20, 0], V: [20, 0, -20], N: [0, 0, 0] }],
  node_results: [
    { node_id: 'n1', ux: 0, uy: 0, phi_z: 0 },
    { node_id: 'n2', ux: 0, uy: 0, phi_z: 0 },
  ],
  reactions: { 'node_n1_Fy': 20, 'node_n2_Fy': 20 },
  max_M: 20, max_V: 20, max_N: 0,
}

beforeEach(() => { vi.restoreAllMocks() })

describe('useFrameSolver — REQ-03-02, REQ-03-03', () => {
  it('success: sets result from 200 response, clears error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockResult,
    }))
    const { result } = renderHook(() => useFrameSolver())
    await act(async () => { await result.current.solve(mockInput) })
    expect(result.current.result).toEqual(mockResult)
    expect(result.current.error).toBeNull()
    expect(result.current.loading).toBe(false)
  })

  it('422: sets error string from detail field', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false,
      status: 422,
      json: async () => ({ detail: 'Cadrul nu are reazeme' }),
    }))
    const { result } = renderHook(() => useFrameSolver())
    await act(async () => { await result.current.solve(mockInput) })
    expect(result.current.result).toBeNull()
    expect(result.current.error).toContain('Cadrul nu are reazeme')
  })

  it('network error: sets error string', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('Network failure')))
    const { result } = renderHook(() => useFrameSolver())
    await act(async () => { await result.current.solve(mockInput) })
    expect(result.current.result).toBeNull()
    expect(result.current.error).toBeTruthy()
  })

  it('reset(): clears result and error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockResult,
    }))
    const { result } = renderHook(() => useFrameSolver())
    await act(async () => { await result.current.solve(mockInput) })
    expect(result.current.result).not.toBeNull()
    act(() => { result.current.reset() })
    expect(result.current.result).toBeNull()
    expect(result.current.error).toBeNull()
  })
})
