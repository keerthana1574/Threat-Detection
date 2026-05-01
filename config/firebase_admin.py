from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Enable CORS
CORS(app, origins="*")

# Initialize Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*")

# Test route
@app.route('/')
def home():
    return jsonify({
        'message': 'AI Cybersecurity Threat Detection System',
        'status': 'running',
        'version': '1.0.0'
    })

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

# Basic API routes for testing
@app.route('/api/cyberbullying/predict', methods=['POST'])
def cyberbullying_predict():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        # Simple mock prediction (replace with your actual model)
        prediction = len([word for word in ['hate', 'stupid', 'idiot', 'kill'] if word in text.lower()]) > 0
        confidence = 0.85 if prediction else 0.15
        
        return jsonify({
            'prediction': prediction,
            'confidence': confidence,
            'processing_time': 0.123
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fake_news/predict', methods=['POST'])
def fake_news_predict():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        # Simple mock prediction
        prediction = len([word for word in ['breaking', 'urgent', 'shocking', 'exclusive'] if word in text.lower()]) > 1
        confidence = 0.78 if prediction else 0.22
        
        return jsonify({
            'prediction': prediction,
            'confidence': confidence,
            'processing_time': 0.156
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sql_injection/predict', methods=['POST'])
def sql_injection_predict():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        # Simple mock prediction
        sql_keywords = ['or', 'union', 'select', 'drop', 'insert', 'delete', '--', ';']
        prediction = any(keyword in text.lower() for keyword in sql_keywords)
        confidence = 0.91 if prediction else 0.09
        
        return jsonify({
            'prediction': prediction,
            'confidence': confidence,
            'processing_time': 0.089
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/xss/predict', methods=['POST'])
def xss_predict():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        # Simple mock prediction
        xss_patterns = ['<script>', 'javascript:', 'onerror=', 'onload=', 'alert(']
        prediction = any(pattern in text.lower() for pattern in xss_patterns)
        confidence = 0.87 if prediction else 0.13
        
        return jsonify({
            'prediction': prediction,
            'confidence': confidence,
            'processing_time': 0.067
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/phishing/predict', methods=['POST'])
def phishing_predict():
    try:
        data = request.get_json()
        url = data.get('url', '')
        text = data.get('text', '')
        
        # Simple mock prediction for URL
        if url:
            suspicious_domains = ['paypal', 'amazon', 'google', 'microsoft']
            # Check for typosquatting
            prediction = any(domain in url.lower() and ('secure' in url or 'verify' in url) for domain in suspicious_domains)
            confidence = 0.82 if prediction else 0.18
        else:
            # Check text for phishing indicators
            phishing_words = ['verify', 'urgent', 'suspended', 'click here', 'confirm']
            prediction = len([word for word in phishing_words if word in text.lower()]) > 2
            confidence = 0.76 if prediction else 0.24
        
        return jsonify({
            'prediction': prediction,
            'confidence': confidence,
            'processing_time': 0.134
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Real-time monitoring routes (mock for now)
@app.route('/api/realtime/social-media/start', methods=['POST'])
def start_social_media_monitoring():
    try:
        data = request.get_json() or {}
        keywords = data.get('keywords', [])
        
        return jsonify({
            'success': True,
            'message': f'Social media monitoring started with keywords: {keywords}',
            'status': 'active'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/realtime/social-media/stop', methods=['POST'])
def stop_social_media_monitoring():
    try:
        return jsonify({
            'success': True,
            'message': 'Social media monitoring stopped',
            'status': 'inactive'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/realtime/social-media/status', methods=['GET'])
def get_social_media_status():
    try:
        return jsonify({
            'is_monitoring': False,
            'request_count': 0,
            'max_requests': 100,
            'remaining_requests': 100
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/realtime/network/start', methods=['POST'])
def start_network_monitoring():
    try:
        return jsonify({
            'success': True,
            'message': 'Network monitoring started',
            'status': 'active'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/realtime/network/stop', methods=['POST'])
def stop_network_monitoring():
    try:
        return jsonify({
            'success': True,
            'message': 'Network monitoring stopped',
            'status': 'inactive'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/realtime/web-security/start', methods=['POST'])
def start_web_security_monitoring():
    try:
        return jsonify({
            'success': True,
            'message': 'Web security monitoring started',
            'status': 'active'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/realtime/web-security/stop', methods=['POST'])
def stop_web_security_monitoring():
    try:
        return jsonify({
            'success': True,
            'message': 'Web security monitoring stopped',
            'status': 'inactive'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Mock data endpoints for dashboard
@app.route('/api/threats', methods=['GET'])
def get_threats():
    return jsonify({
        'threats': [
            {
                'id': 1,
                'type': 'cyberbullying',
                'message': 'Offensive content detected',
                'severity': 'high',
                'timestamp': '2024-01-15T10:30:00Z'
            },
            {
                'id': 2,
                'type': 'fake_news',
                'message': 'Misinformation detected',
                'severity': 'medium',
                'timestamp': '2024-01-15T09:15:00Z'
            }
        ]
    })

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    return jsonify({
        'alerts': [
            {
                'id': 1,
                'type': 'security_breach',
                'message': 'Suspicious login attempt detected',
                'severity': 'high',
                'timestamp': '2024-01-15T11:00:00Z'
            }
        ]
    })

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    return jsonify({
        'metrics': {
            'total_threats': 1247,
            'active_alerts': 15,
            'blocked_attacks': 892,
            'system_uptime': 99.8
        }
    })

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    print("🚀 Starting AI Cybersecurity Threat Detection System...")
    print("📡 Server running on http://localhost:5000")
    print("🔒 Ready to detect threats!")
    
    # Run the app
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)