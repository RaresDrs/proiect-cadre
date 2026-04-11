import { useState, useEffect, useCallback } from 'react'
import { translations, type Lang } from '@/lib/i18n'

const STORAGE_KEY = 'structcalc-lang'

export function useLang() {
  const [lang, setLang] = useState<Lang>(() => {
    const stored = localStorage.getItem(STORAGE_KEY) as Lang | null
    return stored === 'en' ? 'en' : 'ro'
  })

  useEffect(() => {
    document.documentElement.setAttribute('lang', lang)
    localStorage.setItem(STORAGE_KEY, lang)
  }, [lang])

  const toggleLang = useCallback(() => {
    setLang(prev => (prev === 'ro' ? 'en' : 'ro'))
  }, [])

  const t = useCallback((key: string): string => {
    return translations[lang][key] ?? key
  }, [lang])

  return { lang, toggleLang, t }
}
