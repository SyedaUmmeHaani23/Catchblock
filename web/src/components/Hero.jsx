import { useEffect, useRef } from 'react'
import { Ring, paintRing } from './Ring'
import { ScanForm } from './ScanForm'
import { clamp, easeOutCubic, lerp, pinProgress, range } from '../lib/math'
import { onFrame } from '../lib/scroll'

/**
 * The hero is one pinned scroll story:
 *   0.00-0.30  a scan beam sweeps down; the headline lifts away
 *   0.08-0.55  six repo files fly in from the sides and dock around the ring
 *   0.28-0.72  the health score climbs
 *   0.70-0.90  the fixes land: every card flips to green and the verdict stamps
 *   0.88-1.00  the stage zooms away into the next section
 * The files and numbers shown here are an illustration, not a real scan.
 */
const STAGE_VH = 440

const CARDS = [
  { name: 'README.md', bad: 'No setup section', good: 'Setup added', state: 'warn', d: [-30, -23, -4], m: [-21, -35, -4] },
  { name: 'LICENSE', bad: 'No licence file', good: 'MIT added', state: 'fail', d: [30, -25, 3], m: [21, -35, 3] },
  { name: '.env', bad: 'Secret committed', good: 'Ignored + rotate', state: 'fail', d: [-35, 3, 2], m: [-21, 33, 2] },
  { name: 'ci.yml', bad: 'No CI workflow', good: 'Workflow added', state: 'warn', d: [35, 5, -3], m: [21, 33, -3] },
  { name: 'tests/', bad: 'No tests found', good: '3 tests found', state: 'fail', d: [-26, 27, 3], m: [-21, 45, 3] },
  { name: 'CONTRIBUTING', bad: 'Missing', good: 'Added', state: 'warn', d: [26, 29, -2], m: [21, 45, -2] },
]
const LABEL = { fail: 'FAIL', warn: 'WARN', pass: 'PASS' }

