import React, { useMemo } from 'react'
import { Bar } from 'react-chartjs-2'
import StatCard from '../components/StatCard'
import { useAuth } from '../context/AuthContext'

export default function AnalyticsPage() {
  const { profile } = useAuth()
  const analysis = profile?.latest_analysis
  const result = analysis?.result || {}

  const opportunityData = useMemo(() => ({
    labels: (result.reduction_opportunities || []).map((item) => item.label),
    datasets: [
      {
        label: 'Reduction opportunity',
        data: (result.reduction_opportunities || []).map((item) => item.impact),
        backgroundColor: ['#0EA5E9', '#22C55E', '#F59E0B', '#A855F7', '#14B8A6'],
        borderRadius: 12,
      },
    ],
  }), [result])

  return (
    <div className="dashboard-grid">
      <div className="page-card wide">
        <div className="page-header compact">
          <div>
            <p className="eyebrow mb-1">Analytics engine</p>
            <h2>Personalized climate intelligence.</h2>
          </div>
        </div>
        <div className="insight-grid">
          <StatCard label="Carbon score" value={analysis?.carbon_score ?? 'N/A'} hint="0 = best, 100 = highest impact" accent="blue" />
          <StatCard label="Monthly CO₂" value={`${analysis?.monthly_co2 ?? 0} kg`} hint="Estimated based on habits" accent="green" />
          <StatCard label="Rating" value={analysis?.sustainability_rating ?? '—'} hint="Eco Friendly / Moderate / High" accent="amber" />
          <StatCard label="Top emission source" value={result.top_emission_source ?? '—'} hint="Primary intervention target" accent="violet" />
        </div>
      </div>

      <div className="page-card">
        <h3>Insights</h3>
        <ul className="analytics-list">
          {(result.insights || []).map((item) => <li key={item}>{item}</li>)}
        </ul>
      </div>

      <div className="page-card">
        <h3>Recommendations</h3>
        <ul className="analytics-list">
          {(result.recommendations || []).map((item) => <li key={item}>{item}</li>)}
        </ul>
      </div>

      <div className="page-card wide">
        <div className="page-header compact">
          <div>
            <h3>Reduction opportunities</h3>
            <p className="muted-copy mb-0">Priority areas ranked by reduction leverage.</p>
          </div>
        </div>
        <div className="chart-wrap"><Bar data={opportunityData} /></div>
      </div>
    </div>
  )
}
