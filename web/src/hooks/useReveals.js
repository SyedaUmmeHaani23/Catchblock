import { useEffect, useRef } from 'react'

/** Adds .is-in to every [data-reveal] inside the ref'd element the first time it is seen. */
export function useReveals() {
  const ref = useRef(null)
  useEffect(() => {
    const root = ref.current
    if (!root) return
    const io = new IntersectionObserver(
      (entries) =>
        entries.forEach((e) => {
          if (!e.isIntersecting) return
          e.target.classList.add('is-in')
          io.unobserve(e.target)
        }),
      { rootMargin: '0px 0px -8% 0px' },
    )
    const watch = () => root.querySelectorAll('[data-reveal]:not(.is-in)').forEach((el) => io.observe(el))
    watch()
    const mo = new MutationObserver(watch)
    mo.observe(root, { childList: true, subtree: true })
    return () => {
      mo.disconnect()
      io.disconnect()
    }
  }, [])
  return ref
}
