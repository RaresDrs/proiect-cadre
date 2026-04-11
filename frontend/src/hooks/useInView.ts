import { useEffect, useRef, useState } from 'react'

interface UseInViewOptions {
  threshold?: number
  once?: boolean
}

export function useInView({ threshold = 0.15, once = true }: UseInViewOptions = {}) {
  const ref = useRef<HTMLElement | null>(null)
  const [isInView, setIsInView] = useState(false)

  useEffect(() => {
    const element = ref.current
    if (!element) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true)
          if (once) observer.unobserve(element)
        }
      },
      { threshold }
    )

    observer.observe(element)
    return () => observer.disconnect()
  }, [threshold, once])

  return { ref, isInView }
}
