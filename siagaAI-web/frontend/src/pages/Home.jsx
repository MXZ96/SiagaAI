import RiskAlert from '../components/RiskAlert'
import EarthquakeAlert from '../components/EarthquakeAlert'
import EarlyWarning from '../components/EarlyWarning'
import { useState, useEffect } from 'react'

function Home({ location, onNavigate, cities = [] }) {
  const [stats, setStats] = useState({
    cities: 0,
    risk_zones: 0,
    evacuation_points: 0,
    users: 0,
    reports: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/stats')
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatNumber = (num) => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K+'
    }
    return num > 0 ? num + '+' : '0'
  }

  const features = [
    {
      icon: '⚠️',
      title: 'Peringatan Dini',
      description: 'Risiko banjir dan tanah longsor real-time dari BMKG',
      color: 'from-danger-500/20 to-danger-600/10 border-danger-500/20',
      hoverColor: 'hover:from-danger-500/30 hover:to-danger-600/20',
      action: () => onNavigate('dashboard')
    },
    {
      icon: '💬',
      title: 'Chatbot AI Darurat',
      description: 'Panduan evakuasi dan pertolongang pertama berbasis AI',
      color: 'from-success-500/20 to-success-600/10 border-success-500/20',
      hoverColor: 'hover:from-success-500/30 hover:to-success-600/20',
      action: () => {}
    },
    {
      icon: '📸',
      title: 'Laporan Kerusakan',
      description: 'Upload foto kerusakan dan get AI assessment otomatis',
      color: 'from-warning-500/20 to-warning-600/10 border-warning-500/20',
      hoverColor: 'hover:from-warning-500/30 hover:to-warning-600/20',
      action: () => onNavigate('damage')
    },
    {
      icon: '🗺️',
      title: 'Peta Interaktif',
      description: 'Visualisasi zona risiko, titik evakuasi, dan laporan warga',
      color: 'from-primary-500/20 to-primary-600/10 border-primary-500/20',
      hoverColor: 'hover:from-primary-500/30 hover:to-primary-600/20',
      action: () => onNavigate('dashboard')
    }
  ]

  const emergencyContacts = [
    { name: 'BNPB', number: '117', icon: '🚨', color: 'from-danger-500 to-danger-600' },
    { name: 'PMI', number: '122', icon: '🏥', color: 'from-success-500 to-success-600' },
    { name: 'Ambulans', number: '119', icon: '🚑', color: 'from-primary-500 to-primary-600' },
    { name: 'Polisi', number: '110', icon: '👮', color: 'from-blue-500 to-blue-600' },
    { name: 'Pemadam', number: '113', icon: '🔥', color: 'from-orange-500 to-orange-600' }
  ]

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900 p-8 md:p-12 text-white">
        {/* Animated background elements */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-primary-400/20 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2"></div>
        
        <div className="relative z-10">
          <div className="flex items-center space-x-2 mb-4">
            <span className="px-3 py-1 bg-white/20 rounded-full text-sm font-medium backdrop-blur">
              🛡️ Platform Kesiapsiagaan Bencana
            </span>
          </div>
          
          <h1 className="text-4xl md:text-5xl font-bold mb-4 leading-tight">
            SiagaAI - Kesiapsiagaan <br/>
            <span className="text-primary-300">Bencana Indonesia</span>
          </h1>
          
          <p className="text-primary-100 text-lg md:text-xl mb-8 max-w-2xl">
            Platform kesiapsiagaan bencana berbasis AI. Dapatkan peringatan dini, 
            panduan evakuasi, dan laporan kerusakan real-time untuk seluruh Indonesia.
          </p>
          
          <div className="flex flex-wrap gap-4">
            <button 
              onClick={() => onNavigate('dashboard')}
              className="px-8 py-4 bg-white text-primary-700 rounded-2xl font-bold hover:bg-primary-50 transition-all shadow-lg hover:shadow-xl hover:scale-105"
            >
              🗺️ Lihat Peta Risiko
            </button>
            <button 
              onClick={() => onNavigate('damage')}
              className="px-8 py-4 bg-white/10 backdrop-blur text-white rounded-2xl font-bold hover:bg-white/20 transition-all border border-white/20"
            >
              📸 Laporkan Kerusakan
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {loading ? (
          <div className="col-span-4 glass-card p-4 text-center">
            <p className="text-dark-muted">Memuat data...</p>
          </div>
        ) : (
          [
            { label: 'Kota', value: stats.cities, icon: '🏙️' },
            { label: 'Zona Risiko', value: stats.risk_zones, icon: '⚠️' },
            { label: 'Titik Evakuasi', value: stats.evacuation_points, icon: '🏠' },
            { label: 'Users Aktif', value: stats.users, icon: '👥' },
          ].map((stat, index) => (
            <div key={index} className="glass-card p-4 text-center">
              <div className="text-2xl mb-2">{stat.icon}</div>
              <p className="text-2xl font-bold gradient-text">{formatNumber(stat.value)}</p>
              <p className="text-dark-muted text-sm">{stat.label}</p>
            </div>
          ))
        )}
      </div>

      {/* Risk Alert Section - using location prop directly */}
      <div>
        <h2 className="text-2xl font-bold mb-6 flex items-center">
          <span className="mr-3">⚠️</span>
          <span className="gradient-text">Peringatan Dini</span>
        </h2>
        <RiskAlert location={location} />
      </div>

      {/* Earthquake and Early Warning Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Earthquake Section */}
        <div>
          <h2 className="text-2xl font-bold mb-6 flex items-center">
            <span className="mr-3">🌋</span>
            <span className="gradient-text">Gempabumi</span>
          </h2>
          <EarthquakeAlert />
        </div>

        {/* Early Warning Section */}
        <div>
          <h2 className="text-2xl font-bold mb-6 flex items-center">
            <span className="mr-3">📢</span>
            <span className="gradient-text">Peringatan Cuaca</span>
          </h2>
          <EarlyWarning />
        </div>
      </div>

      {/* Features Grid */}
      <div>
        <h2 className="text-2xl font-bold mb-6 flex items-center">
          <span className="mr-3">🎯</span>
          <span className="gradient-text">Fitur Utama</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {features.map((feature, index) => (
            <button
              key={index}
              onClick={feature.action}
              className={`text-left p-6 rounded-2xl border bg-gradient-to-br ${feature.color} ${feature.hoverColor} transition-all hover:shadow-lg hover:scale-[1.02]`}
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-lg font-bold text-white mb-2">{feature.title}</h3>
              <p className="text-dark-muted text-sm">{feature.description}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Emergency Contacts */}
      <div className="glass-card bg-gradient-to-br from-danger-500/10 to-transparent border-danger-500/20">
        <h2 className="text-xl font-bold mb-6 text-white flex items-center">
          <span className="mr-3">📞</span>
          Kontak Darurat
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {emergencyContacts.map((contact, index) => (
            <a
              key={index}
              href={`tel:${contact.number}`}
              className={`group p-4 rounded-xl bg-gradient-to-br ${contact.color} text-white text-center hover:scale-105 transition-transform shadow-lg`}
            >
              <div className="text-2xl mb-2">{contact.icon}</div>
              <p className="font-bold">{contact.name}</p>
              <p className="text-sm opacity-90">{contact.number}</p>
            </a>
          ))}
        </div>
      </div>

      {/* Tips Section */}
      <div className="glass-card">
        <h2 className="text-xl font-bold mb-6 text-white flex items-center">
          <span className="mr-3">💡</span>
          Tips Kesiapsiagaan
        </h2>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/10 p-5 rounded-xl border border-blue-500/20">
            <h3 className="font-semibold text-white mb-3 flex items-center">
              <span className="mr-2">🌊</span> Saat Banjir
            </h3>
            <ul className="text-sm text-dark-muted space-y-2">
              <li className="flex items-start">
                <span className="mr-2 text-blue-400">•</span>
                Evakuasi ke tempat tinggi segera
              </li>
              <li className="flex items-start">
                <span className="mr-2 text-blue-400">•</span>
                Matikan listrik jika air mulai masuk
              </li>
              <li className="flex items-start">
                <span className="mr-2 text-blue-400">•</span>
                Jangan melewati air banjir yang mengalir
              </li>
              <li className="flex items-start">
                <span className="mr-2 text-blue-400">•</span>
                Tetap tenang dan hubungi petugas
              </li>
            </ul>
          </div>
          <div className="bg-gradient-to-br from-orange-500/20 to-orange-600/10 p-5 rounded-xl border border-orange-500/20">
            <h3 className="font-semibold text-white mb-3 flex items-center">
              <span className="mr-2">⛰️</span> Saat Longsor
            </h3>
            <ul className="text-sm text-dark-muted space-y-2">
              <li className="flex items-start">
                <span className="mr-2 text-orange-400">•</span>
                Segera tinggalkan area berbahaya
              </li>
              <li className="flex items-start">
                <span className="mr-2 text-orange-400">•</span>
                Lindungi kepala dan leher
              </li>
              <li className="flex items-start">
                <span className="mr-2 text-orange-400">•</span>
                Jauhi lereng gunung/tebing
              </li>
              <li className="flex items-start">
                <span className="mr-2 text-orange-400">•</span>
                Ikuti instruksi evakuasi
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
