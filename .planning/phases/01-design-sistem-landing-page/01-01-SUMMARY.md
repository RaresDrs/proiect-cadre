---
phase: 01-design-sistem-landing-page
plan: 01
subsystem: frontend-foundation
tags: [design-system, vitest, dark-mode, i18n, hooks, layout]
dependency_graph:
  requires: []
  provides: [useTheme, useLang, i18n.ts, Navbar, Footer, vitest-infrastructure, brand-tokens]
  affects: [01-02, 01-03]
tech_stack:
  added: [vitest, @testing-library/react, @testing-library/user-event, jsdom, @vitest/coverage-v8]
  patterns: [localStorage-persistence, css-custom-properties, react-hooks, jsdom-mocking]
key_files:
  created:
    - frontend/vitest.config.ts
    - frontend/src/__tests__/useTheme.test.ts
    - frontend/src/__tests__/useLang.test.ts
    - frontend/src/__tests__/landing-sections.test.tsx
    - frontend/src/__tests__/EmailCapture.test.tsx
    - frontend/src/__tests__/reducedMotion.test.tsx
    - frontend/src/__tests__/responsive.test.tsx
    - frontend/src/lib/i18n.ts
    - frontend/src/hooks/useTheme.ts
    - frontend/src/hooks/useLang.ts
    - frontend/src/components/layout/Navbar.tsx
    - frontend/src/components/layout/Footer.tsx
  modified:
    - frontend/src/index.css
    - frontend/index.html
    - frontend/package.json
decisions:
  - "jsdom matchMedia mock via Object.defineProperty — vi.spyOn() fails because jsdom does not define window.matchMedia"
  - "Brand tokens appended as new @layer base block after existing shadcn OKLCH tokens — never rewrite existing tokens"
  - "Dark mode FOUC prevention via inline blocking script in <head> before CSS loads"
  - "i18n implemented as plain TypeScript object (no external library) — sufficient for 30+ keys in 2 languages"
metrics:
  duration: "~8 minutes"
  completed: "2026-04-11T17:20:48Z"
  tasks_completed: 3
  files_created: 12
  files_modified: 3
---

# Phase 1 Plan 01: Design System Foundation Summary

Vitest infrastructure, brand CSS tokens, dark mode + i18n hooks, and Navbar/Footer layout components — the complete Wave 0 foundation required by all Phase 1 Wave 1 plans.

## What Was Built

### Task 1: Vitest Infrastructure
- Installed `vitest`, `@testing-library/react`, `@testing-library/user-event`, `jsdom`, `@vitest/coverage-v8`
- Created `frontend/vitest.config.ts` with jsdom environment and `@` path alias
- Created 6 test stub files covering REQ-1a, REQ-1b, REQ-1g, REQ-1h, REQ-1i, REQ-1j/REQ-1l
- Suite exits 0 (25 todo stubs, no failures)

### Task 2: Design Tokens + index.html + Hooks
- Extended `frontend/src/index.css` with StructCalc brand tokens appended after existing shadcn OKLCH tokens
  - Light: `--brand-bg: #F5F5F7`, `--brand-accent: #2563EB`, `--brand-text: #1D1D1F`
  - Dark: `--brand-bg: #000000`, `--brand-accent: #3B82F6` (AAA contrast on black)
  - Added `prefers-reduced-motion` global override
  - Added focus-visible ring and cursor-pointer rules
- Fixed `frontend/index.html`: `lang="ro"`, FOUC-prevention blocking script, manifest link, Apple touch icon meta tags, updated title
- Created `frontend/src/lib/i18n.ts` with 30+ translation keys in both `ro` and `en`
- Created `frontend/src/hooks/useTheme.ts`: persists to `localStorage['structcalc-theme']`, toggles `.dark` on `<html>`
- Created `frontend/src/hooks/useLang.ts`: persists to `localStorage['structcalc-lang']`, updates `document.documentElement.lang`
- Updated test stubs with real passing tests (10 tests pass)

