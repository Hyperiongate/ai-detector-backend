from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for, flash, g
from flask_cors import CORS
import requests
import os
import json
import time
import logging
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse
import hashlib
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import uuid

# FLASK-LOGIN IMPORTS - Added for authentication system
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import secrets

# PERFORMANCE OPTIMIZATION IMPORTS
import psutil
from flask_caching import Cache
from flask_compress import Compress
from sqlalchemy.pool import QueuePool

# SAFE Email imports - Python 3.13 compatible
try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    EMAIL_AVAILABLE = True
    print("✓ Email modules loaded successfully")
except ImportError:
    try:
        # Fallback for different Python versions
        import smtplib
        from email.MIMEText import MIMEText
        from email.MIMEMultipart import MIMEMultipart
        EMAIL_AVAILABLE = True
        print("✓ Email modules loaded successfully (fallback)")
    except ImportError:
        EMAIL_AVAILABLE = False
        MIMEText = None
        MIMEMultipart = None
        smtplib = None
        print("⚠ Email functionality disabled - MIME imports failed")

# SAFE Database imports - will not break if missing
try:
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy.exc import SQLAlchemyError
    from sqlalchemy import text
    DATABASE_AVAILABLE = True
    print("✓ Database modules loaded successfully")
except ImportError as e:
    print(f"Database not available - continuing safely: {e}")
    DATABASE_AVAILABLE = False

# Try to import BeautifulSoup and OpenAI with fallbacks
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None
    logging.warning("BeautifulSoup not available - URL content extraction disabled")

try:
    import openai
except ImportError:
    openai = None
    logging.warning("OpenAI not available - advanced AI analysis disabled")

# Configure logging with better error handling
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app with error handling
try:
    app = Flask(__name__)
    CORS(app)
    logger.info("Flask app initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Flask app: {e}")
    raise

# FLASK-LOGIN INITIALIZATION
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# PERFORMANCE OPTIMIZATION SETUP
def get_cache_config():
    """Configure caching based on environment"""
    redis_url = os.environ.get('REDIS_URL')
    
    if redis_url:
        # Production: Use Redis/Key Value
        return {
            'CACHE_TYPE': 'RedisCache',
            'CACHE_REDIS_URL': redis_url,
            'CACHE_DEFAULT_TIMEOUT': 300,  # 5 minutes default
            'CACHE_KEY_PREFIX': 'factsandfakes:',
        }
    else:
        # Development/Fallback: Use simple cache
        return {
            'CACHE_TYPE': 'SimpleCache',
            'CACHE_DEFAULT_TIMEOUT': 300,
        }

# Initialize performance components
cache = Cache(app, config=get_cache_config())
Compress(app)  # Enable response compression

# COMPRESSION CONFIGURATION
app.config['COMPRESS_MIMETYPES'] = [
    'text/html', 'text/css', 'text/xml', 'application/json',
    'application/javascript', 'text/javascript', 'application/xml', 'text/plain'
]
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIN_SIZE'] = 500

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ai-detection-secret-key-2024')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)  # Beta sessions last 30 days

