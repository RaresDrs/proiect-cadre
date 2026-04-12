# Phase 3: Modul Cadre 2D - Research

**Researched:** 2026-04-12
**Domain:** Interactive 2D frame editor — SVG canvas, anastruct SystemElements, FastAPI, React state management, SVG animation
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Rută separată `/frame`. Ruta `/beam` nu se modifică.
- **D-02:** Navbar: două link-uri separate — „Grindă 2D" → `/beam` și „Cadru 2D" → `/frame`. Nu dropdown, nu toggle.
- **D-03:** FramePage refolosește RootLayout identic.
- **D-04:** Mod hibrid: canvas SVG pentru desenat + câmpuri numerice per element selectat.
- **D-05:** Click-to-draw (stilul Strian/SkyCiv): click pe canvas gol → nod, click pe nod → selectează, click pe alt nod → bară. Toolbar cu moduri Add Node / Add Bar / Select / Delete.
- **D-06:** Grid snap automat la 0.5m implicit, linii de grid vizibile.
- **D-07:** SVG pur (fără Konva/React Flow) — interactivitate via onMouseDown/onMouseMove/onMouseUp.
- **D-08:** Model date cadru: `nodes[]` cu `{id, x, y, constraint}`, `bars[]` cu `{id, node_i, node_j, EI, EA}`, `node_loads[]` cu `{node_id, Fx, Fy, Mz}`, `bar_loads[]` cu `{bar_id, q, q_start, q_end}`.
- **D-09:** EI=21000 kN·m², EA=2100000 kN implicite, editabile per bară.
- **D-10:** Backend FastAPI — nou endpoint `POST /api/v1/frames/solve`. anastruct `SystemElements`.
- **D-11:** Noi scheme Pydantic: `FrameInput` și `FrameResult` în `backend/app/schemas/frame.py`.
- **D-12:** `FrameResult` include per bară: diagrama M/T/N (listă de puncte), deplasări nodale (ux, uy, φ per nod), reacțiuni în reazeme.
- **D-13:** Diagrame M/T/N suprapuse pe canvas-ul cadrului per bară (stilul SkyCiv). Nu panouri separate.
- **D-14:** Tabs deasupra canvas rezultat: M | T | N | Deformată.
- **D-15:** Colorare cu semn: pozitive → #22c55e/0.3, negative → #ef4444/0.3. Umplutură + contur solid.
- **D-16:** Labels max/min per bară vizibile permanent; hover → tooltip cu valoarea exactă.
- **D-17:** Animație draw-in stagger ~80ms per bară cu stroke-dasharray/stroke-dashoffset. Respectă `prefers-reduced-motion`.
- **D-18:** Deformata animată suprapusă pe forma originală (linie punctată), factor de scală ×100.
- **D-19:** URL hash sharing: FrameInput serializat ca JSON → base64 în `location.hash`. La deschidere → populează + auto-solve.
- **D-20:** localStorage key `structcalc-frame-last` — salvare la fiecare submit.
- **D-21:** Buton „Copiază link" — același pattern ca BeamPage.
- **D-22:** Export PDF client-side cu jsPDF + html2canvas. Raportul include schema cadrului, diagramele active, reacțiuni tabulare.

### Claude's Discretion

- Dimensiunile exacte ale canvas-ului (px) și logica de zoom/pan (opțional în Phase 3)
- Dimensiunea nodurilor și stilul vizual al barelor pe canvas (grosime, culori dark/light)
- Iconițele pentru tipurile de constrângere în canvas (triunghi pin, rolă, încastrare)
- Grid snap resolution editabilă de utilizator vs fixă la 0.5m
- Logica de validare a cadrului (cadru cinematic → mesaj de eroare)

### Deferred Ideas (OUT OF SCOPE)

- Zoom/pan pe canvas
- Cadre 3D
- Solver client-side (Wasm/JS)
- Salvare în cont (server-side) — Phase 4
- Validare automată tip cadru (simplu rezemat, consolă, portal etc.)
- Grinzi continue multi-deschidere din Phase 2
</user_constraints>

---

## Summary

Phase 3 construiește un editor vizual interactiv complet pentru cadre 2D. Stack-ul este bine definit prin deciziile din CONTEXT.md și urmează exact pattern-urile Phase 2. Complexitatea reală este concentrată în trei zone: (1) SVG interactiv cu state machine pentru moduri de editare, (2) maparea corectă a modelului de date al cadrului către anastruct SystemElements, și (3) desenarea diagramelor M/T/N perpendicular pe fiecare bară cu semn colorat.

