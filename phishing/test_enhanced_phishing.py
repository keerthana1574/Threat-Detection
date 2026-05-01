# test_enhanced_phishing.py - Complete Version
from fixed_phishing_detector import ImprovedPhishingDetector
import json
import time
import sys
import os

def test_enhanced_detector():
    """Test the enhanced phishing detector with comprehensive test cases"""
    
    print("Testing Enhanced Phishing Detection System")
    print("=" * 60)
    
    # Initialize detector
    detector = ImprovedPhishingDetector()
    
    # Try to load models
    model_dir = 'backend/models/phishing'
    if not os.path.exists(model_dir):
        model_dir = '../../models/phishing'  # Try alternative path
    
    model_loaded = detector.load_models(model_dir)
    if model_loaded:
        print("✓ Enhanced models loaded successfully!")
        print(f"✓ {len(detector.models)} ML models available")
        print(f"✓ {len(detector.feature_columns)} features configured")
    else:
        print("⚠ No models found, using rule-based detection only")
        print(f"Searched in: {model_dir}")
    
    # Comprehensive test cases
    test_cases = [
        # Legitimate URLs - should be classified as SAFE
        {
            'url': 'https://www.paypal.com',
            'expected': False,
            'description': 'Official PayPal (whitelisted)'
        },
        {
            'url': 'https://www.google.com',
            'expected': False,
            'description': 'Official Google (whitelisted)'
        },
        {
            'url': 'https://accounts.google.com/signin',
            'expected': False,
            'description': 'Google Sign-in (legitimate subdomain)'
        },
        {
            'url': 'https://www.amazon.com/signin',
            'expected': False,
            'description': 'Amazon Sign-in (whitelisted)'
        },
        {
            'url': 'https://login.microsoftonline.com',
            'expected': False,
            'description': 'Microsoft Online Login (legitimate)'
        },
        {
            'url': 'https://appleid.apple.com',
            'expected': False,
            'description': 'Apple ID (legitimate subdomain)'
        },
        {
            'url': 'https://www.facebook.com/login',
            'expected': False,
            'description': 'Facebook Login (whitelisted)'
        },
        {
            'url': 'https://www.netflix.com',
            'expected': False,
            'description': 'Netflix (whitelisted)'
        },
        
        # Clear phishing URLs - should be detected
        {
            'url': 'http://paypal-security.tk/urgent-action',
            'expected': True,
            'description': 'Typosquatting + suspicious TLD'
        },
        {
            'url': 'http://192.168.1.100/paypal/login.php',
            'expected': True,
            'description': 'IP address + brand impersonation'
        },
        {
            'url': 'http://amaz0n-verify-account.ml/signin',
            'expected': True,
            'description': 'Character substitution + suspicious TLD'
        },
        {
            'url': 'http://google-security-alert.ga/verify-now',
            'expected': True,
            'description': 'Brand spoofing + urgent language'
        },
        {
            'url': 'http://apple-id-suspended.cf/restore-access',
            'expected': True,
            'description': 'Brand impersonation + fear tactics'
        },
        {
            'url': 'http://microsoft-security-update.pw/urgent',
            'expected': True,
            'description': 'Brand spoofing + suspicious TLD'
        },
        {
            'url': 'http://facebook-account-review.tk/verify',
            'expected': True,
            'description': 'Social media phishing'
        },
        
        # Edge cases and sophisticated attacks
        {
            'url': 'https://bit.ly/paypal-urgent',
            'expected': True,
            'description': 'URL shortener with suspicious keywords'
        },
        {
            'url': 'http://secure-banking-portal.tk/login',
            'expected': True,
            'description': 'Generic banking phishing'
        },
        {
            'url': 'https://facebook.com-verify.ml/security',
            'expected': True,
            'description': 'Subdomain spoofing'
        },
        {
            'url': 'http://paypal.security-team.ga/urgent',
            'expected': True,
            'description': 'Subdomain-based phishing'
        },
        {
            'url': 'http://раураl.com',  # Cyrillic characters
            'expected': True,
            'description': 'Homograph attack (Cyrillic)'
        },
        {
            'url': 'http://chase-bank-security.cf/verify-account',
            'expected': True,
            'description': 'Banking phishing with suspicious TLD'
        }
    ]
    
    print(f"\nRunning {len(test_cases)} test cases...")
    print("-" * 60)
    
    correct_predictions = 0
    total_tests = len(test_cases)
    false_positives = 0
    false_negatives = 0
    
    results_summary = []
    
    for i, test_case in enumerate(test_cases, 1):
        url = test_case['url']
        expected = test_case['expected']
        description = test_case['description']
        
        print(f"\nTest {i}: {description}")
        print(f"URL: {url}")
        
        # Get prediction
        start_time = time.time()
        try:
            result = detector.predict(url)
            prediction_time = time.time() - start_time
            
            prediction = result['final_prediction']
            confidence = result['confidence']
            
            # Check correctness
            is_correct = prediction == expected
            if is_correct:
                correct_predictions += 1
                status = "✓ CORRECT"
            else:
                status = "✗ INCORRECT"
                if prediction and not expected:
                    false_positives += 1
                elif not prediction and expected:
                    false_negatives += 1
            
            # Display results
            pred_text = "PHISHING" if prediction else "LEGITIMATE"
            expected_text = "PHISHING" if expected else "LEGITIMATE"
            
            print(f"Predicted: {pred_text} (confidence: {confidence:.3f})")
            print(f"Expected:  {expected_text}")
            print(f"Result:    {status} ({prediction_time:.3f}s)")
            
            # Show detection details for phishing predictions
            if prediction and result.get('risk_factors'):
                print("Risk factors:")
                for factor in result['risk_factors'][:3]:  # Show top 3
                    factor_type = factor.get('type', 'unknown')
                    factor_desc = factor.get('description', 'N/A')
                    print(f"  - {factor_type}: {factor_desc}")
            
            # Show ML model predictions if available
            if result.get('ml_predictions'):
                print("ML models:")
                for model_name, pred_data in result['ml_predictions'].items():
                    ml_pred = "PHISHING" if pred_data['prediction'] else "LEGITIMATE"
                    ml_prob = pred_data['probability']
                    print(f"  - {model_name}: {ml_pred} ({ml_prob:.3f})")
            
            # Store result for detailed analysis
            results_summary.append({
                'test_id': i,
                'url': url,
                'description': description,
                'expected': expected,
                'predicted': prediction,
                'confidence': confidence,
                'correct': is_correct,
                'processing_time': prediction_time
            })
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            results_summary.append({
                'test_id': i,
                'url': url,
                'description': description,
                'error': str(e)
            })
    
    # Detailed Summary
    accuracy = correct_predictions / total_tests * 100
    print("\n" + "="*60)
    print("DETAILED TEST RESULTS")
    print("="*60)
    print(f"Total tests: {total_tests}")
    print(f"Correct predictions: {correct_predictions}")
    print(f"Accuracy: {accuracy:.1f}%")
    print(f"False positives: {false_positives} (legitimate marked as phishing)")
    print(f"False negatives: {false_negatives} (phishing marked as legitimate)")
    
    if false_positives > 0:
        print(f"False positive rate: {false_positives/total_tests*100:.1f}%")
    if false_negatives > 0:
        print(f"False negative rate: {false_negatives/total_tests*100:.1f}%")
    
    # Performance assessment
    if accuracy >= 95:
        print("🏆 Excellent performance!")
    elif accuracy >= 90:
        print("✓ Very good performance")
    elif accuracy >= 80:
        print("✓ Good performance")
    elif accuracy >= 70:
        print("⚠ Acceptable performance, consider retraining")
    else:
        print("✗ Poor performance, retraining required")
    
    # Show problematic cases
    incorrect_cases = [r for r in results_summary if not r.get('correct', True) and 'error' not in r]
    if incorrect_cases:
        print(f"\nProblematic cases ({len(incorrect_cases)}):")
        for case in incorrect_cases:
            pred_text = "PHISHING" if case['predicted'] else "LEGITIMATE"
            exp_text = "PHISHING" if case['expected'] else "LEGITIMATE"
            print(f"  {case['test_id']}: {case['url'][:50]}...")
            print(f"    Expected: {exp_text}, Got: {pred_text} (conf: {case['confidence']:.3f})")
    
    return accuracy, false_positives, false_negatives

