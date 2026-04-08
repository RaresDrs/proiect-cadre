# Phase 0: Setup Proiect - Research

**Researched:** 2026-04-08
**Domain:** React 18 + Vite + TypeScript + FastAPI monorepo setup, Streamlit migration, CI/CD, deployment
**Confidence:** HIGH

---

## Summary

Phase 0 stabileste infrastructura completa de proiect: un monorepo cu frontend React/Vite/TypeScript si backend FastAPI Python, pornind de la un Streamlit monolith de 2490 linii (`app.py`) care contine 4 module de calcul structural. Calculele trebuie extrase din contextul UI Streamlit si expuse ca endpoint-uri REST pure, fara dependinta de `st.session_state`.

Stack-ul ales este solid si bine sustinut in 2026. Principalele puncte de atentie sunt: (1) Python 3.14 este pe masina locala — FastAPI/Pydantic v2 functioneaza dar se recomanda explicit Python 3.12/3.13 pentru Railway deploy pentru stabilitate maxima; (2) shadcn/ui in 2026 lucreaza nativ cu Tailwind v4 via `@tailwindcss/vite` plugin, nu cu configuratia clasica `tailwind.config.js`; (3) `anastruct` 1.6.2 este deja instalat si functional pe Python 3.14 local — trebuie inclus in `requirements.txt` al backend-ului.

**Primary recommendation:** Structura monorepo simpla cu doua directoare la radacina (`frontend/` si `backend/`) fara Turborepo sau pnpm workspaces — complexitate inutila pentru un proiect cu un singur frontend si un singur backend. GitHub Actions cu path filters separate pentru fiecare director.

---

## Project Constraints (from CLAUDE.md)

- **Single key file:** `app.py` — intreaga aplicatie curenta e acolo
- **Tech stack curent:** Python + Streamlit, NumPy, Matplotlib, anastruct
- **UI si comentarii in romana** — mentinut si in noul cod
- **Target:** Aplicatie 2D structural bar calculation pentru educatie inginereasca

---

## Standard Stack

### Core — Frontend
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| react | 19.2.4 | UI framework | Latest stable, React 19 e curent |
| vite | 8.0.7 | Build tool + dev server | Standard de facto pentru React non-Next.js |
| typescript | 6.0.2 | Type safety | Obligatoriu pentru proiect scalabil |
| @vitejs/plugin-react | 6.0.1 | React + HMR in Vite | Plugin oficial |
| tailwindcss | 4.2.2 | Utility CSS | Versiunea 4 — stil nou via @import |
| @tailwindcss/vite | 4.2.2 | Tailwind v4 plugin Vite | Inlocuieste postcss config clasic |
| shadcn/ui (CLI) | latest | Component library | Instaleaza componente ca cod propriu |

### Core — Backend
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| fastapi | 0.135.3 | REST API framework | Cel mai popular Python API framework 2025 |
| uvicorn[standard] | 0.44.0 | ASGI server | Serverul standard pentru FastAPI |
| pydantic | 2.12.5 | Data validation + schemas | Integrat nativ cu FastAPI |
| numpy | 2.4.4 | Calcule numerice | Deja instalat, deja folosit in app.py |
| scipy | 1.17.1 | Calcule avansate | Deja instalat |
| anastruct | 1.6.2 | FEM solver pentru bare/grinzi | Deja instalat, folosit in app.py |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-multipart | latest | Form data in FastAPI | Daca se accepta upload-uri |
| httpx | latest | HTTP client async | Teste de integrare pentru API |
| pytest | latest | Test runner | Unit tests pentru calcule |
| pytest-asyncio | latest | Async test support | Teste pentru endpoint-uri async |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pnpm workspaces + Turborepo | npm workspaces simple | Turborepo e overkill pentru 1 frontend + 1 backend la inceput |
| Railway pentru backend | Render | Railway are Railpack (succesor Nixpacks), mai simplu pentru Python |
| FastAPI pe Vercel | FastAPI pe Railway | Vercel poate gazdui FastAPI dar Railway e mai potrivit pentru Python long-running |