Vestea bună: anastruct `SystemElements` suportă nativ cadre 2D cu elemente înclinate, noduri cu 3 grade de libertate (ux, uy, phi_z), și returnează per element toate datele necesare (bending_moment, shear_force, N_1/N_2). Pattern-ul solver din Phase 2 (beam_solver.py) se extinde direct — nu este o rescrierea, ci o generalizare.

Principalul risc este coordonarea spațiului SVG: canvas-ul are coordonate pixel cu Y inversat față de sistemul ingineresc (Y crește în jos în SVG, în sus în inginerie). Toate transformările lume→SVG trebuie să fie consistente între editare, afișare deformată, și diagrame suprapuse.

**Primary recommendation:** Separa strict transformarea lume→SVG într-o singură funcție utilitară `worldToSvg(x, y, bbox, svgDims)` și utilizeaz-o pentru toate componentele canvas.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| anastruct | existent în backend | Solver FEM pentru cadre 2D | Deja utilizat în Phase 2; suportă elemente înclinate + 3 DOF per nod |
| React + SVG nativ | React 19.2.4 | Canvas interactiv | D-07 impune SVG pur; pattern deja stabilit în BeamPreview.tsx |
| FastAPI + Pydantic | existent | Endpoint `/frames/solve` | D-10, D-11 — același pattern ca beams.py |
| jsPDF | 4.2.1 (npm registry) | Export PDF | D-22 — ales explicit în context |
| html2canvas | 1.4.1 (npm registry) | Captura canvas SVG pentru PDF | D-22 — ales explicit în context |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| motion (Framer Motion) | 12.38.0 (existent) | Animații opționale extra | Dacă stroke-dasharray nativ nu este suficient; deja în bundle |
| vitest + @testing-library/react | 4.1.4 / 16.3.2 (existent) | Teste unitare hooks și utilitare | Urmează pattern-ul din Phase 2 |
| useLang / useTheme | existent | i18n + dark mode | Toate texte noi în lib/i18n.ts, culorile via CSS vars |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| SVG pur | Konva.js / React Flow | D-07 interzice explicit; SVG e suficient pentru un cadru de câteva zeci de bare |
| stroke-dasharray animation | Framer Motion pathLength | stroke-dasharray e mai simplu și consistent cu StructuralDiagram existent |
| anastruct SystemElements | solver JS manual (stiffness method) | D-10 mandatează backend; anastruct e verificat și există deja |

**Installation (noi dependențe frontend):**
```bash
cd frontend && npm install jspdf html2canvas
```
```bash
cd frontend && npm install --save-dev @types/html2canvas
```

---

## Architecture Patterns

### Recommended Project Structure
```
backend/
├── app/
│   ├── schemas/
│   │   └── frame.py          # FrameInput, FrameResult, FrameNodeResult, FrameBarDiagram
│   ├── services/
│   │   └── frame_solver.py   # solve_frame() — urmează solve_beam()
│   └── api/v1/
│       ├── frames.py         # router POST /frames/solve
│       └── router.py         # adaugă include_router(frames.router)

frontend/src/
├── types/
│   └── api.ts                # adaugă FrameInput, FrameResult, FrameNode, FrameBar
├── lib/
│   ├── frameHash.ts          # encode/decodeFrameHash — replică beamHash.ts
│   └── frameCanvas.ts        # worldToSvg(), svgToWorld(), snapToGrid(), hitTest()
├── hooks/
│   └── useFrameSolver.ts     # replică useBeamSolver.ts
├── components/
│   └── frame/
│       ├── FrameCanvas.tsx   # SVG interactiv principal (editor + results overlay)
│       ├── FrameToolbar.tsx  # Add Node / Add Bar / Select / Delete mode selector
│       ├── FrameSidePanel.tsx # Câmpuri editabile per element selectat
│       ├── FrameDiagrams.tsx # Suprapunere M/T/N/Deformată pe canvas
│       └── __tests__/        # teste vitest pentru logica pură
└── pages/
    └── FramePage.tsx         # structură identică BeamPage.tsx
```

### Pattern 1: State Machine pentru Editor Canvas
**What:** Mod de editare explicit ca enum, previne ambiguitatea click-urilor.
**When to use:** Oricând SVG-ul trebuie să interpreteze diferit același eveniment în funcție de context.

```typescript
// Source: pattern propriu, verificat cu BeamPreview.tsx
type EditorMode = 'add_node' | 'add_bar' | 'select' | 'delete'

interface FrameEditorState {
  nodes: FrameNode[]
  bars: FrameBar[]
  nodeLoads: NodeLoad[]
  barLoads: BarLoad[]
  selectedId: string | null
  selectedType: 'node' | 'bar' | null
  pendingBarStart: string | null  // node_id-ul primului click în modul add_bar
  mode: EditorMode
}
```

