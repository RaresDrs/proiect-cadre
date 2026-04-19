import { useRef, useState, useCallback, useEffect } from 'react'
import {
  worldToSvg, svgToWorld, snapToGrid, hitTestNode, hitTestBar, computeBBox,
  type BBox, type SvgDims,
} from '@/lib/frameCanvas'
import type { FrameNode, FrameBar, NodeLoad, BarLoad, ConstraintType } from '@/types/api'
import type { EditorMode } from './FrameToolbar'
import { FrameSidePanel } from './FrameSidePanel'

const SVG_DIMS: SvgDims = { width: 600, height: 400, margin: 40 }
const DEFAULT_EI = 21000
const DEFAULT_EA = 2100000
const GRID_SIZE = 0.5

function generateId(): string {
  return Math.random().toString(36).slice(2, 9)
}

function ConstraintIcon({ node, bbox, dims }: { node: FrameNode; bbox: BBox; dims: SvgDims }) {
  const { sx, sy } = worldToSvg(node.x, node.y, bbox, dims)
  const c = 'var(--foreground)'

  if (node.constraint === 'pin') {
    return (
      <g>
        <polygon
          points={`${sx},${sy} ${sx - 10},${sy + 18} ${sx + 10},${sy + 18}`}
          fill={c} opacity={0.85}
        />
        <line x1={sx - 14} y1={sy + 20} x2={sx + 14} y2={sy + 20} stroke={c} strokeWidth={2} />
      </g>
    )
  }
  if (node.constraint === 'roller') {
    return (
      <g>
        <polygon
          points={`${sx},${sy} ${sx - 10},${sy + 16} ${sx + 10},${sy + 16}`}
          fill={c} opacity={0.85}
        />
        <circle cx={sx} cy={sy + 22} r={4} fill="none" stroke={c} strokeWidth={1.5} />
      </g>
    )
  }
  if (node.constraint === 'fixed') {
    return (
      <g>
        <rect x={sx - 10} y={sy - 16} width={10} height={32} fill={c} opacity={0.8} />
        {[-10, -2, 6, 14].map((dy, i) => (
          <line key={i} x1={sx - 10} y1={sy + dy} x2={sx - 20} y2={sy + dy + 8} stroke={c} strokeWidth={1.5} />
        ))}
      </g>
    )
  }
  return null
}

function NodeLoadArrow({ load, node, bbox, dims }: { load: NodeLoad; node: FrameNode; bbox: BBox; dims: SvgDims }) {
  const { sx, sy } = worldToSvg(node.x, node.y, bbox, dims)
  const color = '#3b82f6'
  const arrowLen = 35
  const elements: React.ReactNode[] = []

  if (Math.abs(load.Fy) > 1e-9) {
    const dir = load.Fy > 0 ? -1 : 1
    elements.push(
      <g key="fy">
        <line x1={sx} y1={sy + dir * arrowLen} x2={sx} y2={sy} stroke={color} strokeWidth={2} />
        <polygon points={`${sx},${sy} ${sx - 5},${sy + dir * 10} ${sx + 5},${sy + dir * 10}`} fill={color} />
      </g>
    )
  }
  if (Math.abs(load.Fx) > 1e-9) {
    const dir = load.Fx > 0 ? 1 : -1
    const x1 = sx - dir * arrowLen
    elements.push(
      <g key="fx">
        <line x1={x1} y1={sy} x2={sx} y2={sy} stroke={color} strokeWidth={2} />
        <polygon points={`${sx},${sy} ${sx - dir * 10},${sy - 5} ${sx - dir * 10},${sy + 5}`} fill={color} />
      </g>
    )
  }
  return <>{elements}</>
}

