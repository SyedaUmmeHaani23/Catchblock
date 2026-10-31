export const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v))
export const lerp = (a, b, t) => a + (b - a) * t
export const range = (v, a, b) => clamp((v - a) / (b - a))
export const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3)
export const easeInOut = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2)

/** Progress through a tall section whose child is position: sticky. 0 at the top, 1 when it unpins. */
export function pinProgress(el) {
  const rect = el.getBoundingClientRect()
  const vh = window.innerHeight
  const span = Math.max(1, rect.height - vh)
  return { p: clamp(-rect.top / span), rect, vh }
}

export const scoreColor = (v) => (v >= 80 ? 'var(--green)' : v >= 50 ? 'var(--amber)' : 'var(--red)')
export const verdictOf = (v) => (v >= 80 ? 'green' : v >= 50 ? 'amber' : 'red')
