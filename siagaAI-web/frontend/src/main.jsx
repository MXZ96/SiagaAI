/**
 * File Utama (Entry Point) Aplikasi React SiagaAI
 * 
 * Dokumentasi Bahasa Indonesia:
 * - Titik awal aplikasi React
 * - Merender komponen App ke elemen DOM dengan id 'root'
 * - Menggunakan React StrictMode untuk pemeriksaan tambahan
 * 
 * Cara Kerja:
 * 1. Mengimpor React dan ReactDOM
 * 2. Mengimpor komponen utama App
 * 3. Mengimpor stylesheet global (index.css)
 * 4. Me-render aplikasi ke elemen root di index.html
 * 
 * Author: SiagaAI Team
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// Merender aplikasi React ke DOM
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
