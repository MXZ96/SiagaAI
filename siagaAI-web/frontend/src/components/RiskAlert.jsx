import { useState, useEffect, useCallback } from 'react'

function RiskAlert({ location = 'jakarta' }) {
  const [riskData, setRiskData] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchRiskData = useCallback(async (loc) => {
    setLoading(true)
    try {
      // Get risk data and weather from backend
      const [riskResponse, weatherResponse] = await Promise.all([
        fetch(`/api/risk?city=${loc}`),
        fetch(`/api/weather?city=${loc}`)
      ])
      
      const risk = await riskResponse.json()
      const weather = await weatherResponse.json()
      
      console.log('Weather API response:', weather)
      
      // Merge data
      const data = { ...risk }
      if (weather && !weather.error) {
        data.weather = weather
      }
      
      setRiskData(data)
    } catch (error) {
      console.error('Error fetching risk data:', error)
    }
    setLoading(false)
  }, [])

  // Fetch data when location prop changes
  useEffect(() => {
    if (location) {
      fetchRiskData(location)
    }
  }, [location, fetchRiskData])

  const getRiskColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'high':
        return 'from-danger-500 to-danger-600'
      case 'medium':
        return 'from-warning-500 to-warning-600'
      case 'low':
        return 'from-success-500 to-success-600'
      default:
        return 'from-gray-500 to-gray-600'
    }
  }

  const getAlertColor = (alert) => {
    switch (alert?.toLowerCase()) {
      case 'red':
        return 'from-danger-600 to-danger-700 border-danger-500/30'
      case 'orange':
        return 'from-warning-600 to-warning-700 border-warning-500/30'
      case 'green':
        return 'from-success-600 to-success-700 border-success-500/30'
      default:
        return 'from-gray-600 to-gray-700 border-gray-500/30'
    }
  }

  // Helper to normalize weather data from both BMKG and simulated formats
  const getWeatherData = (weather) => {
    if (!weather) return { temp: 'N/A', humidity: 'N/A', windSpeed: 'N/A', visibility: 'N/A', uvIndex: 'N/A', weather: 'Unknown', weatherCode: 0 }
    
    // Helper to check if value is valid (not N/A, not undefined, not null)
    const validValue = (val, fallback) => {
      if (val === undefined || val === null || val === 'N/A' || val === 'null') return fallback
      return val
    }
    
    return {
      temp: validValue(weather.temperature || weather.temp, '30'),
      humidity: validValue(weather.humidity || weather.hu, '70'),
      windSpeed: validValue(weather.wind_speed || weather.ws, '10'),
      visibility: validValue(weather.visibility || weather.vs_text, '10'),
      uvIndex: validValue(weather.uv_index || weather.uv, '5'),
      weather: weather.weather_desc || weather.weather || 'Unknown',
      weatherCode: weather.weather_code || 0,
      source: weather.source || 'Unknown'
    }
  }

  const getWeatherIcon = (code) => {
    if (code >= 95) return '⛈️'
    if (code >= 7) return '🌧️'
    if (code >= 5) return '🌧️'
    if (code >= 3) return '☁️'
    if (code >= 1) return '🌤️'
    return '☀️'
  }

  // Get normalized weather data
  const weatherInfo = getWeatherData(riskData?.weather);

  if (loading) {
    return (
      <div className="glass-card p-6 animate-pulse">
        <div className="flex items-center space-x-4">
          <div className="w-20 h-20 bg-dark-border rounded-2xl"></div>
          <div className="flex-1 space-y-3">
            <div className="h-6 bg-dark-border rounded w-1/2"></div>
            <div className="h-4 bg-dark-border rounded w-3/4"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {riskData && (
        <>
          <div className={`glass-card p-6 border bg-gradient-to-br ${getAlertColor(riskData.alert_level)}`}>
            {/* Source indicator */}
            {riskData.weather?.source && (
              <div className="flex items-center justify-end mb-2">
                <span className="text-xs text-white/50">
                  📡 Sumber: {riskData.weather.source}
                </span>
              </div>
            )}
            {/* Alert Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
              <div className="flex items-center space-x-4">
                <div className={`w-20 h-20 rounded-2xl bg-gradient-to-br ${getRiskColor(riskData.flood_risk)} flex items-center justify-center text-4xl shadow-lg`}>
                {riskData.alert_level === 'red' ? '🚨' : riskData.alert_level === 'orange' ? '⚠️' : '✅'}
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white">
                  {riskData.city}, {riskData.province}
                </h3>
                <p className="text-white/70">
                  Status: <span className={`font-bold uppercase ${
                    riskData.alert_level === 'red' ? 'text-danger-300' : 
                    riskData.alert_level === 'orange' ? 'text-warning-300' : 'text-success-300'
                  }`}>{riskData.alert_level === 'red' ? 'Siaga' : riskData.alert_level === 'orange' ? 'Waspada' : 'Aman'}</span>
                </p>
              </div>
            </div>

            {/* Weather Card */}
            <div className="bg-white/10 rounded-xl p-4 backdrop-blur">
              <div className="flex items-center space-x-4">
                <span className="text-5xl">{getWeatherIcon(riskData.weather?.weather_code)}</span>
                <div>
                  <p className="text-4xl font-bold text-white">{riskData.weather?.temperature}°</p>
                  <p className="text-white/70 text-sm">{riskData.weather?.weather}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Risk Indicators */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-white/10 backdrop-blur rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-2xl">🌊</span>
                <span className="font-semibold text-white">Risiko Banjir</span>
              </div>
              <div className={`inline-block px-4 py-1.5 rounded-lg text-sm font-bold text-white bg-gradient-to-r ${getRiskColor(riskData.flood_risk)}`}>
                {riskData.flood_risk?.toUpperCase()}
              </div>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-2xl">⛰️</span>
                <span className="font-semibold text-white">Risiko Longsor</span>
              </div>
              <div className={`inline-block px-4 py-1.5 rounded-lg text-sm font-bold text-white bg-gradient-to-r ${getRiskColor(riskData.landslide_risk)}`}>
                {riskData.landslide_risk?.toUpperCase()}
              </div>
            </div>
          </div>

          {/* Weather Details */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
            <div className="bg-white/10 backdrop-blur rounded-lg p-3 text-center">
              <p className="text-white/50 text-xs">💧 Kelembaban</p>
              <p className="font-bold text-white">{weatherInfo.humidity}%</p>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-lg p-3 text-center">
              <p className="text-white/50 text-xs">💨 Angin</p>
              <p className="font-bold text-white">{weatherInfo.windSpeed} km/j</p>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-lg p-3 text-center">
              <p className="text-white/50 text-xs">👁️ Jarak Pandang</p>
              <p className="font-bold text-white">{weatherInfo.visibility} km</p>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-lg p-3 text-center">
              <p className="text-white/50 text-xs">☀️ UV Index</p>
              <p className="font-bold text-white">{weatherInfo.uvIndex}</p>
            </div>
          </div>

          {/* Description */}
          <div className="bg-white/5 backdrop-blur rounded-xl p-4 mb-6">
            <p className="text-white/80 leading-relaxed">{riskData.description}</p>
          </div>

          {/* Recommendations */}
          <div className="bg-white/10 backdrop-blur rounded-xl p-5">
            <h4 className="font-semibold text-white mb-3 flex items-center">
              <span className="mr-2">📋</span> Rekomendasi
            </h4>
            <div className="grid md:grid-cols-2 gap-2">
              {riskData.recommendations?.slice(0, 4).map((rec, index) => (
                <div key={index} className="flex items-start text-white/80 text-sm">
                  <span className="mr-2 text-primary-400">•</span>
                  {rec}
                </div>
              ))}
            </div>
          </div>

          {/* Forecast */}
          {riskData.weather?.forecast && (
            <div className="mt-6">
              <h4 className="font-semibold text-white mb-3 flex items-center">
                <span className="mr-2">📅</span> Prakiraan 3 Hari
              </h4>
              <div className="grid grid-cols-3 gap-3">
                {riskData.weather.forecast.map((day, index) => (
                  <div key={index} className="bg-white/10 backdrop-blur rounded-xl p-3 text-center">
                    <p className="text-white/70 text-xs">{day.day}</p>
                    <p className="text-lg my-1">{day.weather === 'Hujan' ? '🌧️' : '☀️'}</p>
                    <p className="text-white text-sm font-bold">{day.temp_min}° - {day.temp_max}°</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Last Updated */}
          <p className="text-white/40 text-xs mt-4 text-right">
            Diperbarui: {new Date(riskData.timestamp).toLocaleString('id-ID')}
          </p>
          </div>
        </>
      )}
    </div>
  )
}

export default RiskAlert