Tranzițiile de stare:
- `add_node` + click pe canvas gol → adaugă nod, rămâne în `add_node`
- `add_bar` + click pe nod → setează `pendingBarStart`; al doilea click pe alt nod → adaugă bară, reset `pendingBarStart`
- `select` + click pe nod/bară → setează `selectedId`; click pe canvas gol → deselect
- `delete` + click pe nod/bară → șterge elementul (și barele conectate dacă e nod)

### Pattern 2: Transformare lume ↔ SVG
**What:** Funcție pură centralizată. Coordonatele inginerești (Y în sus, metri) → coordonate SVG (Y în jos, pixeli).
**When to use:** Orice component care desenează elemente pe canvas.

```typescript
// Source: pattern propriu dedus din BeamPreview.tsx toSvgX()
interface BBox { minX: number; minY: number; maxX: number; maxY: number }
interface SvgDims { width: number; height: number; margin: number }

function worldToSvg(wx: number, wy: number, bbox: BBox, dims: SvgDims) {
  const rangeX = (bbox.maxX - bbox.minX) || 1
  const rangeY = (bbox.maxY - bbox.minY) || 1
  const scale = Math.min(
    (dims.width - 2 * dims.margin) / rangeX,
    (dims.height - 2 * dims.margin) / rangeY
  )
  const sx = dims.margin + (wx - bbox.minX) * scale
  const sy = dims.height - dims.margin - (wy - bbox.minY) * scale  // Y inversat
  return { sx, sy, scale }
}
```

### Pattern 3: anastruct SystemElements pentru Cadre 2D
**What:** Construirea sistemului FEM din modelul de date al cadrului. Verificat live pe mașina de dev.
**When to use:** În `frame_solver.py` — `solve_frame(data: FrameInput) -> FrameResult`.

```python
# Source: verificat live cu anastruct pe mașina de dev (2026-04-12)
ss = SystemElements(EI=DEFAULT_EI, EA=DEFAULT_EA)

# Adaugă elemente — ID-urile nodurilor în anastruct sunt 1-indexed și sequential
# Node mapping: data.nodes[i].id (string UUID) → anastruct node_id (int, 1-based)
node_id_map: dict[str, int] = {}
anastruct_nodes: list[tuple[float, float]] = []
for i, node in enumerate(data.nodes):
    node_id_map[node.id] = i + 1
    anastruct_nodes.append((node.x, node.y))

# Adaugă bare — anastruct derivă nodurile din coordonate
for bar in data.bars:
    n_i = next(n for n in data.nodes if n.id == bar.node_i)
    n_j = next(n for n in data.nodes if n.id == bar.node_j)
    ss.add_element(
        location=[[n_i.x, n_i.y], [n_j.x, n_j.y]],
        EI=bar.EI,
        EA=bar.EA,
    )

# Reazeme
CONSTRAINT_MAP = {
    'pin': ss.add_support_hinged,
    'roller': lambda nid: ss.add_support_roll(nid, direction='x'),
    'fixed': ss.add_support_fixed,
    # 'free' → fără reazem (nod liber)
}
for node in data.nodes:
    if node.constraint != 'free':
        anastruct_nid = node_id_map[node.id]
        CONSTRAINT_MAP[node.constraint](anastruct_nid)

# Sarcini nodale (Fx, Fy, Mz)
for nl in data.node_loads:
    nid = node_id_map[nl.node_id]
    if abs(nl.Fx) > 1e-9 or abs(nl.Fy) > 1e-9:
        ss.point_load(node_id=nid, Fx=nl.Fx, Fy=nl.Fy)
    if abs(nl.Mz) > 1e-9:
        ss.moment_load(node_id=nid, Tz=nl.Mz)

# Sarcini distribuite pe bare
for bl in data.bar_loads:
    # bar_loads element_id = ordinea din data.bars (1-indexed)
    bar_idx = next(i for i, b in enumerate(data.bars) if b.id == bl.bar_id) + 1
    if abs(bl.q) > 1e-9:
        ss.q_load(element_id=bar_idx, q=-bl.q)  # anastruct: negativ = în jos

ss.solve()
```

**Atentie:** anastruct atribuie node_id-uri consecutive începând de la 1, în ordinea în care elementele sunt adăugate. Nodul comun între două elemente primeste același ID dacă coordonatele sunt identice. Mapping-ul `node_id_map` este esential.

### Pattern 4: Diagrame M/T/N suprapuse pe bare SVG
**What:** Fiecare bară are un sistem de coordonate local (de-a lungul axei, perpendicular). Valorile diagramei se desenează perpendicular pe axă.
**When to use:** `FrameDiagrams.tsx` în tab M / T / N activ.

