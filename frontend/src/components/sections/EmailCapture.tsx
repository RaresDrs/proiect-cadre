import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { useLang } from '@/hooks/useLang'

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function EmailCapture() {
  const { t } = useLang()
  const [email, setEmail] = useState('')
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle')

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (!email || !EMAIL_REGEX.test(email)) {
      setStatus('error')
      return
    }
    localStorage.setItem('structcalc-waitlist', email)
    setStatus('success')
  }

  if (status === 'success') {
    return (
      <div
        role="status"
        className="mt-8 p-4 rounded-xl bg-[var(--brand-accent)]/10 border border-[var(--brand-accent)]/30
                   text-[var(--brand-accent)] text-center font-medium"
      >
        {t('email.success')}
      </div>
    )
  }

  return (
    <div className="mt-8">
      <p className="text-sm font-medium text-[var(--brand-muted)] mb-3">
        {t('email.label')}
      </p>
      <form onSubmit={handleSubmit} noValidate className="flex flex-col sm:flex-row gap-3">
        <div className="flex-1">
          <label htmlFor="email-input" className="sr-only">
            {t('email.label')}
          </label>
          <input
            id="email-input"
            type="email"
            role="textbox"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value)
              if (status === 'error') setStatus('idle')
            }}
            placeholder={t('email.placeholder')}
            aria-invalid={status === 'error'}
            aria-describedby={status === 'error' ? 'email-error' : undefined}
            className={[
              'w-full h-11 px-4 rounded-xl text-sm bg-[var(--brand-bg)]',
              'border transition-colors duration-150',
              'text-[var(--brand-text)] placeholder:text-[var(--brand-muted)]',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--brand-accent)] focus-visible:ring-offset-2',
              status === 'error'
                ? 'border-[var(--brand-destructive)]'
                : 'border-[var(--brand-border)] hover:border-[var(--brand-accent)]/50',
            ].join(' ')}
          />
        </div>
        <Button
          type="submit"
          className="bg-[var(--brand-accent)] text-white hover:bg-[var(--brand-accent)]/90
                     transition-colors duration-150 min-h-[44px] px-6 shrink-0"
        >
          {t('email.cta')}
        </Button>
      </form>
      {status === 'error' && (
        <p
          id="email-error"
          role="alert"
          className="mt-2 text-sm text-[var(--brand-destructive)]"
        >
          {t('email.error')}
        </p>
      )}
    </div>
  )
}
