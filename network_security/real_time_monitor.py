# backend/modules/network_security/real_time_monitor.py
import time
import threading
from scapy.all import sniff, IP, TCP, UDP
from collections import deque
import json
import logging

logger = logging.getLogger(__name__)

class NetworkTrafficMonitor:
    def __init__(self, detector, interface='eth0'):
        self.detector = detector
        self.interface = interface
        self.is_monitoring = False
        self.packet_buffer = deque(maxlen=1000)  # Keep last 1000 packets
        self.threat_callback = None
        
    def start_monitoring(self, threat_callback=None):
        """Start real-time network monitoring"""
        self.threat_callback = threat_callback
        self.is_monitoring = True
        
        print(f"Starting network monitoring on interface: {self.interface}")
        
        # Start packet capture in separate thread
        monitor_thread = threading.Thread(target=self._monitor_traffic)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return monitor_thread
    
    def stop_monitoring(self):
        """Stop network monitoring"""
        self.is_monitoring = False
        print("Network monitoring stopped")
    
    def _monitor_traffic(self):
        """Monitor network traffic and analyze packets"""
        try:
            sniff(
                iface=self.interface,
                prn=self._packet_handler,
                stop_filter=lambda x: not self.is_monitoring,
                store=0  # Don't store packets in memory
            )
        except Exception as e:
            logger.error(f"Error monitoring network traffic: {e}")
    
    def _packet_handler(self, packet):
        """Handle each captured packet"""
        try:
            # Extract packet features
            packet_data = self._extract_packet_features(packet)
            
            if packet_data:
                # Add to buffer
                self.packet_buffer.append(packet_data)
                
                # Analyze packet for intrusions
                result = self.detector.detect_intrusion(packet_data)
                
                # If intrusion detected, call callback
                if result.get('is_intrusion', False) and self.threat_callback:
                    self.threat_callback({
                        'type': 'network_intrusion',
                        'data': result,
                        'timestamp': result.get('timestamp')
                    })
                
        except Exception as e:
            logger.error(f"Error handling packet: {e}")
    
    def _extract_packet_features(self, packet):
        """Extract features from captured packet"""
        try:
            features = {}
            
            # Basic packet info
            if IP in packet:
                features['src_ip'] = packet[IP].src
                features['dst_ip'] = packet[IP].dst
                features['protocol'] = 'tcp' if TCP in packet else 'udp' if UDP in packet else 'other'
            else:
                return None  # Skip non-IP packets
            
            # Packet size
            features['src_bytes'] = len(packet)
            features['dst_bytes'] = 0  # This would need bidirectional tracking
            
            # Protocol specifics
            if TCP in packet:
                features['service'] = self._identify_service(packet[TCP].dport)
                features['flag'] = self._get_tcp_flags(packet[TCP])
            elif UDP in packet:
                features['service'] = self._identify_service(packet[UDP].dport)
                features['flag'] = 'UDP'
            else:
                features['service'] = 'other'
                features['flag'] = 'other'
            
            # Default values for other features
            features['duration'] = 0  # Would need connection tracking
            features['land'] = 1 if features['src_ip'] == features['dst_ip'] else 0
            features['wrong_fragment'] = 0
            features['urgent'] = 0
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting packet features: {e}")
            return None
    
    def _identify_service(self, port):
        """Identify service based on port number"""
        port_mapping = {
            21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp',
            53: 'dns', 80: 'http', 110: 'pop3', 143: 'imap',
            443: 'https', 993: 'imaps', 995: 'pop3s'
        }
        return port_mapping.get(port, 'other')
    
    def _get_tcp_flags(self, tcp_layer):
        """Get TCP flags as string"""
        flags = []
        if tcp_layer.flags.S: flags.append('S')  # SYN
        if tcp_layer.flags.A: flags.append('A')  # ACK
        if tcp_layer.flags.F: flags.append('F')  # FIN
        if tcp_layer.flags.R: flags.append('R')  # RST
        if tcp_layer.flags.P: flags.append('P')  # PSH
        if tcp_layer.flags.U: flags.append('U')  # URG
        
        if not flags:
            return 'NULL'
        elif 'S' in flags and 'A' in flags:
            return 'SF'  # Normal connection
        elif 'S' in flags and 'R' in flags:
            return 'S0'  # Connection attempt rejected
        else:
            return ''.join(flags)
    
    def get_traffic_statistics(self):
        """Get current traffic statistics"""
        if not self.packet_buffer:
            return {'message': 'No traffic data available'}
        
        packets_df = pd.DataFrame(list(self.packet_buffer))
        
        stats = {
            'total_packets': len(packets_df),
            'unique_src_ips': packets_df['src_ip'].nunique(),
            'unique_dst_ips': packets_df['dst_ip'].nunique(),
            'protocol_distribution': packets_df['protocol'].value_counts().to_dict(),
            'service_distribution': packets_df['service'].value_counts().to_dict(),
            'avg_packet_size': packets_df['src_bytes'].mean(),
            'timestamp': time.time()
        }
        
        return stats
