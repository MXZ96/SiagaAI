"""
Admin API Module - Admin dashboard endpoints
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
try:
    mongo_client = pymongo.MongoClient(
        MONGODB_URI,
        tls=True,
        tlsAllowInvalidCertificates=True,
        tlsDisableOCSPEndpointCheck=True,
        serverSelectionTimeoutMS=30000,
        connectTimeoutMS=30000
    )
    db = mongo_client[MONGODB_DB_NAME]
    reports_collection = db.reports
    users_collection = db.users
except Exception as e:
    print(f"Admin MongoDB connection error: {e}")
    mongo_client = None
    db = None
    reports_collection = None
    users_collection = None

# Admin secret (in production, use proper auth)
ADMIN_SECRET = os.getenv('ADMIN_SECRET', 'siagaAI-admin-2024-secret')

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check admin secret header
        admin_secret = request.headers.get('X-Admin-Secret')
        
        if not admin_secret or admin_secret != ADMIN_SECRET:
            return jsonify({'error': 'Unauthorized'}), 401
        
        return f(*args, **kwargs)
    
    return decorated


def register_admin_routes(app):
    """Register admin routes with Flask app"""
    
    @app.route('/api/admin/reports', methods=['GET'])
    @admin_required
    def get_admin_reports():
        """Get all reports for admin"""
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
        """Approve a report"""
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
        """Reject a report"""
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
        """Delete a report"""
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
        """Get a single report by ID"""
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
        """Get all users (admin only)"""
        if users_collection is None:
            return jsonify({'error': 'Database not connected'}), 500
        
        try:
            users = list(users_collection.find({}, {'google_id': 0}).sort('created_at', -1).limit(100))
            
            # Convert ObjectId to string
            for user in users:
                user['_id'] = str(user['_id'])
            
            total_users = users_collection.count_documents({})
            
            return jsonify({
                'users': users,
                'total_count': total_users
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/stats', methods=['GET'])
    @admin_required
    def get_admin_stats():
        """Get overall statistics"""
        if reports_collection is None or users_collection is None:
            return jsonify({'error': 'Database not connected'}), 500
        
        try:
            total_reports = reports_collection.count_documents({})
            pending_reports = reports_collection.count_documents({'status': 'pending'})
            approved_reports = reports_collection.count_documents({'status': 'approved'})
            rejected_reports = reports_collection.count_documents({'status': 'rejected'})
            total_users = users_collection.count_documents({})
            
            return jsonify({
                'total_reports': total_reports,
                'pending_reports': pending_reports,
                'approved_reports': approved_reports,
                'rejected_reports': rejected_reports,
                'total_users': total_users
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    print("Admin routes registered: /api/admin/reports, /api/admin/users, /api/admin/stats")