interface FrameCanvasProps {
  mode: EditorMode
  onModeChange: (mode: EditorMode) => void
  nodes: FrameNode[]
  bars: FrameBar[]
  nodeLoads: NodeLoad[]
  barLoads: BarLoad[]
  onNodesChange: (nodes: FrameNode[]) => void
  onBarsChange: (bars: FrameBar[]) => void
  onNodeLoadsChange: (loads: NodeLoad[]) => void
  onBarLoadsChange: (loads: BarLoad[]) => void
}

export function FrameCanvas({
  mode,
  onModeChange,
  nodes,
  bars,
  nodeLoads,
  barLoads,
  onNodesChange,
  onBarsChange,
  onNodeLoadsChange,
  onBarLoadsChange,
}: FrameCanvasProps) {
  const svgRef = useRef<SVGSVGElement>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [selectedType, setSelectedType] = useState<'node' | 'bar' | null>(null)
  const [pendingBarStart, setPendingBarStart] = useState<string | null>(null)
  const [mousePos, setMousePos] = useState<{ sx: number; sy: number } | null>(null)

  const bbox = computeBBox(nodes)
  const dims = SVG_DIMS

  const getSvgCoords = useCallback((e: React.MouseEvent<SVGSVGElement>) => {
    const svg = svgRef.current
    if (!svg) return null
    const rect = svg.getBoundingClientRect()
    // Guard against zero-size rect in jsdom tests
    const w = rect.width || dims.width
    const h = rect.height || dims.height
    return {
      sx: ((e.clientX - rect.left) / w) * dims.width,
      sy: ((e.clientY - rect.top) / h) * dims.height,
    }
  }, [dims])

  // Keyboard shortcuts: 1/2/3/4 → mode, Escape → cancel/deselect
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if ((e.target as HTMLElement)?.tagName === 'INPUT') return
      const map: Record<string, EditorMode> = {
        '1': 'add_node', '2': 'add_bar', '3': 'select', '4': 'delete',
      }
      if (map[e.key]) {
        onModeChange(map[e.key] as EditorMode)
        setPendingBarStart(null)
        setSelectedId(null)
        setSelectedType(null)
      }
      if (e.key === 'Escape') {
        setPendingBarStart(null)
        setSelectedId(null)
        setSelectedType(null)
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [onModeChange])

  const handleMouseMove = useCallback((e: React.MouseEvent<SVGSVGElement>) => {
    const coords = getSvgCoords(e)
    if (coords) setMousePos(coords)
  }, [getSvgCoords])

  const handleClick = useCallback((e: React.MouseEvent<SVGSVGElement>) => {
    const coords = getSvgCoords(e)
    if (!coords) return
    const { sx, sy } = coords
    const { wx, wy } = svgToWorld(sx, sy, bbox, dims)

    if (mode === 'add_node') {
      const hitNodeId = hitTestNode(sx, sy, nodes, bbox, dims)
      if (hitNodeId) {
        setSelectedId(hitNodeId)
        setSelectedType('node')
        onModeChange('select')
      } else {
        const newNode: FrameNode = {
          id: generateId(),
          x: snapToGrid(wx, GRID_SIZE),
          y: snapToGrid(wy, GRID_SIZE),
          constraint: 'free' as ConstraintType,
        }
        onNodesChange([...nodes, newNode])
      }
      return
    }

    if (mode === 'add_bar') {
      const hitNodeId = hitTestNode(sx, sy, nodes, bbox, dims)
      if (!hitNodeId) return

      if (!pendingBarStart) {
        setPendingBarStart(hitNodeId)
      } else if (hitNodeId === pendingBarStart) {
        setPendingBarStart(null)
      } else {
        const newBar: FrameBar = {
          id: generateId(),
          node_i: pendingBarStart,
          node_j: hitNodeId,
          EI: DEFAULT_EI,
          EA: DEFAULT_EA,
        }
        onBarsChange([...bars, newBar])
        setPendingBarStart(null)
      }
      return
    }

    if (mode === 'select') {
      const hitNodeId = hitTestNode(sx, sy, nodes, bbox, dims)
      if (hitNodeId) {
        setSelectedId(hitNodeId)
        setSelectedType('node')
        return
      }
      const hitBarId = hitTestBar(sx, sy, bars, nodes, bbox, dims)
      if (hitBarId) {
        setSelectedId(hitBarId)
        setSelectedType('bar')
        return
      }
      setSelectedId(null)
      setSelectedType(null)
      return
    }

    if (mode === 'delete') {
      const hitNodeId = hitTestNode(sx, sy, nodes, bbox, dims)
      if (hitNodeId) {
        onNodesChange(nodes.filter(n => n.id !== hitNodeId))
        onBarsChange(bars.filter(b => b.node_i !== hitNodeId && b.node_j !== hitNodeId))
        onNodeLoadsChange(nodeLoads.filter(l => l.node_id !== hitNodeId))
        if (selectedId === hitNodeId) { setSelectedId(null); setSelectedType(null) }
        return
      }
      const hitBarId = hitTestBar(sx, sy, bars, nodes, bbox, dims)
      if (hitBarId) {
        onBarsChange(bars.filter(b => b.id !== hitBarId))
        onBarLoadsChange(barLoads.filter(l => l.bar_id !== hitBarId))
        if (selectedId === hitBarId) { setSelectedId(null); setSelectedType(null) }
        return
      }
    }
  }, [mode, nodes, bars, nodeLoads, barLoads, pendingBarStart, bbox, dims, selectedId,
    getSvgCoords, onNodesChange, onBarsChange, onNodeLoadsChange, onBarLoadsChange, onModeChange])

  // Grid lines
  const gridLines: React.ReactNode[] = []
  const gridStep = GRID_SIZE
  const xStart = Math.ceil(bbox.minX / gridStep) * gridStep
  const xEnd = Math.floor(bbox.maxX / gridStep) * gridStep
  const yStart = Math.ceil(bbox.minY / gridStep) * gridStep
  const yEnd = Math.floor(bbox.maxY / gridStep) * gridStep
  for (let gx = xStart; gx <= xEnd + 1e-9; gx += gridStep) {
    const { sx: x1, sy: y1 } = worldToSvg(gx, bbox.minY, bbox, dims)
    const { sy: y2 } = worldToSvg(gx, bbox.maxY, bbox, dims)
    gridLines.push(
      <line key={`vg${gx}`} x1={x1} y1={y1} x2={x1} y2={y2}
        stroke="var(--border)" strokeOpacity="0.4" strokeWidth="0.5" />
    )
  }
  for (let gy = yStart; gy <= yEnd + 1e-9; gy += gridStep) {
    const { sx: x1, sy: y1 } = worldToSvg(bbox.minX, gy, bbox, dims)
    const { sx: x2 } = worldToSvg(bbox.maxX, gy, bbox, dims)
    gridLines.push(
      <line key={`hg${gy}`} x1={x1} y1={y1} x2={x2} y2={y1}
        stroke="var(--border)" strokeOpacity="0.4" strokeWidth="0.5" />
    )
  }

  // Pending bar preview line
  let pendingLine: React.ReactNode = null
  if (pendingBarStart && mousePos) {
    const startNode = nodes.find(n => n.id === pendingBarStart)
    if (startNode) {
      const { sx: x1, sy: y1 } = worldToSvg(startNode.x, startNode.y, bbox, dims)
      pendingLine = (
        <line
          x1={x1} y1={y1} x2={mousePos.sx} y2={mousePos.sy}
          stroke="var(--primary)" strokeWidth={1.5} strokeDasharray="6 4" opacity={0.7}
        />
      )
    }
  }

  const nodeById = new Map(nodes.map(n => [n.id, n]))

  return (
    <div className="flex flex-1 min-h-0">
      <div className="flex-1 min-h-[400px]" data-testid="frame-canvas-container">
        <svg
          ref={svgRef}
          viewBox={`0 0 ${dims.width} ${dims.height}`}
          width="100%"
          height="100%"
          className="rounded border border-[var(--border)] bg-[var(--background)] cursor-crosshair"
          style={{ minHeight: '400px' }}
          onClick={handleClick}
          onMouseMove={handleMouseMove}
          data-testid="frame-canvas-svg"
          aria-label="Frame editor canvas"
        >
          {gridLines}

          {bars.map(bar => {
            const ni = nodeById.get(bar.node_i)
            const nj = nodeById.get(bar.node_j)
            if (!ni || !nj) return null
            const pi = worldToSvg(ni.x, ni.y, bbox, dims)
            const pj = worldToSvg(nj.x, nj.y, bbox, dims)
            const isSelected = selectedId === bar.id
            return (
              <line
                key={bar.id}
                data-testid={`bar-${bar.id}`}
                x1={pi.sx} y1={pi.sy} x2={pj.sx} y2={pj.sy}
                stroke={isSelected ? 'var(--primary)' : 'var(--foreground)'}
                strokeOpacity={isSelected ? 1.0 : 0.8}
                strokeWidth={isSelected ? 3 : 2}
                strokeLinecap="round"
              />
            )
          })}

          {pendingLine}

          {nodes.map(node =>
            node.constraint !== 'free'
              ? <ConstraintIcon key={`c${node.id}`} node={node} bbox={bbox} dims={dims} />
              : null
          )}

          {nodeLoads.map(load => {
            const node = nodeById.get(load.node_id)
            if (!node) return null
            return <NodeLoadArrow key={`la${load.node_id}`} load={load} node={node} bbox={bbox} dims={dims} />
          })}

          {nodes.map(node => {
            const { sx, sy } = worldToSvg(node.x, node.y, bbox, dims)
            const isSelected = selectedId === node.id
            const isPendingStart = pendingBarStart === node.id
            return (
              <circle
                key={node.id}
                data-testid={`node-${node.id}`}
                cx={sx} cy={sy}
                r={isSelected ? 8 : 6}
                fill={isSelected || isPendingStart ? 'var(--primary)' : 'var(--foreground)'}
                stroke={isPendingStart ? 'var(--primary)' : 'none'}
                strokeWidth={isPendingStart ? 3 : 0}
              />
            )
          })}

          {nodes.length === 0 && (
            <text
              x={dims.width / 2} y={dims.height / 2}
              textAnchor="middle" dominantBaseline="middle"
              fontSize={14} fill="var(--muted-foreground)"
            >
              Click pe canvas pentru a adăuga un nod
            </text>
          )}
        </svg>
      </div>

      <FrameSidePanel
        selectedId={selectedId}
        selectedType={selectedType}
        nodes={nodes}
        bars={bars}
        nodeLoads={nodeLoads}
        barLoads={barLoads}
        onNodeChange={(id, updates) => onNodesChange(nodes.map(n => n.id === id ? { ...n, ...updates } : n))}
        onNodeLoadChange={(nodeId, updates) => {
          const existing = nodeLoads.find(l => l.node_id === nodeId)
          if (existing) {
            onNodeLoadsChange(nodeLoads.map(l => l.node_id === nodeId ? { ...l, ...updates } : l))
          } else {
            onNodeLoadsChange([...nodeLoads, { node_id: nodeId, Fx: 0, Fy: 0, Mz: 0, ...updates }])
          }
        }}
        onBarChange={(id, updates) => onBarsChange(bars.map(b => b.id === id ? { ...b, ...updates } : b))}
        onBarLoadChange={(barId, updates) => {
          const existing = barLoads.find(l => l.bar_id === barId)
          if (existing) {
            onBarLoadsChange(barLoads.map(l => l.bar_id === barId ? { ...l, ...updates } : l))
          } else {
            onBarLoadsChange([...barLoads, { bar_id: barId, q: 0, q_start: 0, q_end: 1, ...updates }])
          }
        }}
      />
    </div>
  )
}
