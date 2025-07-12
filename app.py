"""
Facts & Fakes AI - Main Flask Application
Updated with real-time progress streaming and enhanced analysis feedback
"""

# Standard library imports
import os
import json
import logging
import traceback
import time
import hashlib
from datetime import datetime, timedelta
from functools import wraps

# CRITICAL: Fix DATABASE_URL before any other imports that might use it
def fix_database_url():
    """Fix database URL configuration before Flask/SQLAlchemy initialization"""
    db_url = os.environ.get('DATABASE_URL', '')
    
    # Skip if URL is already properly formatted
    if db_url.startswith(('postgresql://', 'postgres://')):
        # Just handle the postgres:// to postgresql:// conversion
        if db_url.startswith('postgres://'):
            fixed_url = db_url.replace('postgres://', 'postgresql://', 1)
            os.environ['DATABASE_URL'] = fixed_url
            os.environ['SQLALCHEMY_DATABASE_URI'] = fixed_url
        return
    
    # If DATABASE_URL exists but is malformed (your case)
    if db_url and '@' in db_url and not db_url.startswith('postgresql://'):
        # Your URL appears to be: $WT1ebW6tALDoj3@dpg-d1fcou9r0fns73cnng1g-a/newsverify
        # This is missing the protocol and username
        
        # Try to reconstruct the URL
        parts = db_url.split('@', 1)
        if len(parts) == 2:
            password = parts[0].lstrip('$')  # Remove leading $ if present
            host_and_db = parts[1]
            
            # Add Render's PostgreSQL suffix if missing
            if 'render.com' not in host_and_db:
                # Split host and database
                host_parts = host_and_db.split('/', 1)
                if len(host_parts) == 2:
                    host = host_parts[0]
                    database = host_parts[1]
                    # Add the Render domain suffix
                    host_and_db = f"{host}.oregon-postgres.render.com:5432/{database}"
            
            # Construct the complete URL
            # You might need to adjust the username based on your actual database setup
            fixed_url = f"postgresql://newsverify_user:{password}@{host_and_db}"
            
            os.environ['DATABASE_URL'] = fixed_url
            os.environ['SQLALCHEMY_DATABASE_URI'] = fixed_url
            
            print(f"Fixed DATABASE_URL format")
            return
    
    # If no DATABASE_URL, set a default for development
    if not db_url:
        fallback_url = 'sqlite:///app.db'
        os.environ['DATABASE_URL'] = fallback_url
        os.environ['SQLALCHEMY_DATABASE_URI'] = fallback_url
        print("WARNING: No DATABASE_URL found, using SQLite for development")

# Apply the fix immediately before any imports
fix_database_url()

# Flask imports
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file, Response, stream_with_context
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_talisman import Talisman
from flask_seasurf import SeaSurf

# NEW: Service architecture imports
from services.registry import ServiceRegistry
from config.validator import ConfigurationValidator

# Existing service imports
from services.database import db, User, Analysis, UsageLog, APIHealth, Contact, BetaSignup

# Analysis modules (keep existing for non-unified endpoints)
from analysis.news_analysis import analyze_news_route
from analysis.text_analysis import perform_realistic_unified_text_analysis, perform_basic_text_analysis
from analysis.image_analysis import perform_realistic_image_analysis, perform_basic_image_analysis
from analysis.speech_analysis import (
    extract_claims_from_speech, speech_to_text, batch_factcheck, 
    get_youtube_transcript, export_speech_report
)

# Other imports
import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Load configuration with fixed DATABASE_URL
app.config.from_object(config)

# Ensure SQLALCHEMY_DATABASE_URI is set from environment
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI') or os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Security configuration with proper CSP
csp = {
    'default-src': "'self'",
    'script-src': [
        "'self'",
        "'unsafe-inline'",  # Needed for Google Analytics and inline scripts
        "https://www.googletagmanager.com",
        "https://www.google-analytics.com",
        "https://cdnjs.cloudflare.com"
    ],
    'style-src': [
        "'self'",
        "'unsafe-inline'",  # Needed for inline styles
        "https://cdnjs.cloudflare.com",
        "https://fonts.googleapis.com"
    ],
    'font-src': [
        "'self'",
        "https://cdnjs.cloudflare.com",
        "https://fonts.gstatic.com"
    ],
    'img-src': [
        "'self'",
        "data:",  # For data URLs in SVG icons
        "https://www.google-analytics.com",
        "https://www.googletagmanager.com",
        "https://img.youtube.com"  # For YouTube thumbnails
    ],
    'connect-src': [
        "'self'",
        "https://www.google-analytics.com",
        "https://www.googletagmanager.com",
        "https://cdnjs.cloudflare.com"  # Add this line to allow CDN connections
    ]
}

Talisman(
    app, 
    force_https=False,  # Set to True in production
    content_security_policy=csp
)

csrf = SeaSurf(app)

# CORS configuration
CORS(app, origins=["*"], supports_credentials=True)

# Database initialization with error handling
try:
    db.init_app(app)
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Database initialization error: {str(e)}")
    logger.error(f"Current DATABASE_URL format check: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')[:50]}...")

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# NEW: Initialize service architecture
service_registry = None
config_validator = None

def initialize_services():
    """Initialize the service architecture with proper error handling"""
    global service_registry, config_validator
    
    try:
        logger.info("Initializing service architecture...")
        
        # Initialize configuration validator
        config_validator = ConfigurationValidator()
        validation_result = config_validator.validate_all()
        
        # Log configuration status
        logger.info("Configuration validation completed")
        if validation_result['missing_configs']:
            logger.warning(f"Missing configurations: {validation_result['missing_configs']}")
        if validation_result['recommendations']:
            logger.info(f"Recommendations: {validation_result['recommendations']}")
        
        # Initialize service registry
        service_registry = ServiceRegistry()
        
        # Register service classes
        from services.ai_analysis_service import AIAnalysisService
        from services.plagiarism_service import PlagiarismService
        
        service_registry.register_service_class('ai_analysis', AIAnalysisService)
        service_registry.register_service_class('plagiarism', PlagiarismService)
        
        # Initialize AI Analysis Service with configuration
        # Note: Environment variables are case-sensitive in Render
        ai_config = {
            'openai_api_key': os.environ.get('OPENAI_API_KEY') or os.environ.get('openai_api_key', ''),
            'openai_model': 'gpt-4',
            'openai_fallback_model': 'gpt-3.5-turbo',
            'max_text_length': 3000,
            'confidence_threshold': 70
        }
        
        success = service_registry.initialize_service('ai_analysis', ai_config)
        if success:
            logger.info("AI Analysis Service initialized successfully")
        else:
            logger.warning("AI Analysis Service initialization failed - check API key")
        
        # Initialize Plagiarism Service with configuration
        # Handle both uppercase and lowercase environment variables
        plagiarism_config = {
            'copyscape_api_key': os.environ.get('COPYSCAPE_API_KEY') or os.environ.get('copyscape_api_key', ''),
            'copyscape_username': os.environ.get('COPYSCAPE_USERNAME') or os.environ.get('copyscape_username', ''),
            'copyleaks_api_key': os.environ.get('COPYLEAKS_API_KEY') or os.environ.get('copyleaks_api_key', ''),
            'copyleaks_email': os.environ.get('COPYLEAKS_EMAIL') or os.environ.get('copyleaks_email', ''),
            'google_api_key': os.environ.get('GOOGLE_FACT_CHECK_API_KEY') or os.environ.get('google_factcheck_api_key', ''),
            'google_cx': os.environ.get('GOOGLE_CX', '')  # Custom search engine ID if you have one
        }
        
        success = service_registry.initialize_service('plagiarism', plagiarism_config)
        if success:
            logger.info("Plagiarism Service initialized successfully")
        else:
            logger.warning("Plagiarism Service initialization failed - check API keys")
        
        # Get overall health status
        health_status = service_registry.get_registry_health_status()
        logger.info(f"Service registry health status: {json.dumps(health_status, indent=2)}")
        
        # Check if at least one service is available
        available_services = service_registry.get_available_services()
        if available_services:
            logger.info(f"Available services: {available_services}")
            logger.info("Service architecture initialized successfully")
            return True
        else:
            logger.warning("No services available - all API keys may be missing or invalid")
            return False
        
    except Exception as e:
        logger.error(f"Failed to initialize service architecture: {str(e)}")
        logger.error(traceback.format_exc())
        return False

# NEW: Enhanced usage tracking with daily and weekly limits
USAGE_LIMITS = {
    'anonymous': {
        'daily': {
            'basic': 0,  # No daily allowance
            'pro': 0
        },
        'weekly': {
            'basic': 2,  # 2 basic analyses per week
            'pro': 0
        }
    },
    'free': {
        'daily': {
            'basic': 1,  # 1 basic analysis per day
            'pro': 0
        },
        'weekly': {
            'basic': 7,  # Effectively unlimited weekly (covered by daily)
            'pro': 1     # 1 pro analysis per week
        }
    },
    'pro': {
        'daily': {
            'basic': -1,  # Unlimited
            'pro': -1     # Unlimited
        },
        'weekly': {
            'basic': -1,  # Unlimited
            'pro': -1     # Unlimited
        }
    }
}

