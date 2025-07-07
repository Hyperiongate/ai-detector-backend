import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Flask Core
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///newsverify.db'
    
    # Handle PostgreSQL URL format for SQLAlchemy
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = int(os.environ.get('SQLALCHEMY_POOL_SIZE', 10))
    SQLALCHEMY_MAX_OVERFLOW = int(os.environ.get('SQLALCHEMY_MAX_OVERFLOW', 20))
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = 3600  # 1 hour
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Session Configuration
    SESSION_TYPE = 'redis'
    SESSION_REDIS = None  # Will be set in app initialization
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'newsverify:'
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    
    # API Keys
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
    GOOGLE_FACT_CHECK_API_KEY = os.environ.get('GOOGLE_FACT_CHECK_API_KEY')
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL') or os.environ.get('REDIS_URL')
    RATELIMIT_DEFAULT = "100 per hour"
    
    # File Upload
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 52428800))  # 50MB
    
    # Error Monitoring
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    
    # Payment Processing
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # Security
    BCRYPT_LOG_ROUNDS = int(os.environ.get('BCRYPT_LOG_ROUNDS', 12))
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Feature Flags
    ENABLE_CACHING = os.environ.get('ENABLE_CACHING', 'true').lower() == 'true'
    ENABLE_RATE_LIMITING = os.environ.get('ENABLE_RATE_LIMITING', 'true').lower() == 'true'
    ENABLE_ERROR_TRACKING = os.environ.get('ENABLE_ERROR_TRACKING', 'true').lower() == 'true'
    ENABLE_BACKGROUND_TASKS = os.environ.get('ENABLE_BACKGROUND_TASKS', 'false').lower() == 'true'
    
    # Cache Configuration
    REDIS_CACHE_TIMEOUT = int(os.environ.get('REDIS_CACHE_TIMEOUT', 3600))  # 1 hour
    
    # Subscription Tiers Configuration
    SUBSCRIPTION_LIMITS = {
        'free': {
            'analyses_per_day': 5,
            'analyses_per_month': 50,
            'features': ['basic_analysis', 'source_verification'],
            'cache_duration': 300,  # 5 minutes
        },
        'pro': {
            'analyses_per_day': 100,
            'analyses_per_month': 1000,
            'features': [
                'basic_analysis', 'source_verification', 'bias_analysis',
                'fact_checking', 'authorship_analysis', 'sentiment_analysis',
                'readability_analysis', 'trend_analysis', 'pdf_reports'
            ],
            'cache_duration': 3600,  # 1 hour
        },
        'enterprise': {
            'analyses_per_day': -1,  # Unlimited
            'analyses_per_month': -1,  # Unlimited
            'features': [
                'basic_analysis', 'source_verification', 'bias_analysis',
                'fact_checking', 'authorship_analysis', 'sentiment_analysis',
                'readability_analysis', 'trend_analysis', 'pdf_reports',
                'api_access', 'priority_support', 'custom_integrations'
            ],
            'cache_duration': 7200,  # 2 hours
        }
    }
    
    # Monitoring Configuration
    HEALTH_CHECK_INTERVAL = int(os.environ.get('HEALTH_CHECK_INTERVAL', 300))  # 5 minutes
    CLEANUP_INTERVAL = int(os.environ.get('CLEANUP_INTERVAL', 86400))  # 24 hours

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    
    # Use SQLite for local development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///newsverify_dev.db'
    
    # Disable some features for development
    ENABLE_RATE_LIMITING = False
    ENABLE_ERROR_TRACKING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    
    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable external services for testing
    ENABLE_CACHING = False
    ENABLE_RATE_LIMITING = False
    ENABLE_ERROR_TRACKING = False
    
    # Shorter timeouts for testing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Ensure all security features are enabled
    ENABLE_RATE_LIMITING = True
    ENABLE_ERROR_TRACKING = True
    
    # Production-specific settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
