import { useState, useEffect, useRef, useCallback, useMemo } from 'react'

function Dashboard({ location, cities = [], onLocationChange }) {
  const mapRef = useRef(null)
  const [map, setMap] = useState(null)
  const [reports, setReports] = useState([])
  const [evacuationPoints, setEvacuationPoints] = useState([])
  const [riskZones, setRiskZones] = useState([])
  const [weatherData, setWeatherData] = useState(null)
  const [selectedFilter, setSelectedFilter] = useState('all')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [reportsSidebarOpen, setReportsSidebarOpen] = useState(true)
  const [currentCity, setCurrentCity] = useState(null)
  const [loading, setLoading] = useState(true)
  const [userLocation, setUserLocation] = useState(null)
  const [locationLoading, setLocationLoading] = useState(false)
  const [locationError, setLocationError] = useState(null)
  const mapInitialized = useRef(false)
  const L_ref = useRef(null)
  const userMarkerRef = useRef(null)

  // Get user's current location
  const getUserLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setLocationError('Geolocation tidak didukung browser Anda')
      return
    }

    setLocationLoading(true)
    setLocationError(null)

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords
        setUserLocation({ lat: latitude, lng: longitude })
        setLocationLoading(false)
        
        // Pan map to user location
        if (map) {
          map.setView([latitude, longitude], 13)
        }
        
        // Show notification
        if (window.Notification && Notification.permission === 'granted') {
          new Notification('SiagaAI', {
            body: `Lokasi Anda ditemukan: ${latitude.toFixed(4)}, ${longitude.toFixed(4)}`,
            icon: '/favicon.svg'
          })
        }
      },
      (error) => {
        setLocationError(error.message)
        setLocationLoading(false)
      },
      { enableHighAccuracy: true, timeout: 10000 }
    )
  }, [map])

  // Add user location marker to map
  useEffect(() => {
    if (map && userLocation && L_ref.current) {
      const L = L_ref.current
      
      // Remove existing user marker
      if (userMarkerRef.current) {
        map.removeLayer(userMarkerRef.current)
      }
      
      // Create custom user marker (blue pulsing dot)
      const userIcon = L.divIcon({
        className: 'user-location-marker',
        html: `<div style="
          width: 20px;
          height: 20px;
          background: #3b82f6;
          border: 3px solid white;
          border-radius: 50%;
          box-shadow: 0 0 10px rgba(59, 130, 246, 0.8);
        "></div>`,
        iconSize: [20, 20],
        iconAnchor: [10, 10]
      })
      
      userMarkerRef.current = L.marker([userLocation.lat, userLocation.lng], { icon: userIcon })
        .addTo(map)
        .bindPopup('<b>📍 Lokasi Anda</b><br/>Ini adalah posisi Anda saat ini')
        .openPopup()
    }
  }, [map, userLocation])

  // Request notification permission
  const requestNotificationPermission = useCallback(async () => {
    if (window.Notification && Notification.permission === 'default') {
      await Notification.requestPermission()
    }
  }, [])

  // Get current city data
  useEffect(() => {
    if (location && cities.length > 0) {
      const city = cities.find(c => c.id === location)
      if (city) setCurrentCity(city)
    }
  }, [location, cities])

  // Fetch ALL data when component mounts
  useEffect(() => {
    setLoading(true)
    fetchAllData().finally(() => setLoading(false))

    // Auto-refresh every 5 seconds
    const interval = setInterval(fetchAllData, 5000)
    return () => clearInterval(interval)
  }, [])

  // Request notification permission on mount
  useEffect(() => {
    requestNotificationPermission()
  }, [])

  // Update map view when city changes
  useEffect(() => {
    if (map && currentCity && !loading) {
      map.setView([currentCity.lat, currentCity.lng], 11)
    }
  }, [map, currentCity, loading])

  // Update markers when filter changes
  useEffect(() => {
    if (map && !loading && L_ref.current) {
      updateMapMarkers()
    }
  }, [map, selectedFilter, loading, currentCity])

  const fetchAllData = async () => {
    try {
      const [evacRes, zonesRes, reportsRes] = await Promise.all([
        fetch('/api/evacuation'),
        fetch('/api/risk-zones'),
        fetch('/api/reports')
      ])

      const evacData = await evacRes.json()
      const zonesData = await zonesRes.json()
      const reportsData = await reportsRes.json()

      setEvacuationPoints(evacData.points || [])
      setRiskZones(zonesData.zones || [])
      setWeatherData(zonesData.weather || null)
      setReports(reportsData.reports || [])
    } catch (error) {
      console.error('Error fetching map data:', error)
    }
  }

  // Filtered data based on selected city
  const filteredRiskZones = useMemo(() => {
    return riskZones.filter(zone => zone.city === location)
  }, [riskZones, location])

  const filteredEvacuationPoints = useMemo(() => {
    return evacuationPoints.filter(point => point.city === location)
  }, [evacuationPoints, location])

  const filteredReports = useMemo(() => {
    return reports.filter(report => report.city === location)
  }, [reports, location])

  const initMap = async () => {
    if (mapRef.current) {
      const L = await import('leaflet')
      L_ref.current = L
      
      delete L.Icon.Default.prototype._getIconUrl
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
        iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      })

      const mapInstance = L.map(mapRef.current).setView([-6.2, 106.8], 5)
      
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(mapInstance)

      setMap(mapInstance)
    }
  }

  const updateMapMarkers = useCallback(async () => {
    if (!map || !L_ref.current) return

    const L = L_ref.current

    map.eachLayer((layer) => {
      if (layer._url === undefined) {
        map.removeLayer(layer)
      }
    })

    // Add risk zones
    if (selectedFilter === 'all' || selectedFilter === 'zones') {
      const zonesToShow = location ? riskZones.filter(z => z.city === location) : riskZones
      
      zonesToShow.forEach((zone) => {
        const color = zone.risk === 'high' ? '#ef4444' : '#f59e0b'
        
        const circle = L.circle([zone.lat, zone.lng], {
          color: color,
          fillColor: color,
          fillOpacity: 0.4,
          radius: zone.radius || 500,
          weight: 2
        })
        
        const popupContent = `
          <div style="min-width: 180px; padding: 5px;">
            <h3 style="margin: 0 0 8px 0; color: #1e293b; font-weight: bold; font-size: 14px;">
              ⚠️ ${zone.name}
            </h3>
            <p style="margin: 4px 0; color: ${color}; font-weight: bold;">
              Tingkat: ${zone.risk.toUpperCase()}
            </p>
            <p style="margin: 4px 0; color: #64748b; font-size: 12px;">
              ${zone.description || ''}
            </p>
            ${weatherData ? `
              <hr style="margin: 8px 0; border: none; border-top: 1px solid #e2e8f0;"/>
              <p style="margin: 4px 0; color: #0f172a; font-weight: bold; font-size: 12px;">
                🌤️ Cuaca: ${weatherData.temperature}°C, ${weatherData.weather_desc}
              </p>
              <p style="margin: 2px 0; color: #64748b; font-size: 11px;">
                💧 ${weatherData.humidity}% | 💨 ${weatherData.wind_speed} km/j
              </p>
            ` : ''}
          </div>
        `
        
        circle.bindPopup(popupContent)
        circle.addTo(map)
      })
    }

    // Add evacuation points
    if (selectedFilter === 'all' || selectedFilter === 'evacuation') {
      const pointsToShow = location ? evacuationPoints.filter(p => p.city === location) : evacuationPoints
      
      const evacIcon = L.divIcon({
        html: '<div style="background: linear-gradient(135deg, #22c55e, #16a34a); width: 32px; height: 32px; border-radius: 50%; border: 3px solid white; display: flex; align-items: center; justify-content: center; font-size: 16px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">🏠</div>',
        iconSize: [32, 32],
        iconAnchor: [16, 16]
      })

      pointsToShow.forEach((point) => {
        const marker = L.marker([point.lat, point.lng], { icon: evacIcon })
        
        const popupContent = `
          <div style="min-width: 150px; padding: 5px;">
            <h3 style="margin: 0 0 8px 0; color: #1e293b; font-weight: bold; font-size: 14px;">
              🏠 ${point.name}
            </h3>
            <p style="margin: 4px 0; color: #64748b; font-size: 12px;">
              Kapasitas: ${point.capacity} orang
            </p>
            <p style="margin: 4px 0; color: #64748b; font-size: 12px;">
              ${point.description || ''}
            </p>
          </div>
        `
        
        marker.bindPopup(popupContent)
        marker.addTo(map)
      })
    }

    // Add damage reports
    if (selectedFilter === 'all' || selectedFilter === 'reports') {
      const reportsToShow = location ? reports.filter(r => r.city === location) : reports
      
      const reportIcon = L.divIcon({
        html: '<div style="background: linear-gradient(135deg, #f59e0b, #d97706); width: 32px; height: 32px; border-radius: 50%; border: 3px solid white; display: flex; align-items: center; justify-content: center; font-size: 16px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">⚠️</div>',
        iconSize: [32, 32],
        iconAnchor: [16, 16]
      })

      reportsToShow.forEach((report) => {
        const marker = L.marker([report.lat, report.lng], { icon: reportIcon })
        
        const popupContent = `
          <div style="min-width: 150px; padding: 5px;">
            <h3 style="margin: 0 0 8px 0; color: #1e293b; font-weight: bold; font-size: 14px;">
              ⚠️ Laporan Kerusakan
            </h3>
            <p style="margin: 4px 0; color: #64748b; font-size: 12px;">
              Jenis: ${report.type}
            </p>
            <p style="margin: 4px 0; color: #f59e0b; font-weight: bold; font-size: 12px;">
              Tingkat: ${report.severity}
            </p>
            <p style="margin: 4px 0; color: #64748b; font-size: 12px;">
              ${report.description}
            </p>
          </div>
        `
        
        marker.bindPopup(popupContent)
        marker.addTo(map)
      })
    }
  }, [map, riskZones, evacuationPoints, reports, selectedFilter, location])

  // Initialize map
  useEffect(() => {
    if (!mapInitialized.current && mapRef.current && cities.length > 0) {
      initMap()
      mapInitialized.current = true
    }
  }, [cities])

  useEffect(() => {
    if (mapInitialized.current && map && !loading && L_ref.current) {
      updateMapMarkers()
    }
  }, [map, loading])

  const handleCityChange = (newCityId) => {
    if (onLocationChange) {
      onLocationChange(newCityId)
    }
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'bg-danger-500'
      case 'medium': return 'bg-warning-500'
      case 'low': return 'bg-success-500'
      default: return 'bg-gray-500'
    }
  }

  const getSeverityTextColor = (severity) => {
    switch (severity) {
      case 'high': return 'text-danger-500'
      case 'medium': return 'text-warning-500'
      case 'low': return 'text-success-500'
      default: return 'text-gray-500'
    }
  }

  return (
    <div className="h-[calc(100vh-8rem)] flex gap-2">
      {/* Left Sidebar - Zones & Evacuation */}
      <div className={`${sidebarOpen ? 'w-80' : 'w-0'} glass-card overflow-hidden transition-all flex flex-col`}>
        <div className="p-4 border-b border-dark-border">
          <h2 className="text-lg font-bold flex items-center">
            <span className="mr-2">🗺️</span>
            <span className="gradient-text">Dashboard</span>
          </h2>
          
          {loading && (
            <div className="mt-2 p-2 bg-primary-500/20 rounded-lg">
              <p className="text-sm text-primary-400">⏳ Memuat...</p>
            </div>
          )}
          
          {currentCity && (
            <div className="mt-3 p-2 bg-primary-500/10 rounded-lg border border-primary-500/20">
              <p className="text-xs text-dark-muted">Lokasi:</p>
              <p className="font-bold text-white text-sm">{currentCity.name}</p>
            </div>
          )}
          
          <select
            value={location}
            onChange={(e) => handleCityChange(e.target.value)}
            className="w-full mt-3 px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-sm text-dark-text"
          >
            {cities.map(city => (
              <option key={city.id} value={city.id}>{city.name}</option>
            ))}
          </select>

          <div className="flex flex-wrap gap-1 mt-3">
            {[
              { value: 'all', label: 'Semua' },
              { value: 'zones', label: 'Zona' },
              { value: 'evacuation', label: 'Evakuasi' },
              { value: 'reports', label: 'Laporan' }
            ].map(filter => (
              <button
                key={filter.value}
                onClick={() => setSelectedFilter(filter.value)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium ${
                  selectedFilter === filter.value
                    ? 'bg-primary-500 text-white'
                    : 'bg-dark-bg text-dark-muted'
                }`}
              >
                {filter.label}
              </button>
            ))}
          </div>
        </div>

        {/* Stats */}
        <div className="p-4 border-b border-dark-border bg-dark-bg/50">
          <div className="grid grid-cols-3 gap-2">
            <div className="bg-dark-card p-2 rounded-lg text-center">
              <p className="text-xl font-bold text-danger-500">{filteredRiskZones.length}</p>
              <p className="text-xs text-dark-muted">Zona</p>
            </div>
            <div className="bg-dark-card p-2 rounded-lg text-center">
              <p className="text-xl font-bold text-success-500">{filteredEvacuationPoints.length}</p>
              <p className="text-xs text-dark-muted">Evak</p>
            </div>
            <div className="bg-dark-card p-2 rounded-lg text-center">
              <p className="text-xl font-bold text-warning-500">{filteredReports.length}</p>
              <p className="text-xs text-dark-muted">Laporan</p>
            </div>
          </div>

          {/* Weather Info */}
          {weatherData && (
            <div className="bg-dark-card p-3 rounded-lg border border-dark-border mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-dark-muted">🌤️ Cuaca BMKG</span>
                <span className="text-xs text-primary-400">{weatherData.source}</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-2xl">
                  {weatherData.weather_desc?.toLowerCase().includes('hujan') ? '🌧️' : '☀️'}
                </span>
                <div>
                  <p className="text-white font-bold">{weatherData.temperature}°C</p>
                  <p className="text-xs text-dark-muted">{weatherData.weather_desc}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2 mt-2 text-xs">
                <div className="text-dark-muted">💧 {weatherData.humidity}%</div>
                <div className="text-dark-muted">💨 {weatherData.wind_speed} km/j</div>
              </div>
            </div>
          )}
        </div>

        {/* Lists */}
          <div className="flex-1 overflow-y-auto p-4">
          <h3 className="font-semibold text-white text-sm mb-2">⚠️ Zona Risiko</h3>
          <div className="space-y-2 mb-4 max-h-32 overflow-y-auto">
            {filteredRiskZones.map((zone, index) => (
              <div key={index} className="bg-dark-bg p-2 rounded-lg border border-dark-border">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-white text-xs">{zone.name}</span>
                  <span className={`px-1.5 py-0.5 rounded text-xs ${zone.risk === 'high' ? 'bg-danger-500' : 'bg-warning-500'} text-white`}>
                    {zone.risk}
                  </span>
                </div>
              </div>
            ))}
            {filteredRiskZones.length === 0 && <p className="text-xs text-dark-muted">-</p>}
          </div>

          <h3 className="font-semibold text-white text-sm mb-2">🏠 Evakuasi</h3>
          <div className="space-y-2 max-h-32 overflow-y-auto">
            {filteredEvacuationPoints.map((point, index) => (
              <div key={index} className="bg-dark-bg p-2 rounded-lg border border-dark-border">
                <span className="font-medium text-white text-xs">{point.name}</span>
              </div>
            ))}
            {filteredEvacuationPoints.length === 0 && <p className="text-xs text-dark-muted">-</p>}
          </div>
        </div>
      </div>

      {/* Map */}
      <div className="flex-1 rounded-2xl overflow-hidden shadow-2xl relative border border-dark-border">
        <div ref={mapRef} className="w-full h-full" />
        
        {/* Legend */}
        <div className="absolute bottom-4 left-4 bg-dark-card/95 backdrop-blur p-3 rounded-xl border border-dark-border z-[1000] text-xs">
          <p className="font-semibold text-white mb-2">Legenda:</p>
          <div className="space-y-1">
            <div className="flex items-center">
              <span className="w-3 h-3 rounded-full bg-danger-500 mr-2"></span>
              <span className="text-dark-muted">Zona Tinggi</span>
            </div>
            <div className="flex items-center">
              <span className="w-3 h-3 rounded-full bg-warning-500 mr-2"></span>
              <span className="text-dark-muted">Zona Sedang</span>
            </div>
            <div className="flex items-center">
              <span className="w-3 h-3 rounded-full bg-success-500 mr-2"></span>
              <span className="text-dark-muted">Evakuasi</span>
            </div>
          </div>
        </div>

        {/* Map toggle buttons */}
        <div className="absolute top-4 left-4 z-[1000] flex gap-2">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="bg-dark-card p-2 rounded-lg border border-dark-border text-dark-muted hover:text-white"
          >
            🗺️
          </button>
          <button
            onClick={() => setReportsSidebarOpen(!reportsSidebarOpen)}
            className="bg-dark-card p-2 rounded-lg border border-dark-border text-dark-muted hover:text-white"
          >
            📋
          </button>
          <button
            onClick={getUserLocation}
            disabled={locationLoading}
            className={`bg-dark-card p-2 rounded-lg border border-dark-border text-dark-muted hover:text-white ${locationLoading ? 'animate-pulse' : ''}`}
            title="Dapatkan lokasi saya"
          >
            {locationLoading ? '⏳' : '📍'}
          </button>
        </div>
      </div>

      {/* Right Sidebar - Reports */}
      <div className={`${reportsSidebarOpen ? 'w-80' : 'w-0'} glass-card overflow-hidden transition-all flex flex-col`}>
        <div className="p-4 border-b border-dark-border flex items-center justify-between">
          <h2 className="text-lg font-bold flex items-center">
            <span className="mr-2">📋</span>
            <span className="gradient-text">Laporan</span>
          </h2>
          <button
            onClick={() => setReportsSidebarOpen(!reportsSidebarOpen)}
            className="text-dark-muted hover:text-white"
          >
            ▶
          </button>
        </div>

        {/* Reports List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {filteredReports.length > 0 ? (
            filteredReports.map((report, index) => (
              <div key={index} className="bg-dark-bg rounded-xl border border-dark-border overflow-hidden">
                {/* Image if available */}
                {report.image_url && (
                  <div className="h-32 bg-dark-border">
                    <img 
                      src={report.image_url} 
                      alt="Damage" 
                      className="w-full h-full object-cover"
                      onError={(e) => e.target.style.display = 'none'}
                    />
                  </div>
                )}
                
                <div className="p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className={`px-2 py-0.5 rounded text-xs font-bold text-white ${getSeverityColor(report.severity)}`}>
                      {report.severity.toUpperCase()}
                    </span>
                    <span className="text-xs text-dark-muted">
                      {new Date(report.timestamp).toLocaleDateString('id-ID')}
                    </span>
                  </div>
                  
                  <p className="text-sm text-white mb-2">{report.description}</p>
                  
                  <div className="flex items-center justify-between text-xs text-dark-muted">
                    <span>📍 {report.city}</span>
                    <span>{report.type}</span>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-8">
              <p className="text-4xl mb-2">📭</p>
              <p className="text-dark-muted text-sm">Belum ada laporan</p>
              <button 
                onClick={() => window.dispatchEvent(new CustomEvent('navigate', { detail: 'damage' }))}
                className="mt-3 px-4 py-2 bg-primary-500 text-white rounded-lg text-sm"
              >
                + Laporan Baru
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
