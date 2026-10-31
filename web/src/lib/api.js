const BASE = import.meta.env.VITE_API || 'http://127.0.0.1:8000'

export const isGithubUrl = (s) => /^(https?:\/\/)?(www\.)?github\.com\//i.test(s.trim())

async function call(path, init) {
  let res
  try {
    res = await fetch(BASE + path, init)
  } catch {
    const e = new Error('The CatchBlock backend is not running.')
    e.code = 'offline'
    throw e
  }
  let data = {}
  try {
    data = await res.json()
  } catch {
    /* empty body */
  }
  if (!res.ok) {
    const e = new Error(data.error || 'Request failed')
    e.code = data.code || 'error'
    throw e
  }
  return data
}

const post = (path, body) =>
  call(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })

/** Accepts a public GitHub URL or (for local use) a folder path. */
export const scanTarget = (input, rules) => {
  const v = input.trim()
  return post('/scan', isGithubUrl(v) ? { url: v, rules } : { path: v, rules })
}
export const applyFixes = (path, rules, ids) => post('/fix', { path, rules, ids })
export const undoFix = (id) => post('/undo', { id })
export const explainFinding = (f) => post('/explain', { finding: { category: f.category, status: f.status, title: f.title, why: f.why } })
export const getBadge = (score, verdict) => post('/badge', { score, verdict })
