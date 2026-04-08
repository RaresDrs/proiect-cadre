# Roadmap — StructCalc
> Aplicatie profesionala de analiza structurala 2D pentru studenti si ingineri
> Student: Pop Rares Darius | AI Partner: Claude (Anthropic Sonnet 4.6)
> Ultima actualizare: Aprilie 2026

---

## Viziune
O aplicatie web + mobile de nivel enterprise care ajuta studentii la constructii
sa verifice calcule de statica (grinzi, cadre 2D etc.), sa inteleaga fizica din
spate si sa invete prin explorare. Tinta: standard de industrie in Romania si
deschidere internationala.

**Stack ales:** React (Vite) + FastAPI + Python backend
**Motiv:** Performanta maxima, separare clara frontend/backend, API reutilizabil
pe mobile, scalabil, modern, angajabil pe piata muncii.

---

## Stack Tehnologic

| Layer | Tehnologie | Rol |
|---|---|---|
| Frontend | React 18 + Vite + TypeScript | UI interactiv, SPA |
| UI Library | shadcn/ui + Tailwind CSS | Design sistem profesional |
| Vizualizari | D3.js + React Three Fiber | Diagrame, animatii 3D viitoare |
| Backend API | FastAPI (Python) | Calcule structurale, REST API |
| Calcule | NumPy + SciPy | Motorul matematic |
| Baza de date | PostgreSQL + SQLAlchemy | Utilizatori, calcule salvate |
| Auth | Supabase Auth | Login, roluri |
| Hosting web | Vercel (frontend) + Railway/Render (API) |
| Mobile | React Native (Expo) | iOS + Android, cod comun cu web |
| CI/CD | GitHub Actions | Deploy automat la push |

---

## Strategia cu Agenti AI (cum lucram noi doi)

### Cum functioneaza cei 24 de agenti disponibili

Folosim sistemul GSD (Get Stuff Done) care orcheztreaza agentii in **valuri paralele**.
Fiecare faza are agenti dedicati care lucreaza simultan:

```
FAZA X
  ├── Val 1 (Cercetare & Planificare)
  │     ├── gsd-phase-researcher  → cerceteaza cum se implementeaza
  │     └── gsd-planner           → scrie planul detaliat (PLAN.md)
  │
  ├── Val 2 (Executie paralela)
  │     ├── gsd-executor [A]      → scrie cod frontend
  │     ├── gsd-executor [B]      → scrie cod backend/API
  │     └── gsd-executor [C]      → scrie teste
  │
  ├── Val 3 (Verificare)
  │     ├── gsd-verifier          → verifica ca totul functioneaza
  │     ├── superpowers:code-reviewer → review cod, best practices
  │     └── gsd-debugger          → rezolva orice bug gasit
  │
  └── Val 4 (UI/UX)
        └── ui-ux-pro-max         → audit vizual, sugereaza imbunatatiri
```

### Comenzi principale pe care le vom folosi

| Comanda | Ce face |
|---|---|
| `/gsd:discuss-phase` | Discutam detaliile inainte de planificare |
| `/gsd:plan-phase` | Planific faza cu agenti paraleli |
| `/gsd:execute-phase` | Execut planul cu agenti in valuri |
| `/gsd:verify-work` | Verific ca totul merge cum trebuie |
| `/gsd:debug` | Debug sistematic cu stare persistenta |
| `/gsd:ui-review` | Audit UI/UX dupa implementare |
| `/superpowers:dispatching-parallel-agents` | Trimitere agenti paraleli independenti |

### Regula de aur
> **Niciodata un singur agent pe o sarcina importanta.**
> Minim: unul scrie, unul testeaza, unul reviewuieste.

---

## Faze de Dezvoltare

### FAZA 0 — Setup Proiect (1-2 zile)
**Status:** URMATORUL PAS