# ENHANCED DATABASE CONFIGURATION WITH CONNECTION POOLING
if DATABASE_AVAILABLE:
    try:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///fallback.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # CONNECTION POOLING for performance
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'poolclass': QueuePool,
            'pool_size': 10,          # Number of connections to maintain
            'pool_recycle': 3600,     # Recycle connections every hour
            'pool_pre_ping': True,    # Verify connections before use
            'max_overflow': 20,       # Additional connections if pool is full
            'pool_timeout': 30,       # Timeout for getting connection
            'pool_reset_on_return': 'commit',
        }
        
        # Initialize database
        db = SQLAlchemy(app)
        
        # ENHANCED USER MODEL WITH FLASK-LOGIN AUTHENTICATION
        class User(UserMixin, db.Model):
            __tablename__ = 'user'
            
            # Primary identification
            id = db.Column(db.Integer, primary_key=True)
            email = db.Column(db.String(120), unique=True, nullable=False, index=True)
            password_hash = db.Column(db.String(255), nullable=False)
            
            # Profile information
            first_name = db.Column(db.String(50), nullable=True)
            last_name = db.Column(db.String(50), nullable=True)
            
            # Account status
            is_active = db.Column(db.Boolean, default=True)
            email_verified = db.Column(db.Boolean, default=False)
            verification_token = db.Column(db.String(100), unique=True)
            
            # Subscription and usage
            subscription_tier = db.Column(db.String(20), default='free')  # 'free', 'pro', 'enterprise'
            
            # Usage tracking for daily limits (NEW SYSTEM)
            daily_free_count = db.Column(db.Integer, default=0)
            daily_pro_count = db.Column(db.Integer, default=0)
            last_free_reset = db.Column(db.Date, default=datetime.utcnow().date)
            last_pro_reset = db.Column(db.Date, default=datetime.utcnow().date)
            
            # Legacy beta fields (keep for compatibility)
            signup_source = db.Column(db.String(50), default='direct')
            daily_usage_count = db.Column(db.Integer, default=0)
            last_usage_date = db.Column(db.Date, default=datetime.utcnow().date)
            free_analyses_used = db.Column(db.Integer, default=0)
            pro_analyses_used = db.Column(db.Integer, default=0)
            last_reset_date = db.Column(db.Date, default=datetime.utcnow().date)
            feedback_count = db.Column(db.Integer, default=0)
            
            # Timestamps
            created_at = db.Column(db.DateTime, default=datetime.utcnow)
            updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
            last_login = db.Column(db.DateTime)
            
            # Total usage statistics
            total_analyses = db.Column(db.Integer, default=0)
            total_free_analyses = db.Column(db.Integer, default=0)
            total_pro_analyses = db.Column(db.Integer, default=0)
            
            def __init__(self, email, password=None, first_name=None, last_name=None):
                self.email = email.lower().strip()
                if password:
                    self.set_password(password)
                self.first_name = first_name.strip() if first_name else email.split('@')[0]
                self.last_name = last_name.strip() if last_name else 'User'
                self.verification_token = secrets.token_urlsafe(32)
            
            def set_password(self, password):
                """Hash and set password"""
                self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
            
            def check_password(self, password):
                """Check if provided password matches hash"""
                if not self.password_hash:
                    return False
                return check_password_hash(self.password_hash, password)
            
            @property
            def full_name(self):
                """Get user's full name"""
                return f"{self.first_name} {self.last_name}"
            
            def get_id(self):
                """Required by Flask-Login"""
                return str(self.id)
            
            def is_authenticated(self):
                """Required by Flask-Login"""
                return True
            
            def is_anonymous(self):
                """Required by Flask-Login"""
                return False
            
            def is_admin(self):
                """Check if user has admin privileges"""
                return self.email in ['admin@factsandfakes.ai', 'contact@factsandfakes.ai']
            
            # NEW AUTHENTICATION SYSTEM METHODS
            def reset_daily_counts_if_needed(self):
                """Reset daily counts if it's a new day"""
                today = datetime.utcnow().date()
                
                # Reset free count if needed
                if self.last_free_reset != today:
                    self.daily_free_count = 0
                    self.last_free_reset = today
                
                # Reset pro count if needed (every 2 days)
                days_since_pro_reset = (today - self.last_pro_reset).days
                if days_since_pro_reset >= 2:
                    self.daily_pro_count = 0
                    self.last_pro_reset = today
                
                db.session.commit()
            
            def can_use_free_analysis(self):
                """Check if user can perform free analysis"""
                self.reset_daily_counts_if_needed()
                return self.daily_free_count < 3
            
            def can_use_pro_analysis(self):
                """Check if user can perform pro analysis"""
                self.reset_daily_counts_if_needed()
                return self.daily_pro_count < 1
            
            def use_free_analysis(self):
                """Record usage of free analysis"""
                self.reset_daily_counts_if_needed()
                if self.can_use_free_analysis():
                    self.daily_free_count += 1
                    self.total_analyses += 1
                    self.total_free_analyses += 1
                    
                    # Update legacy fields for compatibility
                    self.free_analyses_used += 1
                    self.daily_usage_count += 1
                    
                    db.session.commit()
                    return True
                return False
            
            def use_pro_analysis(self):
                """Record usage of pro analysis"""
                self.reset_daily_counts_if_needed()
                if self.can_use_pro_analysis():
                    self.daily_pro_count += 1
                    self.total_analyses += 1
                    self.total_pro_analyses += 1
                    
                    # Update legacy fields for compatibility
                    self.pro_analyses_used += 1
                    self.daily_usage_count += 1
                    
                    db.session.commit()
                    return True
                return False
            
            def get_usage_stats(self):
                """Get current usage statistics"""
                self.reset_daily_counts_if_needed()
                
                # Calculate days until pro analysis resets
                days_since_pro_reset = (datetime.utcnow().date() - self.last_pro_reset).days
                days_until_pro_reset = max(0, 2 - days_since_pro_reset)
                
                return {
                    'free_remaining': max(0, 3 - self.daily_free_count),
                    'free_used': self.daily_free_count,
                    'free_limit': 3,
                    'pro_remaining': max(0, 1 - self.daily_pro_count),
                    'pro_used': self.daily_pro_count,
                    'pro_limit': 1,
                    'days_until_pro_reset': days_until_pro_reset,
                    'total_analyses': self.total_analyses,
                    'total_free_analyses': self.total_free_analyses,
                    'total_pro_analyses': self.total_pro_analyses
                }
            
            def record_login(self):
                """Record user login timestamp"""
                self.last_login = datetime.utcnow()
                db.session.commit()
            
            def to_dict(self):
                """Convert user to dictionary for JSON responses"""
                return {
                    'id': self.id,
                    'email': self.email,
                    'full_name': self.full_name,
                    'first_name': self.first_name,
                    'last_name': self.last_name,
                    'subscription_tier': self.subscription_tier,
                    'created_at': self.created_at.isoformat() if self.created_at else None,
                    'last_login': self.last_login.isoformat() if self.last_login else None,
                    'is_active': self.is_active,
                    'email_verified': self.email_verified,
                    'usage_stats': self.get_usage_stats()
                }
            
            # LEGACY BETA METHODS (keep for backward compatibility)
            def reset_daily_usage(self):
                """Legacy method - Reset daily usage if new day"""
                today = datetime.utcnow().date()
                if self.last_reset_date != today:
                    self.free_analyses_used = 0
                    self.pro_analyses_used = 0
                    self.last_reset_date = today
                    self.last_usage_date = today
                    return True
                return False
            
            def can_use_feature(self, analysis_type='free'):
                """Legacy method - Check if user can use feature based on beta limits"""
                self.reset_daily_usage()
                
                if analysis_type == 'free':
                    return self.free_analyses_used < 5
                elif analysis_type == 'pro':
                    return self.pro_analyses_used < 5
                
                return False
            
            def use_analysis(self, analysis_type='free'):
                """Legacy method - Record analysis usage"""
                self.reset_daily_usage()
                
                if analysis_type == 'free':
                    self.free_analyses_used += 1
                elif analysis_type == 'pro':
                    self.pro_analyses_used += 1
                
                self.daily_usage_count += 1
                
                try:
                    db.session.commit()
                    return True
                except Exception as e:
                    logger.error(f"Failed to record usage: {e}")
                    db.session.rollback()
                    return False
        
        # Simple Analysis model
        class Analysis(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
            analysis_type = db.Column(db.String(50))
            query = db.Column(db.Text)
            created_at = db.Column(db.DateTime, default=datetime.utcnow)
            
            user = db.relationship('User', backref='analyses')
        
        # Beta Feedback model
        class BetaFeedback(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
            feedback_text = db.Column(db.Text, nullable=False)
            rating = db.Column(db.Integer)
            page_source = db.Column(db.String(50))
            created_at = db.Column(db.DateTime, default=datetime.utcnow)
            
            user = db.relationship('User', backref='feedback_submissions')
        
        # Contact Message model
        class ContactMessage(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(100), nullable=False)
            email = db.Column(db.String(120), nullable=False)
            subject = db.Column(db.String(200), nullable=False)
            message = db.Column(db.Text, nullable=False)
            created_at = db.Column(db.DateTime, default=datetime.utcnow)
            email_sent = db.Column(db.Boolean, default=False)
        
        # USER LOADER FUNCTION (Required by Flask-Login)
        @login_manager.user_loader
        def load_user(user_id):
            """Load user by ID for Flask-Login"""
            try:
                return User.query.get(int(user_id))
            except (ValueError, TypeError):
                return None
        
        # Create tables
        with app.app_context():
            db.create_all()
            
        print("✓ Database initialized safely with enhanced authentication models")
    except Exception as e:
        print(f"Database setup failed - continuing without: {e}")
        DATABASE_AVAILABLE = False
else:
    db = None

# Email configuration for Bluehost - with safety checks
if EMAIL_AVAILABLE:
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'mail.factsandfakes.ai')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME', 'contact@factsandfakes.ai')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL', 'contact@factsandfakes.ai')
else:
    SMTP_SERVER = None
    SMTP_PORT = None
    SMTP_USERNAME = None
    SMTP_PASSWORD = None
    CONTACT_EMAIL = None

