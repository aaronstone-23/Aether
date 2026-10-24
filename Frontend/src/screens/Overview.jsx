import React from 'react'
import { CheckForm } from './Check'
import SignalField from '../components/SignalField'
import { Icon } from '../components/Icons'
import QuickNav from '../components/QuickNav'

/* ── Product overview ── */
export default function Overview({
  status,
  history,
  onResult,
  go,
  onAsk,
  onPractice,
  heistMode = false,
}) { return <main className="screen overview"><section className="hero"><div className="hero-copy"><p className="eyebrow"><span className={`status-dot ${status}`}/>{status==='connected'?'Live threat monitor':status==='connecting'?'Connecting to threat monitor':'Threat monitor offline'} <span className="status-text">· {status}</span></p><h1>
  {heistMode
    ? <>Plan the next move<br />with more <em>control.</em></>
    : <>Make your next move<br />with more <em>signal.</em></>}
</h1><p className="intro">Read the warning signs in a suspicious message before you respond. Clear analysis, safer next steps.</p><QuickNav go={go}/><div className="hero-links"><a href="tel:1930" className="helpline"><span className="pulse-dot"/>Cyber fraud helpline <strong>1930</strong></a><button className="text-button" onClick={()=>go('recovery')}>Already sent money? Start recovery <Icon name="arrow"/></button></div></div><div className="signal-panel"><div className="signal-heading"><div><p className="label">Signal field</p><p className="muted">Recent checks · this session</p></div><span className="eyebrow">{history.length} CHECKS</span></div><SignalField data={history} onSelect={r=>r&&onResult(r)}/><div className="signal-axis"><span>Earlier</span><span>Now</span></div></div></section>
 <section className="metrics" aria-label="Aether capabilities"><div className="metric metric-count"><span className="label">Checks this session</span><strong>{history.length.toString().padStart(2,'0')}</strong><span className="muted">Stored in this browser session</span></div><div className="metric"><span className="label">Accepted input</span><div className="chip-row">{['SMS','Chat','Email','URL','Phone','UPI ID'].map(x=><span className="format-chip" key={x}>{x}</span>)}</div><span className="muted">One check flow for common message formats</span></div><div className="metric metric-layers"><span className="label">Detection layers</span><strong>04</strong><div className="layer-bar" role="img" aria-label="Four detection layers: text signals, links, phone numbers, email headers"><i/><i/><i/><i/></div><span className="muted">Text · links · phone · headers</span></div></section>
 <section className="overview-check"><div><p className="eyebrow">Start with the message</p><h2>Check before<br/><em>you answer.</em></h2><p className="muted">Paste a message below. No account required.</p></div><CheckForm compact onResult={onResult} onAsk={onAsk} onPractice={onPractice}/></section>
 <section className="path-section"><p className="label">A clear path through a difficult moment</p><div className="path-flow"><span>Detect</span><i/><span>Learn</span><i/><span>Recover</span></div><p className="privacy-line">Message text is not retained. Cases may retain verdict and risk indicators for service operations.</p><div className="trust-strip"><span>India cyber fraud helpline <b>1930</b></span><span>Official portal <b>cybercrime.gov.in</b></span><span>No account details requested</span></div></section>
 </main> }
