import { useEffect, useRef } from 'react'

/**
 * Full-screen interactive water-ripple canvas.
 * - Idle: slow, gentle ambient waves roll across the surface.
 * - On mouse move: a ripple erupts at the cursor position and propagates
 *   outward, distorting the wave grid like a drop hitting still water.
 */
export default function WaterBackground() {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')

    // ── grid dimensions ────────────────────────────────────────────
    const COLS = 80   // wave grid columns
    const ROWS = 50   // wave grid rows

    let W = window.innerWidth
    let H = window.innerHeight

    // Each cell stores its current height and velocity (2-D wave sim)
    let cur  = Array.from({ length: ROWS }, () => new Float32Array(COLS))
    let prev = Array.from({ length: ROWS }, () => new Float32Array(COLS))

    // Accumulated time for ambient wave injection
    let t = 0

    // Active ripple sparks emitted by the mouse
    const sparks = [] // { x, y, r, maxR, strength, age }

    // ── resize ─────────────────────────────────────────────────────
    const resize = () => {
      W = window.innerWidth
      H = window.innerHeight
      canvas.width  = W
      canvas.height = H
    }
    resize()
    window.addEventListener('resize', resize)

    // ── mouse → ripple ─────────────────────────────────────────────
    const onMove = (e) => {
      const gx = Math.floor((e.clientX / W) * COLS)
      const gy = Math.floor((e.clientY / H) * ROWS)
      const cx = Math.max(1, Math.min(COLS - 2, gx))
      const cy = Math.max(1, Math.min(ROWS - 2, gy))

      // Inject energy into the wave grid
      cur[cy][cx]     += 6
      cur[cy-1]?.[cx] && (cur[cy-1][cx] += 3)
      cur[cy+1]?.[cx] && (cur[cy+1][cx] += 3)
      cur[cy]?.[cx-1] && (cur[cy][cx-1] += 3)
      cur[cy]?.[cx+1] && (cur[cy][cx+1] += 3)

      // Store a visual spark for the ripple ring glow
      sparks.push({
        x: e.clientX,
        y: e.clientY,
        r: 0,
        maxR: 120 + Math.random() * 80,
        strength: 0.7 + Math.random() * 0.3,
        age: 0,
      })
    }
    window.addEventListener('mousemove', onMove)

    // ── animation loop ─────────────────────────────────────────────
    let rafId
    const DAMPING  = 0.985   // energy loss per frame
    const SPREAD   = 0.22    // how fast waves propagate to neighbours

    const tick = () => {
      t += 0.016

      // — Ambient wave injection along edges & center —
      // left edge sine wave
      for (let gy = 0; gy < ROWS; gy++) {
        cur[gy][0] = Math.sin(t * 1.4 + gy * 0.35) * 1.8
          + Math.sin(t * 0.7 + gy * 0.6) * 0.8
      }
      // subtle top-edge drips
      if (Math.random() < 0.04) {
        const rx = 2 + Math.floor(Math.random() * (COLS - 4))
        cur[0][rx] += 3 + Math.random() * 2
      }

      // — 2-D wave propagation —
      for (let gy = 1; gy < ROWS - 1; gy++) {
        for (let gx = 1; gx < COLS - 1; gx++) {
          const neighbours =
            cur[gy-1][gx] + cur[gy+1][gx] +
            cur[gy][gx-1] + cur[gy][gx+1]
          prev[gy][gx] =
            (neighbours * SPREAD +
             cur[gy][gx] * (1 - SPREAD * 2)) * DAMPING
        }
      }
      // swap buffers
      ;[cur, prev] = [prev, cur]

      // ── draw ───────────────────────────────────────────────────
      ctx.clearRect(0, 0, W, H)

      const cellW = W / (COLS - 1)
      const cellH = H / (ROWS - 1)

      // Draw horizontal wave lines (like a rippling water surface viewed top-down)
      for (let gy = 0; gy < ROWS; gy++) {
        ctx.beginPath()

        for (let gx = 0; gx < COLS; gx++) {
          const px = gx * cellW
          const height = cur[gy][gx]

          // Vertical displacement = wave height
          const py = gy * cellH + height * 3.5

          // Color: cool blues, teal tints, shift based on wave height
          const intensity = Math.min(1, Math.abs(height) / 5)
          const r = Math.round(180 + intensity * 30)
          const g = Math.round(210 + intensity * 20)
          const b = Math.round(240 + intensity * 15)
          const a = 0.06 + intensity * 0.18

          if (gx === 0) {
            ctx.moveTo(px, py)
          } else {
            // Smooth curve through points
            const prevPx = (gx - 1) * cellW
            const prevHeight = cur[gy][gx - 1]
            const prevPy = gy * cellH + prevHeight * 3.5
            const cpx = (prevPx + px) / 2
            ctx.quadraticCurveTo(prevPx, prevPy, cpx, (prevPy + py) / 2)
          }

          ctx.strokeStyle = `rgba(${r},${g},${b},${a})`
        }

        const lineHeight = Math.max(0, Math.min(1, Math.abs(cur[gy][COLS >> 1]) / 6))
        ctx.lineWidth = 0.5 + lineHeight * 1.5
        ctx.strokeStyle = `rgba(147,197,253,${0.05 + lineHeight * 0.2})`
        ctx.stroke()
      }

      // Draw vertical lines for the grid mesh feel
      for (let gx = 0; gx < COLS; gx += 4) {
        ctx.beginPath()
        for (let gy = 0; gy < ROWS; gy++) {
          const px = gx * cellW + cur[gy][gx] * 2
          const py = gy * cellH
          gy === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py)
        }
        ctx.strokeStyle = 'rgba(147,197,253,0.04)'
        ctx.lineWidth = 0.5
        ctx.stroke()
      }

      // ── ripple ring glows (mouse sparks) ───────────────────────
      for (let i = sparks.length - 1; i >= 0; i--) {
        const s = sparks[i]
        s.r   += (s.maxR - s.r) * 0.07
        s.age += 0.03

        const progress = s.r / s.maxR
        const alpha    = (1 - progress) * s.strength * 0.55

        if (alpha <= 0.005) { sparks.splice(i, 1); continue }

        // Outer glow ring
        const grad = ctx.createRadialGradient(s.x, s.y, s.r * 0.6, s.x, s.y, s.r)
        grad.addColorStop(0, `rgba(96,165,250,0)`)
        grad.addColorStop(0.6, `rgba(96,165,250,${alpha * 0.4})`)
        grad.addColorStop(0.85, `rgba(147,197,253,${alpha})`)
        grad.addColorStop(1, `rgba(224,242,254,0)`)

        ctx.beginPath()
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2)
        ctx.strokeStyle = `rgba(147,197,253,${alpha})`
        ctx.lineWidth = 1.5
        ctx.stroke()

        // Inner fill pulse
        ctx.beginPath()
        ctx.arc(s.x, s.y, s.r * 0.3 * (1 - progress), 0, Math.PI * 2)
        ctx.fillStyle = `rgba(186,230,253,${alpha * 0.3})`
        ctx.fill()
      }

      rafId = requestAnimationFrame(tick)
    }

    rafId = requestAnimationFrame(tick)

    return () => {
      cancelAnimationFrame(rafId)
      window.removeEventListener('resize', resize)
      window.removeEventListener('mousemove', onMove)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="water-bg-canvas"
      aria-hidden="true"
    />
  )
}
