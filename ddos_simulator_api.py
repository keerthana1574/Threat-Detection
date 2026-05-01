# backend/api/ddos_simulator_api.py

from flask import Blueprint, request, jsonify
from backend.modules.network_security.ddos_simulator import DDoSAttackSimulator
from backend.modules.network_security.nsl_detector import NSLNetworkDetector
import threading
import time

ddos_simulator_bp = Blueprint('ddos_simulator', __name__)

# Initialize simulator and detector
simulator = DDoSAttackSimulator()
detector = NSLNetworkDetector('backend/models/network_security')

# Global state
simulation_state = {
    'active': False,
    'attack_type': None,
    'start_time': None
}

@ddos_simulator_bp.route('/start_simulation', methods=['POST'])
def start_simulation():
    """Start DDoS attack simulation"""
    try:
        data = request.get_json()
        attack_type = data.get('attack_type', 'syn_flood')
        intensity = data.get('intensity', 'medium')
        duration = data.get('duration', 60)
        
        # Validate attack type
        valid_attacks = ['syn_flood', 'udp_flood', 'http_flood', 'icmp_flood', 'slowloris', 'amplification']
        if attack_type not in valid_attacks:
            return jsonify({'error': f'Invalid attack type. Must be one of: {valid_attacks}'}), 400
        
        # Validate intensity
        valid_intensities = ['low', 'medium', 'high', 'critical']
        if intensity not in valid_intensities:
            return jsonify({'error': f'Invalid intensity. Must be one of: {valid_intensities}'}), 400
        
        # Start simulation
        result = simulator.start_attack(attack_type, intensity, duration)
        
        simulation_state['active'] = True
        simulation_state['attack_type'] = attack_type
        simulation_state['start_time'] = time.time()
        
        return jsonify({
            'status': 'success',
            'message': 'DDoS simulation started',
            'simulation': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ddos_simulator_bp.route('/stop_simulation', methods=['POST'])
def stop_simulation():
    """Stop DDoS attack simulation"""
    try:
        result = simulator.stop_attack()
        
        simulation_state['active'] = False
        simulation_state['attack_type'] = None
        simulation_state['start_time'] = None
        
        return jsonify({
            'status': 'success',
            'message': 'DDoS simulation stopped',
            'result': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ddos_simulator_bp.route('/status', methods=['GET'])
def get_status():
    """Get current simulation status"""
    try:
        stats = simulator.get_attack_statistics()
        
        # Add simulation state info
        stats['simulation_state'] = simulation_state
        
        if simulation_state['start_time']:
            stats['elapsed_time'] = int(time.time() - simulation_state['start_time'])
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ddos_simulator_bp.route('/visualization_data', methods=['GET'])
def get_visualization_data():
    """Get data formatted for visualization"""
    try:
        last_n_seconds = int(request.args.get('seconds', 10))
        data = simulator.get_live_visualization_data(last_n_seconds)
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ddos_simulator_bp.route('/detection_metrics', methods=['GET'])
def get_detection_metrics():
    """Get ML detection performance metrics"""
    try:
        if not simulator.attack_traffic and not simulator.legitimate_traffic:
            return jsonify({
                'status': 'no_data',
                'message': 'No traffic data available. Start a simulation first.'
            })
        
        # Analyze traffic with ML model
        metrics = simulator.analyze_with_ml_model(detector)
        
        return jsonify({
            'status': 'success',
            'metrics': metrics,
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ddos_simulator_bp.route('/attack_types', methods=['GET'])
def get_attack_types():
    """Get available attack types and their descriptions"""
    attack_types = [
        {
            'id': 'syn_flood',
            'name': 'SYN Flood Attack',
            'description': 'Exploits TCP three-way handshake by sending numerous SYN requests',
            'severity': 'high',
            'typical_pps': '1000-10000',
            'detection_difficulty': 'medium'
        },
        {
            'id': 'udp_flood',
            'name': 'UDP Flood Attack',
            'description': 'Overwhelms target with UDP packets on random ports',
            'severity': 'high',
            'typical_pps': '5000-50000',
            'detection_difficulty': 'medium'
        },
        {
            'id': 'http_flood',
            'name': 'HTTP Flood Attack',
            'description': 'Application layer attack using HTTP GET/POST requests',
            'severity': 'medium',
            'typical_pps': '100-1000',
            'detection_difficulty': 'hard'
        },
        {
            'id': 'icmp_flood',
            'name': 'ICMP Flood (Ping Flood)',
            'description': 'Floods target with ICMP Echo Request packets',
            'severity': 'medium',
            'typical_pps': '1000-5000',
            'detection_difficulty': 'easy'
        },
        {
            'id': 'slowloris',
            'name': 'Slowloris Attack',
            'description': 'Keeps many HTTP connections open with slow, partial requests',
            'severity': 'critical',
            'typical_pps': '10-100',
            'detection_difficulty': 'hard'
        },
        {
            'id': 'amplification',
            'name': 'DNS/NTP Amplification',
            'description': 'Reflection attack using DNS or NTP servers to amplify traffic',
            'severity': 'critical',
            'typical_pps': '10000-100000',
            'detection_difficulty': 'medium'
        }
    ]
    
    return jsonify({
        'attack_types': attack_types,
        'total': len(attack_types)
    })

@ddos_simulator_bp.route('/intensity_levels', methods=['GET'])
def get_intensity_levels():
    """Get available intensity levels"""
    intensities = [
        {
            'level': 'low',
            'packets_per_second': 100,
            'source_ips': 10,
            'description': 'Low-intensity attack, easy to detect and mitigate',
            'use_case': 'Testing basic detection capabilities'
        },
        {
            'level': 'medium',
            'packets_per_second': 500,
            'source_ips': 50,
            'description': 'Medium-intensity attack, moderate challenge',
            'use_case': 'Standard penetration testing'
        },
        {
            'level': 'high',
            'packets_per_second': 1000,
            'source_ips': 100,
            'description': 'High-intensity attack, significant threat',
            'use_case': 'Stress testing infrastructure'
        },
        {
            'level': 'critical',
            'packets_per_second': 5000,
            'source_ips': 500,
            'description': 'Critical-level attack, severe threat',
            'use_case': 'Testing maximum defense capabilities'
        }
    ]
    
    return jsonify({
        'intensity_levels': intensities,
        'total': len(intensities)
    })

@ddos_simulator_bp.route('/recent_packets', methods=['GET'])
def get_recent_packets():
    """Get recent attack and legitimate packets"""
    try:
        limit = int(request.args.get('limit', 20))
        
        recent_attack = simulator.attack_traffic[-limit:] if simulator.attack_traffic else []
        recent_legit = simulator.legitimate_traffic[-limit:] if simulator.legitimate_traffic else []
        
        # Format for display
        formatted_attack = []
        for packet in recent_attack:
            formatted_attack.append({
                'timestamp': packet['timestamp'].strftime('%H:%M:%S.%f')[:-3],
                'type': packet.get('attack_type', 'Unknown'),
                'src': f"{packet['src_ip']}:{packet['src_port']}",
                'dst': f"{packet['dst_ip']}:{packet['dst_port']}",
                'protocol': packet['protocol'],
                'size': packet['packet_size'],
                'is_attack': True
            })
        
        formatted_legit = []
        for packet in recent_legit:
            formatted_legit.append({
                'timestamp': packet['timestamp'].strftime('%H:%M:%S.%f')[:-3],
                'type': 'Legitimate',
                'src': f"{packet['src_ip']}:{packet['src_port']}",
                'dst': f"{packet['dst_ip']}:{packet['dst_port']}",
                'protocol': packet['protocol'],
                'size': packet['packet_size'],
                'is_attack': False
            })
        
        return jsonify({
            'attack_packets': formatted_attack,
            'legitimate_packets': formatted_legit,
            'total_attack': len(simulator.attack_traffic),
            'total_legitimate': len(simulator.legitimate_traffic)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ddos_simulator_bp.route('/clear_data', methods=['POST'])
def clear_data():
    """Clear all simulation data"""
    try:
        simulator.attack_traffic.clear()
        simulator.legitimate_traffic.clear()
        simulator.detection_results.clear()
        
        return jsonify({
            'status': 'success',
            'message': 'All simulation data cleared'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ddos_simulator_bp.route('/export_data', methods=['GET'])
def export_data():
    """Export simulation data for analysis"""
    try:
        import json
        from datetime import datetime
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'simulation_state': simulation_state,
            'statistics': simulator.get_attack_statistics(),
            'attack_packets_count': len(simulator.attack_traffic),
            'legitimate_packets_count': len(simulator.legitimate_traffic),
            'sample_attack_packets': [
                {
                    'timestamp': p['timestamp'].isoformat(),
                    'attack_type': p.get('attack_type'),
                    'src_ip': p['src_ip'],
                    'dst_ip': p['dst_ip'],
                    'protocol': p['protocol'],
                    'packet_size': p['packet_size']
                }
                for p in simulator.attack_traffic[-100:]
            ]
        }
        
        return jsonify(export_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ddos_simulator_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'simulator_active': simulator.attack_active,
        'detector_loaded': detector.rf_model is not None,
        'attack_packets_in_memory': len(simulator.attack_traffic),
        'legitimate_packets_in_memory': len(simulator.legitimate_traffic)
    })