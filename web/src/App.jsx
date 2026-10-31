import { useCallback, useEffect, useState } from 'react'
import { Header, Footer } from './components/Chrome'
import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import { scanTarget } from './lib/api'

const useHash = () => {
  const [h, setH] = useState(() => location.hash)
  useEffect(() => {
    const on = () => setH(location.hash)
    window.addEventListener('hashchange', on)
    return () => window.removeEventListener('hashchange', on)
  }, [])
  return h
}

export default function App() {
  const hash = useHash()
  const [scan, setScan] = useState({ status: 'idle' })
  const onReport = scan.status === 'done'
  const route = hash === '#/report' ? 'report' : 'landing'

  const start = useCallback(async (input, rules) => {
    setScan({ status: 'loading', input, rules })
    location.hash = '#/report'
    window.scrollTo(0, 0)
    try {
      const report = await scanTarget(input, rules)
      setScan({ status: 'done', input, rules, report })
    } catch (error) {
      setScan({ status: 'error', input, rules, error })
    }
  }, [])

  // A direct visit to #/report with nothing scanned goes back to the start.
  useEffect(() => {
    if (route === 'report' && scan.status === 'idle') location.hash = ''
  }, [route, scan.status])
  useEffect(() => { if (route === 'landing') window.scrollTo(0, 0) }, [route])

  const home = () => { location.hash = ''; setScan((s) => (s.status === 'loading' ? s : { status: 'idle' })) }

  return (
    <>
      <Header mode={route} onHome={home} />
      {route === 'report' && scan.status !== 'idle' ? (
        <Dashboard scan={scan} onScan={start} setReport={(report) => setScan((s) => ({ ...s, report, status: 'done' }))} />
      ) : (
        <Landing onScan={start} />
      )}
      {(route === 'landing' || onReport) && <Footer />}
    </>
  )
}
