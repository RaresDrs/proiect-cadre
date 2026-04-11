import { Lock } from 'lucide-react'
import { useLang } from '@/hooks/useLang'
import { EmailCapture } from './EmailCapture'

export function PricingSection() {
  const { t } = useLang()

  return (
    <section
      id="pricing"
      className="py-[var(--space-3xl)] bg-[var(--brand-bg)]"
    >
      <div className="max-w-[1200px] mx-auto px-6">
        <h2 className="text-[clamp(28px,4vw,40px)] font-bold text-[var(--brand-text)] text-center mb-12">
          {t('pricing.heading')}
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {/* Free tier — fully visible */}
          <div
            className="bg-[var(--brand-card)] border-2 border-[var(--brand-accent)] rounded-2xl p-8
                       relative flex flex-col"
          >
            <div className="mb-6">
              <h3 className="text-xl font-bold text-[var(--brand-text)] mb-1">
                {t('pricing.free.name')}
              </h3>
              <p className="text-sm text-[var(--brand-muted)]">
                {t('pricing.free.tagline')}
              </p>
            </div>
            <div className="text-4xl font-bold text-[var(--brand-text)] mb-6">
              €0
              <span className="text-base font-normal text-[var(--brand-muted)]">/lună</span>
            </div>
            <ul className="space-y-3 text-sm text-[var(--brand-muted)] flex-1">
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--brand-accent)] shrink-0" />
                Analiză bare 2D nelimitată
              </li>
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--brand-accent)] shrink-0" />
                Export PDF
              </li>
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--brand-accent)] shrink-0" />
                Dark mode & PWA
              </li>
            </ul>
          </div>

          {/* Pro tier — blurred with lock */}
          <div
            className="bg-[var(--brand-card)] border border-[var(--brand-border)] rounded-2xl p-8
                       relative flex flex-col overflow-hidden"
          >
            {/* Locked badge */}
            <div
              className="absolute top-3 right-3 flex items-center gap-1 px-2 py-1 rounded-full
                         bg-[var(--brand-muted)]/10 text-[var(--brand-muted)] text-xs font-medium"
            >
              <Lock className="w-3 h-3" aria-hidden="true" />
              {t('pricing.badge')}
            </div>
            <div className="blur-sm select-none pointer-events-none">
              <div className="mb-6">
                <h3 className="text-xl font-bold text-[var(--brand-text)] mb-1">Pro</h3>
                <p className="text-sm text-[var(--brand-muted)]">{t('pricing.locked')}</p>
              </div>
              <div className="text-4xl font-bold text-[var(--brand-text)] mb-6">
                €X<span className="text-base font-normal text-[var(--brand-muted)]">/lună</span>
              </div>
              <ul className="space-y-3 text-sm text-[var(--brand-muted)]">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[var(--brand-muted)] shrink-0" />
                  Tot din Free, plus...
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[var(--brand-muted)] shrink-0" />
                  Cadre 2D avansate
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[var(--brand-muted)] shrink-0" />
                  Suport prioritar
                </li>
              </ul>
            </div>
          </div>

          {/* Enterprise tier — blurred with lock */}
          <div
            className="bg-[var(--brand-card)] border border-[var(--brand-border)] rounded-2xl p-8
                       relative flex flex-col overflow-hidden"
          >
            {/* Locked badge */}
            <div
              className="absolute top-3 right-3 flex items-center gap-1 px-2 py-1 rounded-full
                         bg-[var(--brand-muted)]/10 text-[var(--brand-muted)] text-xs font-medium"
            >
              <Lock className="w-3 h-3" aria-hidden="true" />
              {t('pricing.badge')}
            </div>
            <div className="blur-sm select-none pointer-events-none">
              <div className="mb-6">
                <h3 className="text-xl font-bold text-[var(--brand-text)] mb-1">Enterprise</h3>
                <p className="text-sm text-[var(--brand-muted)]">{t('pricing.locked')}</p>
              </div>
              <div className="text-4xl font-bold text-[var(--brand-text)] mb-6">
                Custom
              </div>
              <ul className="space-y-3 text-sm text-[var(--brand-muted)]">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[var(--brand-muted)] shrink-0" />
                  Tot din Pro, plus...
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[var(--brand-muted)] shrink-0" />
                  Licență organizație
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[var(--brand-muted)] shrink-0" />
                  SLA dedicat
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Email capture below pricing tiers */}
        <div className="max-w-[560px] mx-auto">
          <EmailCapture />
        </div>
      </div>
    </section>
  )
}
