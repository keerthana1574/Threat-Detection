from functools import wraps
from flask import request, jsonify, g
from config.firebase_admin import firebase_admin_instance
from config.database import db_manager

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401
        
        # Extract token
        try:
            token = auth_header.split(' ')[1]  # Remove 'Bearer ' prefix
        except IndexError:
            return jsonify({'error': 'Invalid authorization header format'}), 401
        
        # Verify token
        decoded_token = firebase_admin_instance.verify_token(token)
        
        if not decoded_token:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Get user from database
        cursor = db_manager.get_postgres_cursor()
        cursor.execute("SELECT * FROM users WHERE uid = %s", (decoded_token['uid'],))
        user = cursor.fetchone()
        
        if not user:
            # Create user if doesn't exist
            cursor.execute("""
                INSERT INTO users (uid, email, username) 
                VALUES (%s, %s, %s) 
                RETURNING *
            """, (decoded_token['uid'], decoded_token.get('email'), decoded_token.get('name')))
            user = cursor.fetchone()
        
        # Store user in request context
        g.current_user = user
        g.decoded_token = decoded_token
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_role(required_role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'current_user') or not g.current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            if g.current_user['role'] != required_role and g.current_user['role'] != 'admin':
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator