---
phase: 03-modul-cadre-2d
plan: "03"
subsystem: frontend-utilities
tags: [typescript, vitest, tdd, frameHash, frameCanvas, useFrameSolver, wave-2]
dependency_graph:
  requires:
    - "03-01 — FrameInput/FrameResult type contracts in frontend/src/types/api.ts"
  provides:
    - "encodeFrameHash/decodeFrameHash — URL-safe round-trip encoding for FrameInput (D-19)"
    - "worldToSvg/svgToWorld/snapToGrid/hitTestNode/hitTestBar — canvas coordinate math (D-06, D-07)"
    - "useFrameSolver hook — fetch + state for /api/v1/frames/solve (D-10)"
  affects:
    - "03-04 — FrameCanvas component will import from frameCanvas.ts"
    - "03-05 — FramePage will import useFrameSolver and encodeFrameHash"
tech_stack:
  added: []
  patterns:
    - "TDD RED-GREEN: test scaffolds from 03-01 filled with real assertions, implementation then written to pass"
    - "Y-axis inversion in worldToSvg: sy = height - margin - (wy - minY) * scale"
    - "Point-to-segment distance for accurate bar hit testing"
    - "useCallback for solve/reset to prevent unnecessary re-renders when passed as props"
key_files:
  created:
    - frontend/src/lib/frameHash.ts
    - frontend/src/lib/frameCanvas.ts
    - frontend/src/hooks/useFrameSolver.ts
  modified:
    - frontend/src/__tests__/frameHash.test.ts
    - frontend/src/__tests__/frameCanvas.test.ts
    - frontend/src/__tests__/useFrameSolver.test.ts
    - frontend/src/__tests__/setup.ts
decisions:
  - "computeBBox included in frameCanvas exports (not in plan) — required by hit-test tests to build BBox from nodes, follows existing pattern"
  - "setup.ts merge conflict resolved by keeping both comment variants merged cleanly"
metrics:
  duration_minutes: 5
  completed_date: "2026-04-18"
  tasks_completed: 3
  files_created: 3
  files_modified: 4
---

# Phase 3 Plan 03: Frontend Utility Libraries Summary

**One-liner:** frameHash URL encoding, frameCanvas Y-inverted coordinate math with hit testing, and useFrameSolver fetch hook — 3 tested utilities (19 passing tests) for Phase 3 canvas feature.

## What Was Built

### Task 1: frameHash.ts + frameHash.test.ts (TDD RED → GREEN)

Created `frontend/src/lib/frameHash.ts` implementing:

- `encodeFrameHash(input: FrameInput): string` — btoa(encodeURIComponent(JSON.stringify(input))) for URL-safe hash sharing
- `decodeFrameHash(hash: string): FrameInput | null` — inverse with null guards: empty string, malformed base64, missing nodes/bars arrays

4 tests all pass:
- Round-trip encode/decode preserves all fields (nodes.length=4, bars.length=3, Fx=10)
- Null for empty string
- Null for malformed base64 (`!!!not-valid-base64!!!`)
- Null when nodes or bars array missing from decoded object

Also fixed a merge conflict in `setup.ts` (duplicate IntersectionObserver comment markers from git cherry-pick).

### Task 2: frameCanvas.ts + frameCanvas.test.ts (TDD RED → GREEN)

Created `frontend/src/lib/frameCanvas.ts` implementing 6 exported functions:

| Function | Purpose |
|----------|---------|
| `worldToSvg` | World coords → SVG px, Y-inverted, aspect-ratio preserved |
| `svgToWorld` | Inverse of worldToSvg for click-to-world conversion |
| `computeBBox` | Bounding box from FrameNode array with padding |
| `snapToGrid` | Round to nearest grid multiple (0.3→0.5, 0.8→1.0) |
| `hitTestNode` | Returns node.id within threshold px, null otherwise |
| `hitTestBar` | Returns bar.id using point-to-segment distance, null otherwise |

11 tests all pass (3 worldToSvg, 4 snapToGrid, 2 hitTestNode, 2 hitTestBar).

Key implementation detail: Y-inversion formula `sy = height - margin - (wy - minY) * scale` ensures higher world Y produces lower SVG y coordinate, matching SVG's top-down coordinate system.

### Task 3: useFrameSolver.ts + useFrameSolver.test.ts (TDD RED → GREEN)

Created `frontend/src/hooks/useFrameSolver.ts` implementing:

- State: `{ result: FrameResult | null, loading: boolean, error: string | null }`
- `solve(input: FrameInput)` — POST to `/api/v1/frames/solve`, handles 200 / non-ok / network error
- `reset()` — clears result and error
- Both `solve` and `reset` wrapped in `useCallback` (consistent with useBeamSolver pattern)

4 tests all pass:
- 200 response: result set to mockResult, error null, loading false
- 422 response: result null, error contains "Cadrul nu are reazeme" from detail field
- Network error: result null, error truthy string
- reset(): result null, error null after prior successful solve

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| Task 1 | `f9ed5a3` | feat(03-03): implement frameHash encode/decode with round-trip tests |
| Task 2 | `1ee9fad` | feat(03-03): implement frameCanvas utilities with canvas math tests |
| Task 3 | `d5da449` | feat(03-03): implement useFrameSolver hook with fetch state management tests |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Merge conflict in setup.ts**
- **Found during:** Task 1 (test run failed with parse error)
- **Issue:** Cherry-picking 03-01 commits introduced a git conflict marker (`<<<<<<< HEAD` / `>>>>>>>`) in `frontend/src/__tests__/setup.ts` at line 20, causing vitest transform to fail
- **Fix:** Removed conflict markers, kept the more informative comment from the incoming branch
- **Files modified:** `frontend/src/__tests__/setup.ts`
- **Commit:** `f9ed5a3` (included in Task 1 commit)

**2. [Rule 2 - Missing functionality] computeBBox not in plan but required**
- **Found during:** Task 2 (test file needed computeBBox to build BBox without hardcoding values)
- **Issue:** Test assertions require a real BBox derived from the test nodes, not hardcoded values, to validate hit-test accuracy
- **Fix:** Added `computeBBox` export to frameCanvas.ts (7 lines) — purely additive, no behavioral change to other functions
- **Files modified:** `frontend/src/lib/frameCanvas.ts`
- **Commit:** `1ee9fad`

## Known Stubs

None — all three libraries are fully implemented. The remaining test scaffold files (frameDiagrams.test.ts, FramePage.test.tsx) are out of scope for this plan and remain as it.todo stubs per the 03-01 design.

## Self-Check: PASSED

- `frontend/src/lib/frameHash.ts` — exists, exports encodeFrameHash + decodeFrameHash
- `frontend/src/lib/frameCanvas.ts` — exists, exports worldToSvg, svgToWorld, computeBBox, snapToGrid, hitTestNode, hitTestBar
- `frontend/src/hooks/useFrameSolver.ts` — exists, exports useFrameSolver
- 19 tests pass across 3 test files (4 + 11 + 4)
- `npx tsc --noEmit` exits 0
- Commit `f9ed5a3` — Task 1
- Commit `1ee9fad` — Task 2
- Commit `d5da449` — Task 3
