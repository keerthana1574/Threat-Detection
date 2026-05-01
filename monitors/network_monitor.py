import scapy.all as scapy
import threading
import time
import psutil
import socket
from datetime import datetime, timedelta
from collections import defaultdict, deque
from config.database import db_manager
from modules.network_security.ddos_detector import DDoSDetector
from modules.network_security.anomaly_detector import NetworkAnomalyDetector
from utils.alert_system import AlertSystem
import logging

class NetworkMonitor:
    def __init__(self):
        self.ddos_detector = DDoSDetector()
        self.anomaly_detector = NetworkAnomalyDetector()
        self.alert_system = AlertSystem()
        self.is_monitoring = False
        
        # Traffic tracking
        self.packet_counts = defaultdict(int)
        self.connection_counts = defaultdict(int)
        self.traffic_history = deque(maxlen=1000)
        self.suspicious_ips = set()
        
        # Thresholds
        self.ddos_threshold = 1000  # packets per minute
        self.anomaly_threshold = 0.8
        
    def start_monitoring(self, interface=None):
        """Start network monitoring"""
        if self.is_monitoring:
            return {"error": "Network monitoring already active"}
        
        self.is_monitoring = True
        
        # Get default interface if not specified
        if not interface:
            interface = self._get_default_interface()
        
        # Start packet capture in separate thread
        capture_thread = threading.Thread(
            target=self._capture_packets,
            args=(interface,)
        )
        capture_thread.daemon = True
        capture_thread.start()
        
        # Start analysis thread
        analysis_thread = threading.Thread(target=self._analyze_traffic)
        analysis_thread.daemon = True
        analysis_thread.start()
        
        return {"success": f"Network monitoring started on interface {interface}"}
    
    def stop_monitoring(self):
        """Stop network monitoring"""
        self.is_monitoring = False
        return {"success": "Network monitoring stopped"}
    
    def _get_default_interface(self):
        """Get default network interface"""
        try:
            # Get the interface with default route
            gateways = scapy.conf.route.route("0.0.0.0")
            return gateways[0]
        except:
            # Fallback to first available interface
            interfaces = psutil.net_if_addrs()
            for interface in interfaces:
                if interface != 'lo' and interface != 'Loopback':
                    return interface
            return 'eth0'  # Final fallback
    
    def _capture_packets(self, interface):
        """Capture network packets"""
        try:
            scapy.sniff(
                iface=interface,
                prn=self._process_packet,
                stop_filter=lambda x: not self.is_monitoring,
                store=False
            )
        except Exception as e:
            logging.error(f"Packet capture error: {e}")
    
    def _process_packet(self, packet):
        """Process individual packet"""
        try:
            timestamp = datetime.now()
            
            # Extract packet information
            packet_info = {
                'timestamp': timestamp,
                'size': len(packet),
                'protocol': packet.proto if hasattr(packet, 'proto') else 'unknown'
            }
            
            # Extract IP information
            if packet.haslayer(scapy.IP):
                ip_layer = packet[scapy.IP]
                packet_info.update({
                    'src_ip': ip_layer.src,
                    'dst_ip': ip_layer.dst,
                    'protocol': ip_layer.proto
                })
                
                # Count packets per IP
                self.packet_counts[ip_layer.src] += 1
            
            # Extract TCP information
            if packet.haslayer(scapy.TCP):
                tcp_layer = packet[scapy.TCP]
                packet_info.update({
                    'src_port': tcp_layer.sport,
                    'dst_port': tcp_layer.dport,
                    'flags': tcp_layer.flags
                })
                
                # Check for potential attacks
                self._check_tcp_attacks(packet_info)
            
            # Extract UDP information
            if packet.haslayer(scapy.UDP):
                udp_layer = packet[scapy.UDP]
                packet_info.update({
                    'src_port': udp_layer.sport,
                    'dst_port': udp_layer.dport
                })
            
            # Add to traffic history
            self.traffic_history.append(packet_info)
            
            # Log to MongoDB
            mongo_collection = db_manager.get_mongo_collection('network_packets')
            mongo_collection.insert_one({
                **packet_info,
                'timestamp': timestamp.isoformat()
            })
            
        except Exception as e:
            logging.error(f"Packet processing error: {e}")
    
    def _check_tcp_attacks(self, packet_info):
        """Check for TCP-based attacks"""
        try:
            # SYN flood detection
            if packet_info.get('flags') == 2:  # SYN flag
                src_ip = packet_info.get('src_ip')
                if src_ip:
                    self.connection_counts[src_ip] += 1
                    
                    # Check if threshold exceeded
                    if self.connection_counts[src_ip] > 100:  # 100 SYN packets
                        self._log_threat(
                            threat_type='syn_flood',
                            description=f'Potential SYN flood from {src_ip}',
                            source_ip=src_ip,
                            severity='high'
                        )
                        
                        self.suspicious_ips.add(src_ip)
            
            # Port scanning detection
            dst_port = packet_info.get('dst_port')
            src_ip = packet_info.get('src_ip')
            
            if dst_port and src_ip:
                # Track port scanning behavior
                # This is a simplified detection
                if dst_port in [22, 23, 80, 443, 3389]:  # Common ports
                    self._check_port_scanning(src_ip, dst_port)
                    
        except Exception as e:
            logging.error(f"TCP attack check error: {e}")
    
    def _check_port_scanning(self, src_ip, dst_port):
        """Check for port scanning patterns"""
        # Simple port scanning detection
        # In production, use more sophisticated algorithms
        pass
    
    def _analyze_traffic(self):
        """Analyze traffic patterns for anomalies"""
        while self.is_monitoring:
            try:
                time.sleep(60)  # Analyze every minute
                
                # Check for DDoS patterns
                self._check_ddos_patterns()
                
                # Check for network anomalies
                self._check_network_anomalies()
                
                # Reset counters periodically
                self._reset_counters()
                
            except Exception as e:
                logging.error(f"Traffic analysis error: {e}")
    
    def _check_ddos_patterns(self):
        """Check for DDoS attack patterns"""
        try:
            current_time = datetime.now()
            
            # Check packet rates per IP
            for ip, count in self.packet_counts.items():
                if count > self.ddos_threshold:
                    # Potential DDoS detected
                    self._log_threat(
                        threat_type='ddos',
                        description=f'Potential DDoS attack from {ip}: {count} packets/min',
                        source_ip=ip,
                        severity='critical'
                    )
                    
                    # Send alert
                    self.alert_system.send_alert(
                        alert_type='ddos',
                        message=f'DDoS attack detected from {ip}',
                        severity='critical'
                    )
            
        except Exception as e:
            logging.error(f"DDoS pattern check error: {e}")
    
    def _check_network_anomalies(self):
        """Check for network anomalies using ML model"""
        try:
            if len(self.traffic_history) < 100:
                return
            
            # Prepare traffic features for analysis
            traffic_features = self._extract_traffic_features()
            
            # Use anomaly detector
            anomaly_result = self.anomaly_detector.predict(traffic_features)
            
            if anomaly_result['prediction']:
                self._log_threat(
                    threat_type='network_anomaly',
                    description='Unusual network traffic pattern detected',
                    source_ip='multiple',
                    severity='medium'
                )
                
                self.alert_system.send_alert(
                    alert_type='network_anomaly',
                    message='Network anomaly detected',
                    severity='medium'
                )
            
        except Exception as e:
            logging.error(f"Network anomaly check error: {e}")
    
    def _extract_traffic_features(self):
        """Extract features from traffic history for ML analysis"""
        try:
            # Simple feature extraction
            recent_traffic = list(self.traffic_history)[-100:]
            
            features = {
                'packet_count': len(recent_traffic),
                'avg_packet_size': sum(p.get('size', 0) for p in recent_traffic) / len(recent_traffic),
                'unique_ips': len(set(p.get('src_ip') for p in recent_traffic if p.get('src_ip'))),
                'tcp_ratio': len([p for p in recent_traffic if p.get('protocol') == 6]) / len(recent_traffic),
                'udp_ratio': len([p for p in recent_traffic if p.get('protocol') == 17]) / len(recent_traffic)
            }
            
            return features
            
        except Exception as e:
            logging.error(f"Feature extraction error: {e}")
            return {}
    
    def _reset_counters(self):
        """Reset packet counters periodically"""
        # Reset hourly
        current_time = datetime.now()
        if current_time.minute == 0:
            self.packet_counts.clear()
            self.connection_counts.clear()
    
    def _log_threat(self, threat_type, description, source_ip, severity):
        """Log network threat to database"""
        try:
            cursor = db_manager.get_postgres_cursor()
            cursor.execute("""
                INSERT INTO threat_logs (threat_type, description, source_ip, severity)
                VALUES (%s, %s, %s, %s)
            """, (threat_type, description, source_ip, severity))
            
        except Exception as e:
            logging.error(f"Database logging error: {e}")
    
    def get_monitoring_status(self):
        """Get network monitoring status"""
        return {
            'is_monitoring': self.is_monitoring,
            'total_packets': sum(self.packet_counts.values()),
            'unique_ips': len(self.packet_counts),
            'suspicious_ips': len(self.suspicious_ips),
            'traffic_history_size': len(self.traffic_history)
        }

# Global network monitor instance
network_monitor = NetworkMonitor()