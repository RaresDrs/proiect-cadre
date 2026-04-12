import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { BeamInputForm } from '@/components/beam/BeamInputForm'
import type { BeamInput } from '@/types/api'

const defaultInput: BeamInput = {
  length: 6, angle_deg: 0, supports: [], point_loads: [],
  distributed_load: 0, q_start: 0, q_end: 6, EI: 21000, EA: 2100000,
}

function renderForm(overrides?: Partial<BeamInput>, onSolve = vi.fn()) {
  const input = { ...defaultInput, ...overrides }
  return render(
    <MemoryRouter>
      <BeamInputForm initialInput={input} onSolve={onSolve} />
    </MemoryRouter>
  )
}

describe('BeamInputForm — REQ-02-01', () => {
  it('renders length field', () => {
    renderForm()
    expect(screen.getByLabelText(/lungime|length/i)).toBeTruthy()
  })

  it('renders Calculează button', () => {
    renderForm()
    expect(screen.getByRole('button', { name: /calculea|calculate/i })).toBeTruthy()
  })

  it('Calculează disabled with 0 supports', () => {
    renderForm({ supports: [] })
    const btn = screen.getByRole('button', { name: /calculea|calculate/i })
    expect(btn).toBeDisabled()
  })

  it('Calculează disabled with 1 roller only (unstable)', () => {
    renderForm({ supports: [{ x: 3, type: 2 }] })
    const btn = screen.getByRole('button', { name: /calculea|calculate/i })
    expect(btn).toBeDisabled()
  })

  it('Calculează enabled with pin + roller (stable)', () => {
    renderForm({ supports: [{ x: 0, type: 1 }, { x: 6, type: 2 }] })
    const btn = screen.getByRole('button', { name: /calculea|calculate/i })
    expect(btn).not.toBeDisabled()
  })

  it('calls onSolve with BeamInput on submit', async () => {
    const onSolve = vi.fn()
    renderForm({ supports: [{ x: 0, type: 1 }, { x: 6, type: 2 }] }, onSolve)
    const btn = screen.getByRole('button', { name: /calculea|calculate/i })
    fireEvent.click(btn)
    expect(onSolve).toHaveBeenCalledOnce()
    const arg = onSolve.mock.calls[0][0] as BeamInput
    expect(arg.length).toBe(6)
    expect(arg.supports).toHaveLength(2)
  })
})
