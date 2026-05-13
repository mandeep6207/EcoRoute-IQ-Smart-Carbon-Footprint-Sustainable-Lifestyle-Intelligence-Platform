import React, { useEffect, useMemo, useState } from 'react'
import { Bar, Line, Pie } from 'react-chartjs-2'
import LoadingScreen from '../components/LoadingScreen'
import StatCard from '../components/StatCard'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'

export default function DashboardPage() {
  const { profile, refreshProfile } = useAuth()
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        await refreshProfile()
        const response = await api.get('/history')
        setHistory(response.data.history || [])
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [refreshProfile])

  const latestAnalysis = profile?.latest_analysis

  const pieData = useMemo(() => {
    const breakdown = latestAnalysis?.result?.category_breakdown || {}
    const labels = Object.keys(breakdown).filter((label) => breakdown[label] > 0)
    return {
      labels,
      datasets: [
        {
          data: labels.map((label) => breakdown[label]),
          backgroundColor: ['#1D4ED8', '#0EA5E9', '#10B981', '#F59E0B', '#8B5CF6'],
          borderWidth: 0,
        },
      ],
    }
  }, [latestAnalysis])

  const lineData = useMemo(() => {
    const labels = history.slice().reverse().map((item) => new Date(item.created_at).toLocaleDateString())
    return {
      labels,
      datasets: [
        {
          label: 'Monthly CO₂ (kg)',
          data: history.slice().reverse().map((item) => item.monthly_co2),
          borderColor: '#7DD3FC',
          backgroundColor: 'rgba(125, 211, 252, 0.16)',
          fill: true,
          tension: 0.35,
        },
      ],
    }
  }, [history])

  const barData = useMemo(() => {
    const scores = latestAnalysis?.result?.source_scores || {}
    return {
      labels: Object.keys(scores),
      datasets: [
        {
          label: 'Impact points',
          data: Object.values(scores),
          backgroundColor: '#34D399',
          borderRadius: 12,
        },
      ],
    }
  }, [latestAnalysis])

  if (loading) {
    return <LoadingScreen label="Loading dashboard data..." />
  }

  return (
    <div className="dashboard-grid">
      <div className="dashboard-hero page-card">
        <div>
          <p className="eyebrow mb-1">Overview</p>
          <h2>Your carbon footprint at a glance.</h2>
          <p className="muted-copy">
            Review your score, emissions, and top impact area. The latest analysis is pulled from SQLite and updated after each submission.
          </p>
        </div>
        <div className="hero-score">
          <span>Current score</span>
          <strong>{latestAnalysis?.carbon_score ?? 'N/A'}</strong>
          <small>{latestAnalysis?.sustainability_rating ?? 'No analysis yet'}</small>
        </div>
      </div>

      <div className="stats-row">
        <StatCard label="Carbon score" value={latestAnalysis?.carbon_score ?? 'N/A'} hint="Lower is better" accent="blue" icon="◎" delta="Current footprint score" />
        <StatCard label="Monthly CO₂" value={`${latestAnalysis?.monthly_co2 ?? 0} kg`} hint="Estimated footprint" accent="green" icon="◈" delta="Per monthly habit profile" />
        <StatCard label="Sustainability rating" value={latestAnalysis?.sustainability_rating ?? '—'} hint="Impact category" accent="amber" icon="⬢" delta="Rule-based score band" />
        <StatCard label="Top source" value={latestAnalysis?.result?.top_emission_source ?? '—'} hint="Highest leverage area" accent="violet" icon="⬟" delta="Best near-term reduction target" />
      </div>

      <div className="chart-card page-card">
        <div className="page-header compact">
          <div>
            <h3>Emission source pie chart</h3>
            <p className="muted-copy mb-0">Your latest category-level carbon distribution.</p>
          </div>
        </div>
        <div className="chart-wrap"><Pie data={pieData} /></div>
      </div>

      <div className="chart-card page-card">
        <div className="page-header compact">
          <div>
            <h3>Monthly trend line chart</h3>
            <p className="muted-copy mb-0">Recent monthly emissions from your saved history.</p>
          </div>
        </div>
        <div className="chart-wrap"><Line data={lineData} /></div>
      </div>

      <div className="chart-card page-card wide">
        <div className="page-header compact">
          <div>
            <h3>Category comparison bar chart</h3>
            <p className="muted-copy mb-0">Impact points across the main footprint drivers.</p>
          </div>
        </div>
        <div className="chart-wrap"><Bar data={barData} /></div>
      </div>
    </div>
  )
}
