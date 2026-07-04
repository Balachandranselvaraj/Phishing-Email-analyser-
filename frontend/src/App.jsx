import { useState } from 'react';
import './App.css';
import Analyzer from './pages/Analyzer.jsx'
import History from './pages/History.jsx'
import WaterBackground from './components/WaterBackground.jsx'
import { Shield } from 'lucide-react'

export default function App() {
  const [page, setPage] = useState('analyzer')

  return (
    <div className="app-shell">
      <WaterBackground />
      <nav className="navbar">
        <div className="brand">
          <Shield size={28} className="animated-hook" />
          <span>Email Analyzer</span>
        </div>
        <div className="nav-actions">
          <button onClick={() => setPage('analyzer')} className={page === 'analyzer' ? 'active' : ''}>Analyzer</button>
          <button onClick={() => setPage('history')} className={page === 'history' ? 'active' : ''}>History</button>
        </div>
      </nav>

      <main>
        {page === 'analyzer' ? <Analyzer /> : <History />}
      </main>
    </div>
  )
}
