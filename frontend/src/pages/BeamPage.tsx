import { useLang } from '@/hooks/useLang'

export default function BeamPage() {
  const { t } = useLang()
  return (
    <div className="min-h-screen pt-16">
      <div className="max-w-[1200px] mx-auto px-6 py-8">
        <h1 className="text-3xl font-bold text-[var(--brand-text)] mb-2">
          {t('beam.page.title')}
        </h1>
        <p className="text-[var(--brand-muted)] mb-8">{t('beam.page.subtitle')}</p>
        {/* BeamInputForm and BeamDiagrams wired in 02-02 */}
      </div>
    </div>
  )
}
