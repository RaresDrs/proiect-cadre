---
phase: 03-modul-cadre-2d
plan: "01"
subsystem: frontend-types, test-scaffolds
tags: [types, typescript, vitest, pytest, wave-0, tdd]
dependency_graph:
  requires: []
  provides:
    - "FrameInput/FrameResult TypeScript types in frontend/src/types/api.ts"
    - "8 Wave 0 test scaffold files in RED state (all todos)"
    - "jspdf and html2canvas installed in frontend"
  affects:
    - "All Phase 3 frontend files that import from @/types/api"
    - "03-02-PLAN.md — implement frame utilities and backend solver"
tech_stack:
  added:
    - "jspdf ^4.2.1 — PDF export for frame results"
    - "html2canvas ^1.4.1 — canvas capture for PDF generation"
  patterns:
    - "it.todo() stubs for Wave 0 TDD scaffolding (Nyquist rule)"
    - "pytest.skip() stubs for backend test scaffolding"
key_files:
  created:
    - frontend/src/__tests__/frameHash.test.ts
    - frontend/src/__tests__/useFrameSolver.test.ts
    - frontend/src/__tests__/frameCanvas.test.ts
    - frontend/src/__tests__/frameDiagrams.test.ts
    - frontend/src/pages/__tests__/FramePage.test.tsx
    - backend/tests/test_frame_solver.py
    - backend/tests/test_frames_api.py
  modified:
    - frontend/src/types/api.ts
    - frontend/package.json
decisions:
  - "jsPDF installed with html2canvas peer dep — both packages available for Phase 3 PDF export"
  - "Test scaffolds use it.todo() not commented-out imports — vitest counts todos without failing"
  - "pages/__tests__ directory created alongside existing __tests__ to match Phase 2 pattern"
metrics:
  duration_minutes: 4
  completed_date: "2026-04-18"
  tasks_completed: 2
  files_created: 7
  files_modified: 2
---

# Phase 3 Plan 01: Wave 0 Type Contracts and Test Scaffolds Summary

**One-liner:** FrameInput/FrameResult TypeScript contracts + 8 vitest/pytest scaffold files in it.todo state, plus jsPDF and html2canvas installed.

## What Was Built

### Task 1: Extend api.ts with FrameInput / FrameResult type contracts

Extended `frontend/src/types/api.ts` with 8 new exported types for Phase 3 (Modul Cadre 2D):

- `ConstraintType` — union type `'free' | 'pin' | 'roller' | 'fixed'`
- `FrameNode` — node with id, x/y coordinates (metres, Y-up), constraint
- `FrameBar` — bar with id, node_i, node_j, EI, EA properties
- `NodeLoad` — point load at node: Fx, Fy, Mz
- `BarLoad` — distributed load on bar: q, q_start, q_end fractions
- `FrameInput` — aggregate input: nodes, bars, node_loads, bar_loads
- `FrameBarDiagram` — per-bar M/V/N diagram arrays returned by backend
- `FrameNodeResult` — per-node ux/uy/phi_z displacement results
- `FrameResult` — full solver output: bar_diagrams, node_results, reactions, max_M/V/N

All existing BeamInput, BeamResult, SectionInput, SectionResult types unchanged. `npx tsc --noEmit` exits 0.

### Task 2: Install jsPDF + html2canvas and write 8 Wave 0 test scaffolds

**Dependencies installed:** `jspdf@4.2.1`, `html2canvas@1.4.1` added to frontend/package.json.

**Frontend test scaffolds (all using it.todo — 22 todos total):**

| File | REQs | Todos |
|------|------|-------|
| `frameHash.test.ts` | REQ-03-01, REQ-03-10 | 4 |
| `useFrameSolver.test.ts` | REQ-03-02, REQ-03-03 | 4 |
| `frameCanvas.test.ts` | REQ-03-04, REQ-03-05 | 8 |
| `frameDiagrams.test.ts` | REQ-03-11 | 4 |
| `FramePage.test.tsx` | REQ-03-14 | 5 |

**Backend test scaffolds (all using pytest.skip):**

| File | REQs | Tests |
|------|------|-------|
| `test_frame_solver.py` | REQ-03-06, REQ-03-07, REQ-03-15 | 6 skips |
| `test_frames_api.py` | REQ-03-08, REQ-03-09 | 3 skips |

`npx vitest run` on all 4 frontend scaffold files completes with 22 todos — no parse errors, no crashes.

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| Task 1 | `e30a3da` | feat(03-01): extend api.ts with FrameInput/FrameResult type contracts |
| Task 2 | `27c782c` | feat(03-01): install jspdf/html2canvas and write 8 Wave 0 test scaffolds |

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

The test files themselves are intentional stubs (it.todo / pytest.skip). They exist to satisfy the Nyquist rule — implementations come in 03-02-PLAN.md and later. This is by design.

No production code stubs were created.

## Self-Check: PASSED

- `frontend/src/types/api.ts` — contains FrameInput, FrameResult, ConstraintType (verified)
- `frontend/src/__tests__/frameHash.test.ts` — exists (verified)
- `frontend/src/__tests__/useFrameSolver.test.ts` — exists (verified)
- `frontend/src/__tests__/frameCanvas.test.ts` — exists (verified)
- `frontend/src/__tests__/frameDiagrams.test.ts` — exists (verified)
- `frontend/src/pages/__tests__/FramePage.test.tsx` — exists (verified)
- `backend/tests/test_frame_solver.py` — exists (verified)
- `backend/tests/test_frames_api.py` — exists (verified)
- Commit `e30a3da` — confirmed in git log
- Commit `27c782c` — confirmed in git log
- `npx tsc --noEmit` — exits 0 (TS OK)
- `npx vitest run` on 4 frontend files — 22 todos, no errors
