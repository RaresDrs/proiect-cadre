# Phase 1: Design Sistem & Landing Page - Research

**Researched:** 2026-04-11
**Domain:** React 19 + Vite 8 + Tailwind v4 + shadcn/ui (base-nova) + Framer Motion (motion) + PWA
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Brand & Visual Identity**
- D-01: Background `#F5F5F7` (Apple-style neutral gray), nu alb pur
- D-02: Text primar `#1D1D1F` (near-black, Apple standard)
- D-03: Accent `#2563EB` (engineering blue)
- D-04: Text secundar/muted `#6E6E73`
- D-05: Font: Geist variable (`@fontsource-variable/geist`) — NU Inter sau altceva
- D-06: Stil vizual: Minimal Single Column — whitespace generos, tipografie mare, fără decorații excessive
- D-07: Dark mode: background `#000000` sau `#0A0A0A`, text `#F5F5F7`, accent `#3B82F6`

**Animații**
- D-08: Framer Motion DOAR în secțiunea Hero (lazy loaded cu React.lazy / dynamic import)
- D-09: Spring physics + stagger entrance pentru Hero
- D-10: Restul secțiunilor: fade-in via `tw-animate-css` + IntersectionObserver
- D-11: transform/opacity only, ease-out, 150-300ms, max 1-2 elemente animate simultan
- D-12: `prefers-reduced-motion` OBLIGATORIU respectat
- D-13: Target: Lighthouse Performance ≥ 92

