import React, { Suspense } from 'react'
import { Button } from '@/components/ui/button'
import { useLang } from '@/hooks/useLang'
import { StructuralDiagram } from './StructuralDiagram'

// Lazy-load Framer Motion (motion/react) — keeps initial bundle small (D-08)
const MotionHeroContent = React.lazy(() =>
  import('motion/react').then(({ LazyMotion, domAnimation, m }) => ({
    default: function MotionHeroContent({ t }: { t: (k: string) => string }) {
      const scrollTo = (id: string) =>
        document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
      return (
        <LazyMotion features={domAnimation}>
          <m.h1
            className="text-[clamp(36px,5vw,56px)] font-bold leading-[1.1]
                       text-[var(--brand-text)] max-w-[640px]"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ type: 'spring', stiffness: 100, damping: 20, delay: 0 }}
          >
            {t('hero.headline')}
          </m.h1>
          <m.p
            className="mt-4 text-[clamp(18px,2vw,20px)] font-normal leading-[1.5]
                       text-[var(--brand-muted)] max-w-[560px]"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ type: 'spring', stiffness: 100, damping: 20, delay: 0.15 }}
          >
            {t('hero.subheadline')}
          </m.p>
          <m.div
            className="mt-8 flex flex-wrap gap-4"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ type: 'spring', stiffness: 120, damping: 22, delay: 0.3 }}
          >
            <Button
              size="lg"
              onClick={() => scrollTo('cta')}
              className="bg-[var(--brand-accent)] text-white hover:bg-[var(--brand-accent)]/90
                         transition-colors duration-150 min-h-[44px] px-6"
            >
              {t('hero.cta.primary')}
            </Button>
            <Button
              variant="outline"
              size="lg"
              onClick={() => scrollTo('features')}
              className="min-h-[44px] px-6 transition-colors duration-150"
            >
              {t('hero.cta.secondary')}
            </Button>
          </m.div>
        </LazyMotion>
      )
    },
  }))
)

// Static fallback for when motion is loading or prefers-reduced-motion
function StaticHeroContent({ t }: { t: (k: string) => string }) {
  const scrollTo = (id: string) =>
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
  return (
    <>
      <h1
        className="text-[clamp(36px,5vw,56px)] font-bold leading-[1.1]
                   text-[var(--brand-text)] max-w-[640px]"
      >
        {t('hero.headline')}
      </h1>
      <p
        className="mt-4 text-[clamp(18px,2vw,20px)] font-normal leading-[1.5]
                   text-[var(--brand-muted)] max-w-[560px]"
      >
        {t('hero.subheadline')}
      </p>
      <div className="mt-8 flex flex-wrap gap-4">
        <Button
          size="lg"
          onClick={() => scrollTo('cta')}
          className="bg-[var(--brand-accent)] text-white hover:bg-[var(--brand-accent)]/90
                     transition-colors duration-150 min-h-[44px] px-6"
        >
          {t('hero.cta.primary')}
        </Button>
        <Button
          variant="outline"
          size="lg"
          onClick={() => scrollTo('features')}
          className="min-h-[44px] px-6 transition-colors duration-150"
        >
          {t('hero.cta.secondary')}
        </Button>
      </div>
    </>
  )
}

export function HeroSection() {
  const { t } = useLang()
  const prefersReducedMotion =
    typeof window !== 'undefined' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches

  return (
    <section
      id="hero"
      className="min-h-[100svh] lg:min-h-0 lg:py-[64px]
                 bg-[var(--brand-bg)]
                 flex items-center
                 pt-16"
    >
      <div
        className="max-w-[1200px] mx-auto px-6 w-full
                   grid grid-cols-1 lg:grid-cols-2 gap-12 items-center"
      >
        {/* Text content */}
        <div>
          {prefersReducedMotion ? (
            <StaticHeroContent t={t} />
          ) : (
            <Suspense fallback={<StaticHeroContent t={t} />}>
              <MotionHeroContent t={t} />
            </Suspense>
          )}
        </div>

        {/* Structural diagram */}
        <div className="flex justify-center">
          <StructuralDiagram />
        </div>
      </div>
    </section>
  )
}
