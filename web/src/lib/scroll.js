/**
 * One rAF loop for the whole page. Every scroll-driven component reads its own position and writes
 * styles directly, so scrolling never goes through React state. The loop only runs while something
 * is subscribed.
 */
const subs = new Set()
let raf = 0
let last = 0

function loop(time) {
  const dt = last ? Math.min(0.1, (time - last) / 1000) : 1 / 60
  last = time
  subs.forEach((fn) => fn(time, dt))
  raf = subs.size ? requestAnimationFrame(loop) : 0
  if (!raf) last = 0
}

export function onFrame(fn) {
  subs.add(fn)
  if (!raf) raf = requestAnimationFrame(loop)
  return () => {
    subs.delete(fn)
  }
}

/** Smoothly moves to a section by id (or the top). */
export function scrollToId(id) {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  const el = id === 'top' ? null : document.getElementById(id)
  const top = el ? el.getBoundingClientRect().top + window.scrollY : 0
  window.scrollTo({ top, behavior: reduce ? 'auto' : 'smooth' })
}