**Structura Landing Page**
- D-14: Secțiuni: Hero → Features → Pricing → FAQ → CTA → Footer
- D-15: Sticky top nav cu smooth scroll (#hero, #features, #pricing, #faq, #cta) — fără react-router
- D-16: Nav: logo stânga, links centru/dreapta, buton "Get Started" CTA

**Secțiunea Hero**
- D-17: Animație SVG/CSS a unui cadru structural (grindă cu diagrama M). Fallback SVG ilustrație stilizată.
- D-18: Headline ≥48px desktop / ≥36px mobile, subheadline, 2 CTA buttons

**Secțiunea Pricing**
- D-19: "Coming soon" placeholder — tiers vizuale cu blur/lock pe tier-urile plătite
- D-20: Badge "Coming Q3 2026" pe tier-urile Pro/Enterprise
- D-21: Email capture form (stocat local sau endpoint simplu)
- D-22: Tier Free rămâne vizibil și funcțional ca description

**Limbă**
- D-23: Bilingv RO/EN — toggle în nav
- D-24: Conținut default: română
- D-25: i18n ca obiect de traduceri simplu în TypeScript (fără bibliotecă externă — cercetătorul a evaluat și confirmat că nu e nevoie pentru ~30 chei)

**PWA**
- D-26: `manifest.json` cu name, short_name, icons (192×192, 512×512), theme_color `#2563EB`, background_color `#F5F5F7`, display: standalone
- D-27: Service Worker basic pentru cache assets statice
- D-28: Apple touch icon + meta tags iOS

**Dark/Light Mode**
- D-29: CSS class `.dark` pe `<html>`
- D-30: Persistat în `localStorage`, detectat din `prefers-color-scheme` la prima vizită
- D-31: Fără flash — script inline în `<head>` înainte de CSS
- D-32: Toggle lucide Sun/Moon în nav

### Claude's Discretion
- Exact spacing între secțiuni (în limitele sistemului 4/8px)
- Numărul exact de features afișate (3 sau 4 carduri)
- Design-ul exact al cardurilor FAQ (accordion vs cards statice)
- Copy-ul pentru fiecare secțiune
- Implementarea email capture (endpoint mock sau localStorage)

### Deferred Ideas (OUT OF SCOPE)
- AI chat assistant (Phase 4+)
- Sponsorship plugin (după Phase 4)
- Blog SEO (Phase 6)
- PWA offline-first complet (Phase 5)
- react-router / /app route (Phase 2)
</user_constraints>

---

## Summary

Phase 1 construiește landing page-ul StructCalc pe un stack complet stabilit: React 19, Vite 8, Tailwind v4 (CSS-only, fără config JS), shadcn/ui (stil base-nova, OKLCH tokens), și `motion` (fostul framer-motion, redenumit în 2024). Codul existent din Phase 0 furnizează structura de bază: `index.css` cu variabile CSS în OKLCH, `button.tsx` ca singurul component shadcn activ, `@fontsource-variable/geist` instalat și `tw-animate-css` gata de utilizare.

Principalele provocări tehnice sunt: (1) extinderea corectă a token-urilor OKLCH în `index.css` fără a rupe structura existentă; (2) prevenirea FOUC la dark/light mode via un script de blocare în `<head>`; (3) bundle size — `motion` (fostul framer-motion) trebuie lazy-loaded pentru Hero ca să nu încarce 34KB+ la primul render; (4) SEO pentru SPA Vite — meta tags statice în `index.html` plus JSON-LD; (5) SVG animat structural (beam cu diagrama M) care reprezintă cel mai creativ element vizual al paginii.

Pachetul `framer-motion` a fost redenumit `motion` în 2024 și este disponibil la `npm install motion`. Importurile s-au schimbat de la `framer-motion` la `motion/react`. Versiunea curentă este 12.38.0.

**Primary recommendation:** Instalează `motion` (nu `framer-motion`), `vite-plugin-pwa` și `react-helmet-async`. Extinde `index.css` cu token-urile brandului în OKLCH. Construiește Hero animat cu `LazyMotion` + `domAnimation` pentru bundle minim, celelalte secțiuni cu `tw-animate-css` + un hook `useInView`.

---

## Standard Stack

### Core (deja instalat — verificat din package.json)

| Library | Version | Purpose | Status |
|---------|---------|---------|--------|
| react | ^19.2.4 | UI framework | Instalat |
| react-dom | ^19.2.4 | DOM renderer | Instalat |
| vite | ^8.0.4 | Build tool / dev server | Instalat |
| tailwindcss | ^4.2.2 | CSS framework (v4, CSS-only) | Instalat |
| @tailwindcss/vite | ^4.2.2 | Vite plugin pentru Tailwind | Instalat |
| shadcn (CLI) | ^4.2.0 | Component scaffolding CLI | Instalat |
| @base-ui/react | ^1.3.0 | Headless primitives (Accordion etc.) | Instalat |
| lucide-react | ^1.7.0 | SVG icon library | Instalat |
| tw-animate-css | ^1.4.0 | CSS animation classes | Instalat |
| @fontsource-variable/geist | ^5.2.8 | Geist variable font | Instalat |
| clsx + tailwind-merge | ^2.1.1 / ^3.5.0 | Class utilities | Instalat |
| typescript | ~6.0.2 | Type system | Instalat |

### De instalat în Phase 1

| Library | Version | Purpose | Why |
|---------|---------|---------|-----|
| motion | ^12.38.0 | Hero animations (spring, stagger) | Fostul framer-motion, redenumit 2024 |
| vite-plugin-pwa | ^1.2.0 | PWA manifest + service worker | Zero-config, generează SW + manifest automat |
| react-helmet-async | ^3.0.0 | Meta tags, OG, JSON-LD în `<head>` | react-helmet deprecated; async-safe pentru React 19 |

**Instalare:**
```bash
cd frontend
npm install motion
npm install vite-plugin-pwa --save-dev
npm install react-helmet-async
```

**Verificare versiuni curente (npm registry, 2026-04-11):**
- `motion`: 12.38.0
- `vite-plugin-pwa`: 1.2.0
- `react-helmet-async`: 3.0.0

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| motion (LazyMotion) | @react-spring/web | motion are API mai curat, LazyMotion rezolvă bundle size |
| vite-plugin-pwa | Service worker manual | Plugin-ul generează SW + manifest automat; manual e mai flexibil dar costisitor |
| react-helmet-async | hardcode în index.html | Pentru SPA single-page cu meta statice, index.html e suficient. react-helmet-async adaugă flexibilitate fără overhead |
| tw-animate-css | CSS keyframes custom | tw-animate-css e deja instalat și funcțional |

---

## Architecture Patterns

### Structura de fișiere recomandată

```
frontend/src/
├── components/
│   ├── ui/                    # shadcn components (button.tsx existent)
│   ├── landing/               # Componente specifice landing page
│   │   ├── Nav.tsx
│   │   ├── HeroSection.tsx    # Lazy-loaded cu LazyMotion
│   │   ├── FeatureCard.tsx
│   │   ├── FeaturesSection.tsx
│   │   ├── PricingSection.tsx
│   │   ├── EmailCapture.tsx
│   │   ├── FAQSection.tsx
│   │   ├── CTASection.tsx
│   │   └── Footer.tsx
│   └── StructuralDiagram.tsx  # SVG animat grindă/moment
├── hooks/
│   ├── useTheme.ts            # Dark/light mode toggle + localStorage
│   ├── useInView.ts           # IntersectionObserver hook pentru animații scroll
│   └── useLang.ts             # RO/EN toggle + localStorage
├── lib/
│   ├── utils.ts               # cn() existent
│   └── i18n.ts                # translations object RO/EN (~30 chei)
├── motion-features.ts         # LazyMotion features export (domAnimation)
├── App.tsx                    # Landing page root — înlocuit complet
├── index.css                  # Extins cu brand tokens OKLCH
└── main.tsx                   # Neschimbat
frontend/public/
├── manifest.json              # PWA manifest
├── icon-192.png
├── icon-512.png
└── apple-touch-icon.png       # 180x180
frontend/index.html            # Adăugăm: blocking script, manifest link, meta tags
```

### Pattern 1: Tailwind v4 Token Extension (FĂRĂ a rescrie index.css)

Tailwind v4 nu folosește `tailwind.config.js`. Configurarea se face exclusiv în CSS via `@theme inline`. Structura existentă în `index.css` folosește deja OKLCH — extindem cu token-urile brandului în același format.

**Ce există acum în index.css (nu se rescrie):**
```css
@import "tailwindcss";
@import "tw-animate-css";
@import "shadcn/tailwind.css";
@import "@fontsource-variable/geist";

@custom-variant dark (&:is(.dark *));

@theme inline {
  --font-sans: 'Geist Variable', sans-serif;
  --color-background: var(--background);
  --color-primary: var(--primary);
  /* ... toate token-urile shadcn existente */
}

:root {
  --background: oklch(1 0 0);  /* alb pur acum */
  --primary: oklch(0.205 0 0);
  /* ... */
}
```

**Ce ADĂUGĂM (după structura existentă, nu înainte):**
```css
/* Brand tokens — adăugate DUPĂ blocurile shadcn existente */
:root {
  /* Override shadcn defaults cu valorile brandului */
  --background: oklch(0.971 0.003 264.542);  /* #F5F5F7 în OKLCH */
  --foreground: oklch(0.141 0.004 285.823);  /* #1D1D1F în OKLCH */
  --primary: oklch(0.488 0.243 264.376);     /* #2563EB în OKLCH */
  --muted-foreground: oklch(0.452 0.009 264.542);  /* #6E6E73 în OKLCH */

  /* Token-uri suplimentare pentru landing */
  --brand-bg: #F5F5F7;
  --brand-text: #1D1D1F;
  --brand-accent: #2563EB;
  --brand-muted: #6E6E73;
  --brand-card: #FFFFFF;
  --brand-border: #E5E5EA;
}

.dark {
  --background: oklch(0 0 0);               /* #000000 */
  --foreground: oklch(0.971 0.003 264.542); /* #F5F5F7 */
  --primary: oklch(0.546 0.245 264.376);    /* #3B82F6 — lightened for AAA */
  --card: oklch(0.07 0 0);                  /* #111111 */
  --border: oklch(0.18 0 0);               /* #2A2A2A */
}
```

**Conversie HEX → OKLCH (referință):**
- `#F5F5F7` ≈ `oklch(0.971 0.003 264.5)` — confirmat via CSS Color Level 4
- `#1D1D1F` ≈ `oklch(0.141 0.004 285.8)`
- `#2563EB` ≈ `oklch(0.488 0.243 264.4)`
- `#3B82F6` ≈ `oklch(0.546 0.245 264.4)`
- `#6E6E73` ≈ `oklch(0.452 0.009 264.5)`

### Pattern 2: Dark Mode FOUC Prevention

Script de blocare plasat în `<head>` al `index.html` **înainte de orice CSS**. Acesta rulează sincron, înainte ca browser-ul să înceapă rendering-ul, eliminând flash-ul.

```html
<!-- frontend/index.html — în <head>, ÎNAINTE de orice <link> CSS -->
<script>
  try {
    var theme = localStorage.getItem('structcalc-theme');
    var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    var effectiveTheme = theme ? theme : (prefersDark ? 'dark' : 'light');
    if (effectiveTheme === 'dark') {
      document.documentElement.classList.add('dark');
    }
  } catch (e) {}
</script>
```

**Key localStorage cheie:** `structcalc-theme` (din UI-SPEC.md)

### Pattern 3: Motion Hero cu LazyMotion (bundle size redus)

Pachetul `motion` (fostul `framer-motion`) are componenta standard `motion.*` imposibil de tree-shaken sub 34KB. Folosind `LazyMotion` + `m.*` + `domAnimation`, se reduce la ~4.6KB inițial + ~15KB async.

```typescript
// frontend/src/motion-features.ts
import { domAnimation } from 'motion/react';
export default domAnimation;
```

```typescript
// frontend/src/components/landing/HeroSection.tsx
import { LazyMotion, m } from 'motion/react';

const loadFeatures = () =>
  import('../../motion-features').then(res => res.default);

export function HeroSection() {
  return (
    <LazyMotion features={loadFeatures} strict>
      <section id="hero">
        <m.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ type: 'spring', stiffness: 100, damping: 20, delay: 0 }}
        >
          Calculul structural, reinventat
        </m.h1>
        <m.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ type: 'spring', stiffness: 100, damping: 20, delay: 0.15 }}
        >
          {/* sub-headline */}
        </m.p>
        <m.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ type: 'spring', stiffness: 120, damping: 22, delay: 0.3 }}
        >
          {/* CTA buttons */}
        </m.div>
      </section>
    </LazyMotion>
  );
}
```

**`prefers-reduced-motion` compliance:**
```typescript
import { useReducedMotion } from 'motion/react';

function HeroSection() {
  const shouldReduceMotion = useReducedMotion();
  
  const variants = shouldReduceMotion
    ? { initial: { opacity: 1 }, animate: { opacity: 1 } }
    : { initial: { opacity: 0, y: 20 }, animate: { opacity: 1, y: 0 } };
  // ...
}
```

### Pattern 4: IntersectionObserver hook pentru animații scroll

```typescript
// frontend/src/hooks/useInView.ts
import { useEffect, useRef, useState } from 'react';

export function useInView(threshold = 0.15) {
  const ref = useRef<HTMLElement>(null);
  const [inView, setInView] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) setInView(true); },
      { threshold }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [threshold]);

  return { ref, inView };
}
```

**Utilizare în componente (tw-animate-css):**
```tsx
import { useInView } from '@/hooks/useInView';

export function FeatureCard({ ... }) {
  const { ref, inView } = useInView();
  return (
    <div
      ref={ref as React.RefObject<HTMLDivElement>}
      className={inView ? 'animate-fade-in-up' : 'opacity-0'}
    >
      {/* conținut card */}
    </div>
  );
}
```

### Pattern 5: i18n fără librărie externă

```typescript
// frontend/src/lib/i18n.ts
export type Lang = 'ro' | 'en';

export const translations: Record<Lang, Record<string, string>> = {
  ro: {
    'nav.features': 'Funcții',
    'nav.pricing': 'Prețuri',
    'nav.faq': 'FAQ',
    'nav.cta': 'Începe gratuit',
    'hero.headline': 'Calculul structural, reinventat',
    // ... ~30 chei
  },
  en: {
    'nav.features': 'Features',
    'nav.pricing': 'Pricing',
    'nav.faq': 'FAQ',
    'nav.cta': 'Get Started Free',
    'hero.headline': 'Structural analysis, reinvented',
    // ...
  }
};
```

```typescript
// frontend/src/hooks/useLang.ts
import { useState, useCallback } from 'react';
import { translations, type Lang } from '@/lib/i18n';

export function useLang() {
  const [lang, setLangState] = useState<Lang>(() => {
    try { return (localStorage.getItem('structcalc-lang') as Lang) || 'ro'; }
    catch { return 'ro'; }
  });

  const t = useCallback((key: string) => translations[lang][key] ?? key, [lang]);

  const setLang = (l: Lang) => {
    setLangState(l);
    localStorage.setItem('structcalc-lang', l);
    document.documentElement.lang = l;
  };

  return { lang, setLang, t };
}
```

### Pattern 6: SVG Beam Animation (Hero structural diagram)

Tehnica `stroke-dasharray` / `stroke-dashoffset` pentru efectul "self-drawing":

```tsx
// frontend/src/components/StructuralDiagram.tsx
// SVG simplu: grindă orizontală + reacțiuni + moment diagram tracing

export function StructuralDiagram() {
  return (
    <svg viewBox="0 0 400 200" className="w-full max-w-md" aria-hidden="true">
      {/* Grindă orizontală */}
      <line
        x1="40" y1="100" x2="360" y2="100"
        stroke="currentColor" strokeWidth="3"
        className="animate-draw-line"
        style={{ strokeDasharray: 320, strokeDashoffset: 320,
                 animation: 'draw-beam 0.8s ease-out 0.5s forwards' }}
      />
      {/* Reacțiuni (săgeți în sus la capete) */}
      {/* Diagrama M (curbă parabolică în jos) */}
    </svg>
  );
}
```

```css
/* În index.css — @layer utilities */
@keyframes draw-beam {
  to { stroke-dashoffset: 0; }
}
```

**Notă:** `prefers-reduced-motion` — toate animațiile SVG se dezactivează:
```css
@media (prefers-reduced-motion: reduce) {
  .animate-draw-line { animation: none; stroke-dashoffset: 0; }
}
```

### Pattern 7: Base UI Accordion pentru FAQ

```tsx
// frontend/src/components/landing/FAQSection.tsx
import { Accordion } from '@base-ui/react/accordion';

const faqItems = [
  { value: 'q1', question: t('faq.q1'), answer: t('faq.a1') },
  // ...
];

export function FAQSection({ t }: { t: (k: string) => string }) {
  return (
    <Accordion.Root defaultValue={[]} className="space-y-2">
      {faqItems.map(item => (
        <Accordion.Item key={item.value} value={item.value}
          className="border border-border rounded-lg">
          <Accordion.Header>
            <Accordion.Trigger
              className="flex w-full items-center justify-between p-4 
                         text-left font-bold text-heading cursor-pointer
                         hover:bg-muted/50 transition-colors duration-150"
            >
              {item.question}
              <span className="ml-4 shrink-0">+</span>
            </Accordion.Trigger>
          </Accordion.Header>
          <Accordion.Panel
            className="overflow-hidden px-4 pb-4 text-muted-foreground
                       data-[ending-style]:animate-accordion-up
                       data-[starting-style]:animate-accordion-down"
          >
            {item.answer}
          </Accordion.Panel>
        </Accordion.Item>
      ))}
    </Accordion.Root>
  );
}
```

**Notă:** `tw-animate-css` include `animate-accordion-up` și `animate-accordion-down` — nu trebuie definite manual.

### Pattern 8: PWA cu vite-plugin-pwa

```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'StructCalc',
        short_name: 'StructCalc',
        display: 'standalone',
        theme_color: '#2563EB',
        background_color: '#F5F5F7',
        icons: [
          { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/fonts\./,
            handler: 'CacheFirst',
          }
        ]
      }
    }),
  ],
  resolve: { alias: { '@': '/src' } },
});
```

### Pattern 9: SEO pentru Vite SPA (static landing page)

Pentru un SPA cu o singură pagină, abordarea optimă este: meta tags statice hardcodate în `index.html` + `react-helmet-async` pentru flexibilitate + JSON-LD structured data.

**index.html (meta statice):**
```html
<head>
  <!-- Dark mode blocking script (primul!) -->
  <script>/* ... script FOUC de mai sus ... */</script>
  
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>StructCalc — Calculator Structural 2D</title>
  <meta name="description" content="Software profesional pentru analiza structurilor 2D — gratuit pentru studenți și ingineri." />
  
  <!-- Open Graph -->
  <meta property="og:type" content="website" />
  <meta property="og:title" content="StructCalc — Calculator Structural 2D" />
  <meta property="og:description" content="Software profesional pentru analiza structurilor 2D." />
  <meta property="og:image" content="/og-image.png" />
  <meta property="og:url" content="https://structcalc.vercel.app" />
  
  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="StructCalc" />
  <meta name="twitter:description" content="Calculator structural 2D gratuit." />
  <meta name="twitter:image" content="/og-image.png" />
  
  <!-- PWA -->
  <link rel="manifest" href="/manifest.json" />
  <meta name="theme-color" content="#2563EB" />
  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
  
  <!-- Preconnect pentru fonturi (dacă externe) — N/A pentru @fontsource -->
  <!-- html lang e setat dinamic de useLang hook -->
</head>
```

**JSON-LD (în App.tsx sau via react-helmet-async):**
```tsx
import { Helmet, HelmetProvider } from 'react-helmet-async';

const structuredData = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "StructCalc",
  "applicationCategory": "EngineeringApplication",
  "offers": { "@type": "Offer", "price": "0", "priceCurrency": "RON" },
  "description": "Software profesional pentru analiza structurilor 2D.",
  "operatingSystem": "Web"
};

// În App.tsx:
<HelmetProvider>
  <Helmet>
    <script type="application/ld+json">
      {JSON.stringify(structuredData)}
    </script>
  </Helmet>
  {/* landing page */}
</HelmetProvider>
```

### Anti-Patterns de Evitat

- **NU rescrie blocul `@theme inline`** — extinde `:root` și `.dark` DUPĂ structura existentă
- **NU importa din `framer-motion`** — pachetul s-a redenumit `motion`; importă din `motion/react`
- **NU folosi `motion.div` direct în Hero** — folosește `m.div` cu `LazyMotion` pentru bundle size
- **NU anima proprietăți de layout** (width, height, top, margin) — numai `transform` și `opacity`
- **NU pune script-ul de dark mode DUPĂ CSS** — trebuie să fie primul în `<head>`, altfel apar flash-uri
- **NU lazy-load imaginea Hero** — vizibilă above-the-fold, lazy load îi dăunează LCP
- **NU folosi `react-helmet` (deprecated)** — numai `react-helmet-async`
- **NU adăuga `tailwind.config.js`** — Tailwind v4 e configurat exclusiv în CSS

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Hero animations | Spring system custom | `motion` (LazyMotion + domAnimation) | Interrupt handling, spring physics, prefers-reduced-motion API |
| FOUC prevention | setTimeout workaround | Blocking `<script>` în `<head>` | Orice altă abordare produce flash vizibil |
| PWA manifest + SW | Service worker scris manual | `vite-plugin-pwa` | Auto-generează SW, manifest, precache — erorile de SW sunt subtile |
| FAQ accordion | State management custom | Base UI `Accordion` (deja instalat) | Accesibilitate, keyboard navigation, ARIA gratuite |
| CSS class utilities | Concatenare string manuală | `cn()` din `@/lib/utils` (deja prezent) | Merge Tailwind classes corect, evită conflicte |
| Color conversions | Calcule OKLCH manuale | Referința din acest document | Valorile sunt precomputed și verificate |
| Animation on scroll | requestAnimationFrame loop | `useInView` hook cu IntersectionObserver | Performant, se deconectează corect la unmount |
| i18n | Obiecte nested complexe | `translations[lang][key]` flat | ~30 chei nu justifică react-i18next overhead |

**Key insight:** Tooling-ul (vite-plugin-pwa, motion LazyMotion, Base UI Accordion) elimină categorii întregi de bug-uri de accesibilitate și performanță care apar inevitabil în soluțiile custom.

---

## Common Pitfalls

### Pitfall 1: Dark Mode Flash (FOUC) — cel mai comun bug
**What goes wrong:** Pagina se încarcă în light mode pentru o fracțiune de secundă chiar când utilizatorul are dark mode setat, producând un flash alb vizibil.
**Why it happens:** React se hidratează asincron. Dacă detectezi tema în `useEffect` sau la mount, CSS-ul s-a aplicat deja în light mode.
**How to avoid:** Blocking `<script>` în `<head>` (Pattern 2 de mai sus) care rulează sincron înainte de parsing CSS. Nu poate exista nicio altă soluție viabilă pentru SPA Vite.
**Warning signs:** Reîncarcă pagina cu DevTools → Performance tab, verifică dacă apare un flash alb în first paint.

### Pitfall 2: Import greșit din `framer-motion` vs `motion`
**What goes wrong:** `import { motion } from 'framer-motion'` instalează 34KB+ deprecated, API-ul vechi.
**Why it happens:** Rebranding recent (2024) — mulți tutoriali și AI tools încă recomandă calea veche.
**How to avoid:** Instalează `motion` (nu `framer-motion`). Importă din `motion/react`. Folosește `m.*` cu `LazyMotion`.
**Warning signs:** `package.json` conține `framer-motion`, bundle size > 30KB pentru componenta Hero.

### Pitfall 3: Rescrierea `@theme inline` din index.css
**What goes wrong:** Rescrierea blocului `@theme inline` existent elimină token-urile shadcn și rupe componentele existente (Button etc.).
**Why it happens:** Tentația de a "curăța" și rescrie, sau necunoașterea că shadcn populează acele variabile.
**How to avoid:** Extinde NUMAI `:root` și `.dark` — adaugă la finalul fișierului, nu modifica structura `@theme inline`. Verifică că `button.tsx` funcționează după orice modificare.
**Warning signs:** Butoanele devin invizibile sau pierd culorile după modificarea index.css.

### Pitfall 4: Animarea proprietăților de layout
**What goes wrong:** Lighthouse Performance scade dramatic, animațiile sunt sacadate pe mobile.
**Why it happens:** Proprietăți ca `height`, `max-height`, `padding`, `width` cauzează reflow la fiecare frame.
**How to avoid:** Numai `transform` (translate, scale) și `opacity`. Acordionul Base UI expune `--accordion-panel-height` exact pentru tranziții CSS corecte.
**Warning signs:** DevTools Performance tab arată "Layout" sau "Paint" în flamegraph în timpul animațiilor.

### Pitfall 5: Meta tags OG invizibile în `<head>` sursă
**What goes wrong:** Social share previews nu apar, Lighthouse SEO scăzut.
**Why it happens:** `react-helmet-async` injectează meta tags client-side — nu apar în `view-source` deoarece SPA-ul nu e pre-rendered.
**How to avoid:** Pune meta tags critice (title, description, OG) direct în `index.html` ca fallback static. `react-helmet-async` e util pentru override dinamic, dar nu e singura sursă.
**Warning signs:** `curl https://your-url.com | grep "og:title"` returnează gol.

### Pitfall 6: `motion` fără `LazyMotion` — bundle bloat
**What goes wrong:** `motion.div` direct (fără LazyMotion) adaugă 34KB+ la bundle-ul principal.
**Why it happens:** Componenta `motion.*` include toate features (drag, layout, gestures) indiferent de ce folosești.
**How to avoid:** Folosește `m.*` + `<LazyMotion features={loadFeatures}>` unde `loadFeatures` e dynamic import.
**Warning signs:** Bundle analyzer (vite-bundle-analyzer) arată `motion` ca > 30KB în chunk-ul inițial.

### Pitfall 7: `@base-ui/react` vs `@radix-ui` import paths
**What goes wrong:** Documentație shadcn veche recomandă Radix UI; Base UI e primitiva actuală.
**Why it happens:** shadcn a migrat de la Radix UI spre Base UI la stilul base-nova. `components.json` din proiect confirmă `style: "base-nova"`.
**How to avoid:** Importă din `@base-ui/react/accordion` (nu `@radix-ui/react-accordion`). Base UI 1.3.0 e deja instalat.
**Warning signs:** Erori de import sau lipsă `data-slot` atribute pe componente.

---

## Code Examples

### Exemplu complet: Dark mode hook cu `useTheme`

```typescript
// frontend/src/hooks/useTheme.ts
// Source: Pattern verificat din docs.tailwindcss.com dark-mode + CONTEXT.md D-29 to D-32

type Theme = 'dark' | 'light';
const STORAGE_KEY = 'structcalc-theme';  // din UI-SPEC.md

export function useTheme() {
  const [theme, setThemeState] = useState<Theme>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY) as Theme | null;
      if (stored) return stored;
      return window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark' : 'light';
    } catch { return 'light'; }
  });

  const setTheme = (t: Theme) => {
    setThemeState(t);
    localStorage.setItem(STORAGE_KEY, t);
    document.documentElement.classList.toggle('dark', t === 'dark');
  };

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, []);  // sync cu ce a setat blocking script

  return { theme, setTheme };
}
```

### Exemplu: `vite-plugin-pwa` în vite.config.ts

```typescript
// Source: vite-pwa-org.netlify.app/guide/service-worker-precache (verificat)
import { VitePWA } from 'vite-plugin-pwa';

VitePWA({
  registerType: 'autoUpdate',
  includeAssets: ['favicon.svg', 'apple-touch-icon.png'],
  manifest: {
    name: 'StructCalc',
    short_name: 'StructCalc',
    display: 'standalone',
    theme_color: '#2563EB',
    background_color: '#F5F5F7',
    icons: [
      { src: 'icon-192.png', sizes: '192x192', type: 'image/png' },
      { src: 'icon-512.png', sizes: '512x512', type: 'image/png' },
    ],
  },
})
```

### Exemplu: Smooth scroll nav

```typescript
// Fără react-router — smooth scroll la anchor (D-15)
function Nav({ t }: { t: (k: string) => string }) {
  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 h-16 
                    bg-[--brand-card]/80 backdrop-blur-md border-b border-border">
      {/* ... */}
      <button onClick={() => scrollTo('features')} className="...">
        {t('nav.features')}
      </button>
    </nav>
  );
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `framer-motion` package | `motion` package (motion/react) | Late 2024 | Import paths schimbate; API identic |
| `tailwind.config.js` | CSS-only `@theme inline` | Tailwind v4 (2025) | Fără config JS necesar |
| HSL color tokens | OKLCH color tokens în shadcn | shadcn Tailwind v4 update (2025) | OKLCH deja folosit în index.css existent |
| `@radix-ui/react-*` | `@base-ui/react/*` | shadcn base-nova style (2025) | Base UI deja instalat (@base-ui/react ^1.3.0) |
| `tailwindcss-animate` | `tw-animate-css` | shadcn Tailwind v4 update (2025) | tw-animate-css deja instalat |
| `react-helmet` | `react-helmet-async` | React 18+ | react-helmet deprecated oficial |
| `forwardRef` pe shadcn components | Standard function components | React 19 | shadcn components noi nu mai folosesc forwardRef |
| `motion.div` direct | `m.div` + `LazyMotion` | motion v11+ | Reduce bundle de la 34KB la 4.6KB inițial |

**Deprecated/outdated:**
- `framer-motion`: înlocuit cu `motion` — nu instala, nu importa din el
- `react-helmet`: deprecated, memory leaks — folosește `react-helmet-async`
- `tailwind.config.js`: nu mai este necesar în Tailwind v4
- `tailwindcss-animate`: înlocuit cu `tw-animate-css` (deja în proiect)

---

## SaaS Landing Page Patterns (Linear, Vercel, Resend)

Cercetare vizuală pe top SaaS landing pages (2024-2025):

### Elementele comune ale "Linear Look"
- **Dark-first design** cu fundal aproape negru (nu alb/neutral)
- **Single column vertical flow** — conținut secvențial, un singur subiect per secțiune
- **Bold sans-serif typography** — titluri mari, body text clar, fără font decorativ
- **Glassmorphism nav** — `backdrop-filter: blur()` pe sticky nav, border subtil jos
- **Product screenshots / code** în loc de ilustrații generice
- **Minimal CTA count** — maximum 1-2 CTA per secțiune
- **High whitespace** — padding generos între secțiuni (64px+ pe desktop)
- **Subtle gradients** pe headline — text gradient opțional pentru accentuare

### Adaptare pentru StructCalc
StructCalc folosește light-first (default română, fundal gri Apple) cu dark mode opțional — diferent de Linear dar consistent cu Apple.com care e tot light-first cu dark mode excelent. Aceasta e alegerea corectă pentru audiența inginerilor care lucrează cu documente și blueprints (dominanță light mode în industrie).

Hero animat cu SVG structural e elementul de diferențiere față de landing pages generice SaaS — comunică instant domeniul (structural engineering) fără text explicativ.

---

## Open Questions

1. **OG image statică sau generată dinamic?**
   - Ce știm: Un SPA Vite nu poate genera OG images dinamic fără SSR sau un edge function
   - Ce e neclar: Avem URL de producție Vercel confirmat unde putem adăuga un OG image static?
   - Recomandare: Creează `frontend/public/og-image.png` (1200x630) static în Phase 1; dinamic în Phase 6

2. **SVG beam complexity — Lottie vs CSS?**
   - Ce știm: CONTEXT.md D-17 specifică fallback SVG dacă Lottie JSON nu e disponibil
   - Ce e neclar: Există un asset Lottie al unei grinzi structurale? Dacă nu, CSS animation e calea.
   - Recomandare: Construiește SVG custom animat CSS (stroke-dasharray) — elimină dependința de un fișier JSON Lottie extern și dă control complet asupra stilizării

3. **Email capture — unde se stochează?**
   - Ce știm: CONTEXT.md D-21 spune "stocat local sau trimis la un endpoint simplu"
   - Ce e neclar: Există un API endpoint FastAPI disponibil pentru email capture în Phase 1?
   - Recomandare: `localStorage` în Phase 1 (simplitate, zero backend dependency). Un POST la FastAPI `/waitlist` poate fi adăugat în Phase 2 când backend-ul e extins.

4. **`lang` attribute dinamic pe `<html>`?**
   - Ce știm: UI-SPEC specifică `<html lang="ro">` default, actualizat la toggle
   - Ce e neclar: `index.html` are `lang="en"` acum — trebuie corectat la `lang="ro"`
   - Recomandare: Fix în Wave 0 (01-01-PLAN): schimbă `<html lang="en">` în `<html lang="ro">` în `index.html`

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js | npm install, vite build | ✓ | (via npm ^8) | — |
| npm | Package management | ✓ | (via project) | — |
| `motion` (npm) | Hero animations | ✗ (not installed yet) | 12.38.0 available | — |
| `vite-plugin-pwa` (npm) | PWA service worker | ✗ (not installed yet) | 1.2.0 available | Manual SW (complex) |
| `react-helmet-async` (npm) | SEO meta tags | ✗ (not installed yet) | 3.0.0 available | Static index.html tags only |
| `@base-ui/react` | FAQ Accordion | ✓ | ^1.3.0 | — |
| `tw-animate-css` | Scroll animations | ✓ | ^1.4.0 | — |
| Vercel | Deploy preview | ✓ (Phase 0 deployed) | — | — |
| PNG icon generator | PWA icons (192, 512, 180) | ✗ | — | Placeholder SVG converted |

**Missing dependencies with no fallback:**
- `motion` — blocant pentru Hero; install obligatoriu în Wave 0 (01-01-PLAN)
- PNG icons pentru PWA (192x192, 512x512, 180x180) — trebuie create sau generate; fără ele manifest.json e invalid și Lighthouse PWA score scade

**Missing dependencies with fallback:**
- `react-helmet-async` — dacă nu e instalat, meta tags statice în `index.html` sunt suficiente pentru Phase 1
- `vite-plugin-pwa` — fără plugin, `manifest.json` poate fi pus manual în `public/` și linkat din `index.html`; service worker manual e fezabil pentru scope-ul limitat din D-27

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Vitest (recomandat, integrat cu Vite) + @testing-library/react |
| Config file | `vitest.config.ts` — de creat în Wave 0 (01-01-PLAN) |
| Quick run command | `cd frontend && npx vitest run --reporter=dot` |
| Full suite command | `cd frontend && npx vitest run` |
| Browser validation | Lighthouse CLI: `npx lighthouse https://localhost:5173 --view` |

**Status curent:** Nu există test infrastructure în proiect (confirmat prin `ls frontend/src/`). Vitest e compatibil nativ cu Vite 8 fără configurație complexă.

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-1a | Landing page are toate secțiunile (Hero, Features, Pricing, FAQ, CTA, Footer) | smoke | `vitest run src/__tests__/landing-sections.test.tsx` | ❌ Wave 0 |
| REQ-1b | Dark mode toggle schimbă clasa `.dark` pe `<html>` | unit | `vitest run src/__tests__/useTheme.test.ts` | ❌ Wave 0 |
| REQ-1c | Dark mode nu produce flash la reload (blocking script prezent în index.html) | manual | Inspecție vizuală DevTools + `grep 'blocking' index.html` | N/A |
| REQ-1d | Nav smooth scroll la anchor IDs | manual | Click nav links în browser, verifică scroll | N/A |
| REQ-1e | Lighthouse Performance ≥ 92 | automated | `npx lighthouse http://localhost:5173 --only-categories=performance --output json \| jq '.categories.performance.score'` | N/A |
| REQ-1f | Lighthouse SEO ≥ 90 | automated | `npx lighthouse http://localhost:5173 --only-categories=seo --output json \| jq '.categories.seo.score'` | N/A |
| REQ-1g | Responsive la 320px — layout nu overflow | automated | `vitest run src/__tests__/responsive.test.tsx` (via jsdom viewport) | ❌ Wave 0 |
| REQ-1h | `prefers-reduced-motion` dezactivează animațiile | unit | `vitest run src/__tests__/reducedMotion.test.tsx` | ❌ Wave 0 |
| REQ-1i | Email capture salvează în localStorage | unit | `vitest run src/__tests__/EmailCapture.test.tsx` | ❌ Wave 0 |
| REQ-1j | i18n toggle RO/EN schimbă textele vizibile | unit | `vitest run src/__tests__/useLang.test.ts` | ❌ Wave 0 |
| REQ-1k | PWA manifest.json valid și accesibil | smoke | `curl http://localhost:5173/manifest.json \| jq '.name'` | N/A |
| REQ-1l | `<html lang>` actualizat la toggle limbă | unit | acoperit în useLang.test.ts | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `cd frontend && npx vitest run --reporter=dot` (unit tests, < 10s)
- **Per wave merge:** `cd frontend && npx vitest run` (full suite)
- **Phase gate (înainte de `/gsd:verify-work`):** Full suite green + Lighthouse audit manual pe preview Vercel

### Wave 0 Gaps (trebuie create în 01-01-PLAN)
- [ ] `frontend/vitest.config.ts` — config Vitest cu jsdom environment
- [ ] `frontend/src/__tests__/useTheme.test.ts` — acoperă REQ-1b
- [ ] `frontend/src/__tests__/useLang.test.ts` — acoperă REQ-1j, REQ-1l
- [ ] `frontend/src/__tests__/landing-sections.test.tsx` — acoperă REQ-1a
- [ ] `frontend/src/__tests__/EmailCapture.test.tsx` — acoperă REQ-1i
- [ ] `frontend/src/__tests__/reducedMotion.test.tsx` — acoperă REQ-1h
- [ ] `frontend/src/__tests__/responsive.test.tsx` — acoperă REQ-1g
- [ ] `npm install --save-dev vitest @testing-library/react @testing-library/user-event jsdom` în Wave 0

---

## Sources

### Primary (HIGH confidence)
- `frontend/package.json` — versiuni reale ale dependințelor instalate (citit direct)
- `frontend/src/index.css` — structura existentă Tailwind v4 + OKLCH tokens (citit direct)
- `frontend/components.json` — shadcn config: base-nova, neutral, cssVariables (citit direct)
- `frontend/src/App.tsx` — structura actuală a aplicației (citit direct)
- [shadcn/ui Tailwind v4 Docs](https://ui.shadcn.com/docs/tailwind-v4) — breaking changes, CSS variable format
- [Base UI Accordion API](https://base-ui.com/react/components/accordion) — component composition, props
- [Motion LazyMotion Docs](https://motion.dev/docs/react-lazy-motion) — bundle size reduction pattern
- [Motion Reduce Bundle Size](https://motion.dev/docs/react-reduce-bundle-size) — LazyMotion + domAnimation

### Secondary (MEDIUM confidence)
- [Not a Number — Dark Mode FOUC Fix](https://notanumber.in/blog/fixing-react-dark-mode-flickering) — blocking script pattern, verificat cu Tailwind dark mode docs
- [vite-plugin-pwa Docs](https://vite-pwa-org.netlify.app/guide/service-worker-precache) — workbox config
- [Frontend Horse — The Linear Look](https://frontend.horse/articles/the-linear-look/) — SaaS design patterns
- [LogRocket — Linear Design](https://blog.logrocket.com/ux-design/linear-design/) — design patterns 2024-2025

### Tertiary (LOW confidence)
- [WebSearch: SVG stroke-dasharray animation] — tehnica e standard CSS, implementarea exactă a beamului structural e de creat de la zero

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — verificat din package.json real + npm registry
- Architecture patterns: HIGH — bazate pe codul existent + docs oficiale
- Dark mode FOUC: HIGH — pattern de blocare script verificat cu multiple surse + Tailwind docs
- Motion LazyMotion: HIGH — docs oficiale motion.dev
- Pitfalls: HIGH — derivate din codul existent + breaking changes documentate
- SVG beam animation: MEDIUM — tehnica stroke-dasharray e standard, implementarea exactă e nevalidată

**Research date:** 2026-04-11
**Valid until:** 2026-05-11 (stack stabil, dar motion și vite-plugin-pwa au release-uri frecvente)
