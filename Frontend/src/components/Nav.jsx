import React, { useEffect, useRef, useState } from 'react'
import { useTheme } from '../lib/contexts'
import { Icon, Mark } from './Icons'

const navGroups = [
  { label: 'Workspace', links: [['overview', 'Overview']] },
  { label: 'Analyze', links: [['check', 'Check a message'], ['email', 'Email forensics']] },
  { label: 'Learn', links: [['practice', 'Practice']] },
  { label: 'Monitor', links: [['bank', 'Bank watch'], ['map', 'Scam reports']] },
  { label: 'Respond', links: [['recovery', 'Recovery']] },
]
const navOrder = navGroups.flatMap(group => group.links.map(([id]) => id))

/* ── Dynamic Island navigation ── */
export default function Nav({ page, go }) {
  const [open,setOpen]=useState(false)
  const [pupil,setPupil]=useState({ x: 0, y: 0 })
  const eyeRef=useRef(null)
  const {theme,setTheme}=useTheme()
  const nextTheme=theme==='light'?'dark':'light'
  const close=()=>setOpen(false)
  const shortcut=/Mac|iPhone|iPad/.test(navigator.platform)?'⌘ K':'Ctrl K'
  const trackPointer=event=>{
    const eye=eyeRef.current
    if(!eye) return
    const rect=eye.getBoundingClientRect()
    const centerX=rect.left+rect.width/2
    const centerY=rect.top+rect.height/2
    const clamp=value=>Math.max(-1,Math.min(1,value))
    setPupil({
      x:Number((clamp((event.clientX-centerX)/(window.innerWidth*.38))*4.2).toFixed(1)),
      y:Number((clamp((event.clientY-centerY)/Math.max(72,window.innerHeight*.26))*3.1).toFixed(1)),
    })
  }
  const resetPupil=()=>setPupil({ x: 0, y: 0 })

  useEffect(()=>{
    const onKeyDown=event=>{
      if (!(event.metaKey||event.ctrlKey) || event.key.toLowerCase()!=='k') return
      const target=event.target
      if (target instanceof HTMLElement && (target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName))) return
      event.preventDefault()
      setOpen(true)
    }
    window.addEventListener('keydown',onKeyDown)
    return ()=>window.removeEventListener('keydown',onKeyDown)
  },[])

  return <header className={`island ${open?'island-open':''}`} onMouseEnter={()=>setOpen(true)} onPointerMove={trackPointer} onMouseLeave={()=>{close();resetPupil()}} onFocus={()=>setOpen(true)} onBlur={e=>{if(!e.currentTarget.contains(e.relatedTarget))close()}}>
    <div className="island-top">
      <span className="island-wordmark" aria-hidden="true">AETHER</span>
      <button className="brand-mark" aria-label="Aether overview" onClick={()=>go('overview')} ref={eyeRef}>
        <Mark className="island-eye" size={60} pupilX={pupil.x} pupilY={pupil.y}/>
      </button>
      <div className="island-tools">
        <button className="theme-icon" aria-label={`Switch to ${nextTheme} theme`} onClick={()=>setTheme(nextTheme)}><Icon name={theme==='light'?'sun':'moon'}/></button>
        <span className="key-hint">{shortcut}</span>
      </div>
    </div>
    <nav className="island-links" aria-label="Main navigation">
      {navGroups.map(group => (
        <div className="nav-group" key={group.label}>
          <span className="nav-group-label">{group.label}</span>
          <div className="nav-group-items">
            {group.links.map(([id, label]) => (
              <button
                key={id}
                className={`nav-link ${page === id ? 'active' : ''}`}
                style={{ '--item': navOrder.indexOf(id) }}
                aria-current={page === id ? 'page' : undefined}
                onClick={() => { go(id); close() }}
              >{label}</button>
            ))}
          </div>
        </div>
      ))}
      <button className="nav-help" onClick={() => { go('recovery'); close() }}>I need help now <Icon name="arrow"/></button>
    </nav>
  </header>
}
