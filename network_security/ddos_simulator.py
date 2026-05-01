# backend/modules/network_security/ddos_simulator.py

import random
import time
from datetime import datetime, timedelta
from collections import defaultdict
import threading

class DDoSAttackSimulator:
    """Simulates various types of DDoS attacks for demonstration"""
    
    def __init__(self):
        self.attack_active = False
        self.attack_type = None
        self.attack_intensity = "medium"
        self.legitimate_traffic = []
        self.attack_traffic = []
        self.detection_results = []
        
        # Attack patterns
        self.attack_patterns = {
            'syn_flood': self._generate_syn_flood,
            'udp_flood': self._generate_udp_flood,
            'http_flood': self._generate_http_flood,
            'icmp_flood': self._generate_icmp_flood,
            'slowloris': self._generate_slowloris,
            'amplification': self._generate_amplification
        }
        
        # Intensity configurations
        self.intensity_config = {
            'low': {'packets_per_second': 100, 'source_ips': 10},
            'medium': {'packets_per_second': 500, 'source_ips': 50},
            'high': {'packets_per_second': 1000, 'source_ips': 100},
            'critical': {'packets_per_second': 5000, 'source_ips': 500}
        }
    
    def start_attack(self, attack_type, intensity='medium', duration=60):
        """Start a simulated DDoS attack"""
        if attack_type not in self.attack_patterns:
            raise ValueError(f"Unknown attack type: {attack_type}")
        
        self.attack_active = True
        self.attack_type = attack_type
        self.attack_intensity = intensity
        
        # Start attack thread
        attack_thread = threading.Thread(
            target=self._run_attack,
            args=(attack_type, intensity, duration)
        )
        attack_thread.daemon = True
        attack_thread.start()
        
        return {
            'status': 'started',
            'attack_type': attack_type,
            'intensity': intensity,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }
    
    def stop_attack(self):
        """Stop the current attack simulation"""
        self.attack_active = False
        
        return {
            'status': 'stopped',
            'attack_type': self.attack_type,
            'packets_generated': len(self.attack_traffic),
            'timestamp': datetime.now().isoformat()
        }
    
    def _run_attack(self, attack_type, intensity, duration):
        """Run the attack simulation"""
        config = self.intensity_config[intensity]
        start_time = time.time()
        
        # Generate attack pattern
        pattern_generator = self.attack_patterns[attack_type]
        
        while self.attack_active and (time.time() - start_time) < duration:
            # Generate attack packets
            packets = pattern_generator(config)
            self.attack_traffic.extend(packets)
            
            # Also generate some legitimate traffic
            legit_packets = self._generate_legitimate_traffic(
                int(config['packets_per_second'] * 0.1)  # 10% legitimate
            )
            self.legitimate_traffic.extend(legit_packets)
            
            # Sleep for 1 second
            time.sleep(1)
        
        self.attack_active = False
    
    def _generate_syn_flood(self, config):
        """Generate SYN flood attack packets"""
        packets = []
        target_ip = "192.168.1.100"
        target_port = 80
        
        for _ in range(config['packets_per_second']):
            src_ip = self._random_ip()
            src_port = random.randint(1024, 65535)
            
            packet = {
                'timestamp': datetime.now(),
                'attack_type': 'SYN Flood',
                'src_ip': src_ip,
                'dst_ip': target_ip,
                'src_port': src_port,
                'dst_port': target_port,
                'protocol': 'TCP',
                'flags': ['SYN'],
                'packet_size': 60,
                'is_attack': True,
                'severity': 'high'
            }
            packets.append(packet)
        
        return packets
    
    def _generate_udp_flood(self, config):
        """Generate UDP flood attack packets"""
        packets = []
        target_ip = "192.168.1.100"
        
        for _ in range(config['packets_per_second']):
            src_ip = self._random_ip()
            src_port = random.randint(1024, 65535)
            dst_port = random.choice([53, 123, 161, 389])  # Common UDP ports
            
            packet = {
                'timestamp': datetime.now(),
                'attack_type': 'UDP Flood',
                'src_ip': src_ip,
                'dst_ip': target_ip,
                'src_port': src_port,
                'dst_port': dst_port,
                'protocol': 'UDP',
                'flags': [],
                'packet_size': random.randint(100, 1500),
                'is_attack': True,
                'severity': 'high'
            }
            packets.append(packet)
        
        return packets
    
    def _generate_http_flood(self, config):
        """Generate HTTP flood attack packets"""
        packets = []
        target_ip = "192.168.1.100"
        target_port = 80
        
        for _ in range(config['packets_per_second']):
            src_ip = self._random_ip()
            src_port = random.randint(1024, 65535)
            
            packet = {
                'timestamp': datetime.now(),
                'attack_type': 'HTTP Flood',
                'src_ip': src_ip,
                'dst_ip': target_ip,
                'src_port': src_port,
                'dst_port': target_port,
                'protocol': 'TCP',
                'flags': ['PSH', 'ACK'],
                'packet_size': random.randint(200, 800),
                'http_method': random.choice(['GET', 'POST']),
                'http_path': random.choice(['/', '/index.html', '/api/data', '/search']),
                'is_attack': True,
                'severity': 'medium'
            }
            packets.append(packet)
        
        return packets
    
    def _generate_icmp_flood(self, config):
        """Generate ICMP flood (Ping flood) attack packets"""
        packets = []
        target_ip = "192.168.1.100"
        
        for _ in range(config['packets_per_second']):
            src_ip = self._random_ip()
            
            packet = {
                'timestamp': datetime.now(),
                'attack_type': 'ICMP Flood',
                'src_ip': src_ip,
                'dst_ip': target_ip,
                'src_port': 0,
                'dst_port': 0,
                'protocol': 'ICMP',
                'flags': [],
                'packet_size': 64,
                'icmp_type': 8,  # Echo request
                'is_attack': True,
                'severity': 'medium'
            }
            packets.append(packet)
        
        return packets
    
    def _generate_slowloris(self, config):
        """Generate Slowloris attack packets"""
        packets = []
        target_ip = "192.168.1.100"
        target_port = 80
        
        # Slowloris uses fewer connections but keeps them open
        num_connections = min(config['packets_per_second'] // 10, 100)
        
        for _ in range(num_connections):
            src_ip = self._random_ip()
            src_port = random.randint(1024, 65535)
            
            packet = {
                'timestamp': datetime.now(),
                'attack_type': 'Slowloris',
                'src_ip': src_ip,
                'dst_ip': target_ip,
                'src_port': src_port,
                'dst_port': target_port,
                'protocol': 'TCP',
                'flags': ['PSH', 'ACK'],
                'packet_size': random.randint(10, 50),  # Very small packets
                'is_attack': True,
                'severity': 'critical'
            }
            packets.append(packet)
        
        return packets
    
    def _generate_amplification(self, config):
        """Generate DNS/NTP amplification attack packets"""
        packets = []
        target_ip = "192.168.1.100"
        
        # Amplification attacks use spoofed source IPs
        for _ in range(config['packets_per_second']):
            # Response packets from DNS/NTP servers
            server_ip = self._random_ip()
            
            packet = {
                'timestamp': datetime.now(),
                'attack_type': 'Amplification',
                'src_ip': server_ip,
                'dst_ip': target_ip,
                'src_port': random.choice([53, 123]),  # DNS or NTP
                'dst_port': random.randint(1024, 65535),
                'protocol': 'UDP',
                'flags': [],
                'packet_size': random.randint(500, 4000),  # Large response packets
                'is_attack': True,
                'severity': 'critical'
            }
            packets.append(packet)
        
        return packets
    
    def _generate_legitimate_traffic(self, num_packets):
        """Generate legitimate network traffic"""
        packets = []
        
        for _ in range(num_packets):
            src_ip = f"192.168.1.{random.randint(10, 50)}"
            dst_ip = f"192.168.1.{random.randint(100, 200)}"
            
            packet = {
                'timestamp': datetime.now(),
                'attack_type': None,
                'src_ip': src_ip,
                'dst_ip': dst_ip,
                'src_port': random.randint(1024, 65535),
                'dst_port': random.choice([80, 443, 22, 3306]),
                'protocol': random.choice(['TCP', 'UDP']),
                'flags': ['ACK'],
                'packet_size': random.randint(60, 1500),
                'is_attack': False,
                'severity': None
            }
            packets.append(packet)
        
        return packets
    
    def _random_ip(self):
        """Generate random IP address for attack source"""
        # Generate IPs from various ranges to simulate botnet
        ranges = [
            (10, 0, 0, 0),
            (172, 16, 0, 0),
            (192, 168, 0, 0),
            (203, 0, 113, 0)  # TEST-NET-3
        ]
        
        base = random.choice(ranges)
        return f"{base[0]}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
    
    def get_attack_statistics(self):
        """Get current attack statistics"""
        if not self.attack_traffic:
            return {
                'status': 'no_attack',
                'total_packets': 0
            }
        
        # Analyze last minute of traffic
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        recent_attack = [p for p in self.attack_traffic if p['timestamp'] > one_minute_ago]
        recent_legit = [p for p in self.legitimate_traffic if p['timestamp'] > one_minute_ago]
        
        # Calculate metrics
        total_packets = len(recent_attack) + len(recent_legit)
        attack_percentage = (len(recent_attack) / total_packets * 100) if total_packets > 0 else 0
        
        # Source IP distribution
        source_ips = defaultdict(int)
        for packet in recent_attack:
            source_ips[packet['src_ip']] += 1
        
        # Protocol distribution
        protocols = defaultdict(int)
        for packet in recent_attack:
            protocols[packet['protocol']] += 1
        
        # Target analysis
        target_ips = defaultdict(int)
        for packet in recent_attack:
            target_ips[packet['dst_ip']] += 1
        
        return {
            'status': 'active' if self.attack_active else 'completed',
            'attack_type': self.attack_type,
            'intensity': self.attack_intensity,
            'total_packets': total_packets,
            'attack_packets': len(recent_attack),
            'legitimate_packets': len(recent_legit),
            'attack_percentage': round(attack_percentage, 2),
            'packets_per_second': len(recent_attack) // 60,
            'unique_source_ips': len(source_ips),
            'top_source_ips': dict(sorted(source_ips.items(), key=lambda x: x[1], reverse=True)[:10]),
            'protocol_distribution': dict(protocols),
            'target_ips': dict(target_ips),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_live_visualization_data(self, last_n_seconds=10):
        """Get data formatted for real-time visualization"""
        cutoff_time = datetime.now() - timedelta(seconds=last_n_seconds)
        
        recent_attack = [p for p in self.attack_traffic if p['timestamp'] > cutoff_time]
        recent_legit = [p for p in self.legitimate_traffic if p['timestamp'] > cutoff_time]
        
        # Time series data
        time_series = defaultdict(lambda: {'attack': 0, 'legitimate': 0})
        
        for packet in recent_attack:
            second = packet['timestamp'].strftime('%H:%M:%S')
            time_series[second]['attack'] += 1
        
        for packet in recent_legit:
            second = packet['timestamp'].strftime('%H:%M:%S')
            time_series[second]['legitimate'] += 1
        
        # Sort by time
        sorted_times = sorted(time_series.keys())
        
        timeline_data = [
            {
                'time': t,
                'attack_packets': time_series[t]['attack'],
                'legitimate_packets': time_series[t]['legitimate']
            }
            for t in sorted_times
        ]
        
        # Geographic distribution (simulated)
        geo_distribution = [
            {'country': 'USA', 'attacks': random.randint(100, 500)},
            {'country': 'China', 'attacks': random.randint(50, 300)},
            {'country': 'Russia', 'attacks': random.randint(80, 400)},
            {'country': 'Brazil', 'attacks': random.randint(30, 200)},
            {'country': 'Germany', 'attacks': random.randint(20, 150)}
        ]
        
        return {
            'timeline': timeline_data,
            'geo_distribution': geo_distribution,
            'recent_packets': {
                'attack': recent_attack[-20:],  # Last 20 attack packets
                'legitimate': recent_legit[-20:]  # Last 20 legitimate packets
            }
        }
    
    def analyze_with_ml_model(self, detector):
        """Analyze recent traffic with ML model"""
        if not self.attack_traffic:
            return {'error': 'No traffic to analyze'}
        
        # Get recent packets
        recent_packets = self.attack_traffic[-100:] + self.legitimate_traffic[-100:]
        
        # Analyze each packet
        results = []
        for packet in recent_packets:
            # Convert to format expected by detector
            packet_data = {
                'protocol': packet['protocol'].lower(),
                'service': 'http',
                'src_ip': packet['src_ip'],
                'dst_ip': packet['dst_ip'],
                'src_bytes': packet['packet_size'],
                'dst_bytes': 0,
                'count': 1
            }
            
            detection_result = detector.detect_intrusion(packet_data)
            detection_result['actual_attack'] = packet['is_attack']
            results.append(detection_result)
        
        # Calculate accuracy metrics
        true_positives = sum(1 for r in results if r['is_intrusion'] and r['actual_attack'])
        true_negatives = sum(1 for r in results if not r['is_intrusion'] and not r['actual_attack'])
        false_positives = sum(1 for r in results if r['is_intrusion'] and not r['actual_attack'])
        false_negatives = sum(1 for r in results if not r['is_intrusion'] and r['actual_attack'])
        
        total = len(results)
        accuracy = (true_positives + true_negatives) / total if total > 0 else 0
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        
        return {
            'total_analyzed': total,
            'true_positives': true_positives,
            'true_negatives': true_negatives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'accuracy': round(accuracy * 100, 2),
            'precision': round(precision * 100, 2),
            'recall': round(recall * 100, 2),
            'f1_score': round(2 * (precision * recall) / (precision + recall) * 100, 2) if (precision + recall) > 0 else 0
        }