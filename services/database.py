"""
Database models and utilities for Facts & Fakes AI
Enhanced with better migration handling and additional features
"""

import json
import logging
from datetime import datetime, timedelta
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
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    
    # Relationships
    analyses = db.relationship('Analysis', backref='user', lazy='dynamic')
    usage_logs = db.relationship('UsageLog', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def get_usage_count(self, analysis_type, period='daily'):
        """Get usage count for specific analysis type and period"""
        if period == 'daily':
            start_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        else:  # weekly
            today = datetime.utcnow()
            start_time = today - timedelta(days=today.weekday())
            start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        
        return self.usage_logs.filter(
            UsageLog.analysis_type == analysis_type,
            UsageLog.timestamp >= start_time
        ).count()
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'subscription_tier': self.subscription_tier,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'email_verified': self.email_verified
        }

class Analysis(db.Model):
    """Analysis history and results storage"""
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # nullable for anonymous
    content_type = db.Column(db.String(50), nullable=False)  # 'text', 'news', 'image', 'speech', 'unified'
    content_snippet = db.Column(db.Text)  # First 500 chars of content
    results = db.Column(db.Text)  # JSON string of analysis results
    trust_score = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    processing_time = db.Column(db.Float)  # Seconds
    is_pro_analysis = db.Column(db.Boolean, default=False)
    source_url = db.Column(db.String(500))
    
    # Metadata
    ai_probability = db.Column(db.Float)
    plagiarism_score = db.Column(db.Float)
    readability_score = db.Column(db.Float)
    
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
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'processing_time': self.processing_time,
            'is_pro_analysis': self.is_pro_analysis,
            'source_url': self.source_url,
            'ai_probability': self.ai_probability,
            'plagiarism_score': self.plagiarism_score,
            'readability_score': self.readability_score
        }

class UsageLog(db.Model):
    """Track user usage for rate limiting and analytics"""
    __tablename__ = 'usage_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # nullable for anonymous
    session_id = db.Column(db.String(255), nullable=True)  # For anonymous tracking
    analysis_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))  # Support IPv6
    
    # Add indexes for better query performance
    __table_args__ = (
        db.Index('idx_usage_user_time', 'user_id', 'timestamp'),
        db.Index('idx_usage_session_time', 'session_id', 'timestamp'),
        db.Index('idx_usage_type_time', 'analysis_type', 'timestamp'),
    )
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'analysis_type': self.analysis_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ip_address': self.ip_address
        }

class APIHealth(db.Model):
    """Track API health and performance"""
    __tablename__ = 'api_health'
    
    id = db.Column(db.Integer, primary_key=True)
    api_name = db.Column(db.String(50), nullable=False)  # 'openai', 'copyscape', etc.
    service_name = db.Column(db.String(50))  # More specific service
    endpoint = db.Column(db.String(200))
    status = db.Column(db.String(20), nullable=False)  # 'healthy', 'degraded', 'down'
    status_code = db.Column(db.Integer)
    response_time = db.Column(db.Float)  # in seconds
    error_message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_healthy = db.Column(db.Boolean, default=True)
    
    # Add index for performance
    __table_args__ = (
        db.Index('idx_api_health_time', 'api_name', 'timestamp'),
    )
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'api_name': self.api_name,
            'service_name': self.service_name,
            'endpoint': self.endpoint,
            'status': self.status,
            'status_code': self.status_code,
            'response_time': self.response_time,
            'error_message': self.error_message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'is_healthy': self.is_healthy
        }

class Contact(db.Model):
    """Contact form submissions"""
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_resolved = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'is_resolved': self.is_resolved
        }

class BetaSignup(db.Model):
    """Beta signup registrations"""
    __tablename__ = 'beta_signups'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'email': self.email,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'is_approved': self.is_approved
        }

# Utility functions

def init_db():
    """Initialize database with all tables"""
    try:
        # Create all tables
        db.create_all()
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        return False

def create_missing_tables():
    """Create database tables that don't exist yet"""
    try:
        # Get list of existing tables
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        logger.info(f"Existing tables in database: {existing_tables}")
        
        # Define all tables that should exist
        required_tables = ['users', 'analyses', 'usage_logs', 'api_health', 'contacts', 'beta_signups']
        
        # Create only missing tables
        tables_created = []
        for table_name in required_tables:
            if table_name not in existing_tables:
                # Find the model class for this table
                for model in [User, Analysis, UsageLog, APIHealth, Contact, BetaSignup]:
                    if model.__tablename__ == table_name:
                        try:
                            model.__table__.create(db.engine)
                            tables_created.append(table_name)
                            logger.info(f"Created table: {table_name}")
                        except Exception as table_error:
                            logger.error(f"Error creating table {table_name}: {str(table_error)}")
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

