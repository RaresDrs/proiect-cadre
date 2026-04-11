import { Button } from '@/components/ui/button'
import { useLang } from '@/hooks/useLang'

export function CTASection() {
  const { t } = useLang()

  return (
    <section
      id="cta"
      className="py-[var(--space-3xl)] bg-[var(--brand-accent)]"
    >
      <div className="max-w-[800px] mx-auto px-6 text-center">
        <h2 className="text-[clamp(28px,4vw,40px)] font-bold text-white mb-4">
          {t('cta.heading')}
        </h2>
        <p className="text-white/80 text-lg mb-8 max-w-[560px] mx-auto">
          {t('cta.body')}
        </p>
        <Button
          size="lg"
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          className="bg-white text-[var(--brand-accent)] hover:bg-white/90
                     transition-colors duration-150 min-h-[44px] px-8 font-semibold"
        >
          {t('cta.button')}
        </Button>
      </div>
    </section>
  )
}
