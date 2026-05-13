import React, { createContext, useContext, useMemo, useState } from 'react'

const ToastContext = createContext(null)

const toastTypes = {
  success: 'toast-success',
  error: 'toast-error',
  info: 'toast-info'
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const removeToast = (id) => {
    setToasts((current) => current.filter((toast) => toast.id !== id))
  }

  const showToast = (message, type = 'info') => {
    const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`
    setToasts((current) => [...current, { id, message, type }])
    window.setTimeout(() => removeToast(id), 3200)
  }

  const value = useMemo(() => ({ showToast }), [])

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="toast-stack" aria-live="polite" aria-atomic="true">
        {toasts.map((toast) => (
          <div key={toast.id} className={`eco-toast ${toastTypes[toast.type] || toastTypes.info}`}>
            <span>{toast.message}</span>
            <button type="button" className="btn-close btn-close-white ms-3" aria-label="Close" onClick={() => removeToast(toast.id)} />
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within ToastProvider')
  }
  return context
}
