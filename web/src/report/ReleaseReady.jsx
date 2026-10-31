import { useReveals } from '../hooks/useReveals'
import { priority } from '../lib/format'

export function ReleaseReady({ report, onOpen }) {
  const ref = useReveals()
  const todo = report.findings.filter((f) => f.status !== 'pass').sort((a, b) => priority(b) - priority(a))
  const blockers = todo.filter((f) => f.status === 'fail')
  const ready = blockers.length === 0
  return (
    <section ref={ref} className="sec" id="ship" aria-labelledby="ship-title">
      <div className="sec-head" data-reveal>
        <p className="eyebrow">Before you ship</p>
        <h2 id="ship-title" className="h2">{ready ? 'Nothing is blocking a release.' : `${blockers.length} thing${blockers.length > 1 ? 's' : ''} to fix before you ship.`}</h2>
      </div>
      <div className="fh" data-reveal>
        <div className="fh-clock">
          {ready ? <div className="stamp-ready">READY TO SHIP</div>
            : <p className="mono-note">Fix the red items first. Warnings can wait, but they are worth a look.</p>}
        </div>
        <ol className="fh-list">
          {todo.length === 0 && <li className="fine">Every check passed.</li>}
          {todo.map((f) => (
            <li key={f.id}><button onClick={() => onOpen(f)}><span className={`sev sev-${f.severity}`}>{f.severity}</span>{f.title}</button></li>
          ))}
        </ol>
      </div>
    </section>
  )
}
