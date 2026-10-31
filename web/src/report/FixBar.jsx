import { download } from '../lib/format'

export function FixBar({ report, remote, busy, undoId, notice, onApplyAll, onUndo }) {
  const fixable = report.findings.filter((f) => f.fix && f.status !== 'pass')
  if (!fixable.length && !undoId && !notice) return null
  return (
    <div className="fixbar" role="region" aria-label="Fixes">
      {notice && <p className="fixbar-note" role="status">{notice}</p>}
      {fixable.length > 0 && (remote ? (
        <>
          <span><b>{fixable.length}</b> fixes available · read-only repo</span>
          <button className="btn btn-primary" onClick={() => download(`${report.source.repo || 'catchblock'}-fixes.patch`, report.patch)}>Download patch</button>
          <button className="btn" onClick={() => navigator.clipboard?.writeText('git apply catchblock-fixes.patch')}>Copy git apply</button>
        </>
      ) : (
        <>
          <span><b>{fixable.length}</b> safe fixes ready</span>
          <button className="btn btn-primary" disabled={busy} onClick={onApplyAll}>{busy ? 'Applying…' : 'Fix all'}</button>
        </>
      ))}
      {undoId && !remote && <button className="btn" onClick={onUndo}>Undo</button>}
    </div>
  )
}
