import { useEffect, useState } from 'react'
import { getBadge } from '../lib/api'
import { useReveals } from '../hooks/useReveals'

function Spark({ runs }) {
  const pts = runs.map((r, i) => `${4 + (runs.length < 2 ? 0 : (i * 152) / (runs.length - 1))},${36 - (r.score / 100) * 32}`).join(' ')
  return (
    <svg viewBox="0 0 160 40" className="spark" role="img" aria-label={`Scores over your last ${runs.length} scans: ${runs.map((r) => r.score).join(', ')}`}>
      <polyline points={pts} fill="none" stroke="var(--green)" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
      {runs.length > 0 && <circle cx={pts.split(' ').pop().split(',')[0]} cy={pts.split(' ').pop().split(',')[1]} r="3.5" fill="var(--green)" />}
    </svg>
  )
}

export function Track({ report }) {
  const ref = useReveals()
  const [svg, setSvg] = useState('')
  const [msg, setMsg] = useState('')
  useEffect(() => {
    let on = true
    getBadge(report.score, report.verdict).then((r) => on && setSvg(r.svg)).catch(() => on && setSvg(''))
    return () => { on = false }
  }, [report.score, report.verdict])

  const t = report.trend
  const copy = async (text, what) => {
    try { await navigator.clipboard.writeText(text); setMsg(`${what} copied.`) } catch { setMsg('Copy was blocked by the browser. Select the text and copy it yourself.') }
  }
  const download = () => {
    const url = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml' }))
    const a = Object.assign(document.createElement('a'), { href: url, download: 'catchblock-badge.svg' })
    a.click(); URL.revokeObjectURL(url)
  }

  return (
    <section ref={ref} className="sec" id="track" aria-labelledby="track-title">
      <div className="sec-head" data-reveal>
        <p className="eyebrow">Share and track</p>
        <h2 id="track-title" className="h2">Keep the score. Show it off.</h2>
      </div>
      <div className="trk-grid">
        <article className="trk" data-reveal>
          <h3>Trend</h3>
          {t && t.delta !== null ? (
            <>
              <p className={`trk-delta ${t.delta > 0 ? 'up' : t.delta < 0 ? 'down' : ''}`}>{t.delta > 0 ? '▲ +' : t.delta < 0 ? '▼ ' : '● '}{t.delta} points</p>
              <p className="fine">since your previous scan of this repo ({t.previous}/100).</p>
            </>
          ) : <p className="fine">This is the first scan of this repo. Fix a few things and scan again to see your progress.</p>}
          {t?.runs?.length > 1 && <Spark runs={t.runs} />}
          <p className="fine">History is kept on your computer only.</p>
        </article>
        <article className="trk" data-reveal style={{ transitionDelay: '80ms' }}>
          <h3>README badge</h3>
          <div className="badge-prev" dangerouslySetInnerHTML={{ __html: svg || '' }} aria-label="Badge preview" />
          <div className="trk-actions">
            <button className="btn btn-sm" onClick={download} disabled={!svg}>Download SVG</button>
            <button className="btn btn-sm" onClick={() => copy('![CatchBlock health](catchblock-badge.svg)', 'Markdown')}>Copy Markdown</button>
          </div>
          <p className="fine">Commit the file next to your README, then paste the Markdown.</p>
        </article>
        <article className="trk" data-reveal style={{ transitionDelay: '160ms' }}>
          <h3>Issue checklist</h3>
          <p className="fine">Every open finding as a to-do list you can paste into a GitHub issue or pull request.</p>
          <div className="trk-actions">
            <button className="btn btn-sm" onClick={() => copy(report.checklist || '', 'Checklist')} disabled={!report.checklist}>Copy checklist</button>
          </div>
        </article>
      </div>
      <p className="mono-note trk-msg" role="status">{msg}</p>
    </section>
  )
}