```typescript
// Source: pattern geometric propriu, verificat conceptual
// barAngle = unghi bară față de orizontal (radiani)
// pts = DiagramPoint[] cu x (pozitie pe bară 0..L) și valoarea M/V/N
function buildDiagramPath(
  nodeI: { sx: number; sy: number },
  nodeJ: { sx: number; sy: number },
  values: number[],
  scale: number,    // pixels/unitate forță sau moment
  positive: boolean // true = pozitiv în sus față de bară
): string {
  const dx = nodeJ.sx - nodeI.sx
  const dy = nodeJ.sy - nodeI.sy
  const barLen = Math.hypot(dx, dy)
  const ux = dx / barLen  // vector unitar de-a lungul barei
  const uy = dy / barLen
  // perpendicular = rotit 90° CCW
  const px = -uy
  const py = ux

  const n = values.length
  const points = values.map((v, i) => {
    const t = i / (n - 1)
    const bx = nodeI.sx + t * dx
    const by = nodeI.sy + t * dy
    const offset = v * scale
    return `${bx + px * offset},${by + py * offset}`
  })
  return `M ${nodeI.sx},${nodeI.sy} L ${points.join(' L ')} L ${nodeJ.sx},${nodeJ.sy} Z`
}
```

### Pattern 5: Animație draw-in SVG (stroke-dasharray)
**What:** Replică exact animația din StructuralDiagram.tsx, extinsă cu stagger per bară.
**When to use:** `FrameDiagrams.tsx` la afișarea rezultatelor după solve.

```typescript
// Source: StructuralDiagram.tsx (existent în proiect)
// Fiecare <path> primeste:
//   strokeDasharray={pathLength}
//   strokeDashoffset={pathLength}
//   style={{ animation: `drawDiagram 0.6s ease-out ${barIndex * 0.08}s forwards` }}
// CSS global (sau <style> scoped):
//   @keyframes drawDiagram { to { stroke-dashoffset: 0; } }
// prefers-reduced-motion:
//   @media (prefers-reduced-motion: reduce) {
//     path[data-diagram] { animation: none !important; stroke-dashoffset: 0; }
//   }
```

### Anti-Patterns to Avoid
- **Y-axis confusion:** Nu folosi coordonatele inginerești direct în SVG. Orice `y` din model trebuie trecut prin `worldToSvg()` înainte de a fi folosit ca atribut SVG.
- **anastruct node ID din UUID:** anastruct nu acceptă node_id-uri string sau non-consecutive. Mereu mapează `data.nodes[i].id` → `i + 1` și stochează mapping-ul.
- **Element order mismatch:** ID-ul de element în anastruct (`element_map[1]`, `element_map[2]` ...) corespunde ordinii în care `add_element()` a fost chemat — nu unui ID al barei din model. Menține o mapare `bar.id → anastruct_element_id` în solver.
- **React re-render pe SVG mare:** Nu stoca `FrameEditorState` complet în `useState` dacă include sute de puncte de diagrame. Separa starea editorului (nodes/bars) de starea rezultatelor.
- **Hit testing cu `onClick` pe `<svg>`:** Evenimentele `onClick` pe SVG bubble. Foloseste `pointer-events: none` pe elementele decorative (grid, labels) și `pointer-events: all` explicit pe noduri și bare interactive.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Solver FEM cadre 2D | Implementare stiffness method din zero | anastruct `SystemElements` | Assembly matrice de rigiditate globală, pivotare, condiții de contur — zeci de bug-uri potențiale; anastruct verificat |
| Export PDF cu grafice | jsPDF cu canvas manual | jsPDF + html2canvas | html2canvas captează SVG-ul redat, inclusiv culori CSS vars; alternativa manuală ratează dark mode și fonturi |
| URL state serialization | Compresie/encoding custom | `btoa(encodeURIComponent(JSON.stringify()))` | Pattern identic cu beamHash.ts — simplu, reversibil, deja testat |
| Snap la grid | Algoritm geometric custom | `Math.round(v / GRID_STEP) * GRID_STEP` | Un liner; nu justifică o librărie |

**Key insight:** Complexitatea reală în acest modul nu este în calcule (anastruct o face), ci în coordonarea sistemelor de coordonate SVG ↔ inginerie și în state machine-ul editorului.

---

## Common Pitfalls

### Pitfall 1: anastruct Nod ID Clash la Coordonate Identice
**What goes wrong:** Dacă două elemente share un nod dar coordonatele nu sunt exact identice (float imprecision), anastruct creează două noduri separate în loc de unul — cadrul devine disconnected.
**Why it happens:** anastruct identifică nodurile după coordonate (vertex matching cu toleranță mică).
**How to avoid:** Rotunjește toate coordonatele la 4-6 zecimale înainte de `add_element()`. Utilizează `round(x, 4)`.
**Warning signs:** `ss.node_map` are mai multe noduri decât `data.nodes` — inspectat în teste pytest.

