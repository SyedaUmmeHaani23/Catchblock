import { useReveals } from '../hooks/useReveals'

const FEATURES = [
  ['Deleted-secret detection', 'Finds keys that were committed and later removed. They are still in your git history, and anyone can read them.'],
  ['Quick wins, ranked', 'Every problem ranked by the points it is worth, with the score you would reach after the suggested fixes.'],
  ['Diff preview and undo', 'See exactly what a fix changes before it touches your local copy. Undo in one click, or download a patch.'],
  ['Commit heartbeat', 'Your history drawn as a pulse. Spot one giant commit that holds most of the code, or a project with a single author.'],
  ['Health badge', 'Download a self-contained SVG badge with your score for the README. No account, no hosted service.'],
  ['Score trend', 'Scan again after fixing and see how many points you gained or lost since last time.'],
  ['Pre-push guard', 'A git hook that stops a push when a secret or another blocker is about to leave your machine.'],
  ['CI gate', 'Run catchblock scan . --min-score 70 in CI. The build fails when the health of the repo drops.'],
  ['Plain-English explainer', 'Optional and private: a local Gemma model through Ollama explains any finding in simple words. Nothing leaves your computer.'],
]

export function Features() {
  const ref = useReveals()
  return (
    <section id="features" ref={ref} className="sec" aria-labelledby="feat-title">
      <div className="sec-head" data-reveal>
        <p className="eyebrow">What you get</p>
        <h2 id="feat-title" className="h2">The same avoidable problems ship in most repos.</h2>
        <p className="lead">A leaked key, no licence, no tests, no CI, a README nobody can follow. CatchBlock finds them in seconds, explains why they matter in plain English and fixes the ones it safely can.</p>
      </div>
      <div className="feat-grid">
        {FEATURES.map(([h, p], i) => (
          <article key={h} className="feat" data-reveal style={{ transitionDelay: `${(i % 3) * 80}ms` }}>
            <span className="feat-n">{String(i + 1).padStart(2, '0')}</span>
            <h3>{h}</h3>
            <p>{p}</p>
          </article>
        ))}
      </div>
      <p className="fine center">Findings are signals for review, never proof. The projected score is an estimate.</p>
    </section>
  )
}
