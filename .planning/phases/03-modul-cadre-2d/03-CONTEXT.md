# Phase 3: Modul Cadre 2D - Context

**Gathered:** 2026-04-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Editor vizual interactiv pentru construirea unui cadru 2D (noduri + bare), rezolvat prin metoda rigidităților (direct stiffness method) cu un nou endpoint FastAPI. Rezultatele includ: diagrame M/T/N animate suprapuse pe fiecare bară, deformata animată, și export rezultate.

Nu intră în scope: cadre 3D, plăci, autentificare/salvare server-side (Phase 4), editor grinzi continue (Phase 2 extended), mobile app (Phase 5).

</domain>

<decisions>
## Implementation Decisions

### Rută & navigare
- **D-01:** Rută separată `/frame` pentru editorul de cadre. Nu se modifică ruta `/beam` existentă.
- **D-02:** Navbar primește două link-uri separate: „Grindă 2D" → `/beam` și „Cadru 2D" → `/frame`. Nu dropdown, nu toggle. Cele două module sunt distincte.
- **D-03:** Pagina `/frame` refolosește RootLayout (Navbar + Footer) identic cu `/beam` — consistență de brand.

### Editor canvas — interacțiune
- **D-04:** Mod de editare **hibrid**: canvas SVG pentru desenat vizual + câmpuri numerice editabile per element selectat. Utilizatorul poate desena pe canvas SAU introduce coordonate/proprietăți manual.
- **D-05:** Interacțiune canvas (stilul Strian/SkyCiv click-to-draw):
  - Click pe canvas gol → adaugă nod la coordonatele cursorului (snap la grid)
  - Click pe nod → selectează nodul; click pe alt nod → adaugă bară între ele
  - Toolbar sus cu moduri: **Add Node** / **Add Bar** / **Select** / **Delete**
  - Nodul selectat deschide un panou lateral cu câmpuri editabile: x, y, tip constrângere (liber / pin / roller / încastrare)
  - Bara selectată deschide panou lateral cu câmpuri: EI, EA, unghi (pentru bare înclinate), sarcini aplicate pe bară
- **D-06:** Canvas cu **grid snap automat** — linii de grid subtile vizibile, snap la 0.5m implicit. Utilizatorul poate modifica coordonatele exact din panou lateral chiar dacă snap-ul nu e perfect.
- **D-07:** Canvas implementat ca SVG pur (fără bibliotecă externă Konva/React Flow) — consistent cu abordarea BeamPreview din Phase 2. Interactivitate via event handlers SVG (onMouseDown, onMouseMove, onMouseUp).

### Model de date — cadru
- **D-08:** Un cadru este definit ca:
  - `nodes[]`: `{id, x, y, constraint: "free" | "pin" | "roller" | "fixed"}`
  - `bars[]`: `{id, node_i, node_j, EI, EA}` — bare înclinate suportate implicit (coordonate x/y definesc unghiul)
  - `node_loads[]`: `{node_id, Fx, Fy, Mz}` — forțe/momente concentrate în noduri
  - `bar_loads[]`: `{bar_id, q, q_start, q_end}` — sarcini distribuite pe bare
- **D-09:** EI și EA au valori implicite (21000 kN·m², 2.1M kN) — aceleași ca în Phase 2, editabile per bară.

### Motor de calcul — backend
- **D-10:** Solver-ul rulează în **backend FastAPI** — nou endpoint `POST /api/v1/frames/solve`. Abordare identică cu `app.py` și `beam_solver.py` (anastruct `SystemElements`). anastruct suportă cadre cu elemente înclinate și noduri cu 3 grade de libertate.
- **D-11:** Noi scheme Pydantic: `FrameInput` și `FrameResult` în `backend/app/schemas/frame.py`. Nu se modifică `beam.py` existent.
- **D-12:** `FrameResult` include per bară: diagrama M/T/N (listă de puncte), deplasări nodale (ux, uy, φ per nod), reacțiuni în reazeme.

