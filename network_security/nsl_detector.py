# backend/modules/network_security/nsl_detector.py
import numpy as np
import pandas as pd
import joblib
import pickle
import tensorflow as tf
from datetime import datetime
import os

class NSLNetworkDetector:
    def __init__(self, model_dir='backend/models/network_security'):
        self.model_dir = model_dir
        
        # Initialize model placeholders
        self.rf_model = None
        self.lr_model = None
        self.svm_model = None
        self.isolation_forest = None
        self.neural_network = None
        
        # Preprocessing components
        self.label_encoders = {}
        self.scaler = None
        self.columns_info = {}
        
        # Load everything
        self.load_components()
    
    def load_components(self):
        """Load all models and preprocessing components"""
        try:
            print("Loading network intrusion detection system...")
            
            # Load preprocessing components
            with open(f"{self.model_dir}/label_encoders.pkl", 'rb') as f:
                self.label_encoders = pickle.load(f)
            
            with open(f"{self.model_dir}/scaler.pkl", 'rb') as f:
                self.scaler = pickle.load(f)
            
            with open(f"{self.model_dir}/columns_info.pkl", 'rb') as f:
                self.columns_info = pickle.load(f)
            
            print("✓ Preprocessing components loaded")
            
            # Load traditional models
            model_files = {
                'rf_model': 'random_forest_model.pkl',
                'lr_model': 'logistic_regression_model.pkl',
                'svm_model': 'svm_model.pkl',
                'isolation_forest': 'isolation_forest_model.pkl'
            }
            
            loaded_models = []
            for attr_name, filename in model_files.items():
                filepath = f"{self.model_dir}/{filename}"
                if os.path.exists(filepath):
                    setattr(self, attr_name, joblib.load(filepath))
                    loaded_models.append(attr_name)
                    print(f"✓ Loaded {attr_name}")
            
            # Load neural network
            nn_path = f"{self.model_dir}/neural_network_model.keras"
            if os.path.exists(nn_path):
                self.neural_network = tf.keras.models.load_model(nn_path)
                loaded_models.append('neural_network')
                print(f"✓ Loaded neural_network")
            
            print(f"Total models loaded: {len(loaded_models)}")
            
        except Exception as e:
            print(f"Error loading components: {e}")
            import traceback
            traceback.print_exc()
    
    def validate_packet_data(self, packet_data):
        """Validate packet data before processing"""
        if not isinstance(packet_data, dict):
            raise ValueError(f"Packet data must be dict, got {type(packet_data)}")
        
        # Required fields (at minimum)
        required_fields = ['protocol', 'service']
        missing = [f for f in required_fields if f not in packet_data]
        
        if missing:
            print(f"Warning: Missing fields {missing}, using defaults")
        
        # Validate data types and ranges
        if 'src_bytes' in packet_data:
            try:
                packet_data['src_bytes'] = max(0, int(packet_data['src_bytes']))
            except (ValueError, TypeError):
                print(f"Warning: Invalid src_bytes: {packet_data.get('src_bytes')}, using 0")
                packet_data['src_bytes'] = 0
        
        if 'dst_bytes' in packet_data:
            try:
                packet_data['dst_bytes'] = max(0, int(packet_data['dst_bytes']))
            except (ValueError, TypeError):
                print(f"Warning: Invalid dst_bytes: {packet_data.get('dst_bytes')}, using 0")
                packet_data['dst_bytes'] = 0
        
        # Validate protocol
        valid_protocols = ['tcp', 'udp', 'icmp']
        if packet_data.get('protocol', '').lower() not in valid_protocols:
            print(f"Warning: Unknown protocol: {packet_data.get('protocol')}, defaulting to tcp")
            packet_data['protocol'] = 'tcp'
        
        return packet_data
    
    def preprocess_packet(self, packet_data):
        """Preprocess packet data for prediction - must match training exactly"""
        
        # Create ALL 41 features in EXACT training order
        features = {
            'duration': packet_data.get('duration', 0),
            'protocol_type': packet_data.get('protocol', 'tcp'),
            'service': packet_data.get('service', 'http'), 
            'flag': packet_data.get('flag', 'SF'),
            'src_bytes': packet_data.get('src_bytes', 0),
            'dst_bytes': packet_data.get('dst_bytes', 0),
            'land': 1 if packet_data.get('src_ip') == packet_data.get('dst_ip') else 0,
            'wrong_fragment': packet_data.get('wrong_fragment', 0),
            'urgent': packet_data.get('urgent', 0),
            'hot': packet_data.get('hot', 0),
            'num_failed_logins': packet_data.get('num_failed_logins', 0),
            'logged_in': packet_data.get('logged_in', 0),
            'num_compromised': packet_data.get('num_compromised', 0),
            'root_shell': packet_data.get('root_shell', 0),
            'su_attempted': packet_data.get('su_attempted', 0),
            'num_root': packet_data.get('num_root', 0),
            'num_file_creations': packet_data.get('num_file_creations', 0),
            'num_shells': packet_data.get('num_shells', 0),
            'num_access_files': packet_data.get('num_access_files', 0),
            'num_outbound_cmds': packet_data.get('num_outbound_cmds', 0),
            'is_host_login': packet_data.get('is_host_login', 0),
            'is_guest_login': packet_data.get('is_guest_login', 0),
            'count': packet_data.get('count', 1),
            'srv_count': packet_data.get('srv_count', 1),
            'serror_rate': packet_data.get('serror_rate', 0.0),
            'srv_serror_rate': packet_data.get('srv_serror_rate', 0.0),
            'rerror_rate': packet_data.get('rerror_rate', 0.0),
            'srv_rerror_rate': packet_data.get('srv_rerror_rate', 0.0),
            'same_srv_rate': packet_data.get('same_srv_rate', 0.0),
            'diff_srv_rate': packet_data.get('diff_srv_rate', 0.0),
            'srv_diff_host_rate': packet_data.get('srv_diff_host_rate', 0.0),
            'dst_host_count': packet_data.get('dst_host_count', 1),
            'dst_host_srv_count': packet_data.get('dst_host_srv_count', 1),
            'dst_host_same_srv_rate': packet_data.get('dst_host_same_srv_rate', 0.0),
            'dst_host_diff_srv_rate': packet_data.get('dst_host_diff_srv_rate', 0.0),
            'dst_host_same_src_port_rate': packet_data.get('dst_host_same_src_port_rate', 0.0),
            'dst_host_srv_diff_host_rate': packet_data.get('dst_host_srv_diff_host_rate', 0.0),
            'dst_host_serror_rate': packet_data.get('dst_host_serror_rate', 0.0),
            'dst_host_srv_serror_rate': packet_data.get('dst_host_srv_serror_rate', 0.0),
            'dst_host_rerror_rate': packet_data.get('dst_host_rerror_rate', 0.0),
            'dst_host_srv_rerror_rate': packet_data.get('dst_host_srv_rerror_rate', 0.0)
        }
        
        # Create DataFrame
        df = pd.DataFrame([features])
        
        # STEP 1: Encode categorical features FIRST (before scaling)
        categorical_features = ['protocol_type', 'service', 'flag']
        
        for col in categorical_features:
            if col in self.label_encoders:
                le = self.label_encoders[col]
                try:
                    # Handle known categories
                    df[col] = df[col].apply(lambda x: le.transform([str(x)])[0])
                except ValueError:
                    # Handle unknown categories
                    print(f"Warning: Unknown {col} value '{df[col].iloc[0]}', using default")
                    df[col] = 0
            else:
                print(f"Warning: No encoder found for {col}")
                df[col] = 0
        
        # STEP 2: Scale ALL features (now all numerical)
        try:
            df_scaled = pd.DataFrame(
                self.scaler.transform(df),
                columns=df.columns
            )
            return df_scaled
        
        except Exception as e:
            print(f"Scaling error: {e}")
            print(f"DataFrame columns: {df.columns.tolist()}")
            print(f"DataFrame dtypes: {df.dtypes}")
            raise
    
    def detect_intrusion(self, packet_data):
        """Detect network intrusion using ensemble of models"""
        try:
            # Validate packet data first
            packet_data = self.validate_packet_data(packet_data)
            
            # Preprocess packet
            X = self.preprocess_packet(packet_data)
            
            predictions = {}
            
            # Traditional model predictions
            if self.rf_model is not None:
                rf_pred = self.rf_model.predict_proba(X)[0][1]
                predictions['random_forest'] = float(rf_pred)
            
            if self.lr_model is not None:
                lr_pred = self.lr_model.predict_proba(X)[0][1]
                predictions['logistic_regression'] = float(lr_pred)
            
            if self.svm_model is not None:
                svm_pred = self.svm_model.predict_proba(X)[0][1]
                predictions['svm'] = float(svm_pred)
            
            # Anomaly detection
            if self.isolation_forest is not None:
                anomaly_score = self.isolation_forest.decision_function(X)[0]
                is_anomaly = self.isolation_forest.predict(X)[0] == -1
                predictions['isolation_forest'] = float(is_anomaly)
            
            # Neural network
            if self.neural_network is not None:
                nn_pred = self.neural_network.predict(X, verbose=0)[0][0]
                predictions['neural_network'] = float(nn_pred)
            
            # Ensemble prediction
            if predictions:
                confidence = np.mean(list(predictions.values()))
                is_intrusion = confidence > 0.5
                
                # Classify attack type
                attack_type = self._classify_attack_type(packet_data, confidence)
                severity = self._calculate_severity(confidence, packet_data)
                
                return {
                    'is_intrusion': is_intrusion,
                    'confidence': float(confidence),
                    'attack_type': attack_type,
                    'severity': severity,
                    'individual_predictions': predictions,
                    'timestamp': datetime.now().isoformat(),
                    'packet_info': {
                        'src_ip': packet_data.get('src_ip', 'unknown'),
                        'dst_ip': packet_data.get('dst_ip', 'unknown'),
                        'protocol': packet_data.get('protocol', 'unknown'),
                        'service': packet_data.get('service', 'unknown'),
                        'src_bytes': packet_data.get('src_bytes', 0),
                        'dst_bytes': packet_data.get('dst_bytes', 0)
                    }
                }
            else:
                return {
                    'error': 'No models available for prediction',
                    'is_intrusion': False,
                    'confidence': 0.0
                }
        
        except Exception as e:
            print(f"Detection error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'error': str(e),
                'is_intrusion': False,
                'confidence': 0.0
            }
    
    def _classify_attack_type(self, packet_data, confidence):
        """Classify attack type based on packet characteristics"""
        if confidence < 0.5:
            return 'normal'
        
        # Rule-based classification
        src_bytes = packet_data.get('src_bytes', 0)
        dst_bytes = packet_data.get('dst_bytes', 0)
        count = packet_data.get('count', 1)
        serror_rate = packet_data.get('serror_rate', 0)
        
        # DoS patterns
        if src_bytes == 0 and dst_bytes == 0:
            return 'dos'
        
        if count > 100:
            return 'ddos'
        
        # Probe patterns
        if serror_rate > 0.5 and src_bytes < 100:
            return 'probe'
        
        # R2L patterns
        service = packet_data.get('service', '').lower()
        if service in ['ftp', 'telnet', 'ssh'] and packet_data.get('num_failed_logins', 0) > 0:
            return 'r2l'
        
        # U2R patterns
        if packet_data.get('root_shell', 0) > 0 or packet_data.get('su_attempted', 0) > 0:
            return 'u2r'
        
        return 'unknown_attack'
    
    def _calculate_severity(self, confidence, packet_data):
        """Calculate threat severity"""
        base_severity = 'low'
        
        if confidence > 0.8:
            base_severity = 'high'
        elif confidence > 0.6:
            base_severity = 'medium'
        
        # Increase severity for certain conditions
        if packet_data.get('root_shell', 0) > 0:
            return 'critical'
        
        if packet_data.get('dst_bytes', 0) > 1000000:  # Large data transfer
            return 'high'
        
        return base_severity
    
    def analyze_traffic_batch(self, traffic_data):
        """Analyze multiple network packets"""
        results = []
        
        for packet in traffic_data:
            result = self.detect_intrusion(packet)
            results.append(result)
        
        # Generate summary
        total_packets = len(results)
        threats_detected = sum(1 for r in results if r.get('is_intrusion', False))
        
        attack_types = {}
        severities = {}
        
        for result in results:
            if result.get('is_intrusion', False):
                attack_type = result.get('attack_type', 'unknown')
                severity = result.get('severity', 'low')
                
                attack_types[attack_type] = attack_types.get(attack_type, 0) + 1
                severities[severity] = severities.get(severity, 0) + 1
        
        summary = {
            'total_packets': total_packets,
            'threats_detected': threats_detected,
            'threat_rate': threats_detected / total_packets if total_packets > 0 else 0,
            'attack_types': attack_types,
            'severity_distribution': severities,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        return {
            'summary': summary,
            'detailed_results': results
        }