import { describe, it, beforeEach } from 'vitest'

describe('EmailCapture — REQ-1i', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it.todo('submitting valid email saves to localStorage key "structcalc-waitlist"')
  it.todo('submitting invalid email shows error message matching "Introdu o adresă de email validă."')
  it.todo('after successful submit shows success message matching "Ești pe listă!"')
  it.todo('does not submit or save to localStorage when email is empty')
})