### Vizualizare rezultate — diagrame
- **D-13:** Diagramele M/T/N se afișează **suprapuse pe canvas-ul cadrului**, per bară — stilul SkyCiv. Nu panouri separate.
- **D-14:** Tabs de selecție deasupra canvas-ului rezultat: **M | T | N | Deformată**. Un singur tip activ la un moment dat.
- **D-15:** Colorare cu semn: valori pozitive → verde semitransparent (#22c55e cu alpha 0.3), valori negative → roșu semitransparent (#ef4444 cu alpha 0.3). Umplutură + linie contur solidă.
- **D-16:** Valori numerice max/min afișate per bară (label lângă vârful diagramei). Hover → tooltip cu valoarea exactă la poziția x pe bară.
- **D-17:** Animație la submit — draw-in progresiv per bară cu stagger (~80ms între bare), identic ca animația StructuralDiagram de pe landing page. Respectă `prefers-reduced-motion` (apare instant fără animație).
- **D-18:** Deformata (tab „Deformată") — forma deformată a cadrului animată peste forma originală (linie punctată). Factor de scală exagerat pentru vizibilitate (ex. ×100).

### Sharing & persistență
- **D-19:** URL hash sharing identic cu Phase 2 — starea FrameInput serializată ca JSON → base64 în hash-ul URL (`/frame#<base64>`). La deschidere cu hash → populează automat și execută calculul.
- **D-20:** Salvare în `localStorage` (cheia `structcalc-frame-last`) la fiecare submit.
- **D-21:** Buton „Copiază link" după calcul — aceleași pattern ca BeamPage.

### Export
- **D-22:** Buton „Export PDF" după calcul — client-side cu jsPDF + html2canvas, identic ca Phase 2 (D-18). Raportul include: schema cadrului, diagramele active, reacțiuni tabulare.

### Claude's Discretion
- Dimensiunile exacte ale canvas-ului (px) și logica de zoom/pan (opțional în Phase 3)
- Dimensiunea nodurilor și stilul vizual al barelor pe canvas (grosime, culori dark/light)
- Iconițele pentru tipurile de constrângere în canvas (triunghi pin, rolă, încastrare)
- Grid snap resolution editabilă de utilizator vs fixă la 0.5m
- Logica de validare a cadrului (cadru cinematic → mesaj de eroare)

</decisions>

<specifics>
## Specific Ideas

- „Ca Strian" — referință pentru interacțiunea click-to-draw. Strian are cel mai bun UX pentru desenat cadre.
- „Colorate cu semne aferente, să se vadă fiecare valoare în parte" — diagrame cu umplutură color-codată și labels per bară vizibile mereu (nu doar la hover).
- „Animație ca grinda de pe site" — draw-in progresiv cu stagger, exact ca animația StructuralDiagram din HeroSection.
- „Să se poată face în ambele moduri" — canvas drawing ȘI input numeric manual. Nu one-or-the-other.
- Motorul de calcul rămâne backend (anastruct) pentru Phase 3 — va fi revizuit ulterior dacă e nevoie.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Backend (existent — de extins)
- `backend/app/schemas/beam.py` — Pattern Pydantic existent (BeamInput/BeamResult) — de urmat pentru FrameInput/FrameResult
- `backend/app/services/beam_solver.py` — Pattern anastruct existent — de urmat pentru frame_solver.py
- `backend/app/api/v1/beams.py` — Pattern router FastAPI existent — de urmat pentru frames.py

### Frontend — Phase 2 (de refolosit)
- `frontend/src/components/beam/BeamPreview.tsx` — SVG preview pattern (de extins pentru canvas interactiv)
- `frontend/src/hooks/useBeamSolver.ts` — Pattern hook fetch (de replicat ca useFrameSolver.ts)
- `frontend/src/lib/beamHash.ts` — Pattern URL hash (de replicat ca frameHash.ts)
- `frontend/src/pages/BeamPage.tsx` — Structura paginii de calcul (de urmat pentru FramePage.tsx)

### Design system (Phase 1 — de respectat)
- `.planning/phases/01-design-sistem-landing-page/01-CONTEXT.md` — D-01..D-32: paletă culori, font Geist, dark mode, i18n pattern
- `frontend/src/components/layout/` — RootLayout, Navbar, Footer — de refolosit direct

### Animație referință
- `frontend/src/components/sections/` — StructuralDiagram din HeroSection — stilul animației draw-in de replicat în diagrame cadru

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/src/components/beam/BeamPreview.tsx` — SVG renderer existent; logica de desenat bare/noduri pe SVG poate fi extinsă pentru canvas interactiv
- `frontend/src/hooks/useBeamSolver.ts` — Fetch hook cu loading/error/reset state — de replicat ca `useFrameSolver.ts`
- `frontend/src/lib/beamHash.ts` — encode/decode base64 JSON — de replicat ca `frameHash.ts`
- `frontend/src/hooks/useTheme.ts` — Dark mode hook — canvas-ul cadru citește tema pentru culori
- `frontend/src/hooks/useLang.ts` — i18n hook — toate textele noi prin același pattern

### Established Patterns
- CSS tokens (`--color-primary`, `--color-background`, etc.) — diagramele D3/SVG folosesc CSS variables, nu culori hardcodate
- i18n ca plain TS object în `i18n.ts` — Phase 3 adaugă cheile RO/EN pentru `/frame` în același fișier
- React Router v7 cu `<Route>` în `App.tsx` — se adaugă `<Route path="/frame" element={<FramePage />} />`
- Test pattern: vitest + @testing-library/react cu MemoryRouter — de urmat pentru teste noi

### Integration Points
- `frontend/src/App.tsx` — Se adaugă ruta `/frame` → `<FramePage />`
- `frontend/src/components/layout/Navbar.tsx` — Se adaugă link „Cadru 2D" → `/frame` lângă „Grindă 2D"
- `backend/app/api/v1/router.py` — Se include noul router `frames.py`
- `frontend/vite.config.ts` — Proxy `/api` existent acoperă și noul endpoint `/api/v1/frames/solve`

</code_context>

<deferred>
## Deferred Ideas

- **Zoom/pan pe canvas** — poate fi adăugat ca îmbunătățire ulterioară (Phase 3.1 sau backlog)
- **Cadre 3D** — faza separată, nu intră în Phase 3
- **Solver client-side (Wasm/JS)** — posibil în Phase 5 (offline mobile), backend rămâne pentru Phase 3
- **Salvare în cont (server-side)** — Phase 4 (auth)
- **Validare automată tip cadru** (simplu rezemat, consolă, portal etc.) — backlog
- **Grinzi continue multi-deschidere** din Phase 2 deferred — posibil Phase 3 extension

</deferred>

---

*Phase: 03-modul-cadre-2d*
*Context gathered: 2026-04-12*
