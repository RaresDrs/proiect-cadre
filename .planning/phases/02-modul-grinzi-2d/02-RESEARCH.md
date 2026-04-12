# Phase 2: Modul Grinzi 2D - Research

**Researched:** 2026-04-12
**Domain:** React Router v7, D3.js v7, jsPDF v4, URL hash serialization, FastAPI FEM integration
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Routing & navigare**
- D-01: Se adaugă `react-router-dom` v7. Ruta `/` = landing existent. Ruta `/beam` = pagina calculator.
- D-02: Pagina `/beam` refolosește nav-ul și footer-ul din landing (nu full-screen app separată).
- D-03: Landing CTA „Incepe calculul" navighează la `/beam` (nu scroll smooth).

**Input — definire grindă**
- D-04: Layout split: form stânga (lg:w-1/2), SVG preview live dreapta (lg:w-1/2). Mobile: form sus, preview jos.
- D-05: Rezemări: articulație (pin, tip 1), reazem mobil (roller, tip 2), încastrare (fixed, tip 3). Oricâte reazeme la orice poziție x.
- D-06: Încărcări: forțe concentrate (Fx, Fy la x) și sarcină uniform distribuită (q între x_start și x_end). Sarcini triunghiulare/trapezoidale excluse.
- D-07: SVG preview actualizat în timp real (debounce 150ms). Arată schema grinzii fără FEM.
- D-08: Butonul „Calculează" trimite cererea API și declanșează animațiile.

**Diagrame M/T/N + deflecție**
- D-09: Bibliotecă vizualizare: D3.js exclusiv. Nicio altă bibliotecă de charting.
- D-10: 4 panouri stivuite vertical: M, T, N, Deflecție. Fiecare cu titlu + scală + unitate.
- D-11: Animație: SVG path stroke-dasharray draw-in, stagger (M → T → N → Deflecție), ~400ms/panou, ease-out cubic. Respectă prefers-reduced-motion.
- D-12: Hover tooltip: linie verticală + tooltip valori exacte M/T/N/deflecție. D3 bisector.
- D-13: Fără zoom/pan pe diagrame în Phase 2.

**Sharing & persistență**
- D-14: BeamInput JSON → base64 în URL hash `/beam#<base64>`. La deschidere cu hash: populare input + calcul automat.
- D-15: Buton „Copiază link" — generează și copiează URL cu hash în clipboard.
- D-16: Salvare în `localStorage` la cheia `structcalc-beam-last` la fiecare submit.
- D-17: Salvare în cont (server-side) EXCLUSĂ din Phase 2.

**Export PDF**
- D-18: Client-side cu `jsPDF` + `html2canvas`. Conținut: schemă, diagrame, reacțiuni, valori maxime, date input, header StructCalc.
- D-19: Butonul „Export PDF" apare DOAR după ce calculul a fost executat.

**Integrare backend**
- D-20: Se folosesc endpoint-urile existente din `backend/app/api/v1/beams.py` și schema BeamInput/BeamResult. Schema NU se modifică în Phase 2.
- D-21: Apel API via proxy Vite `/api/v1/beams/solve`. Error handling: toast/banner la 4xx/5xx.

### Claude's Discretion
- Exact spacing, typography scales pe pagina `/beam`
- Culori pentru umplerea diagramelor (pozitiv vs negativ)
- Skeleton loading state între submit și răspuns API
- Iconițe pentru tipurile de reazem în SVG preview
- Forma exactă a tooltip-ului hover

### Deferred Ideas (OUT OF SCOPE)
- Grinzi continue multi-deschidere
- Sarcini triunghiulare/trapezoidale
- Salvare în cont (server-side) — Phase 4
- Zoom/pan pe diagrame
- Editor vizual drag-and-drop pe canvas
</user_constraints>

---

## Summary

Phase 2 adds a fully interactive 2D beam calculator at `/beam`, wired to the existing FastAPI FEM solver, visualized with D3.js, and shareable via URL hash. The codebase is healthy: 25 tests pass, Phase 1 design system is complete, and the existing proxy, hooks, and layout components are all reusable.

The primary integration challenge is installing `react-router-dom` v7 and refactoring `App.tsx` from a flat component to a router with a shared layout. The current `App.tsx` renders everything inline — it must become a `RouterProvider` with two routes: `/` (LandingPage) and `/beam` (BeamPage), both wrapped in a layout that includes `<Navbar>` and `<Footer>`.

D3.js diagrams in React require the `useRef + useEffect` pattern (not JSX-rendered SVG children) because D3 imperatively mutates the DOM. The dark-mode CSS variable system from Phase 1 (`var(--brand-primary)`, `var(--brand-bg)`) means D3 code reads `getComputedStyle` values rather than hardcoding colors. The `jsPDF` v4 import changed to `jspdf` named export; `html2canvas` v1.4.1 remains the latest stable.

