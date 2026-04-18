// REQ-03-02, REQ-03-03
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
// useFrameSolver will be created in 03-02-PLAN.md
// import { useFrameSolver } from '@/hooks/useFrameSolver'
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
  it.todo('success: sets result from 200 response, clears error')
  it.todo('422: sets error string from detail field')
  it.todo('network error: sets error string')
  it.todo('reset(): clears result and error')
})
