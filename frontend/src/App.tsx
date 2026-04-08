import { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-primary mb-4">StructCalc</h1>
        <p className="text-muted-foreground mb-8">
          Calculator structural 2D — Stud. Pop Rares Darius
        </p>
        <button
          className="px-4 py-2 bg-primary text-primary-foreground rounded"
          onClick={() => setCount(count + 1)}
        >
          count is {count}
        </button>
      </div>
    </div>
  )
}

export default App