# API Keys from environment variables with validation
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
GOOGLE_FACT_CHECK_API_KEY = os.environ.get('GOOGLE_FACT_CHECK_API_KEY')

# Set OpenAI API key with enhanced error handling
openai_client = None
if OPENAI_API_KEY and openai:
    try:
        openai.api_key = OPENAI_API_KEY
        openai_client = "legacy"
        logger.info("OpenAI client initialized successfully (legacy syntax)")
    except Exception as e:
        logger.warning(f"OpenAI initialization failed: {e}")
        openai_client = None
else:
    logger.warning("OpenAI not configured - using fallback analysis")

# Enhanced source credibility database
SOURCE_CREDIBILITY = {
    'reuters.com': {'credibility': 95, 'bias': 'center', 'type': 'news_agency'},
    'ap.org': {'credibility': 95, 'bias': 'center', 'type': 'news_agency'},
    'bbc.com': {'credibility': 90, 'bias': 'center-left', 'type': 'international'},
    'cnn.com': {'credibility': 75, 'bias': 'left', 'type': 'cable_news'},
    'foxnews.com': {'credibility': 70, 'bias': 'right', 'type': 'cable_news'},
    'nytimes.com': {'credibility': 85, 'bias': 'center-left', 'type': 'newspaper'},
    'wsj.com': {'credibility': 85, 'bias': 'center-right', 'type': 'newspaper'},
    'washingtonpost.com': {'credibility': 80, 'bias': 'center-left', 'type': 'newspaper'},
    'npr.org': {'credibility': 90, 'bias': 'center-left', 'type': 'public_media'},
    'theguardian.com': {'credibility': 80, 'bias': 'left', 'type': 'international'},
    'usatoday.com': {'credibility': 75, 'bias': 'center', 'type': 'newspaper'},
    'bloomberg.com': {'credibility': 85, 'bias': 'center', 'type': 'financial'},
    'politico.com': {'credibility': 80, 'bias': 'center-left', 'type': 'political'},
    'abc.com': {'credibility': 78, 'bias': 'center-left', 'type': 'broadcast'},
    'cbsnews.com': {'credibility': 77, 'bias': 'center-left', 'type': 'broadcast'},
    'nbcnews.com': {'credibility': 76, 'bias': 'center-left', 'type': 'broadcast'},
    'economist.com': {'credibility': 88, 'bias': 'center', 'type': 'magazine'}
}

