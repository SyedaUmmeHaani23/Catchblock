import { useEffect, useRef, useState } from 'react'
import { scrollToId } from '../lib/scroll'

export function Mark({ className = '' }) {
  return (
    <svg viewBox="0 0 32 32" className={className} aria-hidden="true">
      <path d="M16 2 28 7v9c0 7-5 12-12 14C9 28 4 23 4 16V7z" fill="none" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
      <path d="M8 17h4l2-5 4 10 2-5h4" fill="none" stroke="var(--green)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

const NAV = [['findings', 'Findings'], ['heartbeat', 'Heartbeat'], ['features', 'Features']]

export function Header({ mode, onHome }) {
  const [open, setOpen] = useState(false)
  const ref = useRef(null)
  useEffect(() => {
    const on = () => ref.current?.classList.toggle('is-stuck', window.scrollY > 24)
    on()
    window.addEventListener('scroll', on, { passive: true })
    return () => window.removeEventListener('scroll', on)
  }, [])
  const go = (id) => { setOpen(false); scrollToId(id) }
  return (
    <header className="header" ref={ref}>
      <div className="header-in">
        <button className="brand" onClick={onHome} aria-label="CatchBlock home"><Mark className="brand-mark" /><span>CATCHBLOCK</span></button>
        {mode === 'landing' ? (
          <>
            <nav className="nav" aria-label="Primary">
              {NAV.map(([id, l]) => <button key={id} onClick={() => go(id)}>{l}</button>)}
              <button className="btn btn-sm" onClick={() => go('scan')}>Scan a repo</button>
            </nav>
            <button className="menu-btn" aria-expanded={open} onClick={() => setOpen((v) => !v)}>{open ? 'Close' : 'Menu'}</button>
          </>
        ) : (
          <button className="btn btn-sm" onClick={onHome}>← New scan</button>
        )}
      </div>
      {mode === 'landing' && (
        <div className={`mobile-menu ${open ? 'is-open' : ''}`} inert={!open}>
          {NAV.map(([id, l], i) => <button key={id} onClick={() => go(id)}><span>0{i + 1}</span>{l}</button>)}
          <button onClick={() => go('scan')}><span>→</span>Scan a repo</button>
        </div>
      )}
    </header>
  )
}

export function Footer() {
  return (
    <footer className="footer">
      <span><Mark className="brand-mark" /> CATCHBLOCK · Catch issues before they catch you.</span>
      <span>Findings are signals for review, never proof.</span>
    </footer>
  )
}
