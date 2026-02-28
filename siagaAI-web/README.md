# SiagaAI - Platform Kesiapsiagaan Bencana Indonesia

SiagaAI adalah platform informasi dan kesiapsiagaan bencana untuk masyarakat Indonesia. Platform ini menyediakan berbagai fitur untuk membantu warga dalam menghadapi potensi bencana alam seperti banjir, tanah longsor, dan gempa bumi.

## Fitur Utama

### 🔔 Sistem Peringatan Dini
- Data real-time dari BMKG (Badan Meteorologi, Klimatologi, dan Geofisika)
- Peringatan dini cuaca buruk
- Informasi Gempa bumi terkini
- Pembaruan otomatis setiap 30 detik

### 🗺️ Peta Interaktif
- Peta risiko bencana berdasarkan lokasi
- Titik-titik evakuasi terdekat
- Visualisasi laporan kerusakan
- Pilih kota untuk melihat informasi spesifik

### 🤖 Chatbot AI
- Asisten virtual untuk panduan evakuasi
- Informasi pertolongan pertama
- Nomor darurat penting (BNPB, PMI, Ambulans)
- Respons cepat untuk situasi darurat

### 📸 Pelaporan Kerusakan
- Unggah foto kerusakan akibat bencana
- AI untuk penilaian tingkat kerusakan
- Sistem login dengan Google untuk validasi pelapor

### 👤 Autentikasi
- Login dengan Google (OAuth 2.0)
- Satu akun Gmail per pengguna
- Data tersimpan di MongoDB Atlas

## Teknologi

### Frontend
- React.js
- Tailwind CSS
- Leaflet.js (Peta)
- TensorFlow.js (AI Damage Assessment)

### Backend
- Flask (Python)
- MongoDB Atlas (Database)
- JWT (Session Management)

### APIs
- BMKG Cuaca
- BMKG Gempa Bumi
- BMKG Peringatan Dini Cuaca

## Mulai Menggunakan

### Backend
```bash
cd siagaAI-web/backend
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd siagaAI-web/frontend
npm install
npm run dev
```

## Struktur Project

```
siagaAI-web/
├── API/                    # Referensi API BMKG
├── backend/
│   ├── app.py            # Flask API
│   ├── auth.py          # Google OAuth
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/  # Komponen React
│   │   ├── context/     # Auth Context
│   │   ├── pages/      # Halaman
│   │   └── utils/      # Utilities
│   └── package.json
├── DEPLOYMENT.md        # Panduan Deploy
└── README.md
```

## Lisensi

MIT License - SiagaAI Disaster Preparedness Platform
