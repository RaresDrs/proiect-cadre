import { render } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import App from '@/App'

describe('Landing sections — REQ-1a', () => {
  it('renders section#hero', () => {
    const { container } = render(<App />)
    expect(container.querySelector('#hero')).not.toBeNull()
  })
  it('renders section#features', () => {
    const { container } = render(<App />)
    expect(container.querySelector('#features')).not.toBeNull()
  })
  it('renders section#pricing', () => {
    const { container } = render(<App />)
    expect(container.querySelector('#pricing')).not.toBeNull()
  })
  it('renders section#faq', () => {
    const { container } = render(<App />)
    expect(container.querySelector('#faq')).not.toBeNull()
  })
  it('renders section#cta', () => {
    const { container } = render(<App />)
    expect(container.querySelector('#cta')).not.toBeNull()
  })
  it('renders footer', () => {
    const { container } = render(<App />)
    expect(container.querySelector('footer')).not.toBeNull()
  })
  it('has exactly one h1', () => {
    const { container } = render(<App />)
    expect(container.querySelectorAll('h1')).toHaveLength(1)
  })
})
