import { describe, it, beforeEach } from 'vitest'

describe('useTheme — REQ-1b', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.classList.remove('dark')
  })

  it.todo('toggleTheme adds .dark class to <html> when switching to dark mode')
  it.todo('toggleTheme removes .dark class from <html> when switching to light mode')
  it.todo('persists theme to localStorage key "structcalc-theme"')
  it.todo('reads "structcalc-theme" from localStorage on init')
  it.todo('defaults to system prefers-color-scheme when localStorage is empty')
})