**Primary recommendation:** Install `react-router-dom@7`, `d3@7`, `@types/d3@7`, `jspdf@4`, `html2canvas@1` together in one npm command. Scaffold the router in `main.tsx`, extract `LandingLayout` wrapper, add `BeamPage` as a lazy-loaded route.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| react-router-dom | 7.14.0 | Client-side routing `/` → `/beam` | Locked by D-01; React 19 compatible |
| d3 | 7.9.0 | SVG diagrams, bisector tooltip, scales | Locked by D-09; de-facto standard for custom SVG charts |
| @types/d3 | 7.4.3 | TypeScript types for D3 | Companion to d3@7 |
| jspdf | 4.2.1 | PDF generation client-side | Locked by D-18; latest major; ESM-native in v4 |
| html2canvas | 1.4.1 | Capture SVG panels as images for PDF | Locked by D-18; stable; latest |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| shadcn Input, Select, Label | (via `npx shadcn add`) | Form fields for beam definition | D-04 mentions Button.tsx is the only shadcn component so far; add Input/Select/Label for beam form |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| d3 | recharts / visx | User locked D3; recharts simpler but less control over stroke-dasharray animation |
| jspdf + html2canvas | @react-pdf/renderer | @react-pdf is server-rendered, harder to include SVG captures; jsPDF+html2canvas is client-only |
| BrowserRouter | createHashRouter | Hash strategy would conflict with the base64 hash already used for state (D-14 uses `location.hash` for data, not routing) |

**Installation:**
```bash
cd frontend
npm install react-router-dom@7 d3@7 jspdf@4 html2canvas@1
npm install --save-dev @types/d3@7
```

**Version verification (confirmed 2026-04-12):**
```
react-router-dom: 7.14.0 (npm registry)
d3: 7.9.0
@types/d3: 7.4.3
jspdf: 4.2.1
html2canvas: 1.4.1
```

---

## Architecture Patterns

### Recommended Project Structure

```
frontend/src/
├── pages/
│   ├── LandingPage.tsx       # Extracts current App.tsx content (sections)
│   └── BeamPage.tsx          # New: beam calculator, lazy-loaded
├── components/
│   ├── layout/
│   │   ├── Navbar.tsx        # Unchanged (reused on both routes)
│   │   ├── Footer.tsx        # Unchanged
│   │   └── RootLayout.tsx    # NEW: wraps Navbar + <Outlet /> + Footer
│   ├── beam/
│   │   ├── BeamInputForm.tsx  # Form: length, supports list, loads list
│   │   ├── BeamPreview.tsx    # Live SVG schema (no FEM, debounced 150ms)
│   │   ├── DiagramPanel.tsx   # One D3 diagram pane (M or T or N or defl)
│   │   └── BeamDiagrams.tsx   # Orchestrates 4x DiagramPanel with stagger
│   └── ui/
│       └── button.tsx        # Existing
├── hooks/
│   ├── useTheme.ts           # Existing
│   ├── useLang.ts            # Existing
│   ├── useInView.ts          # Existing
│   └── useBeamSolver.ts      # NEW: fetch wrapper for /api/v1/beams/solve
├── lib/
│   ├── i18n.ts               # Extend with beam.* keys
│   ├── beamHash.ts           # NEW: encode/decode BeamInput ↔ URL hash
│   └── beamPdf.ts            # NEW: jsPDF + html2canvas export logic
└── main.tsx                  # Add RouterProvider here
```

### Pattern 1: react-router-dom v7 BrowserRouter with shared layout

**What:** Add `<BrowserRouter>` in `main.tsx`, define routes in `App.tsx` using `<Routes>/<Route>`, with a shared `<RootLayout>` that renders `<Navbar>`, `<Outlet>`, `<Footer>`.

**When to use:** The app has 2 routes both sharing the same nav/footer shell (D-02).

**Why BrowserRouter not createHashRouter:** The app uses `location.hash` for beam state serialization (D-14). If the router itself used hash strategy, `window.location.hash` would be consumed by the router and not available for the base64 payload. BrowserRouter uses `pathname`; hash is free.

**Example:**
```typescript
// main.tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
)
```

```typescript
// App.tsx (refactored)
import { Routes, Route } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import { RootLayout } from '@/components/layout/RootLayout'
import LandingPage from '@/pages/LandingPage'

const BeamPage = lazy(() => import('@/pages/BeamPage'))

export default function App() {
  return (
    <Routes>
      <Route element={<RootLayout />}>
        <Route path="/" element={<LandingPage />} />
        <Route path="/beam" element={
          <Suspense fallback={<div className="min-h-screen" />}>
            <BeamPage />
          </Suspense>
        } />
      </Route>
    </Routes>
  )
}
```

```typescript
// RootLayout.tsx
import { Outlet } from 'react-router-dom'
import { Navbar } from './Navbar'
import { Footer } from './Footer'

export function RootLayout() {
  return (
    <div className="bg-[var(--brand-bg)] text-[var(--brand-text)] min-h-screen">
      <Navbar />
      <main>
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}
```