### Pitfall 2: anastruct Roller Direction
**What goes wrong:** `add_support_roll(node_id)` implicit are `direction='x'` — reazem mobil care se poate deplasa în X (fix în Y). Dacă utilizatorul vrea un roller care alunecă în Y, e nevoie de `direction='y'`.
**Why it happens:** Convenția anastruct nu e intuitivă: `direction` = axa de-a lungul căreia alunecă (nu axa fixată).
**How to avoid:** Pentru Phase 3, `direction='x'` (implicitul) corespunde reazem mobil clasic de grindă orizontală. Dacă cadrul are bare verticale cu roller în vârf, poate fi nevoie de `direction='y'`. Documenteaza în schema `constraint: "roller_x" | "roller_y"` dacă apare nevoia.

### Pitfall 3: SVG `viewBox` Fix vs. Dinamic
**What goes wrong:** Canvas-ul cu viewBox fix (ex. `0 0 600 400`) nu scalează corect cadre de dimensiuni variabile — un cadru de 0.5m pare identic cu unul de 50m.
**Why it happens:** BeamPreview folosește viewBox fix pentru o singură bară orizontală. Cadrul are noduri la coordonate arbitrare.
**How to avoid:** Calculează bounding box din `nodes[]` + padding, derivă viewBox dinamic. Actualizează la fiecare modificare a nodes[]. Funcția `worldToSvg()` trebuie să primească bbox ca parametru.

### Pitfall 4: `pointer-events` pe SVG Interactiv
**What goes wrong:** Click-urile pe labels de diagrame, linii de grid, sau umpluturi de diagrame activează accidental adăugarea de noduri.
**Why it happens:** SVG propagă click-urile prin toate elementele suprapuse care nu au `pointer-events: none`.
**How to avoid:** Aplică `pointerEvents="none"` pe toate elementele non-interactive (grid, diagrams overlay, labels). Aplică `pointerEvents="all"` explicit pe cercurile de noduri și liniile de bare.

### Pitfall 5: html2canvas și CSS Variables
**What goes wrong:** `html2canvas` nu înțelege CSS custom properties (`var(--brand-accent)`) și redă culorile greșit sau transparent în PDF.
**Why it happens:** html2canvas computează stilurile dar poate rata variabilele CSS dacă nu sunt complet inline.
**How to avoid:** Înainte de `html2canvas(element)`, aplică temporar un className care înlocuiește CSS vars cu culori hex concrete, sau foloseste `onclone` callback-ul html2canvas pentru a injectă stiluri inline. Testează explicit cu dark mode activ.

### Pitfall 6: Deformata — Factor de Scală
**What goes wrong:** Deplasările reale (ux, uy în mm sau cm) sunt atât de mici față de dimensiunile cadrului încât deformata nu se vede.
**Why it happens:** Pentru EI=21000 kN·m², deplasările tipice sunt 0.001–0.01 m la forțe de zeci de kN.
**How to avoid:** Factor de scală exagerat ×100 (D-18). Afișează valoarea scalei lângă deformată. Calculat ca: `max_displacement * scale_factor < 0.1 * min_bar_length` → ajustare automată dacă ×100 e prea mult.

---

## anastruct API Reference (Verificat Live)

Toate API-urile de mai jos au fost verificate pe mașina de dev cu Python (2026-04-12):

### Semnături relevante
```python
SystemElements.add_element(
    location: list[list[float]],  # [[x1,y1],[x2,y2]]
    EA: float | None = None,
    EI: float | None = None,
    spring: dict | None = None,   # {1: 0} hinge la start, {2: 0} hinge la end
) -> int  # returnează element_id

SystemElements.add_support_hinged(node_id: int) -> None
SystemElements.add_support_roll(node_id: int, direction: str = 'x') -> None  # 'x' = alunecă în x
SystemElements.add_support_fixed(node_id: int) -> None

SystemElements.point_load(node_id: int, Fx: float = 0, Fy: float = 0) -> None
SystemElements.moment_load(node_id: int, Tz: float = 0) -> None
SystemElements.q_load(q: float, element_id: int, direction: str = 'element') -> None

SystemElements.solve() -> None

# Post-solve
element_map[id].bending_moment  # list[float], 50 puncte per element
element_map[id].shear_force      # list[float], 50 puncte
element_map[id].N_1, .N_2       # float, forță axială la capete
element_map[id].angle            # float, radiani față de orizontal
element_map[id].deflection       # list[float], săgeți perpendiculare

get_node_results_system(node_id: int) -> dict:
    # {'id', 'Fx', 'Fy', 'Tz', 'ux', 'uy', 'phi_z'}
    # Tz = moment de reacțiune (la reazeme cu moment)
    # phi_z = rotație nodală (radiani)
```

