import React, { useEffect, useMemo, useState } from 'react'
import { api } from '../lib/api'
import { Icon } from '../components/Icons'

const LOCAL_REPORTS_KEY = 'aether-map-local-reports'
const MAP_COLOR_KEY = 'aether-map-heat-color'
const DEFAULT_MAP_COLOR = '#0F766E'
const COLOR_PRESETS = [
  { name: 'Aether teal', value: '#0F766E' },
  { name: 'Ocean blue', value: '#2563EB' },
  { name: 'Saffron', value: '#D97706' },
  { name: 'Rose', value: '#DB2777' },
  { name: 'Violet', value: '#7C3AED' },
]

// Hex tiles make the state relationships easy to scan at every screen size.
// Tile placement is schematic; state counts are still attached to the right state.
const stateTiles = [
  { name: 'Ladakh', abbr: 'LA', column: 4, row: 0, isUnionTerritory: true },
  { name: 'Jammu and Kashmir', abbr: 'JK', column: 3, row: 1, isUnionTerritory: true },
  { name: 'Himachal Pradesh', abbr: 'HP', column: 4, row: 1 },
  { name: 'Uttarakhand', abbr: 'UK', column: 5, row: 1 },
  { name: 'Arunachal Pradesh', abbr: 'AR', column: 9, row: 1 },
  { name: 'Punjab', abbr: 'PB', column: 2, row: 2 },
  { name: 'Chandigarh', abbr: 'CH', column: 3, row: 2, isUnionTerritory: true },
  { name: 'Haryana', abbr: 'HR', column: 4, row: 2 },
  { name: 'Uttar Pradesh', abbr: 'UP', column: 5, row: 2 },
  { name: 'Bihar', abbr: 'BR', column: 6, row: 2 },
  { name: 'Sikkim', abbr: 'SK', column: 7, row: 2 },
  { name: 'Assam', abbr: 'AS', column: 8, row: 2 },
  { name: 'Nagaland', abbr: 'NL', column: 9, row: 2 },
  { name: 'Rajasthan', abbr: 'RJ', column: 1, row: 3 },
  { name: 'Delhi', abbr: 'DL', column: 3, row: 3, isUnionTerritory: true },
  { name: 'Jharkhand', abbr: 'JH', column: 6, row: 3 },
  { name: 'West Bengal', abbr: 'WB', column: 7, row: 3 },
  { name: 'Meghalaya', abbr: 'ML', column: 8, row: 3 },
  { name: 'Manipur', abbr: 'MN', column: 9, row: 3 },
  { name: 'Gujarat', abbr: 'GJ', column: 0, row: 4 },
  { name: 'Madhya Pradesh', abbr: 'MP', column: 3, row: 4 },
  { name: 'Chhattisgarh', abbr: 'CG', column: 5, row: 4 },
  { name: 'Tripura', abbr: 'TR', column: 8, row: 4 },
  { name: 'Mizoram', abbr: 'MZ', column: 9, row: 4 },
  {
    name: 'Dadra and Nagar Haveli and Daman and Diu',
    abbr: 'DD',
    column: 0,
    row: 5,
    isUnionTerritory: true,
  },
  { name: 'Maharashtra', abbr: 'MH', column: 2, row: 5 },
  { name: 'Telangana', abbr: 'TG', column: 4, row: 5 },
  { name: 'Odisha', abbr: 'OD', column: 7, row: 5 },
  { name: 'Goa', abbr: 'GA', column: 1, row: 6 },
  { name: 'Karnataka', abbr: 'KA', column: 2, row: 6 },
  { name: 'Andhra Pradesh', abbr: 'AP', column: 5, row: 6 },
  { name: 'Lakshadweep', abbr: 'LD', column: 1, row: 7, isUnionTerritory: true },
  { name: 'Kerala', abbr: 'KL', column: 2, row: 7 },
  { name: 'Tamil Nadu', abbr: 'TN', column: 4, row: 7 },
  { name: 'Puducherry', abbr: 'PY', column: 5, row: 7, isUnionTerritory: true },
  {
    name: 'Andaman and Nicobar Islands',
    abbr: 'AN',
    column: 9,
    row: 7,
    isUnionTerritory: true,
  },
]