### Task 3: Navbar + Footer Components
- Created `frontend/src/components/layout/Navbar.tsx`
  - Fixed top, z-50, glassmorphism background
  - Smooth scroll to section anchors
  - Dark mode toggle with 44px touch target (`aria-label` from `t('a11y.darkmode')`)
  - Language toggle (EN/RO)
  - Nav links hidden below 400px (mobile-first)
- Created `frontend/src/components/layout/Footer.tsx`
  - Copyright line via `t('footer.copyright')`
  - Footer nav links with smooth scroll

## Interfaces Exported (Wave 1 contracts)

```typescript
// frontend/src/hooks/useTheme.ts
export function useTheme(): { theme: 'light' | 'dark', toggleTheme: () => void }

// frontend/src/hooks/useLang.ts
export function useLang(): { lang: Lang, toggleLang: () => void, t: (key: string) => string }

// frontend/src/lib/i18n.ts
export type Lang = 'ro' | 'en'
export const translations: Record<Lang, Record<string, string>>

// frontend/src/components/layout/Navbar.tsx
export function Navbar(): JSX.Element

// frontend/src/components/layout/Footer.tsx
export function Footer(): JSX.Element
```

## Decisions Made

1. **jsdom matchMedia mock**: jsdom does not define `window.matchMedia` — tests use `Object.defineProperty` to mock it. `vi.spyOn()` fails because the property is undefined.
2. **Brand tokens appended**: New `@layer base` block appended after existing shadcn OKLCH tokens. Existing tokens untouched.
3. **FOUC prevention script**: Inline blocking script in `<head>` before any CSS — reads localStorage and applies `.dark` class synchronously on page load.
4. **No i18n library**: Plain TypeScript object for 30+ keys in 2 languages — no `react-i18next` needed at this scale.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed jsdom matchMedia mock in useTheme tests**
- **Found during:** Task 2 test run
- **Issue:** `vi.spyOn(window, 'matchMedia')` throws "can only spy on a function. Received undefined" because jsdom does not implement `window.matchMedia`
- **Fix:** Replaced `vi.spyOn` with `Object.defineProperty(window, 'matchMedia', ...)` helper function that creates a complete mock MediaQueryList
- **Files modified:** `frontend/src/__tests__/useTheme.test.ts`
- **Commit:** `6891f1c`

## Known Stubs

None — all hooks and components are fully wired. The 15 remaining `it.todo` tests in the other 4 test files are intentional stubs for Wave 1 implementation (landing sections, email capture, reduced motion, responsive layout). These stubs exist by design as Wave 0 verification targets.

## Self-Check: PASSED

Files verified:
- `frontend/vitest.config.ts` — exists, contains `environment: 'jsdom'`
- `frontend/src/__tests__/` — 6 files present
- `frontend/src/hooks/useTheme.ts` — contains `structcalc-theme`
- `frontend/src/hooks/useLang.ts` — contains `setAttribute.*lang`
- `frontend/src/lib/i18n.ts` — contains 30+ keys in both languages
- `frontend/src/components/layout/Navbar.tsx` — exists, contains `scrollIntoView`, `min-h-[44px]`, `t('a11y.darkmode')`
- `frontend/src/components/layout/Footer.tsx` — exists, contains `t('footer.copyright')`
- `frontend/src/index.css` — contains `--brand-bg: #F5F5F7` and `--brand-bg: #000000`
- `frontend/index.html` — `lang="ro"`, blocking script, manifest link

Commits verified:
- `cb02851` — Task 1: Vitest infrastructure
- `2ed84e2` — Task 2a: index.css + index.html
- `665f61e` — Task 2b: i18n + hooks + test updates
- `6891f1c` — Task 2 fix: useTheme test matchMedia mock
- `816cb30` — Task 3: Navbar + Footer
