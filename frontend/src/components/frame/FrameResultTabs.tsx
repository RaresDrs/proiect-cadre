import { Button } from '@/components/ui/button'
import { useLang } from '@/hooks/useLang'
import type { DiagramTab } from './FrameDiagrams'

const TABS: Array<{ id: DiagramTab; i18nKey: string }> = [
  { id: 'M', i18nKey: 'frame.result.tab.M' },
  { id: 'V', i18nKey: 'frame.result.tab.V' },
  { id: 'N', i18nKey: 'frame.result.tab.N' },
  { id: 'deformed', i18nKey: 'frame.result.tab.deformed' },
]

interface FrameResultTabsProps {
  activeTab: DiagramTab
  onTabChange: (tab: DiagramTab) => void
  onExportPdf: () => void
  onCopyLink: () => void
  copySuccess: boolean
}

export function FrameResultTabs({
  activeTab,
  onTabChange,
  onExportPdf,
  onCopyLink,
  copySuccess,
}: FrameResultTabsProps) {
  const { t } = useLang()

  return (
    <div
      role="tablist"
      aria-label="Result diagram type"
      className="flex items-center gap-1 px-4 py-2
                 bg-[var(--card)] border-t border-[var(--border)]
                 flex-wrap"
    >
      {TABS.map(({ id, i18nKey }) => (
        <Button
          key={id}
          role="tab"
          variant={activeTab === id ? 'default' : 'outline'}
          size="sm"
          onClick={() => onTabChange(id)}
          aria-selected={activeTab === id}
          className="min-w-[48px]"
        >
          {t(i18nKey)}
        </Button>
      ))}

      <div className="ml-auto flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={onCopyLink}
          aria-label={t('frame.action.copy_link')}
        >
          {copySuccess ? t('frame.copy_success') : t('frame.action.copy_link')}
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={onExportPdf}
          aria-label={t('frame.action.export_pdf')}
        >
          {t('frame.action.export_pdf')}
        </Button>
      </div>
    </div>
  )
}

/**
 * Export PDF using jsPDF + html2canvas (dynamic import — no eager bundle cost).
 * Captures the element with id="frame-results-capture".
 */
export async function exportFramePdf(title: string): Promise<void> {
  const [{ default: jsPDF }, { default: html2canvas }] = await Promise.all([
    import('jspdf'),
    import('html2canvas'),
  ])

  const element = document.getElementById('frame-results-capture')
  if (!element) return

  const canvas = await html2canvas(element, { scale: 2, useCORS: true })
  const imgData = canvas.toDataURL('image/png')

  const pdf = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' })
  const pdfWidth = pdf.internal.pageSize.getWidth()
  const pdfHeight = (canvas.height * pdfWidth) / canvas.width

  pdf.setFontSize(16)
  pdf.text(title, 14, 14)
  pdf.addImage(imgData, 'PNG', 0, 20, pdfWidth, pdfHeight)
  pdf.save('cadru-2d.pdf')
}
