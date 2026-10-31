import { useEffect, useRef } from 'react'

/** Mouse drag-to-swipe for a scroll-snap row (touch already swipes natively). */
export function useDragScroll() {
  const ref = useRef(null)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    let down = false, startX = 0, startLeft = 0
    const pd = (e) => {
      if (e.pointerType !== 'mouse') return
      down = true; startX = e.clientX; startLeft = el.scrollLeft
      el.classList.add('is-dragging')
    }
    const pm = (e) => {
      if (down) el.scrollLeft = startLeft - (e.clientX - startX)
    }
    const pu = () => {
      if (!down) return
      down = false
      el.classList.remove('is-dragging')
    }
    el.addEventListener('pointerdown', pd)
    window.addEventListener('pointermove', pm)
    window.addEventListener('pointerup', pu)
    return () => {
      el.removeEventListener('pointerdown', pd)
      window.removeEventListener('pointermove', pm)
      window.removeEventListener('pointerup', pu)
    }
  }, [])
  return ref
}
