# Roadmap — StructCalc (nume de lucru)
> Aplicatie de analiza structurala 2D pentru studenti la constructii
> Student: Pop Rares Darius | Colaborator: Claude (Anthropic)

---

## Viziune
O aplicatie educationala interactiva care ajuta studentii la constructii sa verifice calculele de statica (grinzi, cadre 2D, etc.), sa inteleaga ce se intampla "in spate" si sa invete prin explorare. Tinta: implementare la nivel de facultate ca instrument de verificare dupa orele de statica.

---

## Faze de dezvoltare

### FAZA 1 — Redesign UI radical (prioritate maxima)
**Status:** TODO

- [ ] Inlocuire completa a interfetei Streamlit cu un design modern
- [ ] Layout responsive (desktop + mobile web)
- [ ] Tema inginereasca: curata, profesionala, dark/light mode
- [ ] Navigare clara intre module (grinzi, cadre, sectiuni, etc.)
- [ ] Landing page integrat (prima pagina = prezentare + CTA)
- [ ] Animatii si vizualizari interactive (diagrame M, T, N)
- [ ] Rezultate explicate in cuvinte, nu doar numere

**Deliverable:** App cu UI complet renovat, gata de prezentat

---

### FAZA 2 — Perfectare modul Grinzi 2D
**Status:** TODO (baza existenta in app.py)

- [ ] Calculator grinda simplu rezemata / consola / continua
- [ ] Incarcare distribuita, concentrate, momente
- [ ] Diagrame M, T automate si clare
- [ ] Verificare sectiune (rezistenta, rigiditate)
- [ ] Explicatii pas cu pas (mod educational)
- [ ] Export PDF al calculului complet

---

### FAZA 3 — Perfectare modul Cadre 2D
**Status:** TODO (baza existenta)

- [ ] Cadre plane cu noduri rigide / articulate
- [ ] Metoda rigiditatilor (stiffness method) completa
- [ ] Vizualizare deformata si eforturi sectionale
- [ ] Incarcari multiple simultane
- [ ] Validare rezultate cu exemple din manuale romanesti

---

### FAZA 4 — Mobile App (React Native / Flutter)
**Status:** PLANIFICAT

- [ ] Alegerea framework-ului (Flutter recomandat — un cod, iOS + Android)
- [ ] Port al calculatoarelor principale pe mobile
- [ ] UI optimizat pentru ecrane mici
- [ ] Publicare Google Play Store
- [ ] Publicare Apple App Store
- [ ] Sincronizare calcule cu versiunea web

---

### FAZA 5 — Landing Page & Prezenta Online
**Status:** TODO

- [ ] Landing page dedicat (domeniu propriu, ex: structcalc.ro)
- [ ] Sectiuni: Despre, Functionalitati, Cum functioneaza, FAQ
- [ ] Demo interactiv embedded
- [ ] SEO pentru "calculator grinda", "calcul cadre", etc.
- [ ] Pagina pentru facultati (parteneriat educational)

---

### FAZA 6 — Monetizare (tinta: $5000)
**Status:** PLANIFICAT

#### Strategie (studenti = gratuit, institutii = platit)

| Sursa de venit | Model | Potential |
|---|---|---|
| **Facultati / universitate** | Licenta institutionala anuala | $500-2000/universitate |
| **Birou proiectare** | Abonament profesional | $20-50/luna |
| **Profesori** | Plan premium (rapoarte, istoric) | $10/luna |
| **Donatie voluntara** | "Cumpara-mi o cafea" | variabil |
| **Grant educational** | Fonduri EU / nationale | $1000-5000 |
| **Cursuri / tutoriale** | Video explicate + app | $15-30/curs |

**Principiu:** Studentii folosesc GRATUIT mereu. Platesc cei care au buget (institutii, birouri).

---

### FAZA 7 — Parteneriate Facultati
**Status:** PLANIFICAT

- [ ] Prezentare pilot la o facultate de constructii
- [ ] Feedback de la profesori si studenti
- [ ] Adaptare curricula (exemple din materia lor)
- [ ] Acord de parteneriat / recomandare oficiala

---

## Stare curenta (Aprilie 2026)

| Modul | Stare |
|---|---|
| UI Streamlit | Functional, necesita redesign radical |
| Grinzi 2D | Baza implementata, de perfectionat |
| Cadre 2D | Baza implementata, de perfectionat |
| Sectiuni transversale | Partial implementat |
| Mobile | Neînceput |
| Landing page | Neînceput |
| Monetizare | Neînceput |

---

## Next Steps imediate
1. **Alegem stack-ul UI** — ramane Streamlit modernizat sau migram la FastAPI + React?
2. **Redesign FAZA 1** — incepem cu layout si landing page
3. **Playwright MCP** — instalam browser automation ca sa pot testa app-ul live

---

## Note & Idei
- Nume posibile: StructCalc, StaticaPro, BeamCheck, CadreRO
- Domeniu recomandat: structcalc.ro sau staticapro.ro
- Publicul tinta primar: studenti ani 2-4, Constructii Civile
- Publicul secundar: birouri mici de proiectare, profesori
