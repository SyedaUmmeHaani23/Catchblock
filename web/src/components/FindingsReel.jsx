import { useEffect, useRef } from 'react'
import { clamp, pinProgress, range } from '../lib/math'
import { onFrame } from '../lib/scroll'

const STAGE_VH = 340
const SAMPLE = [
  { sev: 'critical', cat: 'Security', title: '2 possible secrets in the repo', why: 'Anyone who can see the repo can use these keys. Rotate them and remove them from history.', diff: ['+ .env', '+ *.pem'] },
  { sev: 'high', cat: 'Licence', title: 'No LICENSE file', why: 'Without a licence, nobody can legally reuse your code. Most teams will not touch code they cannot legally reuse.', diff: ['+ MIT License', '+ Copyright (c) 2026 …'] },
  { sev: 'high', cat: 'Disclosure', title: 'AI tools not named in the README', why: 'CatchBlock found a CLAUDE.md and the openai package. Being open about AI tools builds trust. A signal to check, not proof.', diff: ['+ ## AI tools used', '+ - Claude (detected: CLAUDE.md)'] },
  { sev: 'medium', cat: 'CI', title: 'No CI workflow', why: 'CI runs your tests on every push so broken code is caught before anyone else sees it.', diff: ['+ .github/workflows/ci.yml'] },
  { sev: 'medium', cat: 'Git', title: 'One commit holds most of the code', why: 'A single giant commit hides how the project grew. Reviewers read this as a flag to look closer.', diff: [] },
  { sev: 'low', cat: 'Community', title: 'No CONTRIBUTING.md', why: 'Tell newcomers how to help, so your project is easy to join.', diff: ['+ # Contributing', '+ 1. Fork and branch'] },
]

export function FindingsReel() {
  const root = useRef(null)
  const track = useRef(null)
  const cards = useRef([])
  const bar = useRef(null)
  const count = useRef(null)

  useEffect(() => {
    let lastP = -1
    return onFrame(() => {
      const el = root.current, tr = track.current
      if (!el || !tr) return
      const { p, rect, vh } = pinProgress(el)
      if (rect.bottom < 0 || rect.top > vh) return
      if (Math.abs(p - lastP) < 0.00005) return
      lastP = p
      const vw = window.innerWidth
      const k = range(p, 0.04, 0.96)
      const travel = Math.max(0, tr.offsetLeft + tr.scrollWidth - vw * 0.94)
      tr.style.transform = `translate3d(${-k * travel}px, 0, 0)`
      let best = Infinity, near = 0
      cards.current.forEach((c, i) => {
        const r = c.getBoundingClientRect()
        const off = (r.left + r.width / 2 - vw * 0.62) / vw
        const a = clamp(Math.abs(off) * 1.6)
        c.style.opacity = String(1 - a * 0.55)
        c.style.transform = `scale(${1 - a * 0.06}) rotate(${off * 2}deg)`
        if (Math.abs(off) < best) { best = Math.abs(off); near = i }
      })
      bar.current.style.transform = `scaleX(${k})`
      count.current.textContent = `0${near + 1}`
    })
  }, [])

  return (
    <section id="findings" ref={root} className="reel" style={{ height: `${STAGE_VH}svh` }} aria-labelledby="findings-title">
      <div className="reel-stick">
        <div className="reel-copy">
          <p className="eyebrow">Findings</p>
          <h2 id="findings-title" className="h2">Every problem, in plain English.</h2>
          <p className="lead hide-sm">What was checked, why it matters, and a diff for the fix. Nothing is hidden behind a score.</p>
          <div className="reel-count hide-sm" aria-hidden="true">
            <span><b ref={count}>01</b> / 0{SAMPLE.length}</span>
            <span className="reel-bar"><i ref={bar} style={{ transform: 'scaleX(0)' }} /></span>
          </div>
          <p className="fine">Illustrative examples of what a scan reports.</p>
        </div>
        <ol className="reel-track" ref={track}>
          {SAMPLE.map((f, i) => (
            <li key={f.title} className="rcard" ref={(el) => { if (el) cards.current[i] = el }}>
              <div className="rcard-top"><span className={`sev sev-${f.sev}`}>{f.sev}</span><span className="rcard-cat">{f.cat}</span></div>
              <h3>{f.title}</h3>
              <p>{f.why}</p>
              <pre className="diff" aria-label="Suggested fix">{f.diff.length ? f.diff.map((l, j) => <span key={j} className="d-add">{l}{'\n'}</span>) : <span className="d-ctx">Review signal: no auto-fix{'\n'}</span>}</pre>
            </li>
          ))}
        </ol>
      </div>
    </section>
  )
}