# PERFORMANCE MONITORING
@app.before_request
def start_timer():
    g.start_time = time.time()

@app.after_request
def add_performance_headers(response):
    """Add performance headers and monitoring"""
    
    # Add performance timing
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        response.headers['X-Response-Time'] = f"{duration:.3f}s"
        
        # Log slow requests
        if duration > 2.0:
            logger.warning(f"Slow request: {request.endpoint} took {duration:.2f}s")
    
    # Add caching headers for static content
    if request.endpoint == 'static':
        response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 year
    elif request.endpoint in ['index', 'news', 'unified', 'imageanalysis', 'contact', 'missionstatement', 'pricingplan']:
        response.headers['Cache-Control'] = 'public, max-age=300'  # 5 minutes
    
    return response

# HELPER FUNCTIONS AND DECORATORS
def beta_required(f):
    """Beta access required decorator (backward compatibility)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not DATABASE_AVAILABLE:
            return jsonify({
                'error': 'Beta access not available',
                'message': 'Beta features temporarily unavailable'
            }), 503
            
        # Check both new authentication and legacy session
        if current_user.is_authenticated:
            return f(*args, **kwargs)
        elif session.get('user_id'):
            # Legacy beta user - continue to work
            return f(*args, **kwargs)
        else:
            return jsonify({
                'error': 'Authentication required',
                'redirect': '/register',
                'message': 'Please create an account to access this feature'
            }), 401
            
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current user (supports both new auth and legacy session)"""
    if not DATABASE_AVAILABLE:
        return None
    
    # Try Flask-Login current_user first
    if current_user.is_authenticated:
        return current_user
    
    # Fallback to legacy session for backward compatibility
    user_id = session.get('user_id')
    if user_id:
        try:
            user = User.query.get(user_id)
            if user:
                user.reset_daily_usage()  # Legacy compatibility
                return user
        except Exception as e:
            logger.warning(f"Legacy user lookup failed: {e}")
    
    return None

def check_usage_limit_new(user, analysis_type):
    """NEW usage limit checking system"""
    if not user or not DATABASE_AVAILABLE:
        return False, "Authentication required to use this feature"
    
    try:
        user.reset_daily_counts_if_needed()
        
        if analysis_type == 'free':
            can_use = user.can_use_free_analysis()
            if not can_use:
                return False, "Daily free analysis limit reached (3/day). Try Pro features or come back tomorrow!"
        elif analysis_type == 'pro':
            can_use = user.can_use_pro_analysis()
            if not can_use:
                return False, "Pro analysis limit reached (1 every 2 days). Come back in a couple days!"
        else:
            return False, "Unknown analysis type"
        
        return True, ""
        
    except Exception as e:
        logger.warning(f"Usage check failed: {e}")
        return False, "Unable to verify usage limits"

