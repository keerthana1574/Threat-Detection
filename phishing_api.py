from flask import Blueprint, request, jsonify
from backend.modules.phishing.phishing_detector import PhishingDetector
import os

phishing_bp = Blueprint('phishing', __name__)

# Initialize detector
model_dir = 'backend/models/phishing'
detector = PhishingDetector()
detector.load_models(model_dir)

@phishing_bp.route('/analyze_url', methods=['POST'])
def analyze_url():
    """Analyze URL for phishing"""
    try:
        data = request.get_json()
        url = data.get('url', '')
        analyze_content = data.get('analyze_content', False)
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Validate URL format
        if not (url.startswith('http://') or url.startswith('https://')):
            url = 'http://' + url
        
        result = detector.predict(url, analyze_content=analyze_content)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@phishing_bp.route('/analyze_batch', methods=['POST'])
def analyze_batch_urls():
    """Analyze multiple URLs for phishing"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        analyze_content = data.get('analyze_content', False)
        
        if not urls:
            return jsonify({'error': 'No URLs provided'}), 400
        
        results = []
        for url in urls:
            try:
                if not (url.startswith('http://') or url.startswith('https://')):
                    url = 'http://' + url
                
                result = detector.predict(url, analyze_content=analyze_content)
                results.append(result)
            except Exception as e:
                results.append({
                    'url': url,
                    'error': str(e),
                    'final_prediction': False,
                    'confidence': 0.0
                })
        
        # Calculate statistics
        phishing_count = sum(1 for r in results if r.get('final_prediction', False))
        
        return jsonify({
            'total_urls': len(results),
            'phishing_detected': phishing_count,
            'phishing_percentage': (phishing_count / len(results) * 100) if results else 0,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@phishing_bp.route('/quick_check', methods=['POST'])
def quick_check():
    """Quick phishing check using only rule-based detection"""
    try:
        data = request.get_json()
        url = data.get('url', '')
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        if not (url.startswith('http://') or url.startswith('https://')):
            url = 'http://' + url
        
        # Use only rule-based detection for speed
        rule_result = detector.rule_based_detection(url)
        
        return jsonify({
            'url': url,
            'is_phishing': rule_result['is_phishing'],
            'confidence': rule_result['confidence'],
            'risk_score': rule_result['risk_score'],
            'detections': rule_result['detections'],
            'analysis_type': 'rule_based_only'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@phishing_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get phishing detection statistics"""
    try:
        # This would typically pull from a database of analyzed URLs
        # For now, return mock statistics
        stats = {
            'total_urls_analyzed': 1250,
            'phishing_detected': 187,
            'detection_rate': 15.0,
            'top_phishing_targets': [
                {'target': 'PayPal', 'count': 45},
                {'target': 'Amazon', 'count': 32},
                {'target': 'Microsoft', 'count': 28},
                {'target': 'Apple', 'count': 23},
                {'target': 'Google', 'count': 19}
            ],
            'common_techniques': [
                {'technique': 'Typosquatting', 'count': 67},
                {'technique': 'URL Shorteners', 'count': 34},
                {'technique': 'Suspicious TLDs', 'count': 28},
                {'technique': 'IP Addresses', 'count': 24},
                {'technique': 'Homograph Attacks', 'count': 15}
            ]
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@phishing_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': bool(detector.models),
        'features_available': len(detector.feature_columns),
        'analysis_modes': ['rule_based', 'url_analysis', 'content_analysis']
    })