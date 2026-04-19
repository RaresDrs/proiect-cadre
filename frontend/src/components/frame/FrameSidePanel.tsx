import { Separator } from '@/components/ui/separator'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useLang } from '@/hooks/useLang'
import type { FrameNode, FrameBar, NodeLoad, BarLoad, ConstraintType } from '@/types/api'

interface NodePanelProps {
  node: FrameNode
  load: NodeLoad
  onNodeChange: (updates: Partial<FrameNode>) => void
  onLoadChange: (updates: Partial<NodeLoad>) => void
}

function NodePanel({ node, load, onNodeChange, onLoadChange }: NodePanelProps) {
  const { t } = useLang()
  return (
    <div className="space-y-4 p-4">
      <h3 className="text-[20px] font-semibold text-[var(--foreground)]">
        {t('frame.node.heading')}
      </h3>
      <Separator />

      <div className="space-y-2">
        <div>
          <Label htmlFor="node-x" className="text-[12px]">{t('frame.node.x')}</Label>
          <Input
            id="node-x"
            type="number"
            step="0.1"
            value={node.x}
            onChange={e => onNodeChange({ x: parseFloat(e.target.value) || 0 })}
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor="node-y" className="text-[12px]">{t('frame.node.y')}</Label>
          <Input
            id="node-y"
            type="number"
            step="0.1"
            value={node.y}
            onChange={e => onNodeChange({ y: parseFloat(e.target.value) || 0 })}
            className="mt-1"
          />
        </div>
      </div>

      <div>
        <Label htmlFor="node-constraint" className="text-[12px]">{t('frame.node.constraint')}</Label>
        <Select
          value={node.constraint}
          onValueChange={v => onNodeChange({ constraint: v as ConstraintType })}
        >
          <SelectTrigger id="node-constraint" className="mt-1">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="free">{t('frame.node.constraint.free')}</SelectItem>
            <SelectItem value="pin">{t('frame.node.constraint.pin')}</SelectItem>
            <SelectItem value="roller">{t('frame.node.constraint.roller')}</SelectItem>
            <SelectItem value="fixed">{t('frame.node.constraint.fixed')}</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Separator />

      <div className="space-y-2">
        <div>
          <Label htmlFor="node-fx" className="text-[12px]">{t('frame.node.fx')}</Label>
          <Input
            id="node-fx"
            type="number"
            step="0.1"
            value={load.Fx}
            onChange={e => onLoadChange({ Fx: parseFloat(e.target.value) || 0 })}
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor="node-fy" className="text-[12px]">{t('frame.node.fy')}</Label>
          <Input
            id="node-fy"
            type="number"
            step="0.1"
            value={load.Fy}
            onChange={e => onLoadChange({ Fy: parseFloat(e.target.value) || 0 })}
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor="node-mz" className="text-[12px]">{t('frame.node.mz')}</Label>
          <Input
            id="node-mz"
            type="number"
            step="0.1"
            value={load.Mz}
            onChange={e => onLoadChange({ Mz: parseFloat(e.target.value) || 0 })}
            className="mt-1"
          />
        </div>
      </div>
    </div>
  )
}

interface BarPanelProps {
  bar: FrameBar
  load: BarLoad
  onBarChange: (updates: Partial<FrameBar>) => void
  onBarLoadChange: (updates: Partial<BarLoad>) => void
}

function BarPanel({ bar, load, onBarChange, onBarLoadChange }: BarPanelProps) {
  const { t } = useLang()
  return (
    <div className="space-y-4 p-4">
      <h3 className="text-[20px] font-semibold text-[var(--foreground)]">
        {t('frame.bar.heading')}
      </h3>
      <Separator />
      <div className="space-y-2">
        <div>
          <Label htmlFor="bar-ei" className="text-[12px]">{t('frame.bar.ei')}</Label>
          <Input
            id="bar-ei"
            type="number"
            step="100"
            value={bar.EI}
            onChange={e => onBarChange({ EI: parseFloat(e.target.value) || 21000 })}
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor="bar-ea" className="text-[12px]">{t('frame.bar.ea')}</Label>
          <Input
            id="bar-ea"
            type="number"
            step="10000"
            value={bar.EA}
            onChange={e => onBarChange({ EA: parseFloat(e.target.value) || 2100000 })}
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor="bar-q" className="text-[12px]">{t('frame.bar.q')}</Label>
          <Input
            id="bar-q"
            type="number"
            step="0.1"
            value={load.q}
            onChange={e => onBarLoadChange({ q: parseFloat(e.target.value) || 0 })}
            className="mt-1"
          />
        </div>
      </div>
    </div>
  )
}

const EMPTY_NODE_LOAD: Omit<NodeLoad, 'node_id'> = { Fx: 0, Fy: 0, Mz: 0 }
const EMPTY_BAR_LOAD: Omit<BarLoad, 'bar_id'> = { q: 0, q_start: 0, q_end: 1 }

interface FrameSidePanelProps {
  selectedId: string | null
  selectedType: 'node' | 'bar' | null
  nodes: FrameNode[]
  bars: FrameBar[]
  nodeLoads: NodeLoad[]
  barLoads: BarLoad[]
  onNodeChange: (id: string, updates: Partial<FrameNode>) => void
  onNodeLoadChange: (nodeId: string, updates: Partial<Omit<NodeLoad, 'node_id'>>) => void
  onBarChange: (id: string, updates: Partial<FrameBar>) => void
  onBarLoadChange: (barId: string, updates: Partial<Omit<BarLoad, 'bar_id'>>) => void
}

export function FrameSidePanel({
  selectedId,
  selectedType,
  nodes,
  bars,
  nodeLoads,
  barLoads,
  onNodeChange,
  onNodeLoadChange,
  onBarChange,
  onBarLoadChange,
}: FrameSidePanelProps) {
  if (!selectedId || !selectedType) return null

  if (selectedType === 'node') {
    const node = nodes.find(n => n.id === selectedId)
    if (!node) return null
    const load = nodeLoads.find(l => l.node_id === selectedId) ?? { node_id: selectedId, ...EMPTY_NODE_LOAD }
    return (
      <aside
        className="w-[280px] shrink-0 border-l border-[var(--border)]
                   bg-[var(--card)] overflow-y-auto sticky top-28"
        aria-label="Node properties"
      >
        <NodePanel
          node={node}
          load={load}
          onNodeChange={updates => onNodeChange(selectedId, updates)}
          onLoadChange={updates => onNodeLoadChange(selectedId, updates)}
        />
      </aside>
    )
  }

  if (selectedType === 'bar') {
    const bar = bars.find(b => b.id === selectedId)
    if (!bar) return null
    const load = barLoads.find(l => l.bar_id === selectedId) ?? { bar_id: selectedId, ...EMPTY_BAR_LOAD }
    return (
      <aside
        className="w-[280px] shrink-0 border-l border-[var(--border)]
                   bg-[var(--card)] overflow-y-auto sticky top-28"
        aria-label="Bar properties"
      >
        <BarPanel
          bar={bar}
          load={load}
          onBarChange={updates => onBarChange(selectedId, updates)}
          onBarLoadChange={updates => onBarLoadChange(selectedId, updates)}
        />
      </aside>
    )
  }

  return null
}
