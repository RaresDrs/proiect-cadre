import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, beforeEach } from 'vitest'
import { EmailCapture } from '@/components/sections/EmailCapture'

describe('EmailCapture — REQ-1i', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('submitting valid email saves to localStorage key "structcalc-waitlist"', () => {
    render(<EmailCapture />)
    const input = screen.getByRole('textbox')
    fireEvent.change(input, { target: { value: 'test@example.com' } })
    fireEvent.submit(input.closest('form')!)
    expect(localStorage.getItem('structcalc-waitlist')).toBe('test@example.com')
  })

  it('submitting invalid email shows error message matching "Introdu o adresa de email valida."', () => {
    render(<EmailCapture />)
    const input = screen.getByRole('textbox')
    fireEvent.change(input, { target: { value: 'notanemail' } })
    fireEvent.submit(input.closest('form')!)
    expect(screen.getByRole('alert').textContent).toContain('adresa de email valida')
    expect(localStorage.getItem('structcalc-waitlist')).toBeNull()
  })

  it('after successful submit shows success message matching "Esti pe lista!"', () => {
    render(<EmailCapture />)
    const input = screen.getByRole('textbox')
    fireEvent.change(input, { target: { value: 'valid@test.com' } })
    fireEvent.submit(input.closest('form')!)
    expect(screen.getByRole('status').textContent).toContain('lista')
  })

  it('does not submit or save to localStorage when email is empty', () => {
    render(<EmailCapture />)
    const form = document.querySelector('form')!
    fireEvent.submit(form)
    expect(localStorage.getItem('structcalc-waitlist')).toBeNull()
  })
})
