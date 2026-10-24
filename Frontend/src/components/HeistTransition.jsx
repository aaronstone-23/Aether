import React from 'react'
import { HeistMaskIcon } from './Icons'

export default function HeistTransition({ phase }) {
    if (phase === 'idle') return null

    return(
        <div className={`heist-transition heist-transition--${phase}`}
            aria-hidden="true"
        >
            <div className="heist-transition__center">
                <HeistMaskIcon size={260}/>
                    <span>OPERATION ACTIVE</span>
            </div>
        </div>
    )
}