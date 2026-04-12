import { Routes, Route } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import { RootLayout } from '@/components/layout/RootLayout'
import LandingPage from '@/pages/LandingPage'

const BeamPage = lazy(() => import('@/pages/BeamPage'))

export default function App() {
  return (
    <Routes>
      <Route element={<RootLayout />}>
        <Route path="/" element={<LandingPage />} />
        <Route
          path="/beam"
          element={
            <Suspense fallback={<div className="min-h-screen" />}>
              <BeamPage />
            </Suspense>
          }
        />
      </Route>
    </Routes>
  )
}
