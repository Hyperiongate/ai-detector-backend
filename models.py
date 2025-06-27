from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json
import uuid

db = SQLAlchemy()

class User(db.Model):
    """User accounts and subscription management"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    subscription_tier = db.Column(db.String(20), default='free')  # free, pro, enterprise
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Usage tracking
    analyses_today = db.Column(db.Integer, default=0)
    analyses_this_month = db.Column(db.Integer, default=0)
    last_reset_date = db.Column(db.Date, default=datetime.utcnow().date)
    
    # Subscription details
    stripe_customer_id = db.Column(db.String(255), nullable=True)
    subscription_status = db.Column(db.String(50), default='active')  # active, canceled, past_due
    subscription_end_date = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    analyses = db.relationship('Analysis', backref='user', lazy=True, cascade='all, delete-orphan')
    api_keys = db.relationship('UserAPIKey', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def can_analyze(self, analysis_type='free'):
        """Check if user can perform analysis based on tier and usage"""
        today = datetime.utcnow().date()
        
        # Reset daily counter if needed
        if self.last_reset_date < today:
            self.analyses_today = 0
            self.last_reset_date = today
            db.session.commit()
        
        # Check limits based on tier
        if self.subscription_tier == 'free':
            return self.analyses_today < 5  # 5 free analyses per day
        elif self.subscription_tier == 'pro':
            return self.analyses_today < 100  # 100 pro analyses per day
        elif self.subscription_tier == 'enterprise':
            return True  # Unlimited
        
        return False
    
    def increment_usage(self):
        """Increment usage counters"""
        self.analyses_today += 1
        self.analyses_this_month += 1
        self.last_active = datetime.utcnow()
        db.session.commit()

class Analysis(db.Model):
    """Store analysis results and history"""
    __tablename__ = 'analyses'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)  # Allow anonymous
    
    # Analysis metadata
    analysis_type = db.Column(db.String(20), nullable=False)  # news, ai_detection, plagiarism
    tier = db.Column(db.String(20), nullable=False)  # free, pro
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Input data
    input_text = db.Column(db.Text, nullable=True)
    input_url = db.Column(db.String(500), nullable=True)
    input_method = db.Column(db.String(20), nullable=False)  # text, url, file
    
    # Results (stored as JSON)
    results = db.Column(db.JSON, nullable=False)
    
    # Performance metrics
    processing_time_seconds = db.Column(db.Float, nullable=True)
    api_calls_made = db.Column(db.JSON, nullable=True)  # Track which APIs were called
    
    # Status
    status = db.Column(db.String(20), default='completed')  # processing, completed, failed
    error_message = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Analysis {self.id} - {self.analysis_type}>'
    
    def get_summary(self):
        """Get analysis summary for display"""
        if not self.results:
            return None
        
        try:
            if self.analysis_type == 'news':
                score = self.results.get('scoring', {}).get('overall_credibility', 0)
                assessment = self.results.get('executive_summary', {}).get('main_assessment', 'Unknown')
                return {
                    'score': score,
                    'assessment': assessment,
                    'type': 'News Verification'
                }
            elif self.analysis_type == 'ai_detection':
                ai_prob = self.results.get('ai_detection', {}).get('ai_probability', 0)
                return {
                    'ai_probability': ai_prob,
                    'type': 'AI Detection'
                }
        except Exception as e:
            return {'error': str(e)}

class UserAPIKey(db.Model):
    """User API keys for enterprise customers"""
    __tablename__ = 'user_api_keys'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    key_name = db.Column(db.String(100), nullable=False)
    api_key = db.Column(db.String(64), unique=True, nullable=False)  # Generated hash
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Usage tracking
    requests_today = db.Column(db.Integer, default=0)
    requests_this_month = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<APIKey {self.key_name}>'

class SystemMetrics(db.Model):
    """Track platform metrics and health"""
    __tablename__ = 'system_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # API Health
    openai_status = db.Column(db.String(20), default='unknown')
    news_api_status = db.Column(db.String(20), default='unknown')
    google_factcheck_status = db.Column(db.String(20), default='unknown')
    
    # Performance
    avg_response_time = db.Column(db.Float, nullable=True)
    total_analyses_today = db.Column(db.Integer, default=0)
    error_count_today = db.Column(db.Integer, default=0)
    
    # Resource usage
    memory_usage_mb = db.Column(db.Float, nullable=True)
    cpu_usage_percent = db.Column(db.Float, nullable=True)
    
    def __repr__(self):
        return f'<SystemMetrics {self.timestamp}>'

class CachedResult(db.Model):
    """Cache expensive API results"""
    __tablename__ = 'cached_results'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Cache key (hash of input + analysis type)
    cache_key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    
    # Cached data
    result_data = db.Column(db.JSON, nullable=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    hit_count = db.Column(db.Integer, default=0)
    
    # Source tracking
    analysis_type = db.Column(db.String(20), nullable=False)
    input_hash = db.Column(db.String(64), nullable=False)
    
    def __repr__(self):
        return f'<CachedResult {self.cache_key}>'
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    def increment_hit(self):
        self.hit_count += 1
        db.session.commit()

# Database utility functions
def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create indices for performance
        try:
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at DESC);')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_analyses_user_created ON analyses(user_id, created_at DESC);')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_cached_results_expires ON cached_results(expires_at);')
        except Exception as e:
            print(f"Index creation warning: {e}")

def get_or_create_user(email, subscription_tier='free'):
    """Get existing user or create new one"""
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            email=email,
            subscription_tier=subscription_tier
        )
        db.session.add(user)
        db.session.commit()
    return user

def cleanup_expired_cache():
    """Remove expired cache entries"""
    expired = CachedResult.query.filter(CachedResult.expires_at < datetime.utcnow()).all()
    for item in expired:
        db.session.delete(item)
    db.session.commit()
    return len(expired)