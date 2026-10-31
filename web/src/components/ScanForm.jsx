import { useState } from 'react'

const EXAMPLES = [
  ['This project', 'https://github.com/SyedaUmmeHaani23/Catchblock'],
  ['pallets/click', 'https://github.com/pallets/click'],
]

export function ScanForm({ onScan, id, compact = false }) {
  const [value, setValue] = useState('')
  const [err, setErr] = useState('')

  const submit = (e) => {
    e.preventDefault()
    const v = value.trim()
    if (!v) return setErr('Paste a public GitHub repository link first.')
    setErr('')
    onScan(v, 'default')
  }

  return (
    <form className={`scanform ${compact ? 'is-compact' : ''}`} onSubmit={submit} noValidate id={id}>
      <div className="scanform-row">
        <label className="sr-only" htmlFor={`${id || 'sf'}-in`}>GitHub repository URL</label>
        <input id={`${id || 'sf'}-in`} className="scanform-in" value={value} onChange={(e) => { setValue(e.target.value); setErr('') }}
          placeholder="https://github.com/owner/repo" autoComplete="off" spellCheck="false" />
        <button className="btn btn-primary" type="submit">Scan repo <span aria-hidden="true">→</span></button>
      </div>
      <div className="scanform-meta">
        {!compact && (
          <span className="chips">
            Try:
            {EXAMPLES.map(([l, u]) => (
              <button key={u} type="button" className="chip" onClick={() => { setValue(u); setErr('') }}>{l}</button>
            ))}
          </span>
        )}
      </div>
      <p className="scanform-err" role="status">{err}</p>
    </form>
  )
}
