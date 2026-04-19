// REQ-03-12, REQ-03-13
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { FrameCanvas } from '../FrameCanvas'
import type { FrameNode, FrameBar } from '@/types/api'

const EMPTY_PROPS = {
  mode: 'add_node' as const,
  onModeChange: vi.fn(),
  nodes: [] as FrameNode[],
  bars: [] as FrameBar[],
  nodeLoads: [],
  barLoads: [],
  onNodesChange: vi.fn(),
  onBarsChange: vi.fn(),
  onNodeLoadsChange: vi.fn(),
  onBarLoadsChange: vi.fn(),
}

describe('FrameCanvas — REQ-03-12, REQ-03-13', () => {
  it('renders SVG canvas element', () => {
    render(<MemoryRouter><FrameCanvas {...EMPTY_PROPS} /></MemoryRouter>)
    expect(screen.getByTestId('frame-canvas-svg')).toBeInTheDocument()
  })

  it('shows empty state text when no nodes', () => {
    render(<MemoryRouter><FrameCanvas {...EMPTY_PROPS} /></MemoryRouter>)
    expect(screen.getByTestId('frame-canvas-svg')).toBeInTheDocument()
    // Empty state is rendered inside SVG as <text> element
  })

  it('calls onNodesChange when canvas is clicked in add_node mode', () => {
    const onNodesChange = vi.fn()
    render(
      <MemoryRouter>
        <FrameCanvas {...EMPTY_PROPS} onNodesChange={onNodesChange} />
      </MemoryRouter>
    )
    const svg = screen.getByTestId('frame-canvas-svg')
    fireEvent.click(svg, { clientX: 300, clientY: 200 })
    expect(onNodesChange).toHaveBeenCalledTimes(1)
    expect(onNodesChange).toHaveBeenCalledWith(expect.arrayContaining([
      expect.objectContaining({ constraint: 'free' })
    ]))
  })

  it('renders bar elements when nodes and bars provided', () => {
    const nodes: FrameNode[] = [
      { id: 'n1', x: 0, y: 0, constraint: 'pin' },
      { id: 'n2', x: 4, y: 0, constraint: 'roller' },
    ]
    const bars: FrameBar[] = [
      { id: 'b1', node_i: 'n1', node_j: 'n2', EI: 21000, EA: 2100000 },
    ]
    render(
      <MemoryRouter>
        <FrameCanvas {...EMPTY_PROPS} nodes={nodes} bars={bars} />
      </MemoryRouter>
    )
    expect(screen.getByTestId('node-n1')).toBeInTheDocument()
    expect(screen.getByTestId('node-n2')).toBeInTheDocument()
    expect(screen.getByTestId('bar-b1')).toBeInTheDocument()
  })
})
