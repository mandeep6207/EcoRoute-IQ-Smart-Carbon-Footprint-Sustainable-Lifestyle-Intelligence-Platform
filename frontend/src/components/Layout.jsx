import React, { useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'

const links = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/lifestyle', label: 'Lifestyle Input' },
  { to: '/analytics', label: 'Analytics' },
  { to: '/history', label: 'History' },
  { to: '/profile', label: 'Profile' },
]

export default function Layout() {
  const { user, logout } = useAuth()
  const { showToast } = useToast()
  const navigate = useNavigate()
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  const handleLogout = async () => {
    try {
      await logout()
      showToast('Logged out successfully.', 'success')
      navigate('/login')
    } catch (error) {
      showToast(error?.response?.data?.error || 'Unable to log out.', 'error')
    }
  }

  const closeMobileNav = () => setMobileNavOpen(false)

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <div className="brand-badge">EcoRoute IQ</div>
          <p className="sidebar-copy">Carbon intelligence for sustainable lifestyle decisions.</p>
        </div>

        <nav className="sidebar-nav">
          {links.map((link) => (
            <NavLink key={link.to} to={link.to} className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="user-chip">
            <span className="user-chip-label">Signed in as</span>
            <strong>{user?.name || 'User'}</strong>
          </div>
          <button type="button" className="btn btn-outline-light w-100 mt-3" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div>
            <p className="eyebrow mb-1">EcoRoute IQ</p>
            <h1 className="page-title mb-0">Sustainability command center</h1>
          </div>
          <div className="topbar-actions">
            <div className="topbar-pill d-none d-md-inline-flex">Premium eco analytics</div>
            <button type="button" className="btn btn-outline-light mobile-nav-toggle" onClick={() => setMobileNavOpen((current) => !current)}>
              {mobileNavOpen ? 'Close' : 'Menu'}
            </button>
          </div>
        </header>

        {mobileNavOpen && (
          <div className="mobile-nav-panel d-md-none">
            {links.map((link) => (
              <NavLink key={link.to} to={link.to} onClick={closeMobileNav} className={({ isActive }) => `mobile-nav-link ${isActive ? 'active' : ''}`}>
                {link.label}
              </NavLink>
            ))}
          </div>
        )}

        <section className="content-grid">
          <Outlet />
        </section>
      </main>
    </div>
  )
}
