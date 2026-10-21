import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import './styles.css'
import './dispatch.css'
import './fieldnotes.css'
import './quicknav.css'
import './map.css'
import './readability.css'

createRoot(document.getElementById('root')).render(<React.StrictMode><App /></React.StrictMode>)
