from flask import Blueprint, request, jsonify
from backend.modules.network_security.monitor import RealTimeNetworkMonitor
import threading

network_security_bp = Blueprint('network_security', __name__)

# Initialize network monitor
model_dir = 'backend/models/network_security'
monitor = RealTimeNetworkMonitor(model_dir)

# Global monitoring state
monitoring_thread = None

@network_security_bp.route('/start_monitoring', methods=['POST'])
def start_monitoring():
    """Start network monitoring"""
    try:
        global monitoring_thread
        
        if monitor.monitoring:
            return jsonify({'message': 'Monitoring already active'}), 200
        
        # Start monitoring in background thread
        monitoring_thread = threading.Thread(target=monitor.start_monitoring)
        monitoring_thread.daemon = True
        monitoring_thread.start()
        
        return jsonify({'message': 'Network monitoring started successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@network_security_bp.route('/stop_monitoring', methods=['POST'])
def stop_monitoring():
    """Stop network monitoring"""
    try:
        monitor.stop_monitoring()
        return jsonify({'message': 'Network monitoring stopped successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@network_security_bp.route('/status', methods=['GET'])
def get_status():
    """Get current monitoring status"""
    try:
        status = monitor.get_current_status()
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@network_security_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get security alerts"""
    try:
        severity = request.args.get('severity')
        acknowledged = request.args.get('acknowledged')
        limit = int(request.args.get('limit', 100))
        
        if acknowledged is not None:
            acknowledged = acknowledged.lower() == 'true'
        
        alerts = monitor.get_alerts(severity=severity, acknowledged=acknowledged, limit=limit)
        
        return jsonify({
            'alerts': alerts,
            'total': len(alerts)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@network_security_bp.route('/alerts/<int:alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """Acknowledge a security alert"""
    try:
        success = monitor.acknowledge_alert(alert_id)
        
        if success:
            return jsonify({'message': 'Alert acknowledged successfully'})
        else:
            return jsonify({'error': 'Alert not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@network_security_bp.route('/network_stats', methods=['GET'])
def get_network_stats():
    """Get current network statistics"""
    try:
        stats = monitor.traffic_analyzer.get_network_statistics()
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@network_security_bp.route('/system_resources', methods=['GET'])
def get_system_resources():
    """Get current system resource usage"""
    try:
        if monitor.resource_monitor.resource_data:
            latest_data = monitor.resource_monitor.resource_data[-1]
            return jsonify(latest_data)
        else:
            return jsonify({'message': 'No resource data available'})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@network_security_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'monitoring_active': monitor.monitoring,
        'models_loaded': bool(monitor.anomaly_detector.models)
    })