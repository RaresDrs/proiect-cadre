---
phase: 1
slug: design-sistem-landing-page
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-11
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Vitest + @testing-library/react + jsdom |
| **Config file** | `frontend/vitest.config.ts` — none yet, Wave 0 installs |
| **Quick run command** | `cd frontend && npx vitest run --reporter=dot` |
| **Full suite command** | `cd frontend && npx vitest run` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd frontend && npx vitest run --reporter=dot`
- **After every plan wave:** Run `cd frontend && npx vitest run`
- **Before `/gsd:verify-work`:** Full suite must be green + Lighthouse audit on Vercel preview
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| REQ-1a | 01-02 | 1 | Landing sections | smoke | `npx vitest run src/__tests__/landing-sections.test.tsx` | ❌ Wave 0 | ⬜ pending |
| REQ-1b | 01-01 | 0 | Dark mode toggle | unit | `npx vitest run src/__tests__/useTheme.test.ts` | ❌ Wave 0 | ⬜ pending |
| REQ-1c | 01-03 | 2 | Dark mode FOUC | manual | `grep 'blocking\|prefers-color-scheme' frontend/index.html` | N/A | ⬜ pending |
| REQ-1d | 01-02 | 1 | Nav smooth scroll | manual | Click nav links in browser | N/A | ⬜ pending |
| REQ-1e | 01-03 | 2 | Lighthouse Performance ≥ 92 | automated | `npx lighthouse http://localhost:5173 --only-categories=performance --output json \| jq '.categories.performance.score'` | N/A | ⬜ pending |
| REQ-1f | 01-03 | 2 | Lighthouse SEO ≥ 90 | automated | `npx lighthouse http://localhost:5173 --only-categories=seo --output json \| jq '.categories.seo.score'` | N/A | ⬜ pending |
| REQ-1g | 01-03 | 2 | Responsive 320px | automated | `npx vitest run src/__tests__/responsive.test.tsx` | ❌ Wave 0 | ⬜ pending |
| REQ-1h | 01-02 | 1 | prefers-reduced-motion | unit | `npx vitest run src/__tests__/reducedMotion.test.tsx` | ❌ Wave 0 | ⬜ pending |
| REQ-1i | 01-02 | 1 | Email capture localStorage | unit | `npx vitest run src/__tests__/EmailCapture.test.tsx` | ❌ Wave 0 | ⬜ pending |
| REQ-1j | 01-01 | 0 | i18n RO/EN toggle | unit | `npx vitest run src/__tests__/useLang.test.ts` | ❌ Wave 0 | ⬜ pending |
| REQ-1k | 01-03 | 2 | PWA manifest valid | smoke | `curl http://localhost:5173/manifest.json \| jq '.name'` | N/A | ⬜ pending |
| REQ-1l | 01-01 | 0 | html lang update | unit | covered in useLang.test.ts | ❌ Wave 0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `frontend/vitest.config.ts` — config Vitest cu jsdom environment
- [ ] `frontend/src/__tests__/useTheme.test.ts` — acoperă REQ-1b (dark mode toggle)
- [ ] `frontend/src/__tests__/useLang.test.ts` — acoperă REQ-1j, REQ-1l (i18n)
- [ ] `frontend/src/__tests__/landing-sections.test.tsx` — acoperă REQ-1a (sections render)
- [ ] `frontend/src/__tests__/EmailCapture.test.tsx` — acoperă REQ-1i (email localStorage)
- [ ] `frontend/src/__tests__/reducedMotion.test.tsx` — acoperă REQ-1h (reduced motion)
- [ ] `frontend/src/__tests__/responsive.test.tsx` — acoperă REQ-1g (320px viewport)
- [ ] Install: `npm install --save-dev vitest @testing-library/react @testing-library/user-event jsdom @vitest/coverage-v8`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Dark mode FOUC | REQ-1c | Requires visual inspection — jsdom can't detect flash | Reload page in Chrome with DevTools throttling, check no white flash in dark mode |
| Nav smooth scroll | REQ-1d | Requires real browser scroll events | Click each nav link, verify smooth scroll to section |
| Framer Motion animations | REQ-1h | Visual quality check | Load landing in Chrome, verify hero reveal + scroll animations |
| Lighthouse audit | REQ-1e, REQ-1f | Score depends on real network/browser | Run `npx lighthouse https://[vercel-preview-url]` after deploy |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