**Navbar CTA update needed:** The Navbar's "Incepe gratuit" button currently calls `scrollTo('cta')`. After router is added, `<Link to="/beam">` or `useNavigate` replaces the scroll call for this button (D-03).

**Testing implication:** Existing `landing-sections.test.tsx` renders `<App />` directly without a Router wrapper. After refactor, the test must wrap with `<MemoryRouter>` or render `<LandingPage>` directly.

### Pattern 2: D3 diagrams in React — useRef + useEffect

**What:** D3 imperatively selects and mutates DOM nodes. In React the correct pattern is:
1. Render an empty `<svg ref={svgRef} />` in JSX
2. In `useEffect`, run all D3 selection/append/attr/transition logic
3. Clean up by selecting and removing all D3-appended children on re-run

**Why not d3-in-JSX:** Mixing React-managed VDOM with D3 mutations causes double-renders and flickering. D3 owns the SVG interior; React only owns the container ref.

**Dark mode:** D3 must not hardcode color strings. Read CSS variables via:
```typescript
const accent = getComputedStyle(document.documentElement)
  .getPropertyValue('--brand-accent').trim()
```
This resolves correctly for both light and dark mode because the `.dark` class on `<html>` (set by `useTheme`) changes the CSS variable values before `getComputedStyle` reads them. Re-run `useEffect` when `theme` changes.

**Example:**
```typescript
// DiagramPanel.tsx
import { useRef, useEffect } from 'react'
import * as d3 from 'd3'
import { useTheme } from '@/hooks/useTheme'
import type { DiagramPoint } from '@/types/beam'

interface Props {
  data: DiagramPoint[]
  field: 'M' | 'V' | 'N'
  label: string
  unit: string
  animateDelay: number   // stagger: M=0, T=400, N=800, defl=1200
}

export function DiagramPanel({ data, field, label, unit, animateDelay }: Props) {
  const svgRef = useRef<SVGSVGElement>(null)
  const { theme } = useTheme()

  useEffect(() => {
    if (!svgRef.current || !data.length) return
    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()   // clean previous render

    const W = svgRef.current.clientWidth || 600
    const H = 160
    const margin = { top: 20, right: 20, bottom: 30, left: 50 }

    const xScale = d3.scaleLinear()
      .domain([data[0].x, data[data.length - 1].x])
      .range([margin.left, W - margin.right])

    const yVals = data.map(d => d[field] as number)
    const yScale = d3.scaleLinear()
      .domain([d3.min(yVals)! * 1.1, d3.max(yVals)! * 1.1])
      .range([H - margin.bottom, margin.top])

    const area = d3.area<DiagramPoint>()
      .x(d => xScale(d.x))
      .y0(yScale(0))
      .y1(d => yScale(d[field] as number))

    const line = d3.line<DiagramPoint>()
      .x(d => xScale(d.x))
      .y(d => yScale(d[field] as number))

    // Fill area: positive=green/20, negative=red/20
    svg.append('path')
      .datum(data)
      .attr('d', area)
      .attr('fill', 'url(#diagFill)')   // use CSS variable fill defined in SVG defs

    // Stroke line with draw-in animation
    const path = svg.append('path')
      .datum(data)
      .attr('d', line)
      .attr('fill', 'none')
      .attr('stroke', 'var(--brand-accent)')
      .attr('stroke-width', 2)

    // stroke-dasharray draw-in — prefers-reduced-motion handled by CSS
    const totalLength = (path.node() as SVGPathElement).getTotalLength()
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches

    if (!prefersReduced) {
      path
        .attr('stroke-dasharray', `${totalLength} ${totalLength}`)
        .attr('stroke-dashoffset', totalLength)
        .transition()
        .delay(animateDelay)
        .duration(400)
        .ease(d3.easeCubicOut)
        .attr('stroke-dashoffset', 0)
    }

    // Axes
    svg.append('g')
      .attr('transform', `translate(0,${H - margin.bottom})`)
      .call(d3.axisBottom(xScale).ticks(5))

    svg.append('g')
      .attr('transform', `translate(${margin.left},0)`)
      .call(d3.axisLeft(yScale).ticks(4))

  }, [data, field, theme])  // re-run when theme changes so colors update

  return <svg ref={svgRef} width="100%" height={160} />
}
```

### Pattern 3: D3 bisector hover tooltip

**What:** Track `mousemove` on SVG overlay rect, use `d3.bisector` to find nearest data point, show a vertical crosshair line and a floating `<div>` tooltip positioned via JS.

```typescript
// Inside the same useEffect, after building scales:
const bisect = d3.bisector<DiagramPoint, number>(d => d.x).left

// Transparent overlay for mouse events
svg.append('rect')
  .attr('width', W - margin.left - margin.right)
  .attr('height', H - margin.top - margin.bottom)
  .attr('transform', `translate(${margin.left},${margin.top})`)
  .attr('fill', 'none')
  .attr('pointer-events', 'all')
  .on('mousemove', function(event) {
    const [mx] = d3.pointer(event)
    const xVal = xScale.invert(mx + margin.left)
    const idx = bisect(data, xVal)
    const d = data[Math.min(idx, data.length - 1)]
    // position tooltip div via ref or state
  })
  .on('mouseleave', () => { /* hide tooltip */ })
```

