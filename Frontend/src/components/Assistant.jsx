import React, { useEffect, useRef, useState } from 'react'
import { api } from '../lib/api'
import { ChatIcon, Icon } from './Icons'

/* ── Persistent safety assistant ── */
function AssistantPanel({ activeCase, open, setOpen }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const bottom = useRef(null)

  useEffect(() => {
    const scrollArea = bottom.current?.parentElement
    if (scrollArea) scrollArea.scrollTop = scrollArea.scrollHeight
  }, [messages, busy])

  const send = async (value, retry = false) => {
    const message = (value ?? input).trim()
    if (!message || busy) return

    setInput('')
    setError('')
    const prior = retry ? messages.slice(0, -1) : messages
    if (!retry) setMessages([...prior, { role: 'user', content: message }])
    setBusy(true)

    try {
      const context = activeCase
        ? {
            verdict: activeCase.verdict,
            risk_score: activeCase.risk_score,
            red_flags: activeCase.red_flags,
          }
        : null
      const response = await api.assistantReply(
        message,
        prior.slice(-10).map(({ role, content }) => ({ role, content })),
        context,
      )
      const reply = typeof response?.reply === 'string' ? response.reply.trim() : ''
      if (!reply) throw new Error('The assistant returned an empty reply. Please retry.')
      setMessages([...prior, { role: 'user', content: message }, { role: 'assistant', content: reply }])
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setBusy(false)
    }
  }

  return <>
    <button className="assistant-anchor" aria-label={open ? 'Close Aether assistant' : 'Open Aether assistant'} onClick={() => setOpen(!open)}>
      <ChatIcon size={22}/>
    </button>
    {open && <section className="assistant-panel panel" aria-label="Aether safety assistant">
      <header>
        <div><p className="eyebrow">Aether assistant</p><p className="muted">Scam and account safety</p></div>
        <button className="icon-button" aria-label="Close assistant" onClick={() => setOpen(false)}><Icon name="close"/></button>
      </header>
      <div className="chat-messages" aria-live="polite">
        {messages.length === 0 && <div className="starter-chips">
          {['I shared an OTP', 'How do I verify a link?', 'Someone said they’re from my bank'].map((suggestion) =>
            <button key={suggestion} onClick={() => send(suggestion)}>{suggestion}</button>,
          )}
        </div>}
        {messages.map((message, index) =>
          <div key={index} className={`chat-bubble ${message.role}`}>{message.content}</div>,
        )}
        {busy && <div className="typing" aria-label="Assistant is responding"><i/><i/><i/></div>}
        {error && <div className="assistant-error" role="alert">
          {error}
          <button className="text-button" onClick={() => send(messages.at(-1)?.content, true)}>Retry</button>
        </div>}
        <div ref={bottom}/>
      </div>
      <form className="chat-input" onSubmit={(event) => { event.preventDefault(); send() }}>
        <label className="sr-only" htmlFor="assistant-input">Ask a scam safety question</label>
        <input id="assistant-input" value={input} onChange={(event) => setInput(event.target.value)} placeholder="Ask about a suspicious request…" maxLength={1000}/>
        <button className="button primary" disabled={busy || !input.trim()} aria-label="Send message"><Icon name="arrow"/></button>
      </form>
      <p className="chat-reminder">Never share OTP, PIN, or CVV.</p>
    </section>}
  </>
}

class AssistantErrorBoundary extends React.Component {
  state = { failed: false }

  static getDerivedStateFromError() {
    return { failed: true }
  }

  componentDidCatch(error) {
    console.error('Aether assistant render failed:', error)
  }

  render() {
    if (this.state.failed) {
      return <section className="assistant-panel panel" role="alert">
        <p>The assistant hit a display error. The rest of Aether is still available.</p>
        <button className="button secondary" onClick={() => this.setState({ failed: false })}>Reload assistant</button>
      </section>
    }
    return this.props.children
  }
}

export default function Assistant(props) {
  return <AssistantErrorBoundary><AssistantPanel {...props}/></AssistantErrorBoundary>
}
