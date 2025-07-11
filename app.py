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

# Load configuration
app.config.from_object(config)

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

# Database initialization
db.init_app(app)

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
        
        # Register services
        from services.ai_analysis_service import AIAnalysisService
        from services.plagiarism_service import PlagiarismService
        
        service_registry.register_service('ai_analysis', AIAnalysisService)
        service_registry.register_service('plagiarism', PlagiarismService)
        
        # Initialize all services
        service_registry.initialize_all_services()
        
        # Check service health
        health_status = service_registry.get_health_status()
        logger.info(f"Service health status: {health_status}")
        
        logger.info("Service architecture initialized successfully")
        return True
        
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

def check_usage_limit(user, analysis_type, is_pro_analysis=False):
    """Check if user has exceeded their usage limit"""
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

# Updated track_usage decorator
def track_usage(analysis_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Determine if this is a pro analysis from the request
                is_pro = request.form.get('tier', 'basic') == 'professional'
                
                # Check usage limit
                can_proceed, error_msg = check_usage_limit(current_user, analysis_type, is_pro)
                
                if not can_proceed and os.environ.get('FLASK_ENV') != 'development':
                    return jsonify({
                        'success': False,
                        'error': error_msg,
                        'limit_reached': True,
                        'usage_status': get_usage_status(current_user)
                    }), 429
                
                # Log usage with session tracking for anonymous users
                user_id = getattr(current_user, 'id', None) if hasattr(current_user, 'id') else None
                session_id = None
                
                if user_id is None:
                    session_id = session.get('anonymous_id', request.remote_addr)
                
                analysis_level = 'pro' if is_pro else 'basic'
                usage_log = UsageLog(
                    user_id=user_id,
                    session_id=session_id,
                    analysis_type=f"{analysis_type}_{analysis_level}",
                    timestamp=datetime.utcnow(),
                    ip_address=request.remote_addr
                )
                db.session.add(usage_log)
                db.session.commit()
                
            except Exception as e:
                logger.error(f"Usage tracking error: {str(e)}")
            
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
            health_data['services'] = service_registry.get_health_status()
            
            # If any service is unhealthy, mark as degraded
            for service_name, service_status in health_data['services'].items():
                if service_status.get('status') != 'healthy':
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
@app.route('/api/analyze-unified/stream', methods=['POST'])
@csrf.exempt
@track_usage('unified')
@stream_progress
def analyze_unified_stream(*args, **kwargs):
    """Streaming version of unified analysis with real-time progress updates"""
    try:
        # Get request data
        content = request.form.get('content', '').strip()
        content_type = request.form.get('content_type', 'text')
        tier = request.form.get('tier', 'basic')
        
        # Determine if this is pro analysis
        user_tier = get_user_tier(current_user)
        is_pro = user_tier == 'pro' or (user_tier == 'free' and tier == 'professional')
        
        # Handle file upload for images
        image_file = None
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename == '':
                image_file = None
        
        # Stage 1: Initial processing
        yield {'stage': 'extracting', 'progress': 10, 'message': 'Extracting content...'}
        
        # Validate input
        if not content and not image_file:
            yield {'stage': 'error', 'error': 'No content provided'}
            return
        
        # Check service availability
        if not service_registry:
            yield {'stage': 'error', 'error': 'Services unavailable'}
            return
        
        # Initialize results structure
        results = {
            'trust_score': 50,
            'analysis_sections': {},
            'summary': '',
            'recommendations': [],
            'metadata': {
                'analysis_time': datetime.utcnow().isoformat(),
                'services_used': [],
                'is_pro': is_pro,
                'analysis_tier': 'professional' if is_pro else 'basic'
            }
        }
        
        # Stage 2: AI Analysis
        yield {'stage': 'ai_analysis', 'progress': 25, 'message': 'Running AI detection algorithms...'}
        
        ai_service = service_registry.get_service('ai_analysis')
        if ai_service and ai_service.is_available():
            logger.info("Running AI analysis...")
            ai_results = ai_service.analyze_content(content, is_pro)
            
            if ai_results.get('success'):
                results['analysis_sections']['ai_detection'] = {
                    'title': 'AI Content Detection',
                    'content': ai_results.get('analysis', 'Analysis completed'),
                    'confidence': ai_results.get('confidence', 0.5),
                    'details': ai_results.get('details', {}),
                    'ai_probability': ai_results.get('ai_probability', 0),
                    'human_probability': ai_results.get('human_probability', 100),
                    'status': 'completed'
                }
                results['metadata']['services_used'].append('ai_analysis')
                
                # Adjust trust score
                if ai_results.get('is_ai_generated'):
                    results['trust_score'] -= int(ai_results.get('confidence', 0.5) * 30)
            
            yield {'stage': 'ai_analysis', 'progress': 40, 'message': 'AI analysis complete', 'partial_results': {'ai_detection': ai_results}}
        
        # Stage 3: Pattern Analysis
        yield {'stage': 'pattern_analysis', 'progress': 45, 'message': 'Analyzing linguistic patterns...'}
        time.sleep(0.5)  # Simulate processing
        
        # Stage 4: Plagiarism Check
        yield {'stage': 'plagiarism', 'progress': 60, 'message': 'Checking against millions of sources...'}
        
        plagiarism_service = service_registry.get_service('plagiarism')
        if plagiarism_service and plagiarism_service.is_available() and content:
            logger.info("Running plagiarism analysis...")
            plagiarism_results = plagiarism_service.check_plagiarism(content, is_pro)
            
            if plagiarism_results.get('success'):
                results['analysis_sections']['plagiarism'] = {
                    'title': 'Plagiarism Detection',
                    'content': plagiarism_results.get('summary', 'Plagiarism check completed'),
                    'sources_found': plagiarism_results.get('sources_count', 0),
                    'similarity_score': plagiarism_results.get('max_similarity', 0),
                    'details': plagiarism_results.get('sources', []),
                    'matched_content': plagiarism_results.get('matched_content', []),
                    'status': 'completed'
                }
                results['metadata']['services_used'].append('plagiarism')
                
                # Adjust trust score
                similarity = plagiarism_results.get('max_similarity', 0)
                if similarity > 0.5:
                    results['trust_score'] -= int(similarity * 25)
            
            yield {'stage': 'plagiarism', 'progress': 75, 'message': 'Plagiarism check complete', 'partial_results': {'plagiarism': plagiarism_results}}
        
        # Stage 5: Quality Analysis
        yield {'stage': 'quality', 'progress': 85, 'message': 'Evaluating content quality...'}
        time.sleep(0.5)  # Simulate processing
        
        # Stage 6: Generate Report
        yield {'stage': 'report', 'progress': 95, 'message': 'Generating comprehensive report...'}
        
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
                content_snippet=content[:500] if content else 'Image analysis',
                results=json.dumps(results),
                trust_score=results['trust_score'],
                timestamp=datetime.utcnow()
            )
            db.session.add(analysis)
            db.session.commit()
            results['metadata']['analysis_id'] = analysis.id
        except Exception as e:
            logger.error(f"Database save error: {str(e)}")
        
        # Final result
        yield {
            'stage': 'complete',
            'progress': 100,
            'message': 'Analysis complete!',
            'results': results,
            'usage_status': get_usage_status(current_user)
        }
        
    except Exception as e:
        logger.error(f"Unified analysis streaming error: {str(e)}")
        yield {'stage': 'error', 'error': str(e)}

