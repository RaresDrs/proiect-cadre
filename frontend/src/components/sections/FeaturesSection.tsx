import { Ruler, FileText, Smartphone } from 'lucide-react'
import { useLang } from '@/hooks/useLang'
import { useInView } from '@/hooks/useInView'
import type { LucideIcon } from 'lucide-react'

interface FeatureCardProps {
  icon: LucideIcon
  title: string
  body: string
  delay: string
}

function FeatureCard({ icon: Icon, title, body, delay }: FeatureCardProps) {
  const { ref, isInView } = useInView()
  return (
    <div
      ref={ref as React.RefObject<HTMLDivElement>}
      className={[
        'bg-[var(--brand-card)] border border-[var(--brand-border)] rounded-2xl p-8',
        'transition-all duration-500',
        isInView ? 'animate-fade-in-up opacity-100' : 'opacity-0 translate-y-4',
      ].join(' ')}
      style={{ animationDelay: delay }}
    >
      <div className="mb-4 inline-flex items-center justify-center w-12 h-12 rounded-xl bg-[var(--brand-accent)]/10">
        <Icon className="w-6 h-6 text-[var(--brand-accent)]" />
      </div>
      <h3 className="text-lg font-semibold text-[var(--brand-text)] mb-2">{title}</h3>
      <p className="text-[var(--brand-muted)] leading-relaxed">{body}</p>
    </div>
  )
}

export function FeaturesSection() {
  const { t } = useLang()

  const features = [
    { icon: Ruler, titleKey: 'features.1.title', bodyKey: 'features.1.body', delay: '0ms' },
    { icon: FileText, titleKey: 'features.2.title', bodyKey: 'features.2.body', delay: '100ms' },
    { icon: Smartphone, titleKey: 'features.3.title', bodyKey: 'features.3.body', delay: '200ms' },
  ]

  return (
    <section
      id="features"
      className="py-[var(--space-3xl)] bg-[var(--brand-bg)]"
    >
      <div className="max-w-[1200px] mx-auto px-6">
        <h2 className="text-[clamp(28px,4vw,40px)] font-bold text-[var(--brand-text)] text-center mb-12">
          {t('features.heading')}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map(({ icon, titleKey, bodyKey, delay }) => (
            <FeatureCard
              key={titleKey}
              icon={icon}
              title={t(titleKey)}
              body={t(bodyKey)}
              delay={delay}
            />
          ))}
        </div>
      </div>
    </section>
  )
}
