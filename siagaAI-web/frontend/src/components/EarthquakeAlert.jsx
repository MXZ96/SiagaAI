import { useState, useEffect } from 'react'

function EarthquakeAlert() {
  // Fallback earthquake data
  const fallbackEarthquake = {
    source: 'Demo Data',
    date: new Date().toLocaleDateString('id-ID'),
    time: new Date().toLocaleTimeString('id-ID') + ' WIB',
    magnitude: '4.5',
    depth: '10 km',
    latitude: '-6.2',
    longitude: '106.8',
    location: 'Jakarta, DKI Jakarta (Demo)',
    potential: 'Gempa tidak berpotensi tsunami',
    felt: 'Tidak terasa'
  }

  const [earthquake, setEarthquake] = useState(fallbackEarthquake)
  const [feltEarthquakes, setFeltEarthquakes] = useState([
    { date: '-', time: '-', magnitude: '-', location: 'Memuat data...', depth: '-' }
  ])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchEarthquakeData()
    // Refresh every 60 seconds
    const interval = setInterval(fetchEarthquakeData, 60000)
    return () => clearInterval(interval)
  }, [])

  const fetchEarthquakeData = async () => {
    try {
      setLoading(true)
      
      // Fetch from backend API
      const [eqResponse, feltResponse] = await Promise.all([
        fetch('/api/earthquake'),
        fetch('/api/earthquakes-felt')
      ])
      
      const eqData = await eqResponse.json()
      const feltData = await feltResponse.json()
      
      if (eqData && !eqData.error) {
        setEarthquake(eqData)
      }
      
      if (feltData && feltData.earthquakes && feltData.earthquakes.length > 0) {
        setFeltEarthquakes(feltData.earthquakes)
      }
      
      setError(null)
    } catch (err) {
      console.error('Error fetching earthquake:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getMagnitudeColor = (magnitude) => {
    const mag = parseFloat(magnitude)
    if (mag >= 7) return 'from-red-600 to-red-700 border-red-500'
    if (mag >= 5) return 'from-orange-500 to-orange-600 border-orange-400'
    if (mag >= 3) return 'from-yellow-500 to-yellow-600 border-yellow-400'
    return 'from-green-500 to-green-600 border-green-400'
  }

  const getMagnitudeEmoji = (magnitude) => {
    const mag = parseFloat(magnitude)
    if (mag >= 7) return '🔴'
    if (mag >= 5) return '🟠'
    if (mag >= 3) return '🟡'
    return '🟢'
  }

  if (loading && !earthquake) {
    return (
      <div className="glass-card p-6 animate-pulse">
        <div className="flex items-center space-x-4">
          <div className="w-16 h-16 bg-dark-border rounded-2xl"></div>
          <div className="flex-1 space-y-3">
            <div className="h-6 bg-dark-border rounded w-1/2"></div>
            <div className="h-4 bg-dark-border rounded w-3/4"></div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="glass-card p-6 border border-dark-border">
        <div className="flex items-center text-dark-muted">
          <span className="text-2xl mr-3">🌋</span>
          <span>Data gempabumi tidak tersedia</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Latest Earthquake */}
      {earthquake && (
        <div className={`glass-card p-6 border bg-gradient-to-br ${getMagnitudeColor(earthquake.magnitude)}`}>
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-4">
              <div className="text-4xl">
                {getMagnitudeEmoji(earthquake.magnitude)}
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">
                  Gempa Terbaru
                </h3>
                <p className="text-white/80 text-sm">
                  {earthquake.date} • {earthquake.time}
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold text-white">
                M{earthquake.magnitude}
              </p>
              <p className="text-white/70 text-xs">
                Kedalaman: {earthquake.depth}
              </p>
            </div>
          </div>
          
          <div className="mt-4 pt-4 border-t border-white/20">
            <p className="text-white font-medium">
              📍 {earthquake.location}
            </p>
            {earthquake.potential && (
              <p className="text-white/80 text-sm mt-2">
                ⚠️ {earthquake.potential}
              </p>
            )}
            {earthquake.felt && (
              <p className="text-white/70 text-sm mt-1">
                Dirasakan di: {earthquake.felt}
              </p>
            )}
          </div>
          
          {earthquake.shakemap && (
            <div className="mt-4">
              <p className="text-white/70 text-xs mb-2">Peta Guncangan:</p>
              <img 
                src={earthquake.shakemap} 
                alt="Shakemap" 
                className="w-full h-32 object-cover rounded-lg"
                onError={(e) => e.target.style.display = 'none'}
              />
            </div>
          )}
          
          <p className="text-white/50 text-xs mt-4">
            Sumber: BMKG • {earthquake.datetime}
          </p>
        </div>
      )}
      
      {/* Recent Felt Earthquakes */}
      {feltEarthquakes.length > 0 && (
        <div className="glass-card p-4">
          <h3 className="text-sm font-bold text-dark-muted mb-3 flex items-center">
            <span className="mr-2">📊</span>
            Gempa Dirasakan Terbaru
          </h3>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {feltEarthquakes.slice(0, 5).map((eq, index) => (
              <div 
                key={index}
                className="flex items-center justify-between p-3 rounded-lg bg-dark-bg/50"
              >
                <div className="flex items-center space-x-3">
                  <span className="text-lg">{getMagnitudeEmoji(eq.magnitude)}</span>
                  <div>
                    <p className="text-white text-sm font-medium">{eq.location}</p>
                    <p className="text-dark-muted text-xs">{eq.date} • {eq.time}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-white font-bold">M{eq.magnitude}</p>
                  <p className="text-dark-muted text-xs">{eq.depth}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default EarthquakeAlert