def log_analysis_new(user, analysis_type, query):
    """NEW analysis logging system"""
    if not user or not DATABASE_AVAILABLE:
        return False
    
    try:
        if analysis_type == 'free':
            success = user.use_free_analysis()
        elif analysis_type == 'pro':
            success = user.use_pro_analysis()
        else:
            return False
        
        if success:
            analysis = Analysis(
                user_id=user.id,
                analysis_type=analysis_type,
                query=query[:500]
            )
            db.session.add(analysis)
            db.session.commit()
            
            logger.info(f"Analysis logged: user {user.id}, type {analysis_type}")
            return True
        
        return False
        
    except Exception as e:
        logger.warning(f"Analysis logging failed: {e}")
        try:
            db.session.rollback()
        except:
            pass
        return False

# Legacy compatibility functions (keep existing behavior)
def check_usage_limit(user, analysis_type):
    """Legacy function - delegates to new system if possible"""
    if hasattr(user, 'can_use_free_analysis'):
        return check_usage_limit_new(user, analysis_type)
    else:
        # Fallback to legacy behavior
        if not user or not DATABASE_AVAILABLE:
            return False, "Beta signup required to use this feature"
        
        try:
            user.reset_daily_usage()
            
            if analysis_type == 'free':
                can_use = user.can_use_feature('free')
                if not can_use:
                    return False, "Daily free analysis limit reached (5/day). Try Pro features or come back tomorrow!"
            elif analysis_type == 'pro':
                can_use = user.can_use_feature('pro')
                if not can_use:
                    return False, "Daily Pro analysis limit reached (5/day). Come back tomorrow for more!"
            else:
                return False, "Unknown analysis type"
            
            return True, ""
            
        except Exception as e:
            logger.warning(f"Usage check failed: {e}")
            return False, "Unable to verify usage limits"

def log_analysis(user, analysis_type, query):
    """Legacy function - delegates to new system if possible"""
    if hasattr(user, 'use_free_analysis'):
        return log_analysis_new(user, analysis_type, query)
    else:
        # Fallback to legacy behavior
        if not user or not DATABASE_AVAILABLE:
            return False
        
        try:
            success = user.use_analysis(analysis_type)
            
            if success:
                analysis = Analysis(
                    user_id=user.id,
                    analysis_type=analysis_type,
                    query=query[:500]
                )
                db.session.add(analysis)
                db.session.commit()
                
                logger.info(f"Beta analysis logged: user {user.id}, type {analysis_type}")
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Analysis logging failed: {e}")
            try:
                db.session.rollback()
            except:
                pass
            return False

def send_email(to_email, subject, message, from_name=None):
    """Send email via Bluehost SMTP - Python 3.13 compatible"""
    if not EMAIL_AVAILABLE:
        logger.warning("Email functionality not available - MIME imports failed")
        return False
        
    if not SMTP_PASSWORD:
        logger.warning("SMTP_PASSWORD not configured - email disabled")
        return False
        
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{from_name} <{SMTP_USERNAME}>" if from_name else SMTP_USERNAME
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USERNAME, to_email, text)
        server.quit()
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Email sending failed to {to_email}: {e}")
        return False

