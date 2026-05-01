from sql_injection_detector import SQLInjectionDetector, XSSDetector

def test_all():
    print("=" * 60)
    print("TESTING SQL INJECTION DETECTOR")
    print("=" * 60)
    
    sqli_detector = SQLInjectionDetector()
    sqli_detector.load_models('../../models/web_security')
    
    sqli_tests = [
        ("https://www.youtube.com/", "Normal URL"),
        ("user@example.com", "Normal email"),
        ("search query", "Normal search"),
        ("' OR '1'='1", "Classic SQLi"),
        ("'; DROP TABLE users; --", "Drop table attack"),
        ("admin'--", "Comment bypass"),
    ]
    
    for test_input, description in sqli_tests:
        result = sqli_detector.predict(test_input)
        status = "🔴 MALICIOUS" if result['final_prediction'] else "✅ SAFE"
        print(f"{status} | {description:20s} | Confidence: {result['confidence']:.2f}")
        print(f"   Input: {test_input}")
        print()
    
    print("=" * 60)
    print("TESTING XSS DETECTOR")
    print("=" * 60)
    
    xss_detector = XSSDetector()
    xss_detector.load_models('../../models/web_security')
    
    xss_tests = [
        ("https://www.youtube.com/", "Normal URL"),
        ("Hello world", "Normal text"),
        ("user@example.com", "Normal email"),
        ("<script>alert('XSS')</script>", "Script tag XSS"),
        ("<img src=x onerror=alert('XSS')>", "Image onerror XSS"),
        ("javascript:alert('XSS')", "JavaScript protocol"),
    ]
    
    for test_input, description in xss_tests:
        result = xss_detector.predict(test_input)
        status = "🔴 MALICIOUS" if result['final_prediction'] else "✅ SAFE"
        print(f"{status} | {description:20s} | Confidence: {result['confidence']:.2f}")
        print(f"   Input: {test_input}")
        print()

if __name__ == "__main__":
    test_all()