import { useEffect, useRef } from 'react'
import { scoreColor } from '../lib/math'

/** Score ring. Imperative: parents set ring/number through the refs, so scroll never re-renders. */
export function Ring({ ringRef, numRef, size = 320, label = 'health score', initial = 0 }) {
  return (
    <div className="ring" style={{ width: size, height: size }} role="img" aria-label={`Health score ${initial} out of 100`}>
      <svg viewBox="0 0 120 120" aria-hidden="true">
        <circle cx="60" cy="60" r="52" className="ring-track" />
        <circle ref={ringRef} cx="60" cy="60" r="52" className="ring-bar" pathLength="100"
          strokeDasharray="100" strokeDashoffset={100 - initial} transform="rotate(-90 60 60)" />
        {Array.from({ length: 60 }, (_, i) => (
          <line key={i} x1="60" y1="3" x2="60" y2={i % 5 === 0 ? 8 : 5.5} className="ring-tick" transform={`rotate(${i * 6} 60 60)`} />
        ))}
      </svg>
      <div className="ring-center">
        <span ref={numRef} className="ring-num">{initial}</span>
        <span className="ring-label">{label}</span>
      </div>
    </div>
  )
}

export function paintRing(ring, num, v) {
  if (!ring || !num) return
  ring.style.strokeDashoffset = String(100 - v)
  ring.style.stroke = scoreColor(v)
  num.textContent = String(Math.round(v))
  num.style.color = scoreColor(v)
}

/** A ring that counts up to `value` when mounted or when value changes. */
export function AnimatedRing({ value, size, label }) {
  const ring = useRef(null)
  const num = useRef(null)
  const from = useRef(0)
  useEffect(() => {
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const a = from.current, b = value, t0 = performance.now(), dur = reduce ? 1 : 1500
    let raf
    const step = (t) => {
      const k = Math.min(1, (t - t0) / dur)
      paintRing(ring.current, num.current, a + (b - a) * (1 - Math.pow(1 - k, 3)))
      if (k < 1) raf = requestAnimationFrame(step)
      else from.current = b
    }
    raf = requestAnimationFrame(step)
    return () => cancelAnimationFrame(raf)
  }, [value])
  return <Ring ringRef={ring} numRef={num} size={size} label={label} />
}