### Pattern 4: URL hash base64 encoding (D-14)

**What:** Serialize `BeamInput` as `JSON.stringify` → `btoa(encodeURIComponent(...))` → store in `window.location.hash`. Reverse on load.

**Why encodeURIComponent before btoa:** btoa fails on non-Latin1 characters. encodeURIComponent first ensures safe ASCII for btoa.

```typescript
// lib/beamHash.ts
import type { BeamInput } from '@/types/beam'

export function encodeBeamHash(input: BeamInput): string {
  return btoa(encodeURIComponent(JSON.stringify(input)))
}

export function decodeBeamHash(hash: string): BeamInput | null {
  try {
    const raw = hash.startsWith('#') ? hash.slice(1) : hash
    return JSON.parse(decodeURIComponent(atob(raw))) as BeamInput
  } catch {
    return null
  }
}

export function applyBeamHash(input: BeamInput): void {
  window.location.hash = encodeBeamHash(input)
}
```

**On page load in BeamPage:**
```typescript
useEffect(() => {
  const hash = window.location.hash
  if (hash.length > 1) {
    const decoded = decodeBeamHash(hash)
    if (decoded) {
      setFormState(decoded)
      triggerSolve(decoded)   // auto-calculate
    }
  } else {
    // Try localStorage restore
    const saved = localStorage.getItem('structcalc-beam-last')
    if (saved) {
      try { setFormState(JSON.parse(saved)) } catch { /* ignore */ }
    }
  }
}, [])  // empty deps — run once on mount
```

### Pattern 5: API wiring — useBeamSolver hook

**What:** The existing endpoint is `POST /api/v1/beams/solve`. Vite proxy maps `/api` → `http://localhost:8000`. In production, the Railway backend URL must be set via env var. The fetch pattern:

```typescript
// hooks/useBeamSolver.ts
import { useState, useCallback } from 'react'
import type { BeamInput, BeamResult } from '@/types/beam'

interface SolverState {
  result: BeamResult | null
  loading: boolean
  error: string | null
}

export function useBeamSolver() {
  const [state, setState] = useState<SolverState>({ result: null, loading: false, error: null })

  const solve = useCallback(async (input: BeamInput) => {
    setState({ result: null, loading: true, error: null })
    try {
      const res = await fetch('/api/v1/beams/solve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(input),
      })
      if (!res.ok) {
        const detail = await res.json().catch(() => ({}))
        throw new Error(detail?.detail ?? `HTTP ${res.status}`)
      }
      const data: BeamResult = await res.json()
      setState({ result: data, loading: false, error: null })
    } catch (err) {
      setState({ result: null, loading: false, error: (err as Error).message })
    }
  }, [])

  return { ...state, solve }
}
```

**API contract (from beam.py):**
- Endpoint: `POST /api/v1/beams/solve`
- Request body: `BeamInput` — required fields: `length` (float > 0), `supports` (array of `{x, type}`). Optional: `point_loads`, `distributed_load`, `q_start`, `q_end`, `EI`, `EA`, `angle_deg`.
- Response: `BeamResult` — `reactions` (dict), `diagrams` (array of `{x, N, V, M}`), `max_M`, `max_V`, `max_N`, `deflection` (array of `{x, ux, uy}`).
- Error response on invalid input: HTTP 422 with `{ detail: "..." }`.

**Note on diagram fields:** The backend returns `V` (shear) not `T`. The frontend labels it "T (Forță tăietoare)" in the UI per Romanian convention but reads `d.V` from the response.

### Pattern 6: jsPDF v4 with html2canvas

**What:** jsPDF v4 changed the import — it is now ESM-native:

```typescript
// lib/beamPdf.ts
import { jsPDF } from 'jspdf'
import html2canvas from 'html2canvas'

export async function exportBeamPdf(
  containerRef: React.RefObject<HTMLDivElement>,
  title: string
): Promise<void> {
  if (!containerRef.current) return

  const canvas = await html2canvas(containerRef.current, {
    scale: 2,               // high-DPI
    useCORS: true,
    backgroundColor: null,  // transparent — PDF bg is white
  })

  const imgData = canvas.toDataURL('image/png')
  const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })

  const pageW = pdf.internal.pageSize.getWidth()
  const imgH = (canvas.height / canvas.width) * pageW

  pdf.text('StructCalc — Raport Grindă 2D', 14, 14)
  pdf.addImage(imgData, 'PNG', 0, 24, pageW, imgH)

  // If content overflows one page, add a new page
  if (imgH + 24 > pdf.internal.pageSize.getHeight()) {
    pdf.addPage()
  }

  pdf.save(`${title}.pdf`)
}
```

