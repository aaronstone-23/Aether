import { useEffect, useState } from 'react'
import { api } from './api'

/* ── Motion preference ── */
export function useReducedMotion() { const [reduced, setReduced] = useState(false); useEffect(() => { const q = matchMedia('(prefers-reduced-motion: reduce)'); const sync = () => setReduced(q.matches); sync(); q.addEventListener('change', sync); return () => q.removeEventListener('change', sync) }, []); return reduced }

/* ── Number interpolation ── */
export function useCountUp(target = 0, duration = 1400, easing = 'easeOutExpo') { const [value, setValue] = useState(0); const reduce = useReducedMotion(); useEffect(() => { const end = Number(target) || 0; if (reduce) { setValue(end); return } let raf; const start = performance.now(); const tick = now => { const p = Math.min((now - start) / duration, 1); const eased = easing === 'easeOutExpo' ? (p === 1 ? 1 : 1 - 2 ** (-10 * p)) : p; setValue(Math.round(end * eased)); if (p < 1) raf = requestAnimationFrame(tick) }; raf = requestAnimationFrame(tick); return () => cancelAnimationFrame(raf) }, [target, duration, easing, reduce]); return value }

/* ── Reachability state ── */
export function useBackendStatus() { const [status, setStatus] = useState('connecting'); useEffect(() => { let alive = true; const check = () => api.health().then(() => alive && setStatus('connected')).catch(() => alive && setStatus('offline')); check(); const timer = setInterval(check, 30000); return () => { alive = false; clearInterval(timer) } }, []); return status }
