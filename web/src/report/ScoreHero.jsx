import { useEffect, useRef } from 'react'
import { AnimatedRing } from '../components/Ring'
import { easeOutCubic, lerp, pinProgress, range } from '../lib/math'
import { onFrame } from '../lib/scroll'
import { priority } from '../lib/format'

const STAGE_VH = 260

export function ScoreHero({ report }) {
  const root = useRef(null)
  const ringWrap = useRef(null)
  const panel = useRef(null)
  const items = useRef([])
  const top = report.findings.filter((f) => f.status !== 'pass').sort((a, b) => priority(b) - priority(a)).slice(0, 3)
  const name = report.source?.name || 'local folder'
  const fails = report.findings.filter((f) => f.status === 'fail').length
  const warns = report.findings.filter((f) => f.status === 'warn').length
  const passes = report.findings.filter((f) => f.status === 'pass').length

  useEffect(() => {
    let lastP = -1
    return onFrame(() => {
      const el = root.current
      if (!el) return
      const { p, rect, vh } = pinProgress(el)
      if (rect.bottom < 0 || rect.top > vh) return
      if (Math.abs(p - lastP) < 0.00005) return
      lastP = p
      const mobile = window.innerWidth < 900
      const k = easeOutCubic(range(p, 0.05, 0.4))
      ringWrap.current.style.transform = mobile
        ? `translate3d(0, ${lerp(0, -9, k)}vh, 0) scale(${lerp(1, 0.62, k)})`
        : `translate3d(${lerp(0, -22, k)}vw, 0, 0) scale(${lerp(1, 0.86, k)})`
      panel.current.style.opacity = String(range(p, 0.05, 0.25))
      items.current.forEach((it, i) => {
        if (!it) return
        const t = easeOutCubic(range(p, 0.2 + i * 0.14, 0.45 + i * 0.14))
        it.style.opacity = String(t)
        it.style.transform = `translate3d(${lerp(mobile ? 0 : 90, 0, t)}px, ${lerp(mobile ? 50 : 0, 0, t)}px, 0)`
      })
    })
  }, [])

  return (
    <section ref={root} className="shero" style={{ height: `${STAGE_VH}svh` }} aria-labelledby="verdict-title">
      <div className="shero-stick">
        <div className="shero-head">
          <p className="eyebrow">Scan report</p>
          <h1 id="verdict-title" className="shero-name">{name}{report.source?.branch ? <small> · {report.source.branch}</small> : null}</h1>
        </div>
        <div className="shero-grid">
          <div className="shero-ring" ref={ringWrap}>
            <AnimatedRing value={report.score} size={340} label={`${report.verdict} verdict`} />
            <p className={`verdict v-${report.verdict}`}>{report.verdict.toUpperCase()}</p>
            <p className="shero-stats"><b className="t-red">{fails}</b> fail · <b className="t-amber">{warns}</b> warn · <b className="t-green">{passes}</b> pass</p>
          </div>
          <div className="shero-panel" ref={panel} style={{ opacity: 0 }}>
            <p className="eyebrow">{top.length ? 'Fix these first' : 'Nothing to fix'}</p>
            {top.length === 0 && <p className="lead">Every check passed. Nice work.</p>}
            {top.map((f, i) => (
              <button key={f.id} className="top-item" ref={(el) => { items.current[i] = el }} style={{ opacity: 0 }}
                onClick={() => document.getElementById('findings-list')?.scrollIntoView({ behavior: 'smooth' })}>
                <span className={`sev sev-${f.severity}`}>{f.severity}</span>
                <span><b>{f.title}</b><em>{f.why}</em></span>
              </button>
            ))}
            {report.verdict === 'red' && report.findings.some((f) => f.id.startsWith('secrets.') && f.status === 'fail') &&
              <p className="fine">A leaked secret always forces a red verdict.</p>}
          </div>
        </div>
        <p className="scroll-hint">Scroll <span aria-hidden="true">↓</span></p>
      </div>
    </section>
  )
}
