import { useState } from 'react'
import { useReveals } from '../hooks/useReveals'

const COLOR = { green: '22C55E', amber: 'F59E0B', red: 'EF4444' }

export function QuickWins({ report }) {
  const ref = useReveals()
  const [copied, setCopied] = useState(false)
  const qw = report.quick_wins || { items: [], projected: report.score, auto_count: 0 }
  const items = qw.items
  const gain = qw.projected - report.score
  const badge = `![CatchBlock score](https://img.shields.io/badge/CatchBlock-${report.score}%2F100-${COLOR[report.verdict] || '22C55E'})`
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(badge)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch { /* clipboard blocked */ }
  }
  const heading = !items.length
    ? 'Nothing left to fix.'
    : gain > 0
      ? `${report.score} → ${qw.projected} with ${qw.auto_count} suggested fix${qw.auto_count === 1 ? '' : 'es'}.`
      : 'Do these first.'
  return (
    <section ref={ref} className="sec qw" id="quick-wins" aria-labelledby="qw-title">
      <div className="sec-head" data-reveal>
        <p className="eyebrow">Quick wins</p>
        <h2 id="qw-title" className="h2">{heading}</h2>
        {gain > 0 && <p className="lead">Biggest points first. The projected score assumes every suggested fix is applied. It is an estimate, and a leaked secret always keeps the verdict red.</p>}
      </div>
      {items.length > 0 && (
        <ul className="qw-list">
          {items.map((i, k) => (
            <li key={i.id} data-reveal style={{ transitionDelay: `${k * 60}ms` }}>
              <span className="qw-gain">+{i.gain}</span>
              <span className="qw-title">{i.title}</span>
              <span className={`sev sev-${i.severity}`}>{i.severity}</span>
              <span className={`pill ${i.auto ? 'qw-auto' : ''}`}>{i.auto ? 'auto-fix' : 'by hand'}</span>
            </li>
          ))}
        </ul>
      )}
      <div className="qw-badge" data-reveal>
        <code>{badge}</code>
        <button className="btn btn-sm" onClick={copy}>{copied ? 'Copied ✓' : 'Copy README badge'}</button>
      </div>
      <p className="fine">The badge is a snapshot of today’s score. Update it after you fix things.</p>
    </section>
  )
}
