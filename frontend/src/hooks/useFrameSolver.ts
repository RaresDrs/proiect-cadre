// frontend/src/hooks/useFrameSolver.ts
import { useState, useCallback } from 'react'
import type { FrameInput, FrameResult } from '@/types/api'

interface FrameSolverState {
  result: FrameResult | null
  loading: boolean
  error: string | null
}

export function useFrameSolver() {
  const [state, setState] = useState<FrameSolverState>({
    result: null, loading: false, error: null,
  })

  const solve = useCallback(async (input: FrameInput) => {
    setState({ result: null, loading: true, error: null })
    try {
      const response = await fetch('/api/v1/frames/solve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(input),
      })
      if (!response.ok) {
        const body = await response.json().catch(() => ({}))
        const msg = (body as { detail?: string })?.detail ?? `Eroare ${response.status}`
        setState({ result: null, loading: false, error: msg })
        return
      }
      const result: FrameResult = await response.json()
      setState({ result, loading: false, error: null })
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Eroare de rețea'
      setState({ result: null, loading: false, error: msg })
    }
  }, [])

  const reset = useCallback(() => {
    setState({ result: null, loading: false, error: null })
  }, [])

  return { ...state, solve, reset }
}
