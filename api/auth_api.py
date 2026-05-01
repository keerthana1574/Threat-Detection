from flask import Blueprint, request, jsonify, g
from middleware.auth_middleware import require_auth
from config.database import db_manager

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get user profile"""
    try:
        return jsonify({
            'success': True,
            'user': dict(g.current_user)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@require_auth
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        
        cursor = db_manager.get_postgres_cursor()
        cursor.execute("""
            UPDATE users 
            SET username = %s, last_login = CURRENT_TIMESTAMP
            WHERE uid = %s
            RETURNING *
        """, (data.get('username'), g.current_user['uid']))
        
        updated_user = cursor.fetchone()
        
        return jsonify({
            'success': True,
            'user': dict(updated_user)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/users', methods=['GET'])
@require_auth
def get_all_users():
    """Get all users (admin only)"""
    try:
        if g.current_user['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        cursor = db_manager.get_postgres_cursor()
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'users': [dict(user) for user in users]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500