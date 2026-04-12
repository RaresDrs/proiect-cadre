---
phase: 02-modul-grinzi-2d
plan: 01
subsystem: ui
tags: [react-router-dom, react, typescript, vitest, shadcn, tailwind, svg]

# Dependency graph
requires:
  - phase: 01-design-sistem-landing-page
    provides: Navbar, Footer, i18n system, theme/lang hooks, landing page sections

provides:
  - react-router-dom v7 BrowserRouter routing (/ and /beam routes)
  - RootLayout with shared Navbar + Outlet + Footer
  - LandingPage extracted into standalone page component
  - BeamPage with split layout (form left, preview right on lg)
  - BeamInputForm with all fields, stability validation, and Calculează button
  - BeamPreview SVG with 150ms debounce rendering beam schema with supports/loads
  - Full beam i18n keys (beam.form.*, beam.page.*, beam.preview.*) in ro and en

affects: [02-02-beam-solver, 02-03-diagrams-d3, 02-04-pdf-export]

# Tech tracking
tech-stack:
  added: [react-router-dom@7, @testing-library/jest-dom, shadcn input, shadcn label, shadcn select]
  patterns:
    - BrowserRouter in main.tsx wrapping App, App contains only Routes tree
    - RootLayout as parent Route with Outlet pattern for shared nav/footer
    - Lazy-loaded pages with React.lazy + Suspense for code splitting
    - BeamInput as shared state type — form owns input, page owns solve callback
    - SVG beam preview debounced 150ms via setTimeout in useEffect

key-files:
  created:
    - frontend/src/components/layout/RootLayout.tsx
    - frontend/src/pages/LandingPage.tsx
    - frontend/src/pages/BeamPage.tsx
    - frontend/src/components/beam/BeamInputForm.tsx
    - frontend/src/components/beam/BeamPreview.tsx
    - frontend/src/components/ui/input.tsx
    - frontend/src/components/ui/label.tsx
    - frontend/src/components/ui/select.tsx
    - frontend/src/__tests__/beam-routing.test.tsx
    - frontend/src/__tests__/beam-input-form.test.tsx
  modified:
    - frontend/src/main.tsx
    - frontend/src/App.tsx
    - frontend/src/components/layout/Navbar.tsx
    - frontend/src/lib/i18n.ts
    - frontend/src/__tests__/landing-sections.test.tsx
    - frontend/src/__tests__/responsive.test.tsx
    - frontend/src/__tests__/setup.ts
    - frontend/package.json

key-decisions:
  - "Navbar CTA uses useNavigate('/beam') instead of asChild Link — @base-ui/react Button does not support asChild prop"
  - "Native HTML <select> for support type picker — simpler test compatibility vs. base-ui Select Portal complexity"
  - "@testing-library/jest-dom added to setup.ts — required for toBeDisabled matcher used in test stubs"
  - "responsive.test.tsx and landing-sections.test.tsx updated to use MemoryRouter — App now requires Router context"

patterns-established:
  - "All tests wrapping App must use MemoryRouter — App uses Routes which requires Router context"
  - "BeamInput state lives in BeamPage, passed down to BeamInputForm as initialInput — form is controlled but owns its own copy"
  - "onSolve callback pattern: form calls parent with submitted BeamInput, parent decides what to do (stub for 02-02)"

requirements-completed: []

# Metrics
duration: 7min
completed: 2026-04-12
---

# Phase 02 Plan 01: Modul Grinzi 2D — Routing + BeamInputForm + BeamPreview Summary

**react-router-dom v7 routing with RootLayout, LandingPage extracted, /beam route with BeamInputForm (stability validation) and live SVG BeamPreview (150ms debounce)**

## Performance

- **Duration:** ~7 min
- **Started:** 2026-04-12T14:30:12Z
- **Completed:** 2026-04-12T14:36:43Z
- **Tasks:** 3
- **Files modified:** 18

## Accomplishments

- Installed react-router-dom@7 and refactored App into BrowserRouter + Routes tree with RootLayout
- Extracted LandingPage from App, created /beam route with lazy BeamPage and split layout
- Implemented BeamInputForm (7 fields, dynamic supports/point loads, stability check, Calculează button) and BeamPreview SVG (debounced 150ms, renders beam/supports/loads via pure React SVG)
- All 33 tests passing (25 baseline + 2 routing + 6 beam-input-form)

