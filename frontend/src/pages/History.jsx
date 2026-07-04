import { useEffect, useState } from 'react'
import { api } from '../api/client.js'
import ResultView from '../components/ResultView.jsx'

export default function History() {
  const [items, setItems] = useState([])
  const [selected, setSelected] = useState(null)
  const [error, setError] = useState('')

  async function loadHistory() {
    try {
      const response = await api.get('/history')
      setItems(response.data.items || [])
    } catch (err) {
      setError('Unable to load scan history. Check backend server.')
    }
  }

  async function openScan(id) {
    const response = await api.get(`/history/${id}`)
    setSelected(response.data)
  }

  useEffect(() => { loadHistory() }, [])

  return (
    <div className="history-layout">
      <section className="analyzer-card">
        <h2>Scan History</h2>
        {error && <div className="error-box">{error}</div>}
        <div className="history-list">
          {items.map((item) => (
            <button className="history-item" key={item.id} onClick={() => openScan(item.id)}>
              <b>{item.verdict}</b>
              <span>{item.subject || 'No subject'}</span>
              <small>{item.sender || 'Unknown sender'} · Score {item.risk_score}</small>
            </button>
          ))}
          {items.length === 0 && <p className="muted">No scans yet.</p>}
        </div>
      </section>
      <ResultView result={selected} />
    </div>
  )
}
