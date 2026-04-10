---
phase: 00-setup-proiect
plan: 03
subsystem: infra
tags: [github-actions, vercel, railway, ci-cd, monorepo]

requires:
  - phase: 00-setup-proiect (plan 01)
    provides: frontend/ React scaffold with package.json and build scripts
  - phase: 00-setup-proiect (plan 02)
    provides: backend/ FastAPI scaffold with requirements.txt and pytest

provides:
  - GitHub Actions CI for frontend (npm ci + vite build on push)
  - GitHub Actions CI for backend (pip install + pytest on push)
  - frontend/vercel.json with SPA rewrite + Railway API proxy
  - .vercelignore excluding backend/ from Vercel builds
  - Vercel frontend live and proxying /api/* to Railway backend
  - Railway backend live at proiect-cadre-production.up.railway.app

affects: [all future phases — CI runs on every push, deploys are live]

tech-stack:
  added: [github-actions, vercel, railway]
  patterns: [monorepo path-filtered CI, Vercel rewrite proxy to Railway]

key-files:
  created:
    - .github/workflows/frontend-ci.yml
    - .github/workflows/backend-ci.yml
    - frontend/vercel.json
    - .vercelignore
  modified: []

key-decisions:
  - "Vercel proxy approach — /api/* rewrites to Railway URL directly in vercel.json instead of env vars, so same frontend code works in dev (Vite proxy) and prod (Vercel)"
  - "Root Directory = frontend in Vercel dashboard so vercel.json is picked up correctly"
  - "Path-filtered GitHub Actions — frontend CI only triggers on frontend/** changes, backend CI on backend/**"

patterns-established:
  - "Monorepo CI: separate workflow files per sub-project with path filters"
  - "API routing: relative /api paths in frontend, Vercel rewrites to Railway in prod, Vite proxy in dev"

requirements-completed: []

duration: multi-session (Apr 8 + Apr 10)
completed: 2026-04-10
---

# Phase 00-03: CI/CD + Deploy Configuration Summary

**GitHub Actions CI pipelines live, Vercel frontend + Railway backend deployed and connected via /api proxy rewrites**

## Performance

- **Duration:** Multi-session (initial CI setup Apr 8, Vercel→Railway wiring Apr 10)
- **Completed:** 2026-04-10
- **Tasks:** 3 (2 auto + 1 human checkpoint)
- **Files created:** 4

## Accomplishments
- GitHub Actions frontend CI: runs `npm ci` + `vite build` on every push to `frontend/`
- GitHub Actions backend CI: runs `pip install` + `pytest` on every push to `backend/`
- `frontend/vercel.json` configures SPA catch-all + proxies `/api/*` and `/health` to Railway
- `.vercelignore` excludes `backend/`, `app.py`, `.planning/` from Vercel builds
- Railway backend live and returning `{"status":"ok"}` from `/health`
- Vercel frontend live and connected to Railway via rewrite proxy

## Task Commits

1. **Task 1: GitHub Actions CI workflows** — created in worktree during Phase 0 execution (Apr 8)
2. **Task 2: vercel.json + .vercelignore** — `fd492b4` (config: point Vercel rewrites to Railway production API)
3. **Task 3: Human checkpoint** — approved by user (Apr 10) — Vercel and Railway confirmed live

## Files Created/Modified
- `.github/workflows/frontend-ci.yml` — React build CI, path-filtered to `frontend/**`
- `.github/workflows/backend-ci.yml` — pytest CI, path-filtered to `backend/**`
- `frontend/vercel.json` — SPA rewrite + `/api/*` proxy to `https://proiect-cadre-production.up.railway.app`
- `.vercelignore` — excludes backend/, app.py, .planning/, __pycache__

## Decisions Made
- Vercel rewrite proxy instead of env vars — same frontend code works unchanged in dev and prod
- Path-filtered CI to avoid triggering unnecessary builds in a monorepo

## Deviations from Plan
None — plan executed as written across two sessions.

## Issues Encountered
None — Vercel and Railway were already configured in a prior session; this plan formalized the config.

## User Setup Required
None - Vercel and Railway were connected manually in dashboards (already done).

## Next Phase Readiness
- Full CI/CD pipeline live — every push to main triggers appropriate tests
- Frontend on Vercel, backend on Railway, connected via proxy
- Ready for Phase 1: Design Sistem & Landing Page

---
*Phase: 00-setup-proiect*
*Completed: 2026-04-10*