**Installation — Frontend:**
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install -D @tailwindcss/vite
npx shadcn@latest init
```

**Installation — Backend:**
```bash
mkdir backend && cd backend
pip install fastapi uvicorn[standard] pydantic numpy scipy anastruct python-multipart
pip freeze > requirements.txt
```

**Version verification:** Versiunile de mai sus au fost verificate live via `npm view` si `pip index versions` la data de 2026-04-08.

---

## Architecture Patterns

### Recommended Project Structure

```
proiect-cadre/                  # Git root (monorepo simplu)
├── frontend/                   # React + Vite + TypeScript
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/             # shadcn/ui components (generate automat)
│   │   │   ├── beam/           # Componente specifice domeniului
│   │   │   └── layout/         # Header, Sidebar, etc.
│   │   ├── hooks/              # Custom React hooks
│   │   ├── lib/                # Utilitare (cn(), api client)
│   │   ├── types/              # TypeScript types pentru API
│   │   ├── pages/              # Route pages
│   │   └── main.tsx
│   ├── public/
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   └── package.json
│
├── backend/                    # FastAPI Python
│   ├── app/
│   │   ├── main.py             # Entry point, app = FastAPI()
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── router.py   # Include toate sub-routerele
│   │   │       ├── beams.py    # /api/v1/beams endpoint
│   │   │       ├── sections.py # /api/v1/sections endpoint
│   │   │       ├── frames.py   # /api/v1/frames endpoint
│   │   │       └── health.py   # /health endpoint
│   │   ├── schemas/
│   │   │   ├── beam.py         # Pydantic models pentru request/response
│   │   │   ├── section.py
│   │   │   └── frame.py
│   │   ├── services/
│   │   │   ├── beam_solver.py  # Logica din app.py extrasda
│   │   │   ├── section_calc.py
│   │   │   └── frame_solver.py
│   │   └── core/
│   │       └── config.py       # Settings, CORS origins
│   ├── tests/
│   │   ├── test_beams.py
│   │   └── test_sections.py
│   ├── requirements.txt
│   └── railway.json            # Railway deploy config
│
├── .github/
│   └── workflows/
│       ├── frontend-ci.yml     # Trigger: paths: frontend/**
│       └── backend-ci.yml      # Trigger: paths: backend/**
│
├── app.py                      # ORIGINAL — nu se sterge in Faza 0
├── CLAUDE.md
└── planning/
```

### Pattern 1: FastAPI Service Layer (Separare calcule de API)

**What:** Logica de calcul sta in `services/`, nu in router. Routerul primeste request, valideaza cu Pydantic, apeleaza service, returneaza response.

**When to use:** Intotdeauna. Permite testarea calculelor fara HTTP overhead.

**Example:**
```python
# backend/app/schemas/beam.py
from pydantic import BaseModel
from typing import List, Optional

class Support(BaseModel):
    x: float          # pozitie pe bara (m)
    type: int         # 1=pin, 2=roller, 3=fixed

class PointLoad(BaseModel):
    x: float
    fx: float = 0.0
    fy: float = 0.0

class BeamInput(BaseModel):
    length: float           # L in metri
    angle_deg: float = 0.0  # inclinare
    supports: List[Support]
    point_loads: List[PointLoad] = []
    distributed_load: float = 0.0  # q in kN/m
    q_start: float = 0.0
    q_end: Optional[float] = None
    EI: float = 1.0         # rigiditate (E*I)
    EA: float = 1.0

class DiagramPoint(BaseModel):
    x: float
    N: float
    V: float
    M: float

class BeamResult(BaseModel):
    reactions: dict
    diagrams: List[DiagramPoint]
    max_M: float
    max_V: float
    deflection: List[dict]
```

```python
# backend/app/services/beam_solver.py
import numpy as np
from anastruct import SystemElements
from app.schemas.beam import BeamInput, BeamResult

def solve_beam(data: BeamInput) -> BeamResult:
    """Pure calculation function — no Streamlit, no session_state."""
    th = np.radians(data.angle_deg)
    c_ang, s_ang = np.cos(th), np.sin(th)
    L = data.length
    
    ss = SystemElements(EI=data.EI, EA=data.EA)
    # ... logica din app.py liniile 462-525 ...
    ss.solve()
    
    return BeamResult(...)
