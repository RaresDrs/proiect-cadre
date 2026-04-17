# Phase 2: Modul Grinzi 2D - Context

**Gathered:** 2026-04-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Calculator interactiv pentru grinzi 2D cu rezemări libere (nu grinzi continue): utilizatorul definește geometria și încărcările, primește diagramele M/T/N + deflecție animate, poate exporta PDF și poate partaja calculul printr-un link. Salvarea în cont (server-side) este amânată pentru Phase 4 (auth).

Nu intră în scope: grinzi continue multi-deschidere, cadre 2D (Phase 3), autentificare (Phase 4), editor vizual drag-and-drop pe canvas.

</domain>

<decisions>
## Implementation Decisions

### Routing & navigare
- **D-01:** Se adaugă `react-router-dom` v7 la proiect. Ruta `/` rămâne landing page-ul existent. Ruta `/beam` este pagina calculatorului.
- **D-02:** Pagina `/beam` refolosește nav-ul și footer-ul din landing pentru consistență de brand (nu e full-screen app separată).
- **D-03:** Landing CTA „Incepe calculul" / „Start calculating" navighează la `/beam` (nu scroll smooth).

### Input — definire grindă
- **D-04:** Layout split: formular în stânga (lg:w-1/2), SVG preview live în dreapta (lg:w-1/2). Pe mobile: formular sus, preview jos.
- **D-05:** Tipuri de rezemare suportate în Phase 2: articulație (pin, tip 1), reazem mobil (roller, tip 2), încastrare (fixed, tip 3). Utilizatorul poate plasa oricâte reazeme la orice poziție `x` pe grindă (câmp numeric pentru `x` + dropdown pentru tip). Grinzi continue (mai mult de 2 deschideri) sunt excluse din scope, dar plasarea liberă a reazimelor este permisă.
- **D-06:** Încărcări suportate: forțe concentrate (Fx, Fy la poziție x) și sarcină uniform distribuită (q între x_start și x_end). Sarcini triunghiulare/trapezoidale — excluse din Phase 2.
- **D-07:** SVG preview se actualizează în timp real la orice schimbare de input (debounce 150ms) — arată schema grinzii cu simboluri pentru reazeme și săgețile de forțe, fără să execute calculul FEM.
- **D-08:** Butonul „Calculează" / „Calculate" trimite cererea API și declanșează animațiile pe diagrame.

### Diagrame M/T/N + deflecție
- **D-09:** Bibliotecă vizualizare: D3.js (deja menționat în roadmap). Nu se adaugă o altă bibliotecă de charting.
- **D-10:** Layout: 4 panouri stivuite vertical — M (moment încovoietor), T (forță tăietoare), N (forță axială), Deflecție (deformata uy). Fiecare panou are titlu + scală + unitate.
- **D-11:** Animație la submit: diagramele se desenează progresiv (SVG path stroke-dasharray draw-in) cu stagger între panouri (M primul, apoi T, N, Deflecție). Durată per panou: ~400ms. Easing: ease-out cubic. Se respectă `prefers-reduced-motion` (animații dezactivate, apare instant).
- **D-12:** Hover tooltip: linie verticală care urmărește cursorul + tooltip care afișează valorile exacte M/T/N/deflecție la poziția x sub cursor. Se implementează cu D3 bisector.
- **D-13:** Nu există zoom/pan pe diagrame în Phase 2.

### Sharing & persistență
- **D-14:** Starea calculului (BeamInput complet) se serializează ca JSON → base64 și se stochează în URL hash: `/beam#<base64>`. La deschiderea URL-ului cu hash, inputurile se populează automat și calculul se execută imediat.
- **D-15:** Buton „Copiază link" / „Copy link" în UI — generează și copiază URL-ul cu hash în clipboard.
- **D-16:** Calculul se salvează și în `localStorage` (cheia `structcalc-beam-last`) la fiecare submit pentru a restaura ultima sesiune la revenirea pe `/beam`.
- **D-17:** Salvarea în contul utilizatorului (server-side) este EXCLUSĂ din Phase 2 — amânată pentru Phase 4. Butonul de „Salvează în cont" nu apare în Phase 2.

### Export PDF
- **D-18:** Generare PDF client-side cu `jsPDF` + `html2canvas` (nu server-side). Raportul include: schema grinzii, diagramele M/T/N/deflecție (capturi SVG), reacțiunile și valorile maxime (tabel), datele de input. Header cu logo StructCalc.
- **D-19:** Buton „Export PDF" apare după ce calculul a fost executat (nu înainte).

