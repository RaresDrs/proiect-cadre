---
phase: 03-modul-cadre-2d
plan: "05"
subsystem: frontend-visualization
tags: [typescript, react, svg, vitest, FrameDiagrams, FrameResultTabs, buildDiagramPath, wave-4]
dependency_graph:
  requires:
    - "03-01 — FrameResult/FrameBarDiagram/FrameNodeResult types in api.ts"
    - "03-03 — worldToSvg/computeBBox from frameCanvas.ts"
    - "03-04 — FrameCanvas (FrameDiagrams overlaid on same SVG viewBox)"
  provides:
    - "FrameDiagrams — M/V/N diagram filled polygon overlays + deformed shape"
    - "buildDiagramPath — SVG path geometry for perpendicular bar diagram offsets"
    - "FrameResultTabs — tab switcher (M/V/N/deformed) + copy link + export PDF"
    - "exportFramePdf — dynamic jsPDF+html2canvas PDF export"
  affects:
    - "FramePage (03-06) — imports FrameDiagrams and FrameResultTabs"
tech_stack:
  added: []
  patterns:
    - "SVG perpendicular: (ux,uy) → (uy, -ux) for 90° CW = 'above' for rightward bar in SVG y-down space"
    - "Auto-scale: max diagram offset = 15% of shortest bar pixel length"
    - "Dynamic import jsPDF/html2canvas to avoid eager bundle cost"
key_files:
  created:
    - frontend/src/components/frame/FrameDiagrams.tsx
    - frontend/src/components/frame/FrameResultTabs.tsx
  modified:
    - frontend/src/__tests__/frameDiagrams.test.ts (todos → real assertions)
decisions:
  - "Perpendicular formula is (uy, -ux) not (-uy, ux) — SVG y-down space inverts the CCW convention; (-uy,ux) pointed downward for rightward bars, causing test failure"
  - "Animation uses opacity fade instead of stroke-dasharray draw-in — jsdom does not measure SVG path lengths so dasharray=pathLength breaks in tests"
metrics:
  duration_minutes: 8
  completed_date: "2026-04-19"
  tasks_completed: 2
  files_created: 2
  files_modified: 1
---

# Phase 3 Plan 05: Result Visualization Summary

**One-liner:** FrameDiagrams M/V/N overlays + deformed shape + FrameResultTabs with export — 4 geometry tests green, TSC clean.

## What Was Built

### Task 1: FrameDiagrams + buildDiagramPath tests (TDD RED→GREEN)

Created `frontend/src/components/frame/FrameDiagrams.tsx` exporting:

| Export | Purpose |
|--------|---------|
| `buildDiagramPath(nodeI, nodeJ, values, scale)` | Closed SVG path for bar diagram polygon |
| `FrameDiagrams` | Diagram overlay component (M/V/N/deformed) |
| `DiagramTab` type | `'M' \| 'V' \| 'N' \| 'deformed'` |

Key geometry fix: perpendicular formula is `(uy, -ux)` not `(-uy, ux)`. In SVG y-down coordinate space, positive M values should plot "above" a rightward bar (lower sy). The 90° CW rotation `(ux,uy)→(uy,-ux)` achieves this correctly.

Diagram rendering:
- Positive values: `fill="#22c55e"` at 0.3 opacity, `stroke="#22c55e"` solid
- Negative values: `fill="#ef4444"` at 0.3 opacity, `stroke="#ef4444"` solid
- Auto-scale: max offset = 15% of shortest bar pixel length
- Labels: max value in green above, min value in red below
- Animation: opacity fade-in staggered 80ms per bar (opacity instead of dasharray — jsdom doesn't measure SVG path lengths)

Deformed shape (`DeformedShape` sub-component):
- Original frame: dashed `var(--muted-foreground)` lines
- Deformed frame: `var(--primary)` at 0.7 opacity
- Scale factor: ×100 (D-18)

Updated `frameDiagrams.test.ts`: 4 todo stubs → 4 real assertions (all pass).

### Task 2: FrameResultTabs

Created `frontend/src/components/frame/FrameResultTabs.tsx` exporting:

- `FrameResultTabs`: 4 tab buttons (M, V, N, Deformata) + Copy Link + Export PDF
- `exportFramePdf(title)`: async PDF export via dynamic `import('jspdf')` + `import('html2canvas')` — avoids eager bundle loading

## Self-Check: PASSED

- `frontend/src/components/frame/FrameDiagrams.tsx` — exports `buildDiagramPath`, `FrameDiagrams`, `DiagramTab`
- `frontend/src/components/frame/FrameResultTabs.tsx` — exports `FrameResultTabs`, `exportFramePdf`
- `FrameDiagrams.tsx` uses `#22c55e` (positive) and `#ef4444` (negative)
- `DeformedShape` uses `scaleFactor = 100`
- `exportFramePdf` uses dynamic `import('jspdf')` — no top-level import
- 4 tests pass in `frameDiagrams.test.ts`
- `npx tsc --noEmit` exits 0
