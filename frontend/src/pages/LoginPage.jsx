import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import LoadingButton from '../components/LoadingButton'
import { useToast } from '../context/ToastContext'

const initialForm = { email: '', password: '' }

export default function LoginPage() {
  const [form, setForm] = useState(initialForm)
  const [submitting, setSubmitting] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const { login } = useAuth()
  const { showToast } = useToast()
  const navigate = useNavigate()

  const handleChange = (event) => {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSubmitting(true)
    try {
      await login(form)
      showToast('Welcome back.', 'success')
      navigate('/dashboard')
    } catch (error) {
      showToast(error?.response?.data?.error || 'Unable to log in.', 'error')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-copy">
          <p className="eyebrow">Welcome back</p>
          <h1>Sign in to your carbon dashboard.</h1>
          <p>Continue tracking your footprint, review history, and adjust your sustainability strategy.</p>
        </div>
        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label">Email</label>
            <input className="form-control" type="email" name="email" autoComplete="email" value={form.email} onChange={handleChange} placeholder="you@example.com" />
          </div>
          <div className="mb-3">
            <div className="d-flex justify-content-between align-items-center mb-2">
              <label className="form-label mb-0">Password</label>
              <button type="button" className="btn btn-link login-toggle" onClick={() => setShowPassword((current) => !current)}>
                {showPassword ? 'Hide' : 'Show'}
              </button>
            </div>
            <input className="form-control" type={showPassword ? 'text' : 'password'} name="password" autoComplete="current-password" value={form.password} onChange={handleChange} placeholder="Enter your password" />
          </div>
          <div className="login-hint">Tip: use the same email you signed up with to preserve your saved analyses.</div>
          <LoadingButton type="submit" loading={submitting}>Sign in</LoadingButton>
          <p className="auth-switch">
            New here? <Link to="/signup">Create an account</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
