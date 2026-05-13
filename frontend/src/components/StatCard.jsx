import React from 'react'

export default function StatCard({ label, value, hint, accent = 'blue', icon = '◌', delta = null }) {
  return (
    <div className={`stat-card accent-${accent}`}>
      <div className="stat-card-top">
        <div className="stat-icon" aria-hidden="true">{icon}</div>
        <div className="stat-label">{label}</div>
      </div>
      <div className="stat-value">{value}</div>
      {delta && <div className="stat-delta">{delta}</div>}
      <div className="stat-hint">{hint}</div>
    </div>
  )
}
