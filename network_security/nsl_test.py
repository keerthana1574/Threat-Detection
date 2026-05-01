# backend/modules/network_security/nsl_test.py
import sys
import os
import numpy as np

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from nsl_detector import NSLNetworkDetector

def test_nsl_detector():
    """Test the NSL-KDD network detector"""
    
    print("Testing NSL-KDD Network Intrusion Detection System")
    print("="*60)
    
    # Initialize detector
    detector = NSLNetworkDetector('backend/models/network_security')
    
    # Test cases with different attack patterns
    test_packets = [
        # Normal HTTP traffic
        {
            'src_ip': '192.168.1.100',
            'dst_ip': '93.184.216.34',
            'protocol': 'tcp',
            'service': 'http',
            'flag': 'SF',
            'duration': 1.5,
            'src_bytes': 512,
            'dst_bytes': 2048,
            'count': 3,
            'srv_count': 2,
            'serror_rate': 0.0,
            'srv_serror_rate': 0.0
        },
        
        # DoS attack pattern (SYN flood)
        {
            'src_ip': '10.0.0.50',
            'dst_ip': '192.168.1.1',
            'protocol': 'tcp',
            'service': 'http',
            'flag': 'S0',
            'duration': 0,
            'src_bytes': 0,
            'dst_bytes': 0,
            'count': 500,
            'srv_count': 1,
            'serror_rate': 1.0,
            'srv_serror_rate': 1.0
        },
        
        # Port scan (Probe attack)
        {
            'src_ip': '203.0.113.10',
            'dst_ip': '192.168.1.1',
            'protocol': 'tcp',
            'service': 'other',
            'flag': 'REJ',
            'duration': 0,
            'src_bytes': 40,
            'dst_bytes': 0,
            'count': 1,
            'srv_count': 1,
            'serror_rate': 0.5,
            'srv_serror_rate': 0.8
        },
        
        # Suspicious FTP activity (R2L)
        {
            'src_ip': '203.0.113.25',
            'dst_ip': '192.168.1.10',
            'protocol': 'tcp',
            'service': 'ftp',
            'flag': 'SF',
            'duration': 30,
            'src_bytes': 1024,
            'dst_bytes': 50000,
            'count': 10,
            'srv_count': 1,
            'num_failed_logins': 5,
            'serror_rate': 0.2
        },
        
        # Root shell activity (U2R)
        {
            'src_ip': '192.168.1.200',
            'dst_ip': '192.168.1.5',
            'protocol': 'tcp',
            'service': 'telnet',
            'flag': 'SF',
            'duration': 120,
            'src_bytes': 2048,
            'dst_bytes': 4096,
            'count': 1,
            'srv_count': 1,
            'root_shell': 1,
            'su_attempted': 1
        }

        # Add this to your test to see threat detection:

    ]

    # suspicious_packet = {
    #         'protocol': 'tcp',
    #         'service': 'http',
    #         'flag': 'S0',  # Connection attempt failed
    #         'src_bytes': 0,
    #         'dst_bytes': 0,
    #         'count': 1000,  # Very high connection count
    #         'serror_rate': 1.0,  # 100% error rate
    #         'srv_serror_rate': 1.0
    #     }
    
    # Test individual packets
    for i, packet in enumerate(test_packets, 1):
        print(f"\nTest {i}: {packet['src_ip']} -> {packet['dst_ip']} ({packet['service']})")
        
        result = detector.detect_intrusion(packet)
        
        if 'error' in result:
            print(f"Error: {result['error']}")
            continue
        
        print(f"Intrusion Detected: {'YES' if result['is_intrusion'] else 'NO'}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"Attack Type: {result.get('attack_type', 'N/A')}")
        print(f"Severity: {result.get('severity', 'N/A')}")
        
        if 'individual_predictions' in result and result['individual_predictions']:
            print("Model Predictions:")
            for model, pred in result['individual_predictions'].items():
                print(f"  {model}: {pred:.3f}")
    
    # Test batch analysis
    print("\n" + "="*60)
    print("BATCH ANALYSIS TEST")
    print("="*60)
    
    batch_result = detector.analyze_traffic_batch(test_packets)
    
    print("Traffic Analysis Summary:")
    summary = batch_result['summary']
    print(f"Total Packets: {summary['total_packets']}")
    print(f"Threats Detected: {summary['threats_detected']}")
    print(f"Threat Rate: {summary['threat_rate']:.2%}")
    
    if summary['attack_types']:
        print("Attack Types:")
        for attack_type, count in summary['attack_types'].items():
            print(f"  {attack_type}: {count}")
    
    if summary['severity_distribution']:
        print("Severity Distribution:")
        for severity, count in summary['severity_distribution'].items():
            print(f"  {severity}: {count}")

def test_performance():
    """Test detection performance"""
    import time
    
    detector = NSLNetworkDetector('backend/models/network_security')
    
    # Generate test packets
    test_packets = []
    for i in range(100):
        packet = {
            'src_ip': f'192.168.1.{i%254 + 1}',
            'dst_ip': '8.8.8.8',
            'protocol': 'tcp',
            'service': 'http',
            'flag': 'SF',
            'duration': np.random.uniform(0, 5),
            'src_bytes': np.random.randint(0, 10000),
            'dst_bytes': np.random.randint(0, 10000),
            'count': np.random.randint(1, 50),
            'srv_count': np.random.randint(1, 10)
        }
        test_packets.append(packet)
    
    print(f"\nPerformance Test: Analyzing {len(test_packets)} packets...")
    
    start_time = time.time()
    batch_result = detector.analyze_traffic_batch(test_packets)
    end_time = time.time()
    
    total_time = end_time - start_time
    packets_per_second = len(test_packets) / total_time
    
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Packets per second: {packets_per_second:.2f}")
    print(f"Average time per packet: {total_time/len(test_packets):.4f} seconds")
    
    print(f"\nDetection Results:")
    print(f"Threats detected: {batch_result['summary']['threats_detected']}")
    print(f"Threat rate: {batch_result['summary']['threat_rate']:.2%}")

def main():
    """Main testing function"""
    # Check if models exist
    model_dir = 'backend/models/network_security'
    if not os.path.exists(f"{model_dir}/random_forest_model.pkl"):
        print("Models not found! Please run training first:")
        print("python backend/modules/network_security/train.py")
        return
    
    try:
        test_nsl_detector()
        test_performance()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