- [ ] Initializare repo React + Vite + TypeScript
- [ ] Setup FastAPI cu structura de proiect
- [ ] Configurare Tailwind + shadcn/ui
- [ ] Setup GitHub Actions pentru CI/CD
- [ ] Migrare calcule din app.py in module FastAPI
- [ ] Deploy initial pe Vercel + Railway

---

### FAZA 1 — Design Sistem & Landing Page (3-5 zile)
**Status:** TODO

- [ ] Design system complet (culori, tipografie, componente)
- [ ] Landing page cu sectiuni:
  - Hero cu demo animat
  - Functionalitati principale
  - Cum functioneaza (pas cu pas)
  - Testimoniale (studenti, profesori)
  - Pricing (Gratuit / Pro / Institutional)
  - FAQ
  - CTA — Inregistrare gratuita
- [ ] Dark/Light mode
- [ ] Animatii cu Framer Motion
- [ ] SEO optimizat (ro + en)
- [ ] Mobile-first responsive

---

### FAZA 2 — Modul Grinzi 2D (5-7 zile)
**Status:** TODO (logica existenta in app.py)

- [ ] Calculator interactiv cu input vizual (drag & drop incarcare)
- [ ] Grinda simplu rezemata, consola, continua, cu overhang
- [ ] Tipuri incarcare: distribuita, concentrata, moment
- [ ] Diagrame M, T, N animate si interactive
- [ ] Verificare sectiune transversala
- [ ] Mod educational: explicatii pas cu pas ale calculului
- [ ] Export PDF profesional
- [ ] Salvare calcul in cont

---

### FAZA 3 — Modul Cadre 2D (5-7 zile)
**Status:** TODO

- [ ] Editor vizual noduri + bare
- [ ] Metoda rigiditatilor completa
- [ ] Vizualizare deformata animata
- [ ] Eforturi sectionale pe fiecare bara
- [ ] Incarcari combinate
- [ ] Validare cu exemple din manuale (Filipescu, Vlad etc.)
- [ ] Export complet

---

### FAZA 4 — Sistem Conturi & Colaborare (3-4 zile)
**Status:** TODO

- [ ] Autentificare (email, Google)
- [ ] Dashboard personal cu istoricul calculelor
- [ ] Partajare calcul cu link
- [ ] Comentarii si adnotari (pt profesori pe calculul studentului)
- [ ] Roluri: Student / Profesor / Admin Institutional

---

### FAZA 5 — Mobile App (7-10 zile)
**Status:** PLANIFICAT

- [ ] React Native cu Expo
- [ ] Partajare logica de calcul cu web
- [ ] UI adaptat pentru touch
- [ ] Calcule offline (local)
- [ ] Publicare Google Play Store
- [ ] Publicare Apple App Store

---

### FAZA 6 — Landing Page Dedicat & Marketing (3-4 zile)
**Status:** PLANIFICAT

- [ ] Domeniu: structcalc.ro (sau .com)
- [ ] Blog tehnic (SEO: "calcul grinda", "cadre statice" etc.)
- [ ] Pagina pentru institutii (cu formular de contact)
- [ ] Integrare analytics (Plausible / PostHog)
- [ ] Newsletter educativ

---

## Plan de Monetizare Detaliat

### Principiu fundamental
> **Studentii folosesc GRATUIT mereu.**
> Platesc cei cu buget institutional sau profesional.

---

### Surse de venit

#### 1. Licente Institutionale (principal)
| Client | Pret anual | Note |
|---|---|---|
| Universitate / Facultate | $500 - $2000 | Acces nelimitat studenti + analytics pentru profesori |
| Liceu tehnic (constructii) | $200 - $500 | Varianta simplificata |
| Birou de proiectare mic | $300 - $800 | Functii avansate, rapoarte |

**Tinta realista an 1:** 3-5 facultati x $800 = $2400 - $4000

---

