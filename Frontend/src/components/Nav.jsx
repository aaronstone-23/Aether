import React, { useEffect, useState } from 'react'
import { useTheme } from '../lib/contexts'
import { Icon, Mark } from './Icons'

const links = [['overview','Overview'],['check','Check a message'],['email','Email forensics'],['practice','Practice'],['bank','Bank watch'],['map','Scam reports'],['recovery','Recovery']]

/* ── Dynamic Island navigation ── */
export default function Nav({ page, go }) {
  const [open,setOpen]=useState(false)
  const {theme,setTheme}=useTheme()
  const nextTheme=theme==='light'?'dark':'light'
  const close=()=>setOpen(false)
  const shortcut=/Mac|iPhone|iPad/.test(navigator.platform)?'⌘ K':'Ctrl K'

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

  return <header className={`island ${open?'island-open':''}`} onMouseEnter={()=>setOpen(true)} onMouseLeave={close} onFocus={()=>setOpen(true)} onBlur={e=>{if(!e.currentTarget.contains(e.relatedTarget))close()}}>
    <div className="island-top"><button className="theme-icon" aria-label={`Switch to ${nextTheme} theme`} onClick={()=>setTheme(nextTheme)}><Icon name={theme==='light'?'sun':'moon'}/></button><button className="brand-mark" aria-label="Aether overview" onClick={()=>go('overview')}><Mark size={22}/></button><span className="key-hint">{shortcut}</span></div>
    <nav className="island-links" aria-label="Main navigation">{links.map(([id,label],i)=><button key={id} className={`nav-link ${page===id?'active':''}`} style={{'--item':i}} onClick={()=>{go(id);close()}}>{label}</button>)}<span className="nav-break"/><button className="nav-link theme-choice" onClick={()=>setTheme(nextTheme)}>Theme · {nextTheme}</button><button className="nav-help" onClick={()=>{go('recovery');close()}}>I need help now <Icon name="arrow"/></button></nav>
  </header>
}
