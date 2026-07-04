import RiskBadge from './RiskBadge.jsx'
import { API_BASE } from '../api/client.js'

function Section({ title, children }) {
  return <section className="result-section"><h3>{title}</h3>{children}</section>
}

function IssuesList({ items }) {
  if (!items || items.length === 0) return <p className="muted">No items found.</p>
  return (
    <div className="issues-list">
      {items.map((item, index) => (
        <div className="issue-card" key={index}>
          <pre>{JSON.stringify(item, null, 2)}</pre>
        </div>
      ))}
    </div>
  )
}

function statusColor(status) {
  switch (status) {
    case 'High Risk': return '#ff4d4f'
    case 'Moderate': return '#faad14'
    case 'Low': return '#52c41a'
    case 'Clean': return '#8c8c8c'
    default: return '#8c8c8c'
  }
}

function ScoreExplanation({ explanation }) {
  if (!explanation) return null

  const { summary, categories } = explanation

  // Find the max contribution across all categories so bars scale relative to each other
  const maxContribution = Math.max(...categories.map(c => c.contribution ?? 0), 1)

  return (
    <section className="score-explanation">
      <h3>📊 Why This Score?</h3>
      <p className="explanation-summary">{summary}</p>

      <div className="explanation-categories">
        {categories.map((cat, i) => {
          const barWidth = Math.round((cat.contribution / maxContribution) * 100)
          const color = statusColor(cat.status)

          return (
            <div className="explanation-category" key={i}>
              <div className="category-header">
                <span className="category-icon">{cat.icon}</span>
                <span className="category-name">{cat.name}</span>
                <span
                  className="category-status"
                  style={{ color, background: `${color}18` }}
                >
                  {cat.status}
                </span>
                {cat.weight_pct != null && (
                  <span className="category-weight">{cat.weight_pct}% weight</span>
                )}
              </div>

              {/* contribution bar */}
              <div className="contribution-bar-track">
                <div
                  className="contribution-bar-fill"
                  style={{ width: `${barWidth}%`, backgroundColor: color }}
                />
                <span className="contribution-label">+{cat.contribution} pts</span>
              </div>

              {/* reasons */}
              {cat.reasons && cat.reasons.length > 0 && (
                <ul className="category-reasons">
                  {cat.reasons.map((reason, j) => (
                    <li key={j}>{typeof reason === 'string' ? reason : JSON.stringify(reason)}</li>
                  ))}
                </ul>
              )}
            </div>
          )
        })}
      </div>
    </section>
  )
}

export default function ResultView({ result }) {
  if (!result) return null

  const risk = result.risk || {}
  const summary = result.email_summary || {}
  const reportUrl = `${API_BASE}/report/${result.scan_id}`

  return (
    <div className="result-wrapper">
      <div className="result-header">
        <RiskBadge score={risk.score} verdict={risk.verdict} />
        <div className="recommendation">
          <h3>Recommendation</h3>
          <p>{risk.recommendation}</p>
          {result.scan_id && <a href={reportUrl} className="download-button">Download PDF Report</a>}
        </div>
      </div>

      <ScoreExplanation explanation={risk.score_explanation} />

      <Section title="Email Summary">
        <div className="summary-grid">
          <div><b>From</b><span>{summary.from || '-'}</span></div>
          <div><b>To</b><span>{summary.to || '-'}</span></div>
          <div><b>Subject</b><span>{summary.subject || '-'}</span></div>
          <div><b>Date</b><span>{summary.date || '-'}</span></div>
          <div><b>URLs</b><span>{summary.url_count}</span></div>
          <div><b>Attachments</b><span>{summary.attachment_count}</span></div>
        </div>
      </Section>

      <Section title="Header Analysis">
        <IssuesList items={result.header_analysis?.findings?.map((finding) => ({ finding })) || []} />
        <div className="mini-grid">
          <div>SPF: <b>{result.header_analysis?.checks?.spf}</b></div>
          <div>DKIM: <b>{result.header_analysis?.checks?.dkim}</b></div>
          <div>DMARC: <b>{result.header_analysis?.checks?.dmarc}</b></div>
        </div>
      </Section>

      <Section title="URL Analysis">
        <IssuesList items={result.url_analysis?.results || []} />
      </Section>

      <Section title="Attachment Analysis">
        <IssuesList items={result.attachment_analysis?.results || []} />
      </Section>

      <Section title="Content Analysis">
        <IssuesList items={result.content_analysis?.findings || []} />
      </Section>
    </div>
  )
}

