# backend/modules/network_security/performance_monitor.py

import time
from collections import deque
from datetime import datetime

class PerformanceMonitor:
    def __init__(self, max_history=1000):
        self.prediction_times = deque(maxlen=max_history)
        self.error_count = 0
        self.total_predictions = 0
        self.start_time = datetime.now()
    
    def record_prediction(self, duration, success=True):
        """Record prediction performance"""
        self.prediction_times.append(duration)
        self.total_predictions += 1
        if not success:
            self.error_count += 1
    
    def get_stats(self):
        """Get performance statistics"""
        if not self.prediction_times:
            return {}
        
        import numpy as np
        times = list(self.prediction_times)
        
        return {
            'avg_response_time': np.mean(times),
            'median_response_time': np.median(times),
            'p95_response_time': np.percentile(times, 95),
            'p99_response_time': np.percentile(times, 99),
            'total_predictions': self.total_predictions,
            'error_rate': self.error_count / self.total_predictions if self.total_predictions > 0 else 0,
            'uptime': (datetime.now() - self.start_time).total_seconds(),
            'predictions_per_second': self.total_predictions / (datetime.now() - self.start_time).total_seconds()
        }

# In nsl_detector.py:
class NSLNetworkDetector:
    def __init__(self, model_dir):
        # ... existing code ...
        self.performance_monitor = PerformanceMonitor()
    
    def detect_intrusion(self, packet_data):
        """Detect with performance tracking"""
        start_time = time.time()
        success = True
        
        try:
            # existing detection code...
            result = { ... }
            
        except Exception as e:
            success = False
            raise
        
        finally:
            duration = time.time() - start_time
            self.performance_monitor.record_prediction(duration, success)
        
        return result