from flask import request, jsonify, g, has_request_context
from functools import wraps
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
import threading
import hashlib
import logging
import os

class WebApplicationFirewall:
    def __init__(self, sqli_detector, xss_detector):
        self.sqli_detector = sqli_detector
        self.xss_detector = xss_detector
        
        # Rate limiting
        self.request_counts = defaultdict(lambda: deque())
        self.blocked_ips = {}
        
        # Attack tracking
        self.attack_log = []
        self.suspicious_activities = defaultdict(int)
        
        # Configuration
        self.config = {
            'rate_limit_requests': 100,  # requests per minute
            'rate_limit_window': 60,     # seconds
            'block_duration': 300,       # seconds (5 minutes)
            'max_suspicious_activities': 5,
            'enable_logging': True
        }
        
        # Setup logging
        if self.config['enable_logging']:
            # Ensure logs directory exists
            os.makedirs('logs', exist_ok=True)
            
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - WAF - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler('logs/waf.log'),
                    logging.StreamHandler()
                ]
            )
            self.logger = logging.getLogger(__name__)
        
    def get_client_ip(self):
        """Get client IP address"""
        # Check if we're in a Flask request context
        if not has_request_context():
            return '127.0.0.1'  # Default IP for testing
            
        if request.environ.get('HTTP_X_FORWARDED_FOR'):
            return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
        elif request.environ.get('HTTP_X_REAL_IP'):
            return request.environ['HTTP_X_REAL_IP']
        else:
            return request.environ.get('REMOTE_ADDR', '127.0.0.1')
    
    def is_rate_limited(self, client_ip):
        """Check if client is rate limited"""
        current_time = time.time()
        window_start = current_time - self.config['rate_limit_window']
        
        # Clean old requests
        while (self.request_counts[client_ip] and 
               self.request_counts[client_ip][0] < window_start):
            self.request_counts[client_ip].popleft()
        
        # Check rate limit
        if len(self.request_counts[client_ip]) >= self.config['rate_limit_requests']:
            return True
        
        # Add current request
        self.request_counts[client_ip].append(current_time)
        return False
    
    def is_blocked(self, client_ip):
        """Check if IP is currently blocked"""
        if client_ip in self.blocked_ips:
            block_time = self.blocked_ips[client_ip]
            if datetime.now() - block_time < timedelta(seconds=self.config['block_duration']):
                return True
            else:
                # Unblock expired blocks
                del self.blocked_ips[client_ip]
        return False

    def block_ip(self, client_ip, reason):
        """Block an IP address"""
        self.blocked_ips[client_ip] = datetime.now()
        
        # Only log attack if we're in a request context
        if has_request_context():
            self.log_attack(client_ip, 'IP_BLOCKED', reason)
        else:
            # For testing outside request context
            self._log_attack_safe(client_ip, 'IP_BLOCKED', reason)
        
        if self.config['enable_logging']:
            self.logger.warning(f"Blocked IP {client_ip}: {reason}")

    def analyze_request(self, request_data=None):
        """Analyze request for security threats"""
        threats = []
        
        # If no request context, skip analysis
        if not has_request_context():
            return threats
        
        # Analyze all input parameters
        all_inputs = []
        
        # GET parameters
        if request.args:
            all_inputs.extend(request.args.values())
        
        # POST parameters
        if request.form:
            all_inputs.extend(request.form.values())
        
        # JSON data
        if request.is_json and request.json:
            all_inputs.extend(self.extract_json_values(request.json))
        
        # Headers (check for injection in headers)
        suspicious_headers = ['User-Agent', 'Referer', 'X-Forwarded-For']
        for header in suspicious_headers:
            if header in request.headers:
                all_inputs.append(request.headers[header])
        
        # URL path
        all_inputs.append(request.path)
        
        # Analyze each input
        for input_value in all_inputs:
            if not input_value or len(str(input_value)) > 10000:  # Skip very long inputs
                continue
                
            input_str = str(input_value)
            
            # SQL Injection detection
            sqli_result = self.sqli_detector.predict(input_str)
            if sqli_result['final_prediction']:
                threats.append({
                    'type': 'SQL_INJECTION',
                    'input': input_str[:200] + "..." if len(input_str) > 200 else input_str,
                    'confidence': sqli_result['confidence'],
                    'details': sqli_result
                })
            
            # XSS detection
            xss_result = self.xss_detector.predict(input_str)
            if xss_result['final_prediction']:
                threats.append({
                    'type': 'XSS',
                    'input': input_str[:200] + "..." if len(input_str) > 200 else input_str,
                    'confidence': xss_result['confidence'],
                    'details': xss_result
                })
        
        return threats

    def extract_json_values(self, json_obj):
        """Recursively extract all string values from JSON"""
        values = []
        if isinstance(json_obj, dict):
            for value in json_obj.values():
                if isinstance(value, str):
                    values.append(value)
                elif isinstance(value, (dict, list)):
                    values.extend(self.extract_json_values(value))
        elif isinstance(json_obj, list):
            for item in json_obj:
                if isinstance(item, str):
                    values.append(item)
                elif isinstance(item, (dict, list)):
                    values.extend(self.extract_json_values(item))
        return values

    def log_attack(self, client_ip, attack_type, details):
        """Log security attack (requires Flask request context)"""
        if not has_request_context():
            self._log_attack_safe(client_ip, attack_type, details)
            return
            
        attack_record = {
            'timestamp': datetime.now().isoformat(),
            'client_ip': client_ip,
            'attack_type': attack_type,
            'details': details,
            'user_agent': request.headers.get('User-Agent', ''),
            'url': request.url,
            'method': request.method
        }
        
        self.attack_log.append(attack_record)
        
        # Keep only last 1000 attacks
        if len(self.attack_log) > 1000:
            self.attack_log = self.attack_log[-1000:]
        
        if self.config['enable_logging']:
            self.logger.warning(f"Security attack detected: {attack_type} from {client_ip}")

    def _log_attack_safe(self, client_ip, attack_type, details):
        """Log attack without Flask request context (for testing)"""
        attack_record = {
            'timestamp': datetime.now().isoformat(),
            'client_ip': client_ip,
            'attack_type': attack_type,
            'details': details,
            'user_agent': 'Testing/1.0',
            'url': '/test',
            'method': 'GET'
        }
        
        self.attack_log.append(attack_record)
        
        # Keep only last 1000 attacks
        if len(self.attack_log) > 1000:
            self.attack_log = self.attack_log[-1000:]
        
        if self.config['enable_logging']:
            self.logger.warning(f"Security attack detected: {attack_type} from {client_ip}")

    def check_request(self):
        """Main request checking function"""
        client_ip = self.get_client_ip()
        
        # Check if IP is blocked
        if self.is_blocked(client_ip):
            return {
                'allowed': False,
                'reason': 'IP_BLOCKED',
                'message': 'Your IP has been temporarily blocked due to suspicious activity'
            }
        
        # Check rate limiting
        if self.is_rate_limited(client_ip):
            self.suspicious_activities[client_ip] += 1
            
            if self.suspicious_activities[client_ip] >= self.config['max_suspicious_activities']:
                self.block_ip(client_ip, 'RATE_LIMIT_EXCEEDED')
                return {
                    'allowed': False,
                    'reason': 'RATE_LIMIT_EXCEEDED',
                    'message': 'Rate limit exceeded. IP blocked temporarily.'
                }
            
            return {
                'allowed': False,
                'reason': 'RATE_LIMITED',
                'message': 'Rate limit exceeded. Please slow down your requests.'
            }
        
        # Analyze request for threats
        threats = self.analyze_request()
        
        if threats:
            # Log all threats
            for threat in threats:
                if has_request_context():
                    self.log_attack(client_ip, threat['type'], threat)
                else:
                    self._log_attack_safe(client_ip, threat['type'], threat)
            
            self.suspicious_activities[client_ip] += len(threats)
            
            # Block IP if too many threats
            if self.suspicious_activities[client_ip] >= self.config['max_suspicious_activities']:
                self.block_ip(client_ip, f"MULTIPLE_ATTACKS: {[t['type'] for t in threats]}")
                return {
                    'allowed': False,
                    'reason': 'SECURITY_THREAT',
                    'message': 'Request blocked due to security threats'
                }
            
            # High confidence threats are blocked immediately
            high_confidence_threats = [t for t in threats if t['confidence'] > 0.8]
            if high_confidence_threats:
                if has_request_context():
                    self.log_attack(client_ip, 'HIGH_CONFIDENCE_ATTACK', high_confidence_threats)
                else:
                    self._log_attack_safe(client_ip, 'HIGH_CONFIDENCE_ATTACK', high_confidence_threats)
                return {
                    'allowed': False,
                    'reason': 'HIGH_RISK_ATTACK',
                    'message': 'Request blocked due to high-risk security threat',
                    'threats': threats
                }
        
        return {'allowed': True, 'threats': threats}

    def test_detection(self, test_input, client_ip="192.168.1.100"):
        """Test threat detection without Flask context"""
        threats = []
        
        # SQL Injection detection
        sqli_result = self.sqli_detector.predict(test_input)
        if sqli_result['final_prediction']:
            threats.append({
                'type': 'SQL_INJECTION',
                'input': test_input[:200] + "..." if len(test_input) > 200 else test_input,
                'confidence': sqli_result['confidence'],
                'details': sqli_result
            })
        
        # XSS detection
        xss_result = self.xss_detector.predict(test_input)
        if xss_result['final_prediction']:
            threats.append({
                'type': 'XSS',
                'input': test_input[:200] + "..." if len(test_input) > 200 else test_input,
                'confidence': xss_result['confidence'],
                'details': xss_result
            })
        
        return threats


def waf_protect(waf):
    """Decorator to protect routes with WAF"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check request with WAF
            check_result = waf.check_request()

            if not check_result['allowed']:
                response = jsonify({
                    'error': 'Request blocked by Web Application Firewall',
                    'reason': check_result['reason'],
                    'message': check_result.get('message', ''),
                    'timestamp': datetime.now().isoformat()
                })
                
                # Set appropriate HTTP status code
                if check_result['reason'] in ['RATE_LIMITED', 'RATE_LIMIT_EXCEEDED']:
                    response.status_code = 429  # Too Many Requests
                elif check_result['reason'] == 'IP_BLOCKED':
                    response.status_code = 403  # Forbidden
                else:
                    response.status_code = 400  # Bad Request
                
                return response
            
            # Store threat information in Flask's g object for logging
            g.waf_threats = check_result.get('threats', [])
            
            # Continue with normal request processing
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator