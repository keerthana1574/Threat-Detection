from flask import Blueprint, request, jsonify
from flask_socketio import emit
from middleware.auth_middleware import require_auth
from monitors.social_media_monitor import social_media_monitor
from monitors.network_monitor import network_monitor
from monitors.web_security_monitor import web_security_monitor

realtime_bp = Blueprint('realtime', __name__)

@realtime_bp.route('/social-media/start', methods=['POST'])
@require_auth
def start_social_media_monitoring():
    """Start social media monitoring"""
    try:
        data = request.get_json() or {}
        keywords = data.get('keywords')
        users = data.get('users_to_monitor')
        
        result = social_media_monitor.start_monitoring(keywords, users)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@realtime_bp.route('/social-media/stop', methods=['POST'])
@require_auth
def stop_social_media_monitoring():
    """Stop social media monitoring"""
    try:
        result = social_media_monitor.stop_monitoring()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@realtime_bp.route('/social-media/status', methods=['GET'])
@require_auth
def get_social_media_status():
    """Get social media monitoring status"""
    try:
        status = social_media_monitor.get_monitoring_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@realtime_bp.route('/network/start', methods=['POST'])
@require_auth
def start_network_monitoring():
    """Start network monitoring"""
    try:
        data = request.get_json() or {}
        interface = data.get('interface')
        
        result = network_monitor.start_monitoring(interface)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@realtime_bp.route('/network/stop', methods=['POST'])
@require_auth
def stop_network_monitoring():
    """Stop network monitoring"""
    try:
        result = network_monitor.stop_monitoring()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@realtime_bp.route('/network/status', methods=['GET'])
@require_auth
def get_network_status():
    """Get network monitoring status"""
    try:
        status = network_monitor.get_monitoring_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@realtime_bp.route('/web-security/add-endpoint', methods=['POST'])
@require_auth
def add_web_endpoint():
    """Add endpoint for web security monitoring"""
    try:
        data = request.get_json()
        url = data.get('url')
        method = data.get('method', 'GET')
        headers = data.get('headers', {})
        
        result = web_security_monitor.add_endpoint(url, method, headers)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@realtime_bp.route('/web-security/start', methods=['POST'])
@require_auth
def start_web_security_monitoring():
    """Start web security monitoring"""
    try:
        result = web_security_monitor.start_monitoring()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@realtime_bp.route('/web-security/stop', methods=['POST'])
@require_auth
def stop_web_security_monitoring():
    """Stop web security monitoring"""
    try:
        result = web_security_monitor.stop_monitoring()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@realtime_bp.route('/web-security/status', methods=['GET'])
@require_auth
def get_web_security_status():
    """Get web security monitoring status"""
    try:
        status = web_security_monitor.get_monitoring_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500