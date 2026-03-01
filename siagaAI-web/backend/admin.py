"""
Modul API Admin - Endpoint untuk dashboard admin

Dokumentasi Bahasa Indonesia:
- Modul ini menyediakan endpoint-endpoint untuk administrasi
- Memerlukan X-Admin-Secret header untuk autentikasi
- Mengelola laporan kerusakan dan data user

Author: SiagaAI Team
Version: 1.0.0
"""

import os
import json
from functools import wraps
from flask import request, jsonify, g
from datetime import datetime
import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://editormxz_db_user:WQC796PGk7QfGylL@siagaai.m0pmtec.mongodb.net/?appName=siagaAI')
MONGODB_DB_NAME = 'siagaAI'

# Initialize MongoDB
# Konfigurasi MongoDB - hanya untuk reports
try:
    mongo_client = pymongo.MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=30000,
        connectTimeoutMS=30000,
        socketTimeoutMS=30000,
        retryWrites=True,
        retryReads=True
    )
    # Test connection
    mongo_client.admin.command('ping')
    db = mongo_client[MONGODB_DB_NAME]
    reports_collection = db.reports
    # CATATAN: users_collection dihapus - tidak ada sistem user
    users_collection = None
except Exception as e:
    print(f"Admin MongoDB connection error: {e}")
    mongo_client = None
    db = None
    reports_collection = None
    users_collection = None

# Admin secret (in production, use proper auth)
ADMIN_SECRET = os.getenv('ADMIN_SECRET', 'siagaAI-admin-2024-secret')

