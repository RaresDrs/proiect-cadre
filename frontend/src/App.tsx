import { Button } from "@/components/ui/button"

function App() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="border-b px-6 py-4">
        <h1 className="text-2xl font-bold text-primary">
          StructCalc
        </h1>
        <p className="text-sm text-muted-foreground">
          Calculator structural 2D — Stud. Pop Rares Darius
        </p>
      </header>
      <main className="container mx-auto px-6 py-12 text-center">
        <h2 className="text-4xl font-bold mb-4">
          Bun venit la StructCalc
        </h2>
        <p className="text-muted-foreground mb-8 max-w-md mx-auto">
          Aplicatie web de calcul structural 2D pentru grinzi si cadre.
          Stack: React 19 + FastAPI + anastruct.
        </p>
        <Button size="lg" onClick={() => alert('API: /health')}>
          Verifica conexiunea API
        </Button>
      </main>
    </div>
  )
}

export default App