**SVG capture caveat:** `html2canvas` cannot natively capture SVG elements that rely on external CSS variables at print time. Workaround: before calling `html2canvas`, inline the computed CSS color values into the SVG `style` attributes, or render diagrams to a `<canvas>` element instead of SVG (convert with `d3` + `context2d`). The simplest approach: wrap diagrams in a `<div>` with explicit `background-color` CSS (not a variable) and use `html2canvas` with `scale: 2`.

**Romanian text encoding:** jsPDF v4 uses UTF-8 by default for `pdf.text()`. Romanian diacritics (ă, â, î, ș, ț) render correctly without extra configuration in v4. In jsPDF v2 they required a custom font; v4 resolved this.

### Anti-Patterns to Avoid

- **D3 in JSX:** Never use `d3.select` on React-managed SVG children rendered via JSX. D3 and React will fight over the DOM. Use `useRef` and let D3 own the interior.
- **useEffect with missing deps for D3:** Always include `theme` in the dep array — if theme changes but data doesn't, the diagram must re-render with new CSS variable values.
- **btoa without encodeURIComponent:** Raw `JSON.stringify` may produce characters outside Latin1 (e.g., if a future field contains Romanian text). Always `encodeURIComponent` first.
- **createHashRouter for routing:** Hash router consumes `location.hash`, which is also used for the base64 beam state (D-14). Use `BrowserRouter` instead.
- **Modifying backend schemas:** D-20 explicitly forbids modifying `BeamInput`/`BeamResult` in Phase 2.
- **jsPDF v2 import pattern:** `import jsPDF from 'jspdf'` (default) is the v2 pattern. v4 uses `import { jsPDF } from 'jspdf'` (named).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| SVG axis rendering | Custom tick + label logic | `d3.axisBottom`, `d3.axisLeft` | D3 handles tick formatting, overflow, domain → range mapping |
| Finding nearest data point on hover | Binary search loop | `d3.bisector` | Edge cases with duplicate x values, out-of-range cursor |
| PDF generation | Canvas serialization + PDF byte writing | `jsPDF` | PDF spec is complex; page overflow, image compression, text encoding handled |
| DOM-to-image capture | Manual SVG serialization | `html2canvas` | Cross-origin iframes, pseudo-elements, z-index stacking all require specialized handling |
| URL-safe encoding | Custom base64 variant | `encodeURIComponent` + `btoa` | Native browser APIs, no bundle cost |
| Scale computation | Manual min/max + linear interpolation | `d3.scaleLinear`, `d3.scaleOrdinal` | Handles NaN, Infinity, nice tick counts |

**Key insight:** D3's value in this phase is not just charting — it's the complete SVG manipulation ecosystem (scales, axes, bisector, transitions). Using any subset of it properly is cheaper than hand-rolling even one axis renderer.

---

## Common Pitfalls

### Pitfall 1: Landing page tests break after App.tsx refactor

**What goes wrong:** `landing-sections.test.tsx` renders `<App />` directly. After adding `<BrowserRouter>` to `main.tsx` and refactoring `App.tsx` to use `<Routes>`, the test throws: "You should not render `<Route>` or withRouter() outside a `<Router>`".

**Why it happens:** Tests import `App` without the `BrowserRouter` wrapper (which now lives in `main.tsx`).

**How to avoid:** Either (a) wrap `<App />` in `<MemoryRouter>` in the test, or (b) extract `LandingPage` into its own component and test that directly. Option (b) is cleaner and matches the new file structure.

**Warning signs:** `Error: useHref() may be used only in the context of a <Router> component` in test output.

### Pitfall 2: D3 diagram renders blank SVG on first paint

**What goes wrong:** `svgRef.current.clientWidth` returns `0` when the component renders off-screen or before the browser lays out the page.

**Why it happens:** `clientWidth` is 0 in jsdom (tests) and possibly 0 during SSR or initial layout.

**How to avoid:** Add a fallback: `const W = svgRef.current.clientWidth || 600`. For tests, mock `clientWidth` via `Object.defineProperty` on the SVGElement in the test's `beforeEach`.

### Pitfall 3: D3 transitions do not clean up on React re-render

**What goes wrong:** If `useEffect` fires mid-animation (e.g., user edits form during draw-in), the old transition continues on the removed node, causing React warnings about unmounted state updates.

**Why it happens:** D3 transitions are asynchronous and hold a reference to the DOM node.

**How to avoid:** At the top of `useEffect`, call `svg.selectAll('*').remove()` which also cancels active transitions on those nodes. D3 automatically cancels transitions when the element is removed from the DOM.

### Pitfall 4: URL hash and react-router-dom navigation conflict

**What goes wrong:** If `<Link to="/beam#someData">` is used, react-router tries to interpret the hash as an anchor and calls `scrollTo`. The base64 payload (which is not a DOM id) causes a no-op scroll.

**Why it happens:** react-router-dom's `<Link>` treats the hash as an anchor fragment.

**How to avoid:** Never put the base64 payload in the link `to` prop. Instead: navigate to `/beam` programmatically with `useNavigate('/beam')`, then set `window.location.hash = payload` after navigation completes, or use `useNavigate('/beam', { replace: false })` followed by `history.replaceState(null, '', '#' + payload)`.

