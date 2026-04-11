---
phase: 01-design-sistem-landing-page
plan: 03
subsystem: ui
tags: [pwa, seo, lighthouse, service-worker, manifest, og-tags, json-ld, responsive, vitest]

# Dependency graph
requires:
  - phase: 01-design-sistem-landing-page
    provides: index.html base structure with dark mode blocking script, lang="ro", manifest link (01-01)
provides:
  - manifest.json with name=StructCalc, theme_color=#2563EB, display=standalone
  - sw.js cache-first service worker (no Workbox) for static assets
  - PNG placeholder icons (192x192, 512x512, 180x180 apple-touch)
  - og-image.svg placeholder OG image
  - Full SEO meta block (og:title, og:description, og:image, twitter:card, canonical, description, robots)
  - JSON-LD structured data (WebSite type) in index.html
  - Responsive tests at 320px (render-without-crash + class verification)
  - Lighthouse Performance=98, SEO=100, Accessibility=100, Best Practices=100
affects: [01-02, phase-6-landing-page-dedicat]

# Tech tracking
tech-stack:
  added: [service-worker (manual, no Workbox), Web App Manifest, JSON-LD schema.org]
  patterns:
    - Cache-first for static assets (JS/CSS/fonts/icons), network-first for HTML navigation in SW
    - Blocking inline script in <head> before CSS for FOUC-free dark mode
    - Placeholder PNG icons (1x1 base64) — replaced with real icons in Phase 6

key-files:
  created:
    - frontend/public/manifest.json
    - frontend/public/sw.js
    - frontend/public/icon-192.png
    - frontend/public/icon-512.png
    - frontend/public/apple-touch-icon.png
    - frontend/public/og-image.svg
    - frontend/src/__tests__/responsive.test.tsx
    - frontend/src/__tests__/setup.ts
  modified:
    - frontend/index.html

key-decisions:
  - "Placeholder 1x1 PNG icons used — real icons deferred to Phase 6 (no design assets yet)"
  - "Manual service worker (no Workbox) per D-27 — keeps Phase 1 scope minimal and bundle lean"
  - "og-image.svg served directly — SVG OG image works for dev/preview; PNG conversion deferred to Phase 6"
  - "IntersectionObserver mock changed to class-based — arrow functions cannot be used as constructors with new"

patterns-established:
  - "SW versioning: CACHE_VERSION = 'structcalc-v1' — bump on each deploy to invalidate old caches"
  - "Cache-first for /assets/* and static extensions, network-first for request.mode === 'navigate'"

requirements-completed: [REQ-1c, REQ-1e, REQ-1f, REQ-1g, REQ-1k]

# Metrics
duration: ~15min
completed: 2026-04-11
---

# Phase 1 Plan 03: PWA + SEO + Lighthouse Summary

**PWA manifest, cache-first service worker, full SEO meta block with JSON-LD, and responsive tests — Lighthouse Performance=98, SEO=100, Accessibility=100, Best Practices=100**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-04-11
- **Completed:** 2026-04-11
- **Tasks:** 3 (2 auto + 1 checkpoint)
- **Files modified:** 9

## Accomplishments

