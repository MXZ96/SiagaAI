import { useState, useEffect } from 'react'

export default function AdminDashboard() {
  const [reports, setReports] = useState([])
  const [stats, setStats] = useState({ pending: 0, approved: 0, rejected: 0 })
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [adminUser, setAdminUser] = useState(null)
  const [selectedImage, setSelectedImage] = useState(null)

  // Get admin secret from localStorage (set during login)
  const getAdminHeaders = () => {
    const adminData = localStorage.getItem('admin_user')
    if (adminData) {
      const user = JSON.parse(adminData)
      return { 'X-Admin-Secret': user.secret || '' }
    }
    return {}
  }

  useEffect(() => {
    // Check if logged in
    const user = localStorage.getItem('admin_user')
    if (!user) {
      window.location.hash = '#/admin-login'
      window.location.reload()
      return
    }
    setAdminUser(JSON.parse(user))
    fetchReports()

    // Auto-refresh every 30 seconds for real-time updates
    const interval = setInterval(fetchReports, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchReports = async () => {
    try {
      const headers = getAdminHeaders()
      const response = await fetch('/api/admin/reports', {
        headers: {
          'Content-Type': 'application/json',
          ...headers
        }
      })
      
      if (!response.ok) {
        if (response.status === 401) {
          setError('Unauthorized. Please login again.')
          return
        }
        throw new Error('Failed to fetch reports')
      }
      
      const data = await response.json()
      setReports(data.reports || [])
      setStats({
        pending: data.pending_count || 0,
        approved: data.approved_count || 0,
        rejected: data.rejected_count || 0
      })
      setError(null)
    } catch (err) {
      console.error('Error fetching reports:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async (reportId) => {
    try {
      const headers = getAdminHeaders()
      const response = await fetch(`/api/admin/reports/${reportId}/approve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...headers
        }
      })
      const data = await response.json()
      if (data.success) {
        fetchReports()
      }
    } catch (error) {
      console.error('Error approving report:', error)
    }
  }

  const handleReject = async (reportId) => {
    try {
      const headers = getAdminHeaders()
      const response = await fetch(`/api/admin/reports/${reportId}/reject`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...headers
        }
      })
      const data = await response.json()
      if (data.success) {
        fetchReports()
      }
    } catch (error) {
      console.error('Error rejecting report:', error)
    }
  }

  const handleDelete = async (reportId) => {
    if (!confirm('Apakah Anda yakin ingin menghapus laporan ini?')) return
    try {
      const headers = getAdminHeaders()
      const response = await fetch(`/api/admin/reports/${reportId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          ...headers
        }
      })
      const data = await response.json()
      if (data.success) {
        fetchReports()
      }
    } catch (error) {
      console.error('Error deleting report:', error)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('admin_user')
    window.location.hash = '#/admin-login'
    window.location.reload()
  }

  const filteredReports = filter === 'all' 
    ? (reports || [])
    : (reports || []).filter(r => r.status === filter)

  const getStatusBadge = (status) => {
    const styles = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800'
    }
    const labels = {
      pending: 'Menunggu',
      approved: 'Disetujui',
      rejected: 'Ditolak'
    }
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status] || styles.pending}`}>
        {labels[status] || status}
      </span>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p className="text-dark-muted">Memuat data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-dark-bg p-4 lg:p-8">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-8 gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-dark-text">Admin Dashboard</h1>
          <p className="text-dark-muted">Kelola laporan kerusakan bencana</p>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={fetchReports}
            className="px-4 py-2 bg-dark-card border border-dark-border rounded-lg text-dark-muted hover:text-dark-text transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors"
          >
            Logout
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-500/20 border border-red-500/30 rounded-xl">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-dark-card border border-dark-border rounded-xl p-4">
          <p className="text-dark-muted text-sm">Menunggu</p>
          <p className="text-2xl font-bold text-yellow-400">{stats.pending}</p>
        </div>
        <div className="bg-dark-card border border-dark-border rounded-xl p-4">
          <p className="text-dark-muted text-sm">Disetujui</p>
          <p className="text-2xl font-bold text-green-400">{stats.approved}</p>
        </div>
        <div className="bg-dark-card border border-dark-border rounded-xl p-4">
          <p className="text-dark-muted text-sm">Ditolak</p>
          <p className="text-2xl font-bold text-red-400">{stats.rejected}</p>
        </div>
      </div>

      {/* Filter */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {['all', 'pending', 'approved', 'rejected'].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-colors ${
              filter === f 
                ? 'bg-primary-500 text-white' 
                : 'bg-dark-card border border-dark-border text-dark-muted hover:text-dark-text'
            }`}
          >
            {f === 'all' ? 'Semua' : f === 'pending' ? 'Menunggu' : f === 'approved' ? 'Disetujui' : 'Ditolak'}
          </button>
        ))}
      </div>

      {/* Reports List */}
      <div className="bg-dark-card border border-dark-border rounded-xl overflow-hidden">
        {filteredReports.length === 0 ? (
          <div className="p-8 text-center text-dark-muted">
            <p>Tidak ada laporan</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-dark-bg border-b border-dark-border">
                <tr>
                  <th className="text-left p-4 text-dark-muted font-medium">Foto</th>
                  <th className="text-left p-4 text-dark-muted font-medium">Lokasi</th>
                  <th className="text-left p-4 text-dark-muted font-medium">Deskripsi</th>
                  <th className="text-left p-4 text-dark-muted font-medium">Status</th>
                  <th className="text-left p-4 text-dark-muted font-medium">Tanggal</th>
                  <th className="text-left p-4 text-dark-muted font-medium">Aksi</th>
                </tr>
              </thead>
              <tbody>
                {filteredReports.map((report, idx) => (
                  <tr key={report._id || idx} className="border-b border-dark-border hover:bg-dark-bg/50">
                    <td className="p-4">
                      {report.image_url ? (
                        <button
                          onClick={() => setSelectedImage(report.image_url)}
                          className="w-12 h-12 rounded-lg bg-dark-bg overflow-hidden"
                        >
                          <img src={report.image_url} alt="Report" className="w-full h-full object-cover" />
                        </button>
                      ) : (
                        <div className="w-12 h-12 rounded-lg bg-dark-bg flex items-center justify-center text-dark-muted">
                          -
                        </div>
                      )}
                    </td>
                    <td className="p-4 text-dark-text">
                      <p className="font-medium">{report.location || 'Tidak diketahui'}</p>
                      <p className="text-sm text-dark-muted">{report.city || ''}</p>
                    </td>
                    <td className="p-4 text-dark-text max-w-xs">
                      <p className="truncate">{report.description || 'Tidak ada deskripsi'}</p>
                    </td>
                    <td className="p-4">
                      {getStatusBadge(report.status)}
                    </td>
                    <td className="p-4 text-dark-muted text-sm">
                      {report.created_at ? new Date(report.created_at).toLocaleDateString('id-ID') : '-'}
                    </td>
                    <td className="p-4">
                      <div className="flex gap-2">
                        {report.status === 'pending' && (
                          <>
                            <button
                              onClick={() => handleApprove(report._id)}
                              className="p-2 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30"
                              title="Setuju"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                            </button>
                            <button
                              onClick={() => handleReject(report._id)}
                              className="p-2 bg-yellow-500/20 text-yellow-400 rounded-lg hover:bg-yellow-500/30"
                              title="Tolak"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                              </svg>
                            </button>
                          </>
                        )}
                        <button
                          onClick={() => handleDelete(report._id)}
                          className="p-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30"
                          title="Hapus"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Image Modal */}
      {selectedImage && (
        <div 
          className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedImage(null)}
        >
          <img src={selectedImage} alt="Full size" className="max-w-full max-h-full rounded-lg" />
        </div>
      )}
    </div>
  )
}
