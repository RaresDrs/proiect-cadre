import type { FrameResult, FrameNode, FrameBar } from '@/types/api'
import { worldToSvg, computeBBox, type SvgDims } from '@/lib/frameCanvas'

const SVG_DIMS: SvgDims = { width: 600, height: 400, margin: 40 }
const DIAGRAM_SCALE_FACTOR = 0.15

export type DiagramTab = 'M' | 'V' | 'N' | 'deformed'

/**
 * Builds a closed SVG path for a single bar diagram.
 * Values are plotted perpendicular to the bar axis.
 * Positive values → perpendicular left (CCW from bar direction in SVG space).
 * @param nodeI SVG coords of bar start node
 * @param nodeJ SVG coords of bar end node
 * @param values Array of diagram values (M, V, or N)
 * @param scale Pixels per unit value
 * @returns Closed SVG path string "M x0,y0 L ... Z"
 */
export function buildDiagramPath(
  nodeI: { sx: number; sy: number },
  nodeJ: { sx: number; sy: number },
  values: number[],
  scale: number
): string {
  if (values.length < 2) return ''
  const dx = nodeJ.sx - nodeI.sx
  const dy = nodeJ.sy - nodeI.sy
  const barLen = Math.hypot(dx, dy)
  if (barLen < 1e-6) return ''

  // Unit vector along bar
  const ux = dx / barLen
  const uy = dy / barLen
  // Perpendicular vector: 90° CW in standard math = "left" visually in SVG (y-down)
  // (ux,uy) → (uy, -ux) gives "above" for a rightward bar (negative SVG y direction)
  const px = uy
  const py = -ux

  const n = values.length
  const pts = values.map((v, i) => {
    const t = i / (n - 1)
    const bx = nodeI.sx + t * dx
    const by = nodeI.sy + t * dy
    const offset = v * scale
    return `${(bx + px * offset).toFixed(2)},${(by + py * offset).toFixed(2)}`
  })

  return `M ${nodeI.sx.toFixed(2)},${nodeI.sy.toFixed(2)} L ${pts.join(' L ')} L ${nodeJ.sx.toFixed(2)},${nodeJ.sy.toFixed(2)} Z`
}

function computeScale(
  bars: FrameBar[],
  nodes: FrameNode[],
  maxValue: number,
  dims: SvgDims
): number {
  if (maxValue < 1e-9) return 1
  const nodeById = new Map(nodes.map(n => [n.id, n]))
  const bbox = computeBBox(nodes)
  let minBarLen = Infinity
  for (const bar of bars) {
    const ni = nodeById.get(bar.node_i)
    const nj = nodeById.get(bar.node_j)
    if (!ni || !nj) continue
    const pi = worldToSvg(ni.x, ni.y, bbox, dims)
    const pj = worldToSvg(nj.x, nj.y, bbox, dims)
    const len = Math.hypot(pj.sx - pi.sx, pj.sy - pi.sy)
    if (len > 1) minBarLen = Math.min(minBarLen, len)
  }
  if (!isFinite(minBarLen)) return 1
  return (minBarLen * DIAGRAM_SCALE_FACTOR) / maxValue
}

interface SingleBarDiagramProps {
  bar: FrameBar
  values: number[]
  nodeI: FrameNode
  nodeJ: FrameNode
  scale: number
  barIndex: number
  bbox: ReturnType<typeof computeBBox>
  dims: SvgDims
}

function SingleBarDiagram({ bar, values, nodeI, nodeJ, scale, barIndex, bbox, dims }: SingleBarDiagramProps) {
  const pi = worldToSvg(nodeI.x, nodeI.y, bbox, dims)
  const pj = worldToSvg(nodeJ.x, nodeJ.y, bbox, dims)

  const posValues = values.map(v => v > 0 ? v : 0)
  const negValues = values.map(v => v < 0 ? v : 0)

  const hasPos = posValues.some(v => Math.abs(v) > 1e-9)
  const hasNeg = negValues.some(v => Math.abs(v) > 1e-9)

  const animDelay = `${barIndex * 0.08}s`
  const animStyle = {
    animation: `drawDiagram 0.6s ease-out ${animDelay} forwards`,
  }

  const maxV = Math.max(...values)
  const minV = Math.min(...values)
  const maxIdx = values.indexOf(maxV)
  const minIdx = values.indexOf(minV)

  function getPerp(idx: number, v: number) {
    const n = values.length
    const t = idx / (n - 1)
    const dx = pj.sx - pi.sx
    const dy = pj.sy - pi.sy
    const barLen = Math.hypot(dx, dy)
    if (barLen < 1e-6) return { x: pi.sx, y: pi.sy }
    const bx = pi.sx + t * dx
    const by = pi.sy + t * dy
    const perpX = dy / barLen
    const perpY = -dx / barLen
    return { x: bx + perpX * v * scale, y: by + perpY * v * scale }
  }

  const maxLabelPos = getPerp(maxIdx, maxV)
  const minLabelPos = getPerp(minIdx, minV)

  return (
    <g data-testid={`diagram-${bar.id}`}>
      <style>{`
        @keyframes drawDiagram { from { opacity: 0; } to { opacity: 1; } }
        @media (prefers-reduced-motion: reduce) {
          [data-diagram] { animation: none !important; }
        }
      `}</style>

      {hasPos && (
        <path
          data-diagram
          d={buildDiagramPath(pi, pj, posValues, scale)}
          fill="#22c55e"
          fillOpacity={0.3}
          stroke="#22c55e"
          strokeWidth={1.5}
          style={animStyle}
        />
      )}
      {hasNeg && (
        <path
          data-diagram
          d={buildDiagramPath(pi, pj, negValues, scale)}
          fill="#ef4444"
          fillOpacity={0.3}
          stroke="#ef4444"
          strokeWidth={1.5}
          style={animStyle}
        />
      )}

      {Math.abs(maxV) > 1e-9 && (
        <text
          x={maxLabelPos.x} y={maxLabelPos.y - 4}
          fontSize={11} fill="#22c55e" textAnchor="middle"
        >
          {maxV.toFixed(1)}
        </text>
      )}
      {Math.abs(minV) > 1e-9 && minIdx !== maxIdx && (
        <text
          x={minLabelPos.x} y={minLabelPos.y + 12}
          fontSize={11} fill="#ef4444" textAnchor="middle"
        >
          {minV.toFixed(1)}
        </text>
      )}
    </g>
  )
}