- PWA manifest (name=StructCalc, theme_color=#2563EB, display=standalone) + placeholder PNG icons + SW registration wired into index.html
- Manual cache-first service worker (no Workbox) caching static assets; network-first for HTML navigation
- Full SEO meta block: og:title, og:description, og:image, twitter:card, canonical URL, meta description, robots, JSON-LD WebSite schema
- Responsive test suite (320px render-without-crash + class verification) with corrected IntersectionObserver mock
- Lighthouse audit passed: Performance=98, SEO=100, Accessibility=100, Best Practices=100 (all exceed plan thresholds of >=92 / >=90)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create manifest.json + PWA icons + service worker** - `a643c18` (feat)
2. **Task 2: Add SEO meta tags + JSON-LD + responsive test** - `a643c18` (feat — cherry-pick applied via stash, included in same commit)
3. **Task 3: Lighthouse checkpoint (human-verified)** - Approved: Performance=98, SEO=100, Accessibility=100, Best Practices=100

## Lighthouse Scores

| Category       | Score | Threshold | Result |
|----------------|-------|-----------|--------|
| Performance    | 98    | >=92      | PASS   |
| SEO            | 100   | >=90      | PASS   |
| Accessibility  | 100   | —         | PASS   |
| Best Practices | 100   | —         | PASS   |

## Files Created/Modified

- `frontend/public/manifest.json` — PWA manifest: name=StructCalc, theme_color=#2563EB, display=standalone, 192+512 icons
- `frontend/public/sw.js` — Manual service worker: cache-first static assets, network-first HTML, version structcalc-v1
- `frontend/public/icon-192.png` — Placeholder 1x1 PNG (real icons deferred to Phase 6)
- `frontend/public/icon-512.png` — Placeholder 1x1 PNG
- `frontend/public/apple-touch-icon.png` — Placeholder 1x1 PNG (180x180 slot)
- `frontend/public/og-image.svg` — 1200x630 SVG OG image with StructCalc branding
- `frontend/index.html` — Added: SW registration script, SEO meta block (og:*, twitter:card, canonical, description, robots), JSON-LD WebSite schema; preserved: blocking dark mode script, lang="ro", manifest link from 01-01
- `frontend/src/__tests__/responsive.test.tsx` — 320px render-without-crash + min-h-screen class verification
- `frontend/src/__tests__/setup.ts` — IntersectionObserver mock fixed to class-based constructor

## Decisions Made

- Placeholder 1x1 PNG icons — no design assets available in Phase 1; manifest validation passes, real icons added in Phase 6
- Manual SW without Workbox — keeps bundle lean and Phase 1 scope focused; Workbox evaluated for Phase 6
- og-image.svg used directly — browser OG crawlers accept SVG for preview; PNG export deferred to Phase 6
- IntersectionObserver mock required class syntax — arrow function mock from initial setup broke `new IntersectionObserver()` call pattern in section components

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed IntersectionObserver mock from arrow function to class**
- **Found during:** Task 2 (responsive test execution)
- **Issue:** `setup.ts` used `vi.fn()` arrow function for IntersectionObserver mock; arrow functions cannot be used as constructors with `new`, causing test failures
- **Fix:** Replaced with class-based mock implementing `observe`, `unobserve`, `disconnect` methods
- **Files modified:** `frontend/src/__tests__/setup.ts`
- **Verification:** Vitest suite passes with class-based mock
- **Committed in:** `a643c18`

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Fix necessary for test correctness. No scope creep.

## Issues Encountered

- Task 2 cherry-pick resulted in empty commit (content was already applied via stash during Task 1) — both tasks effectively landed in commit `a643c18`. No data loss, all files verified present.

## User Setup Required

None — no external service configuration required. PWA icons are placeholder; replace with real 192x192 and 512x512 PNGs in Phase 6.

## Known Stubs

- `frontend/public/icon-192.png` — 1x1 placeholder PNG; replace with real branded icon in Phase 6
- `frontend/public/icon-512.png` — 1x1 placeholder PNG; replace with real branded icon in Phase 6
- `frontend/public/apple-touch-icon.png` — 1x1 placeholder PNG; replace with real 180x180 icon in Phase 6
- `frontend/public/og-image.svg` — SVG placeholder; convert to 1200x630 PNG for production OG crawlers in Phase 6

## Next Phase Readiness

- Phase 1 complete: design system, all landing page sections, dark mode, PWA, SEO, Lighthouse all passing
- Phase 2 (Modul Grinzi 2D) can begin — no blockers from Phase 1
- Phase 6 (Landing Page Dedicat) will need real PNG icons and PNG OG image to replace SVG/placeholder stubs

---

## Self-Check: PASSED

- `a643c18` exists: verified in git log
- `frontend/public/manifest.json` exists: confirmed (created in Task 1)
- `frontend/public/sw.js` exists: confirmed
- `frontend/index.html` contains `og:title`: confirmed
- `frontend/index.html` contains `application/ld+json`: confirmed
- Lighthouse scores: Performance=98, SEO=100, Accessibility=100, Best Practices=100 (human-verified checkpoint approved)

---
*Phase: 01-design-sistem-landing-page*
*Completed: 2026-04-11*
