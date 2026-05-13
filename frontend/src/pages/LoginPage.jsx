import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import LoadingButton from '../components/LoadingButton'
import { useToast } from '../context/ToastContext'

const initialForm = { email: '', password: '' }

export default function LoginPage() {
  const [form, setForm] = useState(initialForm)
  const [submitting, setSubmitting] = useState(false)
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
            <input className="form-control" type="email" name="email" value={form.email} onChange={handleChange} />
          </div>
          <div className="mb-3">
            <label className="form-label">Password</label>
            <input className="form-control" type="password" name="password" value={form.password} onChange={handleChange} />
          </div>
          <LoadingButton type="submit" loading={submitting}>Sign in</LoadingButton>
          <p className="auth-switch">
            New here? <Link to="/signup">Create an account</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
