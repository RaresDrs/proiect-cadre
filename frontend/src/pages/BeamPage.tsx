import { useState, useEffect, useCallback } from 'react'
import { useLang } from '@/hooks/useLang'
import { useBeamSolver } from '@/hooks/useBeamSolver'
import { BeamInputForm } from '@/components/beam/BeamInputForm'
import { BeamPreview } from '@/components/beam/BeamPreview'
import { encodeBeamHash, decodeBeamHash } from '@/lib/beamHash'
import type { BeamInput } from '@/types/api'

const STORAGE_KEY = 'structcalc-beam-last'

const DEFAULT_INPUT: BeamInput = {
  length: 6, angle_deg: 0,
  supports: [{ x: 0, type: 1 }, { x: 6, type: 2 }],
  point_loads: [], distributed_load: 0,
  q_start: 0, q_end: 6, EI: 21000, EA: 2100000,
}

export default function BeamPage() {
  const { t } = useLang()
  const { solve, result, loading, error, reset } = useBeamSolver()

  // Restore state: priority → URL hash → localStorage → default
  const [input, setInput] = useState<BeamInput>(() => {
    // Hash takes precedence (shared link)
    const hashPayload = window.location.hash.replace(/^#/, '')
    const fromHash = decodeBeamHash(hashPayload)
    if (fromHash) return fromHash
    // Fallback: localStorage last session
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) return JSON.parse(stored) as BeamInput
    } catch { /* ignore */ }
    return DEFAULT_INPUT
  })

  // On mount: if hash was present, auto-solve (D-14)
  useEffect(() => {
    const hashPayload = window.location.hash.replace(/^#/, '')
    const fromHash = decodeBeamHash(hashPayload)
    if (fromHash) {
      solve(fromHash)
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const handleSolve = useCallback(async (submittedInput: BeamInput) => {
    setInput(submittedInput)
    // Persist to localStorage (D-16)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(submittedInput))
    // Update URL hash (D-14)
    window.location.hash = encodeBeamHash(submittedInput)
    // Call API
    await solve(submittedInput)
  }, [solve])

  const handleCopyLink = useCallback(() => {
    // D-15: copy current URL (with hash) to clipboard
    navigator.clipboard.writeText(window.location.href).catch(() => {
      // Fallback: create a temporary input element for older browsers
      const el = document.createElement('input')
      el.value = window.location.href
      document.body.appendChild(el)
      el.select()
      document.execCommand('copy')
      document.body.removeChild(el)
    })
  }, [])

  void reset // available for future use (e.g. clear button)

  return (
    <div className="min-h-screen pt-16">
      <div className="max-w-[1200px] mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-3xl font-bold text-[var(--brand-text)]">
            {t('beam.page.title')}
          </h1>
          {/* Copy link button (D-15) — always visible */}
          <button
            onClick={handleCopyLink}
            className="text-sm text-[var(--brand-muted)] hover:text-[var(--brand-accent)] transition-colors"
            aria-label={t('beam.action.copy.link')}
          >
            {t('beam.action.copy.link')}
          </button>
        </div>
        <p className="text-[var(--brand-muted)] mb-8">{t('beam.page.subtitle')}</p>

        {/* Error banner (D-21) */}
        {error && (
          <div
            role="alert"
            className="mb-6 p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300"
          >
            {error}
          </div>
        )}

        {/* Loading skeleton */}
        {loading && (
          <div
            aria-busy="true"
            className="mb-6 h-2 rounded bg-[var(--brand-border)] animate-pulse"
          />
        )}

        <div className="flex flex-col lg:flex-row gap-8">
          <div className="w-full lg:w-1/2">
            <BeamInputForm
              initialInput={input}
              onSolve={handleSolve}
              loading={loading}
            />
          </div>
          <div className="w-full lg:w-1/2">
            <BeamPreview input={input} />
          </div>
        </div>

        {/* Diagram area placeholder — filled in 02-03 */}
        {result && (
          <div id="beam-diagrams" className="mt-10">
            {/* BeamDiagrams component wired in 02-03 */}
            <pre className="text-xs text-[var(--brand-muted)] overflow-auto">
              {JSON.stringify({ max_M: result.max_M, max_V: result.max_V }, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}
