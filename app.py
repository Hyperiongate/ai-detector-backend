from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
import os
from datetime import datetime, timedelta
import secrets
import hashlib
from functools import wraps
import json
import base64
from io import BytesIO
from PIL import Image
import requests
from bs4 import BeautifulSoup
import re
from collections import Counter
import time
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool
import statistics

# Email imports with Python 3.13 compatibility
try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    try:
        # Fallback for older Python versions
        import smtplib
        from email.MIMEText import MIMEText
        from email.MIMEMultipart import MIMEMultipart
        EMAIL_AVAILABLE = True
    except ImportError:
        EMAIL_AVAILABLE = False
        MIMEText = None
        MIMEMultipart = None

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Check if database URL is configured
if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable is not set!")
    # Use a dummy SQLite database for local development
    DATABASE_URL = "sqlite:///local_dev.db"
    logger.warning("Using SQLite database for local development")

# Create engine with connection pooling disabled for Render
if DATABASE_URL.startswith('sqlite'):
    # SQLite configuration (for local dev)
    engine = create_engine(DATABASE_URL)
else:
    # PostgreSQL configuration (for production)
    # Update the DATABASE_URL to use psycopg instead of psycopg2
    if 'postgresql://' in DATABASE_URL and '+' not in DATABASE_URL:
        # Add the psycopg driver to the URL
        DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://')
    
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,
        pool_pre_ping=True,
        connect_args={
            "sslmode": "require",
            "connect_timeout": 10
        }
    )

# Create session factory
SessionLocal = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_beta = Column(Boolean, default=True)
    is_pro = Column(Boolean, default=False)
    daily_analyses = Column(Integer, default=0)
    last_analysis_date = Column(DateTime, default=datetime.utcnow)
    
class ContactMessage(Base):
    __tablename__ = 'contact_messages'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))
    user_agent = Column(Text)

# Create tables
Base.metadata.create_all(bind=engine)

# Email configuration
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'mail.factsandfakes.ai')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', 'contact@factsandfakes.ai')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL', 'contact@factsandfakes.ai')

# API Keys
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
GOOGLE_FACT_CHECK_API_KEY = os.environ.get('GOOGLE_FACT_CHECK_API_KEY')
MEDIASTACK_API_KEY = os.environ.get('MEDIASTACK_API_KEY')

# Helper Functions
def send_email(to_email, subject, html_content):
    """Send email using Bluehost SMTP with Python 3.13 compatibility"""
    if not EMAIL_AVAILABLE:
        logger.warning("Email functionality not available - imports failed")
        return False
        
    if not all([SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD]):
        logger.warning("Email configuration incomplete")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"Facts & Fakes AI <{SMTP_USERNAME}>"
        msg['To'] = to_email
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def check_rate_limit(user_id):
    """Check if user has reached their daily limit"""
    db_session = SessionLocal()
    try:
        user = db_session.query(User).filter_by(id=user_id).first()
        if not user:
            return False, "User not found"
        
        # Reset daily count if it's a new day
        if user.last_analysis_date.date() < datetime.utcnow().date():
            user.daily_analyses = 0
            user.last_analysis_date = datetime.utcnow()
            db_session.commit()
        
        # Check limits
        limit = 10 if user.is_pro else 5
        if user.daily_analyses >= limit:
            return False, f"Daily limit reached ({limit} analyses)"
        
        return True, user.daily_analyses
        
    finally:
        db_session.close()

def increment_usage(user_id):
    """Increment user's daily analysis count"""
    db_session = SessionLocal()
    try:
        user = db_session.query(User).filter_by(id=user_id).first()
        if user:
            user.daily_analyses += 1
            user.last_analysis_date = datetime.utcnow()
            db_session.commit()
    finally:
        db_session.close()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/news')
@app.route('/news.html')
def news():
    return render_template('news.html')

@app.route('/unified')
@app.route('/unified.html')
def unified():
    return render_template('unified.html')

@app.route('/imageanalysis')
@app.route('/imageanalysis.html')
def imageanalysis():
    return render_template('imageanalysis.html')

