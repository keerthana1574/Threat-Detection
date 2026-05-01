# import os
# from dotenv import load_dotenv

# load_dotenv()

# class Config:
#     SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
#     DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/cybersecurity_db')
#     REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'cybersecurity-dashboard-secret-key-2024')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///cybersecurity.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis configuration (for caching and session management)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # API Keys
    TWITTER_API_KEY = os.getenv('eVdTmPJpLe2trEcBWnjzMbZBR')
    TWITTER_API_SECRET = os.getenv('zrUSGC5nDIHPIMqwk5zbyao1Ta9iJqaXNQPYgom95jCotlCcDo')
    TWITTER_ACCESS_TOKEN = os.getenv('1759606899732025344-eN5igcpmBCrcBUtjqHi5ZXf73sFSp6')
    TWITTER_ACCESS_SECRET = os.getenv('K6C0dPe87V3ivYS12FXxaRSCJRot1gh0QAijK8qIt5TVc')
    TWITTER_BEARER_TOKEN = os.getenv('AAAAAAAAAAAAAAAAAAAAAL%2BN3gEAAAAAsZFH09MvFghorHlnRBImW2p68mQ%3DAFHw0R1I9qwcq5nzaHLqH8wZfVN7M8kyR8zxkMYMpePEoDBsGD')
    
    # Security settings
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
    
    # Monitoring settings
    MONITORING_INTERVAL = 30  # seconds
    ALERT_RETENTION_DAYS = 30
    LOG_RETENTION_DAYS = 90
    
    # Model paths
    MODEL_BASE_PATH = os.path.join(os.getcwd(), 'backend', 'models')
    CYBERBULLYING_MODEL_PATH = os.path.join(MODEL_BASE_PATH, 'cyberbullying')
    FAKE_NEWS_MODEL_PATH = os.path.join(MODEL_BASE_PATH, 'fake_news')
    NETWORK_SECURITY_MODEL_PATH = os.path.join(MODEL_BASE_PATH, 'network_security')
    WEB_SECURITY_MODEL_PATH = os.path.join(MODEL_BASE_PATH, 'web_security')
    
    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/cybersecurity_dashboard.log'
    
    @staticmethod
    def init_app(app):
        # Ensure required directories exist
        os.makedirs('logs', exist_ok=True)
        os.makedirs('backend/models', exist_ok=True)
        
        # Create model subdirectories
        for model_path in [Config.CYBERBULLYING_MODEL_PATH, Config.FAKE_NEWS_MODEL_PATH,
                          Config.NETWORK_SECURITY_MODEL_PATH, Config.WEB_SECURITY_MODEL_PATH]:
            os.makedirs(model_path, exist_ok=True)

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    DATABASE_URL = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}