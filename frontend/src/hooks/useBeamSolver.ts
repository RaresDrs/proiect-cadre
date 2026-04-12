// frontend/src/hooks/useBeamSolver.ts
import { useState, useCallback } from 'react'
import type { BeamInput, BeamResult } from '@/types/api'

interface BeamSolverState {
  result: BeamResult | null
  loading: boolean
  error: string | null
}

export function useBeamSolver() {
  const [state, setState] = useState<BeamSolverState>({
    result: null, loading: false, error: null,
  })

  const solve = useCallback(async (input: BeamInput) => {
    setState({ result: null, loading: true, error: null })
    try {
      const response = await fetch('/api/v1/beams/solve', {
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
      const result: BeamResult = await response.json()
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
