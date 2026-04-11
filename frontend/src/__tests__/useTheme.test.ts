import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useTheme } from '@/hooks/useTheme'

function mockMatchMedia(matches: boolean) {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    configurable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  })
}

describe('useTheme — REQ-1b', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.classList.remove('dark')
    mockMatchMedia(false)
  })

  it('toggleTheme adds .dark class to <html> when switching to dark mode', () => {
    const { result } = renderHook(() => useTheme())
    expect(result.current.theme).toBe('light')
    act(() => {
      result.current.toggleTheme()
    })
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('toggleTheme removes .dark class from <html> when switching to light mode', () => {
    localStorage.setItem('structcalc-theme', 'dark')
    const { result } = renderHook(() => useTheme())
    expect(result.current.theme).toBe('dark')
    act(() => {
      result.current.toggleTheme()
    })
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })

  it('persists theme to localStorage key "structcalc-theme"', () => {
    const { result } = renderHook(() => useTheme())
    act(() => {
      result.current.toggleTheme()
    })
    expect(localStorage.getItem('structcalc-theme')).toBe('dark')
  })

  it('reads "structcalc-theme" from localStorage on init', () => {
    localStorage.setItem('structcalc-theme', 'dark')
    const { result } = renderHook(() => useTheme())
    expect(result.current.theme).toBe('dark')
  })

  it('defaults to system prefers-color-scheme when localStorage is empty', () => {
    mockMatchMedia(true)
    const { result } = renderHook(() => useTheme())
    expect(result.current.theme).toBe('dark')
  })
})
