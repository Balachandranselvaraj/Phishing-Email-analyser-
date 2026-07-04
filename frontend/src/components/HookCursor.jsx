import { useEffect, useRef, useState } from 'react'

/**
 * Custom hook-shaped cursor.
 * - Replaces the native cursor site-wide.
 * - The hook SVG tilts forward while moving and snaps back when idle.
 * - A small trailing dot follows behind for depth.
 */
export default function HookCursor() {
  const cursorRef = useRef(null)
  const dotRef = useRef(null)

  // Current real position
  const pos = useRef({ x: -100, y: -100 })
  // Smoothed dot position
  const dotPos = useRef({ x: -100, y: -100 })
  // Velocity tracking for tilt
  const vel = useRef({ x: 0, y: 0 })
  const lastPos = useRef({ x: -100, y: -100 })

  const [isPointer, setIsPointer] = useState(false)
  const [isClicking, setIsClicking] = useState(false)
  const rafRef = useRef(null)

  useEffect(() => {
    // Hide the native cursor globally
    document.body.style.cursor = 'none'

    const onMove = (e) => {
      pos.current = { x: e.clientX, y: e.clientY }

      // Detect if hovering a clickable element
      const target = e.target
      const style = window.getComputedStyle(target).cursor
      setIsPointer(style === 'pointer' || target.closest('button, a, [role="button"], input, textarea, select, label') !== null)
    }

    const onDown = () => setIsClicking(true)
    const onUp   = () => setIsClicking(false)

    window.addEventListener('mousemove', onMove)
    window.addEventListener('mousedown', onDown)
    window.addEventListener('mouseup',   onUp)

    // RAF loop — smooth dot trailing + velocity-based tilt
    const loop = () => {
      const { x, y } = pos.current

      // Velocity
      vel.current.x = x - lastPos.current.x
      vel.current.y = y - lastPos.current.y
      lastPos.current = { x, y }

      // Move cursor SVG instantly
      if (cursorRef.current) {
        cursorRef.current.style.transform = `translate(${x}px, ${y}px)`
      }

      // Smooth trailing dot (lerp)
      dotPos.current.x += (x - dotPos.current.x) * 0.18
      dotPos.current.y += (y - dotPos.current.y) * 0.18
      if (dotRef.current) {
        dotRef.current.style.transform = `translate(${dotPos.current.x}px, ${dotPos.current.y}px)`
      }

      rafRef.current = requestAnimationFrame(loop)
    }

    rafRef.current = requestAnimationFrame(loop)

    return () => {
      document.body.style.cursor = ''
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mousedown', onDown)
      window.removeEventListener('mouseup',   onUp)
      cancelAnimationFrame(rafRef.current)
    }
  }, [])

  // Tilt: lean forward when moving right, back when moving left
  const tiltDeg = Math.max(-30, Math.min(30, vel.current.x * 2.5))
  const scale   = isClicking ? 0.82 : isPointer ? 1.18 : 1

  return (
    <>
      {/* Trailing dot */}
      <div ref={dotRef} className="hook-cursor-dot" />

      {/* Hook SVG cursor */}
      <div
        ref={cursorRef}
        className={`hook-cursor${isPointer ? ' hook-cursor--pointer' : ''}${isClicking ? ' hook-cursor--clicking' : ''}`}
        style={{ '--tilt': `${tiltDeg}deg`, '--scale': scale }}
        aria-hidden="true"
      >
        <svg
          width="32"
          height="38"
          viewBox="0 0 32 38"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Hook shaft */}
          <line x1="16" y1="2" x2="16" y2="22" stroke="url(#hookGrad)" strokeWidth="3.5" strokeLinecap="round"/>
          {/* Hook curve */}
          <path
            d="M16 22 C16 30, 26 30, 26 24 C26 19, 20 18, 18 21"
            stroke="url(#hookGrad)"
            strokeWidth="3.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            fill="none"
          />
          {/* Barb (the sharp tip pointing back) */}
          <path
            d="M18 21 L14 25"
            stroke="url(#hookGrad)"
            strokeWidth="2.5"
            strokeLinecap="round"
          />
          {/* Eye / loop at top */}
          <circle cx="16" cy="4" r="3" stroke="url(#hookGrad)" strokeWidth="2.5" fill="none"/>

          <defs>
            <linearGradient id="hookGrad" x1="16" y1="0" x2="26" y2="38" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#60a5fa"/>
              <stop offset="100%" stopColor="#1e40af"/>
            </linearGradient>
          </defs>
        </svg>
      </div>
    </>
  )
}