### Portal frame exemplu (validat numeric):
```
Cadru: beam 4m (top) + 2 coloane 3m, baze încastrate, H=10kN la top-left
Rezultat anastruct:
  Nod 3 (baza stg): Fx=5.020, Fy=3.062, Tz=-8.918 kN/kNm
  Nod 4 (baza dr):  Fx=4.980, Fy=-3.062, Tz=-8.834 kN/kNm
  Elem 2 (col stg): M_max=8.918 kNm
  Elem 3 (col dr):  M_max=8.834 kNm
```
Aceste valori pot fi folosite ca golden test în pytest pentru `frame_solver.py`.

---

## Schema Pydantic Propusă

### FrameInput (`backend/app/schemas/frame.py`)
```python
from pydantic import BaseModel
from typing import List, Literal

class FrameNode(BaseModel):
    id: str                    # UUID generat frontend
    x: float                   # metri
    y: float                   # metri
    constraint: Literal['free', 'pin', 'roller', 'fixed'] = 'free'

class FrameBar(BaseModel):
    id: str                    # UUID generat frontend
    node_i: str                # FrameNode.id
    node_j: str                # FrameNode.id
    EI: float = 21000.0        # kN·m²
    EA: float = 2100000.0      # kN

class NodeLoad(BaseModel):
    node_id: str
    Fx: float = 0.0            # kN
    Fy: float = 0.0            # kN
    Mz: float = 0.0            # kN·m

class BarLoad(BaseModel):
    bar_id: str
    q: float = 0.0             # kN/m (pozitiv = în jos)
    q_start: float = 0.0       # pozitie pe bară 0..1 (relativ la lungime)
    q_end: float = 1.0

class FrameInput(BaseModel):
    nodes: List[FrameNode]
    bars: List[FrameBar]
    node_loads: List[NodeLoad] = []
    bar_loads: List[BarLoad] = []
```

### FrameResult (`backend/app/schemas/frame.py`)
```python
class FrameDiagramPoint(BaseModel):
    t: float      # pozitie relativa 0..1 pe bara
    N: float
    V: float
    M: float

class FrameBarResult(BaseModel):
    bar_id: str
    diagrams: List[FrameDiagramPoint]  # 50 puncte
    max_M: float
    max_V: float
    max_N: float

class FrameNodeDisplacement(BaseModel):
    node_id: str
    ux: float     # deplasare orizontala (m)
    uy: float     # deplasare verticala (m)
    phi_z: float  # rotatie (rad)

class FrameReaction(BaseModel):
    node_id: str
    Fx: float
    Fy: float
    Mz: float

class FrameResult(BaseModel):
    bar_results: List[FrameBarResult]
    node_displacements: List[FrameNodeDisplacement]
    reactions: List[FrameReaction]
```

**Note pe schemă:**
- `FrameDiagramPoint.t` (0..1) în loc de `x` absolut — independent de lungimea barei, ușor de mapat la SVG
- Reacțiunile per nod (nu per tip reazem ca în beam schema) — mai clar pentru cadre cu bare înclinate

---

## TypeScript API Types