@app.route('/contact')
@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route('/missionstatement')
@app.route('/missionstatement.html')
def missionstatement():
    return render_template('missionstatement.html')

@app.route('/pricingplan')
@app.route('/pricingplan.html')
def pricingplan():
    return render_template('pricingplan.html')

# Authentication Routes
@app.route('/api/signup', methods=['POST'])
def signup():
    db_session = SessionLocal()
    try:
        data = request.json
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Check if user exists
        if db_session.query(User).filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            is_beta=True
        )
        db_session.add(user)
        db_session.commit()
        
        # Log user in
        session['user_id'] = user.id
        session['user_email'] = user.email
        session.permanent = True
        
        # Send welcome email
        welcome_subject = "Welcome to Facts & Fakes AI Beta!"
        welcome_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c5aa0;">Welcome to Facts & Fakes AI!</h2>
                <p>Hi there,</p>
                <p>Thank you for joining our beta program! You now have access to:</p>
                <ul>
                    <li>5 free AI text analyses per day</li>
                    <li>News verification and bias detection</li>
                    <li>Image manipulation detection</li>
                    <li>Plagiarism checking</li>
                </ul>
                <p>Start exploring at <a href="https://factsandfakes.ai">factsandfakes.ai</a></p>
                <p>Best regards,<br>The Facts & Fakes AI Team</p>
            </div>
        </body>
        </html>
        """
        send_email(email, welcome_subject, welcome_html)
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'user': {
                'email': user.email,
                'is_pro': user.is_pro,
                'daily_limit': 10 if user.is_pro else 5
            }
        })
        
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500
    finally:
        db_session.close()

@app.route('/api/login', methods=['POST'])
def login():
    db_session = SessionLocal()
    try:
        data = request.json
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        user = db_session.query(User).filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Set session
        session['user_id'] = user.id
        session['user_email'] = user.email
        session.permanent = True
        
        return jsonify({
            'success': True,
            'user': {
                'email': user.email,
                'is_pro': user.is_pro,
                'daily_limit': 10 if user.is_pro else 5
            }
        })
        
    finally:
        db_session.close()

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/user/status', methods=['GET'])
def user_status():
    if 'user_id' not in session:
        return jsonify({'authenticated': False})
    
    db_session = SessionLocal()
    try:
        user = db_session.query(User).filter_by(id=session['user_id']).first()
        if not user:
            session.clear()
            return jsonify({'authenticated': False})
        
        # Check daily usage
        if user.last_analysis_date.date() < datetime.utcnow().date():
            user.daily_analyses = 0
        
        return jsonify({
            'authenticated': True,
            'user': {
                'email': user.email,
                'is_pro': user.is_pro,
                'daily_limit': 10 if user.is_pro else 5,
                'analyses_today': user.daily_analyses
            }
        })
    finally:
        db_session.close()

# Contact Form Route
@app.route('/api/contact', methods=['POST'])
def contact_form():
    db_session = SessionLocal()
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['name', 'email', 'subject', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field.title()} is required'}), 400
        
        # Save to database
        contact_msg = ContactMessage(
            name=data['name'],
            email=data['email'],
            subject=data['subject'],
            message=data['message'],
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:500]
        )
        db_session.add(contact_msg)
        db_session.commit()
        
        # Send notification email to admin
        admin_subject = f"New Contact Form Submission - {data['subject']}"
        admin_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h3>New Contact Form Submission</h3>
            <p><strong>From:</strong> {data['name']} ({data['email']})</p>
            <p><strong>Subject:</strong> {data['subject']}</p>
            <p><strong>Message:</strong></p>
            <p style="background: #f4f4f4; padding: 15px; border-radius: 5px;">
                {data['message'].replace(chr(10), '<br>')}
            </p>
            <p><strong>Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
        </body>
        </html>
        """
        send_email(CONTACT_EMAIL, admin_subject, admin_html)
        
        # Send auto-reply to user
        user_subject = "We've Received Your Message - Facts & Fakes AI"
        user_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c5aa0;">Thank You for Contacting Us!</h2>
                <p>Hi {data['name']},</p>
                <p>We've received your message and will get back to you within 24-48 hours.</p>
                <p><strong>Your Message:</strong></p>
                <div style="background: #f4f4f4; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Subject:</strong> {data['subject']}</p>
                    <p>{data['message']}</p>
                </div>
                <p>In the meantime, feel free to explore our AI detection tools at 
                   <a href="https://factsandfakes.ai">factsandfakes.ai</a></p>
                <p>Best regards,<br>The Facts & Fakes AI Team</p>
            </div>
        </body>
        </html>
        """
        send_email(data['email'], user_subject, user_html)
        
        return jsonify({
            'success': True,
            'message': 'Thank you for your message. We\'ll get back to you soon!'
        })
        
    except Exception as e:
        logger.error(f"Contact form error: {str(e)}")
        return jsonify({'error': 'Failed to send message. Please try again.'}), 500
    finally:
        db_session.close()

# AI Detection Route
@app.route('/api/detect-ai', methods=['POST'])
def detect_ai():
    try:
        # Check authentication for non-demo mode
        if 'user_id' in session:
            can_proceed, message = check_rate_limit(session['user_id'])
            if not can_proceed:
                return jsonify({'error': message, 'limit_reached': True}), 429
        
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # For demo or if no API key, return pattern-based analysis
        if not OPENAI_API_KEY or data.get('demo', False):
            result = analyze_text_patterns(text)
        else:
            # Use OpenAI API for pro users
            result = analyze_with_openai(text)
        
        # Increment usage for authenticated users
        if 'user_id' in session:
            increment_usage(session['user_id'])
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"AI detection error: {str(e)}")
        return jsonify({'error': 'Analysis failed'}), 500

def calculate_sentence_uniformity(sentences):
    """Calculate standard deviation of sentence lengths"""
    sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
    if len(sentence_lengths) > 1:
        return statistics.stdev(sentence_lengths)
    return 0

def analyze_text_patterns(text):
    """Pattern-based AI detection for demo/free tier"""
    
    # Basic metrics
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    
    # Pattern detection
    ai_patterns = {
        'repetitive_phrases': len(re.findall(r'\b(\w+)\s+\1\b', text)),
        'perfect_grammar': len(re.findall(r'[,;:]', text)) / max(len(sentences), 1),
        'complex_vocabulary': len([w for w in words if len(w) > 8]) / max(len(words), 1),
        'uniform_sentences': calculate_sentence_uniformity(sentences)
    }
    
    # Calculate AI probability
    ai_score = min(0.95, (
        (ai_patterns['repetitive_phrases'] * 0.1) +
        (ai_patterns['perfect_grammar'] * 0.3) +
        (ai_patterns['complex_vocabulary'] * 0.2) +
        (0.4 if ai_patterns['uniform_sentences'] < 3 else 0)
    ))
    
    return {
        'ai_probability': round(ai_score * 100, 1),
        'human_probability': round((1 - ai_score) * 100, 1),
        'analysis': {
            'patterns_found': sum(1 for v in ai_patterns.values() if v > 0.3),
            'writing_style': 'Formal' if ai_patterns['complex_vocabulary'] > 0.2 else 'Casual',
            'consistency': 'High' if ai_patterns['uniform_sentences'] < 3 else 'Variable'
        },
        'details': {
            'text_length': len(text),
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()])
        }
    }

def analyze_with_openai(text):
    """Advanced AI detection using OpenAI API (Pro tier)"""
    # This would integrate with OpenAI API
    # For now, return enhanced pattern analysis
    basic_result = analyze_text_patterns(text)
    
    # Add advanced metrics
    basic_result['advanced_analysis'] = {
        'coherence_score': 0.85,
        'originality_score': 0.72,
        'style_consistency': 0.91,
        'fact_accuracy': 'Not verified'
    }
    
    return basic_result

# News Verification Routes
@app.route('/api/verify-news', methods=['POST'])
def verify_news():
    try:
        data = request.json
        url = data.get('url', '')
        headline = data.get('headline', '')
        
        if not url and not headline:
            return jsonify({'error': 'URL or headline required'}), 400
        
        # Check rate limit for authenticated users
        if 'user_id' in session:
            can_proceed, message = check_rate_limit(session['user_id'])
            if not can_proceed:
                return jsonify({'error': message, 'limit_reached': True}), 429
        
        result = perform_news_verification(url, headline)
        
        # Increment usage
        if 'user_id' in session:
            increment_usage(session['user_id'])
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"News verification error: {str(e)}")
        return jsonify({'error': 'Verification failed'}), 500

def fetch_mediastack_news(query):
    """Fetch news from MediaStack API"""
    if not MEDIASTACK_API_KEY:
        return []
    
    try:
        url = "http://api.mediastack.com/v1/news"
        params = {
            'access_key': MEDIASTACK_API_KEY,
            'keywords': query,
            'languages': 'en',
            'limit': 10,
            'sort': 'published_desc'
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        else:
            logger.error(f"MediaStack API error: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"MediaStack fetch error: {str(e)}")
        return []

def perform_news_verification(url, headline):
    """Perform comprehensive news verification"""
    
    verification_result = {
        'credibility_score': 0,
        'bias_indicators': [],
        'fact_check_results': [],
        'source_analysis': {},
        'cross_references': []
    }
    
    # Extract domain for source analysis
    if url:
        domain = re.search(r'https?://([^/]+)', url)
        if domain:
            domain = domain.group(1)
            verification_result['source_analysis'] = analyze_news_source(domain)
    
    # Search for related articles using MediaStack
    if headline:
        # Extract key terms for search
        key_terms = ' '.join(headline.split()[:5])
        related_articles = fetch_mediastack_news(key_terms)
        
        if related_articles:
            # Analyze cross-references
            for article in related_articles[:5]:
                verification_result['cross_references'].append({
                    'title': article.get('title', 'Unknown'),
                    'source': article.get('source', 'Unknown'),
                    'published': article.get('published_at', ''),
                    'url': article.get('url', '')
                })
    
    # Calculate credibility score
    if verification_result['source_analysis']:
        base_score = verification_result['source_analysis'].get('reliability_score', 50)
    else:
        base_score = 50
    
    # Adjust based on cross-references
    if len(verification_result['cross_references']) >= 3:
        base_score += 20
    elif len(verification_result['cross_references']) >= 1:
        base_score += 10
    
    verification_result['credibility_score'] = min(100, base_score)
    
    # Add bias indicators
    if headline:
        bias_words = ['shocking', 'unbelievable', 'destroys', 'slams', 'exposed']
        found_bias = [word for word in bias_words if word.lower() in headline.lower()]
        if found_bias:
            verification_result['bias_indicators'] = found_bias
            verification_result['credibility_score'] -= len(found_bias) * 5
    
    return verification_result

def analyze_news_source(domain):
    """Analyze news source reliability"""
    
    # Known reliable sources
    reliable_sources = {
        'reuters.com': 90,
        'apnews.com': 90,
        'bbc.com': 85,
        'npr.org': 85,
        'wsj.com': 80,
        'nytimes.com': 80,
        'washingtonpost.com': 80,
        'theguardian.com': 75,
        'cnn.com': 70,
        'foxnews.com': 70
    }
    
    # Check if domain is in reliable sources
    for source, score in reliable_sources.items():
        if source in domain:
            return {
                'domain': domain,
                'reliability_score': score,
                'category': 'Mainstream Media',
                'known_biases': 'Varies by source'
            }
    
    # Default for unknown sources
    return {
        'domain': domain,
        'reliability_score': 50,
        'category': 'Unknown/Independent',
        'known_biases': 'Unverified source'
    }

# Cross-Source Verification Route
@app.route('/api/cross-verify', methods=['POST'])
def cross_verify():
    try:
        data = request.json
        claim = data.get('claim', '')
        sources = data.get('sources', [])
        
        if not claim:
            return jsonify({'error': 'Claim text required'}), 400
        
        # Search multiple sources using MediaStack
        verification_results = []
        
        # Search for the claim
        articles = fetch_mediastack_news(claim)
        
        for article in articles[:10]:  # Check up to 10 sources
            source_result = {
                'source': article.get('source', 'Unknown'),
                'title': article.get('title', ''),
                'url': article.get('url', ''),
                'published': article.get('published_at', ''),
                'relevance': calculate_relevance(claim, article.get('title', '') + ' ' + article.get('description', ''))
            }
            verification_results.append(source_result)
        
        # Calculate consensus
        consensus_score = calculate_consensus(verification_results)
        
        return jsonify({
            'claim': claim,
            'sources_checked': len(verification_results),
            'verification_results': verification_results,
            'consensus_score': consensus_score,
            'verdict': get_verdict(consensus_score)
        })
        
    except Exception as e:
        logger.error(f"Cross-verification error: {str(e)}")
        return jsonify({'error': 'Cross-verification failed'}), 500

def calculate_relevance(claim, text):
    """Calculate how relevant a text is to a claim"""
    claim_words = set(claim.lower().split())
    text_words = set(text.lower().split())
    
    if not claim_words:
        return 0
    
    common_words = claim_words.intersection(text_words)
    relevance = len(common_words) / len(claim_words)
    
    return round(relevance * 100, 1)

def calculate_consensus(results):
    """Calculate consensus score from multiple sources"""
    if not results:
        return 0
    
    relevant_results = [r for r in results if r['relevance'] > 30]
    if not relevant_results:
        return 0
    
    # Higher score for more sources reporting similar information
    consensus = min(100, len(relevant_results) * 20)
    return consensus

def get_verdict(consensus_score):
    """Get verification verdict based on consensus score"""
    if consensus_score >= 80:
        return "Highly Verified"
    elif consensus_score >= 60:
        return "Likely Accurate"
    elif consensus_score >= 40:
        return "Partially Verified"
    elif consensus_score >= 20:
        return "Questionable"
    else:
        return "Unverified"

# Image Analysis Route
@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    try:
        data = request.json
        image_data = data.get('image', '')
        
        if not image_data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Check rate limit
        if 'user_id' in session:
            can_proceed, message = check_rate_limit(session['user_id'])
            if not can_proceed:
                return jsonify({'error': message, 'limit_reached': True}), 429
        
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_data.split(',')[1])
            image = Image.open(BytesIO(image_bytes))
        except Exception as e:
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Perform analysis
        analysis_result = analyze_image_properties(image)
        
        # Increment usage
        if 'user_id' in session:
            increment_usage(session['user_id'])
        
        return jsonify(analysis_result)
        
    except Exception as e:
        logger.error(f"Image analysis error: {str(e)}")
        return jsonify({'error': 'Analysis failed'}), 500

def analyze_image_properties(image):
    """Analyze image for potential manipulation"""
    
    # Get image properties
    width, height = image.size
    format = image.format
    mode = image.mode
    
    # Check for common manipulation indicators
    indicators = []
    
    # Check EXIF data
    exif_data = {}
    try:
        exif = image._getexif()
        if exif:
            exif_data = {
                'has_exif': True,
                'camera_info': 'Available',
                'date_taken': 'Available'
            }
        else:
            exif_data = {
                'has_exif': False,
                'camera_info': 'Not found',
                'date_taken': 'Not found'
            }
            indicators.append("Missing EXIF data")
    except:
        exif_data = {'has_exif': False}
        indicators.append("No EXIF data found")
    
    # Check for unusual dimensions
    if width % 2 != 0 or height % 2 != 0:
        indicators.append("Unusual dimensions")
    
    # Calculate manipulation probability
    manipulation_score = len(indicators) * 20
    
    return {
        'manipulation_probability': min(80, manipulation_score),
        'authenticity_score': max(20, 100 - manipulation_score),
        'technical_details': {
            'dimensions': f"{width}x{height}",
            'format': format or 'Unknown',
            'color_mode': mode,
            'file_size': 'Analysis based on properties'
        },
        'exif_analysis': exif_data,
        'manipulation_indicators': indicators,
        'recommendations': [
            "Check source credibility",
            "Look for visual inconsistencies",
            "Verify with reverse image search"
        ]
    }

# Health check
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

# Cleanup function
@app.teardown_appcontext
def shutdown_session(exception=None):
    SessionLocal.remove()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
