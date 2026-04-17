---
phase: 2
slug: modul-grinzi-2d
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-12
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Vitest 4.1.4 + @testing-library/react 16.3.2 |
| **Config file** | `frontend/vitest.config.ts` (exists) |
| **Quick run command** | `cd frontend && npx vitest run --reporter=verbose` |
| **Full suite command** | `cd frontend && npx vitest run --coverage` |
| **Estimated runtime** | ~15 seconds |

**Baseline:** 25 tests, 6 test files — all passing as of 2026-04-12. New Phase 2 tests must not break this baseline.

---

## Sampling Rate

- **After every task commit:** Run `cd frontend && npx vitest run --reporter=verbose`
- **After every plan wave:** Run `cd frontend && npx vitest run --coverage`
- **Before `/gsd:verify-work`:** Full suite must be green (25 baseline + new tests)
- **Max feedback latency:** ~15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Behavior | Test Type | Automated Command | File | Status |
|---------|------|------|----------|-----------|-------------------|------|--------|
| 02-01-01 | 01 | 0 | `/beam` route renders | unit | `npx vitest run src/__tests__/beam-routing.test.tsx` | Wave 0 | ⬜ pending |
| 02-01-02 | 01 | 0 | Landing still works after router refactor | unit | `npx vitest run src/__tests__/landing-sections.test.tsx` | Update existing | ⬜ pending |
| 02-01-03 | 01 | 1 | BeamInputForm renders all fields | unit | `npx vitest run src/__tests__/beam-input-form.test.tsx` | Wave 0 | ⬜ pending |
| 02-01-04 | 01 | 1 | BeamInputForm: 0 supports → validation error | unit | same file | Wave 0 | ⬜ pending |
| 02-01-05 | 01 | 1 | BeamInputForm: 1 roller → unstable error | unit | same file | Wave 0 | ⬜ pending |
| 02-01-06 | 01 | 1 | BeamInputForm: valid data calls solve() | unit (mock fetch) | same file | Wave 0 | ⬜ pending |
| 02-02-01 | 02 | 0 | useBeamSolver: success sets result | unit (mock fetch) | `npx vitest run src/__tests__/useBeamSolver.test.ts` | Wave 0 | ⬜ pending |
| 02-02-02 | 02 | 0 | useBeamSolver: 422 sets error message | unit (mock fetch) | same file | Wave 0 | ⬜ pending |
| 02-02-03 | 02 | 0 | useBeamSolver: network error sets error | unit (mock fetch) | same file | Wave 0 | ⬜ pending |
| 02-02-04 | 02 | 1 | encodeBeamHash / decodeBeamHash round-trip | unit | `npx vitest run src/__tests__/beamHash.test.ts` | Wave 0 | ⬜ pending |
| 02-02-05 | 02 | 1 | decodeBeamHash: malformed hash → null | unit | same file | Wave 0 | ⬜ pending |
| 02-03-01 | 03 | 0 | DiagramPanel renders SVG without crash | unit | `npx vitest run src/__tests__/diagram-panel.test.tsx` | Wave 0 | ⬜ pending |
| 02-03-02 | 03 | 0 | DiagramPanel: empty data → no crash | unit | same file | Wave 0 | ⬜ pending |
| 02-04-01 | 04 | 1 | BeamPage reads hash on mount → calls solve | unit | `npx vitest run src/__tests__/beam-page.test.tsx` | Wave 0 | ⬜ pending |
| 02-04-02 | 04 | 1 | BeamPage saves to localStorage on solve | unit | same file | Wave 0 | ⬜ pending |
| 02-04-03 | 04 | 1 | BeamPage: copy link → clipboard write | unit (mock clipboard) | same file | Wave 0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `frontend/src/__tests__/beam-routing.test.tsx` — route renders, MemoryRouter wrapper
- [ ] `frontend/src/__tests__/beam-input-form.test.tsx` — form field stubs for all 6 behaviors above
- [ ] `frontend/src/__tests__/useBeamSolver.test.ts` — hook stubs with mocked fetch
- [ ] `frontend/src/__tests__/beamHash.test.ts` — encode/decode round-trip stubs
- [ ] `frontend/src/__tests__/diagram-panel.test.tsx` — SVG render stubs
- [ ] `frontend/src/__tests__/beam-page.test.tsx` — page integration stubs
- [ ] Update `frontend/src/__tests__/landing-sections.test.tsx` — wrap with MemoryRouter after router refactor

*Existing test infrastructure (vitest.config.ts, setup.ts) is reused — no new framework install needed.*

---

## Key Acceptance Criteria (Programmatically Verifiable)

1. `window.location.hash` after submit equals `btoa(encodeURIComponent(JSON.stringify(input)))`
2. `localStorage.getItem('structcalc-beam-last')` after submit parses to the submitted `BeamInput`
3. Rendering `<BeamPage />` with a valid hash in `window.location.hash` calls the solve function (spy on `useBeamSolver`)
4. The fetch call body sent to `/api/v1/beams/solve` is valid JSON matching `BeamInput` schema
5. On API error, an element with `role="alert"` or error class appears in the DOM
6. Backend field: shear force is `d.V` in `DiagramPoint`, displayed in UI as "T (Forță tăietoare)"

---

## Manual-Only Verifications

| Behavior | Why Manual | Test Instructions |
|----------|------------|-------------------|
| SVG preview updates live while typing | D3 side effects, hard to assert timing | Open `/beam`, type length=6, add support, watch SVG preview update within 150ms |
| Diagram draw-in animation plays | Visual — `prefers-reduced-motion` skips it | Submit a valid beam, watch M/T/N/Deflecție panels draw in with stagger |
| Hover tooltip shows correct values | D3 mousemove events | Hover over M diagram at x=L/2, verify tooltip shows correct Mmax value |
| PDF renders correctly | html2canvas capture | Click Export PDF, verify diagrams visible and Romanian text correct |
| Shareable URL round-trips | Browser navigation | Copy link, open in new tab, verify form pre-filled and calculation auto-runs |
| Dark mode diagrams use correct colors | CSS variable resolution | Toggle dark mode, verify diagram fills change to dark palette |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING file references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