def add_missing_columns():
    """Add any missing columns to existing tables"""
    try:
        with db.engine.connect() as conn:
            inspector = db.inspect(db.engine)
            
            # Check and add missing columns for each table
            updates_made = []
            
            # Check users table
            if 'users' in inspector.get_table_names():
                user_columns = [col['name'] for col in inspector.get_columns('users')]
                
                if 'is_active' not in user_columns:
                    conn.execute('ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE')
                    updates_made.append('users.is_active')
                
                if 'email_verified' not in user_columns:
                    conn.execute('ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE')
                    updates_made.append('users.email_verified')
            
            # Check analyses table
            if 'analyses' in inspector.get_table_names():
                analysis_columns = [col['name'] for col in inspector.get_columns('analyses')]
                
                if 'processing_time' not in analysis_columns:
                    conn.execute('ALTER TABLE analyses ADD COLUMN processing_time FLOAT')
                    updates_made.append('analyses.processing_time')
                
                if 'is_pro_analysis' not in analysis_columns:
                    conn.execute('ALTER TABLE analyses ADD COLUMN is_pro_analysis BOOLEAN DEFAULT FALSE')
                    updates_made.append('analyses.is_pro_analysis')
                
                if 'source_url' not in analysis_columns:
                    conn.execute('ALTER TABLE analyses ADD COLUMN source_url VARCHAR(500)')
                    updates_made.append('analyses.source_url')
                
                if 'ai_probability' not in analysis_columns:
                    conn.execute('ALTER TABLE analyses ADD COLUMN ai_probability FLOAT')
                    updates_made.append('analyses.ai_probability')
                
                if 'plagiarism_score' not in analysis_columns:
                    conn.execute('ALTER TABLE analyses ADD COLUMN plagiarism_score FLOAT')
                    updates_made.append('analyses.plagiarism_score')
                
                if 'readability_score' not in analysis_columns:
                    conn.execute('ALTER TABLE analyses ADD COLUMN readability_score FLOAT')
                    updates_made.append('analyses.readability_score')
            
            # Check usage_logs table
            if 'usage_logs' in inspector.get_table_names():
                usage_columns = [col['name'] for col in inspector.get_columns('usage_logs')]
                
                if 'session_id' not in usage_columns:
                    conn.execute('ALTER TABLE usage_logs ADD COLUMN session_id VARCHAR(255)')
                    updates_made.append('usage_logs.session_id')
                
                if 'ip_address' not in usage_columns:
                    conn.execute('ALTER TABLE usage_logs ADD COLUMN ip_address VARCHAR(45)')
                    updates_made.append('usage_logs.ip_address')
            
            # Check api_health table
            if 'api_health' in inspector.get_table_names():
                health_columns = [col['name'] for col in inspector.get_columns('api_health')]
                
                if 'service_name' not in health_columns:
                    conn.execute('ALTER TABLE api_health ADD COLUMN service_name VARCHAR(50)')
                    updates_made.append('api_health.service_name')
                
                if 'endpoint' not in health_columns:
                    conn.execute('ALTER TABLE api_health ADD COLUMN endpoint VARCHAR(200)')
                    updates_made.append('api_health.endpoint')
                
                if 'status_code' not in health_columns:
                    conn.execute('ALTER TABLE api_health ADD COLUMN status_code INTEGER')
                    updates_made.append('api_health.status_code')
                
                if 'is_healthy' not in health_columns:
                    conn.execute('ALTER TABLE api_health ADD COLUMN is_healthy BOOLEAN DEFAULT TRUE')
                    updates_made.append('api_health.is_healthy')
            
            # Check contacts table
            if 'contacts' in inspector.get_table_names():
                contact_columns = [col['name'] for col in inspector.get_columns('contacts')]
                
                if 'is_resolved' not in contact_columns:
                    conn.execute('ALTER TABLE contacts ADD COLUMN is_resolved BOOLEAN DEFAULT FALSE')
                    updates_made.append('contacts.is_resolved')
            
            # Check beta_signups table
            if 'beta_signups' in inspector.get_table_names():
                beta_columns = [col['name'] for col in inspector.get_columns('beta_signups')]
                
                if 'is_approved' not in beta_columns:
                    conn.execute('ALTER TABLE beta_signups ADD COLUMN is_approved BOOLEAN DEFAULT FALSE')
                    updates_made.append('beta_signups.is_approved')
            
            conn.commit()
            
            if updates_made:
                logger.info(f"Added {len(updates_made)} missing columns: {', '.join(updates_made)}")
            else:
                logger.info("All columns already exist")
            
            return True
            
    except Exception as e:
        logger.error(f"Error adding missing columns: {str(e)}")
        return False

