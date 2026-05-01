from flask import Blueprint, request, jsonify, g
from backend.modules.web_security.sql_injection_detector import SQLInjectionDetector, XSSDetector
from backend.modules.web_security.waf_middleware import WebApplicationFirewall, waf_protect
import os

web_security_bp = Blueprint('web_security', __name__)

# Initialize detectors
model_dir = 'backend/models/web_security'
sqli_detector = SQLInjectionDetector()
xss_detector = XSSDetector()

# Load models
sqli_detector.load_models(model_dir)
xss_detector.load_models(model_dir)

# Initialize WAF
waf = WebApplicationFirewall(sqli_detector, xss_detector)

@web_security_bp.route('/analyze/sql_injection', methods=['POST'])
def analyze_sql_injection():
    """Analyze input for SQL injection"""
    try:
        data = request.get_json()
        input_text = data.get('input', '')
        
        if not input_text:
            return jsonify({'error': 'No input provided'}), 400
        
        result = sqli_detector.predict(input_text)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@web_security_bp.route('/analyze/xss', methods=['POST'])
def analyze_xss():
    """Analyze input for XSS"""
    try:
        data = request.get_json()
        input_text = data.get('input', '')
        
        if not input_text:
            return jsonify({'error': 'No input provided'}), 400
        
        result = xss_detector.predict(input_text)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@web_security_bp.route('/analyze/batch', methods=['POST'])
def analyze_batch():
    """Analyze multiple inputs for both SQL injection and XSS"""
    try:
        data = request.get_json()
        inputs = data.get('inputs', [])
        
        if not inputs:
            return jsonify({'error': 'No inputs provided'}), 400
        
        results = []
        for input_text in inputs:
            sqli_result = sqli_detector.predict(input_text)
            xss_result = xss_detector.predict(input_text)
            
            results.append({
                'input': input_text,
                'sql_injection': sqli_result,
                'xss': xss_result,
                'overall_threat': sqli_result['final_prediction'] or xss_result['final_prediction']
            })
        
        return jsonify({'results': results})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@web_security_bp.route('/waf/status', methods=['GET'])
def waf_status():
    """Get WAF status and statistics"""
    try:
        # Recent attacks (last hour)
        from datetime import datetime, timedelta
        current_time = datetime.now()
        recent_attacks = [
            attack for attack in waf.attack_log
            if datetime.fromisoformat(attack['timestamp']) > current_time - timedelta(hours=1)
        ]
        
        # Attack statistics
        attack_types = {}
        for attack in recent_attacks:
            attack_type = attack['attack_type']
            attack_types[attack_type] = attack_types.get(attack_type, 0) + 1
        
        status = {
            'active': True,
            'total_attacks_logged': len(waf.attack_log),
            'recent_attacks': len(recent_attacks),
            'blocked_ips': len(waf.blocked_ips),
            'attack_types': attack_types,
            'configuration': waf.config,
            'top_attacking_ips': waf.get_top_attacking_ips(limit=10)
        }
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@web_security_bp.route('/waf/attacks', methods=['GET'])
def get_attacks():
    """Get attack logs"""
    try:
        limit = int(request.args.get('limit', 100))
        attack_type = request.args.get('type')
        
        attacks = waf.attack_log.copy()
        
        # Filter by attack type if specified
        if attack_type:
            attacks = [a for a in attacks if a['attack_type'] == attack_type]
        
        # Sort by timestamp (newest first)
        attacks.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Limit results
        attacks = attacks[:limit]
        
        return jsonify({
            'attacks': attacks,
            'total': len(attacks)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@web_security_bp.route('/waf/unblock_ip', methods=['POST'])
def unblock_ip():
    """Unblock an IP address"""
    try:
        data = request.get_json()
        ip_address = data.get('ip')
        
        if not ip_address:
            return jsonify({'error': 'IP address required'}), 400
        
        if ip_address in waf.blocked_ips:
            del waf.blocked_ips[ip_address]
            return jsonify({'message': f'IP {ip_address} unblocked successfully'})
        else:
            return jsonify({'message': f'IP {ip_address} was not blocked'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Protected route example
@web_security_bp.route('/protected_endpoint', methods=['POST'])
@waf_protect(waf)
def protected_endpoint():
    """Example of a protected endpoint"""
    # This endpoint is automatically protected by WAF
    threats_detected = getattr(g, 'waf_threats', [])
    
    return jsonify({
        'message': 'Request allowed',
        'threats_detected': len(threats_detected),
        'threats': threats_detected
    })

@web_security_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'sql_injection_models_loaded': bool(sqli_detector.models),
        'xss_models_loaded': bool(xss_detector.models),
        'waf_active': True
    })

# Add method to WAF class for getting top attacking IPs
def get_top_attacking_ips(self, limit=10):
    """Get top attacking IP addresses"""
    ip_counts = {}
    for attack in self.attack_log:
        ip = attack['client_ip']
        ip_counts[ip] = ip_counts.get(ip, 0) + 1
    
    # Sort by count and return top IPs
    sorted_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_ips[:limit])

# Monkey patch the method to WAF class
WebApplicationFirewall.get_top_attacking_ips = get_top_attacking_ips