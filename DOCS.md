# SiagaAI - Dokumentasi Teknis Lengkap

## Daftar Isi

1. [Gambaran Umum Project](#gambaran-umum-project)
2. [Arsitektur Sistem](#arsitektur-sistem)
3. [Struktur File](#struktur-file)
4. [API Endpoints](#api-endpoints)
5. [Komponen Frontend](#komponen-frontend)
6. [Halaman Frontend](#halaman-frontend)
7. [Autentikasi & Otorisasi](#autentikasi--otorisasi)
8. [Integrasi External API](#integrasi-external-api)
9. [Konfigurasi Environment](#konfigurasi-environment)
10. [Panduan Instalasi](#panduan-instalasi)
11. [Fitur Utama](#fitur-utama)
12. [Disaster Classifier](#12-disaster-classifier)

---

## Gambaran Umum Project

SiagaAI adalah platform kesiapsiagaan bencana untuk masyarakat Indonesia yang dibangun dengan teknologi modern. Platform ini mengintegrasikan data real-time dari BMKG (Badan Meteorologi, Klimatologi, dan Geofisika) untuk memberikan informasi peringatan dini bencana kepada masyarakat.

### Tujuan Project

- Menyediakan informasi bencana real-time kepada masyarakat Indonesia
- Memudahkan pelaporan kerusakan akibat bencana
- Memberikan panduan evakuasi dan pertolongan pertama
- Membantu pemerintah dalam mengelola data bencana

### Teknologi yang Digunakan

| Layer | Teknologi |
|-------|-----------|
| Frontend | React.js 18, Tailwind CSS, Leaflet.js, TensorFlow.js |
| Backend | Flask (Python 3.11), MongoDB Atlas |
| Authentication | Google OAuth 2.0, JWT |
| External APIs | BMKG Cuaca, BMKG Gempa, BMKG Peringatan Dini |
| Deployment | Vercel (Frontend), Railway (Backend) |

---

## Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────────────────┐    │
│  │  Home   │  │Dashboard │  │Admin    │  │    Components   │    │
│  │ Page    │  │ Page     │  │ Pages   │  │ (Chatbot, etc) │    │
│  └────┬────┘  └────┬─────┘  └────┬────┘  └────────┬─────────┘    │
│       │           │             │                │              │
│       └───────────┴─────────────┴────────────────┘              │
│                            │                                      │
│                     ┌──────▼──────┐                              │
│                     │  api.js     │  (API Utility)               │
│                     └──────┬──────┘                              │
└────────────────────────────┼────────────────────────────────────┘
                             │ HTTP/HTTPS
┌────────────────────────────┼────────────────────────────────────┐
│                     BACKEND API                                  │
│                            │                                      │
│  ┌─────────────┬──────────┼──────────┬─────────────┐            │
│  │             │          │          │             │            │
│  ▼             ▼          ▼          ▼             ▼            │
│ ┌──────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐        │
│ │Weather│  │Earthquake│ │Early   │  │Risk    │  │Chat    │        │
│ │API   │  │API     │  │Warning │  │Assessment│ │Bot API │        │
│ └──────┘  └────────┘  └────────┘  └────────┘  └────────┘        │
│                              │                                   │
│              ┌───────────────┼───────────────┐                  │
│              ▼               ▼               ▼                  │
│        ┌──────────┐   ┌───────────┐   ┌──────────┐              │
│        │ Auth     │   │ Admin     │   │ Reports  │              │
│        │ (Google) │   │ Dashboard │   │ Manager  │              │
│        └──────────┘   └───────────┘   └──────────┘              │
│                            │                                    │
│                     ┌──────▼──────┐                             │
│                     │ MongoDB     │                             │
│                     │ Atlas       │                             │
│                     └─────────────┘                             │
└──────────────────────────────────────────────────────────────────┘
```

---

## Struktur File

```
siagaAI-web/
├── backend/
│   ├── app.py                 # Main Flask application
│   │                           # - Weather API (BMKG integration)
│   │                           # - Earthquake API
│   │                           # - Early warnings
│   │                           # - Risk assessment
│   │                           # - Evacuation points
│   │                           # - Chatbot API
│   │                           # - Reports management
│   │                           # - Stats endpoints
│   │                           #
│   ├── auth.py                # Google OAuth 2.0 authentication
│   │                           # - /api/auth/google (POST)
│   │                           # - /api/auth/me (GET)
│   │                           # - /api/auth/logout (POST)
│   │                           # - /api/auth/verify (POST)
│   │                           #
│   ├── admin.py               # Admin dashboard routes
│   │                           # - /api/admin/reports (GET)
│   │                           # - /api/admin/reports/:id/approve (POST)
│   │                           # - /api/admin/reports/:id/reject (POST)
│   │                           # - /api/admin/reports/:id (DELETE/GET)
│   │                           # - /api/admin/users (GET)
│   │                           # - /api/admin/stats (GET)
│   │                           #
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment variables template
│   ├── Procfile              # Railway deployment config
│   ├── runtime.txt           # Python version specification
│   ├── pyrightconfig.json   # Type checking config
│   └── railway.json          # Railway deployment config
│
├── frontend/
│   ├── src/
│   │   ├── main.jsx           # React entry point
│   │   ├── App.jsx            # Main app component with routing
│   │   ├── index.css          # Global styles (Tailwind)
│   │   │
│   │   ├── components/
│   │   │   ├── Chatbot.jsx           # AI chatbot for disaster guidance
│   │   │   ├── DamageUpload.jsx       # Damage report submission with AI assessment
│   │   │   ├── EarlyWarning.jsx       # Early warning display component
│   │   │   ├── EarthquakeAlert.jsx    # Real-time earthquake alerts
│   │   │   ├── ErrorBoundary.jsx      # React error boundary
│   │   │   ├── LoadingSpinner.jsx     # Loading indicator
│   │   │   └── RiskAlert.jsx           # Risk level display component
│   │   │
│   │   ├── pages/
│   │   │   ├── Home.jsx               # Landing page
│   │   │   ├── Dashboard.jsx          # Main dashboard with map
│   │   │   ├── AdminLogin.jsx          # Admin login page
│   │   │   └── AdminDashboard.jsx      # Admin dashboard for managing reports
│   │   │
│   │   └── utils/
│   │       └── api.js                  # API utility functions
│   │
│   ├── public/
│   │   └── favicon.svg          # App favicon
│   │
│   ├── index.html               # HTML template
│   ├── package.json             # NPM dependencies
│   ├── vite.config.js           # Vite configuration
│   ├── tailwind.config.js       # Tailwind CSS configuration
│   ├── postcss.config.js        # PostCSS configuration
│   ├── vercel.json              # Vercel deployment config
│   └── .env.example             # Environment variables template
│
├── README.md                    # Project overview
├── DEPLOYMENT.md                # Deployment guide
└── vercel.json                  # Vercel root config
```

---

## API Endpoints

### Public API Endpoints

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/` | Landing page | - |
| GET | `/api/cities` | Get all Indonesian cities | - |
| GET | `/api/weather` | Get weather data for city | `city` (query) |
| GET | `/api/earthquake` | Get latest earthquake | - |
| GET | `/api/earthquakes-felt` | Get felt earthquakes | `min_magnitude` (optional) |
| GET | `/api/early-warnings` | Get early warnings | - |
| GET | `/api/risk` | Get risk assessment | `city` (query) |
| GET | `/api/evacuation` | Get evacuation points | `city` (query) |
| GET | `/api/risk-zones` | Get risk zones | `city` (query) |
| POST | `/api/chat` | Chatbot message | `message`, `location` |
| POST | `/api/admin/login` | Admin login | `username`, `password` |
| GET | `/api/reports` | Get all damage reports | - |
| POST | `/api/reports` | Submit damage report | `city`, `description`, `image`, `location` |
| POST | `/api/assess-damage` | AI damage assessment | `image` (base64) |
| GET | `/api/stats` | Get statistics | - |
| POST | `/api/classify-disaster` | Color-based disaster classification | `image` (base64) |

### Response Format

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/google` | Google OAuth login | No |
| GET | `/api/auth/me` | Get current user | Yes |
| POST | `/api/auth/logout` | Logout user | Yes |
| POST | `/api/auth/verify` | Verify JWT token | No |

### Admin API Endpoints (Requires Admin Access)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/reports` | Get all reports |
| GET | `/api/admin/reports/<report_id>` | Get specific report |
| POST | `/api/admin/reports/<report_id>/approve` | Approve report |
| POST | `/api/admin/reports/<report_id>/reject` | Reject report |
| DELETE | `/api/admin/reports/<report_id>` | Delete report |
| GET | `/api/admin/users` | Get all users |
| GET | `/api/admin/stats` | Get admin statistics | 

## 12. Disaster Classifier

Sistem klasifikasi bencana berbasis analisis warna gambar menggunakan pendekatan hybrid feature extraction.

### 12.1 Arsitektur Modul

**Lokasi**: `backend/disaster_classifier.py`

| Fungsi | Deskripsi |
|--------|-----------|
| decode_base64_image() | Decode gambar base64 ke numpy array |
| analyze_hsv_colors() | Analisis warna HSV |
| calculate_glcm_features() | Ekstrak fitur tekstur GLCM |
| analyze_edges_and_structure() | Edge detection Canny |
| detect_lava() | Deteksi lava |
| detect_cone_shape() | Deteksi bentuk kerucut (gunung) |
| detect_smoke_advanced() | Deteksi asap |
| detect_foam() | Deteksi busa (tsunami) |
| detect_horizon() | Deteksi garis horizon |
| detect_surface_flatness() | Deteksi permukaan datar |
| classify_disaster() | Klasifikasi utama |

### 12.2 Metode Ekstraksi Fitur

**Analisis Warna (HSV):**
- Merah (Hue 0-20): Api, lava
- Oranye (Hue 20-40): Api, asap
- Hijau (Hue 35-85): Vegetasi
- Biru (Hue 85-130): Air, tsunami
- Coklat (Hue 20-35, sat sedang): Banjir
- Abu (low saturation): Asap
- Putih (high value, low saturation): Busa

**Analisis Tekstur (GLCM):**
- Contrast, Energy, Homogeneity, Entropy

**Edge Detection (Canny):**
- Edge density, Horizontal/Vertical ratio, Irregular edges

### 12.3 Aturan Klasifikasi

| Disaster | Kriteria Utama |
|----------|----------------|
| Kebakaran | Merah+Oranye >=25% + Smoke + NO Cone |
| Gunung Berapi | Lava + Cone OR Cone + Smoke |
| Gempa | Building damage + Irregular edges >35% |
| Tsunami | Wave + Horizon/Blue/Foam |
| Banjir | Flat surface + Brown >25% + Homogeneity >60% |
| Tanah Longsor | Green+Brown >=40% + Irregular >25% + Slope |

**Threshold:** 0.65-0.75 (bergantung pada score gap)

### 12.4 Endpoint API

**POST /api/assess-damage**
- Input: `{"image": "base64..."}`
- Output: disaster_type, confidence, severity, recommendations, color_analysis

**POST /api/classify-disaster**
- Input: `{"image": "base64..."}`
- Output: kategori_bencana, confidence_score, top_2_kemungkinan

### 12.5 Catatan Penting

1. **Bukan ML**: Rule-based color analysis (bukan machine learning)
2. **No Memory**: Setiap upload dianalisis secara independen
3. **Deterministik**: Gambar yang sama = hasil yang sama
4. **Threshold Tinggi**: Banyak gambar -> "Tidak Teridentifikasi"

### Response Format

### Response Format

#### Success Response
```json
{
  "success": true,
  "data": { ... }
}
```

#### Error Response
```json
{
  "success": false,
  "error": "Error message here"
}
```

#### City List Response
```json
{
  "success": true,
  "cities": [
    {
      "id": "jakarta",
      "name": "Jakarta",
      "lat": -6.2088,
      "lng": 106.8456,
      "province": "DKI Jakarta"
    }
  ]
}
```

#### Weather Response
```json
{
  "success": true,
  "weather": {
    "source": "BMKG",
    "temperature": 30,
    "humidity": 75,
    "wind_speed": 10,
    "wind_direction": "SE",
    "weather_code": 1,
    "weather_desc": "Cerah berawan",
    "local_datetime": "2024-01-15T10:00:00",
    "visibility": "10",
    "uv_index": "6",
    "forecast": [...]
  }
}
```

#### Earthquake Response
```json
{
  "success": true,
  "earthquake": {
    "id": "eq-2024-001",
    "lat": -6.5,
    "lng": 107.0,
    "magnitude": 5.2,
    "depth": 10,
    "location": "Jawa Barat",
    "time": "2024-01-15T09:30:00",
    "felt": true,
    "tsunami": false
  }
}
```

---

## Komponen Frontend

### Chatbot.jsx

**Lokasi**: `frontend/src/components/Chatbot.jsx`

**Deskripsi**: Komponen chatbot AI yang memberikan panduan terkait bencana.

**Fitur**:
- Respons otomatis untuk pertanyaan umum tentang bencana
- Informasi rute evakuasi
- Panduan pertolongan pertama
- Nomor darurat penting (BNPB, PMI, Ambulans)
- Riwayat percakapan

**State**:
```javascript
{
  messages: Array,      // Daftar pesan
  inputMessage: String, // Input pengguna
  isLoading: Boolean    // Status loading
}
```

**API yang Digunakan**: `POST /api/chat`

---

### DamageUpload.jsx

**Lokasi**: `frontend/src/components/DamageUpload.jsx`

**Deskripsi**: Komponen untuk upload foto kerusakan akibat bencana dengan penilaian AI.

**Fitur**:
- Upload gambar kerusakan
- AI assessment menggunakan TensorFlow.js
- Tingkat kerusakan: Ringan, Sedang, Berat
- Form laporan dengan deskripsi
- Pilih lokasi pada peta

**State**:
```javascript
{
  image: String|Null,           // Gambar yang diupload
  preview: String|Null,        // Preview gambar
  description: String,          // Deskripsi kerusakan
  damageLevel: String,          // Tingkat kerusakan (ringan/sedang/berat)
  confidence: Number,           // Confidence score AI
  location: Object,             // Lokasi kerusakan
  isAssessing: Boolean,        // Status assessment
  isSubmitting: Boolean,       // Status submit
  error: String|Null            // Pesan error
}
```

**API yang Digunakan**: 
- `POST /api/assess-damage` - Penilaian AI
- `POST /api/reports` - Submit laporan

---

### EarlyWarning.jsx

**Lokasi**: `frontend/src/components/EarlyWarning.jsx`

**Deskripsi**: Komponen menampilkan peringatan dini dari BMKG.

**Fitur**:
- Daftar peringatan dini aktif
- Kategori peringatan (cuaca, banjir, dll)
- Tingkat severity
- Waktu berlaku
- Pembaruan otomatis

**API yang Digunakan**: `GET /api/early-warnings`

---

### EarthquakeAlert.jsx

**Lokasi**: `frontend/src/components/EarthquakeAlert.jsx`

**Deskripsi**: Komponen menampilkan informasi gempa bumi terkini.

**Fitur**:
- Info gempa terkini dari BMKG
- Magnitude dan lokasi
- Kedalaman
- Status tsunami
- Visualisasi pada peta

**API yang Digunakan**: 
- `GET /api/earthquake`
- `GET /api/earthquakes-felt`

---

### RiskAlert.jsx

**Lokasi**: `frontend/src/components/RiskAlert.jsx`

**Deskripsi**: Komponen menampilkan уровень risiko bencana untuk suatu lokasi.

**Fitur**:
- Tingkat risiko (Rendah, Sedang, Tinggi)
- Faktor risiko
- Rekomendasi tindakan
- Visualisasi peta risiko

**API yang Digunakan**: `GET /api/risk`

---

### LoadingSpinner.jsx

**Lokasi**: `frontend/src/components/LoadingSpinner.jsx`

**Deskripsi**: Komponen indikator loading sederhana.

**Props**:
- `size`: 'sm' | 'md' | 'lg' (default: 'md')
- `color`: String (default: 'blue')

---

### ErrorBoundary.jsx

**Lokasi**: `frontend/src/components/ErrorBoundary.jsx`

**Deskripsi**: React Error Boundary untuk menangani error pada komponen child.

**Fitur**:
- Tangkap error JavaScript
- Tampilkan pesan error yang ramah pengguna
- Opsi untuk retry

---

## Halaman Frontend

### Home.jsx

**Lokasi**: `frontend/src/pages/Home.jsx`

**Deskripsi**: Halaman landing utama aplikasi.

**Fitur**:
- Hero section dengan judul dan deskripsi
- Pilih lokasi kota
- Tombol ke dashboard
- Fitur utama:
  - Peringatan Dini
  - Peta Interaktif
  - Chatbot AI
  - Pelaporan Kerusakan
- Latest earthquake display

**Navigasi**:
- Button "Mulai Sekarang" → Dashboard
- Hash navigation untuk admin

---

### Dashboard.jsx

**Lokasi**: `frontend/src/pages/Dashboard.jsx`

**Deskripsi**: Halaman utama dengan peta interaktif dan semua fitur.

**Fitur**:
- Peta interaktif (Leaflet.js)
  - Risk zones visualization
  - Evacuation points markers
  - Damage reports markers
  - User location
- Control panel:
  - City selector
  - Filter options (all, evacuation, reports, risk)
  - Layer toggles
- Weather widget
- Risk assessment widget
- Early warnings panel
- Recent earthquakes
- Chatbot toggle
- Damage upload button

**State**:
```javascript
{
  map: Object,                    // Leaflet map instance
  reports: Array,                 // Damage reports
  evacuationPoints: Array,        // Evacuation points
  riskZones: Array,               // Risk zones data
  weatherData: Object,            // Weather information
  selectedFilter: String,         // Current filter
  currentCity: Object,            // Selected city
  userLocation: Object,           // User's geolocation
  loading: Boolean                // Loading state
}
```

**API yang Digunakan**:
- `/api/cities` - Daftar kota
- `/api/weather` - Data cuaca
- `/api/evacuation` - Titik evakuasi
- `/api/risk-zones` - Zona risiko
- `/api/reports` - Laporan kerusakan

---

### AdminLogin.jsx

**Lokasi**: `frontend/src/pages/AdminLogin.jsx`

**Deskripsi**: Halaman login untuk administrator.

**Fitur**:
- Form login dengan username dan password
- Validasi input
- Error handling
- Redirect ke admin dashboard setelah login

**API yang Digunakan**: `POST /api/admin/login`

---

### AdminDashboard.jsx

**Lokasi**: `frontend/src/pages/AdminDashboard.jsx`

**Deskripsi**: Dashboard untuk administrator mengelola laporan kerusakan.

**Fitur**:
- Statistics overview
  - Total reports
  - Approved reports
  - Rejected reports
  - Pending reports
- Reports table dengan:
  - Tanggal
  - Lokasi
  - Tingkat kerusakan
  - Status
  - Action buttons (Approve, Reject, Delete)
- Filter by status
- User management

**API yang Digunakan**:
- `GET /api/admin/stats` - Statistics
- `GET /api/admin/reports` - Reports list
- `POST /api/admin/reports/:id/approve` - Approve
- `POST /api/admin/reports/:id/reject` - Reject
- `DELETE /api/admin/reports/:id` - Delete
- `GET /api/admin/users` - User list

---

## Autentikasi & Otorisasi

### Google OAuth 2.0

**File**: `backend/auth.py`

**Flow**:
1. Frontend mengirim request ke `/api/auth/google` dengan Google ID token
2. Backend memverifikasi token dengan Google
3. Jika valid, buat atau update user di MongoDB
4. Generate JWT token untuk session
5. Return user data dan token

**Environment Variables Required**:
```
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
JWT_SECRET=your-jwt-secret
```

### JWT Token

**Token Structure**:
```json
{
  "user_id": "user-id-from-mongodb",
  "email": "user@gmail.com",
  "name": "User Name",
  "exp": 1715433600
}
```

**Token Verification**:
- Decode menggunakan `JWT_SECRET`
- Check expiration
- Return user data

### Admin Authentication

**File**: `backend/admin.py`

**Admin Login**:
- Username dan password didefinisikan di environment
- Default credentials (development):
  - Username: `siagaAI_admin`
  - Password: `siagaAI-admin-2024-secret`

**Protected Routes**:
- Menggunakan decorator `@admin_required`
- Check `Authorization` header dengan admin token

---

## Integrasi External API

### BMKG API

**Weather API**:
- URL: `https://api.bmkg.go.id/publik/prakiraan-cuaca`
- Endpoint: `?adm4={city_code}`
- Response: Weather forecast data

**Earthquake API**:
- URL: `https://data.bmkg.go.id/gempadirasakan.xml`
- Format: XML
- Parser: Python `xml.etree.ElementTree`

**Early Warnings API**:
- URL: `https://earlywarning.bmkg.go.id/api/v1/warning`
- Format: JSON

**City Codes**:
| Kota | Kode BMKG |
|------|-----------|
| Jakarta | 31.71.01.1001 |
| Surabaya | 31.78.01.1001 |
| Bandung | 32.73.01.1001 |
| Medan | 12.71.01.1001 |
| Semarang | 33.74.01.1001 |
| Makassar | 73.71.01.1001 |
| Palembang | 16.71.01.1001 |
| Tangerang | 36.73.01.1001 |
| Depok | 32.71.01.1004 |
| Bogor | 32.71.01.1001 |
| Yogyakarta | 34.74.01.1001 |
| Malang | 31.73.01.1007 |
| Solo | 33.71.01.1001 |
| Bekasi | 32.71.01.1002 |
| Denpasar | 51.71.01.1001 |
| Pontianak | 61.71.01.1001 |
| Banjarmasin | 63.71.01.1001 |
| Padang | 13.71.01.1001 |
| Pekanbaru | 14.71.01.1001 |

### Fallback Data

Jika BMKG API gagal, sistem menggunakan data simulasi yang realistis berdasarkan:
- Waktu hari ini (pola cuaca Indonesia)
- Lokasi kota
- Kondisi musim (data historis)

---

## Konfigurasi Environment

### Backend (.env)

```env
# Flask
FLASK_APP=app.py
FLASK_ENV=development

# MongoDB
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/siagaAI

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret

# JWT
JWT_SECRET=your-super-secret-jwt-key

# Admin
ADMIN_SECRET=siagaAI-admin-2024-secret
ADMIN_USERNAME=siagaAI_admin
ADMIN_PASSWORD=siagaAI-admin-2024-secret
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:5000
# Untuk production, gunakan URL backend yang sudah di-deploy
```

---

## Panduan Instalasi

### Prerequisites

- Node.js 18+
- Python 3.11+
- MongoDB Atlas account (atau MongoDB lokal)
- Google Cloud Console project (untuk OAuth)

### Backend Setup

```bash
# Navigate ke backend folder
cd siagaAI-web/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env
# Edit .env dengan konfigurasi Anda

# Run development server
python app.py
```

**Backend akan berjalan di**: `http://localhost:5000`

### Frontend Setup

```bash
# Navigate ke frontend folder
cd siagaAI-web/frontend

# Install dependencies
npm install

# Copy environment file
copy .env.example .env
# Edit .env dengan konfigurasi Anda

# Run development server
npm run dev
```

**Frontend akan berjalan di**: `http://localhost:5173`

---

## Fitur Utama

### 1. Sistem Peringatan Dini 🔔

- Data real-time dari BMKG
- Peringatan cuaca buruk
- Pembaruan otomatis setiap 30 detik
- Notifikasi push (jika diizinkan)

### 2. Peta Interaktif 🗺️

- Peta risiko bencana
- Titik evakuasi terdekat
- Laporan kerusakan visualisasi
- Pilih kota untuk info spesifik

### 3. Chatbot AI 🤖

- Asisten virtual evakuasi
- Pertolongan pertama
- Nomor darurat penting
- Respons cepat situasi darurat

### 4. Pelaporan Kerusakan 📸

- Upload foto kerusakan
- AI penilaian tingkat kerusakan
- Publik (tanpa login)
- Status tracking

### 5. Dashboard Admin 👤

- Kelola laporan kerusakan
- Approve/Reject laporan
- Statistik lengkap
- Manajemen user

---

## Troubleshooting

### Common Issues

**Weather API tidak berfungsi**:
- Check koneksi internet
- Verify BMKG API tidak sedang maintenance
- Cek log error di backend

**Google OAuth error**:
- Verify Google Client ID dan Secret benar
- Check redirect URI di Google Cloud Console
- Pastikan `email` scope sudah diaktifkan

**MongoDB connection error**:
- Verify MongoDB URI benar
- Check network/firewall settings
- Pastikan cluster sudah aktif

**CORS error**:
- Check CORS configuration di `app.py`
- Verify frontend API URL benar

---

## Lisensi

MIT License - SiagaAI Disaster Preparedness Platform

---

*Terakhir diperbarui: 2024*
*Dokumentasi ini dibuat untuk SiagaAI v1.0*