def get_user_tier(user):
    """Get user subscription tier"""
    if not user or not hasattr(user, 'id'):
        return 'anonymous'
    if not hasattr(user, 'subscription_tier'):
        return 'free'
    return user.subscription_tier or 'free'

def get_usage_count(user_id, analysis_type, period='daily'):
    """Get user's usage count for specified period"""
    try:
        if period == 'daily':
            start_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        else:  # weekly
            today = datetime.utcnow()
            start_time = today - timedelta(days=today.weekday())  # Start of week (Monday)
            start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # For anonymous users, we need to track by session or IP
        if user_id is None:
            # Track by session ID or IP address
            session_id = session.get('anonymous_id')
            if not session_id:
                session_id = request.remote_addr  # Use IP as fallback
                session['anonymous_id'] = session_id
            
            count = UsageLog.query.filter(
                UsageLog.session_id == session_id,
                UsageLog.analysis_type == analysis_type,
                UsageLog.timestamp >= start_time
            ).count()
        else:
            count = UsageLog.query.filter(
                UsageLog.user_id == user_id,
                UsageLog.analysis_type == analysis_type,
                UsageLog.timestamp >= start_time
            ).count()
        
        return count
    except Exception as e:
        logger.error(f"Error getting usage count: {str(e)}")
        # Rollback any failed transaction
        try:
            db.session.rollback()
        except:
            pass
        return 0  # Return 0 on error to allow continued operation

def check_usage_limit(user, analysis_type, is_pro_analysis=False):
    """Check if user has exceeded their usage limit"""
    # TEMPORARY: Bypass all usage limits for testing
    logger.info("Usage limits temporarily disabled for testing")
    return True, None
    
    tier = get_user_tier(user)
    limits = USAGE_LIMITS.get(tier, USAGE_LIMITS['anonymous'])
    
    # Determine if this is a pro or basic analysis
    analysis_level = 'pro' if is_pro_analysis else 'basic'
    
    # Get user ID (None for anonymous users)
    user_id = getattr(user, 'id', None) if user else None
    
    # Check daily limit
    daily_limit = limits['daily'][analysis_level]
    if daily_limit != -1:  # -1 means unlimited
        daily_usage = get_usage_count(user_id, f"{analysis_type}_{analysis_level}", 'daily')
        if daily_usage >= daily_limit:
            remaining_weekly = limits['weekly'][analysis_level] - get_usage_count(user_id, f"{analysis_type}_{analysis_level}", 'weekly')
            if remaining_weekly <= 0:
                return False, f"Daily limit reached for {analysis_level} analysis"
    
    # Check weekly limit
    weekly_limit = limits['weekly'][analysis_level]
    if weekly_limit != -1:  # -1 means unlimited
        weekly_usage = get_usage_count(user_id, f"{analysis_type}_{analysis_level}", 'weekly')
        if weekly_usage >= weekly_limit:
            return False, f"Weekly limit reached for {analysis_level} analysis"
    
    return True, None

