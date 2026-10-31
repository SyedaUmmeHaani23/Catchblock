export const SEV = { critical: 4, high: 3, medium: 2, low: 1 }
export const priority = (f) => SEV[f.severity] * f.weight

export const pad = (n) => String(n).padStart(2, '0')

export function download(name, text) {
  const url = URL.createObjectURL(new Blob([text], { type: 'text/plain' }))
  const a = Object.assign(document.createElement('a'), { href: url, download: name })
  document.body.appendChild(a)
  a.click()
  a.remove()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
