# backend/modules/network_security/config.py

import os
import json

class NetworkSecurityConfig:
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        config_file = 'config/network_security.json'
        
        default_config = {
            'detection': {
                'confidence_threshold': 0.5,
                'high_severity_threshold': 0.8,
                'enable_anomaly_detection': True,
                'enable_neural_network': True
            },
            'performance': {
                'max_batch_size': 100,
                'prediction_timeout': 5.0,
                'cache_predictions': False
            },
            'alerts': {
                'enable_email_alerts': False,
                'alert_on_critical_only': False,
                'max_alerts_per_minute': 10
            },
            'logging': {
                'log_all_predictions': False,
                'log_errors_only': True,
                'retention_days': 30
            }
        }
        
        if os.path.exists(config_file):
            with open(config_file) as f:
                loaded_config = json.load(f)
                self.config = {**default_config, **loaded_config}
        else:
            self.config = default_config
            # Save default config
            os.makedirs('config', exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
    
    def get(self, key, default=None):
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, default)
            if value is None:
                return default
        return value

# Usage in nsl_detector.py:
from config import NetworkSecurityConfig

class NSLNetworkDetector:
    def __init__(self, model_dir):
        # ... existing code ...
        self.config = NetworkSecurityConfig()
        self.confidence_threshold = self.config.get('detection.confidence_threshold', 0.5)