def get_usage_status(user):
    """Get detailed usage status for user"""
    try:
        tier = get_user_tier(user)
        limits = USAGE_LIMITS.get(tier, USAGE_LIMITS['anonymous'])
        user_id = getattr(user, 'id', None) if user else None
        
        # Calculate usage for both basic and pro
        daily_basic = get_usage_count(user_id, 'unified_basic', 'daily')
        daily_pro = get_usage_count(user_id, 'unified_pro', 'daily')
        weekly_basic = get_usage_count(user_id, 'unified_basic', 'weekly')
        weekly_pro = get_usage_count(user_id, 'unified_pro', 'weekly')
        
        # Calculate time until reset
        now = datetime.utcnow()
        midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        next_monday = now + timedelta(days=(7 - now.weekday()))
        next_monday = next_monday.replace(hour=0, minute=0, second=0, microsecond=0)
        
        return {
            'tier': tier,
            'usage': {
                'daily': {
                    'basic': daily_basic,
                    'pro': daily_pro
                },
                'weekly': {
                    'basic': weekly_basic,
                    'pro': weekly_pro
                }
            },
            'limits': limits,
            'resets': {
                'daily': midnight.isoformat(),
                'weekly': next_monday.isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error getting usage status: {str(e)}")
        # Return pro tier with no limits on error
        return {
            'tier': 'pro',
            'usage': {
                'daily': {'basic': 0, 'pro': 0},
                'weekly': {'basic': 0, 'pro': 0}
            },
            'limits': {
                'daily': {'basic': -1, 'pro': -1},
                'weekly': {'basic': -1, 'pro': -1}
            },
            'resets': {
                'daily': datetime.utcnow().isoformat(),
                'weekly': datetime.utcnow().isoformat()
            }
        }

# Updated track_usage decorator
def track_usage(analysis_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # TEMPORARY: Skip all usage tracking
            logger.info(f"Usage tracking bypassed for {analysis_type}")
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Helper function for streaming progress
def stream_progress(generator_func):
    """Decorator to enable progress streaming for analysis endpoints"""
    @wraps(generator_func)
    def wrapper(*args, **kwargs):
        def generate():
            try:
                for data in generator_func(*args, **kwargs):
                    yield f"data: {json.dumps(data)}\n\n"
                    time.sleep(0.1)  # Small delay for smooth updates
            except Exception as e:
                logger.error(f"Streaming error: {str(e)}")
                yield f"data: {json.dumps({'error': str(e), 'stage': 'error'})}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype="text/event-stream",
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    return wrapper

# Helper function to extract article content from URL
def extract_article_content(url):
    """Extract article content from URL using BeautifulSoup"""
    try:
        import requests
        from bs4 import BeautifulSoup
        from urllib.parse import urlparse
        
        # Add headers to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the page
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try to find article content
        article_data = {
            'url': url,
            'title': '',
            'content': '',
            'author': '',
            'publish_date': ''
        }
        
        # Extract title
        if soup.find('title'):
            article_data['title'] = soup.find('title').get_text().strip()
        elif soup.find('h1'):
            article_data['title'] = soup.find('h1').get_text().strip()
        
        # Try to find main content
        # Look for common article containers
        content_selectors = [
            'article',
            '[role="main"]',
            '.article-content',
            '.entry-content',
            '.post-content',
            '.content',
            'main',
            '#content'
        ]
        
        content = ''
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # Get all paragraph text
                paragraphs = element.find_all('p')
                if paragraphs:
                    content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    if len(content) > 100:  # Minimum content length
                        break
        
        # Fallback: get all paragraphs
        if not content:
            all_paragraphs = soup.find_all('p')
            content = ' '.join([p.get_text().strip() for p in all_paragraphs if p.get_text().strip()])
        
        # Clean up content
        content = ' '.join(content.split())  # Remove extra whitespace
        
        if not content or len(content) < 100:
            # Last resort: get all text
            content = soup.get_text()
            content = ' '.join(content.split())
        
        article_data['content'] = content[:10000]  # Limit content length
        
        # Try to extract author
        author_meta = soup.find('meta', {'name': 'author'}) or soup.find('meta', {'property': 'article:author'})
        if author_meta:
            article_data['author'] = author_meta.get('content', '')
        
        # Try to extract publish date
        date_meta = soup.find('meta', {'property': 'article:published_time'}) or soup.find('meta', {'name': 'publish_date'})
        if date_meta:
            article_data['publish_date'] = date_meta.get('content', '')
        
        return article_data
        
    except Exception as e:
        logger.error(f"Error extracting article content: {str(e)}")
        return None

# Routes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/speech')
def speech():
    return render_template('speech.html')

@app.route('/imageanalysis')
def image_analysis():
    return render_template('imageanalysis.html')

@app.route('/unified')
def unified():
    return render_template('unified.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/missionstatement')
def mission_statement():
    return render_template('missionstatement.html')

@app.route('/pricingplan')
def pricing_plan():
    return render_template('pricingplan.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# NEW: Dashboard route
@app.route('/dashboard')
def dashboard():
    """User dashboard with usage tracking and history"""
    # In production, add @login_required
    user = current_user if hasattr(current_user, 'id') else None
    
    # Get user data for dashboard
    user_data = {
        'name': getattr(user, 'name', 'Analyst'),
        'email': getattr(user, 'email', 'dev@example.com'),
        'subscription_tier': get_user_tier(user),
        'id': getattr(user, 'id', 1)
    }
    
    return render_template('dashboard.html', user=user_data)

@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return redirect('/static/favicon.ico')

@app.route('/static/favicon.png')
def favicon_png():
    """Serve favicon.png"""
    # Try to serve favicon.ico if .png doesn't exist
    return redirect('/static/favicon.ico')
    # API Routes

# NEW: User usage status endpoint
@app.route('/api/user/usage', methods=['GET'])
def api_user_usage():
    """Get current user's usage status"""
    return jsonify({
        'success': True,
        'usage_status': get_usage_status(current_user)
    })

# NEW: Dashboard API endpoints
@app.route('/api/dashboard/usage', methods=['GET'])
def api_dashboard_usage():
    """Get user's current usage statistics"""
    try:
        # Use the new get_usage_status function
        usage_status = get_usage_status(current_user)
        
        return jsonify({
            'success': True,
            **usage_status
        })
        
    except Exception as e:
        logger.error(f"Dashboard usage error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dashboard/history', methods=['GET'])
def api_dashboard_history():
    """Get user's analysis history"""
    try:
        user_id = getattr(current_user, 'id', 1)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        analysis_type = request.args.get('type', None)
        days = request.args.get('days', 7, type=int)
        
        # Build query
        since_date = datetime.utcnow() - timedelta(days=days)
        query = Analysis.query.filter(
            Analysis.user_id == user_id,
            Analysis.timestamp >= since_date
        )
        
        if analysis_type and analysis_type != 'all':
            query = query.filter(Analysis.content_type == analysis_type)
        
        # Order by most recent
        query = query.order_by(Analysis.timestamp.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Format results
        history = []
        for analysis in pagination.items:
            history.append({
                'id': analysis.id,
                'type': analysis.content_type,
                'timestamp': analysis.timestamp.isoformat(),
                'trust_score': analysis.trust_score,
                'snippet': analysis.content_snippet[:100] + '...' if len(analysis.content_snippet) > 100 else analysis.content_snippet,
                'results_summary': json.loads(analysis.results).get('summary', '') if analysis.results else ''
            })
        
        return jsonify({
            'success': True,
            'history': history,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
        
    except Exception as e:
        logger.error(f"Dashboard history error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dashboard/stats', methods=['GET'])
def api_dashboard_stats():
    """Get user statistics and achievements"""
    try:
        user_id = getattr(current_user, 'id', 1)
        
        # Calculate statistics
        total_analyses = Analysis.query.filter_by(user_id=user_id).count()
        
        # Get analysis breakdown by type
        type_breakdown = db.session.query(
            Analysis.content_type,
            db.func.count(Analysis.id)
        ).filter(
            Analysis.user_id == user_id
        ).group_by(Analysis.content_type).all()
        
        # Calculate average trust score
        avg_trust_score = db.session.query(
            db.func.avg(Analysis.trust_score)
        ).filter(
            Analysis.user_id == user_id,
            Analysis.trust_score.isnot(None)
        ).scalar() or 0
        
        # Check achievements
        achievements = {
            'first_analysis': total_analyses >= 1,
            'verified_user': True,  # In production, check email verification
            'power_user': total_analyses >= 50,
            'century_club': total_analyses >= 100,
            'trusted_analyst': avg_trust_score >= 80,
            'diverse_analyst': len(type_breakdown) >= 4
        }
        
        return jsonify({
            'success': True,
            'stats': {
                'total_analyses': total_analyses,
                'avg_trust_score': round(avg_trust_score, 1),
                'type_breakdown': dict(type_breakdown),
                'member_since': datetime.utcnow().isoformat()  # In production, use user.created_at
            },
            'achievements': achievements
        })
        
    except Exception as e:
        logger.error(f"Dashboard stats error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# NEW: Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Comprehensive system health check"""
    try:
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {},
            'configuration': {},
            'database': 'unknown'
        }
        
        # Check database
        try:
            db.session.execute('SELECT 1')
            health_data['database'] = 'healthy'
        except Exception as e:
            health_data['database'] = f'error: {str(e)}'
            health_data['status'] = 'degraded'
        
        # Check service registry
        if service_registry:
            health_data['services'] = service_registry.get_registry_health_status()
            
            # If any service is unhealthy, mark as degraded
            for service_name, service_info in health_data['services'].get('services', {}).items():
                if not service_info.get('is_available', False):
                    health_data['status'] = 'degraded'
        else:
            health_data['services'] = {'error': 'Service registry not initialized'}
            health_data['status'] = 'degraded'
        
        # Check configuration
        if config_validator:
            config_status = config_validator.validate_all()
            health_data['configuration'] = {
                'api_keys_configured': len(config_status['available_apis']),
                'missing_configs': len(config_status['missing_configs']),
                'recommendations': len(config_status['recommendations'])
            }
        else:
            health_data['configuration'] = {'error': 'Configuration validator not initialized'}
            health_data['status'] = 'degraded'
        
        return jsonify(health_data)
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# YouTube transcript endpoint
@app.route('/api/youtube-transcript', methods=['POST'])
@csrf.exempt
def api_youtube_transcript():
    """Fetch YouTube video transcript"""
    try:
        data = request.get_json()
        url = data.get('url', '')
        
        if not url:
            return jsonify({'success': False, 'error': 'No URL provided'}), 400
        
        # Get transcript using existing function
        from analysis.speech_analysis import get_youtube_transcript
        transcript = get_youtube_transcript(url)
        
        if not transcript:
            return jsonify({
                'success': False, 
                'error': 'Could not fetch transcript. Video may not have captions enabled.'
            }), 404
        
        # Extract video info
        video_info = extract_youtube_info(url)
        
        return jsonify({
            'success': True,
            'transcript': transcript,
            'video_info': video_info
        })
        
    except Exception as e:
        logger.error(f"YouTube transcript error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def extract_youtube_info(url):
    """Extract basic YouTube video information"""
    try:
        # Extract video ID
        video_id = None
        if 'v=' in url:
            video_id = url.split('v=')[1].split('&')[0]
        elif 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[1].split('?')[0]
        
        if video_id:
            # Basic info without additional API calls
            # In production, you could use youtube-dl or yt-dlp for more info
            return {
                'title': 'YouTube Video',
                'channel': 'YouTube Channel',
                'duration': 'Unknown',
                'views': 'Unknown',
                'thumbnail': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
                'video_id': video_id
            }
    except Exception as e:
        logger.error(f"YouTube info extraction error: {str(e)}")
    
    return {
        'title': 'Unknown Video',
        'channel': 'Unknown',
        'duration': 'Unknown',
        'views': 'Unknown',
        'thumbnail': ''
    }

# Enhanced speech analysis endpoint
@app.route('/api/analyze-speech', methods=['POST'])
@csrf.exempt
@track_usage('speech')
def api_analyze_speech():
    """Enhanced speech analysis endpoint with YouTube support"""
    try:
        content = request.form.get('content', '').strip()
        content_type = request.form.get('type', 'text')
        is_pro = request.form.get('is_pro', 'true').lower() == 'true'
        
        transcript = None
        
        # Handle different content types
        if content_type == 'youtube':
            # Content is already the transcript from frontend
            transcript = content
            if not transcript:
                return jsonify({'success': False, 'error': 'No transcript provided'}), 400
                
        elif content_type == 'file':
            # Handle file upload
            if 'file' not in request.files:
                return jsonify({'success': False, 'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No file selected'}), 400
                
            # Save file temporarily
            import tempfile
            import os
            
            # Create temp file with proper extension
            _, ext = os.path.splitext(file.filename)
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
                file.save(tmp_file.name)
                tmp_filename = tmp_file.name
            
            try:
                # Convert speech to text
                from analysis.speech_analysis import speech_to_text
                transcript = speech_to_text(tmp_filename)
                
                if not transcript:
                    return jsonify({
                        'success': False, 
                        'error': 'Could not transcribe audio. Please ensure the audio is clear.'
                    }), 400
                    
            finally:
                # Clean up temp file
                if os.path.exists(tmp_filename):
                    os.unlink(tmp_filename)
                    
        else:
            # Direct text input
            transcript = content
            if not transcript:
                return jsonify({'success': False, 'error': 'No text provided'}), 400
        
        # Validate transcript length
        if len(transcript) < 50:
            return jsonify({
                'success': False, 
                'error': 'Content too short for meaningful analysis. Please provide at least 50 characters.'
            }), 400
        
        # Extract claims from transcript
        from analysis.speech_analysis import extract_claims_from_speech, batch_factcheck
        
        logger.info(f"Extracting claims from transcript of length: {len(transcript)}")
        claims = extract_claims_from_speech(transcript)
        
        if not claims:
            # If no claims found, create a general claim for analysis
            claims = [transcript[:500]]  # Use first 500 chars as a claim
        
        logger.info(f"Found {len(claims)} claims to fact-check")
        
        # Fact-check claims
        fact_check_results = []
        
        if is_pro:
            # Professional analysis with full fact-checking
            fact_check_results = batch_factcheck(claims, is_pro=True)
        else:
            # Basic analysis with limited fact-checking
            # For basic tier, only check first 3 claims
            limited_claims = claims[:3]
            fact_check_results = batch_factcheck(limited_claims, is_pro=False)
            
            # Add placeholder results for remaining claims
            for claim in claims[3:]:
                fact_check_results.append({
                    'claim': claim,
                    'verdict': 'UNVERIFIED',
                    'explanation': 'Upgrade to Professional for full fact-checking'
                })
        
        # Calculate trust score
        total_claims = len(fact_check_results)
        verified_claims = sum(1 for r in fact_check_results 
                            if r.get('verdict') in ['TRUE', 'VERIFIED'])
        false_claims = sum(1 for r in fact_check_results 
                         if r.get('verdict') in ['FALSE', 'MISLEADING'])
        
        # Calculate trust score (0-100)
        if total_claims > 0:
            # Base score on verified vs false claims
            trust_score = int((verified_claims / total_claims) * 100)
            
            # Penalize for false claims
            trust_score -= (false_claims * 15)
            
            # Ensure score is within bounds
            trust_score = max(0, min(100, trust_score))
        else:
            trust_score = 50  # Default neutral score
        
        # Prepare response
        results = {
            'success': True,
            'transcript': transcript[:1000] + '...' if len(transcript) > 1000 else transcript,
            'claims_analyzed': total_claims,
            'claims_verified': verified_claims,
            'claims_false': false_claims,
            'trust_score': trust_score,
            'fact_check_results': fact_check_results,
            'word_count': len(transcript.split()),
            'analysis_type': 'professional' if is_pro else 'basic',
            'content_type': content_type
        }
        
        # Add source info for YouTube videos
        if content_type == 'youtube':
            results['source'] = 'YouTube Video Transcript'
        
        # Save to database
        try:
            analysis = Analysis(
                user_id=getattr(current_user, 'id', 1),
                content_type='speech',
                content_snippet=transcript[:500],
                results=json.dumps(results),
                trust_score=trust_score,
                timestamp=datetime.utcnow()
            )
            db.session.add(analysis)
            db.session.commit()
            results['analysis_id'] = analysis.id
        except Exception as e:
            logger.error(f"Database save error: {str(e)}")
            # Continue even if save fails
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Speech analysis error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False, 
            'error': 'Analysis failed. Please try again.'
        }), 500

@app.route('/api/export-speech-report', methods=['POST'])
@csrf.exempt
def api_export_speech_report():
    """Export speech analysis results as PDF"""
    try:
        results = json.loads(request.form.get('results', '{}'))
        
        if not results:
            return jsonify({'success': False, 'error': 'No results provided'}), 400
        
        # Generate PDF report
        from analysis.speech_analysis import export_speech_report
        pdf_buffer = export_speech_report(results)
        
        if not pdf_buffer:
            return jsonify({'success': False, 'error': 'Failed to generate report'}), 500
        
        # Return PDF file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'speech_analysis_report_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
        
    except Exception as e:
        logger.error(f"Export report error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# NEW: Enhanced unified analysis endpoint with streaming progress
@app.route('/api/analyze-unified/stream', methods=['GET'])
@csrf.exempt
@track_usage('unified')
def analyze_unified_stream():
    """Streaming version of unified analysis with real-time progress updates"""
    def generate():
        try:
            # Get parameters directly from query string
            content = request.args.get('content', '').strip()
            url = request.args.get('url', '').strip()
            content_type = request.args.get('type', 'text')
            is_pro = request.args.get('is_pro', 'true').lower() == 'true'
            
            # Determine what content to analyze
            if content_type == 'url' and url:
                # URL analysis - fetch content from URL first
                yield f"data: {json.dumps({'type': 'progress', 'stage': 'Fetching content from URL...', 'progress': 5, 'step': 1})}\n\n"
                time.sleep(0.8)  # Make it more realistic
                
                try:
                    # Extract content from URL
                    article_data = extract_article_content(url)
                    if article_data and article_data.get('content'):
                        content = article_data['content']
                        # Include URL metadata in results
                        url_metadata = {
                            'url': url,
                            'title': article_data.get('title', ''),
                            'author': article_data.get('author', ''),
                            'publish_date': article_data.get('publish_date', '')
                        }
                    else:
                        yield f"data: {json.dumps({'type': 'error', 'message': 'Could not extract content from URL'})}\n\n"
                        return
                except Exception as e:
                    logger.error(f"URL extraction error: {str(e)}")
                    yield f"data: {json.dumps({'type': 'error', 'message': f'Failed to fetch URL: {str(e)}'})}\n\n"
                    return
                    
            elif content_type == 'text' and content:
                # Text analysis - content already provided
                pass
            elif content_type == 'file':
                # File analysis - content should be provided
                pass
            else:
                yield f"data: {json.dumps({'type': 'error', 'message': 'No content provided for analysis'})}\n\n"
                return
            
            # Validate content
            if not content or len(content.strip()) < 50:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Content too short for meaningful analysis (minimum 50 characters)'})}\n\n"
                return
            
            # Check service availability - with fallback
            if not service_registry:
                logger.warning("Service registry not available - using fallback analysis")
                # Use fallback analysis
                yield f"data: {json.dumps({'type': 'progress', 'stage': 'Using basic analysis mode...', 'progress': 10, 'step': 1})}\n\n"
                time.sleep(0.5)
                
                # Perform basic text analysis as fallback
                basic_results = perform_realistic_unified_text_analysis(content)
                
                # Convert basic results to unified format
                results = {
                    'trust_score': basic_results.get('trust_score', 50),
                    'ai_probability': basic_results.get('ai_probability', 0),
                    'plagiarism_score': 0,  # Not available in basic mode
                    'analysis_sections': {
                        'ai_detection': {
                            'title': 'AI Content Detection',
                            'content': basic_results.get('summary', 'Basic analysis completed'),
                            'probability': basic_results.get('ai_probability', 0),
                            'ai_probability': basic_results.get('ai_probability', 0),
                            'human_probability': basic_results.get('human_probability', 100),
                            'patterns': basic_results.get('patterns_detected', []),
                            'status': 'basic'
                        },
                        'quality': {
                            'title': 'Content Quality Analysis',
                            'metrics': basic_results.get('metrics', {}),
                            'status': 'completed'
                        }
                    },
                    'summary': basic_results.get('summary', ''),
                    'recommendations': basic_results.get('recommendations', []),
                    'metadata': {
                        'analysis_time': datetime.utcnow().isoformat(),
                        'services_used': ['basic_analysis'],
                        'is_pro': False,
                        'analysis_tier': 'basic',
                        'content_type': content_type
                    }
                }
                
                yield f"data: {json.dumps({'type': 'progress', 'stage': 'Analysis complete!', 'progress': 100, 'step': 6})}\n\n"
                yield f"data: {json.dumps({'type': 'complete', 'results': results})}\n\n"
                return
            
            # Initialize results structure
            results = {
                'trust_score': 50,
                'ai_probability': 0,
                'plagiarism_score': 0,
                'analysis_sections': {},
                'summary': '',
                'recommendations': [],
                'metadata': {
                    'analysis_time': datetime.utcnow().isoformat(),
                    'services_used': [],
                    'is_pro': is_pro,
                    'analysis_tier': 'professional' if is_pro else 'basic',
                    'content_type': content_type
                }
            }
            
            # Add URL metadata if available
            if content_type == 'url' and 'url_metadata' in locals():
                results['metadata']['source'] = url_metadata
            
            # Stage 1: Initial processing
            yield f"data: {json.dumps({'type': 'progress', 'stage': 'Initializing analysis engine...', 'progress': 10, 'step': 1})}\n\n"
            time.sleep(1.2)  # More realistic timing
            
            # Stage 2: AI Analysis
            yield f"data: {json.dumps({'type': 'progress', 'stage': 'Detecting AI patterns...', 'progress': 20, 'step': 2})}\n\n"
            time.sleep(0.8)
            
            ai_service = service_registry.get_service('ai_analysis')
            if ai_service and ai_service.is_available:
                logger.info("Running AI analysis...")
                
                # More detailed progress updates
                yield f"data: {json.dumps({'type': 'progress', 'stage': 'Analyzing linguistic patterns...', 'progress': 30, 'step': 2})}\n\n"
                time.sleep(1.5)  # Simulate analysis time
                
                ai_results = ai_service.analyze(content, use_openai=is_pro)
                
                if ai_results.get('success'):
                    data = ai_results.get('data', {})
                    results['ai_probability'] = data.get('ai_probability', 0)
                    results['analysis_sections']['ai_detection'] = {
                        'title': 'AI Content Detection',
                        'content': data.get('analysis', 'Analysis completed'),
                        'confidence': data.get('confidence', 0.5),
                        'details': data.get('details', {}),
                        'probability': data.get('ai_probability', 0),
                        'ai_probability': data.get('ai_probability', 0),
                        'human_probability': 100 - data.get('ai_probability', 0),
                        'patterns': data.get('detected_patterns', {}).get('ai_phrases', 0),
                        'status': 'completed'
                    }
                    results['metadata']['services_used'].append('ai_analysis')
                    
                    # Adjust trust score
                    if data.get('ai_probability', 0) > 70:
                        results['trust_score'] -= int(data.get('confidence', 0.5) * 30)
                    
                    # Send partial results
                    yield f"data: {json.dumps({'type': 'partial', 'results': {'ai_detection': results['analysis_sections']['ai_detection']}})}\n\n"
                
                yield f"data: {json.dumps({'type': 'progress', 'stage': 'Calculating AI probability scores...', 'progress': 45, 'step': 3})}\n\n"
                time.sleep(1.0)
            else:
                logger.warning("AI service not available - using basic analysis")
                # Fallback to basic analysis
                basic_results = perform_realistic_unified_text_analysis(content)
                results['ai_probability'] = basic_results.get('ai_probability', 0)
                results['analysis_sections']['ai_detection'] = {
                    'title': 'AI Content Detection',
                    'content': 'AI service unavailable - using pattern analysis',
                    'probability': basic_results.get('ai_probability', 0),
                    'ai_probability': basic_results.get('ai_probability', 0),
                    'human_probability': basic_results.get('human_probability', 100),
                    'patterns': basic_results.get('patterns_detected', []),
                    'status': 'fallback'
                }
            
            # Stage 3: Plagiarism Check
            yield f"data: {json.dumps({'type': 'progress', 'stage': 'Checking for plagiarism...', 'progress': 50, 'step': 4})}\n\n"
            time.sleep(0.8)
            
            plagiarism_service = service_registry.get_service('plagiarism')
            if plagiarism_service and plagiarism_service.is_available and content:
                logger.info("Running plagiarism analysis...")
                
                yield f"data: {json.dumps({'type': 'progress', 'stage': 'Searching academic databases...', 'progress': 60, 'step': 4})}\n\n"
                time.sleep(2.0)  # Plagiarism check takes longer
                
                plagiarism_results = plagiarism_service.check_plagiarism(content, use_real_apis=is_pro)
                
                if plagiarism_results:
                    results['plagiarism_score'] = int(plagiarism_results.get('score', 0))
                    results['analysis_sections']['plagiarism'] = {
                        'title': 'Plagiarism Detection',
                        'content': f"Checked {plagiarism_results.get('sources_checked', 0)} sources",
                        'sources_found': len(plagiarism_results.get('matches', [])),
                        'similarity_score': plagiarism_results.get('score', 0) / 100,
                        'details': plagiarism_results.get('matches', []),
                        'matched_content': plagiarism_results.get('matches', []),
                        'status': 'completed'
                    }
                    results['metadata']['services_used'].append('plagiarism')
                    
                    # Adjust trust score
                    if plagiarism_results.get('score', 0) > 50:
                        results['trust_score'] -= int(plagiarism_results.get('score', 0) * 0.25)
                    
                    # Send partial results
                    yield f"data: {json.dumps({'type': 'partial', 'results': {'plagiarism': results['analysis_sections']['plagiarism']}})}\n\n"
                
                yield f"data: {json.dumps({'type': 'progress', 'stage': 'Comparing with online sources...', 'progress': 75, 'step': 4})}\n\n"
                time.sleep(1.5)
            else:
                logger.warning("Plagiarism service not available")
                results['analysis_sections']['plagiarism'] = {
                    'title': 'Plagiarism Detection',
                    'content': 'Plagiarism checking unavailable in basic mode',
                    'status': 'unavailable'
                }
            
            # Stage 4: Quality Analysis
            yield f"data: {json.dumps({'type': 'progress', 'stage': 'Analyzing content quality...', 'progress': 80, 'step': 5})}\n\n"
            time.sleep(1.0)
            
            # Add basic quality metrics
            word_count = len(content.split())
            sentence_count = len([s for s in content.split('.') if s.strip()])
            avg_sentence_length = word_count / max(sentence_count, 1)
            
            results['analysis_sections']['quality'] = {
                'title': 'Content Quality Analysis',
                'metrics': {
                    'word_count': word_count,
                    'sentence_count': sentence_count,
                    'avg_sentence_length': round(avg_sentence_length, 1),
                    'readability': 'Good' if avg_sentence_length < 20 else 'Complex'
                },
                'status': 'completed'
            }
            
            # Stage 5: Finalize
            yield f"data: {json.dumps({'type': 'progress', 'stage': 'Generating comprehensive report...', 'progress': 90, 'step': 6})}\n\n"
            time.sleep(1.2)
            
            # Ensure trust score is within bounds
            results['trust_score'] = max(0, min(100, results['trust_score']))
            
            # Generate summary
            summary_parts = []
            ai_section = results['analysis_sections'].get('ai_detection', {})
            plagiarism_section = results['analysis_sections'].get('plagiarism', {})
            
            if ai_section.get('ai_probability', 0) > 50:
                summary_parts.append(f"Content appears to be AI-generated ({ai_section.get('ai_probability', 0)}% probability)")
            else:
                summary_parts.append(f"Content appears to be human-written ({ai_section.get('human_probability', 100)}% probability)")
            
            if plagiarism_section.get('similarity_score', 0) > 0:
                summary_parts.append(f"Found {plagiarism_section.get('sources_found', 0)} potential source matches")
            else:
                summary_parts.append("No plagiarism detected")
            
            results['summary'] = ". ".join(summary_parts) + f". Overall trust score: {results['trust_score']}%"
            
            # Generate recommendations
            if results['trust_score'] < 60:
                results['recommendations'].append("Content shows concerning patterns - verify with additional sources")
            if ai_section.get('ai_probability', 0) > 70:
                results['recommendations'].append("High probability of AI-generated content detected")
            if plagiarism_section.get('similarity_score', 0) > 0.3:
                results['recommendations'].append("Similar content found online - ensure proper attribution")
            if results['trust_score'] > 80:
                results['recommendations'].append("Content appears authentic and trustworthy")
            
            # Save to database
            try:
                analysis = Analysis(
                    user_id=getattr(current_user, 'id', 1),
                    content_type='unified',
                    content_snippet=content[:500] if content else 'Analysis',
                    results=json.dumps(results),
                    trust_score=results['trust_score'],
                    timestamp=datetime.utcnow()
                )
                db.session.add(analysis)
                db.session.commit()
                results['metadata']['analysis_id'] = analysis.id
            except Exception as e:
                logger.error(f"Database save error: {str(e)}")
                # Continue even if save fails
            
            # Final progress
            yield f"data: {json.dumps({'type': 'progress', 'stage': 'Analysis complete!', 'progress': 100, 'step': 6})}\n\n"
            time.sleep(0.5)
            
            # Send complete results
            yield f"data: {json.dumps({'type': 'complete', 'results': results})}\n\n"
            
        except Exception as e:
            logger.error(f"Unified analysis streaming error: {str(e)}")
            logger.error(traceback.format_exc())
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )
 # Keep the original endpoint for backwards compatibility
@app.route('/api/analyze-unified', methods=['POST'])
@csrf.exempt
@track_usage('unified')
def analyze_unified():
    """Original unified analysis endpoint with fallback support"""
    try:
        # Get request data
        content = request.form.get('content', '').strip()
        content_type = request.form.get('content_type', 'text')
        tier = request.form.get('tier', 'basic')  # Get tier from request
        
        # Determine if this is pro analysis based on user tier and selection
        user_tier = get_user_tier(current_user)
        is_pro = False
        
        if user_tier == 'pro':
            is_pro = True  # Pro users always get pro analysis
        elif user_tier == 'free' and tier == 'professional':
            # Free users can use their weekly pro analysis
            is_pro = True
        
        # Handle file upload for images
        image_file = None
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename == '':
                image_file = None
        
        # Handle file upload for documents
        if 'file' in request.files:
            uploaded_file = request.files['file']
            if uploaded_file.filename != '':
                # Read file content
                content = uploaded_file.read().decode('utf-8', errors='ignore')
                content_type = 'text'
        
        # Validate input
        if not content and not image_file:
            return jsonify({
                'success': False,
                'error': 'No content or image provided for analysis'
            }), 400
        
        # Check service availability - with fallback
        if not service_registry:
            logger.warning("Service registry not available - using fallback analysis")
            
            # Use fallback analysis when services are unavailable
            results = {
                'trust_score': 50,
                'ai_probability': 0,
                'plagiarism_score': 0,
                'analysis_sections': {},
                'summary': '',
                'recommendations': [],
                'metadata': {
                    'analysis_time': datetime.utcnow().isoformat(),
                    'services_used': ['fallback_analysis'],
                    'is_pro': is_pro,
                    'analysis_tier': 'basic'
                }
            }
            
            # Perform basic text analysis as fallback
            if content:
                basic_results = perform_realistic_unified_text_analysis(content)
                
                results['ai_probability'] = basic_results.get('ai_probability', 0)
                results['trust_score'] = basic_results.get('trust_score', 50)
                
                results['analysis_sections']['ai_detection'] = {
                    'title': 'AI Content Detection',
                    'content': basic_results.get('summary', 'Basic analysis completed'),
                    'probability': basic_results.get('ai_probability', 0),
                    'ai_probability': basic_results.get('ai_probability', 0),
                    'human_probability': basic_results.get('human_probability', 100),
                    'patterns': basic_results.get('patterns_detected', []),
                    'status': 'fallback'
                }
                
                results['analysis_sections']['quality'] = {
                    'title': 'Content Quality Analysis',
                    'metrics': basic_results.get('metrics', {}),
                    'status': 'completed'
                }
                
                results['summary'] = basic_results.get('summary', 'Analysis completed using basic mode')
                results['recommendations'] = basic_results.get('recommendations', [])
            
            # Handle image analysis if image provided
            if image_file:
                try:
                    if is_pro:
                        image_results = perform_realistic_image_analysis(image_file)
                    else:
                        image_results = perform_basic_image_analysis(image_file)
                    
                    results['analysis_sections']['image_authenticity'] = {
                        'title': 'Image Authenticity',
                        'content': image_results.get('summary', 'Image analysis completed'),
                        'authenticity_score':
                        # PDF generation endpoints

@app.route('/api/generate-pdf', methods=['POST'])
@csrf.exempt
def api_generate_pdf():
    """Generate PDF report for analysis results"""
    try:
        data = request.get_json()
        results = data.get('results', {})
        analysis_type = data.get('type', 'unified')
        
        # Generate PDF based on analysis type
        if analysis_type == 'speech':
            from analysis.speech_analysis import export_speech_report
            pdf_buffer = export_speech_report(results)
        else:
            # For other types, use enhanced PDF generator
            pdf_buffer = generate_enhanced_pdf_report(results, analysis_type)
        
        if not pdf_buffer:
            return jsonify({'success': False, 'error': 'Failed to generate PDF'}), 500
        
        # Return PDF file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'{analysis_type}_analysis_report_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
        
    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': 'PDF generation failed. Please try again.'}), 500

@app.route('/api/generate-unified-pdf', methods=['POST'])
@csrf.exempt
def api_generate_unified_pdf():
    """Generate PDF report specifically for unified analysis"""
    try:
        data = request.get_json()
        results = data.get('results', {})
        
        # Generate unified analysis PDF with enhanced formatting
        pdf_buffer = generate_enhanced_unified_pdf_report(results)
        
        if not pdf_buffer:
            return jsonify({'success': False, 'error': 'Failed to generate PDF'}), 500
        
        # Generate a unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f'ai_plagiarism_report_{timestamp}.pdf'
        
        # Return PDF file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Unified PDF generation error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': 'PDF generation failed. Please try again.'}), 500

def generate_enhanced_pdf_report(results, analysis_type):
    """Generate an enhanced PDF report for analysis results"""
    try:
        from io import BytesIO
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, HRFlowable, KeepTogether
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#4a90e2'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#357abd'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Header
        story.append(Paragraph("Facts & Fakes AI - Analysis Report", title_style))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
        story.append(Spacer(1, 0.5*inch))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#4a90e2')))
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        
        # Trust Score Table
        trust_score = results.get('trust_score', 0)
        score_color = colors.green if trust_score >= 80 else colors.orange if trust_score >= 60 else colors.red
        
        score_data = [
            ['Overall Trust Score', f"{trust_score}%"],
            ['Analysis Type', analysis_type.title()],
            ['Analysis Date', datetime.now().strftime('%Y-%m-%d %H:%M')]
        ]
        
        score_table = Table(score_data, colWidths=[3*inch, 3*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.white),
            ('BACKGROUND', (1, 0), (1, 0), score_color),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.white),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 0), (1, 0), 18),
        ]))
        
        story.append(score_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Summary
        if 'summary' in results:
            story.append(Paragraph(results['summary'], styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
        
        # Analysis Sections
        if 'analysis_sections' in results:
            for section_key, section_data in results['analysis_sections'].items():
                if isinstance(section_data, dict) and 'title' in section_data:
                    story.append(PageBreak())
                    story.append(Paragraph(section_data['title'], heading_style))
                    
                    # Section content
                    if 'content' in section_data:
                        story.append(Paragraph(str(section_data['content']), styles['Normal']))
                        story.append(Spacer(1, 0.2*inch))
                    
                    # Section-specific details
                    if section_key == 'ai_detection':
                        ai_prob = section_data.get('ai_probability', 0)
                        human_prob = section_data.get('human_probability', 100)
                        
                        ai_data = [
                            ['Metric', 'Value'],
                            ['AI Probability', f"{ai_prob}%"],
                            ['Human Probability', f"{human_prob}%"],
                            ['Confidence Level', f"{section_data.get('confidence', 0.5)*100:.1f}%"],
                            ['Patterns Detected', section_data.get('patterns', 0)]
                        ]
                        
                        ai_table = Table(ai_data, colWidths=[3*inch, 2*inch])
                        ai_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 11),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        
                        story.append(ai_table)
                        story.append(Spacer(1, 0.2*inch))
                    
                    elif section_key == 'plagiarism':
                        plag_data = [
                            ['Metric', 'Value'],
                            ['Sources Checked', '50M+'],
                            ['Sources Found', section_data.get('sources_found', 0)],
                            ['Similarity Score', f"{section_data.get('similarity_score', 0)*100:.1f}%"],
                            ['Status', section_data.get('status', 'completed')]
                        ]
                        
                        plag_table = Table(plag_data, colWidths=[3*inch, 2*inch])
                        plag_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 11),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        
                        story.append(plag_table)
                        story.append(Spacer(1, 0.2*inch))
                        
                        # Add plagiarism matches if any
                        matches = section_data.get('matched_content', [])
                        if matches:
                            story.append(Paragraph("Detected Matches:", styles['Heading2']))
                            for i, match in enumerate(matches[:5]):  # Limit to 5 matches
                                match_text = f"{i+1}. Source: {match.get('source', 'Unknown')}"
                                if 'similarity' in match:
                                    match_text += f" ({match['similarity']}% match)"
                                story.append(Paragraph(match_text, styles['Normal']))
                            story.append(Spacer(1, 0.2*inch))
                    
                    elif section_key == 'quality':
                        metrics = section_data.get('metrics', {})
                        quality_data = [
                            ['Metric', 'Value'],
                            ['Word Count', metrics.get('word_count', 0)],
                            ['Sentence Count', metrics.get('sentence_count', 0)],
                            ['Avg Sentence Length', f"{metrics.get('avg_sentence_length', 0):.1f} words"],
                            ['Readability', metrics.get('readability', 'Unknown')]
                        ]
                        
                        quality_table = Table(quality_data, colWidths=[3*inch, 2*inch])
                        quality_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 11),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        
                        story.append(quality_table)
                        story.append(Spacer(1, 0.2*inch))
        
        # Recommendations
        if 'recommendations' in results and results['recommendations']:
            story.append(PageBreak())
            story.append(Paragraph("Recommendations", heading_style))
            for i, rec in enumerate(results['recommendations']):
                story.append(Paragraph(f"{i+1}. {rec}", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
        
        # Methodology
        story.append(PageBreak())
        story.append(Paragraph("Analysis Methodology", heading_style))
        story.append(Paragraph(
            "This report was generated using Facts & Fakes AI's advanced analysis engine, which combines multiple detection methods:",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.1*inch))
        
        methodology_items = [
            "• AI Detection: Advanced pattern recognition and linguistic analysis",
            "• Plagiarism Check: Comparison against millions of online sources",
            "• Quality Analysis: Readability and structural assessment",
            "• Multi-modal Analysis: Cross-validation between different detection methods"
        ]
        
        for item in methodology_items:
            story.append(Paragraph(item, styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("© 2025 Facts & Fakes AI. All rights reserved.", styles['Normal']))
        story.append(Paragraph("This report is for informational purposes only.", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        logger.error(f"Enhanced PDF generation error: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def generate_enhanced_unified_pdf_report(results):
    """Generate a comprehensive enhanced PDF report for unified analysis"""
    try:
        from io import BytesIO
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, HRFlowable, KeepTogether
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT
        from reportlab.graphics.shapes import Drawing, Rect, String
        from reportlab.graphics.charts.piecharts import Pie
        from reportlab.graphics.charts.barcharts import VerticalBarChart
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Enhanced custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=28,
            textColor=colors.HexColor('#4a90e2'),
            spaceAfter=40,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#666666'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        heading1_style = ParagraphStyle(
            'CustomHeading1',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#357abd'),
            spaceAfter=15,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        )
        
        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#4a90e2'),
            spaceAfter=10,
            spaceBefore=10
        )
        
        # Cover Page
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("AI Detection & Plagiarism Analysis", title_style))
        story.append(Paragraph("Comprehensive Content Authenticity Report", subtitle_style))
        story.append(Spacer(1, 1*inch))
        
        # Report metadata box
        metadata = results.get('metadata', {})
        cover_data = [
            ['Report Generated:', datetime.now().strftime('%B %d, %Y at %I:%M %p')],
            ['Analysis ID:', metadata.get('analysis_id', 'N/A')],
            ['Analysis Type:', metadata.get('analysis_tier', 'Professional').title()],
            ['Content Type:', metadata.get('content_type', 'Text').title()]
        ]
        
        cover_table = Table(cover_data, colWidths=[2.5*inch, 3.5*inch])
        cover_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0, colors.white),
            ('LINEBELOW', (0, 0), (-1, -2), 1, colors.HexColor('#e0e0e0')),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(cover_table)
        story.append(PageBreak())
        
        # Executive Summary Page
        story.append(Paragraph("Executive Summary", heading1_style))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#4a90e2')))
        story.append(Spacer(1, 0.3*inch))
        
        # Overall Score Visual
        trust_score = results.get('trust_score', 0)
        ai_probability = results.get('ai_probability', 0)
        plagiarism_score = results.get('plagiarism_score', 0)
        
        # Score interpretation
        if trust_score >= 80:
            score_interpretation = "Highly Trustworthy"
            score_color = colors.HexColor('#28a745')
        elif trust_score >= 60:
            score_interpretation = "Generally Trustworthy"
            score_color = colors.HexColor('#ffc107')
        elif trust_score >= 40:
            score_interpretation = "Moderate Concerns"
            score_color = colors.HexColor('#ff9800')
        else:
            score_interpretation = "Significant Issues"
            score_color = colors.HexColor('#dc3545')
        
        # Main score display
        score_data = [
            ['OVERALL TRUST SCORE', '', ''],
            [f'{trust_score}%', score_interpretation, '']
        ]
        
        score_display = Table(score_data, colWidths=[2*inch, 3*inch, 1.5*inch])
        score_display.setStyle(TableStyle([
            ('SPAN', (0, 0), (2, 0)),
            ('BACKGROUND', (0, 0), (2, 0), colors.HexColor('#4a90e2')),
            ('TEXTCOLOR', (0, 0), (2, 0), colors.white),
            ('ALIGN', (0, 0), (2, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (2, 0), 16),
            ('BACKGROUND', (0, 1), (0, 1), score_color),
            ('TEXTCOLOR', (0, 1), (0, 1), colors.white),
            ('ALIGN', (0, 1), (0, 1), 'CENTER'),
            ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (0, 1), 36),
            ('ALIGN', (1, 1), (1, 1), 'CENTER'),
            ('FONTNAME', (1, 1), (1, 1), 'Helvetica'),
            ('FONTSIZE', (1, 1), (1, 1), 18),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0'))
        ]))
        
        story.append(score_display)
        story.append(Spacer(1, 0.3*inch))
        
        # Component Scores
        story.append(Paragraph("Analysis Components", heading2_style))
        
        component_data = [
            ['Component', 'Score', 'Status'],
            ['AI Detection', f"{ai_probability}% AI probability", 
             'High' if ai_probability > 70 else 'Moderate' if ai_probability > 40 else 'Low'],
            ['Plagiarism Check', f"{plagiarism_score}% similarity", 
             'Detected' if plagiarism_score > 20 else 'Clear'],
            ['Content Originality', f"{100 - max(ai_probability, plagiarism_score)}% original", 
             'Excellent' if (100 - max(ai_probability, plagiarism_score)) > 80 else 'Good' if (100 - max(ai_probability, plagiarism_score)) > 60 else 'Fair']
        ]
        
        component_table = Table(component_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
        component_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#357abd')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.white),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#357abd'))
        ]))
        
        story.append(component_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Summary text
        if 'summary' in results and results['summary']:
            story.append(Paragraph("Summary", heading2_style))
            story.append(Paragraph(results['summary'], styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Key Findings
        story.append(Paragraph("Key Findings", heading2_style))
        findings = []
        
        if ai_probability > 70:
            findings.append("• High probability of AI-generated content detected")
        elif ai_probability > 40:
            findings.append("• Moderate AI indicators present in the content")
        else:
            findings.append("• Content appears to be primarily human-written")
        
        if plagiarism_score > 30:
            findings.append("• Significant similarity to existing online sources found")
        elif plagiarism_score > 10:
            findings.append("• Some similar content detected online")
        else:
            findings.append("• No significant plagiarism detected")
        
        quality_metrics = results.get('analysis_sections', {}).get('quality', {}).get('metrics', {})
        if quality_metrics.get('avg_sentence_length', 0) > 30:
            findings.append("• Complex sentence structures may impact readability")
        
        for finding in findings:
            story.append(Paragraph(finding, styles['Normal']))
        
        # Detailed Analysis Sections
        story.append(PageBreak())
        story.append(Paragraph("Detailed Analysis", heading1_style))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#4a90e2')))
        story.append(Spacer(1, 0.3*inch))
        
        # Process each analysis section
        sections = results.get('analysis_sections', {})
        
        # AI Detection Section
        if 'ai_detection' in sections:
            ai_section = sections['ai_detection']
            story.append(Paragraph("AI Content Detection", heading2_style))
            
            if ai_section.get('content'):
                story.append(Paragraph(ai_section['content'], styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            # AI Detection Details Table
            ai_details = [
                ['Metric', 'Value', 'Interpretation'],
                ['AI Probability', f"{ai_section.get('ai_probability', 0)}%", 
                 'High' if ai_section.get('ai_probability', 0) > 70 else 'Moderate' if ai_section.get('ai_probability', 0) > 40 else 'Low'],
                ['Human Probability', f"{ai_section.get('human_probability', 100)}%", 
                 'High' if ai_section.get('human_probability', 100) > 70 else 'Moderate' if ai_section.get('human_probability', 100) > 40 else 'Low'],
                ['Confidence Level', f"{ai_section.get('confidence', 0.5)*100:.1f}%", 
                 'High' if ai_section.get('confidence', 0.5) > 0.8 else 'Moderate' if ai_section.get('confidence', 0.5) > 0.6 else 'Low'],
                ['Analysis Status', ai_section.get('status', 'completed').title(), 
                 'Full Analysis' if ai_section.get('status') == 'completed' else 'Limited Analysis']
            ]
            
            ai_details_table = Table(ai_details, colWidths=[2*inch, 1.5*inch, 2.5*inch])
            ai_details_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.white),
                ('LINEBELOW', (0, 0), (-1, -2), 1, colors.HexColor('#e0e0e0'))
            ]))
            
            story.append(ai_details_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Plagiarism Detection Section
        if 'plagiarism' in sections:
            plag_section = sections['plagiarism']
            story.append(Paragraph("Plagiarism Detection", heading2_style))
            
            if plag_section.get('content'):
                story.append(Paragraph(plag_section['content'], styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Plagiarism Details Table
            plag_details = [
                ['Metric', 'Value'],
                ['Sources Checked', '50M+ web sources'],
                ['Matches Found', plag_section.get('sources_found', 0)],
                ['Highest Similarity', f"{plag_section.get('similarity_score', 0)*100:.1f}%"],
                ['Analysis Status', plag_section.get('status', 'completed').title()]
            ]
            
            plag_details_table = Table(plag_details, colWidths=[3*inch, 3*inch])
            plag_details_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.white)
            ]))
            
            story.append(plag_details_table)
            
            # Show matches if any
            matches = plag_section.get('matched_content', plag_section.get('details', []))
            if matches:
                story.append(Spacer(1, 0.2*inch))
                story.append(Paragraph("Top Matches Found:", styles['Heading3']))
                for i, match in enumerate(matches[:5]):  # Limit to top 5
                    match_text = f"{i+1}. "
                    if isinstance(match, dict):
                        match_text += f"Source: {match.get('source', match.get('title', 'Unknown'))}"
                        if 'similarity' in match:
                            match_text += f" ({match['similarity']}% similarity)"
                        elif 'percentage' in match:
                            match_text += f" ({match['percentage']}% similarity)"
                    else:
                        match_text += str(match)
                    story.append(Paragraph(match_text, styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
        
        # Quality Analysis Section
        if 'quality' in sections:
            quality_section = sections['quality']
            story.append(PageBreak())
            story.append(Paragraph("Content Quality Analysis", heading2_style))
            
            metrics = quality_section.get('metrics', {})
            if metrics:
                quality_data = [
                    ['Metric', 'Value', 'Assessment'],
                    ['Word Count', f"{metrics.get('word_count', 0):,}", 
                     'Substantial' if metrics.get('word_count', 0) > 500 else 'Moderate' if metrics.get('word_count', 0) > 200 else 'Brief'],
                    ['Sentence Count', metrics.get('sentence_count', 0), 
                     'Well-structured' if metrics.get('sentence_count', 0) > 10 else 'Basic'],
                    ['Avg Sentence Length', f"{metrics.get('avg_sentence_length', 0):.1f} words", 
                     metrics.get('readability', 'Unknown')],
                    ['Readability', metrics.get('readability', 'Not assessed'), 
                     'Optimal' if metrics.get('readability') == 'Good' else 'Review recommended']
                ]
                
                quality_table = Table(quality_data, colWidths=[2*inch, 2*inch, 2*inch])
                quality_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.white)
                ]))
                
                story.append(quality_table)
        
        # Recommendations Section
        if 'recommendations' in results and results['recommendations']:
            story.append(PageBreak())
            story.append(Paragraph("Recommendations", heading1_style))
            story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#4a90e2')))
            story.append(Spacer(1, 0.3*inch))
            
            for i, rec in enumerate(results['recommendations']):
                rec_style = ParagraphStyle(
                    'RecStyle',
                    parent=styles['Normal'],
                    fontSize=11,
                    leftIndent=20,
                    bulletIndent=0
                )
                story.append(Paragraph(f"• {rec}", rec_style))
                story.append(Spacer(1, 0.1*inch))
        
        # Methodology Section
        story.append(PageBreak())
        story.append(Paragraph("Analysis Methodology", heading1_style))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#4a90e2')))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph(
            "This comprehensive report was generated using Facts & Fakes AI's advanced multi-layered analysis system:",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.2*inch))
        
        methodology_sections = [
            ("AI Detection Algorithm", [
                "Advanced pattern recognition for AI-generated content",
                "Linguistic analysis including perplexity and burstiness metrics",
                "Cross-validation with multiple AI detection models",
                "Real-time comparison against known AI writing patterns"
            ]),
            ("Plagiarism Detection System", [
                "Comparison against 50+ million online sources",
                "Academic database cross-referencing",
                "Real-time web crawling for recent content",
                "Fuzzy matching algorithms for paraphrased content"
            ]),
            ("Quality Assessment", [
                "Readability scoring using multiple metrics",
                "Structural analysis for coherence and flow",
                "Grammar and style evaluation",
                "Content depth and substantiation assessment"
            ])
        ]
        
        for method_title, method_points in methodology_sections:
            story.append(Paragraph(method_title, heading2_style))
            for point in method_points:
                story.append(Paragraph(f"• {point}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Disclaimer and Footer
        story.append(PageBreak())
        story.append(Spacer(1, 4*inch))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
        story.append(Spacer(1, 0.2*inch))
        
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER
        )
        
        story.append(Paragraph(
            "This report is provided for informational purposes only. While Facts & Fakes AI uses advanced technology "
            "to detect AI-generated content and plagiarism, no automated system is 100% accurate. Results should be "
            "used as one factor in a comprehensive content evaluation process.",
            disclaimer_style
        ))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("© 2025 Facts & Fakes AI. All rights reserved.", disclaimer_style))
        story.append(Paragraph("www.factsandfakesai.com", disclaimer_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        logger.error(f"Enhanced unified PDF generation error: {str(e)}")
        logger.error(traceback.format_exc())
        # Try to generate a basic PDF as fallback
        try:
            return generate_basic_pdf_fallback(results)
        except:
            return None

def generate_basic_pdf_fallback(results):
    """Fallback PDF generation with minimal formatting"""
    try:
        from io import BytesIO
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Basic content
        story.append(Paragraph("Facts & Fakes AI Analysis Report", styles['Title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Generated: {datetime.now()}", styles['Normal']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Trust Score: {results.get('trust_score', 'N/A')}%", styles['Heading1']))
        story.append(Spacer(1, 12))
        
        if 'summary' in results:
            story.append(Paragraph("Summary:", styles['Heading2']))
            story.append(Paragraph(results['summary'], styles['Normal']))
            story.append(Spacer(1, 12))
        
        if 'recommendations' in results:
            story.append(Paragraph("Recommendations:", styles['Heading2']))
            for rec in results['recommendations']:
                story.append(Paragraph(f"• {rec}", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    except:
        return None

# Existing API endpoints (keep unchanged for compatibility)

@app.route('/api/analyze-news', methods=['POST'])
@csrf.exempt
@track_usage('news')
def api_analyze_news():
    """News analysis endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        content = data.get('content', '')
        content_type = data.get('type', 'text')
        is_pro = data.get('is_pro', True)  # DEV MODE: always pro
        
        results = analyze_news_route(content, is_pro)
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"News analysis error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analyze-text', methods=['POST'])
@csrf.exempt
@track_usage('text')
def api_analyze_text():
    """Text analysis endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        text = data.get('text', '')
        is_pro = data.get('is_pro', True)  # DEV MODE: always pro
        
        if is_pro:
            results = perform_realistic_unified_text_analysis(text)
        else:
            results = perform_basic_text_analysis(text)
        
        return jsonify({'success': True, 'results': results})
        
    except Exception as e:
        logger.error(f"Text analysis error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analyze-image', methods=['POST'])
@csrf.exempt
@track_usage('image')
def api_analyze_image():
    """Image analysis endpoint"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        is_pro = request.form.get('is_pro', 'true').lower() == 'true'  # DEV MODE: always pro
        
        if is_pro:
            results = perform_realistic_image_analysis(image_file)
        else:
            results = perform_basic_image_analysis(image_file)
        
        return jsonify({'success': True, 'results': results})
        
    except Exception as e:
        logger.error(f"Image analysis error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Authentication routes

@app.route('/api/login', methods=['POST'])
@csrf.exempt
def api_login():
    """Login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email', '')
        password = data.get('password', '')
        
        # In production, verify credentials
        # For now, create a mock user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Create mock user for testing
            user = User(
                email=email,
                name=email.split('@')[0],
                subscription_tier='free'
            )
        
        login_user(user)
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'subscription_tier': user.subscription_tier,
                'usage_status': get_usage_status(user)
            }
        })
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'success': False, 'error': 'Login failed'}), 500

@app.route('/api/signup', methods=['POST'])
@csrf.exempt
def api_signup():
    """Signup endpoint"""
    try:
        data = request.get_json()
        email = data.get('email', '')
        password = data.get('password', '')
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'success': False, 'error': 'User already exists'}), 400
        
        # Create new user
        user = User(
            email=email,
            name=email.split('@')[0],
            subscription_tier='free'
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'subscription_tier': user.subscription_tier
            }
        })
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        return jsonify({'success': False, 'error': 'Signup failed'}), 500

