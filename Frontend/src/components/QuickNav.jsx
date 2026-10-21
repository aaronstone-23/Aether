import React, { useMemo, useState } from 'react'
import { Icon } from './Icons'

const destinations = [
  { id: 'check', label: 'Check a message', detail: 'Inspect a suspicious text, link, phone number, or UPI ID.' },
  { id: 'email', label: 'Email forensics', detail: 'Review raw email headers and authentication signals.' },
  { id: 'practice', label: 'Practice', detail: 'Try a fictional scam recognition scenario.' },
  { id: 'bank', label: 'Bank watch', detail: 'Search curated incidents and published coverage.' },
  { id: 'map', label: 'Scam reports', detail: 'View or submit anonymous regional reports.' },
  { id: 'recovery', label: 'Recovery guidance', detail: 'Find immediate steps after a suspicious contact or payment.' },
]

export default function QuickNav({ go }) {
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const [activeIndex, setActiveIndex] = useState(0)
  const matches = useMemo(() => {
    const term = query.trim().toLocaleLowerCase()
    return destinations.filter((destination) =>
      !term || `${destination.label} ${destination.detail}`.toLocaleLowerCase().includes(term),
    )
  }, [query])

  const navigate = (destination) => {
    go(destination.id)
    setQuery('')
    setOpen(false)
    setActiveIndex(0)
  }

  const onKeyDown = (event) => {
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      setActiveIndex((index) => Math.min(index + 1, matches.length - 1))
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      setActiveIndex((index) => Math.max(index - 1, 0))
    } else if (event.key === 'Enter' && matches.length) {
      event.preventDefault()
      navigate(matches[Math.min(activeIndex, matches.length - 1)])
    } else if (event.key === 'Escape') {
      setQuery('')
      setOpen(false)
      setActiveIndex(0)
      event.currentTarget.blur()
    }
  }

  return <div className="quick-nav">
    <div className="quick-nav-meta"><span>QUICK NAVIGATION</span><span>FIND AETHER TOOLS</span></div>
    <div className="quick-nav-box">
      <div className="quick-nav-field">
        <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.8" cy="10.8" r="6.3"/><path d="m16 16 4.2 4.2"/></svg>
        <input
          type="search"
          aria-label="Find a page"
          aria-expanded={open}
          aria-controls="quick-nav-results"
          placeholder="Where do you want to go?"
          value={query}
          onFocus={() => setOpen(true)}
          onChange={(event) => { setQuery(event.target.value); setOpen(true); setActiveIndex(0) }}
          onKeyDown={onKeyDown}
          onBlur={(event) => {
            if (!event.currentTarget.parentElement?.parentElement?.contains(event.relatedTarget)) setOpen(false)
          }}
        />
        {query
          ? <button className="quick-nav-clear" aria-label="Clear search" onMouseDown={(event) => event.preventDefault()} onClick={() => { setQuery(''); setActiveIndex(0) }}>Clear</button>
          : <kbd>↑ ↓ ↵</kbd>}
      </div>
      {open && <div className="quick-nav-results" id="quick-nav-results" role="listbox" aria-label="Aether pages">
        {matches.length
          ? matches.map((destination, index) =>
            <button
              type="button"
              className={`quick-nav-option ${index === activeIndex ? 'is-active' : ''}`}
              key={destination.id}
              role="option"
              aria-selected={index === activeIndex}
              onMouseEnter={() => setActiveIndex(index)}
              onMouseDown={(event) => event.preventDefault()}
              onClick={() => navigate(destination)}
            >
              <span className="quick-nav-option-copy"><strong>{destination.label}</strong><small>{destination.detail}</small></span>
              <Icon name="arrow"/>
            </button>,
          )
          : <p className="quick-nav-empty">No Aether pages match “{query}”.</p>}
      </div>}
    </div>
    <p className="quick-nav-caption">Search tools or use ↑ / ↓ and Enter to navigate.</p>
  </div>
}
