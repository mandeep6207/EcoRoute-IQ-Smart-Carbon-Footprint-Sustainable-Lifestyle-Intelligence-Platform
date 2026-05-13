import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)

  const hydrateProfile = useCallback(async () => {
    try {
      const response = await api.get('/profile')
      setUser(response.data.user)
      setProfile(response.data)
    } catch (error) {
      setUser(null)
      setProfile(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    hydrateProfile()
  }, [])

  const signup = useCallback(async (payload) => {
    const response = await api.post('/signup', payload)
    setUser(response.data.user)
    await hydrateProfile()
    return response.data
  }, [hydrateProfile])

  const login = useCallback(async (payload) => {
    const response = await api.post('/login', payload)
    setUser(response.data.user)
    await hydrateProfile()
    return response.data
  }, [hydrateProfile])

  const logout = useCallback(async () => {
    await api.post('/logout')
    setUser(null)
    setProfile(null)
  }, [])

  const analyzeLifestyle = useCallback(async (payload) => {
    const response = await api.post('/analyze', payload)
    await hydrateProfile()
    return response.data
  }, [hydrateProfile])

  const refreshProfile = useCallback(async () => {
    await hydrateProfile()
  }, [hydrateProfile])

  const value = useMemo(() => ({
    user,
    profile,
    loading,
    signup,
    login,
    logout,
    analyzeLifestyle,
    refreshProfile,
  }), [user, profile, loading])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
