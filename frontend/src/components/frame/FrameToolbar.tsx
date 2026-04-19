import { PlusCircle, Minus, MousePointer, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { useLang } from '@/hooks/useLang'

export type EditorMode = 'add_node' | 'add_bar' | 'select' | 'delete'

interface FrameToolbarProps {
  mode: EditorMode
  onModeChange: (mode: EditorMode) => void
  onSolve: () => void
  loading: boolean
  canSolve: boolean
}

const MODES: Array<{
  id: EditorMode
  i18nKey: string
  Icon: React.ComponentType<{ className?: string }>
  shortcut: string
}> = [
  { id: 'add_node', i18nKey: 'frame.toolbar.add_node', Icon: PlusCircle, shortcut: '1' },
  { id: 'add_bar', i18nKey: 'frame.toolbar.add_bar', Icon: Minus, shortcut: '2' },
  { id: 'select', i18nKey: 'frame.toolbar.select', Icon: MousePointer, shortcut: '3' },
  { id: 'delete', i18nKey: 'frame.toolbar.delete', Icon: Trash2, shortcut: '4' },
]

export function FrameToolbar({ mode, onModeChange, onSolve, loading, canSolve }: FrameToolbarProps) {
  const { t } = useLang()

  return (
    <div
      role="toolbar"
      aria-label={t('frame.page.title')}
      className="sticky top-16 z-40 h-12 flex items-center gap-1 px-4
                 bg-[var(--card)] border-b border-[var(--border)]"
    >
      {MODES.map(({ id, i18nKey, Icon, shortcut }) => {
        const isActive = mode === id
        const isDelete = id === 'delete'
        return (
          <Button
            key={id}
            variant={isActive ? 'default' : 'ghost'}
            size="sm"
            onClick={() => onModeChange(id)}
            aria-pressed={isActive}
            aria-label={`${t(i18nKey)} (${shortcut})`}
            className={[
              'flex items-center gap-1.5 text-sm',
              isActive && isDelete
                ? 'bg-[var(--destructive)] text-white hover:bg-[var(--destructive)]/90'
                : '',
              !isActive && isDelete
                ? 'text-[var(--destructive)] hover:text-[var(--destructive)]'
                : '',
            ].join(' ')}
          >
            <Icon className="size-4" />
            <span className="hidden sm:inline">{t(i18nKey)}</span>
            <Badge variant="outline" className="hidden md:inline-flex text-[10px] px-1 py-0 h-4">
              {shortcut}
            </Badge>
          </Button>
        )
      })}

      <Separator orientation="vertical" className="mx-2 h-6" />

      <Button
        size="sm"
        onClick={onSolve}
        disabled={loading || !canSolve}
        className="ml-auto bg-[var(--primary)] text-[var(--primary-foreground)]
                   hover:bg-[var(--primary)]/90 disabled:opacity-50"
        aria-label={t('frame.toolbar.solve')}
      >
        {loading ? '...' : t('frame.toolbar.solve')}
      </Button>
    </div>
  )
}
