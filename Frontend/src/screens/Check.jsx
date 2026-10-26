import React, { useState } from 'react'
import { api } from '../lib/api'
import CaseResult from '../components/CaseResult'
import { Icon } from '../components/Icons'

export function CheckForm({
  onResult,
  onAsk,
  onPractice,
  onSaveCase,
  compact = false,
}) {
  const [mode, setMode] = useState('auto')
  const [text, setText] = useState('')
  const [file, setFile] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [saved, setSaved] = useState(false)

  const percentage = Math.min(100, (text.length / 20000) * 100)

  async function submit(event) {
    event.preventDefault()
    setError('')

    if (!text.trim() && !file) {
      setError('Paste a message or choose a .eml or .txt file.')
      return
    }

    if (text.length > 20000) {
      setError('This message is over the 20,000 character limit.')
      return
    }

    if (
      file &&
      (file.size > 1024 * 1024 || !/\.(eml|txt)$/i.test(file.name))
    ) {
      setError('Choose a .eml or .txt file up to 1 MB.')
      return
    }

    setBusy(true)

    try {
      const data = file
        ? await api.analyzeFile(file)
        : await api.analyzeMessage(text, mode)

      setResult(data)
      setSaved(false)
      onResult?.(data)

      if (!compact) {
        const resultElement = document.querySelector('.result-card')
        const top = resultElement
          ? resultElement.getBoundingClientRect().top + window.scrollY - 110
          : 0

        window.scrollTo({
          top,
          behavior: 'smooth',
        })
      }
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setBusy(false)
    }
  }

  function saveResult() {
    if (!result || !onSaveCase) return

    const didSave = onSaveCase(result)

    if (didSave) {
      setSaved(true)
      setError('')
    } else {
      setError('Could not save this case to the browser.')
    }
  }

  return (
    <div className="check-column">
      <form className="panel check-form" onSubmit={submit}>
        <div className="mode-tabs" role="tablist" aria-label="Message type">
          {[
            ['auto', 'Auto-detect'],
            ['text', 'Message'],
            ['email', 'Email'],
          ].map(([id, label]) => (
            <button
              type="button"
              role="tab"
              aria-selected={mode === id}
              className={mode === id ? 'selected' : ''}
              onClick={() => setMode(id)}
              key={id}
            >
              {label}
            </button>
          ))}
        </div>

        <label
          className="field-label"
          htmlFor={`message-${compact ? 'overview' : 'check'}`}
        >
          {mode === 'email'
            ? 'Message or email headers'
            : 'Paste a suspicious message'}
        </label>

        <textarea
          id={`message-${compact ? 'overview' : 'check'}`}
          placeholder="Paste an SMS, chat, email, URL, phone number, or UPI ID…"
          value={text}
          onChange={(event) => setText(event.target.value)}
          maxLength={22000}
          rows={compact ? 5 : 8}
        />

        <div className="char-meta">
          <span>{text.length.toLocaleString()} / 20,000</span>

          <span className="char-track">
            <i
              style={{
                width: `${percentage}%`,
                background:
                  percentage >= 95
                    ? 'var(--risk-danger)'
                    : percentage >= 80
                      ? 'var(--risk-caution)'
                      : 'var(--accent)',
              }}
            />
          </span>

          <label className="upload-link">
            <Icon name="upload" />
            Attach .eml or .txt
            <input
              type="file"
              accept=".eml,.txt"
              onChange={(event) =>
                setFile(event.target.files?.[0] || null)
              }
            />
          </label>
        </div>

        {file && (
          <div className="file-chip">
            {file.name}
            <button
              type="button"
              aria-label="Remove attached file"
              onClick={() => setFile(null)}
            >
              <Icon name="close" />
            </button>
          </div>
        )}

        {error && (
          <p className="inline-error" role="alert">
            {error}
          </p>
        )}

        <div className="submit-line">
          <span className="privacy-line">
            Message text is not retained. Saved Casebook records contain
            selected analysis details only.
          </span>

          <button className="button primary" disabled={busy}>
            {busy ? 'Analyzing…' : 'Analyze message'}
            {!busy && <Icon name="arrow" />}
          </button>
        </div>
      </form>

      {result && (
        <>
          <CaseResult
            data={result}
            onAsk={onAsk}
            onPractice={onPractice}
          />

          <div className="casebook-save-row">
            <button
              className="button secondary"
              type="button"
              onClick={saveResult}
              disabled={saved || !onSaveCase}
            >
              {saved ? 'Saved to Casebook' : 'Save to Casebook'}
            </button>

            <span aria-live="polite">
              {saved
                ? 'Saved in this browser. The original message was not saved.'
                : 'Optional: save the verdict, score, warning signals, and next steps.'}
            </span>
          </div>
        </>
      )}
    </div>
  )
}

export default function Check({
  onResult,
  onAsk,
  onPractice,
  onSaveCase,
  heistMode = false,
}) {
  return (
    <main className="screen">
      <div className="screen-heading">
        <p className="eyebrow">Message inspection</p>

        <h1>
          {heistMode ? (
            <>Read the signs before <em>you respond</em></>
          ) : (
            <>Put the message <em>under review</em></>
          )}
        </h1>

        <p className="intro">
          Paste the exact wording, including sender details or links.
          Aether checks for common warning signals and explains what to
          verify.
        </p>
      </div>

      <CheckForm
        onResult={onResult}
        onAsk={onAsk}
        onPractice={onPractice}
        onSaveCase={onSaveCase}
      />
    </main>
  )
}