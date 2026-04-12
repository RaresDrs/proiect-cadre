import { Sun, Moon } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { useTheme } from '@/hooks/useTheme'
import { useLang } from '@/hooks/useLang'

export function Navbar() {
  const { theme, toggleTheme } = useTheme()
  const { lang, toggleLang, t } = useLang()
  const navigate = useNavigate()

  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <nav
      role="navigation"
      aria-label={lang === 'ro' ? 'Navigare principala' : 'Main navigation'}
      className="fixed top-0 left-0 right-0 z-50 h-16 flex items-center px-6
                 bg-[var(--brand-card)]/80 backdrop-blur-md
                 border-b border-[var(--brand-border)]"
    >
      <div className="flex items-center justify-between w-full max-w-[1200px] mx-auto">
        {/* Logo */}
        <span className="font-bold text-[var(--brand-text)] text-lg select-none">
          {t('nav.logo')}
        </span>

        {/* Nav links — hidden below 400px */}
        <div className="hidden min-[400px]:flex items-center gap-1">
          {(['features', 'pricing', 'faq'] as const).map((id) => (
            <Button
              key={id}
              variant="ghost"
              size="sm"
              onClick={() => scrollTo(id)}
              className="text-[var(--brand-text)] hover:text-[var(--brand-accent)]
                         text-sm font-normal transition-colors duration-150"
            >
              {t(`nav.${id}`)}
            </Button>
          ))}
        </div>

        {/* Right controls */}
        <div className="flex items-center gap-2">
          {/* Language toggle — hidden below 400px */}
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleLang}
            className="hidden min-[400px]:inline-flex text-[var(--brand-muted)]
                       hover:text-[var(--brand-text)] text-sm font-normal"
            aria-label={lang === 'ro' ? 'Switch to English' : 'Schimba in romana'}
          >
            {lang === 'ro' ? 'EN' : 'RO'}
          </Button>

          {/* Dark mode toggle — minimum 44x44px touch target */}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            aria-label={t('a11y.darkmode')}
            className="min-w-[44px] min-h-[44px] text-[var(--brand-text)]"
          >
            {theme === 'dark' ? <Sun className="size-5" /> : <Moon className="size-5" />}
          </Button>

          {/* CTA */}
          <Button
            size="sm"
            onClick={() => navigate('/beam')}
            className="bg-[var(--brand-accent)] text-white hover:bg-[var(--brand-accent)]/90
                       transition-colors duration-150"
          >
            {t('nav.cta')}
          </Button>
        </div>
      </div>
    </nav>
  )
}
