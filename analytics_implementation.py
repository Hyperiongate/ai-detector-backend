# COMPLETE ANALYTICS IMPLEMENTATION FOR FACTS & FAKES AI
# Phase 1: Analytics Setup - Backend Implementation

import json
import time
import uuid
from datetime import datetime, timedelta
from functools import wraps
from flask import request, session, g, jsonify
from sqlalchemy import func, desc
import logging

# =============================================================================
# 1. DATABASE MODELS FOR ANALYTICS
# =============================================================================

class UserAnalytics(db.Model):
    """Comprehensive user analytics tracking"""
    __tablename__ = 'user_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    session_id = db.Column(db.String(100), nullable=False)
    
    # Page & Action Tracking
    page_visited = db.Column(db.String(200), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Request Details
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    referrer = db.Column(db.String(500))
    
    # Performance Metrics
    response_time_ms = db.Column(db.Float)
    status_code = db.Column(db.Integer)
    
    # Custom Metadata (JSON string)
    metadata = db.Column(db.Text)
    
    def __repr__(self):
        return f'<UserAnalytics {self.action_type} - {self.page_visited}>'

class ConversionTracking(db.Model):
    """Track conversion funnel progression"""
    __tablename__ = 'conversion_tracking'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    session_id = db.Column(db.String(100), nullable=False)
    
    # Funnel Steps
    funnel_step = db.Column(db.String(50), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Source Attribution
    traffic_source = db.Column(db.String(100))
    campaign = db.Column(db.String(100))
    
    # Conversion Metadata
    metadata = db.Column(db.Text)
    
    def __repr__(self):
        return f'<ConversionTracking {self.funnel_step} - Step {self.step_number}>'

class FeatureUsage(db.Model):
    """Track specific feature usage patterns"""
    __tablename__ = 'feature_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    session_id = db.Column(db.String(100), nullable=False)
    
    # Feature Details
    feature_name = db.Column(db.String(100), nullable=False)
    feature_category = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Usage Metrics
    success = db.Column(db.Boolean, default=True)
    processing_time_ms = db.Column(db.Float)
    input_size = db.Column(db.Integer)  # Text length, image size, etc.
    
    # User Tier & Limits
    user_tier = db.Column(db.String(20))
    usage_count_today = db.Column(db.Integer, default=0)
    limit_reached = db.Column(db.Boolean, default=False)
    
    # Results Metadata
    results = db.Column(db.Text)  # JSON string of analysis results
    
    def __repr__(self):
        return f'<FeatureUsage {self.feature_name} - {self.user_tier}>'

class PerformanceMetrics(db.Model):
    """System performance tracking"""
    __tablename__ = 'performance_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Response Time Tracking
    endpoint = db.Column(db.String(200), nullable=False)
    avg_response_time = db.Column(db.Float)
    max_response_time = db.Column(db.Float)
    min_response_time = db.Column(db.Float)
    
    # Request Counts
    total_requests = db.Column(db.Integer, default=0)
    error_count = db.Column(db.Integer, default=0)
    success_count = db.Column(db.Integer, default=0)
    
    # System Health
    cpu_usage = db.Column(db.Float)
    memory_usage = db.Column(db.Float)
    active_users = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<PerformanceMetrics {self.endpoint} - {self.timestamp}>'

# =============================================================================
# 2. ANALYTICS TRACKING FUNCTIONS
# =============================================================================

class AnalyticsTracker:
    """Central analytics tracking system"""
    
    def __init__(self):
        self.session_timeout = 30 * 60  # 30 minutes
        
    def get_or_create_session_id(self):
        """Get or create session ID for tracking"""
        if 'analytics_session_id' not in session:
            session['analytics_session_id'] = str(uuid.uuid4())
            session['session_start'] = datetime.utcnow().isoformat()
        return session['analytics_session_id']
    
    def track_page_visit(self, user_id=None, page=None, metadata=None):
        """Track page visits with full context"""
        try:
            session_id = self.get_or_create_session_id()
            
            analytics = UserAnalytics(
                user_id=user_id,
                session_id=session_id,
                page_visited=page or request.endpoint,
                action_type='page_visit',
                ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
                user_agent=request.headers.get('User-Agent'),
                referrer=request.referrer,
                metadata=json.dumps(metadata) if metadata else None
            )
            
            db.session.add(analytics)
            db.session.commit()
            
        except Exception as e:
            print(f"Analytics tracking error: {e}")
            # Don't let analytics errors break the app
            db.session.rollback()
    
    def track_user_action(self, action_type, user_id=None, page=None, metadata=None, 
                         response_time=None, status_code=200):
        """Track specific user actions"""
        try:
            session_id = self.get_or_create_session_id()
            
            analytics = UserAnalytics(
                user_id=user_id,
                session_id=session_id,
                page_visited=page or request.endpoint,
                action_type=action_type,
                ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
                user_agent=request.headers.get('User-Agent'),
                referrer=request.referrer,
                response_time_ms=response_time,
                status_code=status_code,
                metadata=json.dumps(metadata) if metadata else None
            )
            
            db.session.add(analytics)
            db.session.commit()
            
        except Exception as e:
            print(f"Action tracking error: {e}")
            db.session.rollback()
    
    def track_feature_usage(self, feature_name, user_id=None, success=True, 
                           processing_time=None, input_size=None, results=None):
        """Track feature usage with detailed metrics"""
        try:
            session_id = self.get_or_create_session_id()
            user_tier = session.get('user_tier', 'free')
            
            # Get today's usage count for this user/feature
            today = datetime.utcnow().date()
            usage_today = FeatureUsage.query.filter(
                FeatureUsage.user_id == user_id,
                FeatureUsage.feature_name == feature_name,
                func.date(FeatureUsage.timestamp) == today
            ).count()
            
            # Check if limit reached
            daily_limits = {'free': 5, 'pro': 50, 'enterprise': 1000}
            limit = daily_limits.get(user_tier, 5)
            limit_reached = usage_today >= limit
            
            feature_usage = FeatureUsage(
                user_id=user_id,
                session_id=session_id,
                feature_name=feature_name,
                feature_category=self._get_feature_category(feature_name),
                success=success,
                processing_time_ms=processing_time,
                input_size=input_size,
                user_tier=user_tier,
                usage_count_today=usage_today + 1,
                limit_reached=limit_reached,
                results=json.dumps(results) if results else None
            )
            
            db.session.add(feature_usage)
            db.session.commit()
            
            return {'usage_count': usage_today + 1, 'limit_reached': limit_reached}
            
        except Exception as e:
            print(f"Feature usage tracking error: {e}")
            db.session.rollback()
            return {'usage_count': 0, 'limit_reached': False}
    
    def track_conversion_step(self, step_name, user_id=None, traffic_source=None, 
                             campaign=None, metadata=None):
        """Track conversion funnel progression"""
        try:
            session_id = self.get_or_create_session_id()
            
            # Define funnel steps
            funnel_steps = [
                'homepage_visit', 'feature_demo', 'beta_modal_opened', 
                'email_entered', 'signup_submitted', 'signup_completed',
                'first_analysis', 'upgrade_prompt', 'payment_initiated', 'payment_completed'
            ]
            
            step_number = funnel_steps.index(step_name) + 1 if step_name in funnel_steps else 0
            
            conversion = ConversionTracking(
                user_id=user_id,
                session_id=session_id,
                funnel_step=step_name,
                step_number=step_number,
                traffic_source=traffic_source or session.get('traffic_source'),
                campaign=campaign or session.get('campaign'),
                metadata=json.dumps(metadata) if metadata else None
            )
            
            db.session.add(conversion)
            db.session.commit()
            
        except Exception as e:
            print(f"Conversion tracking error: {e}")
            db.session.rollback()
    
    def _get_feature_category(self, feature_name):
        """Categorize features for analytics"""
        categories = {
            'text_analysis': ['unified', 'news', 'plagiarism'],
            'image_analysis': ['imageanalysis', 'deepfake'],
            'admin': ['contact', 'pricing', 'mission'],
            'account': ['signup', 'login', 'profile']
        }
        
        for category, features in categories.items():
            if any(feature in feature_name.lower() for feature in features):
                return category
        return 'other'

# Initialize analytics tracker
analytics_tracker = AnalyticsTracker()

# =============================================================================
# 3. FLASK DECORATORS FOR AUTOMATIC TRACKING
# =============================================================================

def track_performance(f):
    """Decorator to track route performance automatically"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        try:
            # Execute the route function
            result = f(*args, **kwargs)
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Track the page visit and performance
            analytics_tracker.track_user_action(
                action_type='route_access',
                user_id=session.get('user_id'),
                response_time=response_time,
                status_code=200,
                metadata={
                    'endpoint': request.endpoint,
                    'method': request.method,
                    'performance_category': 'fast' if response_time < 1000 else 'slow'
                }
            )
            
            # Log slow requests
            if response_time > 2000:
                print(f"SLOW REQUEST: {request.endpoint} took {response_time:.2f}ms")
                analytics_tracker.track_user_action(
                    action_type='slow_request',
                    user_id=session.get('user_id'),
                    metadata={'response_time_ms': response_time, 'endpoint': request.endpoint}
                )
            
            return result
            
        except Exception as e:
            # Track errors
            response_time = (time.time() - start_time) * 1000
            analytics_tracker.track_user_action(
                action_type='error_occurred',
                user_id=session.get('user_id'),
                response_time=response_time,
                status_code=500,
                metadata={
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'endpoint': request.endpoint
                }
            )
            raise e
    
    return decorated_function

def track_feature_usage_decorator(feature_name, category=None):
    """Decorator to track feature usage automatically"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Execute the feature function
                result = f(*args, **kwargs)
                
                # Calculate processing time
                processing_time = (time.time() - start_time) * 1000
                
                # Get input size if available
                input_size = len(request.form.get('text', '')) if request.form.get('text') else 0
                
                # Track feature usage
                usage_stats = analytics_tracker.track_feature_usage(
                    feature_name=feature_name,
                    user_id=session.get('user_id'),
                    success=True,
                    processing_time=processing_time,
                    input_size=input_size,
                    results={'status': 'success', 'processing_time': processing_time}
                )
                
                # Add usage stats to response if it's a template render
                if hasattr(result, 'data') and 'usage_count' in usage_stats:
                    # For rendered templates, add usage info to context
                    pass
                
                return result
                
            except Exception as e:
                # Track failed feature usage
                processing_time = (time.time() - start_time) * 1000
                analytics_tracker.track_feature_usage(
                    feature_name=feature_name,
                    user_id=session.get('user_id'),
                    success=False,
                    processing_time=processing_time,
                    results={'status': 'error', 'error': str(e)}
                )
                raise e
        
        return decorated_function
    return decorator

# =============================================================================
# 4. ANALYTICS MIDDLEWARE
# =============================================================================

@app.before_request
def before_request_analytics():
    """Track every request automatically"""
    # Skip static files and admin endpoints
    if (request.endpoint and 
        not request.endpoint.startswith('static') and 
        not request.endpoint.startswith('admin')):
        
        # Set traffic source if not already set
        if 'traffic_source' not in session and request.referrer:
            if 'google' in request.referrer:
                session['traffic_source'] = 'google'
            elif 'facebook' in request.referrer:
                session['traffic_source'] = 'facebook'
            elif 'linkedin' in request.referrer:
                session['traffic_source'] = 'linkedin'
            elif 'twitter' in request.referrer:
                session['traffic_source'] = 'twitter'
            else:
                session['traffic_source'] = 'referral'
        elif 'traffic_source' not in session:
            session['traffic_source'] = 'direct'
        
        # Track page visit
        analytics_tracker.track_page_visit(
            user_id=session.get('user_id'),
            metadata={
                'traffic_source': session.get('traffic_source'),
                'user_agent': request.headers.get('User-Agent'),
                'is_mobile': 'Mobile' in request.headers.get('User-Agent', ''),
                'method': request.method
            }
        )

# =============================================================================
# 5. ANALYTICS API ENDPOINTS
# =============================================================================

@app.route('/api/analytics/track', methods=['POST'])
def track_custom_event():
    """API endpoint for custom event tracking from frontend"""
    try:
        data = request.get_json()
        
        analytics_tracker.track_user_action(
            action_type=data.get('event_type', 'custom_event'),
            user_id=session.get('user_id'),
            metadata=data.get('metadata', {})
        )
        
        return jsonify({'status': 'tracked', 'timestamp': datetime.utcnow().isoformat()})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/analytics/conversion', methods=['POST'])
def track_conversion():
    """API endpoint for conversion tracking from frontend"""
    try:
        data = request.get_json()
        
        analytics_tracker.track_conversion_step(
            step_name=data.get('step'),
            user_id=session.get('user_id'),
            metadata=data
        )
        
        return jsonify({'status': 'tracked', 'step': data.get('step')})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/admin/analytics/dashboard')
def analytics_dashboard():
    """Admin dashboard for analytics overview"""
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Get key metrics for last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Page views
        page_views = UserAnalytics.query.filter(
            UserAnalytics.timestamp >= thirty_days_ago,
            UserAnalytics.action_type == 'page_visit'
        ).count()
        
        # Unique users
        unique_users = db.session.query(UserAnalytics.session_id).filter(
            UserAnalytics.timestamp >= thirty_days_ago
        ).distinct().count()
        
        # Feature usage
        feature_usage = FeatureUsage.query.filter(
            FeatureUsage.timestamp >= thirty_days_ago
        ).count()
        
        # Conversion funnel
        conversion_steps = db.session.query(
            ConversionTracking.funnel_step,
            func.count(ConversionTracking.id).label('count')
        ).filter(
            ConversionTracking.timestamp >= thirty_days_ago
        ).group_by(ConversionTracking.funnel_step).all()
        
        # Top pages
        top_pages = db.session.query(
            UserAnalytics.page_visited,
            func.count(UserAnalytics.id).label('count')
        ).filter(
            UserAnalytics.timestamp >= thirty_days_ago,
            UserAnalytics.action_type == 'page_visit'
        ).group_by(UserAnalytics.page_visited).order_by(desc('count')).limit(10).all()
        
        return jsonify({
            'page_views': page_views,
            'unique_users': unique_users,
            'feature_usage': feature_usage,
            'conversion_funnel': [{'step': step, 'count': count} for step, count in conversion_steps],
            'top_pages': [{'page': page, 'views': count} for page, count in top_pages],
            'date_range': '30 days'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================================================
# 6. ROUTE UPDATES WITH ANALYTICS
# =============================================================================

# Update existing routes to include analytics tracking
@app.route('/')
@track_performance
def index():
    """Updated homepage with conversion tracking"""
    analytics_tracker.track_conversion_step('homepage_visit', session.get('user_id'))
    # Your existing index code here
    return render_template('index.html')

@app.route('/unified', methods=['GET', 'POST'])
@track_performance
@track_feature_usage_decorator('unified_analysis')
def unified_analysis():
    """Updated unified analysis with feature tracking"""
    if request.method == 'POST':
        analytics_tracker.track_conversion_step('feature_demo', session.get('user_id'))
    # Your existing unified analysis code here
    return render_template('unified.html')

@app.route('/beta-signup', methods=['POST'])
@track_performance
def beta_signup():
    """Updated beta signup with conversion tracking"""
    analytics_tracker.track_conversion_step('beta_modal_opened', session.get('user_id'))
    
    if request.form.get('email'):
        analytics_tracker.track_conversion_step('email_entered', session.get('user_id'))
        analytics_tracker.track_conversion_step('signup_submitted', session.get('user_id'))
        
        # Your existing signup code here
        
        analytics_tracker.track_conversion_step('signup_completed', session.get('user_id'))
    
    # Your existing beta signup code here
    return jsonify({'status': 'success'})

# =============================================================================
# 7. DATABASE INITIALIZATION
# =============================================================================

def initialize_analytics_tables():
    """Initialize analytics tables - run this once"""
    try:
        db.create_all()
        print("✅ Analytics tables created successfully")
        
        # Create sample data for testing (optional)
        # This would be removed in production
        sample_analytics = UserAnalytics(
            session_id='test_session',
            page_visited='index',
            action_type='page_visit',
            ip_address='127.0.0.1',
            user_agent='Test Agent'
        )
        db.session.add(sample_analytics)
        db.session.commit()
        print("✅ Sample analytics data created")
        
    except Exception as e:
        print(f"❌ Error creating analytics tables: {e}")
        db.session.rollback()

# =============================================================================
# 8. USAGE EXAMPLE
# =============================================================================

"""
IMPLEMENTATION INSTRUCTIONS:

1. Add to app.py initialization:
   ```python
   # Initialize analytics tables (run once)
   with app.app_context():
       initialize_analytics_tables()
   ```

2. Update existing routes:
   - Add @track_performance decorator to all routes
   - Add @track_feature_usage_decorator to analysis routes
   - Update beta signup flow with conversion tracking

3. Frontend JavaScript integration:
   ```javascript
   // Track custom events
   function trackEvent(eventType, metadata = {}) {
       fetch('/api/analytics/track', {
           method: 'POST',
           headers: {'Content-Type': 'application/json'},
           body: JSON.stringify({
               event_type: eventType,
               metadata: metadata
           })
       });
   }
   
   // Track conversion steps
   function trackConversion(step, metadata = {}) {
       fetch('/api/analytics/conversion', {
           method: 'POST',
           headers: {'Content-Type': 'application/json'},
           body: JSON.stringify({
               step: step,
               ...metadata
           })
       });
   }
   ```

4. Access analytics dashboard:
   - Visit /admin/analytics/dashboard (admin only)
   - View comprehensive metrics and conversion funnel
   - Monitor user behavior and performance

EXPECTED RESULTS:
- Complete user journey tracking
- Conversion funnel analysis
- Performance monitoring
- Feature usage insights
- Revenue attribution data
"""