```

```python
# backend/app/api/v1/beams.py
from fastapi import APIRouter
from app.schemas.beam import BeamInput, BeamResult
from app.services.beam_solver import solve_beam

router = APIRouter(prefix="/beams", tags=["beams"])

@router.post("/solve", response_model=BeamResult)
def calculate_beam(data: BeamInput):
    return solve_beam(data)
```

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(title="StructCalc API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # ["http://localhost:5173", "https://...vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok", "service": "StructCalc API"}
```

### Pattern 2: Vite + Tailwind v4 + shadcn/ui (2026 style)

**What:** Tailwind v4 nu mai foloseste `tailwind.config.js`. Plugin-ul `@tailwindcss/vite` inlocuieste PostCSS. CSS-ul principal are `@import "tailwindcss"`.

**When to use:** Orice proiect nou cu shadcn/ui in 2026.

**Example:**
```typescript
// frontend/vite.config.ts
import path from "path"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
```

```css
/* frontend/src/index.css */
@import "tailwindcss";
@import "tw-animate-css";

@custom-variant dark (&:is(.dark *));
/* shadcn theme variables generate automat de CLI */
```

```json
// frontend/tsconfig.app.json (adaugat de shadcn init)
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### Pattern 3: GitHub Actions cu Path Filters pentru Monorepo

**What:** Doua fisiere workflow separate, fiecare triggerat doar cand codul relevant s-a schimbat.

**Example:**
```yaml
# .github/workflows/backend-ci.yml
name: Backend CI
on:
  push:
    paths:
      - 'backend/**'
      - '.github/workflows/backend-ci.yml'
  pull_request:
    paths:
      - 'backend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'   # 3.12 pe CI — mai stabil decat 3.14
      - name: Install dependencies
        run: pip install -r backend/requirements.txt
      - name: Run tests
        run: pytest backend/tests/ -v
```

```yaml
# .github/workflows/frontend-ci.yml
name: Frontend CI
on:
  push:
    paths:
      - 'frontend/**'
      - '.github/workflows/frontend-ci.yml'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '24'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci --prefix frontend
      - run: npm run build --prefix frontend
```

### Anti-Patterns to Avoid

- **Calcule in router (anti-pattern):** Nu pune logica NumPy/anastruct direct in functia de endpoint. Separa in `services/`.
- **Session state in API:** app.py foloseste `st.session_state` — asta NU exista in FastAPI. Fiecare request trebuie sa fie stateless; clientul trimite TOATA starea in request body.
- **tailwind.config.js cu Tailwind v4:** Nu crea `tailwind.config.js` — v4 nu il mai foloseste. Va cauza conflicte.
- **FastAPI pe Vercel ca serverless:** Vercel poate rula FastAPI dar ca serverless function cu timeout de 10s. Pentru calcule FEM care pot dura mai mult, Railway cu server persistent e mai potrivit.
- **Python 3.14 pe Railway:** Python 3.14 este prea nou pentru stabilitate maxima pe servere. Foloseste Python 3.12 in `railway.json` sau `runtime.txt`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Request validation | Validare manuala cu if/else | Pydantic BaseModel | Edge cases, type coercion, error messages |
| CORS | Middleware custom | FastAPI CORSMiddleware | Greseli subtile cu preflight requests |
| Component UI | Butoane/inputuri custom din zero | shadcn/ui CLI | Accesibilitate, keyboard nav, dark mode |
| FEM solver | Implementare proprie matrix stiffness | anastruct (deja instalat) | Algoritm complex, deja testat in app.py |
| API client TypeScript | fetch() manual | Axios sau fetch cu types generate | Type safety, interceptors, error handling |
| CI cache | Fara cache | `actions/cache` sau `cache:` in setup-node | Build-uri de 2-3x mai rapide |

**Key insight:** anastruct este deja validat in productie prin app.py. Nu rescrie FEM solver-ul — extrage-l.

---

## Migration Strategy: app.py → FastAPI

### Inventar calcule in app.py (din analiza structurii)

| Modul Streamlit | Linii | Calcule de migrat | Endpoint propus |
|----------------|-------|-------------------|-----------------|
| Calcul Grinzi simplu | 235-930 | anastruct solver, reactiuni, diagrame N/T/M | `POST /api/v1/beams/solve` |
| Rezistenta Materialelor | 931-1133 | Proprietati sectiune (I, A, Wel, Wpl) | `POST /api/v1/sections/properties` |
| Statica 1 — Static Determinate | 1134-2028 | Grinda simpla, Gerber, Cadre 2D, Arc, Zabrele | `POST /api/v1/frames/solve` |
| Statica 2 — Static Nedeterminate | 2031-2490 | Grinda continua, Metoda deplasarilor, Cross, Mohr | `POST /api/v1/frames/indeterminate` |

### Strategia de extractie

**Principiu cheie:** tot codul util in app.py este DUPA liniile `if modul == "..."`. Codul inainte (liniile 1-230) sunt: imports, CSS, UI setup, functii de desenat cu matplotlib — astea NU merg in API.

Calculele pure sunt in blocurile marcate cu `# --- anastruct solver ---` si sectiunile cu numpy.

