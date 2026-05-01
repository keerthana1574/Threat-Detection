# backend/modules/network_security/packet_capture.py
import socket
import struct
from datetime import datetime
import threading
import time

class LivePacketCapture:
    def __init__(self):
        self.capturing = False
        self.packets = []
        self.stats = {
            'total_packets': 0,
            'tcp_count': 0,
            'udp_count': 0,
            'icmp_count': 0,
            'other_count': 0,
            'total_bytes': 0
        }
        
    def start_capture(self, interface='eth0', callback=None):
        """Start capturing packets"""
        self.capturing = True
        self.callback = callback
        
        # Start capture thread
        capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        capture_thread.start()
        
    def _capture_loop(self):
        """Main packet capture loop"""
        try:
            # Create raw socket (requires admin/root)
            sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
            
            while self.capturing:
                # Receive packet
                packet, addr = sock.recvfrom(65535)
                
                # Parse packet
                parsed = self._parse_packet(packet)
                
                if parsed:
                    self.packets.append(parsed)
                    self.stats['total_packets'] += 1
                    self.stats['total_bytes'] += len(packet)
                    
                    # Update protocol stats
                    proto = parsed.get('protocol', 'other').lower()
                    if proto == 'tcp':
                        self.stats['tcp_count'] += 1
                    elif proto == 'udp':
                        self.stats['udp_count'] += 1
                    elif proto == 'icmp':
                        self.stats['icmp_count'] += 1
                    else:
                        self.stats['other_count'] += 1
                    
                    # Callback for real-time emission
                    if self.callback:
                        self.callback(parsed)
                        
        except PermissionError:
            print("[ERROR] Packet capture requires administrator/root privileges")
        except Exception as e:
            print(f"[ERROR] Packet capture error: {e}")
            
    def _parse_packet(self, packet):
        """Parse raw packet data"""
        try:
            # Ethernet header (14 bytes)
            eth_header = packet[:14]
            eth = struct.unpack('!6s6sH', eth_header)
            eth_protocol = socket.ntohs(eth[2])
            
            # IP packet
            if eth_protocol == 8:  # IPv4
                ip_header = packet[14:34]
                iph = struct.unpack('!BBHHHBBH4s4s', ip_header)
                
                version_ihl = iph[0]
                ihl = version_ihl & 0xF
                iph_length = ihl * 4
                
                protocol = iph[6]
                src_ip = socket.inet_ntoa(iph[8])
                dst_ip = socket.inet_ntoa(iph[9])
                
                # Determine protocol
                if protocol == 6:  # TCP
                    proto_name = 'TCP'
                    tcp_header = packet[14 + iph_length:14 + iph_length + 20]
                    tcph = struct.unpack('!HHLLBBHHH', tcp_header)
                    src_port = tcph[0]
                    dst_port = tcph[1]
                elif protocol == 17:  # UDP
                    proto_name = 'UDP'
                    udp_header = packet[14 + iph_length:14 + iph_length + 8]
                    udph = struct.unpack('!HHHH', udp_header)
                    src_port = udph[0]
                    dst_port = udph[1]
                elif protocol == 1:  # ICMP
                    proto_name = 'ICMP'
                    src_port = None
                    dst_port = None
                else:
                    proto_name = 'OTHER'
                    src_port = None
                    dst_port = None
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    'protocol': proto_name,
                    'src_ip': src_ip,
                    'dst_ip': dst_ip,
                    'src_port': src_port,
                    'dst_port': dst_port,
                    'size': len(packet),
                    'type': 'normal'  # Will be marked as 'threat' if ML detects anomaly
                }
                
        except Exception as e:
            return None
            
    def stop_capture(self):
        """Stop packet capture"""
        self.capturing = False
        
    def get_stats(self):
        """Get capture statistics"""
        return self.stats