const reportCategories = [
  ['upi_fraud', 'UPI fraud'],
  ['digital_arrest', 'Digital arrest'],
  ['fake_loan_app', 'Fake loan app'],
  ['kyc_fraud', 'KYC fraud'],
  ['phishing', 'Phishing'],
  ['other', 'Other'],
]

function readLocalReports() {
  try {
    const saved = JSON.parse(localStorage.getItem(LOCAL_REPORTS_KEY) || '[]')
    return Array.isArray(saved)
      ? saved.filter((item) => typeof item?.state === 'string')
      : []
  } catch {
    return []
  }
}

function getInitialMapColor() {
  try {
    const saved = localStorage.getItem(MAP_COLOR_KEY)
    return saved && /^#[0-9a-f]{6}$/i.test(saved) ? saved : DEFAULT_MAP_COLOR
  } catch {
    return DEFAULT_MAP_COLOR
  }
}

function canonicalStateName(name) {
  return name === 'Chattisgarh' ? 'Chhattisgarh' : name
}

function stateLevel(count, maximum) {
  if (!count || !maximum) return 0
  return Math.max(1, Math.ceil(Math.sqrt(count / maximum) * 4))
}

export default function ScamMap() {
  const [data, setData] = useState(null)
  const [localReports, setLocalReports] = useState(readLocalReports)
  const [mapColor, setMapColor] = useState(getInitialMapColor)
  const [busy, setBusy] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [selectedState, setSelectedState] = useState('')
  const [reportState, setReportState] = useState('')
  const [category, setCategory] = useState('upi_fraud')
  const [notice, setNotice] = useState(null)

  const refresh = async () => {
    setBusy(true)
    try {
      setData(await api.mapData())
      setError('')
    } catch {
      setError('Shared totals are unavailable. Reports submitted here can still be saved on this device.')
    } finally {
      setBusy(false)
    }
  }

  useEffect(() => {
    void refresh()
  }, [])

  const counts = useMemo(() => {
    const totals = new Map()
    for (const report of data?.live_reports || []) {
      const name = canonicalStateName(report.state)
      totals.set(name, (totals.get(name) || 0) + (Number(report.count) || 0))
    }
    for (const report of localReports) {
      const name = canonicalStateName(report.state)
      totals.set(name, (totals.get(name) || 0) + 1)
    }
    return totals
  }, [data, localReports])

  const rows = useMemo(
    () => [...counts.entries()]
      .map(([state, count]) => ({ state, count }))
      .sort((a, b) => b.count - a.count || a.state.localeCompare(b.state)),
    [counts],
  )
  const maximum = rows[0]?.count || 0
  const totalReports = rows.reduce((total, row) => total + row.count, 0)
  const selectedCount = counts.get(selectedState) || 0

  const chooseState = (name) => {
    setSelectedState(name)
    setReportState(name)
  }

  const changeMapColor = (color) => {
    setMapColor(color)
    try {
      localStorage.setItem(MAP_COLOR_KEY, color)
    } catch {
      // The current color still applies for this visit if storage is disabled.
    }
  }

  const storeLocally = (state, scamType) => {
    const next = [...localReports, { state, scam_type: scamType }]
    localStorage.setItem(LOCAL_REPORTS_KEY, JSON.stringify(next))
    setLocalReports(next)
  }

  const submit = async (event) => {
    event.preventDefault()
    setNotice(null)
    if (!reportState) return

    setSubmitting(true)
    try {
      const response = await api.submitReport(reportState, category)
      setNotice(response.storage === 'local'
        ? { kind: 'local', text: 'Saved on this Aether instance. This signal is not visible to other deployments.' }
        : { kind: 'success', text: 'Report shared. Thank you for adding a community signal.' })
      setSelectedState(reportState)
      setReportState('')
      await refresh()
    } catch (submitError) {
      if (!submitError.status || submitError.status === 503) {
        try {
          storeLocally(reportState, category)
          setNotice({
            kind: 'local',
            text: 'Saved on this device. The shared report service is unavailable, so this signal is not visible to other users.',
          })
          setSelectedState(reportState)
          setReportState('')
        } catch {
          setNotice({ kind: 'error', text: 'Could not save this report on this device. Please retry.' })
        }
      } else {
        setNotice({ kind: 'error', text: submitError.message })
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="screen map-screen">
      <div className="screen-heading map-heading">
        <p className="eyebrow">Community report desk</p>
        <h1>See the signals<br />across <em>India.</em></h1>
        <p className="intro">
          Explore scam reports by state and union territory. Add an anonymous regional signal to help build a clearer picture.
        </p>
      </div>

      <section className="map-stats" aria-label="Regional report summary">
        <div className="map-stat">
          <span className="label">Community reports</span>
          <strong>{totalReports.toLocaleString('en-IN')}</strong>
          <span className="muted">{data?.storage === 'local' ? 'This Aether instance plus this device' : 'Shared totals plus this device'}</span>
        </div>
        <div className="map-stat">
          <span className="label">Regions with reports</span>
          <strong>{rows.length.toLocaleString('en-IN')}</strong>
          <span className="muted">States and union territories</span>
        </div>
        <div className="map-stat map-stat-top">
          <span className="label">Most reported</span>
          <strong>{rows[0]?.state || 'Awaiting reports'}</strong>
          <span className="muted">{rows[0] ? `${rows[0].count} reports recorded` : 'No regional reports recorded yet'}</span>
        </div>
      </section>

      <section className="report-dashboard">
        <div className="map-panel panel">
          <div className="map-panel-heading">
            <div>
              <p className="eyebrow">State and union territory view</p>
              <h2>Reported scam signals</h2>
            </div>
            <button
              className="icon-button"
              type="button"
              onClick={refresh}
              disabled={busy}
              aria-label="Refresh regional report totals"
              title="Refresh report totals"
            >
              <Icon name="refresh" />
            </button>
          </div>

          <div className="map-tools">
            <div className="map-legend" aria-label="Report count color legend">
              <span className="legend-title">Report activity</span>
              {[0, 1, 2, 3, 4].map((level) => (
                <span className="legend-item" key={level}>
                  <i className={`legend-swatch level-${level}`} style={{ '--map-heat': mapColor }} />
                  <small>{level === 0 ? 'None' : ['Few', 'Some', 'More', 'Most'][level - 1]}</small>
                </span>
              ))}
            </div>
            <div className="map-color-picker">
              <label htmlFor="map-color-input">Map color</label>
              <input
                id="map-color-input"
                type="color"
                value={mapColor}
                onChange={(event) => changeMapColor(event.target.value)}
                aria-label="Choose the map's report color"
              />
              <div className="map-color-presets" aria-label="Color presets">
                {COLOR_PRESETS.map((preset) => (
                  <button
                    key={preset.value}
                    className={mapColor.toLowerCase() === preset.value.toLowerCase() ? 'active' : ''}
                    style={{ '--preset-color': preset.value }}
                    type="button"
                    onClick={() => changeMapColor(preset.value)}
                    aria-label={`Set map color to ${preset.name}`}
                    title={preset.name}
                  />
                ))}
              </div>
              <button className="map-reset" type="button" onClick={() => changeMapColor(DEFAULT_MAP_COLOR)}>
                Reset
              </button>
            </div>
          </div>

          {error && <p className="map-service-note" role="status">{error}</p>}
          {data?.storage === 'local' && !error && (
            <p className="map-service-note" role="status">
              Reports are saved on this Aether instance. They are not shared with other deployments.
            </p>
          )}

          <div className="state-map-wrap" aria-busy={busy}>
            <svg
              className="state-map"
              viewBox="0 0 840 610"
              role="group"
              aria-label="Schematic India state map. Select a tile to see report counts."
            >
              <text className="map-region-label" x="626" y="150">NORTH EAST</text>
              {stateTiles.map((tile) => {
                const count = counts.get(tile.name) || 0
                const level = stateLevel(count, maximum)
                const x = 35 + tile.column * 75
                const y = 22 + tile.row * 67
                const selected = selectedState === tile.name
                return (
                  <g
                    key={tile.name}
                    className="state-tile"
                    data-level={level}
                    style={{ '--map-heat': mapColor }}
                    transform={`translate(${x} ${y})`}
                    role="button"
                    tabIndex="0"
                    aria-label={`${tile.name}${tile.isUnionTerritory ? ', union territory' : ''}: ${count} reports`}
                    aria-pressed={selected}
                    onMouseEnter={() => setSelectedState(tile.name)}
                    onFocus={() => setSelectedState(tile.name)}
                    onClick={() => chooseState(tile.name)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter' || event.key === ' ') {
                        event.preventDefault()
                        chooseState(tile.name)
                      }
                    }}
                  >
                    <title>{`${tile.name}${tile.isUnionTerritory ? ' (UT)' : ''} — ${count} community reports`}</title>
                    <path
                      className="state-tile-shape"
                      d="M 12 0 H 60 L 72 31 L 60 62 H 12 L 0 31 Z"
                    />
                    <text className="state-tile-abbr" x="36" y="26">{tile.abbr}</text>
                    <text className="state-tile-count" x="36" y="44">{count ? count.toLocaleString('en-IN') : '—'}</text>
                    {selected && <path className="state-tile-selected" d="M 12 0 H 60 L 72 31 L 60 62 H 12 L 0 31 Z" />}
                  </g>
                )
              })}
            </svg>
          </div>

          <div className="map-detail-row">
            <div>
              <span className="label">Selected region</span>
              <strong>{selectedState || 'Choose a tile on the map'}</strong>
            </div>
            <div className="map-selected-count">
              <strong>{selectedState ? selectedCount.toLocaleString('en-IN') : '—'}</strong>
              <span>{selectedState ? 'community reports' : 'select a region to see its count'}</span>
            </div>
            {selectedState && (
              <button className="text-button" type="button" onClick={() => { setReportState(selectedState); document.getElementById('report-category')?.focus() }}>
                Report from here <span aria-hidden="true">→</span>
              </button>
            )}
          </div>
          <p className="map-footnote">
            Schematic tile map for readability. Report counts are voluntary and incomplete; they do not represent all incidents or personal risk.
          </p>
        </div>

        <aside className="report-side">
          <form className="panel report-form" onSubmit={submit}>
            <p className="eyebrow">Anonymous report</p>
            <h2>Add a regional signal.</h2>
            <p className="muted">Only a state or union territory and scam type are requested. Never include names, phone numbers, or message contents.</p>

            <label className="field-label" htmlFor="report-state">State or union territory</label>
            <select id="report-state" required value={reportState} onChange={(event) => chooseState(event.target.value)}>
              <option value="">Choose a region</option>
              {stateTiles.map((tile) => <option key={tile.name} value={tile.name}>{tile.name}{tile.isUnionTerritory ? ' (UT)' : ''}</option>)}
            </select>

            <label className="field-label" htmlFor="report-category">Scam type</label>
            <select id="report-category" value={category} onChange={(event) => setCategory(event.target.value)}>
              {reportCategories.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>

            {notice && (
              <p className={`report-notice ${notice.kind}`} role={notice.kind === 'error' ? 'alert' : 'status'}>
                {notice.text}
              </p>
            )}
            <button className="button primary" type="submit" disabled={submitting || !reportState}>
              {submitting ? 'Submitting…' : 'Submit report'} <Icon name="arrow" />
            </button>
            <p className="small-note">If the report service cannot save it, the report is kept only in this browser and clearly marked as local.</p>
            <p className="small-note map-official-link">For urgent cyber fraud, use <a href="https://cybercrime.gov.in" target="_blank" rel="noreferrer">India’s official cybercrime portal</a>.</p>
          </form>

          <section className="panel report-ranking" aria-labelledby="ranking-title">
            <div className="section-row">
              <div>
                <p className="eyebrow">Regional snapshot</p>
                <h2 id="ranking-title">Most reported</h2>
              </div>
              {busy && <span className="ranking-loading" aria-label="Refreshing">Updating</span>}
            </div>
            {rows.length ? (
              <ol>
                {rows.slice(0, 6).map((row, index) => (
                  <li key={row.state}>
                    <button type="button" className={selectedState === row.state ? 'selected' : ''} onClick={() => chooseState(row.state)}>
                      <span className="ranking-index">{String(index + 1).padStart(2, '0')}</span>
                      <span className="ranking-name">{row.state}<i><b style={{ width: `${Math.max(5, row.count / maximum * 100)}%`, backgroundColor: mapColor }} /></i></span>
                      <strong>{row.count.toLocaleString('en-IN')}</strong>
                    </button>
                  </li>
                ))}
              </ol>
            ) : (
              <p className="ranking-empty">No reports have been recorded yet. Regions stay unshaded until a report is available.</p>
            )}
          </section>
        </aside>
      </section>
    </main>
  )
}
