from flask import Blueprint, request, jsonify
from backend.modules.cyberbullying.detector import CyberbullyingDetector, TwitterMonitor
import os

cyberbullying_bp = Blueprint('cyberbullying', __name__)

# Initialize detector
model_dir = 'backend/models/cyberbullying'
detector = CyberbullyingDetector(model_dir)

@cyberbullying_bp.route('/predict', methods=['POST'])
def predict_cyberbullying():
    """Predict cyberbullying for given text"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        result = detector.predict_single(text)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cyberbullying_bp.route('/predict/batch', methods=['POST'])
def predict_batch_cyberbullying():
    """Predict cyberbullying for multiple texts"""
    try:
        data = request.get_json()
        texts = data.get('texts', [])
        
        if not texts:
            return jsonify({'error': 'No texts provided'}), 400
        
        results = detector.predict_batch(texts)
        return jsonify({'results': results})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cyberbullying_bp.route('/monitor/twitter', methods=['POST'])
def monitor_twitter():
    """Monitor Twitter for cyberbullying"""
    try:
        data = request.get_json()
        keywords = data.get('keywords', [])
        count = data.get('count', 100)
        
        # Twitter API credentials from config
        api_credentials = {
            'api_key': os.getenv('eVdTmPJpLe2trEcBWnjzMbZBR'),
            'api_secret': os.getenv('zrUSGC5nDIHPIMqwk5zbyao1Ta9iJqaXNQPYgom95jCotlCcDo'),
            'access_token': os.getenv('1759606899732025344-eN5igcpmBCrcBUtjqHi5ZXf73sFSp6'),
            'access_secret': os.getenv('K6C0dPe87V3ivYS12FXxaRSCJRot1gh0QAijK8qIt5TVc'),
            'bearer_token': os.getenv('AAAAAAAAAAAAAAAAAAAAAL%2BN3gEAAAAAsZFH09MvFghorHlnRBImW2p68mQ%3DAFHw0R1I9qwcq5nzaHLqH8wZfVN7M8kyR8zxkMYMpePEoDBsGD')  # Add this
        }
        
        monitor = TwitterMonitor(api_credentials, detector)
        results = monitor.monitor_tweets(keywords, count)
        
        return jsonify({
            'total_tweets': len(results),
            'cyberbullying_detected': sum(1 for r in results if r['is_cyberbullying']),
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cyberbullying_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': len(detector.models) > 0
    })