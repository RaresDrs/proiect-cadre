import { useState, useEffect } from 'react'
import { useLang } from '@/hooks/useLang'
import type { BeamInput, Support, PointLoad } from '@/types/api'

interface BeamPreviewProps {
  input: BeamInput
}

// Map beam x-coordinate to SVG x-coordinate
function toSvgX(x: number, length: number): number {
  if (length === 0) return 40
  return 40 + (x / length) * 520
}

function renderSupport(support: Support, length: number, key: number) {
  const svgX = toSvgX(support.x, length)
  const beamY = 100

  if (support.type === 3) {
    // Fixed support: hatched rectangle on the left
    return (
      <g key={key}>
        <rect x={svgX - 12} y={beamY - 20} width={12} height={40}
          fill="var(--brand-primary, #6366f1)" opacity={0.8} />
        {[-15, -5, 5, 15].map((dy, i) => (
          <line key={i}
            x1={svgX - 12} y1={beamY + dy}
            x2={svgX - 22} y2={beamY + dy + 8}
            stroke="var(--brand-primary, #6366f1)" strokeWidth={1.5} />
        ))}
      </g>
    )
  }

  if (support.type === 1) {
    // Pin support: triangle pointing up, vertex at beam
    return (
      <g key={key}>
        <polygon
          points={`${svgX},${beamY} ${svgX - 12},${beamY + 22} ${svgX + 12},${beamY + 22}`}
          fill="var(--brand-primary, #6366f1)"
          opacity={0.85}
        />
        <line x1={svgX - 16} y1={beamY + 24} x2={svgX + 16} y2={beamY + 24}
          stroke="var(--brand-primary, #6366f1)" strokeWidth={2} />
      </g>
    )
  }

  // Roller: triangle + circle underneath
  return (
    <g key={key}>
      <polygon
        points={`${svgX},${beamY} ${svgX - 12},${beamY + 20} ${svgX + 12},${beamY + 20}`}
        fill="var(--brand-primary, #6366f1)"
        opacity={0.85}
      />
      <circle cx={svgX} cy={beamY + 26} r={5}
        fill="none" stroke="var(--brand-primary, #6366f1)" strokeWidth={2} />
    </g>
  )
}

function renderPointLoad(load: PointLoad, length: number, key: number) {
  const svgX = toSvgX(load.x, length)
  const beamY = 100
  const arrowLen = 35

  const elements = []

  if (load.fy !== 0) {
    const dir = load.fy > 0 ? -1 : 1  // positive fy = upward
    const y1 = beamY + dir * arrowLen
    const y2 = beamY
    elements.push(
      <g key={`fy-${key}`}>
        <line x1={svgX} y1={y1} x2={svgX} y2={y2}
          stroke="var(--color-success, #22c55e)" strokeWidth={2} />
        <polygon
          points={`${svgX},${y2} ${svgX - 5},${y2 + dir * 10} ${svgX + 5},${y2 + dir * 10}`}
          fill="var(--color-success, #22c55e)"
        />
      </g>
    )
  }

  if (load.fx !== 0) {
    const dir = load.fx > 0 ? 1 : -1  // positive fx = rightward
    const x1 = svgX - dir * arrowLen
    const x2 = svgX
    elements.push(
      <g key={`fx-${key}`}>
        <line x1={x1} y1={beamY} x2={x2} y2={beamY}
          stroke="var(--color-success, #22c55e)" strokeWidth={2} />
        <polygon
          points={`${x2},${beamY} ${x2 - dir * 10},${beamY - 5} ${x2 - dir * 10},${beamY + 5}`}
          fill="var(--color-success, #22c55e)"
        />
      </g>
    )
  }

  return <g key={key}>{elements}</g>
}

function renderDistributedLoad(input: BeamInput) {
  if (input.distributed_load === 0) return null
  const x1 = toSvgX(input.q_start, input.length)
  const x2 = toSvgX(input.q_end, input.length)
  const beamY = 100
  const arrowTop = beamY - 45
  const arrowLen = 30
  const step = Math.max(20, (x2 - x1) / 8)

  const arrows = []
  for (let x = x1; x <= x2 + 1; x += step) {
    const cx = Math.min(x, x2)
    arrows.push(
      <g key={cx}>
        <line x1={cx} y1={arrowTop} x2={cx} y2={beamY}
          stroke="var(--color-success, #22c55e)" strokeWidth={1.5} />
        <polygon
          points={`${cx},${beamY} ${cx - 4},${beamY - 8} ${cx + 4},${beamY - 8}`}
          fill="var(--color-success, #22c55e)"
        />
      </g>
    )
  }

  return (
    <g>
      <line x1={x1} y1={arrowTop} x2={x2} y2={arrowTop}
        stroke="var(--color-success, #22c55e)" strokeWidth={2} />
      {arrows}
    </g>
  )
}

export function BeamPreview({ input }: BeamPreviewProps) {
  const { t } = useLang()
  const [debouncedInput, setDebouncedInput] = useState(input)

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedInput(input), 150)
    return () => clearTimeout(timer)
  }, [input])

  return (
    <div className="rounded-xl border border-[var(--brand-border)] bg-[var(--brand-card)] p-4">
      <h3 className="font-semibold text-sm text-[var(--brand-text)] mb-3">
        {t('beam.preview.title')}
      </h3>
      <svg
        viewBox="0 0 600 200"
        width="100%"
        aria-label={t('beam.preview.title')}
        className="rounded"
      >
        {/* Background */}
        <rect x={0} y={0} width={600} height={200} fill="transparent" />

        {/* Beam line */}
        <line
          x1={40} y1={100}
          x2={560} y2={100}
          stroke="var(--brand-accent, #8b5cf6)"
          strokeWidth={4}
          strokeLinecap="round"
        />

        {/* Supports */}
        {debouncedInput.supports.map((support, i) =>
          renderSupport(support, debouncedInput.length, i)
        )}

        {/* Point loads */}
        {debouncedInput.point_loads.map((load, i) =>
          renderPointLoad(load, debouncedInput.length, i)
        )}

        {/* Distributed load */}
        {renderDistributedLoad(debouncedInput)}

        {/* Length label */}
        <text
          x={300} y={185}
          textAnchor="middle"
          fontSize={11}
          fill="var(--brand-muted, #94a3b8)"
        >
          L = {debouncedInput.length} m
        </text>
      </svg>
    </div>
  )
}
