import { ScanForm } from './ScanForm'
import { useReveals } from '../hooks/useReveals'

const STEPS = [
  ['01', 'Paste', 'A public GitHub link. Nothing is installed or run.'],
  ['02', 'Scan', 'Shallow temporary clone, 17+ checks, then it’s deleted.'],
  ['03', 'Fix', 'Preview each diff. Apply to a local copy with undo, or download a patch.'],
]

export function FinalCta({ onScan }) {
  const ref = useReveals()
  return (
    <section id="scan" ref={ref} className="sec cta" aria-labelledby="cta-title">
      <div className="sec-head" data-reveal>
        <p className="eyebrow">Run it on your repo</p>
        <h2 id="cta-title" className="h2">Catch issues before they catch you.</h2>
      </div>
      <div className="steps">
        {STEPS.map(([n, h, p], i) => (
          <div key={n} className="step" data-reveal data-from={i === 1 ? 'up' : i ? 'right' : 'left'} style={{ transitionDelay: `${i * 100}ms` }}>
            <span>{n}</span><h3>{h}</h3><p>{p}</p>
          </div>
        ))}
      </div>
      <div className="cta-form" data-reveal><ScanForm id="cta-scan" onScan={onScan} /></div>
    </section>
  )
}
