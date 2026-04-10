# Phase 1: Design Sistem & Landing Page - Context

**Gathered:** 2026-04-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Landing page profesional pentru StructCalc cu design system complet, dark/light mode, animații și SEO optimizat. Acoperă: design tokens (culori, tipografie, spațiere), componente shadcn extinse, secțiunile Hero / Features / Pricing / FAQ / CTA, PWA manifest, și suport bilingv RO/EN.

Nu include: calculator interactiv (Phase 2), autentificare/conturi (Phase 4), blog SEO (Phase 6), sau AI chat.

</domain>

<decisions>
## Implementation Decisions

### Brand & Visual Identity
- **D-01:** Background `#F5F5F7` (Apple-style neutral gray), nu alb pur
- **D-02:** Text primar `#1D1D1F` (near-black, Apple standard)
- **D-03:** Accent `#2563EB` (engineering blue — evocă blueprints, CAD, precizie)
- **D-04:** Text secundar/muted `#6E6E73`
- **D-05:** Font: Geist variable (deja instalat via `@fontsource-variable/geist`) — NU se instalează Inter sau altceva
- **D-06:** Stil vizual: Minimal Single Column — whitespace generos, tipografie mare, fără decorații excessive. Feeling: Linear.app meets structural engineering.
- **D-07:** Dark mode: background `#000000` sau `#0A0A0A` (OLED-friendly), text `#F5F5F7`, accent rămâne `#2563EB` (ajustat pentru contrast AAA)

### Animații
- **D-08:** Framer Motion instalat și folosit **DOAR** în secțiunea Hero (lazy loaded cu React.lazy / dynamic import)
- **D-09:** Spring physics + stagger entrance pentru Hero (titlu, subtitlu, CTA apar secvențial)
- **D-10:** Restul secțiunilor: fade-in via `tw-animate-css` + IntersectionObserver (zero overhead extra)
- **D-11:** Reguli obligatorii: transform/opacity only, ease-out la intrare, 150-300ms, max 1-2 elemente animate simultan pe view
- **D-12:** `prefers-reduced-motion` OBLIGATORIU respectat — animațiile se dezactivează complet
- **D-13:** Target: Lighthouse Performance ≥ 92

