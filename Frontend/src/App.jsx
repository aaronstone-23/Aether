import React, { useState } from 'react'
import { ThemeProvider, useTheme } from './lib/contexts'
import { useBackendStatus } from './lib/hooks'
import Nav from './components/Nav'
import Assistant from './components/Assistant'
import Overview from './screens/Overview'
import Check from './screens/Check'
import Email from './screens/Email'
import Practice from './screens/Practice'
import Bank from './screens/Bank'
import ScamMap from './screens/Map'
import Recovery from './screens/Recovery'

/* ── Client-side screen router ── */
function Router({ page, go, status, history, setHistory, setActiveCase, onAsk, onPractice }) { const onResult=data=>{setActiveCase(data);setHistory(prev=>[{id:`${Date.now()}`,risk_score:Number(data.risk_score)||0,verdict:data.verdict||'Review',time:new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'}),case:data},...prev].slice(0,40))};const props={onResult,onAsk,onPractice};switch(page){case'check':return <Check {...props}/>;case'email':return <Email {...props}/>;case'practice':return <Practice/>;case'bank':return <Bank/>;case'map':return <ScamMap/>;case'recovery':return <Recovery/>;default:return <Overview status={status} history={history} onResult={onResult} go={go} onAsk={onAsk} onPractice={onPractice}/>}}

/* ── Application composition ── */
function Shell() { const [page,setPage]=useState('overview'),[history,setHistory]=useState([]),[activeCase,setActiveCase]=useState(null),[chatOpen,setChatOpen]=useState(false);const status=useBackendStatus();const {theme}=useTheme();const go=id=>{setPage(id);window.scrollTo({top:0,behavior:'smooth'})};const ask=()=>setChatOpen(true);return <><Nav page={page} go={go}/><div className={`app-shell theme-${theme}`}><Router page={page} go={go} status={status} history={history} setHistory={setHistory} setActiveCase={setActiveCase} onAsk={ask} onPractice={()=>go('practice')}/><footer className="site-footer"><button onClick={()=>go('overview')}><span className="footer-mark">A</span> Aether</button><span>Clear signals for safer decisions.</span><button onClick={()=>go('recovery')}>Recovery guidance <span aria-hidden="true">→</span></button></footer></div><Assistant activeCase={activeCase} open={chatOpen} setOpen={setChatOpen}/></>}
export default function App() { return <ThemeProvider><Shell/></ThemeProvider> }
