import { useState } from 'react';
import { api } from '../api/client.js';
import ResultView from '../components/ResultView.jsx';

export default function Analyzer() {
  const [rawEmail, setRawEmail] = useState('')
  const [emailFile, setEmailFile] = useState(null)
  const [attachments, setAttachments] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  async function analyze(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('raw_email', rawEmail)
      if (emailFile) formData.append('email_file', emailFile)
      for (const file of attachments) formData.append('attachments', file)

      const response = await api.post('/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.error || 'Analysis failed. Check backend server.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-grid">
      <section className="hero-card">
        <p className="eyebrow">Phishing Detection MVP</p>
        <h1>Analyze suspicious emails safely</h1>
        <p>
          Paste a raw email or upload a .eml file. The backend checks headers, links,
          attachments, phishing keywords, and generates a risk score.
        </p>
      </section>

      <form onSubmit={analyze} className="analyzer-card">
        <label>
          Raw email content
          <textarea
            value={rawEmail}
            onChange={(e) => setRawEmail(e.target.value)}
            placeholder="Paste full email address or email body here..."
          />
        </label>

        <div className="file-row">
          <label>
            Upload .eml / .txt email
            <input type="file" accept=".eml,.txt" onChange={(e) => setEmailFile(e.target.files[0])} />
          </label>
          <label>
            Optional attachments
            <input type="file" multiple onChange={(e) => setAttachments(Array.from(e.target.files))} />
          </label>
        </div>

        {error && <div className="error-box">{error}</div>}
        <button className="primary-button" disabled={loading} type="submit">
          {loading ? 'Analyzing...' : 'Analyze Email'}
        </button>
      </form>

      <ResultView result={result} />
    </div>
  )
}