def migrate_database():
    """Run complete database migration"""
    try:
        logger.info("Starting database migration...")
        
        # Step 1: Create missing tables
        if not create_missing_tables():
            logger.error("Failed to create missing tables")
            return False
        
        # Step 2: Add missing columns
        if not add_missing_columns():
            logger.error("Failed to add missing columns")
            return False
        
        # Step 3: Create indexes if they don't exist
        try:
            with db.engine.connect() as conn:
                # Create indexes manually if they don't exist
                # PostgreSQL will ignore if they already exist
                index_commands = [
                    "CREATE INDEX IF NOT EXISTS idx_usage_user_time ON usage_logs(user_id, timestamp)",
                    "CREATE INDEX IF NOT EXISTS idx_usage_session_time ON usage_logs(session_id, timestamp)",
                    "CREATE INDEX IF NOT EXISTS idx_usage_type_time ON usage_logs(analysis_type, timestamp)",
                    "CREATE INDEX IF NOT EXISTS idx_api_health_time ON api_health(api_name, timestamp)"
                ]
                
                for cmd in index_commands:
                    try:
                        conn.execute(cmd)
                    except Exception as idx_error:
                        # Index might already exist
                        logger.debug(f"Index creation note: {str(idx_error)}")
                
                conn.commit()
                
        except Exception as idx_error:
            logger.warning(f"Index creation warning: {str(idx_error)}")
        
        logger.info("Database migration completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database migration error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def get_user_analytics(user_id, days=30):
    """Get analytics for a specific user"""
    try:
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
        
        # Get recent analyses
        recent_analyses = Analysis.query.filter(
            Analysis.user_id == user_id,
            Analysis.timestamp >= since_date
        ).order_by(Analysis.timestamp.desc()).limit(10).all()
        
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
            ],
            'recent_analyses': [a.to_dict() for a in recent_analyses]
        }
        
    except Exception as e:
        logger.error(f"Error getting user analytics: {str(e)}")
        return {'analyses_by_type': [], 'usage_by_date': [], 'recent_analyses': []}

def get_system_health():
    """Get overall system health metrics"""
    try:
        # Recent API health
        recent_health = db.session.query(
            APIHealth.api_name,
            db.func.avg(APIHealth.response_time).label('avg_response_time'),
            db.func.sum(db.case([(APIHealth.is_healthy == True, 1)], else_=0)).label('healthy_count'),
            db.func.count(APIHealth.id).label('total_count')
        ).filter(
            APIHealth.timestamp >= datetime.utcnow() - timedelta(hours=1)
        ).group_by(APIHealth.api_name).all()
        
        health_by_service = {}
        for api_name, avg_time, healthy_count, total_count in recent_health:
            health_by_service[api_name] = {
                'avg_response_time': float(avg_time or 0),
                'success_rate': (healthy_count / total_count * 100) if total_count > 0 else 0,
                'total_requests': total_count
            }
        
        # Usage statistics
        total_users = User.query.count()
        active_users = User.query.filter(
            User.last_login >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        total_analyses = Analysis.query.count()
        recent_analyses = Analysis.query.filter(
            Analysis.timestamp >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        return {
            'api_health': health_by_service,
            'users': {
                'total': total_users,
                'active_weekly': active_users
            },
            'analyses': {
                'total': total_analyses,
                'last_24h': recent_analyses
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting system health: {str(e)}")
        return {
            'api_health': {},
            'users': {'total': 0, 'active_weekly': 0},
            'analyses': {'total': 0, 'last_24h': 0},
            'timestamp': datetime.utcnow().isoformat()
        }

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
