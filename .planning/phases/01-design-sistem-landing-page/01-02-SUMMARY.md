---
phase: 01-design-sistem-landing-page
plan: 02
subsystem: landing-sections
tags: [landing-page, framer-motion, faq-accordion, email-capture, pricing, hero, vitest]
dependency_graph:
  requires: [01-01]
  provides: [HeroSection, FeaturesSection, PricingSection, FAQSection, CTASection, EmailCapture, StructuralDiagram, useInView]
  affects: [01-03]
tech_stack:
  added: [motion@12.38.0, @base-ui/react Collapsible]
  patterns: [LazyMotion-lazy-loading, IntersectionObserver-scroll-animation, localStorage-email-capture, aria-expanded-accordion]
key_files:
  created:
    - frontend/src/hooks/useInView.ts
    - frontend/src/components/sections/HeroSection.tsx
    - frontend/src/components/sections/StructuralDiagram.tsx
    - frontend/src/components/sections/FeaturesSection.tsx
    - frontend/src/components/sections/FAQSection.tsx
    - frontend/src/components/sections/CTASection.tsx
    - frontend/src/components/sections/EmailCapture.tsx
    - frontend/src/components/sections/PricingSection.tsx
  modified:
    - frontend/src/App.tsx
    - frontend/src/__tests__/landing-sections.test.tsx
    - frontend/src/__tests__/EmailCapture.test.tsx
    - frontend/src/__tests__/reducedMotion.test.tsx
    - frontend/src/__tests__/setup.ts
decisions:
  - "motion/react LazyMotion + React.lazy for hero animations — reduces initial bundle from 34KB to 4.6KB"
  - "StaticHeroContent fallback for prefers-reduced-motion — renders h1 immediately with no animation"
  - "IntersectionObserver mock must use class not arrow function — arrow functions are not constructors in Vitest"
  - "FAQSection single-open accordion via openItem state + Collapsible.Root open prop — no @base-ui accordion primitive needed"
  - "EmailCapture regex /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/ — simple email validation without external library"
  - "PricingSection blur-sm + pointer-events-none on locked tiers — keeps DOM accessible but visually blurred"
metrics:
  duration: "~10 minutes"
  completed: "2026-04-11T22:39:41Z"
  tasks_completed: 3
  files_created: 8
  files_modified: 5
---

# Phase 1 Plan 02: Landing Page Sections Summary

All 5 landing page sections built with Framer Motion lazy-loaded hero, IntersectionObserver scroll animations, @base-ui/react FAQ accordion, EmailCapture with localStorage, and blurred Pricing tiers — full Vitest suite green (23 tests passing).

## What Was Built

### Task 1: motion + useInView + HeroSection + StructuralDiagram

- Installed `motion@12.38.0` (replaces framer-motion; reduces initial bundle from 34KB to 4.6KB via LazyMotion)
- Created `frontend/src/hooks/useInView.ts` — IntersectionObserver hook with `threshold=0.15`, `once=true`, returns `{ ref, isInView }`
- Created `frontend/src/components/sections/StructuralDiagram.tsx` — animated SVG simply-supported beam with:
  - Distributed load arrows (7 arrows) in `var(--brand-accent)` color
  - Moment diagram parabola animated via CSS `stroke-dasharray` / `stroke-dashoffset` keyframe (`drawBeamDiagram`, 1.2s)
  - `M(x)` label fades in after diagram draws
  - `aria-hidden="true"` (decorative illustration)
- Created `frontend/src/components/sections/HeroSection.tsx`:
  - `React.lazy()` loads the `motion/react` module only when needed (D-08 lazy loading)
  - `LazyMotion features={domAnimation}` reduces motion bundle to 4.6KB
  - Spring physics: headline (stiffness 100, damping 20, delay 0ms), sub-headline (delay 150ms), CTAs (stiffness 120, damping 22, delay 300ms)
  - `StaticHeroContent` fallback used when `prefers-reduced-motion: reduce` or while motion loads
  - `id="hero"`, single `<h1>` per page
- Fixed `reducedMotion.test.tsx` with real passing tests

### Task 2: FeaturesSection, FAQSection, CTASection

- Created `frontend/src/components/sections/FeaturesSection.tsx`:
  - 3 feature cards with `useInView` + `animate-fade-in-up` (tw-animate-css) stagger (0ms, 100ms, 200ms delays)
  - Icons: Ruler, FileText, Smartphone from lucide-react
  - `id="features"`, `<h2>` section heading
- Created `frontend/src/components/sections/FAQSection.tsx`:
  - `@base-ui/react/collapsible` Collapsible primitive
  - Single-open via `openItem` state — only one item open at a time
  - `aria-expanded={isOpen}` on Collapsible.Trigger
  - ChevronDown rotates 180deg when open
  - 4 FAQ items from i18n keys `faq.q1-q4`, `faq.a1-a4`
  - `id="faq"`, `<h2>` section heading
- Created `frontend/src/components/sections/CTASection.tsx`:
  - Full-width `bg-[var(--brand-accent)]` band
  - White heading + body text from i18n
  - Button calls `window.scrollTo({ top: 0, behavior: 'smooth' })`
  - `id="cta"`
- Filled `landing-sections.test.tsx` with real passing tests (7 tests)

### Task 3: EmailCapture + PricingSection + App.tsx wiring

- Created `frontend/src/components/sections/EmailCapture.tsx`:
  - Regex email validation: `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`
  - On valid: `localStorage.setItem('structcalc-waitlist', email)`, shows success `role="status"`
  - On invalid/empty: shows error `role="alert"`, `aria-invalid="true"` on input, `aria-describedby="email-error"`
  - Uses `useLang()` for all i18n strings (email.label, email.placeholder, email.cta, email.success, email.error)
