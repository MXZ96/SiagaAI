import { useState, useRef, useCallback } from 'react'

function DamageUpload({ location = 'jakarta' }) {
  const [image, setImage] = useState(null)
  const [preview, setPreview] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState(null)
  const [description, setDescription] = useState('')
  const [reporterName, setReporterName] = useState('')
  const [reporterPhone, setReporterPhone] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitSuccess, setSubmitSuccess] = useState(false)
  const fileInputRef = useRef(null)

  const analyzeImage = useCallback(async (imageData) => {
    setIsAnalyzing(true)
    setResult(null)
    
    try {
      // Use backend API for assessment
      const response = await fetch('/api/assess-damage', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          image: imageData
        })
      })
      
      const data = await response.json()
      
      // Handle error response (not a disaster image)
      if (!data.success) {
        setResult({
          success: false,
          error: data.error || 'Gambar tidak dapat dianalisis',
          is_disaster: false
        })
        return
      }
      
      // Success - disaster image detected
      setResult({
        success: true,
        is_disaster: true,
        disaster_type: data.disaster_type,
        severity: data.severity,
        damage_description: data.damage_description,
        affected_areas: data.affected_areas,
        recommended_actions: data.recommended_actions,
        estimated_impact: data.estimated_impact,
        confidence: data.confidence
      })
    } catch (error) {
      console.error('Error analyzing image:', error)
      setResult({
        success: false,
        error: 'Terjadi kesalahan saat menganalisis gambar'
      })
    }
    
    setIsAnalyzing(false)
  }, [])

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (!file) return

    const reader = new FileReader()
    reader.onloadend = () => {
      setPreview(reader.result)
      setImage(reader.result)
      setResult(null)
      setSubmitSuccess(false)
    }
    reader.readAsDataURL(file)
  }

  const handleAnalyze = () => {
    if (!image) return
    analyzeImage(image)
  }

  const handleSubmit = async () => {
    // Only allow submission if it's a valid disaster image
    if (!result || !result.success || !result.is_disaster || !description) return

    setIsSubmitting(true)
    
    try {
      const response = await fetch('/api/reports', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          lat: -6.2 + (Math.random() * 0.1),
          lng: 106.8 + (Math.random() * 0.1),
          city: location,
          type: 'damage',
          severity: result.severity,
          description: description,
          image_url: preview,
          reporter_name: reporterName || 'Anonim',
          reporter_phone: reporterPhone
        })
      })

      const data = await response.json()
      
      if (data.success) {
        setSubmitSuccess(true)
        setTimeout(() => {
          setImage(null)
          setPreview(null)
          setResult(null)
          setDescription('')
          setReporterName('')
          setReporterPhone('')
          setSubmitSuccess(false)
        }, 3000)
      }
    } catch (error) {
      console.error('Error submitting report:', error)
    }

    setIsSubmitting(false)
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
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

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'high':
        return '🔴'
      case 'medium':
        return '🟡'
      case 'low':
        return '🟢'
      default:
        return '⚪'
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="glass-card p-8">
        <h2 className="text-2xl font-bold mb-2 flex items-center">
          <span className="mr-3">📸</span>
          <span className="gradient-text">Laporan Kerusakan</span>
        </h2>
        <p className="text-dark-muted mb-8">Laporkan kerusakan bencana dengan AI assessment</p>

        {/* Upload Area */}
        <div 
          className="border-2 border-dashed border-dark-border hover:border-primary-500 rounded-2xl p-10 text-center cursor-pointer transition-all bg-dark-bg/30 hover:bg-primary-500/5"
          onClick={() => fileInputRef.current?.click()}
        >
          {preview ? (
            <div className="relative">
              <img 
                src={preview} 
                alt="Preview" 
                className="max-h-72 mx-auto rounded-xl shadow-lg"
              />
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  setPreview(null)
                  setImage(null)
                  setResult(null)
                }}
                className="absolute top-3 right-3 bg-danger-500 text-white rounded-full p-2 hover:bg-danger-600 shadow-lg"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          ) : (
            <>
              <div className="text-6xl mb-4">🖼️</div>
              <p className="text-dark-text mb-2 font-medium">
                Klik untuk upload foto kerusakan
              </p>
              <p className="text-dark-muted text-sm">
                Format: JPG, PNG (max 5MB)
              </p>
            </>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>

        {/* Analyze Button */}
        {image && !result && (
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            className="w-full mt-6 btn-primary flex items-center justify-center space-x-3 py-4"
          >
            {isAnalyzing ? (
              <>
                <div className="animate-spin rounded-full h-6 w-6 border-2 border-white border-t-transparent"></div>
                <span>Menganalisis dengan AI...</span>
              </>
            ) : (
              <>
                <span className="text-xl">🔍</span>
                <span>Analisis Kerusakan</span>
              </>
            )}
          </button>
        )}

        {/* Result */}
        {result && (
          <div className="mt-8 p-6 bg-dark-bg/50 rounded-2xl border border-dark-border">
            <h3 className="font-bold text-lg mb-5 flex items-center">
              <span className="mr-2">📊</span> 
              <span className="gradient-text">Hasil Analisis AI</span>
            </h3>
            
            {/* Error - Not a disaster image */}
            {!result.success ? (
              <div className="p-6 bg-danger-500/10 border border-danger-500 rounded-xl text-center">
                <div className="text-5xl mb-4">❌</div>
                <h4 className="text-danger-400 font-bold text-lg mb-2">Gambar Tidak Valid</h4>
                <p className="text-dark-muted">{result.error}</p>
                <button
                  onClick={() => {
                    setPreview(null)
                    setImage(null)
                    setResult(null)
                  }}
                  className="mt-4 btn-secondary"
                >
                  Upload Foto Lain
                </button>
              </div>
            ) : (
              <>
                {/* Disaster Type */}
                <div className="flex items-center justify-between mb-6 p-4 bg-dark-card rounded-xl border border-danger-500/30">
                  <div className="flex items-center space-x-4">
                    <span className="text-4xl">🚨</span>
                    <div>
                      <p className="font-bold text-lg text-white capitalize">
                        Jenis Bencana: {result.disaster_type}
                      </p>
                      <p className="text-dark-muted text-sm">{result.damage_description}</p>
                    </div>
                  </div>
                </div>

                {/* Severity */}
                <div className="flex items-center justify-between mb-6 p-4 bg-dark-card rounded-xl border border-dark-border">
                  <div className="flex items-center space-x-4">
                    <span className="text-4xl">{getSeverityIcon(result.severity)}</span>
                    <div>
                      <p className="font-bold text-lg text-white capitalize">Tingkat Kerusakan: {result.severity}</p>
                      <p className="text-dark-muted text-sm">{result.estimated_impact}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-dark-muted text-xs">Confidence</p>
                    <p className="text-2xl font-bold text-primary-400">{((result.confidence || 0) * 100).toFixed(0)}%</p>
                  </div>
                </div>

                {/* Affected Areas */}
                {result.affected_areas && result.affected_areas.length > 0 && (
                  <div className="bg-dark-card rounded-xl p-4 mb-6 border border-dark-border">
                    <p className="text-sm font-semibold text-white mb-3 flex items-center">
                      <span className="mr-2">🏚️</span> Area Terdampak
                    </p>
                    <ul className="text-sm text-dark-muted space-y-2">
                      {result.affected_areas.map((area, index) => (
                        <li key={index} className="flex items-start">
                          <span className="mr-2 text-danger-400">•</span>
                          {area}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Recommendations */}
                {result.recommended_actions && result.recommended_actions.length > 0 && (
                  <div className="bg-dark-card rounded-xl p-4 mb-6 border border-dark-border">
                    <p className="text-sm font-semibold text-white mb-3 flex items-center">
                      <span className="mr-2">💡</span> Rekomendasi
                    </p>
                    <ul className="text-sm text-dark-muted space-y-2">
                      {result.recommended_actions.map((rec, index) => (
                        <li key={index} className="flex items-start">
                          <span className="mr-2 text-primary-400">•</span>
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Reporter Info */}
                <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-white mb-2">
                  👤 Nama Pelapor
                </label>
                <input
                  type="text"
                  value={reporterName}
                  onChange={(e) => setReporterName(e.target.value)}
                  placeholder="Nama Anda (opsional)"
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-white mb-2">
                  📱 No. HP
                </label>
                <input
                  type="tel"
                  value={reporterPhone}
                  onChange={(e) => setReporterPhone(e.target.value)}
                  placeholder="Nomor telepon (opsional)"
                  className="input-field"
                />
              </div>
            </div>

            {/* Description Input */}
            <div className="mb-6">
              <label className="block text-sm font-semibold text-white mb-2">
                📝 Deskripsi Tambahan
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Jelaskan kondisi kerusakan..."
                className="input-field"
                rows={3}
              />
            </div>

            {/* Submit Button */}
            <button
              onClick={handleSubmit}
              disabled={!description || isSubmitting || !result?.is_disaster}
              className="w-full btn-success flex items-center justify-center space-x-3 py-4"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-6 w-6 border-2 border-white border-t-transparent"></div>
                  <span>Mengirim...</span>
                </>
              ) : submitSuccess ? (
                <>
                  <span className="text-xl">✅</span>
                  <span>Laporan Terkirim & Menunggu Verifikasi!</span>
                </>
              ) : (
                <>
                  <span className="text-xl">📤</span>
                  <span>Kirim Laporan</span>
                </>
              )}
            </button>
            </>
            )}
          </div>
        )}

        {/* Tips */}
        <div className="mt-8 p-5 bg-primary-500/10 rounded-xl border border-primary-500/20">
          <h4 className="font-semibold text-white mb-3 flex items-center">
            <span className="mr-2">💡</span> Tips Pelaporan
          </h4>
          <ul className="text-sm text-dark-muted space-y-2">
            <li className="flex items-start">
              <span className="mr-2 text-primary-400">•</span>
              Ambil foto dengan pencahayaan yang baik
            </li>
            <li className="flex items-start">
              <span className="mr-2 text-primary-400">•</span>
              Tunjukkan skala kerusakan dengan benda sekitar
            </li>
            <li className="flex items-start">
              <span className="mr-2 text-primary-400">•</span>
              Sertakan lokasi jelas dalam foto
            </li>
            <li className="flex items-start">
              <span className="mr-2 text-primary-400">•</span>
              Berikan deskripsi yang detail dan akurat
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default DamageUpload
