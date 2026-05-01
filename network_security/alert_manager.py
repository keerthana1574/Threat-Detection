# backend/modules/network_security/alert_manager.py

from datetime import datetime
from venv import logger


class AlertManager:
    def __init__(self):
        self.alerts = []
        self.alert_callbacks = []
    
    def register_callback(self, callback):
        """Register alert callback function"""
        self.alert_callbacks.append(callback)
    
    def trigger_alert(self, threat_data):
        """Trigger alert for detected threat"""
        alert = {
            'id': len(self.alerts) + 1,
            'timestamp': datetime.now().isoformat(),
            'threat_type': threat_data.get('attack_type'),
            'severity': threat_data.get('severity'),
            'confidence': threat_data.get('confidence'),
            'source_ip': threat_data.get('packet_info', {}).get('src_ip'),
            'target_ip': threat_data.get('packet_info', {}).get('dst_ip')
        }
        
        self.alerts.append(alert)
        
        # Execute callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
        
        return alert