interface DeformedShapeProps {
  nodes: FrameNode[]
  bars: FrameBar[]
  result: FrameResult
  bbox: ReturnType<typeof computeBBox>
  dims: SvgDims
  scaleFactor?: number
}

function DeformedShape({ nodes, bars, result, bbox, dims, scaleFactor = 100 }: DeformedShapeProps) {
  const nodeById = new Map(nodes.map(n => [n.id, n]))
  const nodeResultById = new Map(result.node_results.map(r => [r.node_id, r]))

  return (
    <g data-testid="deformed-shape">
      {bars.map(bar => {
        const ni = nodeById.get(bar.node_i)
        const nj = nodeById.get(bar.node_j)
        if (!ni || !nj) return null
        const pi = worldToSvg(ni.x, ni.y, bbox, dims)
        const pj = worldToSvg(nj.x, nj.y, bbox, dims)
        return (
          <line
            key={`orig-${bar.id}`}
            x1={pi.sx} y1={pi.sy} x2={pj.sx} y2={pj.sy}
            stroke="var(--muted-foreground)"
            strokeWidth={1.5}
            strokeDasharray="4 4"
            opacity={0.6}
          />
        )
      })}

      {bars.map((bar, idx) => {
        const ni = nodeById.get(bar.node_i)
        const nj = nodeById.get(bar.node_j)
        if (!ni || !nj) return null
        const ri = nodeResultById.get(bar.node_i)
        const rj = nodeResultById.get(bar.node_j)
        if (!ri || !rj) return null

        const defIx = ni.x + ri.ux * scaleFactor
        const defIy = ni.y + ri.uy * scaleFactor
        const defJx = nj.x + rj.ux * scaleFactor
        const defJy = nj.y + rj.uy * scaleFactor

        const pi = worldToSvg(defIx, defIy, bbox, dims)
        const pj = worldToSvg(defJx, defJy, bbox, dims)
        const animDelay = `${idx * 0.08}s`

        return (
          <line
            key={`def-${bar.id}`}
            data-diagram
            x1={pi.sx} y1={pi.sy} x2={pj.sx} y2={pj.sy}
            stroke="var(--primary)"
            strokeWidth={2}
            opacity={0.7}
            style={{ animation: `drawDiagram 0.8s ease-out ${animDelay} forwards` }}
          />
        )
      })}
    </g>
  )
}

interface FrameDiagramsProps {
  nodes: FrameNode[]
  bars: FrameBar[]
  result: FrameResult
  activeTab: DiagramTab
  dims?: SvgDims
}

export function FrameDiagrams({ nodes, bars, result, activeTab, dims = SVG_DIMS }: FrameDiagramsProps) {
  const nodeById = new Map(nodes.map(n => [n.id, n]))
  const bbox = computeBBox(nodes)

  if (activeTab === 'deformed') {
    return <DeformedShape nodes={nodes} bars={bars} result={result} bbox={bbox} dims={dims} />
  }

  const maxValue = activeTab === 'M' ? result.max_M
    : activeTab === 'V' ? result.max_V
    : result.max_N

  const scale = computeScale(bars, nodes, maxValue, dims)

  return (
    <g data-testid="frame-diagrams">
      {result.bar_diagrams.map((bd, idx) => {
        const bar = bars.find(b => b.id === bd.bar_id)
        if (!bar) return null
        const ni = nodeById.get(bar.node_i)
        const nj = nodeById.get(bar.node_j)
        if (!ni || !nj) return null

        const values = activeTab === 'M' ? bd.M
          : activeTab === 'V' ? bd.V
          : bd.N

        return (
          <SingleBarDiagram
            key={bd.bar_id}
            bar={bar}
            values={values}
            nodeI={ni}
            nodeJ={nj}
            scale={scale}
            barIndex={idx}
            bbox={bbox}
            dims={dims}
          />
        )
      })}
    </g>
  )
}
