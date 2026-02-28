/**
 * UserLogin - User login page with Google OAuth
 * Required for submitting damage reports
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

// Google OAuth Client ID (should be set in .env)
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';

export default function UserLogin({ onNavigate }) {
  const { loginWithGoogle, isAuthenticated, loading, error } = useAuth();
  
  const [googleLoading, setGoogleLoading] = useState(false);
  
  // Redirect if already logged in
  useEffect(() => {
    if (isAuthenticated && !loading && onNavigate) {
      onNavigate('home');
    }
  }, [isAuthenticated, loading, onNavigate]);

  // Initialize Google Identity Services
  useEffect(() => {
    if (!GOOGLE_CLIENT_ID) {
      console.warn('Google Client ID not configured');
      return;
    }

    // Load Google Identity Services script
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    script.onload = initializeGoogleButton;
    document.body.appendChild(script);

    return () => {
      // Cleanup
      const existingScript = document.body.querySelector('script[src="https://accounts.google.com/gsi/client"]');
      if (existingScript) {
        document.body.removeChild(existingScript);
      }
    };
  }, []);

  const initializeGoogleButton = () => {
    if (window.google) {
      window.google.accounts.oauth2.initTokenClient({
        client_id: GOOGLE_CLIENT_ID,
        scope: 'profile email openid',
        callback: handleCredentialResponse,
      });
    }
  };

  const handleCredentialResponse = async (response) => {
    if (response.access_token) {
      const idToken = response.credential;
      
      if (idToken) {
        setGoogleLoading(true);
        console.log('Sending credential to backend...');
        const result = await loginWithGoogle(idToken);
        console.log('Login result:', result);
        setGoogleLoading(false);
        
        console.log('Result success:', result?.success, 'onNavigate:', typeof onNavigate);
        if (result?.success) {
          if (onNavigate) {
            onNavigate('home');
          } else {
            // Fallback: use window.location
            window.location.href = '/#/home';
          }
        } else {
          console.error('Login failed:', result?.error);
        }
      }
    }
  };

  const handleManualGoogleLogin = () => {
    if (!GOOGLE_CLIENT_ID) {
      alert('Google Client ID belum dikonfigurasi. Silakan hubungi administrator.');
      return;
    }

    // Fallback: Use the older Google Identity Services
    if (window.google?.accounts?.id) {
      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleCredentialResponse,
        auto_select: false,
        cancel_on_tap_outside: false,
      });
      
      window.google.accounts.id.prompt((notification) => {
        if (notification.isNotDisplayed()) {
          console.log('Google prompt not displayed:', notification);
        }
      });
    } else {
      alert('Layanan Google tidak tersedia. Silakan coba lagi.');
    }
  };

  const handleBack = () => {
    if (onNavigate) {
      onNavigate('home');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-cyan-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Memuat...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-cyan-50 px-4">
      <div className="max-w-md w-full">
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-blue-600 to-cyan-500 mb-4">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">SiagaAI</h1>
          <p className="text-gray-600">Masuk untuk mengirim laporan kerusakan</p>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}

          {/* Info Box */}
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start">
              <svg className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="text-sm text-blue-800 font-medium">Mengapa harus login?</p>
                <p className="text-xs text-blue-600 mt-1">
                  Login diperlukan untuk mengirim laporan kerusakan bencana. 
                  Satu akun Gmail hanya bisa membuat satu akun pengguna.
                </p>
              </div>
            </div>
          </div>

          {/* Google Login Button */}
          <button
            onClick={handleManualGoogleLogin}
            disabled={googleLoading}
            className="w-full flex items-center justify-center px-4 py-3 bg-white border-2 border-gray-300 rounded-lg hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {googleLoading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-600"></div>
            ) : (
              <>
                <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                <span className="text-gray-700 font-medium">Masuk dengan Google</span>
              </>
            )}
          </button>

          {/* Terms */}
          <p className="text-xs text-gray-500 text-center mt-6">
            Dengan masuk, Anda menyetujui 
            <a href="#" className="text-blue-600 hover:underline"> Kebijakan Privasi</a> 
            {' '}dan{' '}
            <a href="#" className="text-blue-600 hover:underline">Ketentuan Layanan</a>
          </p>
        </div>

        {/* Back to Home */}
        <div className="text-center mt-6">
          <button
            onClick={handleBack}
            className="text-gray-600 hover:text-gray-900 text-sm flex items-center justify-center mx-auto"
          >
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Kembali ke Beranda
          </button>
        </div>
      </div>
    </div>
  );
}
