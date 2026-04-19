---
phase: 03-modul-cadre-2d
plan: "04"
subsystem: frontend-ui
tags: [typescript, react, svg, vitest, FrameCanvas, FrameToolbar, FrameSidePanel, wave-3]
dependency_graph:
  requires:
    - "03-01 — FrameNode/FrameBar/NodeLoad/BarLoad types in frontend/src/types/api.ts"
    - "03-03 — worldToSvg/svgToWorld/snapToGrid/hitTestNode/hitTestBar/computeBBox in frameCanvas.ts"
  provides:
    - "FrameToolbar — mode switcher with keyboard shortcuts 1/2/3/4"
    - "FrameSidePanel — property editor for selected node/bar"
    - "FrameCanvas — interactive SVG editor with click-to-draw state machine"
  affects:
    - "03-05 — FramePage will import FrameCanvas + FrameToolbar and wire useFrameSolver"
tech_stack:
  added:
    - "shadcn badge, separator, alert-dialog components"
  patterns:
    - "Controlled canvas state lifted to FramePage — FrameCanvas receives nodes/bars as props"
    - "getSvgCoords guards against zero-size rect in jsdom — uses dims.width fallback"
    - "Grid lines computed from bbox extent with +1e-9 epsilon for float equality"
key_files:
  created:
    - frontend/src/components/frame/FrameToolbar.tsx
    - frontend/src/components/frame/FrameSidePanel.tsx
    - frontend/src/components/frame/FrameCanvas.tsx
    - frontend/src/components/frame/__tests__/FrameCanvas.test.tsx
    - frontend/src/components/ui/badge.tsx
    - frontend/src/components/ui/separator.tsx
    - frontend/src/components/ui/alert-dialog.tsx
  modified:
    - frontend/src/lib/i18n.ts (frame.* keys added to both ro and en)
decisions:
  - "getBoundingClientRect returns 0 in jsdom — getSvgCoords uses dims.width/height fallback so click tests work without layout"
  - "03-03 worktree was not merged to master — had to git merge worktree-agent-ab02b201 before starting this plan"
metrics:
  duration_minutes: 12
  completed_date: "2026-04-19"
  tasks_completed: 3
  files_created: 7
  files_modified: 1
---

# Phase 3 Plan 04: Core UI Components Summary

**One-liner:** FrameToolbar + FrameSidePanel + FrameCanvas SVG editor with 4-mode state machine — 4 tests green, TSC clean.

## What Was Built

### Task 1: shadcn install + FrameToolbar + i18n keys

Installed `badge`, `separator`, `alert-dialog` shadcn components. Added 38 `frame.*` i18n keys to both `ro` and `en` objects in `i18n.ts`.

Created `FrameToolbar.tsx`:
- Exports `EditorMode` type: `'add_node' | 'add_bar' | 'select' | 'delete'`
- 4 mode buttons with lucide icons, keyboard shortcut badges, aria-pressed
- Delete mode styled with `var(--destructive)` color
- Solve button right-aligned, disabled when `!canSolve || loading`

### Task 2: FrameSidePanel

Created `FrameSidePanel.tsx` with two sub-components:
- `NodePanel` — x/y number inputs, constraint Select dropdown, Fx/Fy/Mz load inputs
- `BarPanel` — EI/EA number inputs, q distributed load input
- Returns `null` when nothing selected, renders as `<aside>` with `aria-label`
- Missing loads fall back to `EMPTY_NODE_LOAD` / `EMPTY_BAR_LOAD` defaults

### Task 3: FrameCanvas + tests

Created `FrameCanvas.tsx` — the interactive SVG editor:

| Feature | Implementation |
|---------|---------------|
| Grid lines | Computed from bbox, 0.5m step, `var(--border)` at 0.4 opacity |
| Nodes | `<circle>` r=6 (unselected) / r=8 (selected), `data-testid="node-{id}"` |
| Bars | `<line>` strokeWidth=2/3, `data-testid="bar-{id}"` |
| Constraint icons | pin=triangle, roller=triangle+circle, fixed=rect+hatches |
| Load arrows | Blue-500 arrows for Fx/Fy |
| Pending bar | Dashed preview line to mouse position |
| Keyboard | 1/2/3/4→mode, Escape→cancel/deselect |
| State machine | add_node / add_bar / select / delete modes |

Key fix: `getSvgCoords` uses `rect.width || dims.width` fallback since `getBoundingClientRect()` returns 0 in jsdom tests.

4 tests all pass:
- Renders SVG canvas element
- Shows empty state when no nodes
- Click in add_node mode calls onNodesChange with `{ constraint: 'free' }`
- Renders node and bar elements with correct data-testid

Also resolved: 03-03 worktree (`agent-ab02b201`) had never been merged — performed `git merge worktree-agent-ab02b201` and resolved planning file conflicts before starting this plan.

## Self-Check: PASSED

- `frontend/src/components/frame/FrameToolbar.tsx` — exists, exports `EditorMode` + `FrameToolbar`
- `frontend/src/components/frame/FrameSidePanel.tsx` — exists, exports `FrameSidePanel`
- `frontend/src/components/frame/FrameCanvas.tsx` — exists, imports `worldToSvg` from `frameCanvas`
- `frontend/src/components/frame/__tests__/FrameCanvas.test.tsx` — 4 tests pass
- `frontend/src/lib/i18n.ts` — contains `frame.page.title` and `frame.toolbar.add_node` in both locales
- `npx tsc --noEmit` exits 0
