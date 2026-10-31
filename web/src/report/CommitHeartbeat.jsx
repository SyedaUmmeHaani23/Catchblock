import { useEffect, useMemo, useRef } from 'react'

const W = 1200, H = 320, BASE = 230

export function CommitHeartbeat({ report }) {
  const ref = useRef(null)
  const { commits, event, history } = report
  const geo = useMemo(() => {
    if (!commits.length) return null
    const times = commits.map((c) => new Date(c.time).getTime())
    const s = event?.start ? new Date(event.start).getTime() : null
    const f = event?.freeze ? new Date(event.freeze).getTime() : null
    const lo = Math.min(...times, s ?? Infinity), hi = Math.max(...times, f ?? -Infinity)
    const span = Math.max(1, hi - lo)
    const x = (t) => 40 + ((t - lo) / span) * (W - 80)
    const maxIns = Math.max(1, ...commits.map((c) => c.ins))
    const spikes = commits.map((c, i) => ({ ...c, x: x(times[i]), h: 22 + (Math.log(c.ins + 1) / Math.log(maxIns + 1)) * 110 }))
      .sort((a, b) => a.x - b.x)
    let d = `M0 ${BASE}`, last = 0
    for (const sp of spikes) {
      const sx = Math.max(sp.x, last + 20)
      d += ` L${sx - 14} ${BASE} L${sx - 8} ${BASE - sp.h * 0.25} L${sx - 3} ${BASE + sp.h * 0.3} L${sx} ${BASE - sp.h} L${sx + 4} ${BASE + sp.h * 0.35} L${sx + 10} ${BASE}`
      last = sx
    }
    d += ` L${W} ${BASE}`
    return { d, spikes, s: s != null ? x(s) : null, f: f != null ? x(f) : null }
  }, [commits, event])

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { el.classList.add('is-in'); io.disconnect() } }, { threshold: 0.3 })
    io.observe(el)
    return () => io.disconnect()
  }, [geo])

  const flagged = commits.filter((c) => c.flags.length)
  const count = (k) => commits.filter((c) => c.flags.includes(k)).length
  const authors = new Set(commits.map((c) => c.author)).size

  return (
    <section className="sec" id="heartbeat" aria-labelledby="hb-title">
      <div className="sec-head">
        <p className="eyebrow">Commit heartbeat</p>
        <h2 id="hb-title" className="h2">{history.commits} commits by {history.authors} {history.authors === 1 ? 'author' : 'authors'}.</h2>
        <p className="lead">Each spike is a commit, taller when it adds more lines. Flags are signals for a human to review, never proof of anything.</p>
      </div>
      {!geo ? <p className="fine">No git history was found in this repository.</p> : (
        <div className="hb" ref={ref}>
          <svg viewBox={`0 0 ${W} ${H}`} className="beat-svg" role="img" aria-label={`Commit timeline with ${flagged.length} flagged commits`}>
            {geo.s != null && geo.f != null && <rect x={geo.s} y="30" width={Math.max(0, geo.f - geo.s)} height="250" className="beat-window" />}
            {geo.s != null && <text x={geo.s + 8} y="50" className="beat-lbl">EVENT START</text>}
            {geo.f != null && <text x={geo.f - 8} y="50" className="beat-lbl" textAnchor="end">FREEZE</text>}
            <line x1="0" x2={W} y1={BASE} y2={BASE} className="beat-base" />
            <path d={geo.d} pathLength={1} className="beat-line hb-draw" fill="none" strokeDasharray="1 1" />
            {geo.spikes.filter((s) => s.flags.length).map((s, i) => (
              <g key={i} transform={`translate(${s.x} ${BASE - s.h})`}>
                <circle r="6" className={`hb-dot hb-${s.flags[0]}`} />
                <title>{`${s.author}: ${s.msg}  (${s.ins} lines) · ${s.flags.join(', ')}`}</title>
              </g>
            ))}
          </svg>
          <ul className="hb-legend">
            {geo.s != null && <li><i className="hb-pre" />Before start <b>{count('pre-start')}</b></li>}
            <li><i className="hb-dump" />Giant commit <b>{count('dump')}</b></li>
            {geo.f != null && <li><i className="hb-post-freeze" />After freeze <b>{count('post-freeze')}</b></li>}
            <li><i className="hb-solo" />Authors <b>{authors}</b></li>
          </ul>
          {history.shallow && <p className="fine">Only the most recent commits were fetched (shallow clone), so the very first commit may be missing. Run CatchBlock on a full local clone to verify early history.</p>}
        </div>
      )}
    </section>
  )
}
