export type Lang = 'ro' | 'en'

export const translations: Record<Lang, Record<string, string>> = {
  ro: {
    // Nav
    'nav.logo': 'StructCalc',
    'nav.features': 'Functii',
    'nav.pricing': 'Preturi',
    'nav.faq': 'FAQ',
    'nav.cta': 'Incepe gratuit',
    // Hero
    'hero.headline': 'Calculul structural, reinventat',
    'hero.subheadline': 'Software profesional pentru analiza structurilor 2D — gratuit pentru studenti si ingineri.',
    'hero.cta.primary': 'Incearca gratuit',
    'hero.cta.secondary': 'Vezi cum functioneaza',
    // Features
    'features.heading': 'De ce StructCalc?',
    'features.1.title': 'Calcul precis',
    'features.1.body': 'Algoritmi verificati pentru bare, grinzi si cadre 2D.',
    'features.2.title': 'Export PDF',
    'features.2.body': 'Rapoarte profesionale gata de prezentat.',
    'features.3.title': 'Dark mode & PWA',
    'features.3.body': 'Functioneaza offline, pe orice dispozitiv.',
    // Pricing
    'pricing.heading': 'Preturi',
    'pricing.badge': 'Disponibil Q3 2026',
    'pricing.locked': 'Deblocat in curand',
    'pricing.free.name': 'Gratuit',
    'pricing.free.tagline': 'Pentru studenti si utilizatori solo',
    // Email capture
    'email.label': 'Fii primul care afla',
    'email.placeholder': 'adresa@email.com',
    'email.cta': 'Notifica-ma',
    'email.success': 'Esti pe lista! Te anuntam cand lansam.',
    'email.error': 'Introdu o adresa de email valida.',
    // FAQ
    'faq.heading': 'Intrebari frecvente',
    'faq.q1': 'Ce tipuri de structuri pot analiza?',
    'faq.a1': 'StructCalc suporta bare, grinzi simplu rezemate, cadre 2D si structuri cu noduri rigide.',
    'faq.q2': 'Este cu adevarat gratuit?',
    'faq.a2': 'Da. Tier-ul Free nu expira si nu necesita card.',
    'faq.q3': 'Functioneaza pe mobil?',
    'faq.a3': 'Da, e PWA — instalabil pe iOS si Android, functioneaza si offline.',
    'faq.q4': 'Cand vine tier-ul Pro?',
    'faq.a4': 'Planificam lansarea in Q3 2026. Inscrie-te mai sus pentru acces anticipat.',
    // CTA section
    'cta.heading': 'Gata sa calculezi?',
    'cta.body': 'Alatura-te inginerilor si studentilor care folosesc StructCalc.',
    'cta.button': 'Incepe gratuit',
    // Footer
    'footer.copyright': '© 2026 StructCalc. Toate drepturile rezervate.',
    // Accessibility
    'a11y.darkmode': 'Comuta modul intunecat',
    'a11y.skip': 'Sari la continut',
    // Beam page
    'beam.page.title': 'Calculator grinda 2D',
    'beam.page.subtitle': 'Definiti geometria, rezemerile si incarcaturile pentru a obtine diagramele M, T, N si deformata.',
    'nav.beam': 'Calculator',
  },
  en: {
    // Nav
    'nav.logo': 'StructCalc',
    'nav.features': 'Features',
    'nav.pricing': 'Pricing',
    'nav.faq': 'FAQ',
    'nav.cta': 'Get Started Free',
    // Hero
    'hero.headline': 'Structural analysis, reinvented',
    'hero.subheadline': 'Professional software for 2D structural analysis — free for students and engineers.',
    'hero.cta.primary': 'Try for free',
    'hero.cta.secondary': 'See how it works',
    // Features
    'features.heading': 'Why StructCalc?',
    'features.1.title': 'Precise calculation',
    'features.1.body': 'Verified algorithms for 2D bars, beams and frames.',
    'features.2.title': 'PDF Export',
    'features.2.body': 'Professional reports ready to present.',
    'features.3.title': 'Dark mode & PWA',
    'features.3.body': 'Works offline, on any device.',
    // Pricing
    'pricing.heading': 'Pricing',
    'pricing.badge': 'Available Q3 2026',
    'pricing.locked': 'Unlocking soon',
    'pricing.free.name': 'Free',
    'pricing.free.tagline': 'For students and solo users',
    // Email capture
    'email.label': 'Be the first to know',
    'email.placeholder': 'your@email.com',
    'email.cta': 'Notify me',
    'email.success': "You're on the list! We'll notify you at launch.",
    'email.error': 'Enter a valid email address.',
    // FAQ
    'faq.heading': 'Frequently asked questions',
    'faq.q1': 'What types of structures can I analyze?',
    'faq.a1': 'StructCalc supports bars, simply supported beams, 2D frames and rigid-joint structures.',
    'faq.q2': 'Is it really free?',
    'faq.a2': 'Yes. The Free tier never expires and requires no card.',
    'faq.q3': 'Does it work on mobile?',
    'faq.a3': "Yes, it's a PWA — installable on iOS and Android, works offline too.",
    'faq.q4': 'When is the Pro tier coming?',
    'faq.a4': "We're planning launch in Q3 2026. Sign up above for early access.",
    // CTA section
    'cta.heading': 'Ready to calculate?',
    'cta.body': 'Join the engineers and students using StructCalc.',
    'cta.button': 'Get Started Free',
    // Footer
    'footer.copyright': '© 2026 StructCalc. All rights reserved.',
    // Accessibility
    'a11y.darkmode': 'Toggle dark mode',
    'a11y.skip': 'Skip to content',
    // Beam page
    'beam.page.title': '2D Beam Calculator',
    'beam.page.subtitle': 'Define geometry, supports and loads to get M, V, N diagrams and deflection.',
    'nav.beam': 'Calculator',
  },
}
