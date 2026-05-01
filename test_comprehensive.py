#!/usr/bin/env python3
"""
Comprehensive Test Suite for AI Cybersecurity Threat Detection System
Tests all modules including enhanced detectors and real-time monitoring
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
import threading

# Base URL for the API
BASE_URL = "http://localhost:5000"

class ComprehensiveTester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_results': {}
        }

    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive AI Cybersecurity Test Suite")
        print("=" * 60)

        # Test system health first
        if not self.test_system_health():
            print("❌ System health check failed. Aborting tests.")
            return False

        # Run individual module tests
        test_modules = [
            ('Cyberbullying Detection', self.test_cyberbullying_detection),
            ('Fake News Detection', self.test_fake_news_detection),
            ('Phishing Detection', self.test_phishing_detection),
            ('SQL Injection Detection', self.test_sql_injection_detection),
            ('XSS Detection', self.test_xss_detection),
            ('Network Security', self.test_network_security),
            ('Social Media Monitoring', self.test_social_media_monitoring),
            ('Real-time Systems', self.test_realtime_systems),
            ('API Endpoints', self.test_api_endpoints),
        ]

        for module_name, test_func in test_modules:
            print(f"\n🔍 Testing {module_name}...")
            try:
                success = test_func()
                self.results['test_results'][module_name] = {
                    'status': 'PASSED' if success else 'FAILED',
                    'timestamp': datetime.now().isoformat()
                }
                if success:
                    print(f"✅ {module_name} tests PASSED")
                    self.results['passed_tests'] += 1
                else:
                    print(f"❌ {module_name} tests FAILED")
                    self.results['failed_tests'] += 1
            except Exception as e:
                print(f"💥 {module_name} tests CRASHED: {e}")
                self.results['test_results'][module_name] = {
                    'status': 'CRASHED',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                self.results['failed_tests'] += 1

            self.results['total_tests'] += 1

        # Print final results
        self.print_final_results()
        return self.results['failed_tests'] == 0

    def test_system_health(self):
        """Test system health and basic connectivity"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ System Status: {health_data.get('status', 'unknown')}")
                print(f"📊 Detector Status: {health_data.get('detector_status', {})}")
                return True
            else:
                print(f"❌ Health check failed with status: {response.status_code}")
                return False
        except Exception as e:
            print(f"💥 Cannot connect to system: {e}")
            return False

    def test_cyberbullying_detection(self):
        """Test cyberbullying detection with various inputs"""
        test_cases = [
            {
                'text': 'You are so stupid and worthless, go kill yourself!',
                'expected': True,
                'description': 'Severe cyberbullying'
            },
            {
                'text': 'Have a great day everyone! Hope you achieve your goals.',
                'expected': False,
                'description': 'Positive message'
            },
            {
                'text': 'I hate you so much, you ugly loser.',
                'expected': True,
                'description': 'Moderate cyberbullying'
            },
            {
                'text': 'Thank you for helping me with my homework.',
                'expected': False,
                'description': 'Neutral/positive'
            }
        ]

        passed = 0
        for i, case in enumerate(test_cases):
            try:
                response = self.session.post(
                    f"{self.base_url}/api/cyberbullying/predict",
                    json={'text': case['text']},
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    prediction = result.get('prediction', False)

                    if prediction == case['expected']:
                        print(f"  ✅ Test {i+1}: {case['description']}")
                        passed += 1
                    else:
                        print(f"  ❌ Test {i+1}: {case['description']} - Expected: {case['expected']}, Got: {prediction}")
                else:
                    print(f"  ❌ Test {i+1}: HTTP {response.status_code}")

            except Exception as e:
                print(f"  💥 Test {i+1}: {e}")

        return passed == len(test_cases)

    def test_fake_news_detection(self):
        """Test fake news detection"""
        test_cases = [
            {
                'text': 'BREAKING: Scientists discover that vaccines contain microchips for mind control!',
                'expected': True,
                'description': 'Obvious fake news'
            },
            {
                'text': 'A new study published in Nature shows promising results for cancer treatment.',
                'expected': False,
                'description': 'Legitimate news'
            },
            {
                'text': 'SHOCKING: Aliens landed in Times Square, government covers it up!',
                'expected': True,
                'description': 'Sensational fake news'
            }
        ]

        passed = 0
        for i, case in enumerate(test_cases):
            try:
                response = self.session.post(
                    f"{self.base_url}/api/fake_news/predict",
                    json={'text': case['text']},
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    prediction = result.get('prediction', False)

                    if prediction == case['expected']:
                        print(f"  ✅ Test {i+1}: {case['description']}")
                        passed += 1
                    else:
                        print(f"  ❌ Test {i+1}: {case['description']} - Expected: {case['expected']}, Got: {prediction}")
                else:
                    print(f"  ❌ Test {i+1}: HTTP {response.status_code}")

            except Exception as e:
                print(f"  💥 Test {i+1}: {e}")

        return passed >= len(test_cases) * 0.7  # 70% success rate

    def test_phishing_detection(self):
        """Test phishing URL detection"""
        test_cases = [
            {
                'url': 'https://www.google.com',
                'expected': False,
                'description': 'Legitimate Google URL'
            },
            {
                'url': 'https://www.g00gle.com/login',
                'expected': True,
                'description': 'Google typosquatting'
            },
            {
                'url': 'https://www.microsoft.com',
                'expected': False,
                'description': 'Legitimate Microsoft URL'
            },
            {
                'url': 'https://micros0ft.com/security',
                'expected': True,
                'description': 'Microsoft typosquatting'
            },
            {
                'url': 'http://payp4l.com/update-account',
                'expected': True,
                'description': 'PayPal phishing'
            }
        ]

        passed = 0
        for i, case in enumerate(test_cases):
            try:
                response = self.session.post(
                    f"{self.base_url}/api/phishing/predict",
                    json={'url': case['url']},
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    prediction = result.get('prediction', False)

                    if prediction == case['expected']:
                        print(f"  ✅ Test {i+1}: {case['description']}")
                        passed += 1
                    else:
                        print(f"  ❌ Test {i+1}: {case['description']} - Expected: {case['expected']}, Got: {prediction}")
                else:
                    print(f"  ❌ Test {i+1}: HTTP {response.status_code}")

            except Exception as e:
                print(f"  💥 Test {i+1}: {e}")

        return passed >= len(test_cases) * 0.8  # 80% success rate

    def test_sql_injection_detection(self):
        """Test SQL injection detection"""
        test_cases = [
            {
                'text': "SELECT * FROM users WHERE id = 1",
                'expected': False,
                'description': 'Normal SQL query'
            },
            {
                'text': "' OR '1'='1",
                'expected': True,
                'description': 'Basic SQL injection'
            },
            {
                'text': "'; DROP TABLE users; --",
                'expected': True,
                'description': 'Destructive SQL injection'
            },
            {
                'text': "admin' --",
                'expected': True,
                'description': 'Comment-based injection'
            },
            {
                'text': "username123",
                'expected': False,
                'description': 'Normal input'
            }
        ]

        passed = 0
        for i, case in enumerate(test_cases):
            try:
                response = self.session.post(
                    f"{self.base_url}/api/sql_injection/predict",
                    json={'text': case['text']},
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    prediction = result.get('prediction', False)

                    if prediction == case['expected']:
                        print(f"  ✅ Test {i+1}: {case['description']}")
                        passed += 1
                    else:
                        print(f"  ❌ Test {i+1}: {case['description']} - Expected: {case['expected']}, Got: {prediction}")
                else:
                    print(f"  ❌ Test {i+1}: HTTP {response.status_code}")

            except Exception as e:
                print(f"  💥 Test {i+1}: {e}")

        return passed >= len(test_cases) * 0.8  # 80% success rate

    def test_xss_detection(self):
        """Test XSS detection"""
        test_cases = [
            {
                'text': '<script>alert("XSS")</script>',
                'expected': True,
                'description': 'Basic XSS script'
            },
            {
                'text': 'Hello world!',
                'expected': False,
                'description': 'Normal text'
            },
            {
                'text': '<iframe src="javascript:alert(1)"></iframe>',
                'expected': True,
                'description': 'Iframe XSS'
            },
            {
                'text': 'javascript:alert(document.cookie)',
                'expected': True,
                'description': 'JavaScript protocol XSS'
            },
            {
                'text': '<div onclick="alert(1)">Click me</div>',
                'expected': True,
                'description': 'Event handler XSS'
            }
        ]

        passed = 0
        for i, case in enumerate(test_cases):
            try:
                response = self.session.post(
                    f"{self.base_url}/api/xss/predict",
                    json={'text': case['text']},
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    prediction = result.get('prediction', False)

                    if prediction == case['expected']:
                        print(f"  ✅ Test {i+1}: {case['description']}")
                        passed += 1
                    else:
                        print(f"  ❌ Test {i+1}: {case['description']} - Expected: {case['expected']}, Got: {prediction}")
                else:
                    print(f"  ❌ Test {i+1}: HTTP {response.status_code}")

            except Exception as e:
                print(f"  💥 Test {i+1}: {e}")

        return passed >= len(test_cases) * 0.8  # 80% success rate

    def test_network_security(self):
        """Test network security features"""
        try:
            # Test if network monitoring endpoints exist
            response = self.session.get(f"{self.base_url}/api/network/status", timeout=10)
            print(f"  📊 Network status endpoint: {response.status_code}")

            # Test metrics endpoint
            response = self.session.get(f"{self.base_url}/api/metrics", timeout=10)
            if response.status_code == 200:
                metrics = response.json()
                print(f"  ✅ Metrics available: {metrics.get('metrics', {})}")
                return True
            else:
                print(f"  ⚠️ Metrics endpoint returned {response.status_code}")
                return False

        except Exception as e:
            print(f"  💥 Network security test failed: {e}")
            return False

    def test_social_media_monitoring(self):
        """Test social media monitoring capabilities"""
        try:
            # Test starting social media monitoring
            response = self.session.post(
                f"{self.base_url}/api/realtime/social-media/start",
                json={},
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ Social media monitoring started: {result.get('status')}")

                # Test stopping monitoring
                response = self.session.post(
                    f"{self.base_url}/api/realtime/social-media/stop",
                    timeout=10
                )

                if response.status_code == 200:
                    result = response.json()
                    print(f"  ✅ Social media monitoring stopped: {result.get('status')}")
                    return True

            return False

        except Exception as e:
            print(f"  💥 Social media monitoring test failed: {e}")
            return False

    def test_realtime_systems(self):
        """Test real-time monitoring and alerting"""
        try:
            # Test alerts endpoint
            response = self.session.get(f"{self.base_url}/api/alerts", timeout=10)
            if response.status_code == 200:
                alerts = response.json()
                print(f"  ✅ Alerts system available: {len(alerts.get('alerts', []))} alerts")

            # Test threats endpoint
            response = self.session.get(f"{self.base_url}/api/threats", timeout=10)
            if response.status_code == 200:
                threats = response.json()
                print(f"  ✅ Threats system available: {len(threats.get('threats', []))} threats")
                return True

            return False

        except Exception as e:
            print(f"  💥 Real-time systems test failed: {e}")
            return False

    def test_api_endpoints(self):
        """Test all API endpoints for basic functionality"""
        endpoints = [
            ('GET', '/'),
            ('GET', '/health'),
            ('GET', '/api/metrics'),
            ('GET', '/api/alerts'),
            ('GET', '/api/threats'),
        ]

        passed = 0
        for method, endpoint in endpoints:
            try:
                if method == 'GET':
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                else:
                    response = self.session.post(f"{self.base_url}{endpoint}", timeout=10)

                if response.status_code in [200, 201]:
                    print(f"  ✅ {method} {endpoint}: {response.status_code}")
                    passed += 1
                else:
                    print(f"  ❌ {method} {endpoint}: {response.status_code}")

            except Exception as e:
                print(f"  💥 {method} {endpoint}: {e}")

        return passed >= len(endpoints) * 0.8  # 80% success rate

    def test_phishing_comprehensive(self):
        """Run comprehensive phishing detection tests"""
        response = self.session.post(f"{self.base_url}/api/phishing/test", timeout=30)
        if response.status_code == 200:
            results = response.json()
            accuracy = results.get('accuracy', 0)
            print(f"  📊 Phishing test accuracy: {accuracy}%")
            return accuracy >= 80  # Require 80% accuracy
        return False

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE TEST RESULTS")
        print("=" * 60)

        print(f"📊 Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed_tests']}")
        print(f"❌ Failed: {self.results['failed_tests']}")

        if self.results['total_tests'] > 0:
            success_rate = (self.results['passed_tests'] / self.results['total_tests']) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")

            if success_rate >= 80:
                print("\n🎉 SYSTEM READY FOR PRODUCTION! 🎉")
            elif success_rate >= 60:
                print("\n⚠️ SYSTEM PARTIALLY READY - SOME ISSUES DETECTED")
            else:
                print("\n🚨 SYSTEM NOT READY - CRITICAL ISSUES FOUND")

        print("\n📋 Detailed Results:")
        for module, result in self.results['test_results'].items():
            status_icon = {"PASSED": "✅", "FAILED": "❌", "CRASHED": "💥"}.get(result['status'], "❓")
            print(f"  {status_icon} {module}: {result['status']}")

        # Save results to file
        self.save_results()

    def save_results(self):
        """Save test results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_results_{timestamp}.json"

        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\n💾 Results saved to: {filename}")
        except Exception as e:
            print(f"\n⚠️ Could not save results: {e}")


def main():
    """Main test execution"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = BASE_URL

    print(f"🎯 Target System: {base_url}")

    tester = ComprehensiveTester(base_url)

    # Run all tests
    success = tester.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()