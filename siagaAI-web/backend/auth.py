"""
Modul Autentikasi Admin Saja - Tanpa User Login
CATATAN: Aplikasi ini hanya untuk admin, tidak ada sistem login user.

Dokumentasi Bahasa Indonesia:
- Sistem autentikasi sederhana hanya untuk admin
- Menggunakan secret key untuk proteksi API admin
- TIDAK ada database user
- TIDAK ada Google OAuth

Author: SiagaAI Team
Version: 1.0.0
"""

import os
import jwt
import datetime
from functools import wraps
from flask import request, jsonify
from dotenv import load_dotenv

load_dotenv()

# Konfigurasi Admin
ADMIN_SECRET = os.getenv('ADMIN_SECRET', 'siagaAI-admin-2024-secret')
JWT_SECRET = os.getenv('JWT_SECRET', '6d3f17cb6d5d7ce136b28ca95dfb3772ff54023261ce1ad65029b36e684bbc71')


def generate_token(username):
    """
    Membuat token JWT sederhana untuk admin.
    
    Args:
        username (str): Nama admin
        
    Returns:
        str: Token JWT yang sudah di-encode
    """
    payload = {
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def decode_token(token):
    """
    Mem-verify dan mendekode token JWT.
    
    Args:
        token (str): Token JWT yang akan didecode
        
    Returns:
        dict: Payload token jika valid, None jika expired/invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """
    Decorator untuk memproteksi endpoint yang memerlukan autentikasi admin.
    
    Usage:
        @app.route('/protected')
        @token_required
        def protected_route():
            return jsonify({'message': 'Authorized'})
    
    Notes:
        - Memeriksa header Authorization
        - Format: "Authorization: Bearer <token>"
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        return f(*args, **kwargs)
    
    return decorated


# ==================== API ROUTES ====================

def register_auth_routes(app):
    """
    Mendaftarkan route-route autentikasi ke aplikasi Flask.
    
    Endpoint yang didaftarkan:
        - POST /api/auth/admin-login - Login admin saja
        - POST /api/auth/logout - Logout admin
        - POST /api/auth/verify - Verifikasi token admin
    
    Args:
        app: Instance aplikasi Flask
    """
    
    @app.route('/api/auth/google', methods=['POST'])
    def google_login():
        """
        Endpoint Login Admin (menggunakan credentials sederhana).
        CATATAN: Sebelumnya menggunakan Google OAuth, sekarang hanya admin static.
        
        Request Body:
            JSON dengan fields:
            - username (str): Username admin
            - password (str): Password admin
            
        Returns:
            JSON: Token JWT dan data admin jika berhasil
            JSON: Error message jika gagal
            
        Notes:
            - Hanya admin yang sudah dikonfigurasi di environment yang bisa login
            - Untuk keamanan, gunakan ADMIN_SECRET yang kuat di environment
        """
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Username and password are required'}), 400
        
        username = data['username']
        password = data['password']
        
        # Verifikasi credentials admin (bisa dikonfigurasi di environment)
        admin_user = os.getenv('ADMIN_USERNAME', 'admin')
        admin_pass = os.getenv('ADMIN_PASSWORD', 'siagaAI2024')
        
        if username == admin_user and password == admin_pass:
            token = generate_token(username)
            return jsonify({
                'token': token,
                'user': {
                    'username': username,
                    'role': 'admin'
                }
            }), 200
        
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    
    @app.route('/api/auth/me', methods=['GET'])
    @token_required
    def get_current_user():
        """
        Mengambil data admin yang sedang login.
        
        Returns:
            JSON: Data admin
            JSON: Error jika token invalid
        """
        return jsonify({'user': {'role': 'admin'}}), 200
    
    @app.route('/api/auth/logout', methods=['POST'])
    @token_required
    def logout():
        """
        Endpoint logout.
        
        Returns:
            JSON: Pesan sukses
            
        Notes:
            - Client harus menghapus token dari local storage
            - Server tidak menyimpan state token (stateless)
        """
        return jsonify({'message': 'Logged out successfully'}), 200
    
    @app.route('/api/auth/verify', methods=['POST'])
    def verify_token():
        """
        Memverifikasi validitas token JWT.
        
        Request Body:
            JSON dengan field:
            - token (str): Token JWT yang akan diverifikasi
            
        Returns:
            JSON: valid=True jika token valid
            JSON: valid=False jika token invalid/expired
            
        Notes:
            - Tidak memerlukan autentikasi (bisa dipanggil tanpa token)
        """
        data = request.get_json()
        
        if not data or 'token' not in data:
            return jsonify({'error': 'Token is required'}), 400
        
        token = data['token']
        payload = decode_token(token)
        
        if not payload:
            return jsonify({'valid': False, 'error': 'Invalid or expired token'}), 401
        
        return jsonify({
            'valid': True,
            'user': {'username': payload.get('username'), 'role': 'admin'}
        }), 200
    
    print("Auth routes registered: /api/auth/google (admin only), /api/auth/me, /api/auth/verify, /api/auth/logout")

