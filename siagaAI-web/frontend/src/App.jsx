import { useState, useEffect, useCallback } from 'react'
import RiskAlert from './components/RiskAlert'
import Chatbot from './components/Chatbot'
import DamageUpload from './components/DamageUpload'
import Dashboard from './pages/Dashboard'
import Home from './pages/Home'
import AdminLogin from './pages/AdminLogin'
import AdminDashboard from './pages/AdminDashboard'


// App content
function AppContent() {
  const [currentPage, setCurrentPage] = useState('home')
  const [location, setLocation] = useState('jakarta')
  const [showChatbot, setShowChatbot] = useState(false)
  const [cities, setCities] = useState([])
  

  // Fetch cities list
  useEffect(() => {
    fetch('/api/cities')
      .then(res => res.json())
      .then(data => {
        setCities(data.cities || [])
      })
      .catch(console.error)
  }, [])

  // Check for admin pages on mount and hash change
  useEffect(() => {
    const checkHash = () => {
      const hash = window.location.hash
      if (hash === '#/admin-login') {
        setCurrentPage('admin-login')
      } else if (hash === '#/admin-dashboard') {
        setCurrentPage('admin-dashboard')
      }
    }
    
    checkHash()
    window.addEventListener('hashchange', checkHash)
    return () => window.removeEventListener('hashchange', checkHash)
  }, [])

  const handleLocationChange = useCallback((newLocation) => {
    setLocation(newLocation)
  }, [])

  const navigateTo = (page) => {
    console.log('Navigating to:', page)
    setCurrentPage(page)
    setShowChatbot(false)
    
    // Update hash for direct linking
    if (page === 'admin-login') {
      window.location.hash = '#/admin-login'
    } else if (page === 'admin-dashboard') {
      window.location.hash = '#/admin-dashboard'
    } else {
      window.location.hash = ''
    }
  }

  // Show admin login page
  if (currentPage === 'admin-login') {
    return <AdminLogin />
  }

  // Show admin dashboard
  if (currentPage === 'admin-dashboard') {
    return <AdminDashboard />
  }

  // Normal pages
  return (
    <div className="min-h-screen bg-dark-bg">
      {/* Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-primary-500/10 via-transparent to-transparent rounded-full blur-3xl"></div>
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-danger-500/10 via-transparent to-transparent rounded-full blur-3xl"></div>
      </div>

      {/* Header */}
      <header className="relative bg-dark-card/80 backdrop-blur-xl border-b border-white/5 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div 
              className="flex items-center space-x-3 cursor-pointer group"
              onClick={() => navigateTo('home')}
            >
              <div className="w-12 h-12 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center shadow-lg shadow-primary-500/30 group-hover:scale-110 transition-transform">
                <span className="text-2xl">🛡️</span>
              </div>
              <div>
                <h1 className="text-xl font-bold gradient-text">SiagaAI</h1>
                <p className="text-xs text-dark-muted">Kesiapsiagaan Bencana Indonesia</p>
              </div>
            </div>

            {/* City Selector */}
            <div className="hidden md:flex items-center space-x-2">
              <span className="text-dark-muted text-sm">📍</span>
              <select
                value={location}
                onChange={(e) => handleLocationChange(e.target.value)}
                className="bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 text-dark-text"
              >
                {cities.map(city => (
                  <option key={city.id} value={city.id}>{city.name}</option>
                ))}
              </select>
            </div>

            {/* Navigation */}
            <nav className="hidden lg:flex items-center space-x-2">
              {[
                { id: 'home', icon: '🏠', label: 'Beranda' },
                { id: 'dashboard', icon: '🗺️', label: 'Peta' },
                { id: 'damage', icon: '📸', label: 'Laporan' },
              ].map(item => (
                <button
                  key={item.id}
                  onClick={() => navigateTo(item.id)}
                  className={`px-4 py-2 rounded-xl font-medium transition-all ${
                    currentPage === item.id
                      ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                      : 'text-dark-muted hover:text-dark-text hover:bg-dark-card'
                  }`}
                >
                  <span className="mr-2">{item.icon}</span>
                  {item.label}
                </button>
              ))}
            </nav>

            {/* Chat Button & User/Admin */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowChatbot(!showChatbot)}
                className="bg-gradient-to-r from-success-500 to-success-600 hover:from-success-600 hover:to-success-700 px-5 py-2.5 rounded-xl flex items-center space-x-2 transition-all shadow-lg shadow-success-500/25 hover:shadow-success-500/40"
              >
                <span className="text-lg">💬</span>
                <span className="font-semibold hidden sm:inline">Chat AI</span>
              </button>

              {/* User Login/Logout Button */}
              {isAuthenticated ? (
                <div className="flex items-center gap-2 ml-2">
                  {user?.picture ? (
                    <img 
                      src={user.picture} 
                      alt={user.name}
                      className="w-8 h-8 rounded-full border-2 border-dark-border"
                    />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-primary-500 flex items-center justify-center text-white text-sm font-bold">
                      {user?.name?.charAt(0) || 'U'}
                    </div>
                  )}
                  <button
                    onClick={logout}
                    className="px-3 py-2 rounded-xl text-dark-muted hover:text-danger-400 hover:bg-dark-card transition-colors flex items-center gap-2 border border-dark-border"
                    title="Logout"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                  </button>
                </div>
              ) : null}

              {/* Admin Button */}
              <button
                onClick={() => {
                  console.log('Admin button clicked!')
                  navigateTo('admin-login')
                }}
                className="ml-2 px-3 py-2 rounded-xl text-dark-muted hover:text-dark-text hover:bg-dark-card transition-colors flex items-center gap-2 border border-dark-border"
                title="Admin Dashboard"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                <span className="text-sm font-medium">Admin</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Navigation */}
      <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-dark-card/95 backdrop-blur-xl border-t border-white/5 z-50 pb-safe">
        <div className="flex justify-around py-3">
          {[
            { id: 'home', icon: '🏠', label: 'Beranda' },
            { id: 'dashboard', icon: '🗺️', label: 'Peta' },
            { id: 'damage', icon: '📸', label: 'Laporan' },
          ].map(item => (
            <button
              key={item.id}
              onClick={() => navigateTo(item.id)}
              className={`flex flex-col items-center px-4 py-2 rounded-xl transition-all ${
                currentPage === item.id 
                  ? 'text-primary-400' 
                  : 'text-dark-muted'
              }`}
            >
              <span className="text-xl">{item.icon}</span>
              <span className="text-xs mt-1">{item.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <main className="relative container mx-auto px-2 py-4 pb-24 lg:pb-4">
        {currentPage === 'home' && (
          <Home 
            location={location} 
            onNavigate={navigateTo} 
            cities={cities}
          />
        )}
        {currentPage === 'dashboard' && (
          <Dashboard 
            location={location}
            cities={cities}
            onLocationChange={handleLocationChange}
          />
        )}
        {currentPage === 'damage' && (
          <DamageUpload 
            location={location} 
          />
        )}
      </main>

      {/* Chatbot Overlay */}
      {showChatbot && (
        <div className="fixed bottom-24 right-4 z-50 w-96 max-w-[calc(100vw-2rem)]">
          <Chatbot 
            location={location} 
            onClose={() => setShowChatbot(false)} 
          />
        </div>
      )}

      {/* Emergency Banner */}
      <div className="fixed bottom-24 left-4 z-40 hidden lg:block">
        <div className="bg-gradient-to-r from-danger-600 to-danger-700 text-white px-5 py-3 rounded-xl shadow-xl border border-danger-500/30">
          <p className="font-bold text-sm">🚨 Darurat? Hubungi:</p>
          <p className="text-xs text-danger-200 mt-1">BNPB: 117 • PMI: 122 • Ambulans: 119</p>
        </div>
      </div>
    </div>
  )
}

// Main App with AuthProvider
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App