def admin_required(f):
    """
    Decorator untuk memproteksi endpoint admin.
    
    Usage:
        @app.route('/admin/protected')
        @admin_required
        def admin_protected_route():
            return jsonify({'message': 'Admin authorized'})
    
    Notes:
        - Memeriksa header X-Admin-Secret
        - SECRET didefinisikan di environment variable ADMIN_SECRET
        - Jika secret tidak cocok, mengembalikan 401 Unauthorized
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check admin secret header
        admin_secret = request.headers.get('X-Admin-Secret')
        
        if not admin_secret or admin_secret != ADMIN_SECRET:
            return jsonify({'error': 'Unauthorized'}), 401
        
        return f(*args, **kwargs)
    
    return decorated


def register_admin_routes(app):
    """
    Mendaftarkan route-route admin ke aplikasi Flask.
    
    Endpoint yang didaftarkan:
        - GET /api/admin/reports - Ambil semua laporan
        - POST /api/admin/reports/<id>/approve - Setuju laporan
        - POST /api/admin/reports/<id>/reject - Tolak laporan
        - DELETE /api/admin/reports/<id> - Hapus laporan
        - GET /api/admin/reports/<id> - Ambil satu laporan
        - GET /api/admin/users - Ambil semua user
        - GET /api/admin/stats - Ambil statistik keseluruhan
    
    Args:
        app: Instance aplikasi Flask
    """
    app
    
    @app.route('/api/admin/reports', methods=['GET'])
    @admin_required
    def get_admin_reports():
        """
        Mengambil semua laporan untuk admin.
        
        Query Parameters:
            status (str): Filter berdasarkan status (pending/approved/rejected/all)
        
        Returns:
            JSON: Dictionary dengan:
                  - reports: Daftar laporan
                  - pending_count: Jumlah laporan pending
                  - approved_count: Jumlah laporan disetujui
                  - rejected_count: Jumlah laporan ditolak
        
        Notes:
            - Memerlukan X-Admin-Secret header
            - Mengembalikan 100 laporan terbaru
        """
        # Check if database is connected
        if reports_collection is None:
            return jsonify({'error': 'Database not connected', 'reports': [], 'pending_count': 0, 'approved_count': 0, 'rejected_count': 0}), 200
        
        try:
            # Get filter from query params
            status = request.args.get('status')
            
            query = {}
            if status and status != 'all':
                query['status'] = status
            
            # Get reports - handle case where sort field might not exist
            try:
                reports = list(reports_collection.find(query).sort('created_at', -1).limit(100))
            except Exception as sort_error:
                # If sort fails, just get recent reports without sorting
                print(f"Sort error: {sort_error}")
                reports = list(reports_collection.find(query).limit(100))
            
            # Convert ObjectId to string
            for report in reports:
                report['_id'] = str(report['_id'])
            
            # Get counts
            try:
                pending_count = reports_collection.count_documents({'status': 'pending'})
                approved_count = reports_collection.count_documents({'status': 'approved'})
                rejected_count = reports_collection.count_documents({'status': 'rejected'})
            except:
                pending_count = 0
                approved_count = 0
                rejected_count = 0
            
            return jsonify({
                'reports': reports,
                'pending_count': pending_count,
                'approved_count': approved_count,
                'rejected_count': rejected_count
            }), 200
            
        except Exception as e:
            print(f"Admin reports error: {e}")
            return jsonify({'error': str(e), 'reports': [], 'pending_count': 0, 'approved_count': 0, 'rejected_count': 0}), 200
    
    @app.route('/api/admin/reports/<report_id>/approve', methods=['POST'])
    @admin_required
    def approve_report(report_id):
        """
        Menyetuju sebuah laporan.
        
        Args:
            report_id (str): ID laporan di MongoDB
        
        Returns:
            JSON: Success=True jika berhasil
            JSON: Error jika laporan tidak ditemukan
        
        Notes:
            - Mengubah status laporan menjadi 'approved'
            - Menambahkan timestamp updated_at
        """
        # Check database connection
        if reports_collection is None:
            return jsonify({'error': 'Database not connected'}), 500
        
        try:
            result = reports_collection.update_one(
                {'_id': ObjectId(report_id)},
                {'$set': {'status': 'approved', 'updated_at': datetime.utcnow()}}
            )
            
            if result.matched_count == 0:
                return jsonify({'error': 'Report not found'}), 404
            
            return jsonify({'success': True, 'message': 'Report approved'}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/reports/<report_id>/reject', methods=['POST'])
    @admin_required
    def reject_report(report_id):
        """
        Menolak sebuah laporan.
        
        Args:
            report_id (str): ID laporan di MongoDB
        
        Returns:
            JSON: Success=True jika berhasil
            JSON: Error jika laporan tidak ditemukan
        
        Notes:
            - Mengubah status laporan menjadi 'rejected'
            - Menambahkan timestamp updated_at
        """
        # Check database connection
        if reports_collection is None:
            return jsonify({'error': 'Database not connected'}), 500
        
        try:
            result = reports_collection.update_one(
                {'_id': ObjectId(report_id)},
                {'$set': {'status': 'rejected', 'updated_at': datetime.utcnow()}}
            )
            
            if result.matched_count == 0:
                return jsonify({'error': 'Report not found'}), 404
            
            return jsonify({'success': True, 'message': 'Report rejected'}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/reports/<report_id>', methods=['DELETE'])
    @admin_required
    def delete_report(report_id):
        """
        Menghapus sebuah laporan.
        
        Args:
            report_id (str): ID laporan di MongoDB
        
        Returns:
            JSON: Success=True jika berhasil dihapus
            JSON: Error jika laporan tidak ditemukan
        
        Notes:
            - Menghapus permanen laporan dari database
        """
        # Check database connection
        if reports_collection is None:
            return jsonify({'error': 'Database not connected'}), 500
        
        try:
            result = reports_collection.delete_one({'_id': ObjectId(report_id)})
            
            if result.deleted_count == 0:
                return jsonify({'error': 'Report not found'}), 404
            
            return jsonify({'success': True, 'message': 'Report deleted'}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/reports/<report_id>', methods=['GET'])
    @admin_required
    def get_report(report_id):
        """
        Mengambil satu laporan berdasarkan ID.
        
        Args:
            report_id (str): ID laporan di MongoDB
        
        Returns:
            JSON: Data laporan lengkap
            JSON: Error jika laporan tidak ditemukan
        """
        # Check database connection
        if reports_collection is None:
            return jsonify({'error': 'Database not connected'}), 500
        
        try:
            report = reports_collection.find_one({'_id': ObjectId(report_id)})
            
            if not report:
                return jsonify({'error': 'Report not found'}), 404
            
            report['_id'] = str(report['_id'])
            return jsonify({'report': report}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/users', methods=['GET'])
    @admin_required
    def get_users():
        """
        Mengambil semua user (tidak digunakan - hanya ada admin).
        
        Returns:
            JSON: Pesan bahwa tidak ada sistem user
        
        Notes:
            - Aplikasi ini tidak memiliki sistem user
            - Hanya admin yang bisa mengakses dashboard
        """
        # Tidak ada sistem user - hanya admin
        return jsonify({
            'users': [],
            'total_count': 0,
            'message': 'Tidak ada sistem user - hanya admin yang ada'
        }), 200
    
    @app.route('/api/admin/stats', methods=['GET'])
    @admin_required
    def get_admin_stats():
        """
        Mengambil statistik keseluruhan platform.
        
        Returns:
            JSON: Statistik meliputi:
                  - total_reports: Total semua laporan
                  - pending_reports: Laporan pending
                  - approved_reports: Laporan disetujui
                  - rejected_reports: Laporan ditolak
                  - total_users: Selalu 1 (hanya admin)
        
        Notes:
            - Berguna untuk dashboard admin
            - Memberikan gambaran umum aktivitas platform
        """
        # Check database connection
        if reports_collection is None:
            return jsonify({'error': 'Database not connected'}), 500
        
        try:
            total_reports = reports_collection.count_documents({})
            pending_reports = reports_collection.count_documents({'status': 'pending'})
            approved_reports = reports_collection.count_documents({'status': 'approved'})
            rejected_reports = reports_collection.count_documents({'status': 'rejected'})
            
            return jsonify({
                'total_reports': total_reports,
                'pending_reports': pending_reports,
                'approved_reports': approved_reports,
                'rejected_reports': rejected_reports,
                'total_users': 1  # Hanya admin
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    print("Admin routes registered: /api/admin/reports, /api/admin/users, /api/admin/stats")
