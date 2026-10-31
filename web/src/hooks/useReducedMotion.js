import { useEffect, useState } from 'react'
const Q = '(prefers-reduced-motion: reduce)'
export function useReducedMotion() {
  const [r, setR] = useState(() => window.matchMedia(Q).matches)
  useEffect(() => {
    const mq = window.matchMedia(Q)
    const on = () => setR(mq.matches)
    mq.addEventListener('change', on)
    return () => mq.removeEventListener('change', on)
  }, [])
  return r
}
