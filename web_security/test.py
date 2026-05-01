from sql_injection_detector import SQLInjectionDetector, XSSDetector
from waf_middleware import WebApplicationFirewall

def test_sql_injection():
    """Test SQL injection detection"""
    print("Testing SQL Injection Detection")
    print("=" * 40)
    
    detector = SQLInjectionDetector()
    
    # Load models if available
    detector.load_models('../../models/web_security')
    
    test_inputs = [
        # Normal inputs
        "user123",
        "password123",
        "search query",
        "john.doe@example.com",
        
        # SQL injection attacks
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "' UNION SELECT username, password FROM admin --",
        "1' AND (SELECT COUNT(*) FROM users)>0--",
        "admin'--"
    ]
    
    for input_text in test_inputs:
        result = detector.predict(input_text)
        
        print(f"Input: {input_text}")
        print(f"Malicious: {'YES' if result['final_prediction'] else 'NO'}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"Rule-based risk score: {result['rule_based']['risk_score']}")
        if result['rule_based']['detections']:
            print(f"Detections: {len(result['rule_based']['detections'])}")
        print("-" * 40)

def test_xss_detection():
    """Test XSS detection"""
    print("\nTesting XSS Detection")
    print("=" * 40)
    
    detector = XSSDetector()
    
    # Load models if available
    detector.load_models('../../models/web_security')
    
    test_inputs = [
        # Normal inputs
        "Hello world",
        "user@example.com",
        "Product description",
        "Search for items",
        
        # XSS attacks
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<iframe src=javascript:alert('XSS')></iframe>",
        "<svg onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "<body onload=alert('XSS')>"
    ]
    
    for input_text in test_inputs:
        result = detector.predict(input_text)
        
        print(f"Input: {input_text}")
        print(f"Malicious: {'YES' if result['final_prediction'] else 'NO'}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"Rule-based risk score: {result['rule_based']['risk_score']}")
        if result['rule_based']['detections']:
            print(f"Detections: {len(result['rule_based']['detections'])}")
        print("-" * 40)

def test_waf():
    """Test WAF functionality"""
    print("\nTesting Web Application Firewall")
    print("=" * 40)
    
    # Initialize detectors
    sqli_detector = SQLInjectionDetector()
    xss_detector = XSSDetector()
    
    # Initialize WAF
    waf = WebApplicationFirewall(sqli_detector, xss_detector)
    
    # Simulate some attack scenarios
    print("WAF configuration:", waf.config)
    print("Blocked IPs:", len(waf.blocked_ips))
    print("Attack log entries:", len(waf.attack_log))
    
    # Test IP blocking
    test_ip = "192.168.1.100"
    waf.block_ip(test_ip, "Test block")
    print(f"Blocked {test_ip}: {waf.is_blocked(test_ip)}")

if __name__ == "__main__":
    test_sql_injection()
    test_xss_detection()
    test_waf()