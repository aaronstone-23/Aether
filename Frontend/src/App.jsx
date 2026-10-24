import React, { useEffect, useRef, useState } from 'react'
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
import HeistTransition from './components/HeistTransition'

function Router({
    page,
    go,
    status,
    history,
    setHistory,
    setActiveCase,
    onAsk,
    onPractice,
    heistMode,
}) {
    const onResult = (data) => {
        setActiveCase(data)
        setHistory((prev) => [
            {
                id: `${Date.now()}`,
                risk_score: Number(data.risk_score) || 0,
                verdict: data.verdict || 'Review',
                time: new Date().toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                }),
                case: data,
            },
            ...prev,
        ].slice(0, 40))
    }

    const props = { onResult, onAsk, onPractice, heistMode }

    switch (page) {
        case 'check':
            return <Check {...props} />
        case 'email':
            return <Email {...props} />
        case 'practice':
            return <Practice heistMode={heistMode} />
        case 'bank':
            return <Bank heistMode={heistMode} />
        case 'map':
            return <ScamMap heistMode={heistMode} />
        case 'recovery':
            return <Recovery heistMode={heistMode} />
        default:
            return (
                <Overview
                    status={status}
                    history={history}
                    onResult={onResult}
                    go={go}
                    onAsk={onAsk}
                    onPractice={onPractice}
                    heistMode={heistMode}
                />
            )
    }
}

function Shell() {
    const [page, setPage] = useState('overview')
    const [history, setHistory] = useState([])
    const [activeCase, setActiveCase] = useState(null)
    const [chatOpen, setChatOpen] = useState(false)
    const [heistMode, setHeistMode] = useState(false)
    const [transitionPhase, setTransitionPhase] = useState('idle')

    const transitioning = useRef(false)
    const transitionTimers = useRef([])
    const audioRef = useRef(null)
    const audioFadeTimer = useRef(null)

    const status = useBackendStatus()
    const { theme } = useTheme()

    const go = (id) => {
        setPage(id)
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        })
    }
    const ask = () => setChatOpen(true)

    useEffect(() => {
        document.documentElement.dataset.heistMode = heistMode ? 'on' : 'off'
    }, [heistMode])

    useEffect(() => {
        return () => {
            transitionTimers.current.forEach((timer) => window.clearTimeout(timer))

            if (audioFadeTimer.current) {
                window.clearInterval(audioFadeTimer.current)
            }

            if (audioRef.current) {
                audioRef.current.pause()
                audioRef.current.currentTime = 0
            }

            delete document.documentElement.dataset.heistMode
        }
    }, [])

    const toggleHeistMode = () => {
        if (transitioning.current) return

        transitioning.current = true
        const nextMode = !heistMode
        setTransitionPhase('cover')

        const audio = audioRef.current

        if (audio) {
            if (audioFadeTimer.current) {
                window.clearInterval(audioFadeTimer.current)
            }

            audio.currentTime = 0
            audio.volume = 0.3

            const startedAT = performance.now()
            const playResult = audio.play()
            playResult?.catch?.(() => { })

            audioFadeTimer.current = window.setInterval(() => {
                const progress = Math.min((performance.now() - startedAT) / 1700, 1)
                audio.volume = 0.3 * (1 - progress)

                if (progress >= 1) {
                    window.clearInterval(audioFadeTimer.current)
                    audio.pause()
                    audio.currentTime = 0
                }
            }, 50)
        }


        transitionTimers.current = [
            window.setTimeout(() => {
                setHeistMode(nextMode)
                setTransitionPhase('reveal')
            }, 900),

            window.setTimeout(() => {
                setTransitionPhase('idle')
                transitioning.current = false
            }, 1800),
        ]
    }

    return (
        <>
            <audio
                ref={audioRef}
                src='/audio/heist-sting.mp3'
                preload='auto'
            />

            <Nav
                page={page}
                go={go}
                heistMode={heistMode}
                onToggleHeist={toggleHeistMode}
            />

            <div className={`app-shell theme-${theme}`}>
                <Router
                    page={page}
                    go={go}
                    status={status}
                    history={history}
                    setHistory={setHistory}
                    setActiveCase={setActiveCase}
                    onAsk={ask}
                    onPractice={() => go('practice')}
                    heistMode={heistMode}
                />

                <footer className='site-footer'>
                    <button onClick={() => go('overview')}>
                        <span className='footer-mark'>{heistMode ? 'R' : 'A'}</span>
                        {heistMode ? 'The operation' : 'Aether'}
                    </button>
                    <span>
                        {heistMode
                            ? 'Stay calm. Check every signal.'
                            : 'Clear signals for safer decisions.'}

                    </span>
                    <button onClick={() => go('recovery')}>
                        {heistMode ? 'Recovery plan' : 'Recovery guidance'}
                        {' '}<span aria-hidden='true'>→</span>
                    </button>

                </footer>
            </div>

            <Assistant
                activeCase={activeCase}
                open={chatOpen}
                setOpen={setChatOpen}
                heistMode={heistMode}
            />



            <HeistTransition phase={transitionPhase} />

        </>


    )

}

export default function App() {
    return (
        <ThemeProvider>
            <Shell />
        </ThemeProvider>
    )
}