Adăugat în `frontend/src/types/api.ts`:
```typescript
export interface FrameNode {
  id: string
  x: number
  y: number
  constraint: 'free' | 'pin' | 'roller' | 'fixed'
}

export interface FrameBar {
  id: string
  node_i: string
  node_j: string
  EI: number
  EA: number
}

export interface NodeLoad {
  node_id: string
  Fx: number
  Fy: number
  Mz: number
}

export interface BarLoad {
  bar_id: string
  q: number
  q_start: number
  q_end: number
}

export interface FrameInput {
  nodes: FrameNode[]
  bars: FrameBar[]
  node_loads: NodeLoad[]
  bar_loads: BarLoad[]
}

export interface FrameDiagramPoint {
  t: number   // 0..1 pozitie pe bara
  N: number
  V: number
  M: number
}

export interface FrameBarResult {
  bar_id: string
  diagrams: FrameDiagramPoint[]
  max_M: number
  max_V: number
  max_N: number
}

export interface FrameNodeDisplacement {
  node_id: string
  ux: number
  uy: number
  phi_z: number
}

export interface FrameReaction {
  node_id: string
  Fx: number
  Fy: number
  Mz: number
}

export interface FrameResult {
  bar_results: FrameBarResult[]
  node_displacements: FrameNodeDisplacement[]
  reactions: FrameReaction[]
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| BeamPreview static SVG | FrameCanvas interactive SVG (event handlers) | Phase 3 | SVG-ul devine editor, nu doar preview |
| BeamInput plat (lungime + reazeme) | FrameInput: nodes[] + bars[] (graf) | Phase 3 | Structura de date generalizată pentru topologii arbitrare |
| Diagrame D3 (Phase 2 plan) | Diagrame SVG nativ suprapuse pe canvas | Phase 3 D-13 | Elimină dependința D3 pentru frame; consistent cu canvas SVG |
| solve_beam (1D, x de-a lungul grinzii) | solve_frame (2D, coordonate x/y) | Phase 3 | Node mapping explicit, elemente înclinate native |

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python/anastruct | Backend solver | ✓ | existent | — |
| Node.js/npm | Frontend build | ✓ | existent | — |
| jsPDF | D-22 Export PDF | ✗ (nu în package.json) | 4.2.1 (npm) | — (Wave 0: instalare) |
| html2canvas | D-22 Export PDF | ✗ (nu în package.json) | 1.4.1 (npm) | — (Wave 0: instalare) |
| vitest | Teste frontend | ✓ | 4.1.4 | — |
| FastAPI/uvicorn | Backend | ✓ | existent | — |

**Missing dependencies with no fallback:**
- `jspdf` și `html2canvas` — trebuie instalate în Wave 0 (`npm install jspdf html2canvas`)

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | vitest 4.1.4 + @testing-library/react 16.3.2 (frontend); pytest (backend) |
| Config file | `frontend/vitest.config.ts` (existent); `backend/pytest.ini` sau inline |
| Quick run command | `cd frontend && npx vitest run --reporter=verbose` |
| Full suite command | `cd frontend && npx vitest run && cd ../backend && python -m pytest` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-03-01 | `encodeFrameHash` / `decodeFrameHash` round-trip fără pierderi | unit | `npx vitest run src/__tests__/frameHash.test.ts` | ❌ Wave 0 |
| REQ-03-02 | `useFrameSolver` — success: setează `result` din 200 response | unit | `npx vitest run src/__tests__/useFrameSolver.test.ts` | ❌ Wave 0 |
| REQ-03-03 | `useFrameSolver` — 422: setează `error` din `detail` | unit | `npx vitest run src/__tests__/useFrameSolver.test.ts` | ❌ Wave 0 |
| REQ-03-04 | `worldToSvg()` — Y inversat corect (y_ingineresc creste = sy scade) | unit | `npx vitest run src/__tests__/frameCanvas.test.ts` | ❌ Wave 0 |
| REQ-03-05 | `snapToGrid(0.7, 0.5)` returnează `1.0` | unit | `npx vitest run src/__tests__/frameCanvas.test.ts` | ❌ Wave 0 |
| REQ-03-06 | `solve_frame` — portal frame cu baze fixe, H=10kN produce reacțiuni corecte (±5%) | unit | `cd backend && python -m pytest tests/test_frame_solver.py::test_portal_frame` | ❌ Wave 0 |
| REQ-03-07 | `solve_frame` — cadru simplu rezemat cu sarcină verticală, suma reacțiunilor Fy = sarcina aplicată | unit | `cd backend && python -m pytest tests/test_frame_solver.py::test_vertical_load_equilibrium` | ❌ Wave 0 |
| REQ-03-08 | `POST /api/v1/frames/solve` — răspunde 200 cu `FrameResult` valid pentru input minim (2 noduri, 1 bară, 2 reazeme) | integration | `cd backend && python -m pytest tests/test_frames_api.py::test_solve_minimal` | ❌ Wave 0 |
| REQ-03-09 | `POST /api/v1/frames/solve` — răspunde 422 pentru input fără reazeme (cadru cinematic) | integration | `cd backend && python -m pytest tests/test_frames_api.py::test_solve_no_supports` | ❌ Wave 0 |
| REQ-03-10 | `decodeFrameHash` returnează `null` pentru hash malformat | unit | `npx vitest run src/__tests__/frameHash.test.ts` | ❌ Wave 0 |
| REQ-03-11 | `buildDiagramPath()` — returnează string SVG path valid (starts with 'M', no NaN) | unit | `npx vitest run src/__tests__/frameDiagrams.test.ts` | ❌ Wave 0 |
| REQ-03-12 | `FrameCanvas` — click în mod `add_node` adaugă nod la coordonatele cursorului (snap) | unit (RTL) | `npx vitest run src/components/frame/__tests__/FrameCanvas.test.tsx` | ❌ Wave 0 |
| REQ-03-13 | `FrameCanvas` — click pe nod în mod `delete` șterge nodul și barele conectate | unit (RTL) | `npx vitest run src/components/frame/__tests__/FrameCanvas.test.tsx` | ❌ Wave 0 |
| REQ-03-14 | `FramePage` — localStorage `structcalc-frame-last` este actualizat la submit | unit (RTL) | `npx vitest run src/pages/__tests__/FramePage.test.tsx` | ❌ Wave 0 |
| REQ-03-15 | `solve_frame` — element înclinat (45°) produce `el.angle ≈ π/4` | unit | `cd backend && python -m pytest tests/test_frame_solver.py::test_inclined_element` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `cd frontend && npx vitest run --reporter=dot`
- **Per wave merge:** `cd frontend && npx vitest run && cd ../backend && python -m pytest`
- **Phase gate:** Full suite green înainte de `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `frontend/src/__tests__/frameHash.test.ts` — REQ-03-01, REQ-03-10
- [ ] `frontend/src/__tests__/useFrameSolver.test.ts` — REQ-03-02, REQ-03-03
- [ ] `frontend/src/__tests__/frameCanvas.test.ts` — REQ-03-04, REQ-03-05
- [ ] `frontend/src/__tests__/frameDiagrams.test.ts` — REQ-03-11
- [ ] `frontend/src/components/frame/__tests__/FrameCanvas.test.tsx` — REQ-03-12, REQ-03-13
- [ ] `frontend/src/pages/__tests__/FramePage.test.tsx` — REQ-03-14
- [ ] `backend/tests/test_frame_solver.py` — REQ-03-06, REQ-03-07, REQ-03-15
- [ ] `backend/tests/test_frames_api.py` — REQ-03-08, REQ-03-09
- [ ] `npm install jspdf html2canvas` — dependențe noi necesare pentru D-22

