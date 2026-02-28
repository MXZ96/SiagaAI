import { useState, useEffect } from 'react'

export default function AdminLogin() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    console.log('AdminLogin component mounted')
  }, [])

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      console.log('Attempting login with:', username)
      const response = await fetch('/api/admin/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      })

      console.log('Response status:', response.status)
      const data = await response.json()
      console.log('Response data:', data)

      if (data.success) {
        localStorage.setItem('admin_user', JSON.stringify(data.user))
        window.location.hash = '#/admin-dashboard'
        window.location.reload()
      } else {
        setError(data.message || 'Login failed')
      }
    } catch (err) {
      console.error('Login error:', err)
      setError('Cannot connect to server. Make sure backend is running on port 5000.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #991b1b 0%, #ea580c 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div style={{ 
        background: 'rgba(255,255,255,0.95)', 
        borderRadius: '20px', 
        padding: '40px',
        width: '100%',
        maxWidth: '400px',
        boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)'
      }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <div style={{ 
            width: '60px', 
            height: '60px', 
            background: 'linear-gradient(135deg, #f97316, #dc2626)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 15px'
          }}>
            <span style={{ fontSize: '28px' }}>🛡️</span>
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 'bold', color: '#1f2937', marginBottom: '5px' }}>
            SiagaAI Admin
          </h1>
          <p style={{ color: '#6b7280', fontSize: '14px' }}>Masuk untuk mengelola laporan</p>
        </div>

        {/* Error */}
        {error && (
          <div style={{ 
            background: '#fee2e2', 
            color: '#b91c1c', 
            padding: '12px', 
            borderRadius: '8px', 
            marginBottom: '20px',
            fontSize: '14px'
          }}>
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                fontSize: '14px',
                outline: 'none',
                boxSizing: 'border-box',
                color: '#374151'
              }}
              placeholder="Masukkan username"
              required
            />
          </div>

          <div style={{ marginBottom: '25px' }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                fontSize: '14px',
                outline: 'none',
                boxSizing: 'border-box',
                color: '#374151'
              }}
              placeholder="Masukkan password"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '14px',
              background: loading ? '#9ca3af' : 'linear-gradient(135deg, #f97316, #dc2626)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s'
            }}
          >
            {loading ? 'Memproses...' : 'Masuk'}
          </button>
        </form>

        {/* Back Link */}
        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          <a 
            href="/" 
            style={{ color: '#6b7280', fontSize: '14px', textDecoration: 'none' }}
          >
            ← Kembali ke halaman utama
          </a>
        </div>

        {/* Demo Credentials */}
        <div style={{ 
          marginTop: '20px', 
          padding: '12px', 
          background: '#f3f4f6', 
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <p style={{ color: '#6b7280', fontSize: '12px', margin: 0 }}>
            Demo: <strong>admin</strong> / <strong>siagaai2024</strong>
          </p>
        </div>
      </div>
    </div>
  )
}

