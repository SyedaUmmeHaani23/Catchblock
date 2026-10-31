import { useCallback, useEffect, useRef, useState } from 'react'
import { applyFixes, undoFix, scanTarget } from '../lib/api'
import { Loading, ErrorView } from '../report/Loading'
import { ScoreHero } from '../report/ScoreHero'
import { QuickWins } from '../report/QuickWins'
import { Findings, Drawer } from '../report/Findings'
import { CommitHeartbeat } from '../report/CommitHeartbeat'
import { Track } from '../report/Track'
import { ReleaseReady } from '../report/ReleaseReady'
import { FixBar } from '../report/FixBar'
import { ScanForm } from '../components/ScanForm'

export default function Dashboard({ scan, setReport, onScan }) {
  const [open, setOpen] = useState(null)
  const [busy, setBusy] = useState(false)
  const [undoId, setUndoId] = useState(null)
  const [notice, setNotice] = useState('')
  const timer = useRef(0)
  const { status, report, error, input, rules } = scan
  const remote = report?.source?.type === 'github'

  const say = useCallback((m) => {
    setNotice(m)
    clearTimeout(timer.current)
    timer.current = setTimeout(() => setNotice(''), 6000)
  }, [])
  useEffect(() => () => clearTimeout(timer.current), [])

  const apply = async (ids) => {
    setBusy(true)
    try {
      const r = await applyFixes(report.path, rules, ids)
      setReport(r.report)
      setUndoId(r.undo_id)
      setOpen(null)
      say(r.applied.length ? `Applied ${r.applied.length} fix${r.applied.length > 1 ? 'es' : ''} to your local copy.` : 'Nothing was changed: those files already exist.')
    } catch (e) { say(e.message) } finally { setBusy(false) }
  }
  const undo = async () => {
    setBusy(true)
    try {
      await undoFix(undoId)
      setUndoId(null)
      setReport(await scanTarget(report.path, rules))
      say('Undone. Your files are back as they were.')
    } catch (e) { say(e.message) } finally { setBusy(false) }
  }

  if (status === 'loading') return <main className="dash"><Loading target={input} remote={/github\.com/i.test(input)} /></main>
  if (status === 'error') return <main className="dash"><ErrorView error={error} onRetry={() => { location.hash = '' }} /></main>
  if (!report) return null

  return (
    <main className="dash">
      <ScoreHero report={report} />
      <QuickWins report={report} />
      <Findings findings={report.findings} onOpen={setOpen} />
      <CommitHeartbeat report={report} />
      <Track report={report} />
      <ReleaseReady report={report} onOpen={setOpen} />
      <section className="sec cta">
        <div className="sec-head"><p className="eyebrow">Scan another</p></div>
        <div className="cta-form"><ScanForm id="again" compact onScan={onScan} /></div>
      </section>
      <FixBar report={report} remote={remote} busy={busy} undoId={undoId} notice={notice} onApplyAll={() => apply(undefined)} onUndo={undo} />
      <Drawer finding={open} remote={remote} busy={busy} onClose={() => setOpen(null)} onApply={(f) => apply([f.id])} />
    </main>
  )
}
