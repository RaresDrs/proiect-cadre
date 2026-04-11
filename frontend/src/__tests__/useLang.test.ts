import { describe, it, beforeEach } from 'vitest'

describe('useLang — REQ-1j, REQ-1l', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.setAttribute('lang', 'ro')
  })

  it.todo('defaults to "ro" language')
  it.todo('toggleLang switches from ro to en')
  it.todo('toggleLang switches from en to ro')
  it.todo('persists lang to localStorage key "structcalc-lang"')
  it.todo('updates document.documentElement.lang attribute on toggle')
})
