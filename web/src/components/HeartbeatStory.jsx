import { useEffect, useMemo, useRef } from 'react'
import { clamp, easeOutCubic, pinProgress, range } from '../lib/math'
import { onFrame } from '../lib/scroll'

const STAGE_VH = 320
const BASE = 230
const WIN = [200, 1010]
// Spike positions: ordinary commits plus one review signal.
const FLAGS = [
  { x: 640, h: 150, label: 'Giant dump commit', kind: 'dump' },
]
const spikes = (() => {
  const out = []
  for (let x = 224, i = 0; x < 1000; x += 38, i++) if (Math.abs(x - 640) > 20) out.push({ x, h: 26 + ((i * 37) % 34) })
  return [...out, ...FLAGS].sort((a, b) => a.x - b.x)
})()
const PATH = (() => {
  let d = `M0 ${BASE}`
  for (const s of spikes) {
    d += ` L${s.x - 18} ${BASE} L${s.x - 10} ${BASE - s.h * 0.25} L${s.x - 4} ${BASE + s.h * 0.3} L${s.x} ${BASE - s.h} L${s.x + 5} ${BASE + s.h * 0.35} L${s.x + 12} ${BASE}`
  }
  return d + ` L1200 ${BASE}`
})()

export function HeartbeatStory() {
  const root = useRef(null)
  const path = useRef(null)
  const dot = useRef(null)
  const flagEls = useRef([])
  const count = useRef(null)
  const total = useMemo(() => 47, [])

  useEffect(() => {
    let lastP = -1
    return onFrame(() => {
      const el = root.current, pa = path.current
      if (!el || !pa) return
      const { p, rect, vh } = pinProgress(el)
      if (rect.bottom < 0 || rect.top > vh) return
      if (Math.abs(p - lastP) < 0.00005) return
      lastP = p
      const k = easeOutCubic(range(p, 0.08, 0.9))
      pa.style.strokeDashoffset = String(1 - k)
      const pt = pa.getPointAtLength(pa.getTotalLength() * k)
      dot.current.setAttribute('transform', `translate(${pt.x} ${pt.y})`)
      FLAGS.forEach((f, i) => {
        const e = flagEls.current[i]
        if (e) e.classList.toggle('is-on', pt.x > f.x - 4)
      })
      count.current.textContent = String(Math.round(clamp(k) * total))
    })
  }, [total])

  return (
    <section id="heartbeat" ref={root} className="beat" style={{ height: `${STAGE_VH}svh` }} aria-labelledby="beat-title">
      <div className="beat-stick">
        <div className="beat-head">
          <div>
            <p className="eyebrow">Commit heartbeat</p>
            <h2 id="beat-title" className="h2">Your history, as a pulse.</h2>
          </div>
          <p className="mono-note">commits read <b ref={count}>0</b></p>
        </div>
        <svg viewBox="0 0 1200 340" className="beat-svg" role="img" aria-label="An illustrative commit timeline with one review signal: a giant commit that holds most of the code.">
          <line x1="0" x2="1200" y1={BASE} y2={BASE} className="beat-base" />
          <path d={PATH} className="beat-ghost" fill="none" />
          <path ref={path} d={PATH} pathLength={1} className="beat-line" fill="none" strokeDasharray="1 1" strokeDashoffset="1" />
          <g ref={dot} transform={`translate(0 ${BASE})`}><circle r="12" className="beat-halo" /><circle r="4.5" fill="#fff" /></g>
          {FLAGS.map((f, i) => (
            <g key={f.kind} className="beat-flag" ref={(el) => { if (el) flagEls.current[i] = el }} transform={`translate(${Math.min(f.x, 1090)} ${BASE - f.h - 26})`}>
              <rect x="-62" y="-20" width="124" height="24" rx="5" className={`flag-bg flag-${f.kind}`} />
              <text textAnchor="middle" y="-4" className="flag-t">{f.label}</text>
            </g>
          ))}
        </svg>
        <p className="beat-foot"><b>A pattern is a signal for review, never proof.</b> CatchBlock flags what a human should look at: one commit holding most of the code, or a project with a single author. Illustrative data.</p>
      </div>
    </section>
  )
}