---

## Open Questions

1. **Roller direction pentru bare verticale**
   - What we know: `add_support_roll(direction='x')` (implicit) = alunecă în X, fixează Y — corect pentru bare orizontale.
   - What's unclear: Dacă un utilizator construiește un cadru cu o coloană verticală și un roller pe ea, are nevoie de `direction='y'`. Schema curentă `constraint: 'roller'` nu distinge.
   - Recommendation: Pentru Phase 3, `roller` = `direction='x'` (cazul cel mai comun). Documentează limitarea. Adaugă `roller_y` în backlog dacă utilizatorii cer.

2. **jsPDF + SVG export**
   - What we know: html2canvas poate rata CSS variables în unele browsere; jsPDF 4.x are `html()` method dar cu limitări.
   - What's unclear: Cât de fidel redă html2canvas un SVG complex (diagrame M/T/N cu gradienți și culori semi-transparente).
   - Recommendation: Testează precoce în Wave de implementare. Fallback: `svg.toDataURL()` și embed direct în PDF ca imagine (mai simplu și mai fidel decât html2canvas pentru SVG).

3. **Numărul de puncte per diagramă**
   - What we know: anastruct returnează 50 de puncte per element (`len(el.bending_moment) == 50`).
   - What's unclear: Dacă 50 de puncte × N bare (ex. 20 bare = 1000 puncte) afectează performanța SVG la render.
   - Recommendation: 50 puncte/bară e suficient vizual. Dacă cadrul depășește 30 bare, reduce la 20 puncte/bară via `np.linspace` în solver.

---

## Sources

### Primary (HIGH confidence)
- anastruct API — verificat live cu `python -c "import anastruct; ..."` pe mașina de dev (2026-04-12). Semnăturile și rezultatele documentate direct din cod.
- `backend/app/services/beam_solver.py` — pattern solver verificat, extins pentru frame.
- `backend/app/schemas/beam.py`, `frontend/src/types/api.ts` — schema existentă urmată.
- `frontend/src/components/sections/StructuralDiagram.tsx` — pattern animație draw-in verificat.
- `frontend/src/hooks/useBeamSolver.ts`, `frontend/src/lib/beamHash.ts` — pattern hooks verificat.

### Secondary (MEDIUM confidence)
- jsPDF 4.2.1, html2canvas 1.4.1 — versiuni verificate cu `npm view [package] version`.
- SVG `stroke-dasharray`/`stroke-dashoffset` animation — standard CSS/SVG, documentat MDN.

### Tertiary (LOW confidence)
- html2canvas comportament cu CSS variables — necesită testare practică (menționat ca Open Question 2).

---

## Metadata

**Confidence breakdown:**
- anastruct API pentru cadre: HIGH — verificat live
- SVG interactive patterns: HIGH — pattern existent în proiect (BeamPreview.tsx)
- Schema FrameInput/FrameResult: HIGH — dedus direct din beam.py + anastruct API
- jsPDF/html2canvas: MEDIUM — versiuni confirmate, comportament cu CSS vars neconfirat complet
- Diagrame perpendiculare pe bare: MEDIUM — geometrie standard, nu testat în cod real

**Research date:** 2026-04-12
**Valid until:** 2026-05-12 (dependențe stabile; anastruct nu se modifică rapid)
