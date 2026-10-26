import React, { useMemo, useState } from 'react'
import '../casebook.css'
import { downloadCasebook } from '../lib/casebook'

const STATUS_LABELS = {
  reviewing: 'Reviewing',
  reported: 'Reported',
  resolved: 'Resolved',
}

function riskLabel(score) {
  if (score < 34) return 'Lower'
  if (score < 67) return 'Elevated'
  return 'High'
}

function formatDate(value) {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return 'Date unavailable'
  }

  return date.toLocaleString()
}

export default function Casebook({
  cases = [],
  onUpdateCase,
  onDeleteCase,
  onClearCases,
  storageError = '',
  heistMode = false,
}) {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [riskFilter, setRiskFilter] = useState('all')
  const [selectedId, setSelectedId] = useState(null)

  const visibleCases = useMemo(() => {
    const query = search.trim().toLowerCase()

    return [...cases]
      .filter((caseItem) => {
        const matchesStatus =
          statusFilter === 'all' ||
          caseItem.status === statusFilter

        const matchesRisk =
          riskFilter === 'all' ||
          (riskFilter === 'lower' && caseItem.riskScore < 34) ||
          (riskFilter === 'elevated' &&
            caseItem.riskScore >= 34 &&
            caseItem.riskScore < 67) ||
          (riskFilter === 'high' && caseItem.riskScore >= 67)

        const searchableText = [
          caseItem.title,
          caseItem.channel,
          caseItem.verdict,
          caseItem.note,
          ...caseItem.redFlags,
          ...caseItem.recommendedActions,
        ]
          .join(' ')
          .toLowerCase()

        return (
          matchesStatus &&
          matchesRisk &&
          (!query || searchableText.includes(query))
        )
      })
      .sort(
        (a, b) =>
          new Date(b.updatedAt).getTime() -
          new Date(a.updatedAt).getTime(),
      )
  }, [cases, search, statusFilter, riskFilter])

  const selectedCase =
    visibleCases.find((caseItem) => caseItem.id === selectedId) ||
    visibleCases[0] ||
    null

  function removeSelectedCase() {
    if (!selectedCase) return

    const confirmed = window.confirm(
      `Delete "${selectedCase.title}" from this browser?`,
    )

    if (!confirmed) return

    onDeleteCase(selectedCase.id)
    setSelectedId(null)
  }

  function removeAllCases() {
    const confirmed = window.confirm(
      'Delete every saved case from this browser? This cannot be undone.',
    )

    if (confirmed) {
      onClearCases()
      setSelectedId(null)
    }
  }

  return (
    <main className="screen casebook-screen">
      <div className="screen-heading">
        <p className="eyebrow">
          {heistMode ? 'Operation records' : 'Saved on this device'}
        </p>

        <h1>
          {heistMode ? (
            <>The <em>case files</em></>
          ) : (
            <>Your <em>Casebook</em></>
          )}
        </h1>

        <p className="intro">
          Revisit analyses you chose to save. These records stay in this
          browser unless you export a backup.
        </p>
      </div>

      {storageError && (
        <p className="casebook-error" role="alert">
          {storageError}
        </p>
      )}

      <section className="casebook-toolbar panel" aria-label="Casebook controls">
        <label className="casebook-search">
          <span className="sr-only">Search saved cases</span>
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search titles, warnings, notes…"
          />
        </label>

        <label className="casebook-filter">
          <span>Status</span>
          <select
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
          >
            <option value="all">All statuses</option>
            <option value="reviewing">Reviewing</option>
            <option value="reported">Reported</option>
            <option value="resolved">Resolved</option>
          </select>
        </label>

        <label className="casebook-filter">
          <span>Risk</span>
          <select
            value={riskFilter}
            onChange={(event) => setRiskFilter(event.target.value)}
          >
            <option value="all">All risk levels</option>
            <option value="lower">Lower · 0–33</option>
            <option value="elevated">Elevated · 34–66</option>
            <option value="high">High · 67–100</option>
          </select>
        </label>

        <button
          className="button secondary"
          type="button"
          disabled={cases.length === 0}
          onClick={() => downloadCasebook(cases)}
        >
          Export backup
        </button>

        <button
          className="casebook-clear"
          type="button"
          disabled={cases.length === 0}
          onClick={removeAllCases}
        >
          Clear all
        </button>
      </section>

      <div className="casebook-layout">
        <section className="casebook-list panel" aria-label="Saved cases">
          <div className="casebook-list-heading">
            <div>
              <p className="label">Cases</p>
              <p className="muted">
                {visibleCases.length} shown · {cases.length} saved
              </p>
            </div>
          </div>

          {cases.length === 0 ? (
            <div className="casebook-empty">
              <h2>No saved cases yet</h2>
              <p>
                After an analysis, choose <strong>Save to Casebook</strong>
                to keep its verdict, risk score, warning signals, and next
                steps in this browser.
              </p>
            </div>
          ) : visibleCases.length === 0 ? (
            <div className="casebook-empty">
              <h2>No matches</h2>
              <p>Try changing the search or filters.</p>
            </div>
          ) : (
            <div className="casebook-items">
              {visibleCases.map((caseItem) => (
                <button
                  className={`casebook-item ${
                    selectedCase?.id === caseItem.id ? 'selected' : ''
                  }`}
                  type="button"
                  key={caseItem.id}
                  onClick={() => setSelectedId(caseItem.id)}
                >
                  <span className="casebook-item-top">
                    <strong>{caseItem.title}</strong>
                    <span className={`casebook-score ${riskLabel(caseItem.riskScore).toLowerCase()}`}>
                      {caseItem.riskScore}
                    </span>
                  </span>

                  <span className="casebook-item-meta">
                    {caseItem.verdict} · {caseItem.channel}
                  </span>

                  <span className="casebook-item-bottom">
                    <span>{STATUS_LABELS[caseItem.status]}</span>
                    <span>{formatDate(caseItem.updatedAt)}</span>
                  </span>
                </button>
              ))}
            </div>
          )}
        </section>

        <section className="casebook-detail panel" aria-label="Case details">
          {!selectedCase ? (
            <div className="casebook-empty">
              <h2>Select a case</h2>
              <p>Choose a saved case to view and update its details.</p>
            </div>
          ) : (
            <>
              <div className="casebook-detail-heading">
                <div>
                  <p className="eyebrow">
                    {caseItemDateLabel(selectedCase.createdAt)}
                  </p>
                  <h2>{selectedCase.verdict}</h2>
                  <p className="muted">
                    Risk score {selectedCase.riskScore}/100 ·{' '}
                    {selectedCase.confidence} confidence ·{' '}
                    {selectedCase.channel}
                  </p>
                </div>

                <button
                  className="casebook-delete"
                  type="button"
                  onClick={removeSelectedCase}
                >
                  Delete case
                </button>
              </div>

              <label className="casebook-field">
                <span>Case title</span>
                <input
                  type="text"
                  maxLength={100}
                  value={selectedCase.title}
                  onChange={(event) =>
                    onUpdateCase(selectedCase.id, {
                      title: event.target.value,
                    })
                  }
                />
              </label>

              <label className="casebook-field">
                <span>Status</span>
                <select
                  value={selectedCase.status}
                  onChange={(event) =>
                    onUpdateCase(selectedCase.id, {
                      status: event.target.value,
                    })
                  }
                >
                  <option value="reviewing">Reviewing</option>
                  <option value="reported">Reported</option>
                  <option value="resolved">Resolved</option>
                </select>
              </label>

              <div className="casebook-detail-grid">
                <section>
                  <p className="label">Warning signals</p>
                  {selectedCase.redFlags.length > 0 ? (
                    <ul className="casebook-bullet-list">
                      {selectedCase.redFlags.map((flag, index) => (
                        <li key={`${index}-${flag}`}>{flag}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="muted">
                      No warning signals were saved for this analysis.
                    </p>
                  )}
                </section>

                <section>
                  <p className="label">Recommended actions</p>
                  {selectedCase.recommendedActions.length > 0 ? (
                    <ol className="casebook-bullet-list">
                      {selectedCase.recommendedActions.map((action, index) => (
                        <li key={`${index}-${action}`}>{action}</li>
                      ))}
                    </ol>
                  ) : (
                    <p className="muted">
                      No recommended actions were saved for this analysis.
                    </p>
                  )}
                </section>
              </div>

              <label className="casebook-field">
                <span>Private note · stored in this browser</span>
                <textarea
                  rows={5}
                  maxLength={2000}
                  value={selectedCase.note}
                  onChange={(event) =>
                    onUpdateCase(selectedCase.id, {
                      note: event.target.value,
                    })
                  }
                  placeholder="Add a reminder or note for yourself…"
                />
                <small>{selectedCase.note.length}/2000 characters</small>
              </label>

              <p className="casebook-privacy">
                Saved records include the verdict, score, warning signals,
                recommended actions, title, status, and your note. They do
                not include the original message or uploaded file.
              </p>
            </>
          )}
        </section>
      </div>
    </main>
  )
}

function caseItemDateLabel(value) {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return 'Saved case'
  }

  return `Saved ${date.toLocaleDateString()}`
}