export default function RiskBadge({ score = 0, verdict = 'Unknown' }) {
  let level = 'low'
  if (score >= 70) level = 'danger'
  else if (score >= 35) level = 'suspicious'

  return (
    <div className={`risk-badge ${level}`}>
      <div className="risk-score">{score}</div>
      <div>
        <div className="risk-label">{verdict}</div>
        <div className="risk-subtitle">Risk score / 100</div>
      </div>
    </div>
  )
}
