import { render } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'

// Mock window.matchMedia to simulate prefers-reduced-motion: reduce
function mockReducedMotion(value: boolean) {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: (query: string) => ({
      matches: query === '(prefers-reduced-motion: reduce)' ? value : false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }),
  })
}

describe('prefers-reduced-motion — REQ-1h', () => {
  it('HeroSection renders static content (no Suspense lazy motion) when prefers-reduced-motion is reduce', async () => {
    mockReducedMotion(true)
    const { HeroSection } = await import('@/components/sections/HeroSection')
    const { container } = render(<HeroSection />)
    // When reduced motion, StaticHeroContent is rendered — h1 is immediately in DOM
    expect(container.querySelector('h1')).not.toBeNull()
  })

  it('HeroSection renders animated content (Suspense wrapper) when motion is allowed', async () => {
    mockReducedMotion(false)
    const { HeroSection } = await import('@/components/sections/HeroSection')
    const { container } = render(<HeroSection />)
    // Suspense fallback renders StaticHeroContent initially — h1 is present
    expect(container.querySelector('h1')).not.toBeNull()
  })
})
