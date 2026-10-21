const BASE = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '')

async function request(path, options = {}) {
  let response
  try { response = await fetch(`${BASE}${path}`, options) }
  catch { throw new Error('Aether could not reach its service. Check your connection and retry.') }
  let body = {}
  try { body = await response.json() } catch { /* An empty response becomes a safe message below. */ }
  if (!response.ok) {
    const error = new Error(body.message || body.detail || body.error || 'The request could not be completed. Please retry.')
    error.status = response.status
    throw error
  }
  return body
}

export const api = {
  health: () => request('/health'),
  analyzeMessage: (text, channel = 'auto') => request('/analyse', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text, channel }) }),
  analyzeFile: (file) => { const data = new FormData(); data.append('file', file); return request('/analyze/eml', { method: 'POST', body: data }) },
  nextScenario: (category, difficulty) => { const q = new URLSearchParams(); if (category && category !== 'any') q.set('category', category); if (difficulty) q.set('difficulty', difficulty); return request(`/simulation/next${q.size ? `?${q}` : ''}`) },
  scoreScenario: (scenario_id, answer) => request('/simulation/score', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ scenario_id, answer }) }),
  bankWatch: (bank) => request(`/bank-watch?bank=${encodeURIComponent(bank)}`),
  mapData: () => request('/map/data'),
  submitReport: (state, scam_type) => request('/map/report', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ state, scam_type }) }),
  recoverySteps: (kind) => request(`/panic/${kind}`),
  assistantReply: (message, history = [], context = null, session_id = 'anon') => request('/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message, history, context, session_id: session_id || 'anon' }) }),
}
