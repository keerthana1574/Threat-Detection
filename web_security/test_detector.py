from sql_injection_detector import SQLInjectionDetector

# Test the detector
detector = SQLInjectionDetector()

# Test cases
test_inputs = [
    "normal user input",
    "' OR '1'='1",
    "'; DROP TABLE users; --",
    "SELECT * FROM users WHERE id = 1"
]

print("Testing SQL Injection Detector:")
print("-" * 40)

for test_input in test_inputs:
    result = detector.predict(test_input)
    status = "MALICIOUS" if result['final_prediction'] else "SAFE"
    print(f"Input: {test_input}")
    print(f"Result: {status} (Confidence: {result['confidence']:.2f})")
    print(f"Risk Score: {result['rule_based']['risk_score']}")
    print("-" * 40)