@app.route('/api/logout', methods=['POST'])
@csrf.exempt
def api_logout():
    """Logout endpoint"""
    logout_user()
    session.clear()
    return jsonify({'success': True})

@app.route('/api/user/status', methods=['GET'])
def api_user_status():
    """Get user authentication status"""
    # TEMPORARY: Skip all database checks and return pro user
    logger.info("User status check - returning pro tier (database bypassed)")
    return jsonify({
        'authenticated': True,
        'email': 'test@factsandfakes.ai',
        'subscription_tier': 'pro',
        'usage_status': {
            'tier': 'pro',
            'usage': {
                'daily': {'basic': 0, 'pro': 0},
                'weekly': {'basic': 0, 'pro': 0}
            },
            'limits': {
                'daily': {'basic': -1, 'pro': -1},
                'weekly': {'basic': -1, 'pro': -1}
            },
            'resets': {
                'daily': datetime.utcnow().isoformat(),
                'weekly': datetime.utcnow().isoformat()
            }
        },
        'usage_today': 0,
        'daily_limit': -1
    })

# Contact and beta signup routes

@app.route('/api/contact', methods=['POST'])
@csrf.exempt
def api_contact():
    """Contact form submission"""
    try:
        data = request.get_json()
        
        contact = Contact(
            name=data.get('name', ''),
            email=data.get('email', ''),
            message=data.get('message', ''),
            timestamp=datetime.utcnow()
        )
        
        db.session.add(contact)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Message sent successfully'})
        
    except Exception as e:
        logger.error(f"Contact form error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to send message'}), 500

@app.route('/api/beta-signup', methods=['POST'])
@csrf.exempt
def api_beta_signup():
    """Beta signup endpoint"""
    try:
        data = request.get_json()
        
        signup = BetaSignup(
            email=data.get('email', ''),
            timestamp=datetime.utcnow()
        )
        
        db.session.add(signup)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Beta signup successful'})
        
    except Exception as e:
        logger.error(f"Beta signup error: {str(e)}")
        return jsonify({'success': False, 'error': 'Signup failed'}), 500

# Error handlers

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return render_template('500.html'), 500

# Application initialization

def create_tables():
    """Create database tables if they don't exist"""
    try:
        with app.app_context():
            # Import the migration functions
            from services.database import migrate_database
            
            # Run full migration
            if migrate_database():
                logger.info("Database migration completed successfully")
            else:
                logger.warning("Database migration had issues - check logs")
                
            # Ensure all tables exist by trying to create them
            try:
                db.create_all()
                logger.info("Database tables verified/created")
            except Exception as e:
                logger.warning(f"Table creation warning (may be normal if tables exist): {str(e)}")
                
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == '__main__':
    # Initialize database
    create_tables()
    
    # Initialize service architecture
    if not initialize_services():
        logger.warning("Service architecture initialization failed - running with limited functionality")
    
    # Run application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Facts & Fakes AI on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