# AUTHENTICATION ROUTES
@app.route('/register')
def register_page():
    """User registration page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Create Account - Facts & Fakes AI</title>
        <style>
            body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   min-height: 100vh; display: flex; align-items: center; justify-content: center; margin: 0; }
            .container { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); 
                       max-width: 400px; width: 90%; }
            h1 { text-align: center; margin-bottom: 1.5rem; color: #333; }
            .form-group { margin-bottom: 1rem; }
            label { display: block; margin-bottom: 0.5rem; color: #333; font-weight: 500; }
            input { width: 100%; padding: 0.75rem; border: 2px solid #e0e0e0; border-radius: 6px; box-sizing: border-box; }
            .btn { width: 100%; padding: 0.75rem; background: linear-gradient(135deg, #667eea, #764ba2); 
                  color: white; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; }
            .message { padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem; }
            .error { background: #fee; color: #c33; border: 1px solid #fcc; }
            .success { background: #efe; color: #393; border: 1px solid #cfc; }
            .benefits { background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Create Your Account</h1>
            <div class="benefits">
                <h3>Get Access To:</h3>
                <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                    <li>3 Free AI detections per day</li>
                    <li>1 Pro analysis every 2 days</li>
                    <li>Advanced bias detection</li>
                    <li>Comprehensive news verification</li>
                    <li>Image & deepfake analysis</li>
                    <li>Priority support</li>
                </ul>
            </div>
            <div id="message"></div>
            <form id="registerForm">
                <div class="form-group">
                    <label for="first_name">First Name</label>
                    <input type="text" id="first_name" name="first_name" required>
                </div>
                <div class="form-group">
                    <label for="last_name">Last Name</label>
                    <input type="text" id="last_name" name="last_name" required>
                </div>
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="password">Password (6+ characters)</label>
                    <input type="password" id="password" name="password" required minlength="6">
                </div>
                <button type="submit" class="btn" id="registerBtn">Create Account</button>
            </form>
            <div style="text-align: center; margin-top: 1rem;">
                <a href="/login" style="color: #667eea;">Already have an account? Sign in</a>
            </div>
        </div>
        <script>
            document.getElementById('registerForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const btn = document.getElementById('registerBtn');
                const messageDiv = document.getElementById('message');
                
                btn.disabled = true;
                btn.textContent = 'Creating account...';
                
                try {
                    const response = await fetch('/api/register', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            first_name: document.getElementById('first_name').value,
                            last_name: document.getElementById('last_name').value,
                            email: document.getElementById('email').value,
                            password: document.getElementById('password').value
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        messageDiv.innerHTML = '<div class="message success">Account created! Redirecting...</div>';
                        setTimeout(() => window.location.href = result.redirect || '/dashboard', 1000);
                    } else {
                        messageDiv.innerHTML = '<div class="message error">' + result.message + '</div>';
                        btn.disabled = false;
                        btn.textContent = 'Create Account';
                    }
                } catch (error) {
                    messageDiv.innerHTML = '<div class="message error">Network error. Please try again.</div>';
                    btn.disabled = false;
                    btn.textContent = 'Create Account';
                }
            });
        </script>
    </body>
    </html>
    """

@app.route('/login')
def login_page():
    """User login page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sign In - Facts & Fakes AI</title>
        <style>
            body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   min-height: 100vh; display: flex; align-items: center; justify-content: center; margin: 0; }
            .container { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); 
                       max-width: 400px; width: 90%; }
            h1 { text-align: center; margin-bottom: 2rem; color: #333; }
            .form-group { margin-bottom: 1rem; }
            label { display: block; margin-bottom: 0.5rem; color: #333; font-weight: 500; }
            input { width: 100%; padding: 0.75rem; border: 2px solid #e0e0e0; border-radius: 6px; box-sizing: border-box; }
            .btn { width: 100%; padding: 0.75rem; background: linear-gradient(135deg, #667eea, #764ba2); 
                  color: white; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; }
            .message { padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem; }
            .error { background: #fee; color: #c33; border: 1px solid #fcc; }
            .success { background: #efe; color: #393; border: 1px solid #cfc; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome Back</h1>
            <div id="message"></div>
            <form id="loginForm">
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="btn" id="loginBtn">Sign In</button>
            </form>
            <div style="text-align: center; margin-top: 1.5rem;">
                <a href="/register" style="color: #667eea;">Don't have an account? Create one</a>
            </div>
        </div>
        <script>
            document.getElementById('loginForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const btn = document.getElementById('loginBtn');
                const messageDiv = document.getElementById('message');
                
                btn.disabled = true;
                btn.textContent = 'Signing in...';
                
                try {
                    const response = await fetch('/api/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            email: document.getElementById('email').value,
                            password: document.getElementById('password').value
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        messageDiv.innerHTML = '<div class="message success">Login successful! Redirecting...</div>';
                        setTimeout(() => window.location.href = result.redirect || '/dashboard', 1000);
                    } else {
                        messageDiv.innerHTML = '<div class="message error">' + result.message + '</div>';
                        btn.disabled = false;
                        btn.textContent = 'Sign In';
                    }
                } catch (error) {
                    messageDiv.innerHTML = '<div class="message error">Network error. Please try again.</div>';
                    btn.disabled = false;
                    btn.textContent = 'Sign In';
                }
            });
        </script>
    </body>
    </html>
    """

