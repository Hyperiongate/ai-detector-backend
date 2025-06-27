from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """User model for subscription and usage tracking"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subscription_tier = db.Column(db.String(20), default='free', nullable=False)  # 'free', 'pro'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Usage tracking
    total_analyses = db.Column(db.Integer, default=0)
    subscription_start = db.Column(db.DateTime)
    subscription_end = db.Column(db.DateTime)
    
    # Relationships
    analyses = db.relationship('Analysis', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def is_pro(self):
        """Check if user has active pro subscription"""
        if self.subscription_tier != 'pro':
            return False
        
        if self.subscription_end and self.subscription_end < datetime.utcnow():
            return False
            
        return True
    
    def get_daily_usage(self, analysis_type=None):
        """Get today's usage count for specific analysis type"""
        today = datetime.utcnow().date()
        query = Analysis.query.filter(
            Analysis.user_id == self.id,
            Analysis.created_at >= today
        )
        
        if analysis_type:
            query = query.filter(Analysis.analysis_type == analysis_type)
            
        return query.count()
    
    def can_analyze(self, analysis_type):
        """Check if user can perform analysis based on limits"""
        if self.is_pro():
            return True, ""
        
        # Free tier limits
        limits = {
            'news_analysis': 5,
            'fact_check': 3,
            'general': 10
        }
        
        limit = limits.get(analysis_type, 5)
        current_usage = self.get_daily_usage(analysis_type)
        
        if current_usage >= limit:
            return False, f"Daily limit reached ({limit} {analysis_type} analyses per day)"
        
        return True, ""

class Analysis(db.Model):
    """Analysis history and results storage"""
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    analysis_type = db.Column(db.String(50), nullable=False)  # 'news_analysis', 'fact_check', 'general'
    query = db.Column(db.Text, nullable=False)
    results = db.Column(db.Text)  # JSON string of results
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_pro_result = db.Column(db.Boolean, default=False)
    processing_time = db.Column(db.Float)  # seconds
    api_calls_made = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Analysis {self.id}: {self.analysis_type}>'
    
    def get_results_json(self):
        """Parse results JSON safely"""
        try:
            return json.loads(self.results) if self.results else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def set_results_json(self, results_dict):
        """Set results as JSON string"""
        try:
            self.results = json.dumps(results_dict)
        except (TypeError, ValueError):
            self.results = "{}"

class UsageLog(db.Model):
    """Detailed usage logging for analytics and billing"""
    __tablename__ = 'usage_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # 'api_call', 'analysis_start', 'analysis_complete'
    resource = db.Column(db.String(50))  # 'openai', 'news_api', 'fact_check_api'
    details = db.Column(db.Text)  # JSON string with additional details
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    cost_credits = db.Column(db.Integer, default=0)  # Internal credit system
    
    def __repr__(self):
        return f'<UsageLog {self.action}: {self.resource}>'

class APIHealth(db.Model):
    """Track API health and performance"""
    __tablename__ = 'api_health'
    
    id = db.Column(db.Integer, primary_key=True)
    api_name = db.Column(db.String(50), nullable=False)  # 'openai', 'news_api', 'fact_check_api'
    status = db.Column(db.String(20), nullable=False)  # 'healthy', 'degraded', 'down'
    response_time = db.Column(db.Float)  # milliseconds
    error_message = db.Column(db.Text)
    checked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<APIHealth {self.api_name}: {self.status}>'

def init_db(app):
    """Initialize database with app context"""
    with app.app_context():
        db.create_all()
        
        # Create default admin user if none exists
        if not User.query.filter_by(email='admin@example.com').first():
            admin_user = User(
                email='admin@example.com',
                subscription_tier='pro',
                is_anonymous=False
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Created default admin user")

# Utility functions for database operations
def create_user(email, subscription_tier='free'):
    """Create a new user"""
    try:
        user = User(
            email=email,
            subscription_tier=subscription_tier
        )
        db.session.add(user)
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        raise e

def log_api_usage(user_id, action, resource=None, details=None, cost_credits=0):
    """Log API usage for analytics"""
    try:
        usage_log = UsageLog(
            user_id=user_id,
            action=action,
            resource=resource,
            details=json.dumps(details) if details else None,
            cost_credits=cost_credits
        )
        db.session.add(usage_log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Failed to log usage: {e}")

def update_api_health(api_name, status, response_time=None, error_message=None):
    """Update API health status"""
    try:
        health_record = APIHealth(
            api_name=api_name,
            status=status,
            response_time=response_time,
            error_message=error_message
        )
        db.session.add(health_record)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Failed to update API health: {e}")

def get_user_analytics(user_id, days=30):
    """Get user analytics for dashboard"""
    from datetime import timedelta
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    try:
        analyses = Analysis.query.filter(
            Analysis.user_id == user_id,
            Analysis.created_at >= start_date
        ).all()
        
        analytics = {
            'total_analyses': len(analyses),
            'by_type': {},
            'daily_usage': {},
            'avg_processing_time': 0
        }
        
        # Group by type
        for analysis in analyses:
            analysis_type = analysis.analysis_type
            if analysis_type not in analytics['by_type']:
                analytics['by_type'][analysis_type] = 0
            analytics['by_type'][analysis_type] += 1
        
        # Calculate average processing time
        processing_times = [a.processing_time for a in analyses if a.processing_time]
        if processing_times:
            analytics['avg_processing_time'] = sum(processing_times) / len(processing_times)
        
        return analytics
    
    except Exception as e:
        print(f"Failed to get user analytics: {e}")
        return {}