def benchmark_performance():
    """Benchmark detection speed and memory usage"""
    
    print("\n" + "="*60)
    print("PERFORMANCE BENCHMARK")
    print("="*60)
    
    detector = ImprovedPhishingDetector()
    
    model_dir = 'backend/models/phishing'
    if not os.path.exists(model_dir):
        model_dir = '../../models/phishing'
    
    detector.load_models(model_dir)
    
    # Test URLs for speed benchmark
    benchmark_urls = [
        "https://www.google.com",
        "http://paypal-security.tk/urgent",
        "https://www.amazon.com/signin",
        "http://192.168.1.100/fake-bank/login",
        "https://accounts.microsoft.com",
        "http://g00gle-verify.ml/accounts",
        "https://www.paypal.com",
        "http://apple-suspended.cf/verify",
        "https://www.facebook.com",
        "http://secure-banking.tk/login"
    ] * 10  # 100 total URLs
    
    print(f"Benchmarking with {len(benchmark_urls)} URLs...")
    
    start_time = time.time()
    predictions = []
    
    for i, url in enumerate(benchmark_urls):
        result = detector.predict(url)
        predictions.append(result)
        
        if (i + 1) % 20 == 0:
            elapsed = time.time() - start_time
            progress = (i + 1) / len(benchmark_urls) * 100
            print(f"  Progress: {progress:.0f}% ({elapsed:.1f}s elapsed)")
    
    total_time = time.time() - start_time
    avg_time = total_time / len(benchmark_urls)
    
    print(f"\nPerformance Results:")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average time per URL: {avg_time:.4f} seconds")
    print(f"URLs per second: {1/avg_time:.1f}")
    
    # Analyze prediction distribution
    phishing_count = sum(1 for p in predictions if p['final_prediction'])
    legitimate_count = len(predictions) - phishing_count
    
    print(f"Prediction distribution: {phishing_count} phishing, {legitimate_count} legitimate")
    
    # Confidence analysis
    confidences = [p['confidence'] for p in predictions]
    avg_confidence = sum(confidences) / len(confidences)
    print(f"Average confidence: {avg_confidence:.3f}")
    
    return avg_time