- Created full `frontend/src/components/sections/PricingSection.tsx`:
  - Free tier: fully visible, `border-2 border-[var(--brand-accent)]`
  - Pro tier: `blur-sm` + Lock icon + `pricing.badge` badge
  - Enterprise tier: `blur-sm` + Lock icon + `pricing.badge` badge
  - `EmailCapture` rendered below pricing tiers per D-21
  - `id="pricing"`
- `frontend/src/App.tsx` already wired with all sections in correct order (Navbar, HeroSection, FeaturesSection, PricingSection, FAQSection, CTASection, Footer)
- Fixed `EmailCapture.test.tsx` — replaced 4 `.todo` stubs with real passing tests

### Bug Fix: IntersectionObserver Mock (Rule 1)

Fixed `setup.ts` — replaced arrow function mock with a proper class, since arrow functions cannot be used as constructors with `new`. The tests in `landing-sections.test.tsx` were failing because `useInView` calls `new IntersectionObserver(...)`.

## Interfaces Exported

```typescript
// frontend/src/hooks/useInView.ts
export function useInView(options?: { threshold?: number; once?: boolean }): {
  ref: React.MutableRefObject<HTMLElement | null>
  isInView: boolean
}

// frontend/src/components/sections/HeroSection.tsx
export function HeroSection(): JSX.Element

// frontend/src/components/sections/FeaturesSection.tsx
export function FeaturesSection(): JSX.Element

// frontend/src/components/sections/PricingSection.tsx
export function PricingSection(): JSX.Element

// frontend/src/components/sections/FAQSection.tsx
export function FAQSection(): JSX.Element

// frontend/src/components/sections/CTASection.tsx
export function CTASection(): JSX.Element

// frontend/src/components/sections/EmailCapture.tsx
export function EmailCapture(): JSX.Element

// frontend/src/components/sections/StructuralDiagram.tsx
export function StructuralDiagram(): JSX.Element
```

## Decisions Made

1. **motion/react LazyMotion**: `React.lazy()` + `LazyMotion features={domAnimation}` reduces motion from 34KB to 4.6KB initial JS — hero animations load asynchronously while `StaticHeroContent` renders immediately
2. **StaticHeroContent fallback**: `window.matchMedia('(prefers-reduced-motion: reduce)').matches` checked synchronously — when true, static content renders with no Suspense/motion
3. **IntersectionObserver mock as class**: Vitest uses arrow function for `vi.fn().mockImplementation(() => ({...}))` which returns a non-constructable function; must use `class MockIntersectionObserver` to support `new IntersectionObserver(...)`
4. **FAQSection single-open via state**: `openItem: number | null` state with `Collapsible.Root open={openItem === index}` — simpler than using @base-ui's Accordion primitive; avoids extra component for this use case
5. **PricingSection blur-sm + pointer-events-none**: Locked tiers use `blur-sm select-none pointer-events-none` — keeps DOM structure for SEO while visually indicating future availability

## Test Results

All 23 tests pass (2 `.todo` stubs remain in `responsive.test.tsx` — intentional, scoped to Plan 01-03 responsive work):

| Test File | Tests | Status |
|-----------|-------|--------|
| useTheme.test.ts | 5 | PASS |
| useLang.test.ts | 5 | PASS |
| EmailCapture.test.tsx | 4 | PASS |
| landing-sections.test.tsx | 7 | PASS |
| reducedMotion.test.tsx | 2 | PASS |
| responsive.test.tsx | 2 todo | SKIPPED (intentional) |

TypeScript: 0 errors (`npx tsc --noEmit` exits 0)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed IntersectionObserver mock not constructable**
- **Found during:** Task 2/3 — all landing-sections tests failed with "is not a constructor"
- **Issue:** `vi.fn().mockImplementation(() => ({...}))` creates a non-constructable arrow function; `useInView.ts` calls `new IntersectionObserver(...)` which requires a constructor
- **Fix:** Replaced with `class MockIntersectionObserver` in `frontend/src/__tests__/setup.ts`
- **Files modified:** `frontend/src/__tests__/setup.ts`
- **Commit:** (included in task commits via auto-commit hooks)

## Known Stubs

None — all components are fully wired with real data from i18n. The 2 remaining `.todo` tests in `responsive.test.tsx` are intentional Wave 0 stubs scoped to Plan 01-03 (PWA + responsive work).

## Self-Check: PASSED

Files verified:
- `frontend/src/hooks/useInView.ts` — exists, exports `useInView`
- `frontend/src/components/sections/HeroSection.tsx` — contains `LazyMotion`, `domAnimation`, `React.lazy(`, `prefers-reduced-motion`, `id="hero"`
- `frontend/src/components/sections/StructuralDiagram.tsx` — contains `drawBeamDiagram`, `stroke-dasharray`
- `frontend/src/components/sections/FeaturesSection.tsx` — contains `id="features"`, `useInView`
- `frontend/src/components/sections/FAQSection.tsx` — contains `id="faq"`, `@base-ui/react/collapsible`, `aria-expanded`
- `frontend/src/components/sections/CTASection.tsx` — contains `id="cta"`
- `frontend/src/components/sections/EmailCapture.tsx` — contains `structcalc-waitlist`, `role="alert"`, `role="status"`
- `frontend/src/components/sections/PricingSection.tsx` — contains `id="pricing"`, `blur-sm`, Lock icon
- `frontend/src/App.tsx` — contains all 5 sections in order

Tests: 23/23 passing, TypeScript: 0 errors
