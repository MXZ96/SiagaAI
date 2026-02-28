"""
Google OAuth 2.0 Authentication Module
Handles Google token verification and user management with MongoDB
"""

import os
import jwt
import datetime
from functools import wraps
from flask import request, jsonify, g
from dotenv import load_dotenv
from google.oauth2 import id_token
from google.auth.transport import requests
import pymongo
from bson.objectid import ObjectId

load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://editormxz_db_user:<db_password>@siagaai.m0pmtec.mongodb.net/?appName=siagaAI')
MONGODB_DB_NAME = 'siagaAI'
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
JWT_SECRET = os.getenv('JWT_SECRET', '6d3f17cb6d5d7ce136b28ca95dfb3772ff54023261ce1ad65029b36e684bbc71')

# Initialize MongoDB client
try:
    mongo_client = pymongo.MongoClient(MONGODB_URI)
    db = mongo_client[MONGODB_DB_NAME]
    users_collection = db.users
    reports_collection = db.reports
    
    # Create indexes
    users_collection.create_index('email', unique=True)
    users_collection.create_index('google_id', unique=True)
    print("MongoDB connected successfully")
except Exception as e:
    print(f"MongoDB connection error: {e}")
    mongo_client = None
    db = None
    users_collection = None
    reports_collection = None


def generate_token(user_id, email, name):
    """Generate JWT token for authenticated user"""
    payload = {
        'user_id': str(user_id),
        'email': email,
        'name': name,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def decode_token(token):
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """Decorator to require valid JWT token"""
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
        
        # Store user info in g object
        g.user_id = payload['user_id']
        g.user_email = payload['email']
        g.user_name = payload['name']
        
        return f(*args, **kwargs)
    
    return decorated


def verify_google_token(google_token):
    """
    Verify Google OAuth token and return user info
    Returns: (success: bool, user_info: dict or error_message: str)
    """
    if not GOOGLE_CLIENT_ID:
        return False, "Google Client ID not configured"
    
    try:
        # Specify the CLIENT_ID of the app that accesses the backend
        idinfo = id_token.verify_oauth2_token(
            google_token, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        # ID token is valid
        # Get required user info
        user_info = {
            'google_id': idinfo['sub'],
            'email': idinfo['email'],
            'name': idinfo.get('name', ''),
            'picture': idinfo.get('picture', ''),
            'verified_email': idinfo.get('email_verified', False)
        }
        
        return True, user_info
        
    except ValueError as e:
        # Invalid token
        return False, f"Invalid token: {str(e)}"
    except Exception as e:
        return False, f"Token verification failed: {str(e)}"


def get_or_create_user(user_info):
    """
    Get existing user or create new one
    One Gmail = One account (prevent duplicates by email/google_id)
    """
    if users_collection is None:
        return None, "Database not connected"
    
    try:
        # Check if user exists by google_id or email
        existing_user = users_collection.find_one({
            '$or': [
                {'google_id': user_info['google_id']},
                {'email': user_info['email']}
            ]
        })
        
        if existing_user:
            # Update user info
            users_collection.update_one(
                {'_id': existing_user['_id']},
                {
                    '$set': {
                        'name': user_info['name'],
                        'picture': user_info['picture'],
                        'last_login': datetime.datetime.utcnow()
                    }
                }
            )
            return existing_user, None
        
        # Create new user
        new_user = {
            'google_id': user_info['google_id'],
            'email': user_info['email'],
            'name': user_info['name'],
            'picture': user_info['picture'],
            'verified_email': user_info['verified_email'],
            'created_at': datetime.datetime.utcnow(),
            'last_login': datetime.datetime.utcnow(),
            'role': 'user',  # Default role
            'reports_count': 0
        }
        
        result = users_collection.insert_one(new_user)
        new_user['_id'] = result.inserted_id
        
        return new_user, None
        
    except pymongo.errors.PyMongoError as e:
        return None, f"Database error: {str(e)}"


def get_user_by_id(user_id):
    """Get user by ID (exclude sensitive data)"""
    if users_collection is None:
        return None
    
    try:
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if user:
            # Remove sensitive data
            user.pop('google_id', None)
            user['_id'] = str(user['_id'])
        return user
    except Exception:
        return None


def update_user_reports_count(user_id, increment=1):
    """Update user's reports count"""
    if users_collection is None:
        return False
    
    try:
        users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$inc': {'reports_count': increment}}
        )
        return True
    except Exception:
        return False


# ==================== API ROUTES ====================

def register_auth_routes(app):
    """Register authentication routes with Flask app"""
    
    @app.route('/api/auth/google', methods=['POST'])
    def google_login():
        """
        Google OAuth Login Endpoint
        Request: { "credential": "google_id_token" }
        Response: { "token": "jwt_token", "user": { ... } }
        """
        data = request.get_json()
        
        if not data or 'credential' not in data:
            return jsonify({'error': 'Google credential is required'}), 400
        
        google_token = data['credential']
        
        # Verify Google token
        success, result = verify_google_token(google_token)
        
        if not success:
            return jsonify({'error': result}), 401
        
        user_info = result
        
        # Check if email is verified
        if not user_info.get('verified_email', False):
            return jsonify({'error': 'Email not verified with Google'}), 401
        
        # Get or create user in database
        user, error = get_or_create_user(user_info)
        
        if error:
            return jsonify({'error': error}), 500
        
        if not user:
            return jsonify({'error': 'Failed to create user'}), 500
        
        # Generate JWT token
        token = generate_token(
            user['_id'], 
            user['email'], 
            user['name']
        )
        
        # Return user info (exclude sensitive data)
        user_data = {
            'id': str(user['_id']),
            'email': user['email'],
            'name': user['name'],
            'picture': user.get('picture', ''),
            'role': user.get('role', 'user'),
            'reports_count': user.get('reports_count', 0),
            'created_at': user.get('created_at', '').isoformat() if user.get('created_at') else None
        }
        
        return jsonify({
            'token': token,
            'user': user_data
        }), 200
    
    @app.route('/api/auth/me', methods=['GET'])
    @token_required
    def get_current_user():
        """Get current authenticated user"""
        user = get_user_by_id(g.user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user}), 200
    
    @app.route('/api/auth/logout', methods=['POST'])
    @token_required
    def logout():
        """Logout endpoint (client should remove token)"""
        return jsonify({'message': 'Logged out successfully'}), 200
    
    @app.route('/api/auth/verify', methods=['POST'])
    def verify_token():
        """
        Verify JWT token
        Request: { "token": "jwt_token" }
        Response: { "valid": bool, "user": { ... } }
        """
        data = request.get_json()
        
        if not data or 'token' not in data:
            return jsonify({'error': 'Token is required'}), 400
        
        token = data['token']
        payload = decode_token(token)
        
        if not payload:
            return jsonify({'valid': False, 'error': 'Invalid or expired token'}), 401
        
        # Get user from database
        user = get_user_by_id(payload['user_id'])
        
        if not user:
            return jsonify({'valid': False, 'error': 'User not found'}), 404
        
        return jsonify({
            'valid': True,
            'user': user
        }), 200
    
    print("Auth routes registered: /api/auth/google, /api/auth/me, /api/auth/verify, /api/auth/logout")
