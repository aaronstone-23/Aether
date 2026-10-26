import React, { useEffect, useRef, useState } from 'react'
import { useTheme } from '../lib/contexts'
import { HeistMaskIcon, Icon, Mark } from './Icons'

const navGroups = [
  { label: 'Workspace', links: [['overview', 'Overview'], ['casebook', 'Casebook']] },
  { label: 'Analyze', links: [['check', 'Check a message'], ['email', 'Email forensics']] },
  { label: 'Learn', links: [['practice', 'Practice']] },
  { label: 'Monitor', links: [['bank', 'Bank watch'], ['map', 'Scam reports']] },
  { label: 'Respond', links: [['recovery', 'Recovery']] },
]

const heistNavGroup = [
  { label: 'Command', links: [['overview', 'Briefing'], ['casebook', 'Case files']] },
  { label: 'Assess', links: [['check', 'Read a message'], ['email', 'Trace an email']] },
  { label: 'Train', links: [['practice', 'Rehearse']] },
  { label: 'Monitor', links: [['bank', 'Bank watch'], ['map', 'Signal map']] },
  { label: 'Respond', links: [['recovery', 'Recovery plan']] },
]

const navOrder = navGroups.flatMap((group) =>
  group.links.map(([id]) => id),
)

export default function Nav({
  page,
  go,
  heistMode = false,
  onToggleHeist,
}) {
  const [open, setOpen] = useState(false)

  const eyeRef = useRef(null)
  const eyeCenter = useRef(null)
  const clickCount = useRef(0)
  const clickTimer = useRef(null)
  const pointerFrame = useRef(null)
  const pointerPosition = useRef(null)

  const { theme, setTheme } = useTheme()
  const nextTheme = theme === 'light' ? 'dark' : 'light'
  const visibleGroups = heistMode ? heistNavGroup : navGroups

  const close = () => setOpen(false)

  const measureEyeCenter = () => {
    const eye = eyeRef.current
    if (!eye) return
    const rect = eye.getBoundingClientRect()
    eyeCenter.current = {
      x: rect.left + rect.width / 2,
      y: rect.top + rect.height / 2,
    }
  }

  const openIsland = () => {
    measureEyeCenter()
    setOpen(true)
  }

  const handleBrandClick = () => {
    go('overview')

    clickCount.current += 1
    window.clearTimeout(clickTimer.current)

    if (clickCount.current >= 3) {
      clickCount.current = 0
      onToggleHeist?.()
      return
    }

    clickTimer.current = window.setTimeout(() => {
      clickCount.current = 0
    }, 900)
  }

  const shortcut = /Mac|iPhone|iPad/.test(navigator.platform)
    ? '⌘ K'
    : 'Ctrl K'

  const trackPointer = (event) => {
    if (heistMode) return
    if (!eyeRef.current?.querySelector('.eye-iris')) return
    if (!eyeCenter.current) measureEyeCenter()

    pointerPosition.current = { x: event.clientX, y: event.clientY }
    if (pointerFrame.current !== null) return

    pointerFrame.current = window.requestAnimationFrame(() => {
      pointerFrame.current = null
      const eye = eyeRef.current
      const pointer = pointerPosition.current
      const iris = eye?.querySelector('.eye-iris')
      const center = eyeCenter.current
      if (!eye || !pointer || !iris || !center) return

      const clamp = (value) => Math.max(-1, Math.min(1, value))
      const x = (clamp((pointer.x - center.x) / (window.innerWidth * 0.38)) * 4.2).toFixed(1)
      const y = (clamp((pointer.y - center.y) / Math.max(72, window.innerHeight * 0.26)) * 3.1).toFixed(1)

      iris.setAttribute('transform', `translate(${x} ${y})`)
    })
  }

  const resetPupil = () => {
    pointerPosition.current = null
    eyeCenter.current = null
    if (pointerFrame.current !== null) {
      window.cancelAnimationFrame(pointerFrame.current)
      pointerFrame.current = null
    }
    eyeRef.current?.querySelector('.eye-iris')?.setAttribute('transform', 'translate(0 0)')
  }

  useEffect(() => {
    return () => {
      window.clearTimeout(clickTimer.current)
      if (pointerFrame.current !== null) {
        window.cancelAnimationFrame(pointerFrame.current)
      }
    }
  }, [])

  useEffect(() => {
    const onResize = () => measureEyeCenter()
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [])

  useEffect(() => {
    const onKeyDown = (event) => {
      if (!(event.metaKey || event.ctrlKey) || event.key.toLowerCase() !== 'k') {
        return
      }

      const target = event.target
      if (
        target instanceof HTMLElement &&
        (target.isContentEditable ||
          /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName))
      ) {
        return
      }

      event.preventDefault()
      setOpen(true)
    }

    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [])

  return (
    <header
      className={`island ${heistMode ? 'island-heist' : ''} ${open ? 'island-open' : ''}`}
      onMouseEnter={openIsland}
      onPointerMove={trackPointer}
      onMouseLeave={() => {
        close()
        resetPupil()
      }}
      onFocus={() => setOpen(true)}
      onBlur={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget)) close()
      }}
    >
      <div className="island-top">
        <span className="island-wordmark" aria-hidden="true">
          {heistMode ? 'LA CASA' : 'AETHER'}
        </span>

        <button
          className="brand-mark"
          aria-label="Click three times to change the theme"
          onClick={handleBrandClick}
          ref={eyeRef}
        >
          {heistMode ? (
            <HeistMaskIcon size={42} />
          ) : (
            <Mark
              className="island-eye"
              size={60}
            />
          )}
        </button>

        <div className="island-tools">
          <button
            className="theme-icon"
            aria-label={`Switch to ${nextTheme} theme`}
            onClick={() => setTheme(nextTheme)}
          >
            <Icon name={theme === 'light' ? 'sun' : 'moon'} />
          </button>
          <span className="key-hint">{shortcut}</span>
        </div>
      </div>

      <nav className="island-links" aria-label="Main navigation">
        {visibleGroups.map((group) => (
          <div className="nav-group" key={group.label}>
            <span className="nav-group-label">{group.label}</span>

            <div className="nav-group-items">
              {group.links.map(([id, label]) => (
                <button
                  key={id}
                  className={`nav-link ${page === id ? 'active' : ''}`}
                  style={{ '--item': navOrder.indexOf(id) }}
                  aria-current={page === id ? 'page' : undefined}
                  onClick={() => {
                    go(id)
                    close()
                  }}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        ))}

        <button
          className="nav-help"
          onClick={() => {
            go('recovery')
            close()
          }}
        >
          {heistMode ? 'Open recovery plan' : 'I need help now'}
          <Icon name="arrow" />
        </button>
      </nav>
    </header>
  )
}
