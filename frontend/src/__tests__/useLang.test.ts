import { describe, it, expect, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useLang } from '@/hooks/useLang'

describe('useLang — REQ-1j, REQ-1l', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.setAttribute('lang', 'ro')
  })

  it('defaults to "ro" language', () => {
    const { result } = renderHook(() => useLang())
    expect(result.current.lang).toBe('ro')
  })

  it('toggleLang switches from ro to en', () => {
    const { result } = renderHook(() => useLang())
    act(() => {
      result.current.toggleLang()
    })
    expect(result.current.lang).toBe('en')
  })

  it('toggleLang switches from en to ro', () => {
    localStorage.setItem('structcalc-lang', 'en')
    const { result } = renderHook(() => useLang())
    act(() => {
      result.current.toggleLang()
    })
    expect(result.current.lang).toBe('ro')
  })

  it('persists lang to localStorage key "structcalc-lang"', () => {
    const { result } = renderHook(() => useLang())
    act(() => {
      result.current.toggleLang()
    })
    expect(localStorage.getItem('structcalc-lang')).toBe('en')
  })

  it('updates document.documentElement.lang attribute on toggle', () => {
    const { result } = renderHook(() => useLang())
    act(() => {
      result.current.toggleLang()
    })
    expect(document.documentElement.getAttribute('lang')).toBe('en')
  })
})
