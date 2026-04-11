import { useState } from 'react'
import { Collapsible } from '@base-ui/react/collapsible'
import { ChevronDown } from 'lucide-react'
import { useLang } from '@/hooks/useLang'

interface FAQItemProps {
  question: string
  answer: string
  isOpen: boolean
  onToggle: () => void
}

function FAQItem({ question, answer, isOpen, onToggle }: FAQItemProps) {
  return (
    <Collapsible.Root open={isOpen} onOpenChange={onToggle}>
      <Collapsible.Trigger
        aria-expanded={isOpen}
        className="w-full flex items-center justify-between py-5 text-left
                   text-[var(--brand-text)] font-medium text-base
                   border-b border-[var(--brand-border)] cursor-pointer
                   hover:text-[var(--brand-accent)] transition-colors duration-150
                   focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--brand-accent)]"
      >
        <span>{question}</span>
        <ChevronDown
          className={[
            'w-5 h-5 text-[var(--brand-muted)] flex-shrink-0 transition-transform duration-200',
            isOpen ? 'rotate-180' : '',
          ].join(' ')}
          aria-hidden="true"
        />
      </Collapsible.Trigger>
      <Collapsible.Panel className="overflow-hidden">
        <p className="py-4 text-[var(--brand-muted)] leading-relaxed">{answer}</p>
      </Collapsible.Panel>
    </Collapsible.Root>
  )
}

export function FAQSection() {
  const { t } = useLang()
  const [openItem, setOpenItem] = useState<number | null>(null)

  const faqs = [
    { q: t('faq.q1'), a: t('faq.a1') },
    { q: t('faq.q2'), a: t('faq.a2') },
    { q: t('faq.q3'), a: t('faq.a3') },
    { q: t('faq.q4'), a: t('faq.a4') },
  ]

  return (
    <section
      id="faq"
      className="py-[var(--space-3xl)] bg-[var(--brand-bg)]"
    >
      <div className="max-w-[800px] mx-auto px-6">
        <h2 className="text-[clamp(28px,4vw,40px)] font-bold text-[var(--brand-text)] text-center mb-12">
          {t('faq.heading')}
        </h2>
        <div>
          {faqs.map((faq, index) => (
            <FAQItem
              key={index}
              question={faq.q}
              answer={faq.a}
              isOpen={openItem === index}
              onToggle={() => setOpenItem(openItem === index ? null : index)}
            />
          ))}
        </div>
      </div>
    </section>
  )
}