### Pitfall 5: html2canvas misses SVG content with CSS variables

**What goes wrong:** The captured PNG is blank or shows default colors instead of diagram colors.

**Why it happens:** `html2canvas` does not fully resolve CSS custom properties (`var(--brand-accent)`) when rasterizing SVG. The SVG stroke remains the literal string `var(--brand-accent)` which is not a valid color for canvas.

**How to avoid:** Before calling `html2canvas`, iterate over all SVG `path` and `line` elements and replace `attr('stroke', 'var(...)')` with the computed color using `getComputedStyle`. Alternatively, render diagrams to `<canvas>` (using D3's canvas renderer) instead of SVG, then html2canvas captures the canvas directly without CSS variable issues.

### Pitfall 6: BeamInput validation — unstable beam (insufficient supports)

**What goes wrong:** User submits a beam with 0 supports or only 1 roller (kinematically unstable). The backend's `anastruct` solver throws an exception that propagates as HTTP 422.

**Why it happens:** Anastruct's `solve()` raises when the stiffness matrix is singular.

**How to avoid:** Add client-side pre-validation before submitting: require at least 2 supports, and at least one non-roller. Display a validation error in the form rather than sending the request. The backend 422 is a backstop, not the primary guard.

---

## Code Examples

### BeamInput TypeScript type (mirrors backend schema)

```typescript
// src/types/beam.ts — to be created in Wave 0 of planning
export interface Support {
  x: number       // position on beam (m), 0 <= x <= length
  type: 1 | 2 | 3 // 1=pin, 2=roller, 3=fixed
}

export interface PointLoad {
  x: number
  fx?: number
  fy?: number
}

export interface BeamInput {
  length: number          // > 0
  angle_deg?: number      // default 0
  supports: Support[]
  point_loads?: PointLoad[]
  distributed_load?: number  // kN/m
  q_start?: number
  q_end?: number | null
  EI?: number             // default 21000
  EA?: number             // default 2100000
}

export interface DiagramPoint {
  x: number
  N: number
  V: number    // shear force — displayed as "T" in Romanian UI
  M: number
}

export interface BeamResult {
  reactions: Record<string, number>  // "x=0.00_Fy": 50.0, etc.
  diagrams: DiagramPoint[]
  max_M: number
  max_V: number
  max_N: number
  deflection: Array<{ x: number; ux: number; uy: number }>
}
```

### D3 stroke-dasharray draw-in trigger with prefers-reduced-motion

```typescript
const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
const totalLength = (path.node() as SVGPathElement).getTotalLength()

if (prefersReduced) {
  // Instant appearance
  path.attr('stroke-dasharray', null).attr('stroke-dashoffset', null)
} else {
  path
    .attr('stroke-dasharray', `${totalLength} ${totalLength}`)
    .attr('stroke-dashoffset', totalLength)
    .transition()
    .delay(animateDelay)   // stagger: 0, 400, 800, 1200
    .duration(400)
    .ease(d3.easeCubicOut)
    .attr('stroke-dashoffset', 0)
}
```

### Navbar CTA update for `/beam` navigation (D-03)

```typescript
// In Navbar.tsx — replace scrollTo('cta') with navigate('/beam')
import { useNavigate } from 'react-router-dom'

const navigate = useNavigate()
// ...
<Button onClick={() => navigate('/beam')}>
  {t('nav.cta')}
</Button>
```

### i18n keys to add for Phase 2

```typescript
// Additions to src/lib/i18n.ts
// RO section:
'beam.title': 'Calculator Grinzi 2D',
'beam.length.label': 'Lungime grindă (m)',
'beam.supports.label': 'Reazeme',
'beam.support.add': 'Adaugă reazem',
'beam.support.type.pin': 'Articulație (pin)',
'beam.support.type.roller': 'Reazem mobil',
'beam.support.type.fixed': 'Încastrare',
'beam.loads.label': 'Încărcări',
'beam.load.concentrated': 'Forță concentrată',
'beam.load.distributed': 'Sarcină distribuită',
'beam.calculate': 'Calculează',
'beam.export.pdf': 'Export PDF',
'beam.copy.link': 'Copiază link',
'beam.diagram.M': 'Moment încovoietor M (kNm)',
'beam.diagram.T': 'Forță tăietoare T (kN)',
'beam.diagram.N': 'Forță axială N (kN)',
'beam.diagram.defl': 'Deflecție uy (mm)',
'beam.error.api': 'Eroare la calcul. Verificați inputul.',
'beam.error.unstable': 'Grindă nestabilă. Adăugați cel puțin 2 reazeme.',
'beam.reactions.heading': 'Reacțiuni',
// EN section: (matching keys)
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| jsPDF v2 default import | jsPDF v4 named import `{ jsPDF }` | 2024 (v4.0) | Import statement changes |
| jsPDF v2 Romanian chars need custom font | jsPDF v4 UTF-8 native | 2024 (v4.0) | No custom font loading needed |
| react-router v5 `<Switch>` | react-router v7 `<Routes>` + `createBrowserRouter` | 2022+ | API fully changed |
| react-router v6 `element` prop | react-router v7 same `element` prop | No change | Stable |
| D3 v6 `event` parameter in callbacks | D3 v7 explicit `event` as first param | D3 v7.0 (2021) | `d3.pointer(event)` not `d3.mouse(this)` |

**Deprecated/outdated:**
- `d3.mouse(this)`: replaced by `d3.pointer(event)` in D3 v7. Using `d3.mouse` will throw.
- `jsPDF` default import: v4 uses named export only.
- `<Switch>` in react-router: removed in v6+; use `<Routes>`.
- `withRouter` HOC: removed in react-router v6+; use `useNavigate`/`useLocation` hooks.

---

## Open Questions

1. **Vite proxy in production (Railway)**
   - What we know: The proxy is configured for dev (`localhost:8000`). In production, Vercel serves the frontend and Railway serves the backend.
   - What's unclear: How is `/api` rewired in production? Is there a `VITE_API_URL` env var or does the Vercel deployment use a rewrite rule?
   - Recommendation: Check if `frontend/.env.production` or `vercel.json` exists. For now, the fetch call hardcodes `/api/v1/beams/solve` which works with the Vite dev proxy; production routing should be verified in Phase 2 plan 02-01.

2. **D3 bundle size impact**
   - What we know: `d3` full package is ~500KB minified. Phase 1 used `motion/react` with LazyMotion to keep bundle lean.
   - What's unclear: Whether to use `import * as d3 from 'd3'` (full) or cherry-pick submodules (`d3-scale`, `d3-shape`, etc.).
   - Recommendation: Use `import * as d3 from 'd3'` for simplicity in Phase 2 (BeamPage is lazy-loaded so D3 only loads when user navigates to `/beam`). Tree-shaking via Vite will eliminate unused D3 exports.

3. **shadcn Input and Select components**
   - What we know: Only `button.tsx` is installed. D-04 mentions the form will need Input, Select, Label.
   - What's unclear: Whether `npx shadcn add input select label` works cleanly with the existing shadcn v4 setup.
   - Recommendation: Include the `npx shadcn add` command in Wave 0 of the plan. These are standard shadcn components with no known conflicts.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js | npm install | ✓ | (project runs) | — |
| npm | package install | ✓ | (project runs) | — |
| react-router-dom@7 | routing | ✗ (not installed) | 7.14.0 available | — |
| d3@7 | diagrams | ✗ (not installed) | 7.9.0 available | — |
| jspdf@4 | PDF export | ✗ (not installed) | 4.2.1 available | — |
| html2canvas@1 | PDF capture | ✗ (not installed) | 1.4.1 available | — |
| FastAPI backend | /api/v1/beams/solve | ✓ (Phase 0) | deployed Railway | — |
| Vite proxy /api | dev API calls | ✓ | configured in vite.config.ts | — |

**Missing dependencies with no fallback:**
- react-router-dom, d3, jspdf, html2canvas — all must be installed. Include `npm install` as the first task in Wave 0 of planning.

**Missing dependencies with fallback:**
- None.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Vitest 4.1.4 + @testing-library/react 16.3.2 |
| Config file | `frontend/vitest.config.ts` (exists) |
| Quick run command | `cd frontend && npx vitest run --reporter=verbose` |
| Full suite command | `cd frontend && npx vitest run --coverage` |

**Baseline:** 25 tests, 6 test files — all passing as of 2026-04-12. New Phase 2 tests must not break this baseline.

### Phase Requirements → Test Map

| Behavior | Test Type | Automated Command | File |
|----------|-----------|-------------------|------|
| `/beam` route renders without crashing | unit | `npx vitest run src/__tests__/beam-routing.test.tsx` | Wave 0 |
| Landing page still renders after router refactor | unit | `npx vitest run src/__tests__/landing-sections.test.tsx` (update to wrap MemoryRouter) | Update existing |
| BeamInputForm renders length/supports/loads fields | unit | `npx vitest run src/__tests__/beam-input-form.test.tsx` | Wave 0 |
| BeamInputForm: submit with 0 supports shows validation error | unit | same file | Wave 0 |
| BeamInputForm: submit with 1 roller shows unstable error | unit | same file | Wave 0 |
| BeamInputForm: submit with valid data calls solve() | unit (mock fetch) | same file | Wave 0 |
| useBeamSolver: successful API call sets result | unit (mock fetch) | `npx vitest run src/__tests__/useBeamSolver.test.ts` | Wave 0 |
| useBeamSolver: API 422 sets error message | unit (mock fetch) | same file | Wave 0 |
| useBeamSolver: network error sets error message | unit (mock fetch) | same file | Wave 0 |
| encodeBeamHash / decodeBeamHash round-trip | unit | `npx vitest run src/__tests__/beamHash.test.ts` | Wave 0 |
| decodeBeamHash returns null for malformed hash | unit | same file | Wave 0 |
| BeamPage reads hash on mount and calls solve | unit | `npx vitest run src/__tests__/beam-page.test.tsx` | Wave 0 |
| BeamPage saves to localStorage on solve | unit | same file | Wave 0 |
| BeamPage: copy link writes to clipboard | unit (mock clipboard) | same file | Wave 0 |
| DiagramPanel renders SVG with correct data-testid | unit (mock d3 or ref) | `npx vitest run src/__tests__/diagram-panel.test.tsx` | Wave 0 |
| DiagramPanel: empty data renders empty SVG without crash | unit | same file | Wave 0 |

### Key acceptance criteria (programmatically verifiable)

1. `window.location.hash` after submit equals `btoa(encodeURIComponent(JSON.stringify(input)))`
2. `localStorage.getItem('structcalc-beam-last')` after submit parses to the submitted `BeamInput`
3. Rendering `<BeamPage />` with a valid hash in `window.location.hash` calls the solve function (spy on `useBeamSolver.solve`)
4. The API call body sent to `/api/v1/beams/solve` is valid JSON matching `BeamInput` schema
5. On API error, an element with role `alert` or class matching `error` appears in the DOM

### Sampling Rate

- **Per task commit:** `cd frontend && npx vitest run --reporter=verbose`
- **Per wave merge:** `cd frontend && npx vitest run --coverage`
- **Phase gate:** Full suite green (25 + new tests) before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `frontend/src/__tests__/beam-routing.test.tsx` — route renders, MemoryRouter wrapper
- [ ] `frontend/src/__tests__/beam-input-form.test.tsx` — form validation, submit triggers solve
- [ ] `frontend/src/__tests__/useBeamSolver.test.ts` — fetch mock, success/error states
- [ ] `frontend/src/__tests__/beamHash.test.ts` — encode/decode round-trip, malformed input
- [ ] `frontend/src/__tests__/beam-page.test.tsx` — hash on mount, localStorage, clipboard
- [ ] `frontend/src/__tests__/diagram-panel.test.tsx` — renders SVG, empty data no-crash
- [ ] `frontend/src/types/beam.ts` — TypeScript types mirroring backend schemas
- [ ] Update `frontend/src/__tests__/landing-sections.test.tsx` — wrap with `<MemoryRouter>` after App.tsx refactor

*(Existing setup.ts covers matchMedia and IntersectionObserver mocks — no changes needed there)*

---

## Project Constraints (from CLAUDE.md)

| Directive | Impact on Phase 2 |
|-----------|-------------------|
| Python + Streamlit (UI), NumPy, Matplotlib — original app.py | Backend already migrated to FastAPI in Phase 0; Phase 2 does NOT touch app.py or backend |
| `app.py` — entire application in single file | Not relevant; Phase 2 is frontend-only |
| UI and comments in Romanian | All user-facing text in Romanian (with EN toggle via i18n). All code comments may be in English. |
| `streamlit run app.py` for original app | Phase 2 does not start or depend on Streamlit; uses `npm run dev` + `uvicorn` |

---

## Sources

### Primary (HIGH confidence)
- npm registry — react-router-dom@7.14.0 peer deps verified
- npm registry — d3@7.9.0, @types/d3@7.4.3 confirmed versions
- npm registry — jspdf@4.2.1, html2canvas@1.4.1 confirmed versions
- `backend/app/schemas/beam.py` — BeamInput/BeamResult field names read directly
- `backend/app/api/v1/beams.py` — endpoint URL and HTTP method confirmed
- `frontend/vite.config.ts` — proxy config confirmed
- `frontend/src/main.tsx` — no existing router; BrowserRouter addition is clean
- `frontend/package.json` — all existing deps confirmed; none of the 4 new packages are already installed

### Secondary (MEDIUM confidence)
- D3 v7 `d3.pointer(event)` replacing `d3.mouse(this)` — well-documented breaking change in v7 changelog
- jsPDF v4 named import `{ jsPDF }` — confirmed from npm view exports showing ESM-native dist
- html2canvas CSS variable limitation — known community issue; workaround documented

### Tertiary (LOW confidence)
- html2canvas SVG+CSS variable capture behavior — based on known v1.x limitations; should be tested empirically
- jsPDF v4 UTF-8 Romanian diacritics working natively — plausible given ESM rewrite but not verified against a running instance

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all versions confirmed against npm registry
- Architecture: HIGH — all existing code read directly; patterns are idiomatic
- API contract: HIGH — backend schemas read directly from source
- Pitfalls: MEDIUM-HIGH — most are confirmed by code reading (router test conflict, D3 clientWidth=0) or well-documented D3/jsPDF changes
- PDF CSS variable issue: LOW — known limitation but exact behavior with this codebase not tested

**Research date:** 2026-04-12
**Valid until:** 2026-05-12 (stable libraries; D3 v7 and react-router v7 are not fast-moving)
