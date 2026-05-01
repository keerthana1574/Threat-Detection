import logging
import traceback
from datetime import datetime
from functools import wraps

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/network_security.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def handle_prediction_errors(func):
    """Decorator to handle prediction errors gracefully"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Prediction error in {func.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Return safe fallback
            return {
                'error': str(e),
                'is_intrusion': False,
                'confidence': 0.0,
                'attack_type': 'error',
                'severity': 'unknown',
                'timestamp': datetime.now().isoformat(),
                'safe_mode': True
            }
    return wrapper