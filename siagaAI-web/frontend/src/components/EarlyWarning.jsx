import { useState, useEffect } from 'react'

function EarlyWarning() {
  // Fallback warnings data
  const fallbackWarnings = [
    {
      title: 'Peringatan Dini - Demo',
      description: 'Muatan ulang halaman untuk memperbarui data dari BMKG.',
      pubDate: new Date().toISOString(),
      link: '#'
    }
  ]

  const [warnings, setWarnings] = useState(fallbackWarnings)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchWarnings()
    // Refresh every 30 seconds for more frequent updates
    const interval = setInterval(() => {
      console.log('🔄 Refreshing early warnings...')
      fetchWarnings()
    }, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchWarnings = async () => {
    try {
      setLoading(true)
      
      // Fetch from backend API
      const response = await fetch('/api/early-warnings')
      const data = await response.json()
      
      if (data && data.warnings && data.warnings.length > 0) {
        setWarnings(data.warnings)
      }
      setError(null)
    } catch (err) {
      setError('Gagal mengambil data peringatan dini')
      console.error('Error fetching early warnings:', err)
    } finally {
      setLoading(false)
    }
  }

  const getWarningIcon = (title) => {
    const titleLower = (title || '').toLowerCase()
    if (titleLower.includes('banjir') || titleLower.includes('flood')) return '🌊'
    if (titleLower.includes('gunung') || titleLower.includes('volcano')) return '🌋'
    if (titleLower.includes('angin') || titleLower.includes('wind')) return '💨'
    if (titleLower.includes('gelombang') || titleLower.includes('wave')) return '🌊'
    if (titleLower.includes('petir') || titleLower.includes('lightning')) return '⚡'
    return '⚠️'
  }

  const getWarningColor = (title) => {
    const titleLower = (title || '').toLowerCase()
    if (titleLower.includes('merah') || titleLower.includes('red')) {
      return 'from-danger-600 to-danger-700 border-danger-500/30'
    }
    if (titleLower.includes('kuning') || titleLower.includes('orange') || titleLower.includes('oranye')) {
      return 'from-warning-600 to-warning-700 border-warning-500/30'
    }
    return 'from-blue-600 to-blue-700 border-blue-500/30'
  }

  if (loading && warnings.length === 0) {
    return (
      <div className="glass-card p-4 animate-pulse">
        <div className="h-4 bg-dark-border rounded w-1/3 mb-3"></div>
        <div className="space-y-2">
          <div className="h-16 bg-dark-border rounded"></div>
          <div className="h-16 bg-dark-border rounded"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="glass-card p-4 border border-dark-border">
        <div className="flex items-center text-dark-muted">
          <span className="text-xl mr-2">📢</span>
          <span className="text-sm">Peringatan dini tidak tersedia</span>
        </div>
      </div>
    )
  }

  return (
    <div className="glass-card p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-dark-muted flex items-center">
          <span className="mr-2">📢</span>
          Peringatan Dini Cuaca BMKG
        </h3>
        <button 
          onClick={fetchWarnings}
          className="text-xs text-primary-400 hover:text-primary-300"
        >
          🔄 Refresh
        </button>
      </div>

      {warnings.length === 0 ? (
        <div className="text-center py-6 text-dark-muted">
          <span className="text-3xl mb-2 block">✅</span>
          <p className="text-sm">Tidak ada peringatan dini aktif</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-64 overflow-y-auto">
          {warnings.slice(0, 5).map((warning, index) => (
            <div 
              key={index}
              className={`p-3 rounded-xl border bg-gradient-to-r ${getWarningColor(warning.title)}`}
            >
              <div className="flex items-start space-x-3">
                <span className="text-2xl">{getWarningIcon(warning.title)}</span>
                <div className="flex-1 min-w-0">
                  <h4 className="text-white font-medium text-sm truncate">
                    {warning.title}
                  </h4>
                  {warning.description && (
                    <p className="text-white/70 text-xs mt-1 line-clamp-2">
                      {warning.description.replace(/<[^>]*>/g, '').substring(0, 150)}...
                    </p>
                  )}
                  {warning.pubDate && (
                    <p className="text-white/50 text-xs mt-2">
                      {new Date(warning.pubDate).toLocaleString('id-ID', {
                        day: 'numeric',
                        month: 'short',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <p className="text-dark-muted text-xs mt-3 text-center">
        Sumber: BMKG • Perbarui setiap 30 detik
      </p>
    </div>
  )
}

export default EarlyWarning
