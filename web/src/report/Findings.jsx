import { useEffect, useRef, useState } from 'react'
import { useReveals } from '../hooks/useReveals'
import { priority } from '../lib/format'
import { explainFinding } from '../lib/api'

const TABS = [['all', 'All'], ['fail', 'Fail'], ['warn', 'Warn'], ['pass', 'Pass']]
const ICON = { fail: '✗', warn: '!', pass: '✓' }

export function Findings({ findings, onOpen }) {
  const ref = useReveals()
  const [tab, setTab] = useState('all')
  const list = [...findings].filter((f) => tab === 'all' || f.status === tab)
    .sort((a, b) => ({ fail: 0, warn: 1, pass: 2 }[a.status] - { fail: 0, warn: 1, pass: 2 }[b.status]) || priority(b) - priority(a))
  const n = (s) => findings.filter((f) => s === 'all' || f.status === s).length
  return (
    <section ref={ref} className="sec" id="findings-list" aria-labelledby="fl-title">
      <div className="sec-head" data-reveal>
        <p className="eyebrow">Findings</p>
        <h2 id="fl-title" className="h2">{findings.length} checks, in plain English.</h2>
      </div>
      <div className="tabs" role="tablist" data-reveal>
        {TABS.map(([k, l]) => (
          <button key={k} role="tab" aria-selected={tab === k} className={tab === k ? 'is-on' : ''} onClick={() => setTab(k)}>{l} <span>{n(k)}</span></button>
        ))}
      </div>
      <ul className="flist" key={tab}>
        {list.map((f, i) => (
          <li key={f.id} data-reveal data-from={i % 2 ? 'right' : 'left'} style={{ transitionDelay: `${Math.min(i, 6) * 50}ms` }}>
            <button className={`frow st-${f.status}`} onClick={() => onOpen(f)}>
              <span className="frow-ic" aria-hidden="true">{ICON[f.status]}</span>
              <span className="frow-main"><b>{f.title}</b><em>{f.category} · {f.severity}</em></span>
              {f.fix && <span className="frow-fix">Fix available</span>}
              <span className="frow-go" aria-hidden="true">→</span>
            </button>
          </li>
        ))}
        {list.length === 0 && <li className="fine">Nothing here.</li>}
      </ul>
    </section>
  )
}

function DiffView({ text }) {
  return (
    <pre className="diff" aria-label="Fix preview">
      {text.split('\n').map((l, i) => (
        <span key={i} className={l.startsWith('+') && !l.startsWith('+++') ? 'd-add' : l.startsWith('-') && !l.startsWith('---') ? 'd-del' : l.startsWith('@@') || l.startsWith('diff') ? 'd-hunk' : 'd-ctx'}>{l}{'\n'}</span>
      ))}
    </pre>
  )
}

export function Drawer({ finding, remote, busy, onClose, onApply }) {
  const closeRef = useRef(null)
  const [copied, setCopied] = useState(false)
  const [ex, setEx] = useState(null)
  useEffect(() => {
    if (!finding) return
    closeRef.current?.focus()
    const on = (e) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', on)
    return () => window.removeEventListener('keydown', on)
  }, [finding, onClose])
  useEffect(() => { setCopied(false); setEx(null) }, [finding])
  const f = finding
  const copy = async () => {
    try { await navigator.clipboard.writeText(f.fix.diff); setCopied(true) } catch { /* clipboard blocked */ }
  }
  const explain = async () => {
    setEx('loading')
    try { setEx(await explainFinding(f)) } catch { setEx({ available: false }) }
  }
  return (
    <>
      <div className={`scrim ${f ? 'is-on' : ''}`} onClick={onClose} aria-hidden="true" />
      <aside className={`drawer ${f ? 'is-on' : ''}`} role="dialog" aria-modal="true" aria-label="Finding details" inert={!f}>
        {f && (
          <>
            <button ref={closeRef} className="drawer-x" onClick={onClose} aria-label="Close">✕</button>
            <p className="eyebrow">{f.category}</p>
            <h3 className="drawer-title">{f.title}</h3>
            <p className="drawer-chips"><span className={`sev sev-${f.severity}`}>{f.severity}</span><span className={`pill st-${f.status}`}>{f.status}</span><span className="pill">weight {f.weight}</span></p>
            <h4>Why it matters</h4>
            <p>{f.why}</p>
            {f.plain && (
              <div className="plain">
                <h4>In plain English</h4>
                <p>{f.plain.mean}</p>
                <p><b>First step:</b> {f.plain.step}</p>
              </div>
            )}
            <div className="explain">
              {ex === null && <button className="btn btn-sm" onClick={explain}>Reword it with a local model</button>}
              {ex === 'loading' && <p className="fine">Asking the local model…</p>}
              {ex && ex !== 'loading' && ex.available && (
                <>
                  <p className="explain-text">{ex.text}</p>
                  <p className="fine">Reworded by {ex.model}, running on your computer. The score does not depend on it.</p>
                </>
              )}
              {ex && ex !== 'loading' && !ex.available && (
                <>
                  <p className="fine">No local model found, so the plain-English summary above is all you get here. For a rewording by a model on your own computer, install Ollama and run <code>ollama pull gemma3:4b</code>. The scan works without it.</p>
                  <button className="btn btn-sm" onClick={explain}>Try again</button>
                </>
              )}
            </div>
            {f.fix ? (
              <>
                <h4>Fix preview <small>{f.fix.path}</small></h4>
                {f.fix.diff ? <DiffView text={f.fix.diff} /> : <p className="fine">Already applied or nothing to add.</p>}
                <div className="drawer-actions">
                  {remote ? <button className="btn" onClick={copy}>{copied ? 'Copied ✓' : 'Copy diff'}</button>
                    : <button className="btn btn-primary" disabled={busy} onClick={() => onApply(f)}>{busy ? 'Applying…' : 'Apply this fix'}</button>}
                </div>
                <p className="fine">{remote ? 'This is a read-only scan of a GitHub repo. Apply the diff yourself, or download the full patch.' : 'Never overwrites an existing file. You can undo it right after.'}</p>
              </>
            ) : <p className="fine">No automatic fix for this one. It needs a human decision.</p>}
          </>
        )}
      </aside>
    </>
  )
}