export function Hero({ onScan }) {
  const root = useRef(null)
  const beam = useRef(null)
  const grid = useRef(null)
  const glow = useRef(null)
  const rain = useRef(null)
  const title = useRef(null)
  const stage = useRef(null)
  const center = useRef(null)
  const ring = useRef(null)
  const num = useRef(null)
  const stamp = useRef(null)
  const tag = useRef(null)
  const hud = useRef(null)
  const clock = useRef(null)
  const files = useRef(null)
  const cardRefs = useRef([])

  useEffect(() => {
    const c = rain.current
    const ctx = c.getContext('2d')
    const sync = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2)
      c.width = Math.round(c.clientWidth * dpr)
      c.height = Math.round(c.clientHeight * dpr)
    }
    sync()
    const ro = new ResizeObserver(sync)
    ro.observe(c)
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    let seed = 7
    const rand = () => ((seed = (seed * 16807) % 2147483647) / 2147483647)
    const GLYPHS = '01{}<>/=;#$'
    const cols = Array.from({ length: 46 }, () => ({ x: rand(), y: rand(), s: 0.05 + rand() * 0.12, g: GLYPHS[Math.floor(rand() * GLYPHS.length)], a: 0.08 + rand() * 0.22 }))
    const states = new Array(CARDS.length).fill('')
    let lastP = -1

    const off = onFrame((_t, dt) => {
      const el = root.current
      if (!el) return
      const { p, rect } = pinProgress(el)
      if (rect.bottom < 0) return

      // code rain, only while the hero is mostly on screen
      if (p < 0.9) {
        const w = c.clientWidth, h = c.clientHeight, dpr = c.width / Math.max(1, w)
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
        ctx.clearRect(0, 0, w, h)
        ctx.font = '14px "JetBrains Mono", monospace'
        ctx.fillStyle = '#5cf2b8'
        for (const k of cols) {
          if (!reduce) { k.y += k.s * dt; if (k.y > 1.05) { k.y = -0.05 } }
          ctx.globalAlpha = k.a * (1 - range(p, 0.5, 0.85))
          for (let i = 0; i < 6; i++) ctx.fillText(k.g, k.x * w, (k.y - i * 0.028) * h)
        }
        ctx.globalAlpha = 1
      }

      if (Math.abs(p - lastP) < 0.00005) return
      lastP = p
      const mobile = window.innerWidth < 700
      const exit = easeOutCubic(range(p, 0.88, 1))

      // scan beam
      const sweep = range(p, 0, 0.3)
      beam.current.style.transform = `translate3d(0, ${lerp(-10, 105, sweep)}vh, 0)`
      beam.current.style.opacity = String(sweep > 0 && sweep < 1 ? 1 : 0)
      grid.current.style.backgroundPosition = `0 ${p * 900}px`
      glow.current.style.opacity = String(0.5 + range(p, 0.2, 0.7) * 0.5)

      // headline + form lift away
      const out = easeOutCubic(range(p, 0.02, 0.26))
      title.current.style.opacity = String(1 - out)
      title.current.style.transform = `translate3d(0, ${-out * 14}vh, 0) scale(${1 - out * 0.06})`
      title.current.style.filter = out > 0.01 ? `blur(${out * 8}px)` : ''
      title.current.style.pointerEvents = out > 0.2 ? 'none' : ''

      // score ring
      const show = easeOutCubic(range(p, 0.16, 0.34))
      const climb = range(p, 0.28, 0.72)
      const v = lerp(12, 38, easeOutCubic(range(p, 0.28, 0.5))) + lerp(0, 49, range(p, 0.68, 0.86))
      paintRing(ring.current, num.current, climb > 0 || p > 0.68 ? Math.min(87, v) : 12)
      center.current.style.opacity = String(show * (1 - exit))
      center.current.style.transform = `translate3d(-50%, -50%, 0) scale(${lerp(0.7, 1, show) * (1 + exit * 1.4)})`
      tag.current.style.opacity = String(range(p, 0.36, 0.5) * (1 - range(p, 0.66, 0.74)))
      stamp.current.style.opacity = String(range(p, 0.82, 0.9) * (1 - exit))
      stamp.current.style.transform = `translate3d(-50%, 0, 0) scale(${lerp(1.5, 1, easeOutCubic(range(p, 0.82, 0.9)))}) rotate(-4deg)`

      // files fly in, then flip once fixed
      CARDS.forEach((cd, i) => {
        const el2 = cardRefs.current[i]
        if (!el2) return
        const k = easeOutCubic(range(p, 0.08 + i * 0.04, 0.45 + i * 0.04))
        const [x, y, r] = mobile ? cd.m : cd.d
        const dir = x < 0 ? -1 : 1
        const px = lerp(dir * 70, x, k) * (1 + exit * 0.9)
        const py = lerp(y + 18, y, k) * (1 + exit * 0.9)
        el2.style.transform = `translate3d(calc(-50% + ${px}vw), calc(-50% + ${py}vh), 0) rotate(${lerp(dir * 14, r, k)}deg)`
        el2.style.opacity = String(k * (1 - exit))
        const next = p > 0.7 + i * 0.03 ? 'pass' : cd.state
        if (states[i] !== next) {
          states[i] = next
          el2.dataset.state = next
          el2.querySelector('.fc-chip').textContent = LABEL[next]
          el2.querySelector('.fc-note').textContent = next === 'pass' ? cd.good : cd.bad
        }
      })

      // HUD
      hud.current.style.opacity = String(range(p, 0.03, 0.12) * (1 - range(p, 0.84, 0.92)))
      const secs = Math.floor(p * 14)
      clock.current.textContent = `SCAN T+ 00:00:${String(secs).padStart(2, '0')}`
      files.current.textContent = `files ${Math.round(range(p, 0.05, 0.6) * 214)}/214`
    })
    return () => { off(); ro.disconnect() }
  }, [])

  return (
    <section id="top" ref={root} className="hero" style={{ height: `${STAGE_VH}svh` }} aria-label="CatchBlock">
      <div className="hero-stick" ref={stage}>
        <div className="grid-floor" ref={grid} aria-hidden="true" />
        <div className="hero-glow" ref={glow} aria-hidden="true" />
        <canvas className="rain" ref={rain} aria-hidden="true" />
        <div className="beam" ref={beam} aria-hidden="true" />

        {CARDS.map((c, i) => (
          <div key={c.name} className="fcard" data-state={c.state} aria-hidden="true" style={{ opacity: 0 }}
            ref={(el) => { if (el) cardRefs.current[i] = el }}>
            <span className="fc-name">{c.name}</span>
            <span className="fc-chip">{LABEL[c.state]}</span>
            <span className="fc-note">{c.bad}</span>
          </div>
        ))}

        <div className="hero-center" ref={center} style={{ opacity: 0 }} aria-hidden="true">
          <Ring ringRef={ring} numRef={num} size={300} label="health score" initial={12} />
          <p className="hero-tag" ref={tag}>Illustration: a repo with gaps</p>
        </div>
        <div className="hero-stamp" ref={stamp} style={{ opacity: 0 }} aria-hidden="true">PATCHED · GREEN</div>

        <div className="hero-title" ref={title}>
          <p className="eyebrow">Repository health check</p>
          <h1>Catch issues<br />before they catch you.</h1>
          <p className="hero-sub">Paste a public GitHub repo. Get a health score, plain-English findings, a commit heartbeat and safe fixes. Read-only, nothing is executed.</p>
          <ScanForm id="hero-scan" onScan={onScan} />
          <p className="scroll-hint">Scroll to watch a scan <span aria-hidden="true">↓</span></p>
        </div>

        <div className="hud" ref={hud} aria-hidden="true" style={{ opacity: 0 }}>
          <div className="hud-brackets" />
          <p className="hud-tl" ref={clock}>SCAN T+ 00:00:00</p>
          <p className="hud-tr" ref={files}>files 0/214</p>
          <p className="hud-bl">read-only · no repo code executed</p>
          <p className="hud-br">Scroll <span className="bob">↓</span></p>
        </div>
      </div>
    </section>
  )
}