**Pasii concret pentru migrare:**
1. Identifica sectiunea de calcul (dupa `btn_calc` sau echivalent)
2. Extrage parametrii de input (tot ce vine din `st.session_state` / widgets)
3. Creeaza Pydantic schema cu acei parametri
4. Muta calculul in `services/` ca functie pura Python
5. Creeaza router endpoint care apeleaza service-ul

---

## Common Pitfalls

### Pitfall 1: Python 3.14 pe Railway/Render
**What goes wrong:** Pachetele de build (compilare C extensions) pot esua pe Python 3.14 pe servere Linux in CI/CD.
**Why it happens:** Python 3.14 este prea nou; wheel-urile precompilate pentru numpy/scipy pe Linux pot lipsi.
**How to avoid:** Specifica Python 3.12 explicit in `backend/runtime.txt` (continut: `python-3.12`) sau `railway.json`. Dezvoltarea locala poate continua pe 3.14.
**Warning signs:** `ERROR: Could not find a version that satisfies the requirement numpy` pe CI.

### Pitfall 2: Tailwind v4 vs v3 — CLI shadcn confuz
**What goes wrong:** Daca rulezi `npx shadcn@2.3.0 init` in loc de `npx shadcn@latest init`, primesti configuratie Tailwind v3 (cu `tailwind.config.js`), incompatibila cu `@tailwindcss/vite`.
**Why it happens:** Versiunile vechi de shadcn CLI genereaza config v3.
**How to avoid:** Foloseste intotdeauna `npx shadcn@latest init`. Verifica ca `index.css` contine `@import "tailwindcss"` nu `@tailwind base`.
**Warning signs:** Fisier `tailwind.config.js` creat dupa init.

### Pitfall 3: CORS intre frontend si backend
**What goes wrong:** `fetch("http://localhost:8000/api/...")` din browser primeste eroare CORS.
**Why it happens:** Browserele blocheaza cross-origin requests fara header-ul `Access-Control-Allow-Origin`.
**How to avoid:** Adauga `CORSMiddleware` in `main.py` cu `allow_origins=["http://localhost:5173"]` (portul Vite). In productie: adauga URL-ul Vercel.
**Warning signs:** Eroare in consola browser: `has been blocked by CORS policy`.

### Pitfall 4: anastruct returneaza obiecte non-serializabile
**What goes wrong:** `ss_fem.get_node_results_system()` returneaza dict cu numpy float64 care nu poate fi serializat de JSON standard.
**Why it happens:** `json.dumps()` nu stie ce e `numpy.float64`.
**How to avoid:** Converteste explicit: `float(r["Fy"])` sau configureaza FastAPI cu un custom JSON encoder. Pydantic v2 cu `model_config = ConfigDict(arbitrary_types_allowed=True)` poate ajuta.
**Warning signs:** `TypeError: Object of type float64 is not JSON serializable`.