### Integrare backend
- **D-20:** Se folosesc endpoint-urile existente din `backend/app/api/v1/beams.py` și schema `BeamInput`/`BeamResult` din `backend/app/schemas/beam.py` — nu se modifică schema în Phase 2.
- **D-21:** Apelul API se face din frontend via proxy Vite (`/api/v1/beams/solve` sau echivalentul configurat). Error handling: toast/banner cu mesaj de eroare dacă API returnează 4xx/5xx.

### Claude's Discretion
- Exact spacing, typography scales pe pagina `/beam`
- Culori pentru umplerea diagramelor (pozitiv vs negativ — sugestie: verde/roșu semitransparent)
- Skeleton loading state între submit și primirea răspunsului API
- Iconițe pentru tipurile de reazem în SVG preview
- Forma exactă a tooltip-ului hover

</decisions>

<specifics>
## Specific Ideas

- „Ultra fancy" pe animațiile diagramelor — draw-in progresiv cu stagger, nu toate simultan. Utilizatorul vrea impact vizual puternic la submit.
- Deflecția inclusă neapărat în Phase 2 pentru impact vizual (nu amânată pentru Phase 3).
- Sharing offline-friendly — URL hash cu base64 funcționează fără server, colegi pot deschide calculul fără cont.
- Plasare liberă a reazimelor (nu tipuri predefinite simplu rezemată/consolă) — utilizatorul vrea control complet.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Backend schemas & endpoints (existente, nu se modifică)
- `backend/app/schemas/beam.py` — BeamInput și BeamResult: câmpurile exacte, validări, unități
- `backend/app/api/v1/beams.py` — Endpoint-urile REST disponibile pentru solver
- `backend/app/services/beam_solver.py` — Logica de calcul FEM (pentru înțelegerea outputului)

### Design system (Phase 1 — de respectat)
- `.planning/phases/01-design-sistem-landing-page/01-CONTEXT.md` — Decizii D-01..D-32: paletă culori, font Geist, dark mode, i18n pattern

### Configurare frontend
- `frontend/src/lib/i18n.ts` — Pattern i18n existent (plain TS object, RO/EN) — Phase 2 adaugă cheile noi în același fișier
- `frontend/src/components/layout/` — Nav și footer existente de refolosit pe `/beam`

### No external specs
Nu există ADR-uri sau documente de spec externe pentru Phase 2 — toate deciziile sunt capturate mai sus.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/src/components/layout/` — Nav + Footer: se refolosesc direct pe ruta `/beam`
- `frontend/src/hooks/useTheme.ts` — Dark mode hook: diagramele D3 trebuie să asculte `useTheme` pentru culori
- `frontend/src/hooks/useLang.ts` — i18n hook: toate textele din pagina `/beam` prin același pattern
- `frontend/src/hooks/useInView.ts` — IntersectionObserver hook: poate fi folosit pentru a declanșa animațiile diagramelor când intră în viewport
- `frontend/src/components/ui/Button.tsx` — Singurul component shadcn instalat; formularul va adăuga Input, Select, Label

### Established Patterns
- CSS tokens din Phase 1 (--color-primary, --color-background etc.) — diagramele D3 folosesc `var(--color-primary)` nu hardcodat
- i18n ca plain TS object în `i18n.ts` — Phase 2 adaugă cheile RO/EN pentru pagina beam în același fișier
- Dark mode via `.dark` pe `<html>` — D3 citește CSS variables, se adaptează automat

### Integration Points
- `frontend/vite.config.ts` — Proxy configurat pentru `/api` → Railway backend (verificat în Phase 0)
- `frontend/src/main.tsx` — Punctul de intrare unde se adaugă `<RouterProvider>` sau `<BrowserRouter>`
- `frontend/src/App.tsx` — Rutele react-router se definesc aici (`/` → Landing, `/beam` → BeamPage)

</code_context>

<deferred>
## Deferred Ideas

- **Grinzi continue multi-deschidere** — excluse din Phase 2; schema backend le suportă deja, UI-ul pentru ele aparține unui plan separat sau Phase 3
- **Sarcini triunghiulare/trapezoidale** — excluse din Phase 2
- **Salvare în cont (server-side)** — Phase 4 (Sistem Conturi & Colaborare)
- **Zoom/pan pe diagrame** — poate fi adăugat în Phase 3 sau ca îmbunătățire ulterioară
- **Editor vizual drag-and-drop** (click pe canvas pentru a plasa reazeme) — posibil în Phase 3 pentru cadre 2D; Phase 2 folosește form fields

</deferred>

---

*Phase: 02-modul-grinzi-2d*
*Context gathered: 2026-04-12*
