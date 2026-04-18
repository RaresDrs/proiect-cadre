---
phase: 03-modul-cadre-2d
plan: "02"
subsystem: backend-frame-solver
tags: [backend, pydantic, anastruct, fastapi, fem, pytest, tdd]
dependency_graph:
  requires:
    - "03-01: FrameInput/FrameResult TypeScript types and test scaffolds"
  provides:
    - "FrameInput, FrameResult Pydantic schemas (D-11)"
    - "solve_frame() FEM solver via anastruct SystemElements (D-10)"
    - "POST /api/v1/frames/solve FastAPI endpoint (D-10)"
  affects:
    - "03-03 and later: frontend useFrameSolver hook calls this endpoint"
    - "test_frame_solver.py and test_frames_api.py — now fully green"
tech_stack:
  added: []
  patterns:
    - "anastruct node ID mapping by vertex coordinate (robust vs enumerate-based)"
    - "TDD RED→GREEN for schema and solver tests before implementation"
    - "model_validator(mode='after') for cross-field FrameInput validation"
key_files:
  created:
    - backend/app/schemas/frame.py
    - backend/app/services/frame_solver.py
    - backend/app/api/v1/frames.py
    - backend/tests/test_frame_solver.py
    - backend/tests/test_frames_api.py
    - backend/tests/test_frame_schemas.py
  modified:
    - backend/app/api/v1/router.py
decisions:
  - "anastruct node IDs mapped by vertex coordinate matching, not enumerate — ensures correct support/load assignment when nodes appear out of order across bars"
  - "roller support uses direction='x' (blocks horizontal displacement, free vertical) — matches structural convention for portal frames"
  - "N diagram linearly interpolated between N_1 and N_2 (anastruct stores per-element axial as two endpoints)"
metrics:
  duration_minutes: 4
  completed_date: "2026-04-18"
  tasks_completed: 3
  files_created: 6
  files_modified: 1
---

# Phase 3 Plan 02: Frame Solver Backend Summary

**One-liner:** anastruct FEM frame solver with Pydantic schemas and FastAPI POST /api/v1/frames/solve, passing portal benchmark equilibrium checks.

## What Was Built

### Task 1: backend/app/schemas/frame.py

Created Pydantic input and result models for 2D frame analysis:

**Input models:**
- `FrameNode` — node with id, x/y (metres, Y-up), constraint (`free|pin|roller|fixed`)
- `FrameBar` — bar with id, node_i/node_j references, EI (kN·m²), EA (kN)
- `NodeLoad` — concentrated force/moment at node: Fx, Fy, Mz
- `BarLoad` — distributed load on bar: q (kN/m), q_start/q_end fractions
- `FrameInput` — aggregate with `@model_validator` rejecting: <2 nodes, no supports, invalid bar node refs

**Result models:**
- `FrameBarDiagram` — per-bar M/V/N lists (50 equally-spaced points)
- `FrameNodeResult` — per-node ux/uy/phi_z displacements
- `FrameResult` — aggregate: bar_diagrams, node_results, reactions dict, max_M/V/N

TDD: 6 RED tests confirmed failing before schema creation, 6/6 GREEN after.

### Task 2: backend/app/services/frame_solver.py

Implemented `solve_frame(data: FrameInput) -> FrameResult` using anastruct SystemElements:

1. Add all elements via `ss.add_element(location=[[x_i,y_i],[x_j,y_j]], EI=..., EA=...)`
2. Build `node_id_map` by matching our x/y coordinates to `ss.node_map[n].vertex` — this is more robust than enumerate-based mapping because anastruct assigns IDs based on unique vertex positions encountered across all add_element calls
3. Add supports (`add_support_hinged`, `add_support_roll(direction='x')`, `add_support_fixed`)
4. Add node loads (point_load, moment_load) and bar loads (q_load with negated sign for downward)
5. `ss.solve()` — direct stiffness method
6. Extract M/V from `el.bending_moment`/`el.shear_force`; N from linspace(N_1, N_2, npts)
7. Extract node results from `ss.get_node_results_system(node_id=nid)`

**Portal benchmark results** (Fx=10kN at top-left of 3m×4m portal):
- `sum(Fx reactions) ≈ 10.0 kN` (equilibrium verified)
- `sum(Fy reactions) ≈ 0.0 kN` (no vertical load, verified)
- max_M > 0 (bending present, verified)

TDD: 8 solver tests created, all GREEN.

### Task 3: backend/app/api/v1/frames.py + router.py

Created FastAPI router following beams.py pattern exactly:

```python
router = APIRouter(prefix="/frames", tags=["frames"])

@router.post("/solve", response_model=FrameResult)
def calculate_frame(data: FrameInput):
    try:
        return solve_frame(data)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
```

Registered in `router.py` alongside beams and sections. All 3 API tests pass. Full backend suite: 24/24 tests passing (no regressions).

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| Task 1 | `e67f49e` | feat(03-02): create FrameInput/FrameResult Pydantic schemas |
| Task 2 | `481bbb0` | feat(03-02): create frame_solver.py and solver tests |
| Task 3 | `d50b657` | feat(03-02): create FastAPI frames router and register in router.py |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] anastruct node ID mapping — enumerate vs vertex coordinate**
- **Found during:** Task 2, while probing anastruct API
- **Issue:** The plan's `node_id_map` used `enumerate(data.nodes)` → `i+1`, but anastruct assigns node IDs based on unique vertex positions encountered across all `add_element` calls (not per-node-list order). If bars reference nodes in non-sequential order, `i+1` would map to the wrong anastruct node ID.
- **Fix:** After adding all elements, iterate `ss.node_map` and match by `abs(v.x - node.x) < 1e-6 and abs(v.y - node.y) < 1e-6`. This is robust regardless of node ordering in `data.nodes`.
- **Files modified:** `backend/app/services/frame_solver.py`
- **Commit:** `481bbb0`

**2. [Rule 2 - Missing functionality] Added test_frame_schemas.py**
- **Found during:** Task 1
- **Issue:** The plan called for TDD on frame schemas but had no dedicated schema test file (03-01 stubs were for solver/API only).
- **Fix:** Created `backend/tests/test_frame_schemas.py` with 6 targeted tests for FrameInput validation and FrameResult structure.
- **Files modified:** `backend/tests/test_frame_schemas.py` (new)
- **Commit:** `e67f49e`

## Known Stubs

None. All production code is fully wired. The `phi_z` field uses `r.get('phi_z', r.get('Tz', 0.0))` as a safe fallback since anastruct returns rotation as 'phi_z' key in get_node_results_system.

## Self-Check: PASSED