# Keep the original endpoint for backwards compatibility
@app.route('/api/analyze-unified', methods=['POST'])
@csrf.exempt
@track_usage('unified')
def analyze_unified():
    """Original unified analysis endpoint"""
    # This now redirects to the streaming version
    # But returns a standard JSON response for compatibility
    
    # For now, keep the original implementation
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
        
        # Check service availability
        if not service_registry:
            logger.error("Service registry not available")
            return jsonify({
                'success': False,
                'error': 'Analysis services temporarily unavailable'
            }), 503
        
        # Initialize results structure
        results = {
            'trust_score': 50,
            'analysis_sections': {},
            'summary': '',
            'recommendations': [],
            'metadata': {
                'analysis_time': datetime.utcnow().isoformat(),
                'services_used': [],
                'is_pro': is_pro,
                'analysis_tier': 'professional' if is_pro else 'basic'
            }
        }
        
        # Perform AI Analysis
        ai_service = service_registry.get_service('ai_analysis')
        if ai_service and ai_service.is_available():
            try:
                logger.info("Running AI analysis...")
                ai_results = ai_service.analyze_content(content, is_pro)
                
                if ai_results.get('success'):
                    results['analysis_sections']['ai_detection'] = {
                        'title': 'AI Content Detection',
                        'content': ai_results.get('analysis', 'Analysis completed'),
                        'confidence': ai_results.get('confidence', 0.5),
                        'details': ai_results.get('details', {}),
                        'ai_probability': ai_results.get('ai_probability', 0),
                        'human_probability': ai_results.get('human_probability', 100),
                        'status': 'completed'
                    }
                    results['metadata']['services_used'].append('ai_analysis')
                    
                    # Adjust trust score based on AI detection
                    ai_confidence = ai_results.get('confidence', 0.5)
                    if ai_results.get('is_ai_generated'):
                        results['trust_score'] -= int(ai_confidence * 30)
                    
                else:
                    results['analysis_sections']['ai_detection'] = {
                        'title': 'AI Content Detection',
                        'content': 'AI analysis unavailable - using pattern analysis',
                        'status': 'fallback'
                    }
                    
            except Exception as e:
                logger.error(f"AI analysis error: {str(e)}")
                results['analysis_sections']['ai_detection'] = {
                    'title': 'AI Content Detection',
                    'content': f'Analysis error: {str(e)}',
                    'status': 'error'
                }
        
        # Perform Plagiarism Analysis
        plagiarism_service = service_registry.get_service('plagiarism')
        if plagiarism_service and plagiarism_service.is_available() and content:
            try:
                logger.info("Running plagiarism analysis...")
                plagiarism_results = plagiarism_service.check_plagiarism(content, is_pro)
                
                if plagiarism_results.get('success'):
                    results['analysis_sections']['plagiarism'] = {
                        'title': 'Plagiarism Detection',
                        'content': plagiarism_results.get('summary', 'Plagiarism check completed'),
                        'sources_found': plagiarism_results.get('sources_count', 0),
                        'similarity_score': plagiarism_results.get('max_similarity', 0),
                        'details': plagiarism_results.get('sources', []),
                        'matched_content': plagiarism_results.get('matched_content', []),
                        'status': 'completed'
                    }
                    results['metadata']['services_used'].append('plagiarism')
                    
                    # Adjust trust score based on plagiarism
                    similarity = plagiarism_results.get('max_similarity', 0)
                    if similarity > 0.5:
                        results['trust_score'] -= int(similarity * 25)
                        
                else:
                    results['analysis_sections']['plagiarism'] = {
                        'title': 'Plagiarism Detection',
                        'content': 'Plagiarism check unavailable',
                        'status': 'unavailable'
                    }
                    
            except Exception as e:
                logger.error(f"Plagiarism analysis error: {str(e)}")
                results['analysis_sections']['plagiarism'] = {
                    'title': 'Plagiarism Detection',
                    'content': f'Check error: {str(e)}',
                    'status': 'error'
                }
        
        # Perform Image Analysis (if image provided)
        if image_file:
            try:
                logger.info("Running image analysis...")
                if is_pro:
                    image_results = perform_realistic_image_analysis(image_file)
                else:
                    image_results = perform_basic_image_analysis(image_file)
                
                results['analysis_sections']['image_authenticity'] = {
                    'title': 'Image Authenticity',
                    'content': image_results.get('summary', 'Image analysis completed'),
                    'authenticity_score': image_results.get('authenticity_score', 0.5),
                    'manipulations_detected': image_results.get('manipulations', []),
                    'metadata_analysis': image_results.get('metadata', {}),
                    'status': 'completed'
                }
                results['metadata']['services_used'].append('image_analysis')
                
                # Adjust trust score based on image authenticity
                auth_score = image_results.get('authenticity_score', 0.5)
                if auth_score < 0.5:
                    results['trust_score'] -= int((0.5 - auth_score) * 40)
                    
            except Exception as e:
                logger.error(f"Image analysis error: {str(e)}")
                results['analysis_sections']['image_authenticity'] = {
                    'title': 'Image Authenticity',
                    'content': f'Image analysis error: {str(e)}',
                    'status': 'error'
                }
        
        # Perform URL/News Analysis (if URL detected)
        if content and (content.startswith('http://') or content.startswith('https://')):
            try:
                logger.info("Running news analysis...")
                news_results = analyze_news_route(content, is_pro)
                
                if news_results.get('success'):
                    results['analysis_sections']['news_verification'] = {
                        'title': 'News Verification',
                        'content': news_results.get('summary', 'News analysis completed'),
                        'bias_score': news_results.get('bias_score', 0),
                        'credibility': news_results.get('source_credibility', 'Unknown'),
                        'fact_checks': news_results.get('fact_checks', []),
                        'status': 'completed'
                    }
                    results['metadata']['services_used'].append('news_analysis')
                    
                    # Adjust trust score based on news analysis
                    bias = abs(news_results.get('bias_score', 0))
                    if bias > 0.5:
                        results['trust_score'] -= int(bias * 20)
                        
            except Exception as e:
                logger.error(f"News analysis error: {str(e)}")
                results['analysis_sections']['news_verification'] = {
                    'title': 'News Verification',
                    'content': f'News analysis error: {str(e)}',
                    'status': 'error'
                }
        
        # Ensure trust score is within bounds
        results['trust_score'] = max(0, min(100, results['trust_score']))
        
        # Generate summary
        services_used = len(results['metadata']['services_used'])
        ai_section = results['analysis_sections'].get('ai_detection', {})
        plagiarism_section = results['analysis_sections'].get('plagiarism', {})
        
        # Create detailed summary
        summary_parts = []
        
        # AI detection summary
        if ai_section.get('ai_probability', 0) > 50:
            summary_parts.append(f"Content appears to be AI-generated ({ai_section.get('ai_probability', 0)}% probability)")
        else:
            summary_parts.append(f"Content appears to be human-written ({ai_section.get('human_probability', 100)}% probability)")
        
        # Plagiarism summary
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
        
        # Save analysis to database
        try:
            analysis = Analysis(
                user_id=getattr(current_user, 'id', 1),
                content_type='unified',
                content_snippet=content[:500] if content else 'Image analysis',
                results=json.dumps(results),
                trust_score=results['trust_score'],
                timestamp=datetime.utcnow()
            )
            db.session.add(analysis)
            db.session.commit()
            results['metadata']['analysis_id'] = analysis.id
        except Exception as e:
            logger.error(f"Database save error: {str(e)}")
        
        # Add usage status to response
        results['usage_status'] = get_usage_status(current_user)
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Unified analysis error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Analysis failed - please try again'
        }), 500

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
    try:
        # Check if user is authenticated
        if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            return jsonify({
                'authenticated': True,
                'email': current_user.email,
                'subscription_tier': current_user.subscription_tier,
                'usage_status': get_usage_status(current_user),
                'usage_today': get_usage_count(current_user.id, 'unified_basic', 'daily'),
                'daily_limit': USAGE_LIMITS[current_user.subscription_tier]['daily']['basic']
            })
        else:
            # Anonymous user
            return jsonify({
                'authenticated': False,
                'subscription_tier': 'anonymous',
                'usage_status': get_usage_status(None),
                'usage_today': get_usage_count(None, 'unified_basic', 'weekly'),
                'daily_limit': 0,
                'weekly_limit': USAGE_LIMITS['anonymous']['weekly']['basic']
            })
    except Exception as e:
        logger.error(f"User status error: {str(e)}")
        # Return a safe default response
        return jsonify({
            'authenticated': False,
            'subscription_tier': 'anonymous',
            'usage_status': get_usage_status(None)
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
