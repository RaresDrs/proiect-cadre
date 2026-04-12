import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import App from '@/App'

describe('Routing — REQ-02-01', () => {
  it('renders / without crashing', () => {
    const { container } = render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    )
    expect(container.querySelector('#hero')).not.toBeNull()
  })

  it('renders /beam without crashing', () => {
    const { container } = render(
      <MemoryRouter initialEntries={['/beam']}>
        <App />
      </MemoryRouter>
    )
    // BeamPage is lazy — fallback or main content must render
    expect(container.querySelector('main')).not.toBeNull()
  })
})
