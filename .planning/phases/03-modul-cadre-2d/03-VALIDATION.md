---
phase: 03
slug: modul-cadre-2d
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-12
---

# Phase 03 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | vitest 4.1.4 + @testing-library/react (frontend); pytest (backend) |
| **Config file** | `frontend/vitest.config.ts` (existent); `backend/pytest.ini` sau inline |
| **Quick run command** | `cd frontend && npx vitest run --reporter=dot` |
| **Full suite command** | `cd frontend && npx vitest run && cd ../backend && python -m pytest` |
| **Estimated runtime** | ~15 seconds (frontend) + ~10 seconds (backend) |

---

## Sampling Rate

- **After every task commit:** Run `cd frontend && npx vitest run --reporter=dot`
- **After every plan wave:** Run `cd frontend && npx vitest run && cd ../backend && python -m pytest`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** ~25 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01 | 01 | 0 | REQ-03-01, REQ-03-10 | unit | `npx vitest run src/__tests__/frameHash.test.ts` | ❌ Wave 0 | ⬜ pending |
| 03-02 | 01 | 0 | REQ-03-02, REQ-03-03 | unit | `npx vitest run src/__tests__/useFrameSolver.test.ts` | ❌ Wave 0 | ⬜ pending |
| 03-03 | 01 | 0 | REQ-03-04, REQ-03-05 | unit | `npx vitest run src/__tests__/frameCanvas.test.ts` | ❌ Wave 0 | ⬜ pending |
| 03-04 | 01 | 0 | REQ-03-11 | unit | `npx vitest run src/__tests__/frameDiagrams.test.ts` | ❌ Wave 0 | ⬜ pending |
| 03-05 | 01 | 0 | REQ-03-12, REQ-03-13 | unit (RTL) | `npx vitest run src/components/frame/__tests__/FrameCanvas.test.tsx` | ❌ Wave 0 | ⬜ pending |
| 03-06 | 01 | 0 | REQ-03-14 | unit (RTL) | `npx vitest run src/pages/__tests__/FramePage.test.tsx` | ❌ Wave 0 | ⬜ pending |
| 03-07 | 01 | 0 | REQ-03-06, REQ-03-07, REQ-03-15 | unit | `cd backend && python -m pytest tests/test_frame_solver.py` | ❌ Wave 0 | ⬜ pending |
| 03-08 | 01 | 0 | REQ-03-08, REQ-03-09 | integration | `cd backend && python -m pytest tests/test_frames_api.py` | ❌ Wave 0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `frontend/src/__tests__/frameHash.test.ts` — REQ-03-01, REQ-03-10
- [ ] `frontend/src/__tests__/useFrameSolver.test.ts` — REQ-03-02, REQ-03-03
- [ ] `frontend/src/__tests__/frameCanvas.test.ts` — REQ-03-04, REQ-03-05
- [ ] `frontend/src/__tests__/frameDiagrams.test.ts` — REQ-03-11
- [ ] `frontend/src/components/frame/__tests__/FrameCanvas.test.tsx` — REQ-03-12, REQ-03-13
- [ ] `frontend/src/pages/__tests__/FramePage.test.tsx` — REQ-03-14
- [ ] `backend/tests/test_frame_solver.py` — REQ-03-06, REQ-03-07, REQ-03-15
- [ ] `backend/tests/test_frames_api.py` — REQ-03-08, REQ-03-09
- [ ] `npm install jspdf html2canvas` — dependențe noi necesare pentru export PDF (D-22)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Canvas click-to-draw vizual (nod + bară) | D-04, D-05 | Necesită interacțiune mouse real pe SVG | Deschide /frame, click pe canvas = nod, click nod→nod = bară |
| Diagrame M/T/N animate suprapuse pe bară | D-13, D-17 | Animația CSS/SVG nu se verifică ușor în jsdom | Submit calcul, observă draw-in stagger per bară |
| Deformată animată suprapusă pe cadru | D-18 | Rendering vizual | Tab Deformată — linie punctată animată |
| Export PDF cu diagrame SVG | D-22 | html2canvas fidelitate nu e testabilă automat | Buton Export PDF după calcul, verifică conținut |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
