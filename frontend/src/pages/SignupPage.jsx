import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'

const initialForm = { name: '', email: '', password: '' }

export default function SignupPage() {
  const [form, setForm] = useState(initialForm)
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const { signup } = useAuth()
  const { showToast } = useToast()
  const navigate = useNavigate()

  const handleChange = (event) => {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }))
  }

  const validate = () => {
    const nextErrors = {}
    if (!form.name.trim()) nextErrors.name = 'Name is required.'
    if (!form.email.trim()) nextErrors.email = 'Email is required.'
    if (!form.password.trim()) nextErrors.password = 'Password is required.'
    if (form.password && form.password.length < 6) nextErrors.password = 'Password must be at least 6 characters.'
    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!validate()) return

    setSubmitting(true)
    try {
      await signup(form)
      showToast('Account created successfully.', 'success')
      navigate('/lifestyle')
    } catch (error) {
      showToast(error?.response?.data?.error || 'Unable to create account.', 'error')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-copy">
          <p className="eyebrow">Join EcoRoute IQ</p>
          <h1>Create your sustainability profile.</h1>
          <p>Track carbon impact, get recommendations, and start improving your footprint.</p>
        </div>
        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label">Name</label>
            <input className="form-control" name="name" value={form.name} onChange={handleChange} />
            {errors.name && <small className="form-error">{errors.name}</small>}
          </div>
          <div className="mb-3">
            <label className="form-label">Email</label>
            <input className="form-control" type="email" name="email" value={form.email} onChange={handleChange} />
            {errors.email && <small className="form-error">{errors.email}</small>}
          </div>
          <div className="mb-3">
            <label className="form-label">Password</label>
            <input className="form-control" type="password" name="password" value={form.password} onChange={handleChange} />
            {errors.password && <small className="form-error">{errors.password}</small>}
          </div>
          <button className="btn btn-primary w-100" type="submit" disabled={submitting}>
            {submitting ? 'Creating account...' : 'Create account'}
          </button>
          <p className="auth-switch">
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
