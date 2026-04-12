import { useState } from 'react'
import { useLang } from '@/hooks/useLang'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import type { BeamInput, Support, PointLoad } from '@/types/api'

interface BeamInputFormProps {
  initialInput: BeamInput
  onSolve: (input: BeamInput) => void
  loading?: boolean
}

function isStable(supports: Support[]): boolean {
  if (supports.length < 2) return false
  const hasHorizontalRestraint = supports.some(s => s.type === 1 || s.type === 3)
  const totalRestraints = supports.reduce((acc, s) => {
    if (s.type === 1) return acc + 2  // pin: Fx + Fy
    if (s.type === 2) return acc + 1  // roller: Fy only
    if (s.type === 3) return acc + 3  // fixed: Fx + Fy + M
    return acc
  }, 0)
  return hasHorizontalRestraint && totalRestraints >= 3
}

export function BeamInputForm({ initialInput, onSolve, loading = false }: BeamInputFormProps) {
  const { t } = useLang()
  const [input, setInput] = useState<BeamInput>(initialInput)

  const updateField = <K extends keyof BeamInput>(key: K, value: BeamInput[K]) => {
    setInput(prev => ({ ...prev, [key]: value }))
  }

  const addSupport = () => {
    setInput(prev => ({
      ...prev,
      supports: [...prev.supports, { x: 0, type: 1 }],
    }))
  }

  const removeSupport = (index: number) => {
    setInput(prev => ({
      ...prev,
      supports: prev.supports.filter((_, i) => i !== index),
    }))
  }

  const updateSupport = (index: number, field: keyof Support, value: number) => {
    setInput(prev => ({
      ...prev,
      supports: prev.supports.map((s, i) => i === index ? { ...s, [field]: value } : s),
    }))
  }

  const addPointLoad = () => {
    setInput(prev => ({
      ...prev,
      point_loads: [...prev.point_loads, { x: 0, fx: 0, fy: 0 }],
    }))
  }

  const removePointLoad = (index: number) => {
    setInput(prev => ({
      ...prev,
      point_loads: prev.point_loads.filter((_, i) => i !== index),
    }))
  }

  const updatePointLoad = (index: number, field: keyof PointLoad, value: number) => {
    setInput(prev => ({
      ...prev,
      point_loads: prev.point_loads.map((p, i) => i === index ? { ...p, [field]: value } : p),
    }))
  }

  const stable = isStable(input.supports)

  return (
    <div className="space-y-6 p-4 rounded-xl border border-[var(--brand-border)] bg-[var(--brand-card)]">
      {/* Geometry section */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1">
          <Label htmlFor="beam-length">{t('beam.form.length')}</Label>
          <Input
            id="beam-length"
            type="number"
            min={0.1}
            step={0.1}
            value={input.length}
            onChange={e => updateField('length', parseFloat(e.target.value) || 0)}
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor="beam-angle">{t('beam.form.angle')}</Label>
          <Input
            id="beam-angle"
            type="number"
            step={1}
            value={input.angle_deg}
            onChange={e => updateField('angle_deg', parseFloat(e.target.value) || 0)}
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor="beam-EI">{t('beam.form.EI')}</Label>
          <Input
            id="beam-EI"
            type="number"
            min={0}
            step={100}
            value={input.EI}
            onChange={e => updateField('EI', parseFloat(e.target.value) || 0)}
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor="beam-EA">{t('beam.form.EA')}</Label>
          <Input
            id="beam-EA"
            type="number"
            min={0}
            step={1000}
            value={input.EA}
            onChange={e => updateField('EA', parseFloat(e.target.value) || 0)}
          />
        </div>
      </div>

      {/* Supports section */}
      <div className="space-y-2">
        <h3 className="font-semibold text-sm text-[var(--brand-text)]">{t('beam.form.supports')}</h3>
        {input.supports.map((support, index) => (
          <div key={index} className="flex items-center gap-2">
            <div className="space-y-1 flex-1">
              <Label htmlFor={`support-x-${index}`}>{t('beam.form.support.x')}</Label>
              <Input
                id={`support-x-${index}`}
                type="number"
                min={0}
                step={0.1}
                value={support.x}
                onChange={e => updateSupport(index, 'x', parseFloat(e.target.value) || 0)}
              />
            </div>
            <div className="space-y-1 flex-1">
              <Label htmlFor={`support-type-${index}`}>{t('beam.form.support.type')}</Label>
              <select
                id={`support-type-${index}`}
                value={support.type}
                onChange={e => updateSupport(index, 'type', parseInt(e.target.value))}
                className="h-8 w-full rounded-lg border border-input bg-transparent px-2.5 py-1 text-sm transition-colors outline-none focus-visible:border-ring"
              >
                <option value={1}>{t('beam.form.support.pin')}</option>
                <option value={2}>{t('beam.form.support.roller')}</option>
                <option value={3}>{t('beam.form.support.fixed')}</option>
              </select>
            </div>
            <Button
              variant="destructive"
              size="sm"
              onClick={() => removeSupport(index)}
              className="mt-5"
            >
              {t('beam.form.remove')}
            </Button>
          </div>
        ))}
        <Button variant="outline" size="sm" onClick={addSupport}>
          {t('beam.form.add.support')}
        </Button>
      </div>

      {/* Point loads section */}
      <div className="space-y-2">
        <h3 className="font-semibold text-sm text-[var(--brand-text)]">{t('beam.form.point.loads')}</h3>
        {input.point_loads.map((load, index) => (
          <div key={index} className="flex items-center gap-2">
            <div className="space-y-1 flex-1">
              <Label htmlFor={`load-x-${index}`}>{t('beam.form.load.x')}</Label>
              <Input
                id={`load-x-${index}`}
                type="number"
                step={0.1}
                value={load.x}
                onChange={e => updatePointLoad(index, 'x', parseFloat(e.target.value) || 0)}
              />
            </div>
            <div className="space-y-1 flex-1">
              <Label htmlFor={`load-fx-${index}`}>{t('beam.form.load.fx')}</Label>
              <Input
                id={`load-fx-${index}`}
                type="number"
                step={1}
                value={load.fx}
                onChange={e => updatePointLoad(index, 'fx', parseFloat(e.target.value) || 0)}
              />
            </div>
            <div className="space-y-1 flex-1">
              <Label htmlFor={`load-fy-${index}`}>{t('beam.form.load.fy')}</Label>
              <Input
                id={`load-fy-${index}`}
                type="number"
                step={1}
                value={load.fy}
                onChange={e => updatePointLoad(index, 'fy', parseFloat(e.target.value) || 0)}
              />
            </div>
            <Button
              variant="destructive"
              size="sm"
              onClick={() => removePointLoad(index)}
              className="mt-5"
            >
              {t('beam.form.remove')}
            </Button>
          </div>
        ))}
        <Button variant="outline" size="sm" onClick={addPointLoad}>
          {t('beam.form.add.load')}
        </Button>
      </div>

      {/* Distributed load section */}
      <div className="space-y-2">
        <h3 className="font-semibold text-sm text-[var(--brand-text)]">{t('beam.form.distributed')}</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="space-y-1">
            <Label htmlFor="dist-q">{t('beam.form.dist.q')}</Label>
            <Input
              id="dist-q"
              type="number"
              step={0.1}
              value={input.distributed_load}
              onChange={e => updateField('distributed_load', parseFloat(e.target.value) || 0)}
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="dist-start">{t('beam.form.dist.start')}</Label>
            <Input
              id="dist-start"
              type="number"
              min={0}
              step={0.1}
              value={input.q_start}
              onChange={e => updateField('q_start', parseFloat(e.target.value) || 0)}
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="dist-end">{t('beam.form.dist.end')}</Label>
            <Input
              id="dist-end"
              type="number"
              min={0}
              step={0.1}
              value={input.q_end}
              onChange={e => updateField('q_end', parseFloat(e.target.value) || 0)}
            />
          </div>
        </div>
      </div>

      {/* Stability warning */}
      {!stable && input.supports.length > 0 && (
        <p className="text-sm text-[var(--color-destructive,#ef4444)]">
          {t('beam.form.unstable')}
        </p>
      )}

      {/* Submit button */}
      <Button
        onClick={() => onSolve(input)}
        disabled={!stable || loading}
        className="w-full bg-[var(--brand-accent)] text-white hover:bg-[var(--brand-accent)]/90"
      >
        {t('beam.form.solve')}
      </Button>
    </div>
  )
}
