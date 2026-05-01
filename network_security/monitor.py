# backend/modules/network_security/monitor.py (Real-time monitoring script)
import sys
import os
import time
import signal
import json

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.modules.network_security.nsl_detector import NetworkIntrusionDetector
from real_time_monitor import NetworkTrafficMonitor

class ThreatLogger:
    def __init__(self, log_file='logs/network_security/threats.log'):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        self.log_file = log_file
    
    def log_threat(self, threat_data):
        """Log detected threats"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_entry = {
            'timestamp': timestamp,
            'threat': threat_data
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Print to console
        threat = threat_data['data']
        print(f"\n🚨 THREAT DETECTED at {timestamp}")
        print(f"   Attack Type: {threat.get('attack_type', 'Unknown')}")
        print(f"   Severity: {threat.get('severity', 'Unknown')}")
        print(f"   Confidence: {threat.get('confidence', 0):.3f}")
        print(f"   Source: {threat['packet_info']['src_ip']}")
        print(f"   Target: {threat['packet_info']['dst_ip']}")

def main():
    """Main monitoring function"""
    print("Real-time Network Intrusion Detection Monitor")
    print("="*60)
    
    # Initialize components
    detector = NetworkIntrusionDetector('backend/models/network_security')
    threat_logger = ThreatLogger()
    
    # Setup monitoring
    interface = 'eth0'  # Change to your network interface
    if os.name == 'nt':  # Windows
        interface = 'WiFi'  # Common Windows interface name
    
    monitor = NetworkTrafficMonitor(detector, interface=interface)
    
    # Setup signal handler for graceful shutdown
    def signal_handler(sig, frame):
        print("\nStopping network monitoring...")
        monitor.stop_monitoring()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        print(f"Starting monitoring on interface: {interface}")
        print("Press Ctrl+C to stop monitoring...")
        
        # Start monitoring with threat callback
        monitor.start_monitoring(threat_callback=threat_logger.log_threat)
        
        # Keep main thread alive and show statistics
        while monitor.is_monitoring:
            time.sleep(10)  # Update every 10 seconds
            
            stats = monitor.get_traffic_statistics()
            if 'total_packets' in stats:
                print(f"\r📊 Packets analyzed: {stats['total_packets']}, "
                      f"Unique IPs: {stats['unique_src_ips']}/{stats['unique_dst_ips']}", 
                      end='', flush=True)
    
    except Exception as e:
        print(f"Error during monitoring: {e}")
    finally:
        monitor.stop_monitoring()

if __name__ == "__main__":
    # Check if models exist
    model_dir = 'backend/models/network_security'
    if not os.path.exists(f"{model_dir}/random_forest_model.pkl"):
        print("Models not found! Please run training first:")
        print("python backend/modules/network_security/train.py")
        sys.exit(1)
    
    main()
