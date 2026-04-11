# Roadmap: StructCalc / BeamWise 2D

## Overview

Aplicatie web + mobile de nivel enterprise pentru analiza structurala 2D (grinzi, cadre). Stack: React + Vite + TypeScript frontend, FastAPI + Python backend, NumPy/SciPy calcule, PostgreSQL date. Tinta: standard industrie Romania si deschidere internationala.

## Phases

- [x] **Phase 0: Setup Proiect** - Initializare repo React+Vite+TS, FastAPI, Tailwind+shadcn, CI/CD, migrare calcule din app.py ✓ 2026-04-10
- [ ] **Phase 1: Design Sistem & Landing Page** - Design system complet, landing page cu toate sectiunile, dark/light mode, SEO
- [ ] **Phase 2: Modul Grinzi 2D** - Calculator interactiv cu diagrame M/T/N animate, export PDF, salvare calcul
- [ ] **Phase 3: Modul Cadre 2D** - Editor vizual noduri+bare, metoda rigiditatilor, deformata animata
- [ ] **Phase 4: Sistem Conturi & Colaborare** - Auth, dashboard, partajare, roluri Student/Profesor/Admin
- [ ] **Phase 5: Mobile App** - React Native Expo, calcule offline, Google Play + App Store
- [ ] **Phase 6: Landing Page Dedicat & Marketing** - Domeniu, blog SEO, analytics, newsletter

## Phase Details

### Phase 0: Setup Proiect
**Goal**: Structura completa de proiect React+Vite+TypeScript si FastAPI gata de dezvoltare, cu CI/CD functional si calculele migrate din app.py
**Depends on**: Nothing (first phase)
**Requirements**: []
**Success Criteria** (what must be TRUE):
  1. `npm run dev` porneste frontend React pe localhost fara erori
  2. `uvicorn main:app` porneste FastAPI cu endpoint `/health` functional
  3. Calculele din app.py sunt disponibile ca endpoint-uri REST
  4. GitHub Actions ruleaza CI la fiecare push
  5. Deploy initial pe Vercel (frontend) si Railway (API) functional
**Plans**: 3 planuri in 2 valuri

Plans:
- [x] 00-01-PLAN.md — React 19 + Vite + TypeScript + Tailwind v4 + shadcn/ui scaffold ✓
- [x] 00-02-PLAN.md — FastAPI backend + migrare calcule anastruct din app.py ✓
- [x] 00-03-PLAN.md — GitHub Actions CI/CD + deploy Vercel (frontend) + Railway (API) ✓

### Phase 1: Design Sistem & Landing Page
**Goal**: Landing page profesional cu design system complet, dark/light mode, animatii si SEO optimizat
**Depends on**: Phase 0
**Requirements**: []
**Success Criteria** (what must be TRUE):
  1. Landing page vizibil la URL-ul de productie cu toate sectiunile (Hero, Features, Pricing, FAQ, CTA)
  2. Dark/light mode functioneaza fara flash
  3. Lighthouse score > 90 pentru Performance si SEO
  4. Mobile-first responsive pe ecrane 320px+
**Plans**: TBD

Plans:
- [x] 01-01: Design system (culori, tipografie, componente shadcn) ✓ 2026-04-11
- [x] 01-02: Landing page sectiuni principale + animatii Framer Motion
- [x] 01-03: SEO, dark/light mode, responsive final

### Phase 2: Modul Grinzi 2D
**Goal**: Calculator interactiv grinzi 2D cu vizualizare diagrame M/T/N animate, export PDF si salvare calcul in cont
**Depends on**: Phase 1
**Requirements**: []
**Success Criteria** (what must be TRUE):
  1. Utilizatorul poate defini o grinda (simplu rezemata, consola, continua) si aplica incarcari
  2. Diagramele M, T, N se calculeaza si se afiseaza corect (validate cu exemple din manuale)
  3. Export PDF genereaza raport cu diagrame si rezultate
  4. Calculul se salveaza in contul utilizatorului
**Plans**: TBD

Plans:
- [ ] 02-01: UI input grinda (tip rezemare, geometrie, incarcari)
- [ ] 02-02: Calcule FEM backend si endpoint-uri API
- [ ] 02-03: Vizualizare diagrame M/T/N animate (D3.js)
- [ ] 02-04: Export PDF si salvare calcul

### Phase 3: Modul Cadre 2D
**Goal**: Editor vizual noduri+bare pentru cadre 2D cu metoda rigiditatilor, deformata animata si eforturi sectionale
**Depends on**: Phase 2
**Requirements**: []
**Success Criteria** (what must be TRUE):
  1. Utilizatorul poate construi un cadru 2D vizual (drag & drop noduri si bare)
  2. Calculul prin metoda rigiditatilor produce rezultate corecte (validate cu Filipescu/Vlad)
  3. Deformata se animeaza vizual
  4. Export complet rezultate
**Plans**: TBD

### Phase 4: Sistem Conturi & Colaborare
**Goal**: Autentificare completa cu dashboard personal, partajare calcule si roluri diferentiate
**Depends on**: Phase 2
**Requirements**: []
**Success Criteria** (what must be TRUE):
  1. Utilizatorul se poate inregistra si loga (email + Google)
  2. Dashboard afiseaza istoricul calculelor salvate
  3. Calculul poate fi partajat printr-un link public
  4. Roluri distincte: Student / Profesor / Admin
**Plans**: TBD

### Phase 5: Mobile App
**Goal**: Aplicatie React Native Expo cu calcule offline publicata pe Google Play si App Store
**Depends on**: Phase 4
**Requirements**: []
**Success Criteria** (what must be TRUE):
  1. App instalabila pe Android si iOS
  2. Calculele de baza merg fara conexiune internet
  3. UI adaptat pentru touch, responsive
**Plans**: TBD

### Phase 6: Landing Page Dedicat & Marketing
**Goal**: Domeniu propriu, blog SEO, analytics si newsletter educational
**Depends on**: Phase 1
**Requirements**: []
**Success Criteria** (what must be TRUE):
  1. Domeniu structcalc.ro (sau .com) activ
  2. Blog cu minimum 3 articole SEO indexate
  3. Analytics (Plausible/PostHog) colecteaza date
**Plans**: TBD

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 0. Setup Proiect | 1/3 | In Progress|  |
| 1. Design Sistem & Landing Page | 2/3 | In Progress|  |
| 2. Modul Grinzi 2D | 0/4 | Not started | - |
| 3. Modul Cadre 2D | 0/0 | Not started | - |
| 4. Sistem Conturi & Colaborare | 0/0 | Not started | - |
| 5. Mobile App | 0/0 | Not started | - |
| 6. Landing Page Dedicat & Marketing | 0/0 | Not started | - |
