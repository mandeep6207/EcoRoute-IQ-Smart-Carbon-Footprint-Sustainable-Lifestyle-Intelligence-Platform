import React from 'react'

export default function LoadingButton({ loading, children, className = 'btn btn-primary w-100', type = 'button', disabled = false }) {
  return (
    <button className={className} type={type} disabled={disabled || loading}>
      {loading && <span className="spinner-border spinner-border-sm me-2" aria-hidden="true" />}
      {loading ? 'Working...' : children}
    </button>
  )
}
