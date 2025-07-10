"""
Database models and utilities for Facts & Fakes AI
"""

import json
import logging
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize SQLAlchemy
db = SQLAlchemy()

# Configure logging
logger = logging.getLogger(__name__)

# Database Models

class User(UserMixin, db.Model):
    """User model for authentication and subscription tracking"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(100), nullable=True)
    subscription_tier = db.Column(db.String(20), default='free')  # 'free', 'pro'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    analyses = db.relationship('Analysis', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'subscription_tier': self.subscription_tier,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Analysis(db.Model):
    """Analysis history and results storage"""
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)  # 'text', 'news', 'image', 'speech', 'unified'
    content_snippet = db.Column(db.Text)  # First 500 chars of content
    results = db.Column(db.Text)  # JSON string of analysis results
    trust_score = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_results_dict(self):
        """Get results as dictionary"""
        if self.results:
            try:
                return json.loads(self.results)
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON for analysis {self.id}")
                return {}
        return {}
    
    def set_results_dict(self, results_dict):
        """Set results from dictionary"""
        try:
            self.results = json.dumps(results_dict)
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to encode results to JSON: {str(e)}")
            self.results = '{}'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_type': self.content_type,
            'content_snippet': self.content_snippet,
            'results': self.get_results_dict(),
            'trust_score': self.trust_score,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class UsageLog(db.Model):
    """Track user usage for rate limiting and analytics"""
    __tablename__ = 'usage_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # nullable for anonymous
    session_id = db.Column(db.String(255), nullable=True)  # For anonymous tracking
    analysis_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('usage_logs', lazy='dynamic'))
    
    # Add indexes for better query performance
    __table_args__ = (
        db.Index('idx_usage_user_time', 'user_id', 'timestamp'),
        db.Index('idx_usage_session_time', 'session_id', 'timestamp'),
    )
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'analysis_type': self.analysis_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class APIHealth(db.Model):
    """Track API health and performance"""
    __tablename__ = 'api_health'
    
    id = db.Column(db.Integer, primary_key=True)
    api_name = db.Column(db.String(50), nullable=False)  # 'openai', 'copyscape', etc.
    status = db.Column(db.String(20), nullable=False)  # 'healthy', 'degraded', 'down'
    response_time = db.Column(db.Float)  # in seconds
    error_message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'api_name': self.api_name,
            'status': self.status,
            'response_time': self.response_time,
            'error_message': self.error_message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class Contact(db.Model):
    """Contact form submissions"""
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class BetaSignup(db.Model):
    """Beta signup registrations"""
    __tablename__ = 'beta_signups'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'email': self.email,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

# Utility functions

def create_missing_tables():
    """Create database tables that don't exist yet"""
    try:
        # Get list of existing tables
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        # Define all tables that should exist
        required_tables = ['users', 'analyses', 'usage_logs', 'api_health', 'contacts', 'beta_signups']
        
        # Create only missing tables
        tables_created = []
        for table_name in required_tables:
            if table_name not in existing_tables:
                # Find the model class for this table
                for model in [User, Analysis, UsageLog, APIHealth, Contact, BetaSignup]:
                    if model.__tablename__ == table_name:
                        model.__table__.create(db.engine)
                        tables_created.append(table_name)
                        logger.info(f"Created table: {table_name}")
                        break
        
        if tables_created:
            logger.info(f"Created {len(tables_created)} missing tables: {', '.join(tables_created)}")
        else:
            logger.info("All required tables already exist")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def add_session_id_column():
    """Add session_id column to usage_logs table if it doesn't exist"""
    try:
        with db.engine.connect() as conn:
            # Check if column exists
            result = conn.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='usage_logs' 
                AND column_name='session_id'
            """)
            
            if not result.fetchone():
                # Column doesn't exist, add it
                conn.execute('ALTER TABLE usage_logs ADD COLUMN session_id VARCHAR(255)')
                conn.commit()
                logger.info("Added session_id column to usage_logs table")
                return True
            else:
                logger.info("session_id column already exists")
                return False
    except Exception as e:
        logger.error(f"Error adding session_id column: {str(e)}")
        return False

def get_user_analytics(user_id, days=30):
    """Get analytics for a specific user"""
    try:
        from datetime import timedelta
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Get analysis count by type
        analyses = db.session.query(
            Analysis.content_type,
            db.func.count(Analysis.id).label('count'),
            db.func.avg(Analysis.trust_score).label('avg_trust_score')
        ).filter(
            Analysis.user_id == user_id,
            Analysis.timestamp >= since_date
        ).group_by(Analysis.content_type).all()
        
        # Get usage patterns
        usage = db.session.query(
            db.func.date(UsageLog.timestamp).label('date'),
            db.func.count(UsageLog.id).label('count')
        ).filter(
            UsageLog.user_id == user_id,
            UsageLog.timestamp >= since_date
        ).group_by(db.func.date(UsageLog.timestamp)).all()
        
        return {
            'analyses_by_type': [
                {
                    'type': a.content_type,
                    'count': a.count,
                    'avg_trust_score': float(a.avg_trust_score) if a.avg_trust_score else 0
                }
                for a in analyses
            ],
            'usage_by_date': [
                {
                    'date': str(u.date),
                    'count': u.count
                }
                for u in usage
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting user analytics: {str(e)}")
        return {'analyses_by_type': [], 'usage_by_date': []}

def cleanup_old_data(days=90):
    """Clean up old data from the database"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Delete old usage logs
        old_usage = UsageLog.query.filter(UsageLog.timestamp < cutoff_date).count()
        if old_usage > 0:
            UsageLog.query.filter(UsageLog.timestamp < cutoff_date).delete()
            logger.info(f"Deleted {old_usage} old usage logs")
        
        # Delete old API health records
        old_health = APIHealth.query.filter(APIHealth.timestamp < cutoff_date).count()
        if old_health > 0:
            APIHealth.query.filter(APIHealth.timestamp < cutoff_date).delete()
            logger.info(f"Deleted {old_health} old API health records")
        
        # Commit changes
        db.session.commit()
        
        return True
        
    except Exception as e:
        logger.error(f"Error cleaning up old data: {str(e)}")
        db.session.rollback()
        return False