## Task Commits

1. **Task 1: Install packages + create test stubs** - `9489686` (feat)
2. **Task 2: Router refactor — RootLayout, LandingPage, /beam route, Navbar CTA** - `3b807ed` (feat)
3. **Task 3: BeamInputForm + BeamPreview + i18n beam keys** - `12058f9` (feat)

## Files Created/Modified

- `frontend/src/main.tsx` — Added BrowserRouter wrapper
- `frontend/src/App.tsx` — Refactored to Routes tree (/ and /beam)
- `frontend/src/components/layout/RootLayout.tsx` — Shared layout with Navbar + Outlet + Footer
- `frontend/src/pages/LandingPage.tsx` — Extracted landing page sections
- `frontend/src/pages/BeamPage.tsx` — Beam calculator page with split layout, wired form + preview
- `frontend/src/components/beam/BeamInputForm.tsx` — Full beam definition form with stability validation
- `frontend/src/components/beam/BeamPreview.tsx` — SVG live preview with 150ms debounce
- `frontend/src/components/layout/Navbar.tsx` — CTA now navigates to /beam via useNavigate
- `frontend/src/lib/i18n.ts` — Added beam.page.*, beam.form.*, beam.preview.* keys (ro + en)
- `frontend/src/__tests__/setup.ts` — Added @testing-library/jest-dom import
- `frontend/src/__tests__/beam-routing.test.tsx` — New routing test stub
- `frontend/src/__tests__/beam-input-form.test.tsx` — New form test with all 6 behaviors
- `frontend/src/__tests__/landing-sections.test.tsx` — Updated to use MemoryRouter
- `frontend/src/__tests__/responsive.test.tsx` — Updated to use MemoryRouter
- `frontend/src/components/ui/input.tsx` — shadcn Input component
- `frontend/src/components/ui/label.tsx` — shadcn Label component
- `frontend/src/components/ui/select.tsx` — shadcn Select component
- `frontend/package.json` — Added react-router-dom, @testing-library/jest-dom

## Decisions Made

- **Navbar CTA via useNavigate:** `@base-ui/react` Button does not support `asChild`, so used `useNavigate('/beam')` hook pattern
- **Native select for support type:** Avoided base-ui Select portal complexity; native `<select>` pairs cleanly with `<label htmlFor>` for testing
- **@testing-library/jest-dom added:** The test stubs written in the plan use `toBeDisabled()` which requires jest-dom matchers — added to setup.ts
- **responsive.test.tsx and landing-sections.test.tsx fixed:** After router refactor, App requires Router context; all tests rendering App updated to use `<MemoryRouter>`

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added @testing-library/jest-dom for toBeDisabled matcher**
- **Found during:** Task 3 (beam-input-form tests)
- **Issue:** Test stubs in the plan use `toBeDisabled()` Chai extension which is provided by @testing-library/jest-dom, not included in existing setup
- **Fix:** Installed package, imported in setup.ts
- **Files modified:** frontend/package.json, frontend/src/__tests__/setup.ts
- **Verification:** All 6 beam-input-form tests pass including disabled state checks
- **Committed in:** 12058f9 (Task 3 commit)

**2. [Rule 1 - Bug] Fixed responsive.test.tsx broken by router refactor**
- **Found during:** Task 3 verification (full suite run)
- **Issue:** responsive.test.tsx renders `<App />` without Router context; after Task 2 App now uses `Routes` which requires a Router — 2 tests failed
- **Fix:** Wrapped App in `<MemoryRouter initialEntries={['/']}>`
- **Files modified:** frontend/src/__tests__/responsive.test.tsx
- **Verification:** Full suite shows 33 tests passing
- **Committed in:** 12058f9 (Task 3 commit)

---

**Total deviations:** 2 auto-fixed (1 missing critical, 1 bug)
**Impact on plan:** Both fixes required for correctness and test pass. No scope creep.

## Issues Encountered

None beyond the auto-fixed deviations above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- /beam route with BeamInputForm and BeamPreview fully functional
- BeamInput state shape established (per api.ts types) — 02-02 can wire useBeamSolver directly
- onSolve callback stub in BeamPage.tsx has TODO comment for 02-02
- All routing structure in place for 02-02 (diagrams), 02-03 (D3), 02-04 (PDF)

---
*Phase: 02-modul-grinzi-2d*
*Completed: 2026-04-12*
