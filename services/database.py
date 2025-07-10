"""
Database service - Models and database initialization
"""
from datetime import datetime, timedelta
import bcrypt
import json

# Database imports with safe handling
try:
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy.exc import OperationalError, IntegrityError
    DB_AVAILABLE = True
    print("✓ Database modules loaded successfully")
except ImportError:
    DB_AVAILABLE = False
    SQLAlchemy = None
    print("⚠ Database modules not available - using memory storage")

# Initialize database
if DB_AVAILABLE:
    db = SQLAlchemy()
else:
    db = None

# Database Models
if DB_AVAILABLE:
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(120), unique=True, nullable=False, index=True)
        password_hash = db.Column(db.String(200), nullable=False)
        subscription_tier = db.Column(db.String(20), default='free')
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        last_login = db.Column(db.DateTime)
        daily_analyses_count = db.Column(db.Integer, default=0)
        last_analysis_reset = db.Column(db.Date, default=datetime.utcnow().date)
        is_active = db.Column(db.Boolean, default=True)
        is_beta_user = db.Column(db.Boolean, default=True)
        
        # Relationships
        analyses = db.relationship('Analysis', backref='user', lazy=True, cascade='all, delete-orphan')
        usage_logs = db.relationship('UsageLog', backref='user', lazy=True, cascade='all, delete-orphan')
        
        def set_password(self, password):
            self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        def check_password(self, password):
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        
        def get_daily_limit(self):
            return 10 if self.subscription_tier == 'pro' else 5
        
        def can_analyze(self):
            # DEVELOPMENT MODE: Always return True
            return True
            
        def increment_analysis_count(self):
            # DEVELOPMENT MODE: Skip tracking
            pass

    class Analysis(db.Model):
        """Store analysis results for all types of content analysis"""
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        
        # Analysis metadata
        content_type = db.Column(db.String(50), nullable=False, index=True)  # 'text', 'news', 'image', 'speech', 'unified'
        content_snippet = db.Column(db.Text)  # First 500 chars of analyzed content
        content_hash = db.Column(db.String(64), index=True)  # For duplicate detection
        
        # Results storage
        results = db.Column(db.Text, nullable=False)  # JSON string of analysis results
        trust_score = db.Column(db.Integer, default=50)  # 0-100 trust score
        
        # Analysis details
        analysis_duration = db.Column(db.Float)  # Time taken in seconds
        services_used = db.Column(db.Text)  # JSON array of services used
        api_calls_made = db.Column(db.Integer, default=0)  # Number of API calls
        
        # Status and metadata
        status = db.Column(db.String(20), default='completed')  # 'completed', 'failed', 'partial'
        error_message = db.Column(db.Text)  # Error details if analysis failed
        ip_address = db.Column(db.String(45))  # User's IP for analytics
        user_agent = db.Column(db.String(500))  # Browser info
        
        # Timestamps
        timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Sharing and export
        is_shared = db.Column(db.Boolean, default=False)
        share_token = db.Column(db.String(32), unique=True)  # For public sharing
        pdf_generated = db.Column(db.Boolean, default=False)
        
        def get_results_dict(self):
            """Parse JSON results safely"""
            try:
                return json.loads(self.results) if self.results else {}
            except (json.JSONDecodeError, TypeError):
                return {}
        
        def set_results_dict(self, results_dict):
            """Store results as JSON"""
            try:
                self.results = json.dumps(results_dict)
            except (TypeError, ValueError):
                self.results = '{}'
        
        def get_services_used_list(self):
            """Parse services used safely"""
            try:
                return json.loads(self.services_used) if self.services_used else []
            except (json.JSONDecodeError, TypeError):
                return []
        
        def set_services_used_list(self, services_list):
            """Store services used as JSON"""
            try:
                self.services_used = json.dumps(services_list)
            except (TypeError, ValueError):
                self.services_used = '[]'

    class UsageLog(db.Model):
        """Track detailed usage for analytics and billing"""
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        
        # Usage details
        analysis_type = db.Column(db.String(50), nullable=False, index=True)  # 'text', 'news', 'image', etc.
        analysis_id = db.Column(db.Integer, db.ForeignKey('analysis.id'), nullable=True)
        
        # Resource usage
        processing_time = db.Column(db.Float)  # Seconds
        api_calls = db.Column(db.Integer, default=0)  # Number of API calls made
        tokens_used = db.Column(db.Integer, default=0)  # For AI APIs
        
        # Request details
        content_size = db.Column(db.Integer)  # Size of content analyzed
        subscription_tier = db.Column(db.String(20))  # User's tier at time of analysis
        
        # Technical details
        ip_address = db.Column(db.String(45))
        user_agent = db.Column(db.String(500))
        endpoint = db.Column(db.String(100))  # API endpoint used
        
        # Status
        success = db.Column(db.Boolean, default=True)
        error_type = db.Column(db.String(50))  # Type of error if failed
        
        # Timestamps
        timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
        
        # Billing and limits
        billable = db.Column(db.Boolean, default=True)  # Whether this counts toward limits
        cost_cents = db.Column(db.Integer, default=0)  # Cost in cents for pro features

    class APIHealth(db.Model):
        """Monitor API health and performance"""
        id = db.Column(db.Integer, primary_key=True)
        
        # API details
        service_name = db.Column(db.String(50), nullable=False, index=True)  # 'openai', 'copyscape', etc.
        endpoint = db.Column(db.String(200))  # Specific endpoint tested
        
        # Health metrics
        status = db.Column(db.String(20), nullable=False)  # 'healthy', 'degraded', 'down'
        response_time_ms = db.Column(db.Integer)  # Response time in milliseconds
        success_rate = db.Column(db.Float)  # Success rate over last period
        
        # Error tracking
        last_error = db.Column(db.Text)  # Last error message
        error_count_24h = db.Column(db.Integer, default=0)  # Errors in last 24h
        
        # Usage tracking
        requests_today = db.Column(db.Integer, default=0)
        requests_this_hour = db.Column(db.Integer, default=0)
        rate_limit_hit = db.Column(db.Boolean, default=False)
        
        # Timestamps
        last_check = db.Column(db.DateTime, default=datetime.utcnow, index=True)
        last_success = db.Column(db.DateTime)
        last_failure = db.Column(db.DateTime)
        
        # Configuration
        check_interval_minutes = db.Column(db.Integer, default=5)
        timeout_seconds = db.Column(db.Integer, default=30)
        
        @classmethod
        def get_service_status(cls, service_name):
            """Get the latest status for a service"""
            latest = cls.query.filter_by(service_name=service_name)\
                        .order_by(cls.last_check.desc()).first()
            return latest.status if latest else 'unknown'
        
        @classmethod
        def update_service_health(cls, service_name, status, response_time=None, error=None):
            """Update health status for a service"""
            health_record = cls.query.filter_by(service_name=service_name).first()
            
            if not health_record:
                health_record = cls(service_name=service_name)
                db.session.add(health_record)
            
            health_record.status = status
            health_record.last_check = datetime.utcnow()
            
            if response_time:
                health_record.response_time_ms = response_time
            
            if status == 'healthy':
                health_record.last_success = datetime.utcnow()
            else:
                health_record.last_failure = datetime.utcnow()
                if error:
                    health_record.last_error = str(error)
                    health_record.error_count_24h += 1
            
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Failed to update API health: {e}")

    class Contact(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(120), nullable=False)
        subject = db.Column(db.String(200), nullable=False)
        message = db.Column(db.Text, nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        ip_address = db.Column(db.String(45))
        user_agent = db.Column(db.String(500))

    class BetaSignup(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(120), unique=True, nullable=False, index=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        ip_address = db.Column(db.String(45))
        referrer = db.Column(db.String(500))
        welcome_email_sent = db.Column(db.Boolean, default=False)

else:
    # Placeholder classes if DB not available
    class User:
        pass
    
    class Analysis:
        pass
    
    class UsageLog:
        pass
    
    class APIHealth:
        pass
    
    class Contact:
        pass
    
    class BetaSignup:
        pass

# Utility functions for database operations
def init_database():
    """Initialize database tables"""
    if DB_AVAILABLE and db:
        try:
            db.create_all()
            print("✓ Database tables created successfully")
            return True
        except Exception as e:
            print(f"✗ Database initialization failed: {e}")
            return False
    return False

def get_user_analytics(user_id, days=30):
    """Get user analytics for the last N days"""
    if not DB_AVAILABLE:
        return {}
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    try:
        analyses = Analysis.query.filter(
            Analysis.user_id == user_id,
            Analysis.timestamp >= cutoff_date
        ).all()
        
        usage_logs = UsageLog.query.filter(
            UsageLog.user_id == user_id,
            UsageLog.timestamp >= cutoff_date
        ).all()
        
        return {
            'total_analyses': len(analyses),
            'avg_trust_score': sum(a.trust_score for a in analyses) / len(analyses) if analyses else 0,
            'content_types': {ct: len([a for a in analyses if a.content_type == ct]) 
                            for ct in set(a.content_type for a in analyses)},
            'total_api_calls': sum(log.api_calls for log in usage_logs),
            'avg_processing_time': sum(log.processing_time for log in usage_logs if log.processing_time) / 
                                 len([log for log in usage_logs if log.processing_time]) if usage_logs else 0
        }
    except Exception as e:
        print(f"Analytics error: {e}")
        return {}

def cleanup_old_data(days=90):
    """Clean up old data to maintain performance"""
    if not DB_AVAILABLE:
        return
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    try:
        # Delete old usage logs
        old_logs = UsageLog.query.filter(UsageLog.timestamp < cutoff_date).delete()
        
        # Delete old API health records
        old_health = APIHealth.query.filter(APIHealth.last_check < cutoff_date).delete()
        
        db.session.commit()
        print(f"✓ Cleaned up {old_logs} usage logs and {old_health} health records")
        
    except Exception as e:
        db.session.rollback()
        print(f"✗ Cleanup failed: {e}")
