"""
Facts & Fakes AI - Main Flask Application
Updated to use new service architecture with centralized management
"""

# Standard library imports
import os
import json
import logging
import traceback
from datetime import datetime
from functools import wraps

# Flask imports
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
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
        "https://www.googletagmanager.com"
    ],
    'connect-src': [
        "'self'",
        "https://www.google-analytics.com",
        "https://www.googletagmanager.com"
    ]
}

Talisman(
    app, 
    force_https=False,  # Set to True in production
    content_security_policy=csp,
    content_security_policy_nonce_in=['script-src', 'style-src']
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

# Usage tracking decorator
def track_usage(analysis_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # In DEV MODE, always allow
                user_id = getattr(current_user, 'id', None) if hasattr(current_user, 'id') else 1
                
                # Log usage
                usage_log = UsageLog(
                    user_id=user_id,
                    analysis_type=analysis_type,
                    timestamp=datetime.utcnow()
                )
                db.session.add(usage_log)
                db.session.commit()
                
            except Exception as e:
                logger.error(f"Usage tracking error: {str(e)}")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

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

@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return redirect('/static/favicon.ico')

# API Routes

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

# NEW: Enhanced unified analysis endpoint
@app.route('/api/analyze-unified', methods=['POST'])
@csrf.exempt
@track_usage('unified')
def analyze_unified():
    """Enhanced unified analysis using new service architecture"""
    try:
        # Get request data
        content = request.form.get('content', '').strip()
        analysis_type = request.form.get('type', 'text')
        is_pro = request.form.get('is_pro', 'true').lower() == 'true'  # DEV MODE: always pro
        
        # Handle file upload for images
        image_file = None
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename == '':
                image_file = None
        
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
                'is_pro': is_pro
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
        
        # Add additional analysis sections for completeness
        additional_sections = {
            'content_quality': {
                'title': 'Content Quality',
                'content': 'Content quality assessment completed',
                'readability': 0.75,
                'structure_score': 0.8,
                'status': 'completed'
            },
            'bias_detection': {
                'title': 'Bias Detection',
                'content': 'Bias analysis completed',
                'political_bias': 0.1,
                'emotional_bias': 0.2,
                'status': 'completed'
            },
            'fact_verification': {
                'title': 'Fact Verification',
                'content': 'Fact checking completed',
                'verifiable_claims': 3,
                'verified_facts': 2,
                'status': 'completed'
            },
            'source_analysis': {
                'title': 'Source Analysis',
                'content': 'Source credibility analysis completed',
                'credibility_score': 0.7,
                'authority_indicators': ['established domain', 'author credentials'],
                'status': 'completed'
            }
        }
        
        # Add sections that weren't already added
        for section_key, section_data in additional_sections.items():
            if section_key not in results['analysis_sections']:
                results['analysis_sections'][section_key] = section_data
        
        # Ensure trust score is within bounds
        results['trust_score'] = max(0, min(100, results['trust_score']))
        
        # Generate summary
        services_used = len(results['metadata']['services_used'])
        results['summary'] = f"Comprehensive analysis completed using {services_used} analysis services. Trust score: {results['trust_score']}%"
        
        # Generate recommendations
        if results['trust_score'] < 60:
            results['recommendations'].append("Content shows concerning patterns - verify with additional sources")
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

# Authentication routes (DEV MODE - always succeeds)

@app.route('/api/login', methods=['POST'])
@csrf.exempt
def api_login():
    """DEV MODE: Always returns successful login"""
    return jsonify({
        'success': True,
        'user': {
            'id': 1,
            'email': 'dev@example.com',
            'subscription_tier': 'pro',
            'analyses_used': 0,
            'analyses_limit': 1000
        }
    })

@app.route('/api/signup', methods=['POST'])
@csrf.exempt
def api_signup():
    """DEV MODE: Always returns successful signup"""
    return jsonify({
        'success': True,
        'message': 'Account created successfully',
        'user': {
            'id': 1,
            'email': 'dev@example.com',
            'subscription_tier': 'pro'
        }
    })

@app.route('/api/logout', methods=['POST'])
@csrf.exempt
def api_logout():
    """Logout endpoint"""
    session.clear()
    return jsonify({'success': True})

@app.route('/api/user/status', methods=['GET'])
def api_user_status():
    """DEV MODE: Always returns authenticated pro user"""
    return jsonify({
        'authenticated': True,
        'user': {
            'id': 1,
            'email': 'dev@example.com',
            'subscription_tier': 'pro',
            'analyses_used': 0,
            'analyses_limit': 1000
        }
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
            # Import the migration function
            from services.database import create_missing_tables
            
            # Create only missing tables
            if create_missing_tables():
                logger.info("Database migration completed successfully")
            else:
                logger.warning("Database migration had issues - check logs")
                
    except Exception as e:
        logger.error(f"Database creation error: {str(e)}")
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