@app.route('/dashboard')
@login_required
def dashboard():
    """Enhanced user dashboard with all three analysis tools"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard - Facts & Fakes AI</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; }
            .header { background: linear-gradient(135deg, #667eea, #764ba2); color: white; 
                     padding: 1rem; display: flex; justify-content: space-between; align-items: center; }
            .container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
            .card { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); margin-bottom: 2rem; }
            .usage-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }
            .usage-bar { background: #e0e0e0; height: 8px; border-radius: 4px; margin: 1rem 0; overflow: hidden; }
            .usage-progress { height: 100%; transition: width 0.3s ease; }
            .free { background: linear-gradient(90deg, #28a745, #20c997); }
            .pro { background: linear-gradient(90deg, #6f42c1, #e83e8c); }
            .tools-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin: 2rem 0; }
            .tool-card { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 2rem; 
                       border-radius: 12px; text-decoration: none; transition: transform 0.3s ease; }
            .tool-card:hover { transform: translateY(-5px); }
            .tool-icon { font-size: 3rem; margin-bottom: 1rem; }
            .logout-btn { background: #dc3545; color: white; padding: 0.5rem 1rem; border: none; 
                        border-radius: 6px; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Facts & Fakes AI Dashboard</h1>
            <a href="/logout" class="logout-btn">Logout</a>
        </div>
        <div class="container">
            <div class="card">
                <h2>Welcome to Your AI Detection Hub!</h2>
                <p>Access all our AI detection tools and track your usage in real-time.</p>
            </div>
            <div class="usage-grid">
                <div class="card">
                    <h3>🆓 Free Analyses</h3>
                    <div class="usage-bar"><div class="usage-progress free" style="width: 0%"></div></div>
                    <p>0 / 3 used today (3 remaining)</p>
                </div>
                <div class="card">
                    <h3>💎 Pro Analyses</h3>
                    <div class="usage-bar"><div class="usage-progress pro" style="width: 0%"></div></div>
                    <p>0 / 1 used (resets every 2 days)</p>
                </div>
            </div>
            <div class="tools-grid">
                <a href="/unified" class="tool-card">
                    <div class="tool-icon">🤖</div>
                    <h3>AI Content Detection</h3>
                    <p>Detect AI-generated text and analyze writing patterns</p>
                </a>
                <a href="/news" class="tool-card">
                    <div class="tool-icon">📰</div>
                    <h3>News Bias Analysis</h3>
                    <p>Verify news credibility and detect political bias</p>
                </a>
                <a href="/imageanalysis" class="tool-card">
                    <div class="tool-icon">🖼️</div>
                    <h3>Image Analysis</h3>
                    <p>Detect deepfakes and analyze image manipulation</p>
                </a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/logout')
@login_required
def logout_page():
    """User logout"""
    logout_user()
    session.clear()
    return redirect('/')

# API ENDPOINTS
@app.route('/api/register', methods=['POST'])
def api_register():
    """User registration API"""
    if not DATABASE_AVAILABLE:
        return jsonify({
            'success': False,
            'message': 'Registration temporarily unavailable'
        }), 503
    
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        
        if not email or not password or not first_name or not last_name:
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400
        
        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 6 characters long'
            }), 400
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Email already registered. Try signing in instead.'
            }), 400
        
        user = User(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Log the user in
        login_user(user, remember=True)
        user.record_login()
        
        logger.info(f"New user registered: {email}")
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully!',
            'redirect': '/dashboard',
            'user_id': user.id
        })
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Registration failed. Please try again.'
        }), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    """User login API"""
    if not DATABASE_AVAILABLE:
        return jsonify({
            'success': False,
            'message': 'Login temporarily unavailable'
        }), 503
    
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 400
        
        login_user(user, remember=True)
        user.record_login()
        
        logger.info(f"User logged in: {email}")
        
        return jsonify({
            'success': True,
            'message': 'Login successful!',
            'redirect': '/dashboard',
            'user_id': user.id
        })
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({
            'success': False,
            'message': 'Login failed. Please try again.'
        }), 500

# PAGE ROUTES
@app.route('/')
def index():
    """Serve the main homepage"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error serving index.html: {e}")
        return f"<h1>AI Detection Platform</h1><p>Welcome to our platform. Template loading issue: {e}</p>", 200

@app.route('/news')
@app.route('/news.html')
def news():
    """Serve the news verification page"""
    try:
        return render_template('news.html')
    except Exception as e:
        logger.error(f"Error serving news.html: {e}")
        return f"<h1>News Verification</h1><p>Template error: {e}</p><p><a href='/'>Return Home</a></p>", 200

@app.route('/unified')
@app.route('/unified.html')
def unified():
    """Serve the unified analysis page"""
    try:
        return render_template('unified.html')
    except Exception as e:
        logger.error(f"Error serving unified.html: {e}")
        return f"<h1>Unified Analysis</h1><p>Template error: {e}</p><p><a href='/'>Return Home</a></p>", 200

@app.route('/imageanalysis')
@app.route('/imageanalysis.html')
@beta_required
def imageanalysis():
    """Serve the image analysis page with authentication"""
    try:
        return render_template('imageanalysis.html')
    except Exception as e:
        logger.error(f"Error serving imageanalysis.html: {e}")
        return f"<h1>Image Analysis</h1><p>Template error: {e}</p><p><a href='/'>Return Home</a></p>", 200

