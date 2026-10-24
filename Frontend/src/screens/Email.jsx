import React from 'react'
import { CheckForm } from './Check'

/* ── Email forensics screen ── */
export default function Email({heistMode= false, props}) { return <main className="screen"><div className="screen-heading"><p className="eyebrow">Email forensics</p>
<h1>
  {heistMode
    ? <>Trace the route<br />behind every <em>message.</em></>
    : <>Read the route<br />behind the <em>message.</em></>}
</h1>
<p className="intro">Paste raw headers or attach an .eml file to inspect sender claims, authentication results, and the Received chain.</p></div><CheckForm {...props}/><section className="forensics-notes"><p className="label">Reading header evidence</p><div className="claim-evidence"><div><h3>Claims</h3><p>From · Reply-To · display name</p><p>Declared sending domain</p></div><div><h3>Evidence</h3><p>SPF / DKIM / DMARC results</p><p>Received servers · links · timestamps</p></div></div><p className="caveat">Header evidence can be incomplete or forged. Parsed authentication results are not independently verified unless the backend verifies them. Server location does not identify the sender. Nothing here proves intent.</p></section></main> }