### Pitfall 5: Vercel — `dist` folder pentru Vite
**What goes wrong:** Vercel nu gaseste build output-ul.
**Why it happens:** Vite scoate in `dist/` implicit, dar Vercel poate cauta `public/` sau `build/`.
**How to avoid:** In Vercel dashboard: `Output Directory = dist`, `Build Command = npm run build`, `Install Command = npm install`.
**Warning signs:** Deploy pe Vercel cu 404 pe toate rutele.

---

## Code Examples

### Health endpoint minimal
```python
# Source: FastAPI official docs pattern
# backend/app/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

### Pydantic v2 schema cu numpy-friendly types
```python
# Source: FastAPI + Pydantic v2 docs
from pydantic import BaseModel, field_validator
from typing import List

class BeamInput(BaseModel):
    length: float
    supports: List[dict]
    
    @field_validator('length')
    @classmethod
    def length_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Lungimea trebuie sa fie pozitiva')
        return v
```

### Vite proxy pentru API in development
```typescript
// frontend/vite.config.ts — evita CORS in development
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

### railway.json
```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

---

## Runtime State Inventory

> Faza 0 este greenfield pentru stack-ul nou; nu implica redenumire sau migrare de date. app.py ramane intact.

Nu exista stare runtime de migrat — app.py si noul proiect React+FastAPI coexista in paralel in Faza 0. Calculele sunt extrase ca cod, nu ca date.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js | Frontend build, npm | Yes | v24.14.1 | — |
| npm | Package management | Yes | 11.11.0 | — |
| Python | Backend | Yes | 3.14.3 | — |
| pip | Python packages | Yes | 25.3 | — |
| numpy | Calcule backend | Yes | 2.4.4 | — |
| scipy | Calcule avansate | Yes | 1.17.1 | — |
| anastruct | FEM solver | Yes | 1.6.2 | — |
| FastAPI | API framework | No | — | `pip install fastapi uvicorn` |
| uvicorn | ASGI server | No | — | Instalat odata cu FastAPI |
| git | Version control | Yes (repo exista) | — | — |
| PostgreSQL | DB (Faza 4) | Not needed Phase 0 | — | Omis in Faza 0 |
| Docker | Containerizare | Unknown | — | Railway detecteaza automat fara Docker |

**Missing dependencies with no fallback:**
- FastAPI si uvicorn trebuie instalate (pip install) — nu blocheaza, sunt in requirements.txt

**Missing dependencies with fallback:**
- Docker nu e necesar: Railway suporta deploy direct din GitHub fara Dockerfile

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.x |
| Config file | `backend/pytest.ini` sau `backend/pyproject.toml` — de creat in Wave 0 |
| Quick run command | `pytest backend/tests/ -x -q` |
| Full suite command | `pytest backend/tests/ -v` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-01 | `npm run dev` porneste fara erori | smoke | `npm run build --prefix frontend` (build = dev check) | Wave 0 |
| REQ-02 | `uvicorn main:app` porneste + /health functional | smoke | `pytest backend/tests/test_health.py -x` | Wave 0 |
| REQ-03 | Calculele din app.py disponibile ca REST | unit | `pytest backend/tests/test_beams.py -x` | Wave 0 |
| REQ-04 | GitHub Actions ruleaza CI | manual/verify | Push la GitHub + verifica Actions tab | N/A — manual |
| REQ-05 | Deploy Vercel + Railway functional | manual/verify | Vercel preview URL + Railway health endpoint | N/A — manual |

### Sampling Rate
- **Per task commit:** `pytest backend/tests/ -x -q`
- **Per wave merge:** `npm run build --prefix frontend && pytest backend/tests/ -v`
- **Phase gate:** Build frontend OK + toate testele backend verzi + /health pe Railway raspunde

### Wave 0 Gaps
- [ ] `backend/tests/test_health.py` — verifica GET /health returneaza 200
- [ ] `backend/tests/test_beams.py` — verifica POST /api/v1/beams/solve cu date simple
- [ ] `backend/tests/test_sections.py` — verifica calculul proprietati sectiune
- [ ] `backend/pytest.ini` — configuratie pytest
- [ ] Framework install: `pip install pytest httpx pytest-asyncio`

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| tailwind.config.js | @import "tailwindcss" + @tailwindcss/vite | Tailwind v4 (2025) | Nu mai exista config JS pentru Tailwind |
| CRA (Create React App) | Vite | 2022-2023 | CRA deprecated, Vite e standard |
| PostCSS pentru Tailwind | @tailwindcss/vite plugin | Tailwind v4 | Fara postcss.config.js |
| shadcn@2.x cu Tailwind v3 | shadcn@latest cu Tailwind v4 | 2025 | CLI genereaza cod diferit |
| Nixpacks pe Railway | Railpack pe Railway | 2025 | Nixpacks deprecated, Railpack e noul default |
| Pydantic v1 in FastAPI | Pydantic v2 obligatoriu | FastAPI 0.126+ | Python 3.14 nu suporta Pydantic v1 |

**Deprecated/outdated:**
- `create-react-app`: nu mai e recomandat — foloseste `npm create vite@latest`
- `tailwind.config.js` cu Tailwind v4: nu mai functioneaza — CSS-only config
- Pydantic v1 pe Python 3.14: incompatibil — warning UserWarning la import

---

## Open Questions

1. **PostgreSQL + Supabase Auth — cand se introduce?**
   - What we know: Roadmap spune Faza 4 pentru conturi
   - What's unclear: Daca schema DB se defineste in Faza 0 sau nu
   - Recommendation: NU in Faza 0 — adauga SQLAlchemy + Supabase in Faza 4. Faza 0 = API stateless fara DB.

2. **React Three Fiber pentru vizualizari 3D**
   - What we know: Mentionat in roadmap pentru "viitor"
   - What's unclear: Daca se instaleaza acum sau mai tarziu
   - Recommendation: Instaleaza dependintele de baza (`@react-three/fiber`, `@react-three/drei`, `three`) in Faza 0 dar nu implementa nimic — reduce riscul de conflicte de versiuni mai tarziu.

3. **D3.js vs Recharts pentru diagrame M/V/N**
   - What we know: Roadmap mentioneaza D3.js
   - What's unclear: D3 are curba de invatare mare; Recharts e mai rapid pentru diagrame simple
   - Recommendation: Instaleaza D3 in Faza 0, implementa in Faza 2 — nu decide pattern-ul acum.

---

## Sources

### Primary (HIGH confidence)
- shadcn/ui official docs — https://ui.shadcn.com/docs/installation/vite — Tailwind v4 setup steps
- shadcn/ui Tailwind v4 guide — https://ui.shadcn.com/docs/tailwind-v4 — confirmat v4 e default in 2026
- Railway FastAPI guide — https://docs.railway.com/guides/fastapi — deploy steps Railway
- PyPI FastAPI — versiune 0.135.3 verificata live 2026-04-08
- npm registry — versiuni React 19.2.4, Vite 8.0.7, TypeScript 6.0.2 verificate live
- pip index versions — FastAPI 0.135.3, uvicorn 0.44.0 verificate live

### Secondary (MEDIUM confidence)
- FastAPI best practices (zhanymkanov) — https://github.com/zhanymkanov/fastapi-best-practices — patterns Router/Service/Schema
- GitHub Actions monorepo path filters — https://blog.logrocket.com/creating-separate-monorepo-ci-cd-pipelines-github-actions/ — path triggers CI
- Python 3.14 + Pydantic compatibility — https://github.com/fastapi/fastapi/discussions/14191 — confirmat Pydantic v1 incompatibil cu 3.14

### Tertiary (LOW confidence)
- Railway Railpack replacing Nixpacks — mentionat in search results, neverificat in docs oficiale Railway

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — toate versiunile verificate live via npm/pip la 2026-04-08
- Architecture: HIGH — patterns din FastAPI best practices + shadcn official docs
- Migration strategy: MEDIUM — bazat pe analiza structurii app.py (2490 linii, 4 module identificate)
- Pitfalls: HIGH — Python 3.14 compat verificat via GitHub Issues fastapi; Tailwind v4 vs v3 verificat via shadcn docs; restul din experienta documentata

**Research date:** 2026-04-08
**Valid until:** 2026-05-08 (30 zile — stack relativ stabil)
