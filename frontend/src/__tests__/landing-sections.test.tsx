import { render } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import App from '@/App'

describe('Landing sections — REQ-1a', () => {
  const renderLanding = () =>
    render(<MemoryRouter initialEntries={['/']}><App /></MemoryRouter>)

  it('renders section#hero', () => {
    const { container } = renderLanding()
    expect(container.querySelector('#hero')).not.toBeNull()
  })
  it('renders section#features', () => {
    const { container } = renderLanding()
    expect(container.querySelector('#features')).not.toBeNull()
  })
  it('renders section#pricing', () => {
    const { container } = renderLanding()
    expect(container.querySelector('#pricing')).not.toBeNull()
  })
  it('renders section#faq', () => {
    const { container } = renderLanding()
    expect(container.querySelector('#faq')).not.toBeNull()
  })
  it('renders section#cta', () => {
    const { container } = renderLanding()
    expect(container.querySelector('#cta')).not.toBeNull()
  })
  it('renders footer', () => {
    const { container } = renderLanding()
    expect(container.querySelector('footer')).not.toBeNull()
  })
  it('has exactly one h1', () => {
    const { container } = renderLanding()
    expect(container.querySelectorAll('h1')).toHaveLength(1)
  })
})
