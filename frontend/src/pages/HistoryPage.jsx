import React, { useEffect, useState } from 'react'
import LoadingScreen from '../components/LoadingScreen'
import api from '../services/api'

export default function HistoryPage() {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const response = await api.get('/history')
        setHistory(response.data.history || [])
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [])

  if (loading) {
    return <LoadingScreen label="Loading history..." />
  }

  return (
    <div className="page-card wide">
      <div className="page-header compact">
        <div>
          <p className="eyebrow mb-1">History</p>
          <h2>All saved carbon analyses.</h2>
        </div>
      </div>

      <div className="table-responsive">
        <table className="table table-dark table-hover align-middle mb-0 eco-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Carbon score</th>
              <th>CO₂ estimate</th>
              <th>Sustainability rating</th>
            </tr>
          </thead>
          <tbody>
            {history.map((item) => (
              <tr key={item.id}>
                <td>{new Date(item.created_at).toLocaleString()}</td>
                <td>{item.carbon_score}</td>
                <td>{item.monthly_co2} kg</td>
                <td>{item.sustainability_rating}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
