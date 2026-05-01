import scapy.all as scapy
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.l2 import Ether
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import threading
import time
from collections import defaultdict, Counter
import psutil
import netifaces
import socket
import struct

class NetworkTrafficAnalyzer:
    def __init__(self, interface=None):
        self.interface = interface or self.get_default_interface()
        self.traffic_data = []
        self.connection_states = defaultdict(dict)
        self.flow_stats = defaultdict(lambda: defaultdict(int))
        self.monitoring = False
        
    def get_default_interface(self):
        """Get default network interface"""
        try:
            # Get default gateway
            gateways = netifaces.gateways()
            default_interface = gateways['default'][netifaces.AF_INET][1]
            return default_interface
        except:
            return 'eth0'  # Fallback
    
    def extract_features(self, packet):
        """Extract features from network packet"""
        features = {
            'timestamp': datetime.now(),
            'protocol': 0,
            'src_ip': '',
            'dst_ip': '',
            'src_port': 0,
            'dst_port': 0,
            'packet_size': len(packet),
            'flags': [],
            'ttl': 0,
            'window_size': 0,
            'urgent_ptr': 0,
            'options_length': 0
        }
        
        if IP in packet:
            ip_layer = packet[IP]
            features['src_ip'] = ip_layer.src
            features['dst_ip'] = ip_layer.dst
            features['protocol'] = ip_layer.proto
            features['ttl'] = ip_layer.ttl
            features['packet_size'] = ip_layer.len
            
            if TCP in packet:
                tcp_layer = packet[TCP]
                features['src_port'] = tcp_layer.sport
                features['dst_port'] = tcp_layer.dport
                features['flags'] = self.get_tcp_flags(tcp_layer)
                features['window_size'] = tcp_layer.window
                features['urgent_ptr'] = tcp_layer.urgptr
                
            elif UDP in packet:
                udp_layer = packet[UDP]
                features['src_port'] = udp_layer.sport
                features['dst_port'] = udp_layer.dport
                
        return features
    
    def get_tcp_flags(self, tcp_layer):
        """Extract TCP flags from packet"""
        flags = []
        if tcp_layer.flags & 0x01: flags.append('FIN')
        if tcp_layer.flags & 0x02: flags.append('SYN')
        if tcp_layer.flags & 0x04: flags.append('RST')
        if tcp_layer.flags & 0x08: flags.append('PSH')
        if tcp_layer.flags & 0x10: flags.append('ACK')
        if tcp_layer.flags & 0x20: flags.append('URG')
        return flags
    
    def update_flow_stats(self, features):
        """Update flow statistics"""
        flow_key = f"{features['src_ip']}:{features['src_port']}->{features['dst_ip']}:{features['dst_port']}"
        
        self.flow_stats[flow_key]['packet_count'] += 1
        self.flow_stats[flow_key]['byte_count'] += features['packet_size']
        self.flow_stats[flow_key]['last_seen'] = features['timestamp']
        
        if 'first_seen' not in self.flow_stats[flow_key]:
            self.flow_stats[flow_key]['first_seen'] = features['timestamp']
    
    def detect_port_scan(self, src_ip, time_window=60):
        """Detect port scanning behavior"""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(seconds=time_window)
        
        # Count unique destination ports from this source IP
        recent_flows = [
            flow for flow_key, flow_data in self.flow_stats.items()
            if flow_key.startswith(src_ip) and flow_data['last_seen'] > cutoff_time
        ]
        
        unique_ports = set()
        for flow_key in recent_flows:
            dst_port = flow_key.split('->')[1].split(':')[1]
            unique_ports.add(dst_port)
        
        # Port scan threshold
        if len(unique_ports) > 10:  # More than 10 unique ports in time window
            return True, len(unique_ports)
        
        return False, len(unique_ports)
    
    def detect_ddos_indicators(self, time_window=60):
        """Detect DDoS attack indicators"""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(seconds=time_window)
        
        # Analyze traffic in the time window
        recent_traffic = [
            data for data in self.traffic_data
            if data['timestamp'] > cutoff_time
        ]
        
        if len(recent_traffic) < 10:  # Not enough data
            return {'ddos_detected': False, 'confidence': 0}
        
        # Calculate metrics
        packet_rate = len(recent_traffic) / time_window
        
        # Source IP distribution
        src_ips = [data['src_ip'] for data in recent_traffic]
        src_ip_counter = Counter(src_ips)
        unique_sources = len(src_ip_counter)
        
        # Destination analysis
        dst_ips = [data['dst_ip'] for data in recent_traffic]
        dst_ip_counter = Counter(dst_ips)
        
        # Protocol distribution
        protocols = [data['protocol'] for data in recent_traffic]
        protocol_counter = Counter(protocols)
        
        # DDoS indicators
        indicators = {
            'high_packet_rate': packet_rate > 1000,  # More than 1000 packets/second
            'low_source_diversity': unique_sources < 5,  # Few unique sources
            'concentrated_target': max(dst_ip_counter.values()) > len(recent_traffic) * 0.8,  # 80% to single target
            'syn_flood': protocol_counter.get(6, 0) > len(recent_traffic) * 0.5,  # More than 50% TCP
            'udp_flood': protocol_counter.get(17, 0) > len(recent_traffic) * 0.7  # More than 70% UDP
        }
        
        # Calculate confidence
        confidence = sum(indicators.values()) / len(indicators)
        ddos_detected = confidence > 0.6  # 60% threshold
        
        return {
            'ddos_detected': ddos_detected,
            'confidence': confidence,
            'packet_rate': packet_rate,
            'unique_sources': unique_sources,
            'indicators': indicators,
            'top_sources': dict(src_ip_counter.most_common(5)),
            'top_targets': dict(dst_ip_counter.most_common(5))
        }
    
    def packet_handler(self, packet):
        """Handle captured packets"""
        try:
            features = self.extract_features(packet)
            self.traffic_data.append(features)
            self.update_flow_stats(features)
            
            # Keep only recent data (last 5 minutes)
            cutoff_time = datetime.now() - timedelta(minutes=5)
            self.traffic_data = [
                data for data in self.traffic_data
                if data['timestamp'] > cutoff_time
            ]
            
        except Exception as e:
            print(f"Error processing packet: {e}")
    
    def start_monitoring(self):
        """Start network monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        print(f"Starting network monitoring on interface: {self.interface}")
        
        try:
            scapy.sniff(
                iface=self.interface,
                prn=self.packet_handler,
                stop_filter=lambda x: not self.monitoring,
                store=0  # Don't store packets in memory
            )
        except Exception as e:
            print(f"Error starting packet capture: {e}")
            self.monitoring = False
    
    def stop_monitoring(self):
        """Stop network monitoring"""
        self.monitoring = False
        print("Network monitoring stopped")
    
    def get_network_statistics(self):
        """Get current network statistics"""
        if not self.traffic_data:
            return {}
        
        current_time = datetime.now()
        last_minute = current_time - timedelta(minutes=1)
        
        recent_traffic = [
            data for data in self.traffic_data
            if data['timestamp'] > last_minute
        ]
        
        if not recent_traffic:
            return {}
        
        stats = {
            'total_packets': len(recent_traffic),
            'packet_rate': len(recent_traffic) / 60,  # packets per second
            'unique_sources': len(set(data['src_ip'] for data in recent_traffic)),
            'unique_destinations': len(set(data['dst_ip'] for data in recent_traffic)),
            'total_bytes': sum(data['packet_size'] for data in recent_traffic),
            'avg_packet_size': np.mean([data['packet_size'] for data in recent_traffic]),
            'protocol_distribution': dict(Counter(data['protocol'] for data in recent_traffic)),
            'top_talkers': dict(Counter(data['src_ip'] for data in recent_traffic).most_common(5))
        }
        
        return stats

class SystemResourceMonitor:
    def __init__(self):
        self.monitoring = False
        self.resource_data = []
        
    def collect_system_metrics(self):
        """Collect system resource metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            metrics = {
                'timestamp': datetime.now(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available': memory.available,
                'disk_percent': (disk.used / disk.total) * 100,
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv,
                'network_packets_sent': network.packets_sent,
                'network_packets_recv': network.packets_recv,
                'network_errors_in': network.errin,
                'network_errors_out': network.errout,
                'network_drops_in': network.dropin,
                'network_drops_out': network.dropout
            }
            
            return metrics
            
        except Exception as e:
            print(f"Error collecting system metrics: {e}")
            return None
    
    def detect_resource_anomalies(self, window_size=10):
        """Detect system resource anomalies"""
        if len(self.resource_data) < window_size:
            return {'anomaly_detected': False}
        
        recent_data = self.resource_data[-window_size:]
        
        # Calculate statistics
        cpu_values = [d['cpu_percent'] for d in recent_data]
        memory_values = [d['memory_percent'] for d in recent_data]
        
        cpu_mean = np.mean(cpu_values)
        cpu_std = np.std(cpu_values)
        memory_mean = np.mean(memory_values)
        memory_std = np.std(memory_values)
        
        current = recent_data[-1]
        
        # Anomaly detection using z-score
        cpu_zscore = abs((current['cpu_percent'] - cpu_mean) / (cpu_std + 1e-6))
        memory_zscore = abs((current['memory_percent'] - memory_mean) / (memory_std + 1e-6))
        
        anomalies = {
            'high_cpu': current['cpu_percent'] > 90,
            'high_memory': current['memory_percent'] > 90,
            'cpu_spike': cpu_zscore > 2,
            'memory_spike': memory_zscore > 2,
            'network_errors': current['network_errors_in'] > 0 or current['network_errors_out'] > 0
        }
        
        anomaly_detected = any(anomalies.values())
        
        return {
            'anomaly_detected': anomaly_detected,
            'anomalies': anomalies,
            'current_metrics': current,
            'cpu_zscore': cpu_zscore,
            'memory_zscore': memory_zscore
        }
    
    def start_monitoring(self):
        """Start system resource monitoring"""
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                metrics = self.collect_system_metrics()
                if metrics:
                    self.resource_data.append(metrics)
                    
                    # Keep only last hour of data
                    cutoff_time = datetime.now() - timedelta(hours=1)
                    self.resource_data = [
                        data for data in self.resource_data
                        if data['timestamp'] > cutoff_time
                    ]
                
                time.sleep(5)  # Collect every 5 seconds
        
        monitor_thread = threading.Thread(target=monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop system resource monitoring"""
        self.monitoring = False