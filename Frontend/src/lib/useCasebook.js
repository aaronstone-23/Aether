import { useState } from "react"
import {
    createCaseRecord,
    readCasebook,
    writeCasebook,
} from './casebook'

const VALID_STATUSES = new Set([
    'reviewing',
    'reported',
    'resolved',
])

export function useCasebook() {
    const [cases, setCases] = useState(() => readCasebook())
    const [error, setError] = useState('')

    function commit(nextCases) {
        const saved = writeCasebook(nextCases)

        if (!saved) {
            setError(
                'Aether could not save this browser. Check available storage and try again.'
            )
            return false

        }

        setCases(nextCases)
        setError('')
        return true
    }

    function saveCase(result){
        const newCase = createCaseRecord(result)
        
        if (!newCase) {
            setError('This analysis could not be saved')

            return false
        }

        return commit([newCase, ...cases])
    }

    function updateCase(id, changes) {
        const updatedAt = new Date().toISOString()

        const nextCases = cases.map((caseItem)=>{
            if (caseItem.id !== id) return caseItem

            const nextCase = {
                ...caseItem,
                updatedAt,
            }

            if (typeof changes.title === 'string') {
                nextCase.title = changes.title.slice(0,100)

            }
            
            if (typeof changes.note === 'string') {
                nextCase.note = changes.note.slice(0, 2000)

            }

            if (VALID_STATUSES.has(changes.status)) {
                nextCase.status = changes.status
            }
            return nextCase
        })

        return commit(nextCases)
    }

    function deleteCase(id) {
        return commit(cases.filter((caseItem) => caseItem.id !== id))
    }

    function clearCases(){
        return commit([])

    }

    return {
        cases,
        error,
        saveCase,
        updateCase,
        deleteCase,
        clearCases,
    }
}