#### 2. Plan Pro Individual
| Plan | Pret | Inclus |
|---|---|---|
| Student (gratuit) | $0 | Calcule nelimitate, export basic |
| Inginer Pro | $12/luna | Export PDF profesional, istoric, API access |
| Profesor | $8/luna | Vizualizare calculele studentilor, feedback |

---

#### 3. Finantare de Stat & Granturi (PRIORITATE!)

**Programe romanesti aplicabile:**

| Program | Suma | Conditii |
|---|---|---|
| **Start-Up Nation Romania** | pana la 250.000 RON (~$50k) | Firma inregistrata, plan business |
| **Fondul pentru Inovare (UEFISCDI)** | 50.000 - 500.000 RON | Proiect de cercetare aplicata |
| **Studentul Antreprenor (universitati)** | 5.000 - 15.000 RON | Prin universitate, fara firma |
| **Bursa de excelenta (CNFIS)** | variabil | Merit academic + proiect |

**Programe europene:**

| Program | Suma | Note |
|---|---|---|
| **Erasmus+ KA2** | 50k - 300k EUR | Proiecte educationale, parteneriat cu alte uni |
| **Horizon Europe (EIC Accelerator)** | pana la 2.5M EUR | Startup tehnic cu potential scalare |
| **Digital Europe Programme** | variabil | Digitalizare educatie |

**Sponsorizare echipament (PC):**
- **Intel / AMD / NVIDIA** au programe de donatie echipament pentru studenti cu proiecte tehnice relevante
- **Microsoft for Startups** — credite Azure + echipament potential
- **GitHub Student Pack** — acces gratuit la tooluri pro
- **Google for Startups** — credite cloud + mentorat
- Contacteaza direct departamentul CSR al companiilor IT din Romania (Bitdefender, UiPath, Endava)

---

#### 4. Venituri Secundare
- **Cursuri video** pe Udemy/YouTube: "Statica cu StructCalc" — $15-30/curs
- **Consultanta implementare** pentru facultati — $50-100/ora
- **White-label** pentru birouri mari — $2000+ setup
- **Donatie voluntara** (GitHub Sponsors, Buy Me a Coffee)

---

### Tinta financiara

| Perioada | Sursa | Suma estimata |
|---|---|---|
| Lunile 1-3 | Grant universitar / Start | 5.000 - 15.000 RON |
| Lunile 3-6 | 2-3 licente institutionale | $1500 - $3000 |
| Lunile 6-12 | Licente + Pro + donatie | $3000 - $6000 |
| An 2 | Scale + Grant EU | $10.000+ |

**PC upgrade ($5000):** Realist dupa prima runda de licente + un grant mic.
Alternativ: echipament prin grant Start-Up Nation care acopera si hardware.

---

## Stare Curenta (Aprilie 2026)

| Modul | Stare | Note |
|---|---|---|
| Backend calcule | Functional | app.py — de migrat in FastAPI |
| UI Streamlit | Functional | De inlocuit complet |
| Frontend React | Neînceput | FAZA 0 |
| Grinzi 2D | Baza existenta | De perfectionat |
| Cadre 2D | Baza existenta | De perfectionat |
| Mobile | Neînceput | FAZA 5 |
| Landing page | Neînceput | FAZA 6 |
| Monetizare activa | Neînceput | Dupa FAZA 1-2 |

---

## Next Steps ACUM

1. **FAZA 0** — Cream structura React + FastAPI (comanda: `/gsd:plan-phase`)
2. **Browser automation** — instalam Playwright MCP ca sa pot testa app-ul live
3. **Domeniu** — inregistreaza structcalc.ro cat de curand (ieftin, cerut mai tarziu)
4. **Firma / PFA** — incepe procesul cat mai repede pt acces la granturi

---

## Idei pentru Viitor (Backlog)
- Calcul placi si fundatii
- Modul 3D (structuri spatiale)
- AI care explica erorile din calcul
- Integrare cu AutoCAD / Revit
- Versiune in engleza (piata internationala)
- Certificare pentru utilizare profesionala
