import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'

const initialForm = {
  daily_car_km: '',
  daily_public_transport_km: '',
  monthly_electricity_kwh: '',
  meat_meals_per_week: '',
  flights_per_year: '',
  recycling_frequency: '',
}

export default function LifestylePage() {
  const [form, setForm] = useState(initialForm)
  const [submitting, setSubmitting] = useState(false)
  const [errors, setErrors] = useState({})
  const { analyzeLifestyle } = useAuth()
  const { showToast } = useToast()
  const navigate = useNavigate()

  const handleChange = (event) => {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }))
  }

  const validate = () => {
    const nextErrors = {}
    Object.entries(form).forEach(([key, value]) => {
      if (value === '') {
        nextErrors[key] = 'Required field.'
      } else if (Number(value) < 0) {
        nextErrors[key] = 'Cannot be negative.'
      }
    })
    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!validate()) return

    setSubmitting(true)
    try {
      await analyzeLifestyle(form)
      showToast('Lifestyle analysis saved.', 'success')
      navigate('/dashboard')
    } catch (error) {
      showToast(error?.response?.data?.error || 'Unable to analyze lifestyle data.', 'error')
    } finally {
      setSubmitting(false)
    }
  }

  const fields = [
    ['daily_car_km', 'Daily car travel (km)', 'number', '0.1'],
    ['daily_public_transport_km', 'Public transport usage (km)', 'number', '0.1'],
    ['monthly_electricity_kwh', 'Monthly electricity consumption (kWh)', 'number', '1'],
    ['meat_meals_per_week', 'Meat meals per week', 'number', '1'],
    ['flights_per_year', 'Flights per year', 'number', '1'],
    ['recycling_frequency', 'Recycling frequency per week', 'number', '1'],
  ]

  return (
    <div className="page-card">
      <div className="page-header">
        <div>
          <p className="eyebrow mb-1">Lifestyle input</p>
          <h2>Capture your habits for a monthly carbon analysis.</h2>
        </div>
      </div>

      <form className="input-grid" onSubmit={handleSubmit}>
        {fields.map(([name, label, type, step]) => (
          <div key={name} className="mb-3">
            <label className="form-label">{label}</label>
            <input
              className="form-control"
              type={type}
              step={step}
              min="0"
              name={name}
              value={form[name]}
              onChange={handleChange}
            />
            {errors[name] && <small className="form-error">{errors[name]}</small>}
          </div>
        ))}

        <div className="input-actions">
          <button type="submit" className="btn btn-primary btn-lg" disabled={submitting}>
            {submitting ? 'Analyzing...' : 'Run carbon analysis'}
          </button>
        </div>
      </form>
    </div>
  )
}
