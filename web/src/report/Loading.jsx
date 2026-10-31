import { useEffect, useState } from 'react'

const STEPS = [
  'Validating the repository link',
  'Cloning read-only into a temporary folder',
  'Checking README, licence, CI and tests',
  'Looking for leaked secrets',
  'Reading the commit history',
  'Looking for secrets deleted from history',
  'Auditing AI tools and credits',
  'Ranking the quick wins',
  'Deleting the temporary checkout',
]

export function Loading({ target, remote }) {
  const [i, setI] = useState(0)
  useEffect(() => {
    const id = setInterval(() => setI((v) => Math.min(v + 1, STEPS.length - 1)), remote ? 1700 : 600)
    return () => clearInterval(id)
  }, [remote])
  return (
    <div className="loading">
      <div className="term" role="status" aria-live="polite">
        <div className="term-bar"><i /><i /><i /><span>catchblock scan</span></div>
        <p className="term-cmd">$ catchblock scan {target}</p>
        {STEPS.slice(0, i + 1).map((s, k) => (
          <p key={s} className={k === i ? 'term-cur' : 'term-done'}>{k === i ? '›' : '✓'} {s}{k === i ? '…' : ''}</p>
        ))}
        <div className="term-prog"><i style={{ width: `${((i + 1) / STEPS.length) * 100}%` }} /></div>
      </div>
      <p className="fine center">{remote ? 'Large repositories can take up to a minute.' : 'Scanning your local folder.'}</p>
    </div>
  )
}

export function ErrorView({ error, onRetry }) {
  const offline = error.code === 'offline'
  return (
    <div className="loading">
      <div className="term term-err" role="alert">
        <div className="term-bar"><i /><i /><i /><span>scan failed</span></div>
        <p className="term-bad">✗ {error.message}</p>
        {offline && <>
          <p>Start the backend in a terminal, then try again:</p>
          <pre className="diff"><span className="d-ctx">cd cb{'\n'}python -m catchblock.cli serve</span></pre>
        </>}
        {!offline && error.code === 'not_found' && <p>Check the spelling, and that the repository is public.</p>}
        <button className="btn btn-primary" onClick={onRetry}>Try another repo</button>
      </div>
    </div>
  )
}
