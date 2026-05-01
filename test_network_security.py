#!/usr/bin/env python3
"""
Test Network Security Module
Simple test to verify DDoS detector works without encoding issues
"""

import sys
import os

# Add backend path
backend_path = os.path.join(os.getcwd(), 'backend', 'modules', 'network_security')
if backend_path not in sys.path:
    sys.path.append(backend_path)

def test_ddos_detector():
    """Test DDoS detector initialization and basic functionality"""
    try:
        print("Testing DDoS Detector...")

        # Import the detector
        from ddos_detector import DDoSDetector, NetworkAnomalyDetector
        print("[SUCCESS] Successfully imported DDoS detector modules")

        # Initialize DDoS detector
        print("Initializing DDoS detector...")
        ddos_detector = DDoSDetector()
        print("[SUCCESS] DDoS detector initialized")

        # Test basic functionality
        print("Testing network interfaces...")
        interfaces = ddos_detector.get_network_interfaces()
        print(f"[INFO] Found {len(interfaces)} network interfaces")
        for iface in interfaces:
            print(f"  - {iface['name']}: {iface['ip']}")

        # Test status
        print("Testing current status...")
        status = ddos_detector.get_current_status()
        print(f"[SUCCESS] Status retrieved: monitoring={status['monitoring_active']}")

        # Test NetworkAnomalyDetector
        print("Testing Network Anomaly Detector...")
        anomaly_detector = NetworkAnomalyDetector()
        print("[SUCCESS] Network anomaly detector initialized")

        # Test metrics collection
        print("Testing metrics collection...")
        metrics = anomaly_detector.collect_network_metrics()
        if metrics:
            print(f"[SUCCESS] Metrics collected: {len(metrics)} fields")
            print(f"  - Bytes sent: {metrics.get('bytes_sent', 0)}")
            print(f"  - Bytes received: {metrics.get('bytes_recv', 0)}")
            print(f"  - Connections: {metrics.get('total_connections', 0)}")
        else:
            print("[WARN] No metrics collected")

        print("\n[SUCCESS] All network security tests passed!")
        return True

    except Exception as e:
        print(f"[ERROR] Network security test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_network_security_api():
    """Test if network security can be integrated with Flask app"""
    try:
        print("\nTesting Flask integration...")

        # Test if we can create detector instances for Flask app
        from ddos_detector import DDoSDetector

        # This simulates what happens in app.py
        detector = DDoSDetector()
        print("[SUCCESS] DDoS detector created for Flask integration")

        # Test getting status (what the API endpoint would call)
        status = detector.get_current_status()
        print(f"[SUCCESS] API-style status call works: {status['monitoring_active']}")

        return True

    except Exception as e:
        print(f"[ERROR] Flask integration test failed: {e}")
        return False

def main():
    print("Network Security Module Test Suite")
    print("=" * 40)

    # Test 1: Basic DDoS detector
    test1_passed = test_ddos_detector()

    # Test 2: Flask integration
    test2_passed = test_network_security_api()

    # Summary
    print("\n" + "=" * 40)
    print("Test Results:")
    print(f"  DDoS Detector Test: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"  Flask Integration Test: {'PASSED' if test2_passed else 'FAILED'}")

    if test1_passed and test2_passed:
        print("\n[SUCCESS] Network security module is working correctly!")
        return True
    else:
        print("\n[ERROR] Network security module has issues!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)