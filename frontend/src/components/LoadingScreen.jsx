import React from 'react'

export default function LoadingScreen({ label = 'Loading EcoRoute IQ...' }) {
  return (
    <div className="loading-screen">
      <div className="loading-card">
        <div className="spinner-border text-light mb-3" role="status" aria-label="Loading" />
        <p className="mb-0 text-white-50">{label}</p>
      </div>
    </div>
  )
}
