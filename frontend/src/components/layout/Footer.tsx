import { useLang } from '@/hooks/useLang'

export function Footer() {
  const { t } = useLang()

  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <footer className="border-t border-[var(--brand-border)] bg-[var(--brand-bg)]">
      <div className="max-w-[1200px] mx-auto px-6 py-8 flex flex-col sm:flex-row
                      items-center justify-between gap-4">
        <span className="font-bold text-[var(--brand-text)]">StructCalc</span>

        <nav aria-label="Footer navigation" className="flex gap-4">
          {(['features', 'pricing', 'faq'] as const).map((id) => (
            <button
              key={id}
              onClick={() => scrollTo(id)}
              className="text-sm text-[var(--brand-muted)] hover:text-[var(--brand-text)]
                         transition-colors duration-150 cursor-pointer"
            >
              {t(`nav.${id}`)}
            </button>
          ))}
        </nav>

        <p className="text-sm text-[var(--brand-muted)]">{t('footer.copyright')}</p>
      </div>
    </footer>
  )
}