### Structura Landing Page
- **D-14:** Secțiuni în ordine: Hero → Features → Pricing → FAQ → CTA → Footer
- **D-15:** Navigație: sticky top nav cu smooth scroll la anchore (#hero, #features, #pricing, #faq, #cta) — **fără react-router**, un singur SPA
- **D-16:** Nav items: logo stânga, links centru/dreapta, buton "Get Started" CTA în nav

### Secțiunea Hero
- **D-17:** Element vizual: animație CSS/Lottie a unui cadru structural în analiză (grindă cu diagrama M animată). Dacă Lottie JSON nu e disponibil, fallback la o ilustrație SVG a unei grinzi stilizate cu animație CSS.
- **D-18:** Headline mare (≥48px desktop, ≥36px mobile), subheadline, 2 CTA buttons (primar + secundar)

### Secțiunea Pricing
- **D-19:** "Coming soon" placeholder — tiers vizuale cu blur/lock pe tier-urile plătite
- **D-20:** Badge "Coming Q3 2026" pe tier-urile Pro/Enterprise
- **D-21:** Email capture form pentru early access (stocat local sau trimis la un endpoint simplu)
- **D-22:** Tier Free rămâne vizibil și funcțional ca description (fără blur)

### Limbă
- **D-23:** Bilingv RO/EN — toggle în nav (buton RO | EN)
- **D-24:** Conținut default: română (target primar = studenți/ingineri din România)
- **D-25:** i18n implementat ca obiect de traduceri simplu (fără bibliotecă i18n externă dacă e posibil), sau cu `react-i18next` dacă complexitatea o cere — researcher să evalueze

### PWA
- **D-26:** `manifest.json` cu name, short_name, icons (192×192, 512×512), theme_color `#2563EB`, background_color `#F5F5F7`, display: standalone
- **D-27:** Service Worker basic (Workbox sau manual) pentru cache assets statice — nu offline-first complet
- **D-28:** Apple touch icon + meta tags pentru iOS

### Dark/Light Mode
- **D-29:** Implementare via CSS class `.dark` pe `<html>` (deja configurat în `index.css`)
- **D-30:** Persistat în `localStorage`, detectat automat din `prefers-color-scheme` la prima vizită
- **D-31:** Fără flash la reload — script inline în `<head>` înainte de orice CSS (pattern "blocking script")
- **D-32:** Toggle buton în nav (icon soare/lună cu lucide-react, deja instalat)

### Claude's Discretion
- Exact spacing între secțiuni (în limitele sistemului 4/8px)
- Numărul exact de features afișate în secțiunea Features (3 sau 4 carduri)
- Design-ul exact al cardurilor FAQ (accordion vs cards statice)
- Copy-ul (textul) pentru fiecare secțiune — poate fi placeholder profesional
- Implementarea email capture din Pricing (endpoint mock sau localStorage)

</decisions>

<specifics>
## Specific Ideas

- "Fundal gri tip Apple" — folosim exact paleta Apple (#F5F5F7 light, #000000 dark)
- "Ceva ireal și incredibil de inovativ" — Hero animat cu diagrama structurală (cadru/grindă) care se analizează în timp real vizual
- "Să poți numi 'da asta da, site de analiză structurală'" — design-ul trebuie să comunice instant domeniul (engineering, precizie, calcule)
- Feeling: Linear.app (minimal, precis, pentru developeri/ingineri) combinat cu Apple.com (whitespace, tipografie mare, premium)
- Animația Hero: o grindă simplă care se "rezolvă" animat (reacțiuni care apar, diagrama M care se trasează) — face evidentă valoarea aplicației

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap & requirements
- `.planning/ROADMAP.md` — Phase 1 success criteria (secțiuni obligatorii, Lighthouse >90, mobile 320px+, dark/light mode fără flash)

### Design system source
- `frontend/src/index.css` — CSS variables existente pentru dark/light mode; extinde NU rescrie
- `frontend/src/components/ui/button.tsx` — Singurul component shadcn existent; stil consistent cu el
- `frontend/package.json` — Dependințe instalate; verifică înainte de a adăuga altele noi

### ui-ux-pro-max recommendations
- Pattern aplicat: Minimal Single Column (landing.csv)
- Style aplicat: Minimal/Apple-gray cu Dark Mode support
- Checklist obligatoriu: No emojis as icons, cursor-pointer, hover 150-300ms, contrast 4.5:1, prefers-reduced-motion

No external design specs or ADRs exist — requirements fully captured in decisions above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/src/components/ui/button.tsx` — Button component shadcn cu variante (default, outline, ghost, sm/lg). Folosit direct în Hero CTA și nav.
- `lucide-react` (instalat) — Iconuri SVG consistente. Folosit pentru dark/light toggle, nav icons.
- `tw-animate-css` (instalat) — Animații CSS ready-made. Folosit pentru fade-in secțiuni non-Hero.
- `@fontsource-variable/geist` (instalat) — Font deja loaded în `index.css`.

### Established Patterns
- CSS variables în `:root` și `.dark` în `index.css` — extinde cu noile token-uri (nu rescrie structura)
- Tailwind v4 config via `@import "tailwindcss"` — fără `tailwind.config.js`, configurare în CSS
- `@custom-variant dark (&:is(.dark *))` deja definit — dark mode via class pe `<html>`

### Integration Points
- `frontend/src/App.tsx` — Înlocuit complet cu landing page component (sau refactorizat ca router root)
- `frontend/src/main.tsx` — Rămâne neschimbat
- `frontend/index.html` — Adăugăm: manifest link, apple-touch-icon, dark mode blocking script în `<head>`
- `frontend/public/` — PWA icons (192, 512), manifest.json

</code_context>

<deferred>
## Deferred Ideas

- **AI chat assistant** — menționat în discuție; necesită backend AI + auth. Aparține Phase 4+ sau o nouă fază dedicată.
- **Sponsorship plugin** — utilizatorul a menționat un plugin pentru sponsorizare; neimplementat în Phase 1 (pricing = "coming soon"). De revizuit când Phase 4 (conturi) e gata.
- **Blog SEO** — aparține explicit Phase 6 (Landing Page Dedicat & Marketing).
- **PWA offline-first complet** — service worker complet cu sync în background aparține Phase 5 (Mobile App).
- **react-router / /app route** — nu e necesar în Phase 1. Va fi adăugat în Phase 2 când apare primul modul de calcul.

</deferred>

---

*Phase: 01-design-sistem-landing-page*
*Context gathered: 2026-04-10*