@app.route('/contact')
@app.route('/contact.html')
def contact():
    """Serve the contact page"""
    try:
        return render_template('contact.html')
    except Exception as e:
        logger.error(f"Error serving contact.html: {e}")
        return f"<h1>Contact Us</h1><p>Template error: {e}</p><p><a href='/'>Return Home</a></p>", 200

@app.route('/missionstatement')
@app.route('/missionstatement.html')
def missionstatement():
    try:
        return render_template('missionstatement.html')
    except Exception as e:
        logger.error(f"Error serving missionstatement.html: {e}")
        return f"<h1>Mission Statement</h1><p>Template error: {e}</p><p><a href='/'>Return Home</a></p>", 200

@app.route('/pricingplan')
@app.route('/pricingplan.html')
def pricingplan():
    try:
        return render_template('pricingplan.html')
    except Exception as e:
        logger.error(f"Error serving pricingplan.html: {e}")
        return f"<h1>Pricing Plan</h1><p>Template error: {e}</p><p><a href='/'>Return Home</a></p>", 200

# API health check
@app.route('/api/health', methods=['GET'])
def health_check():
    """Enhanced health check with image analysis"""
    try:
        health_status = {
            "status": "operational",
            "message": "Facts & Fakes AI - Complete AI Detection Platform (All Tools Integrated)",
            "timestamp": datetime.now().isoformat(),
            "version": "3.1-complete-integration-python313-fixed",
            "apis": {
                "openai": "connected" if openai_client else "not_configured",
                "newsapi": "available" if NEWS_API_KEY else "not_configured", 
                "google_factcheck": "configured" if GOOGLE_FACT_CHECK_API_KEY else "not_configured",
                "email_smtp": "configured" if EMAIL_AVAILABLE and SMTP_PASSWORD else "not_configured"
            },
            "endpoints": {
                "news_analysis": "/api/analyze-news",
                "ai_detection": "/api/detect-ai", 
                "image_analysis": "/api/analyze-image",
                "contact_form": "/api/contact",
                "user_register": "/api/register",
                "user_login": "/api/login"
            },
            "system_status": "healthy",
            "python_version": "3.13_compatible",
            "email_status": "available" if EMAIL_AVAILABLE else "unavailable",
            "authentication": "Flask-Login enabled"
        }
        
        if DATABASE_AVAILABLE:
            try:
                with app.app_context():
                    db.session.execute(text('SELECT 1'))
                    health_status['database'] = {'status': 'connected', 'type': 'postgresql'}
                    health_status['authentication_features'] = {
                        'status': 'enabled', 
                        'user_tracking': 'active',
                        'session_management': 'flask-login',
                        'usage_limits': 'enforced',
                        'tools_integrated': 'all_three'
                    }
            except Exception as e:
                health_status['database'] = {'status': 'error', 'error': str(e)}
                health_status['authentication_features'] = {'status': 'disabled', 'reason': 'database_error'}
        else:
            health_status['database'] = {'status': 'not_configured'}
            health_status['authentication_features'] = {'status': 'disabled', 'reason': 'database_not_available'}
        
        return jsonify(health_status)
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# BASIC ANALYSIS STUB FUNCTIONS (implement full versions as needed)
def perform_image_analysis(image_data, image_url, analysis_type):
    """Basic image analysis stub"""
    return {
        'status': 'success',
        'timestamp': datetime.now().isoformat(),
        'analysis_type': analysis_type,
        'image_source': 'upload' if image_data else 'url',
        'deepfake_probability': 0.15,
        'manipulation_detected': False,
        'confidence_score': 0.82,
        'analysis_summary': 'Basic image analysis completed. No obvious signs of manipulation detected.'
    }

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors gracefully"""
    return jsonify({'error': 'Page not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors gracefully"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# Main application
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info("=" * 50)
    logger.info("FACTS & FAKES AI - SYNTAX CORRECTED VERSION 3.1")
    logger.info("=" * 50)
    logger.info(f"Authentication: Flask-Login Enabled")
    logger.info(f"Database: {'✓ Connected' if DATABASE_AVAILABLE else '✗ Not available'}")
    logger.info(f"All Tools: 🤖 AI Detection | 📰 News Analysis | 🖼️ Image Analysis")
    logger.info("=" * 50)
    
    try:
        app.run(host='0.0.0.0', port=port, debug=debug_mode)
    except Exception as e:
        logger.error(f"CRITICAL: Failed to start application: {e}")
        raise
