const STORAGE_KEY = 'aether-casebook-v1'
const CASEBOOK_VERSION = 1

const ALLOWED_STATUSES = new Set([
    'reviewing',
    'reported',
    'resolved',
])

function cleanText(value, maxLength = 500) {
    if (typeof value !== 'string') return ''

    return value
        .replace(/\u0000/g, '')
        .trim()
        .slice(0, maxLength)

}

function cleanTextList(value) {
    if (!Array.isArray(value)) return[]

    return value
        .slice(0,30)
        .map((item)=>{
            if (typeof item === 'string') {
                return cleanText(item, 500)
            }

            if (item && typeof item === 'object') {
                return cleanText(
                    item.title || item.description || item.action|| '',
                    500
                )
            }

            return ''

        })
        .filter(Boolean)

}

function cleanDate(value, fallback) {
    const parsed = new Date(value)

    if (Number.isNaN(parsed.getTime())) {
        return fallback
    }

    return parsed.toISOString()
}

function normalizeCase(item) {
    if (!item || typeof item !=='object')
        return null
    
    const now = new Date(). toISOString()
    const id = cleanText(item.id, 100)

    if (!id) return null

    const parsedRisk = Number(item.riskScore)
    const riskScore = Number.isFinite(parsedRisk)
        ? Math.max(0, Math.min(100, Math.round(parsedRisk)))
        : 0

    const requestedStatus = cleanText(item.status, 30)
    const status = ALLOWED_STATUSES.has(requestedStatus)
        ? requestedStatus
        : 'reviewing'
    return {
        id,
        title: cleanText(item.title, 100) || 'Untitled case',
        createdAt: cleanDate(item.createdAt, now),
        updatedAt: cleanDate(item.updatedAt, now),
        channel: cleanText(item.channel, 40) || 'unknown',
        verdict: cleanText(item.verdict, 100) || 'Review needed',
        confidence: cleanText(item.confidence, 40) || 'unknown',
        riskScore,
        redFlags: cleanTextList(item.redFlags),
        recommendedActions: cleanTextList(item.recommendedActions),
        status,
        note: cleanText(item.note, 2000)
    }

}

export function createCaseRecord(result) {
    if (!result || typeof result !== 'object') {
        return null
    }

    const now = new Date().toISOString()
    const channel = cleanText(result.channel, 40) || 'unknown'
    const dateLabel = new Date(now).toLocaleDateString()

    const id =
        globalThis.crypto?.randomUUID?.() ||
        `${Date.now()}-${Math.random().toString(16).slice(2)}`

    return normalizeCase({
        id,
        title: `${channel} review · ${dateLabel}`,
        createdAt: now,
        updatedAt: now,
        channel, 
        verdict: result.verdict,
        confidence: result.confidence,
        riskScore: result.risk_score,
        redFlags: result.red_flags,
        recommendedActions: result.recommended_actions,
        status: 'reviewing',
        note: '', 
    })
}

export function readCasebook() {
    try{
        const raw = window.localStorage.getItem(STORAGE_KEY)
        if(!raw) return []

        const parsed = JSON.parse(raw)

        if (
            parsed.version !== CASEBOOK_VERSION ||
            !Array.isArray(parsed.cases)

        ) {
            return []

        }

        return parsed.cases
            .map(normalizeCase)
            .filter(Boolean)

    } catch{
        return []

    }
}

export function writeCasebook(cases){
    try {
        const safeCases = Array.isArray(cases)
            ? cases.map(normalizeCase).filter(Boolean)
            : []
        
        window.localStorage.setItem(
            STORAGE_KEY,
            JSON.stringify({
                version: CASEBOOK_VERSION,
                cases: safeCases,
            }),
        )
        return true
    } catch {
        return false
    }
}

export function downloadCasebook(cases) {
    const safeCases = Array.isArray(cases)
        ? cases.map(normalizeCase).filter(Boolean)
        : []
    
    const backup = {
        app: 'Aether',
        version: CASEBOOK_VERSION,
        exportedAt: new Date().toISOString(),
        cases: safeCases,
    }

    const blob = new Blob(
        [JSON.stringify(backup, null, 2)],
        {type: 'application/json'},
    )
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')

    link.href = url
    link.download = `aether-casebook-${new Date()
        .toISOString()
        .slice(0, 10)}.json`

    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
}

