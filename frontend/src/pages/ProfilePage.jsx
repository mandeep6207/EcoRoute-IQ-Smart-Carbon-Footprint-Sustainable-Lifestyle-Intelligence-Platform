import React from 'react'
import StatCard from '../components/StatCard'
import { useAuth } from '../context/AuthContext'

export default function ProfilePage() {
  const { profile } = useAuth()
  const user = profile?.user
  const latest = profile?.latest_analysis

  return (
    <div className="dashboard-grid">
      <div className="page-card wide">
        <div className="page-header compact">
          <div>
            <p className="eyebrow mb-1">Profile</p>
            <h2>User information and account analytics.</h2>
          </div>
        </div>

        <div className="profile-hero">
          <div>
            <div className="profile-avatar">{user?.name?.slice(0, 1)?.toUpperCase() || 'E'}</div>
          </div>
          <div>
            <h3 className="mb-1">{user?.name || 'EcoRoute User'}</h3>
            <p className="muted-copy mb-2">{user?.email || 'No email available'}</p>
            <div className="profile-tags">
              <span>Analysis count: {profile?.analysis_count ?? 0}</span>
              <span>Average score: {profile?.average_carbon_score ?? 0}</span>
            </div>
          </div>
        </div>
      </div>

      <StatCard label="Latest score" value={latest?.carbon_score ?? 'N/A'} hint="Most recent footprint score" accent="blue" />
      <StatCard label="Average monthly emissions" value={`${profile?.average_monthly_emissions ?? 0} kg`} hint="Across all saved analyses" accent="green" />
      <StatCard label="Latest rating" value={latest?.sustainability_rating ?? '—'} hint="Current lifestyle category" accent="amber" />
      <StatCard label="Top source" value={latest?.result?.top_emission_source ?? '—'} hint="Most impactful improvement area" accent="violet" />
    </div>
  )
}
