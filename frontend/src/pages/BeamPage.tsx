import { useState } from 'react'
import { useLang } from '@/hooks/useLang'
import { BeamInputForm } from '@/components/beam/BeamInputForm'
import { BeamPreview } from '@/components/beam/BeamPreview'
import type { BeamInput } from '@/types/api'

const DEFAULT_INPUT: BeamInput = {
  length: 6, angle_deg: 0,
  supports: [{ x: 0, type: 1 }, { x: 6, type: 2 }],
  point_loads: [], distributed_load: 0,
  q_start: 0, q_end: 6, EI: 21000, EA: 2100000,
}

export default function BeamPage() {
  const { t } = useLang()
  const [input, setInput] = useState<BeamInput>(DEFAULT_INPUT)

  // onSolve stub — will be replaced by useBeamSolver integration in 02-02
  const handleSolve = (submittedInput: BeamInput) => {
    setInput(submittedInput)
    // TODO (02-02): call useBeamSolver here
  }

  return (
    <div className="min-h-screen pt-16">
      <div className="max-w-[1200px] mx-auto px-6 py-8">
        <h1 className="text-3xl font-bold text-[var(--brand-text)] mb-2">
          {t('beam.page.title')}
        </h1>
        <p className="text-[var(--brand-muted)] mb-8">{t('beam.page.subtitle')}</p>
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Form — left on lg, full-width on mobile */}
          <div className="w-full lg:w-1/2">
            <BeamInputForm
              initialInput={input}
              onSolve={handleSolve}
            />
          </div>
          {/* Preview — right on lg, below form on mobile */}
          <div className="w-full lg:w-1/2">
            <BeamPreview input={input} />
          </div>
        </div>
      </div>
    </div>
  )
}
