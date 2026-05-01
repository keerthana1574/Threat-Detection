import time
import threading
import requests
from datetime import datetime
from config.database import db_manager
from modules.web_security.sql_injection_detector import SQLInjectionDetector
from modules.web_security.xss_detector import XSSDetector
from utils.alert_system import AlertSystem
import logging

class WebSecurityMonitor:
    def __init__(self):
        self.sql_detector = SQLInjectionDetector()
        self.xss_detector = XSSDetector()
        self.alert_system = AlertSystem()
        self.is_monitoring = False
        self.monitored_endpoints = []
        
    def add_endpoint(self, url, method='GET', headers=None):
        """Add endpoint to monitor"""
        endpoint = {
            'url': url,
            'method': method,
            'headers': headers or {},
            'last_checked': None
        }
        self.monitored_endpoints.append(endpoint)
        return {"success": f"Added endpoint {url} to monitoring"}
    
    def start_monitoring(self):
        """Start web security monitoring"""
        if self.is_monitoring:
            return {"error": "Web security monitoring already active"}
        
        if not self.monitored_endpoints:
            return {"error": "No endpoints to monitor. Add endpoints first."}
        
        self.is_monitoring = True
        
        # Start monitoring in separate thread
        monitor_thread = threading.Thread(target=self._monitor_endpoints)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return {"success": "Web security monitoring started"}
    
    def stop_monitoring(self):
        """Stop web security monitoring"""
        self.is_monitoring = False
        return {"success": "Web security monitoring stopped"}
    
    def _monitor_endpoints(self):
        """Monitor endpoints for web security threats"""
        while self.is_monitoring:
            try:
                for endpoint in self.monitored_endpoints:
                    if not self.is_monitoring:
                        break
                    
                    self._check_endpoint_security(endpoint)
                    time.sleep(5)  # 5 second delay between checks
                
                # Wait before next monitoring cycle
                time.sleep(30)
                
            except Exception as e:
                logging.error(f"Web security monitoring error: {e}")
                time.sleep(60)
    
    def _check_endpoint_security(self, endpoint):
        """Check endpoint for security vulnerabilities"""
        try:
            url = endpoint['url']
            method = endpoint['method']
            headers = endpoint['headers']
            
            # Test for SQL injection
            self._test_sql_injection(url, method, headers)
            
            # Test for XSS
            self._test_xss(url, method, headers)
            
            # Update last checked time
            endpoint['last_checked'] = datetime.now()
            
        except Exception as e:
            logging.error(f"Endpoint security check error: {e}")
    
    def _test_sql_injection(self, url, method, headers):
        """Test endpoint for SQL injection vulnerabilities"""
        try:
            # Common SQL injection payloads
            sql_payloads = [
                "' OR '1'='1",
                "'; DROP TABLE users; --",
                "' UNION SELECT * FROM users --",
                "admin'--",
                "' OR 1=1#"
            ]
            
            for payload in sql_payloads:
                if not self.is_monitoring:
                    break
                
                # Test different parameter injection points
                test_params = {
                    'id': payload,
                    'user': payload,
                    'search': payload,
                    'query': payload
                }
                
                try:
                    if method.upper() == 'GET':
                        response = requests.get(
                            url,
                            params=test_params,
                            headers=headers,
                            timeout=10
                        )
                    else:
                        response = requests.post(
                            url,
                            data=test_params,
                            headers=headers,
                            timeout=10
                        )
                    
                    # Analyze response for SQL injection indicators
                    if self._detect_sql_injection_response(response.text, payload):
                        self._log_web_threat(
                            threat_type='sql_injection',
                            url=url,
                            payload=payload,
                            response_content=response.text[:500]
                        )
                        
                        self.alert_system.send_alert(
                            alert_type='sql_injection',
                            message=f'SQL injection vulnerability detected at {url}',
                            severity='high'
                        )
                
                except requests.RequestException as e:
                    logging.error(f"SQL injection test error: {e}")
                
                time.sleep(1)  # Rate limiting
                
        except Exception as e:
            logging.error(f"SQL injection testing error: {e}")
    
    def _test_xss(self, url, method, headers):
        """Test endpoint for XSS vulnerabilities"""
        try:
            # Common XSS payloads
            xss_payloads = [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "javascript:alert('XSS')",
                "<svg/onload=alert('XSS')>",
                "'><script>alert('XSS')</script>"
            ]
            
            for payload in xss_payloads:
                if not self.is_monitoring:
                    break
                
                # Test different parameter injection points
                test_params = {
                    'comment': payload,
                    'message': payload,
                    'search': payload,
                    'name': payload
                }
                
                try:
                    if method.upper() == 'GET':
                        response = requests.get(
                            url,
                            params=test_params,
                            headers=headers,
                            timeout=10
                        )
                    else:
                        response = requests.post(
                            url,
                            data=test_params,
                            headers=headers,
                            timeout=10
                        )
                    
                    # Analyze response for XSS indicators
                    if self._detect_xss_response(response.text, payload):
                        self._log_web_threat(
                            threat_type='xss',
                            url=url,
                            payload=payload,
                            response_content=response.text[:500]
                        )
                        
                        self.alert_system.send_alert(
                            alert_type='xss',
                            message=f'XSS vulnerability detected at {url}',
                            severity='high'
                        )
                
                except requests.RequestException as e:
                    logging.error(f"XSS test error: {e}")
                
                time.sleep(1)  # Rate limiting
                
        except Exception as e:
            logging.error(f"XSS testing error: {e}")
    
    def _detect_sql_injection_response(self, response_text, payload):
        """Detect SQL injection from response"""
        # SQL error indicators
        sql_errors = [
            'mysql_fetch_array',
            'ORA-01756',
            'Microsoft OLE DB Provider',
            'PostgreSQL query failed',
            'Warning: mysql_',
            'valid MySQL result',
            'MySqlClient.',
            'error in your SQL syntax'
        ]
        
        response_lower = response_text.lower()
        
        for error in sql_errors:
            if error.lower() in response_lower:
                return True
        
        return False
    
    def _detect_xss_response(self, response_text, payload):
        """Detect XSS from response"""
        # Check if payload is reflected in response
        if payload in response_text:
            return True
        
        # Check for XSS indicators
        xss_indicators = [
            '<script',
            'onerror=',
            'onload=',
            'javascript:'
        ]
        
        response_lower = response_text.lower()
        
        for indicator in xss_indicators:
            if indicator in response_lower and payload.lower() in response_lower:
                return True
        
        return False
    
    def _log_web_threat(self, threat_type, url, payload, response_content):
        """Log web security threat"""
        try:
            cursor = db_manager.get_postgres_cursor()
            cursor.execute("""
                INSERT INTO threat_logs (threat_type, description, target_ip, severity)
                VALUES (%s, %s, %s, %s)
            """, (
                threat_type,
                f"Vulnerability detected at {url} with payload: {payload}",
                url,
                'high'
            ))
            
            # Log detection result
            cursor.execute("""
                INSERT INTO detection_results (module_name, input_data, prediction, confidence_score)
                VALUES (%s, %s, %s, %s)
            """, (threat_type, f"{url} | {payload}", True, 0.9))
            
            # Log to MongoDB
            mongo_collection = db_manager.get_mongo_collection('web_security_logs')
            mongo_collection.insert_one({
                'threat_type': threat_type,
                'url': url,
                'payload': payload,
                'response_content': response_content,
                'detected_at': datetime.now().isoformat()
            })
            
        except Exception as e:
            logging.error(f"Web threat logging error: {e}")
    
    def get_monitoring_status(self):
        """Get web security monitoring status"""
        return {
            'is_monitoring': self.is_monitoring,
            'monitored_endpoints': len(self.monitored_endpoints),
            'endpoints': [
                {
                    'url': ep['url'],
                    'method': ep['method'],
                    'last_checked': ep['last_checked'].isoformat() if ep['last_checked'] else None
                }
                for ep in self.monitored_endpoints
            ]
        }

# Global web security monitor instance
web_security_monitor = WebSecurityMonitor()