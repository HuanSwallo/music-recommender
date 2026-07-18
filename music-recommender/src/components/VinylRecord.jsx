import { useId } from 'react'

export default function VinylRecord({ size = 60, duration = "4s", reverse = false, style = {} }) {
  // useId gives each instance a unique ID so multiple vinyls on
  // the same page don't conflict with each other
  const uid = useId().replace(/:/g, '')
  const pathId = `vinyl-label-path-${uid}`

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      role="img"
      aria-label="Flip Side vinyl record logo"
      style={{ flexShrink: 0, ...style }}
    >
      <defs>
        {/*
          Counter-clockwise circle path centered at (50,50) with radius 14.
          Counter-clockwise means text at the top reads left-to-right naturally.
          startOffset="25%" centers the text at the 12 o'clock position.
        */}
        <path
          id={pathId}
          d="M 36,50 a 14,14 0 1,0 28,0 a 14,14 0 1,0 -28,0"
        />
      </defs>

      <g style={{
        transformOrigin: '50px 50px',
        animation: `vinyl-spin ${duration} linear infinite${reverse ? ' reverse' : ''}`
      }}>
        {/* Outer black disc */}
        <circle cx="50" cy="50" r="48" fill="#1a0f08" />

        {/* Groove rings — stroke-only circles give the vinyl texture */}
        <circle cx="50" cy="50" r="44" fill="none" stroke="#2C1810" strokeWidth="1.5" />
        <circle cx="50" cy="50" r="40" fill="none" stroke="#2C1810" strokeWidth="1" />
        <circle cx="50" cy="50" r="36" fill="none" stroke="#2C1810" strokeWidth="1.5" />
        <circle cx="50" cy="50" r="32" fill="none" stroke="#2C1810" strokeWidth="1" />
        <circle cx="50" cy="50" r="28" fill="none" stroke="#2C1810" strokeWidth="1.5" />

        {/* Red label */}
        <circle cx="50" cy="50" r="22" fill="#C0392B" />

        {/* Circular text — follows the path defined in <defs> above */}
        <text
          fontFamily="VT323, monospace"
          fontSize="9"
          fill="#F5EBE0"
          letterSpacing="0.40em"
        >
          <textPath href={`#${pathId}`} startOffset="50%" textAnchor="middle">
            ♪FLIP♪SIDE
          </textPath>
        </text>

        {/* Glare highlight — off-center ellipse makes spin perceptible */}
        <ellipse
          cx="44" cy="43"
          rx="5" ry="3"
          fill="rgba(255,255,255,0.18)"
          transform="rotate(-30 44 43)"
        />

        {/* Center spindle */}
        <circle cx="50" cy="50" r="4" fill="#1a0f08" />
        <circle cx="50" cy="50" r="2" fill="#8B7355" />
      </g>
    </svg>
  )
}