def test_specific_cases():
    """Test specific problematic cases"""
    
    print("\n" + "="*60)
    print("SPECIFIC CASE TESTING")
    print("="*60)
    
    detector = ImprovedPhishingDetector()
    
    model_dir = 'backend/models/phishing'
    if not os.path.exists(model_dir):
        model_dir = '../../models/phishing'
    
    detector.load_models(model_dir)
    
    # Test the original problematic case
    test_url = "https://google.com"
    print(f"Testing original problematic case: {test_url}")
    
    result = detector.predict(test_url)
    prediction = result['final_prediction']
    confidence = result['confidence']
    
    print(f"Result: {'PHISHING' if prediction else 'LEGITIMATE'} (confidence: {confidence:.3f})")
    
    if not prediction:
        print("✓ Fixed! Google.com is now correctly classified as legitimate")
    else:
        print("✗ Still incorrectly flagging Google.com as phishing")
        print("Risk factors:")
        for factor in result.get('risk_factors', []):
            print(f"  - {factor.get('type')}: {factor.get('description')}")
    
    # Test other major sites
    major_sites = [
        "https://www.amazon.com",
        "https://www.microsoft.com", 
        "https://www.apple.com",
        "https://www.facebook.com",
        "https://www.netflix.com"
    ]
    
    print(f"\nTesting major legitimate sites:")
    for site in major_sites:
        result = detector.predict(site)
        status = "SAFE" if not result['final_prediction'] else "PHISHING"
        print(f"  {site}: {status} ({result['confidence']:.3f})")

def export_test_results():
    """Export test results to JSON file"""
    print("\n" + "="*60)
    print("EXPORTING TEST RESULTS")
    print("="*60)
    
    try:
        # Run a quick test
        detector = ImprovedPhishingDetector()
        
        model_dir = 'backend/models/phishing'
        if not os.path.exists(model_dir):
            model_dir = '../../models/phishing'
        
        models_loaded = detector.load_models(model_dir)
        
        test_results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'models_loaded': models_loaded,
            'available_models': list(detector.models.keys()) if models_loaded else [],
            'feature_count': len(detector.feature_columns) if detector.feature_columns else 0,
            'test_cases': []
        }
        
        # Quick tests
        quick_tests = [
            ('https://www.google.com', False),
            ('http://paypal-security.tk', True),
            ('https://www.amazon.com', False),
            ('http://192.168.1.100/login', True)
        ]
        
        for url, expected in quick_tests:
            result = detector.predict(url)
            test_results['test_cases'].append({
                'url': url,
                'expected_phishing': expected,
                'predicted_phishing': result['final_prediction'],
                'confidence': result['confidence'],
                'correct': result['final_prediction'] == expected
            })
        
        # Save results
        with open('phishing_test_results.json', 'w') as f:
            json.dump(test_results, f, indent=2)
        
        print("✓ Test results exported to phishing_test_results.json")
        
    except Exception as e:
        print(f"✗ Export failed: {e}")

def main():
    """Main test function"""
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'quick':
            test_specific_cases()
        elif command == 'benchmark':
            benchmark_performance()
        elif command == 'export':
            export_test_results()
        elif command == 'all':
            accuracy, fp, fn = test_enhanced_detector()
            avg_time = benchmark_performance()
            test_specific_cases()
            export_test_results()
            
            print(f"\n" + "="*60)
            print("FINAL SUMMARY")
            print("="*60)
            print(f"Overall accuracy: {accuracy:.1f}%")
            print(f"False positives: {fp}")
            print(f"False negatives: {fn}")
            print(f"Average speed: {avg_time:.4f}s per URL")
            
            if accuracy >= 90 and avg_time < 0.2 and fp <= 2:
                print("🎉 System is ready for production!")
            else:
                print("⚠ Consider improvements before production deployment")
        else:
            print("Usage: python test_enhanced_phishing.py [quick|benchmark|export|all]")
            print("  quick     - Test specific cases only")
            print("  benchmark - Performance benchmark only") 
            print("  export    - Export test results to JSON")
            print("  all       - Run comprehensive tests")
            print("  (no args) - Run standard test suite")
    else:
        # Default: run standard tests
        accuracy, fp, fn = test_enhanced_detector()
        
        if accuracy < 90:
            print("\n⚠ Accuracy below 90%. Running additional diagnostics...")
            test_specific_cases()

if __name__ == "__main__":
    main()