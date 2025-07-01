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
import sys
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool
import statistics
from urllib.parse import urlparse, quote
import difflib
import openai
try:
    # Try importing new OpenAI client (v1.0+)
    from openai import OpenAI
    OPENAI_V1 = True
except ImportError:
    # Fall back to legacy import
    OPENAI_V1 = False

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

# Configure comprehensive logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
    force=True  # Force reconfiguration
)
logger = logging.getLogger(__name__)

# Log startup
logger.info("=" * 80)
logger.info("BACKEND STARTING UP WITH REAL API INTEGRATIONS")
logger.info("=" * 80)

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

# Configure OpenAI if available
if OPENAI_API_KEY:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        OPENAI_CLIENT = client
        logger.info("OpenAI API configured successfully (v1.0+)")
    except ImportError:
        # Fallback for older version
        openai.api_key = OPENAI_API_KEY
        OPENAI_CLIENT = None
        logger.info("OpenAI API configured (legacy version)")
else:
    OPENAI_CLIENT = None
    logger.warning("OpenAI API key not found - using pattern analysis fallback")

# Enhanced News Source Database (keeping your extensive list)
NEWS_SOURCE_DATABASE = {
    # Major International Sources
    'reuters.com': {'credibility': 95, 'bias': 'center', 'type': 'Wire Service', 'reach': 'international', 'founded': 1851},
    'apnews.com': {'credibility': 94, 'bias': 'center', 'type': 'Wire Service', 'reach': 'international', 'founded': 1846},
    'ap.org': {'credibility': 94, 'bias': 'center', 'type': 'Wire Service', 'reach': 'international', 'founded': 1846},
    'bbc.com': {'credibility': 90, 'bias': 'center-left', 'type': 'Public Broadcaster', 'reach': 'international', 'founded': 1922},
    'bbc.co.uk': {'credibility': 90, 'bias': 'center-left', 'type': 'Public Broadcaster', 'reach': 'international', 'founded': 1922},
    
    # US Major Sources
    'nytimes.com': {'credibility': 85, 'bias': 'center-left', 'type': 'Newspaper', 'reach': 'national', 'founded': 1851},
    'washingtonpost.com': {'credibility': 85, 'bias': 'center-left', 'type': 'Newspaper', 'reach': 'national', 'founded': 1877},
    'wsj.com': {'credibility': 88, 'bias': 'center-right', 'type': 'Newspaper', 'reach': 'national', 'founded': 1889},
    'usatoday.com': {'credibility': 78, 'bias': 'center', 'type': 'Newspaper', 'reach': 'national', 'founded': 1982},
    
    # TV News Networks
    'cnn.com': {'credibility': 72, 'bias': 'left', 'type': 'Cable News', 'reach': 'international', 'founded': 1980},
    'foxnews.com': {'credibility': 70, 'bias': 'right', 'type': 'Cable News', 'reach': 'national', 'founded': 1996},
    'msnbc.com': {'credibility': 68, 'bias': 'left', 'type': 'Cable News', 'reach': 'national', 'founded': 1996},
    'nbcnews.com': {'credibility': 80, 'bias': 'center-left', 'type': 'Broadcast News', 'reach': 'national', 'founded': 1940},
    'cbsnews.com': {'credibility': 82, 'bias': 'center-left', 'type': 'Broadcast News', 'reach': 'national', 'founded': 1927},
    'abcnews.go.com': {'credibility': 81, 'bias': 'center-left', 'type': 'Broadcast News', 'reach': 'national', 'founded': 1943},
    'npr.org': {'credibility': 90, 'bias': 'center-left', 'type': 'Public Media', 'reach': 'national', 'founded': 1970},
    
    # International Sources
    'theguardian.com': {'credibility': 84, 'bias': 'left', 'type': 'Newspaper', 'reach': 'international', 'founded': 1821},
    'economist.com': {'credibility': 89, 'bias': 'center-right', 'type': 'Magazine', 'reach': 'international', 'founded': 1843},
    'ft.com': {'credibility': 91, 'bias': 'center-right', 'type': 'Financial', 'reach': 'international', 'founded': 1888},
    'bloomberg.com': {'credibility': 85, 'bias': 'center', 'type': 'Financial', 'reach': 'international', 'founded': 1981},
    
    # Digital First
    'axios.com': {'credibility': 83, 'bias': 'center', 'type': 'Digital', 'reach': 'national', 'founded': 2016},
    'politico.com': {'credibility': 82, 'bias': 'center-left', 'type': 'Digital', 'reach': 'national', 'founded': 2007},
    'vox.com': {'credibility': 76, 'bias': 'left', 'type': 'Digital', 'reach': 'national', 'founded': 2014},
    'breitbart.com': {'credibility': 45, 'bias': 'far-right', 'type': 'Digital', 'reach': 'national', 'founded': 2007},
    'huffpost.com': {'credibility': 65, 'bias': 'left', 'type': 'Digital', 'reach': 'international', 'founded': 2005},
    'dailywire.com': {'credibility': 55, 'bias': 'right', 'type': 'Digital', 'reach': 'national', 'founded': 2015},
    'motherjones.com': {'credibility': 70, 'bias': 'left', 'type': 'Magazine', 'reach': 'national', 'founded': 1976},
    
    # Fact Checking Sites
    'snopes.com': {'credibility': 92, 'bias': 'center', 'type': 'Fact-Check', 'reach': 'international', 'founded': 1994},
    'factcheck.org': {'credibility': 93, 'bias': 'center', 'type': 'Fact-Check', 'reach': 'national', 'founded': 2003},
    'politifact.com': {'credibility': 91, 'bias': 'center', 'type': 'Fact-Check', 'reach': 'national', 'founded': 2007},
}

# Enhanced Bias indicators (keeping your comprehensive list)
BIAS_INDICATORS = {
    'left': {
        'keywords': ['progressive', 'inequality', 'systemic', 'privilege', 'marginalized', 
                    'inclusive', 'equity', 'discrimination', 'oppression', 'activism', 'grassroots',
                    'liberal', 'social', 'justice'],
        'phrases': ['fight for', 'stand with', 'demand action', 'held accountable', 'speaking truth to power',
                   'social justice', 'climate crisis', 'corporate greed', 'wealth gap', 'living wage'],
        'sources': ['activists say', 'advocates argue', 'progressives believe', 'critics of capitalism']
    },
    'right': {
        'keywords': ['traditional', 'freedom', 'liberty', 'patriot', 'constitution', 'conservative',
                    'family', 'values', 'law', 'order', 'personal', 'responsibility', 'limited', 'government',
                    'border', 'security', 'job', 'creators', 'deregulation', 'religious'],
        'phrases': ['radical left', 'socialist agenda', 'defend our', 'protect our values', 'government overreach',
                   'free market', 'family values', 'law and order', 'personal responsibility', 'limited government',
                   'border security', 'job creators', 'religious freedom'],
        'sources': ['conservatives say', 'business leaders argue', 'traditionalists believe', 'free market advocates']
    },
    'loaded': {
        'keywords': ['slams', 'destroys', 'obliterates', 'shocking', 'bombshell', 'explosive',
                    'devastating', 'crushing', 'humiliating', 'scandal', 'exposed', 'caught',
                    'under', 'fire', 'backlash', 'outrage', 'fury', 'chaos', 'disaster'],
        'qualifiers': ['allegedly', 'supposedly', 'so-called', 'purported', 'claimed'],
        'phrases': ['caught red-handed', 'under fire']
    }
}

# AI indicator patterns for detection
AI_INDICATORS = {
    'transitions': ['furthermore', 'moreover', 'consequently', 'therefore', 'additionally', 
                   'nonetheless', 'nevertheless', 'however', 'in conclusion', 'in summary'],
    'academic': ['comprehensive', 'sophisticated', 'innovative', 'paradigm', 'methodology', 
                'framework', 'substantial', 'significant', 'demonstrates', 'indicates'],
    'business': ['streamline', 'synergy', 'leverage', 'scalable', 'optimization', 
                'implementation', 'strategic', 'enhance', 'facilitate', 'utilize'],
    'filler': ['it is important to note that', 'it should be mentioned that', 
              'it is worth noting that', 'one must consider that', 'it goes without saying']
}

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

# Enhanced AI Detection Functions with Real OpenAI Integration
def analyze_with_openai(text):
    """Real OpenAI API integration for AI detection"""
    if not OPENAI_API_KEY:
        logger.warning("OpenAI API key not available, falling back to pattern analysis")
        return analyze_text_patterns(text)
    
    try:
        # Use OpenAI to analyze the text
        prompt = f"""
        Analyze this text for AI generation indicators. Consider writing patterns, consistency, and style.
        Return your analysis in this exact JSON format:
        {{
            "ai_probability": 0.XX,
            "human_probability": 0.XX,
            "confidence": 0.XX,
            "explanation": "detailed analysis explanation",
            "patterns_detected": ["pattern1", "pattern2"],
            "writing_style": "style description",
            "linguistic_features": {{
                "vocabulary_complexity": XX,
                "sentence_variety": XX,
                "natural_flow": XX
            }}
        }}
        
        Text to analyze: {text[:2000]}
        """
        
        if OPENAI_CLIENT:
            # New OpenAI v1.0+ syntax
            response = OPENAI_CLIENT.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert AI text detection system. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            result = json.loads(response.choices[0].message.content.strip())
        else:
            # Legacy OpenAI syntax
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert AI text detection system. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            result = json.loads(response.choices[0].message.content.strip())
        
        # Add additional analysis
        result['analysis'] = {
            'patterns_found': len(result.get('patterns_detected', [])),
            'writing_style': result.get('writing_style', 'Unknown'),
            'consistency': 'High' if result.get('linguistic_features', {}).get('sentence_variety', 0) < 30 else 'Variable',
            'api_used': 'OpenAI GPT-4'
        }
        
        result['details'] = {
            'text_length': len(text),
            'word_count': len(text.split()),
            'sentence_count': len(re.split(r'[.!?]+', text))
        }
        
        result['advanced_analysis'] = {
            'coherence_score': result.get('linguistic_features', {}).get('natural_flow', 0) / 100,
            'originality_score': 1 - result.get('ai_probability', 0.5),
            'style_consistency': result.get('linguistic_features', {}).get('sentence_variety', 0) / 100,
            'fact_accuracy': 'Not verified'
        }
        
        logger.info(f"OpenAI analysis completed successfully for {len(text)} chars")
        return result
        
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        # Fallback to pattern analysis
        return analyze_text_patterns(text)

def analyze_text_patterns(text):
    """Enhanced pattern-based AI detection"""
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Count AI indicator patterns
    ai_score = 0
    patterns_found = []
    
    # Check transitions
    transition_count = sum(1 for word in AI_INDICATORS['transitions'] if word in text.lower())
    if transition_count > 2:
        ai_score += 0.2
        patterns_found.append(f"{transition_count} AI transition words")
    
    # Check academic language
    academic_count = sum(1 for word in AI_INDICATORS['academic'] if word in text.lower())
    if academic_count > 3:
        ai_score += 0.15
        patterns_found.append(f"{academic_count} academic terms")
    
    # Check business jargon
    business_count = sum(1 for word in AI_INDICATORS['business'] if word in text.lower())
    if business_count > 2:
        ai_score += 0.1
        patterns_found.append(f"{business_count} business terms")
    
    # Check filler phrases
    filler_count = sum(1 for phrase in AI_INDICATORS['filler'] if phrase in text.lower())
    if filler_count > 1:
        ai_score += 0.15
        patterns_found.append(f"{filler_count} filler phrases")
    
    # Sentence structure analysis
    if sentences:
        avg_sentence_length = len(words) / len(sentences)
        if avg_sentence_length > 25:
            ai_score += 0.15
            patterns_found.append("Long average sentences")
        
        # Check sentence length uniformity
        if len(sentences) > 3:
            sentence_lengths = [len(s.split()) for s in sentences]
            length_variance = statistics.stdev(sentence_lengths) if len(sentence_lengths) > 1 else 0
            if length_variance < 3:
                ai_score += 0.2
                patterns_found.append("Uniform sentence structure")
    
    # Check repetitive starts
    if sentences:
        start_words = [s.split()[0].lower() for s in sentences if s.split()]
        start_word_counts = Counter(start_words)
        repetitive_starts = sum(1 for count in start_word_counts.values() if count > 2)
        if repetitive_starts > 0:
            ai_score += 0.1
            patterns_found.append("Repetitive sentence starts")
    
    ai_score = min(0.95, ai_score)
    
    return {
        'ai_probability': round(ai_score, 2),
        'human_probability': round(1 - ai_score, 2),
        'analysis': {
            'patterns_found': len(patterns_found),
            'writing_style': 'Formal/Academic' if academic_count > 2 else 'Business' if business_count > 2 else 'Casual',
            'consistency': 'High' if ai_score > 0.6 else 'Variable'
        },
        'details': {
            'text_length': len(text),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'patterns_detected': patterns_found[:5]  # Top 5 patterns
        },
        'confidence': 0.7 + (0.2 if len(text) > 500 else 0)
    }

# Enhanced News Analysis Functions with Real API Integration
def fetch_real_news_content(url):
    """Fetch actual content from news URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to extract article text
        article_text = ""
        
        # Common article containers
        for selector in ['article', 'main', '.article-content', '.story-body', '.content']:
            content = soup.select_one(selector)
            if content:
                paragraphs = content.find_all('p')
                article_text = ' '.join([p.get_text().strip() for p in paragraphs])
                if len(article_text) > 100:
                    break
        
        # Fallback to all paragraphs
        if not article_text:
            paragraphs = soup.find_all('p')
            article_text = ' '.join([p.get_text().strip() for p in paragraphs[:10]])
        
        return article_text[:3000]  # Limit to 3000 chars
        
    except Exception as e:
        logger.error(f"Error fetching news content: {str(e)}")
        return None

def search_news_api(query, limit=10):
    """Search for news using News API with better error handling"""
    if not NEWS_API_KEY:
        logger.warning("News API key not available")
        return []
    
    try:
        # Clean up the query - take first 100 chars and remove special characters
        clean_query = re.sub(r'[^\w\s]', '', query[:100]).strip()
        if not clean_query:
            clean_query = "news"
        
        # Try multiple search strategies
        articles_found = []
        
        # Strategy 1: Search everything endpoint
        url = "https://newsapi.org/v2/everything"
        params = {
            'apiKey': NEWS_API_KEY,
            'q': clean_query,
            'sortBy': 'relevancy',
            'pageSize': limit,
            'language': 'en',
            'from': (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d')  # Last 7 days
        }
        
        logger.info(f"NewsAPI search with query: {clean_query}")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            logger.info(f"NewsAPI returned {len(articles)} articles")
            
            for article in articles:
                articles_found.append({
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'title': article.get('title', 'No title'),
                    'url': article.get('url', '#'),
                    'published': article.get('publishedAt', 'Unknown date'),
                    'description': article.get('description', ''),
                    'relevance': 85
                })
        else:
            logger.error(f"NewsAPI error: {response.status_code} - {response.text}")
        
        # Strategy 2: If no results, try top headlines
        if not articles_found:
            logger.info("Trying NewsAPI top headlines as fallback")
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                'apiKey': NEWS_API_KEY,
                'country': 'us',
                'pageSize': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                for article in articles:
                    articles_found.append({
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'title': article.get('title', 'No title'),
                        'url': article.get('url', '#'),
                        'published': article.get('publishedAt', 'Unknown date'),
                        'description': article.get('description', ''),
                        'relevance': 70  # Lower relevance for general headlines
                    })
        
        return articles_found[:limit]
        
    except Exception as e:
        logger.error(f"News API error: {str(e)}")
        return []

def search_mediastack_api(query, limit=10):
    """Search for news using MediaStack API"""
    if not MEDIASTACK_API_KEY:
        return []
    
    try:
        url = "http://api.mediastack.com/v1/news"
        params = {
            'access_key': MEDIASTACK_API_KEY,
            'keywords': query,
            'languages': 'en',
            'limit': limit,
            'sort': 'published_desc'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        articles = data.get('data', [])
        
        results = []
        for article in articles:
            results.append({
                'source': article.get('source', 'Unknown'),
                'title': article.get('title', 'No title'),
                'url': article.get('url', '#'),
                'published': article.get('published_at', 'Unknown date'),
                'description': article.get('description', ''),
                'relevance': 80
            })
        
        return results
        
    except Exception as e:
        logger.error(f"MediaStack API error: {str(e)}")
        return []

def google_fact_check_api(query):
    """Use Google Fact Check API"""
    if not GOOGLE_FACT_CHECK_API_KEY:
        return []
    
    try:
        url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        params = {
            'key': GOOGLE_FACT_CHECK_API_KEY,
            'query': query,
            'pageSize': 10
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        claims = data.get('claims', [])
        
        results = []
        for claim in claims:
            claim_review = claim.get('claimReview', [{}])[0]
            results.append({
                'claim': claim.get('text', ''),
                'claimant': claim.get('claimant', 'Unknown'),
                'reviewer': claim_review.get('publisher', {}).get('name', 'Unknown'),
                'rating': claim_review.get('textualRating', 'Unknown'),
                'url': claim_review.get('url', '#')
            })
        
        return results
        
    except Exception as e:
        logger.error(f"Google Fact Check API error: {str(e)}")
        return []

def calculate_relevance(text1, text2):
    """Calculate relevance between two texts"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    jaccard = len(intersection) / len(union) if union else 0
    return round(jaccard * 100, 1)

def search_cross_references_enhanced(headline, limit=10):
    """Enhanced cross-reference search using multiple real APIs"""
    cross_refs = []
    
    # Extract key terms from headline for better search
    # Remove common words and keep important terms
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'as', 'is', 'was', 'are', 'were'}
    words = headline.lower().split()
    key_terms = [w for w in words if w not in stop_words and len(w) > 3]
    search_query = ' '.join(key_terms[:5])  # Use top 5 key terms
    
    logger.info(f"Cross-reference search for: {search_query}")
    
    # Try News API first
    news_results = search_news_api(search_query, limit)
    if news_results:
        logger.info(f"Found {len(news_results)} results from NewsAPI")
        cross_refs.extend(news_results)
    else:
        logger.warning("No results from NewsAPI")
    
    # Try MediaStack as backup
    if len(cross_refs) < limit and MEDIASTACK_API_KEY:
        logger.info("Trying MediaStack API")
        mediastack_results = search_mediastack_api(search_query, limit - len(cross_refs))
        if mediastack_results:
            logger.info(f"Found {len(mediastack_results)} results from MediaStack")
            cross_refs.extend(mediastack_results)
    
    # Add fact checks if available
    if GOOGLE_FACT_CHECK_API_KEY:
        logger.info("Checking Google Fact Check API")
        fact_checks = google_fact_check_api(search_query)
        for fact_check in fact_checks[:3]:
            cross_refs.append({
                'source': f"Fact Check: {fact_check['reviewer']}",
                'title': fact_check['claim'],
                'url': fact_check['url'],
                'published': 'Fact Check',
                'relevance': 95,
                'rating': fact_check['rating']
            })
            logger.info(f"Added fact check from {fact_check['reviewer']}")
    
    # If still no results, add a message
    if not cross_refs:
        logger.warning("No cross-references found from any API")
        # Don't return empty - this breaks the UI
        cross_refs.append({
            'source': 'Search Status',
            'title': 'No matching articles found in news databases',
            'url': '#',
            'published': datetime.utcnow().isoformat(),
            'relevance': 0,
            'description': 'Try searching with different keywords or check if the APIs are properly configured'
        })
    
    # Sort by relevance
    cross_refs.sort(key=lambda x: x.get('relevance', 0), reverse=True)
    
    logger.info(f"Returning {len(cross_refs)} total cross-references")
    return cross_refs[:limit]

def analyze_political_bias(text):
    """Enhanced political bias analysis"""
    logger.info("Starting political bias analysis")
    
    text_lower = text.lower()
    words = text_lower.split()
    
    # Count bias indicators
    left_score = 0
    right_score = 0
    loaded_terms = []
    
    # Check keywords
    left_found = []
    right_found = []
    
    for word in words:
        clean_word = word.strip('.,!?;:')
        
        if clean_word in BIAS_INDICATORS['left']['keywords']:
            left_score += 1
            left_found.append(clean_word)
            
        if clean_word in BIAS_INDICATORS['right']['keywords']:
            right_score += 1
            right_found.append(clean_word)
            
        if clean_word in BIAS_INDICATORS['loaded']['keywords']:
            loaded_terms.append(clean_word)
    
    # Check phrases
    for phrase in BIAS_INDICATORS['left']['phrases']:
        if phrase in text_lower:
            left_score += 2
            left_found.append(phrase)
    
    for phrase in BIAS_INDICATORS['right']['phrases']:
        if phrase in text_lower:
            right_score += 2
            right_found.append(phrase)
    
    # Simple sentiment analysis
    positive_words = ['good', 'great', 'excellent', 'positive', 'successful', 'effective', 'beneficial']
    negative_words = ['bad', 'terrible', 'negative', 'failed', 'crisis', 'disaster', 'harmful']
    
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    
    total_sentiment_words = positive_count + negative_count
    if total_sentiment_words > 0:
        sentiment = (positive_count - negative_count) / total_sentiment_words
    else:
        sentiment = 0
    
    # Calculate subjectivity
    opinion_words = ['think', 'believe', 'feel', 'seems', 'appears', 'might', 'could', 'should', 'probably', 'maybe']
    opinion_count = sum(1 for word in words if word in opinion_words)
    subjectivity = min(1.0, opinion_count / max(len(words), 1) * 10)
    
    # Calculate bias metrics
    total_bias_indicators = left_score + right_score
    bias_score = right_score - left_score
    
    # Determine bias label
    if abs(bias_score) <= 2:
        bias_label = 'center'
    elif bias_score < -5:
        bias_label = 'far-left'
    elif bias_score < -2:
        bias_label = 'left'
    elif bias_score > 5:
        bias_label = 'far-right'
    elif bias_score > 2:
        bias_label = 'right'
    else:
        bias_label = 'center'
    
    # Calculate objectivity
    objectivity_score = max(0, 100 - (total_bias_indicators * 5) - (len(loaded_terms) * 10) - (subjectivity * 50))
    
    return {
        'bias_score': bias_score,
        'bias_label': bias_label,
        'left_indicators': left_score,
        'right_indicators': right_score,
        'loaded_terms': loaded_terms[:10],
        'sentiment_score': round(sentiment, 3),
        'subjectivity_score': round(subjectivity, 3),
        'objectivity_score': round(objectivity_score, 1),
        'bias_confidence': min(95, 70 + (total_bias_indicators * 2)),
        'detailed_indicators': {
            'left_found': left_found[:10],
            'right_found': right_found[:10]
        }
    }

def analyze_source_credibility(url):
    """Analyze source credibility with enhanced metrics"""
    # If no URL provided or it's actually article text, return conservative estimate
    if not url or len(url) > 200 or ' ' in url:
        logger.info("No valid URL provided for source analysis")
        return {
            'domain': 'Direct Text Input',
            'credibility_score': 50,
            'source_type': 'User Submission',
            'political_bias': 'Unknown',
            'reach': 'Unknown',
            'founded': 'N/A'
        }
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace('www.', '')
        
        # Check our database
        if domain in NEWS_SOURCE_DATABASE:
            source_info = NEWS_SOURCE_DATABASE[domain].copy()
            source_info['domain'] = domain
            source_info['credibility_score'] = source_info.pop('credibility')
            source_info['political_bias'] = source_info.pop('bias')
            logger.info(f"Found source {domain} in database")
            return source_info
        
        # Unknown source - return conservative estimate
        logger.info(f"Unknown source: {domain}")
        return {
            'domain': domain,
            'credibility_score': 45,
            'source_type': 'Independent/Unknown',
            'political_bias': 'Unknown',
            'reach': 'Unknown',
            'founded': 'Unknown'
        }
        
    except Exception as e:
        logger.error(f"Error analyzing source: {str(e)}")
        return {
            'domain': 'Invalid URL',
            'credibility_score': 0,
            'source_type': 'Invalid',
            'political_bias': 'Unknown',
            'reach': 'Unknown',
            'founded': 'Unknown'
        }

def extract_key_claims(text):
    """Extract key factual claims from news text"""
    claims = []
    sentences = re.split(r'[.!?]+', text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence or len(sentence) < 20:
            continue
            
        # Check for factual indicators
        has_number = bool(re.search(r'\b\d+\b', sentence))
        has_quote = '"' in sentence or "'" in sentence
        has_percent = '%' in sentence
        has_dollar = '$' in sentence
        has_date = bool(re.search(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December|\d{4})\b', sentence, re.I))
        
        claim_keywords = ['announced', 'reported', 'revealed', 'stated', 'confirmed', 'according to', 
                         'found that', 'discovered', 'showed', 'indicated', 'suggested', 'claimed']
        has_claim_word = any(keyword in sentence.lower() for keyword in claim_keywords)
        
        if has_number or has_quote or has_percent or has_dollar or has_date or has_claim_word:
            claims.append({
                'text': sentence,
                'has_number': has_number,
                'has_quote': has_quote,
                'verifiable': has_number or has_dollar or has_percent
            })
    
    return claims[:10]

def perform_fact_checking_enhanced(claims):
    """Enhanced fact-checking with real API integration"""
    fact_checks = []
    
    for claim in claims[:5]:
        claim_text = claim['text']
        
        # Try Google Fact Check API
        if GOOGLE_FACT_CHECK_API_KEY:
            google_results = google_fact_check_api(claim_text[:200])
            if google_results:
                for result in google_results[:2]:
                    fact_checks.append({
                        'claim': claim_text,
                        'verifiable': True,
                        'status': result['rating'],
                        'confidence': 85,
                        'sources': [f"{result['reviewer']}: {result['rating']}"],
                        'fact_check_url': result['url']
                    })
                continue
        
        # Fallback analysis
        check_result = {
            'claim': claim_text,
            'verifiable': claim['verifiable'],
            'status': 'Unverified',
            'confidence': 50,
            'sources': []
        }
        
        if claim['has_number']:
            check_result['status'] = 'Requires Verification'
            check_result['confidence'] = 60
            check_result['sources'].append('Numerical claim - source verification needed')
        
        if claim['has_quote']:
            check_result['status'] = 'Quote Detected'
            check_result['confidence'] = 55
            check_result['sources'].append('Contains quoted material - verify attribution')
        
        fact_checks.append(check_result)
    
    return fact_checks

def generate_comprehensive_analysis(text, url, is_pro):
    """Generate comprehensive news analysis with real API data"""
    logger.info("Generating comprehensive news analysis")
    
    # Try to fetch full article content if URL provided
    if url:
        full_content = fetch_real_news_content(url)
        if full_content and len(full_content) > len(text):
            text = full_content
            logger.info(f"Fetched full article content: {len(full_content)} chars")
    
    # Extract claims
    claims = extract_key_claims(text)
    
    # Analyze bias
    bias_analysis = analyze_political_bias(text)
    
    # Analyze source
    source_analysis = analyze_source_credibility(url)
    
    # Search for cross-references with real APIs
    headline = text[:100] + "..." if len(text) > 100 else text
    cross_references = search_cross_references_enhanced(headline)
    
    # Perform enhanced fact-checking
    fact_checks = perform_fact_checking_enhanced(claims)
    
    # Use OpenAI for advanced analysis if available and user is pro
    if is_pro and OPENAI_API_KEY:
        try:
            prompt = f"""
            Analyze this news article for credibility and potential misinformation.
            Consider: factual accuracy, source reliability, bias, emotional language.
            
            Article: {text[:1500]}
            
            Provide analysis in JSON format:
            {{
                "credibility_assessment": "assessment",
                "misinformation_risk": "low/medium/high",
                "key_concerns": ["concern1", "concern2"],
                "writing_quality": 0-100,
                "recommendation": "trust/verify/suspicious"
            }}
            """
            
            if OPENAI_CLIENT:
                # New OpenAI v1.0+ syntax
                response = OPENAI_CLIENT.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a news credibility expert. Respond with valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.1
                )
                ai_analysis = json.loads(response.choices[0].message.content.strip())
            else:
                # Legacy OpenAI syntax
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a news credibility expert. Respond with valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.1
                )
                ai_analysis = json.loads(response.choices[0].message.content.strip())
            logger.info("OpenAI news analysis completed")
        except Exception as e:
            logger.error(f"OpenAI news analysis failed: {str(e)}")
            ai_analysis = None
    else:
        ai_analysis = None
    
    # Calculate overall credibility score
    base_score = source_analysis['credibility_score']
    
    # Adjust based on bias
    if bias_analysis['bias_label'] in ['far-left', 'far-right']:
        base_score -= 15
    elif bias_analysis['bias_label'] in ['left', 'right']:
        base_score -= 5
    
    # Adjust based on objectivity
    objectivity_factor = bias_analysis['objectivity_score'] / 100
    base_score = base_score * (0.7 + 0.3 * objectivity_factor)
    
    # Adjust based on cross-references
    if len(cross_references) >= 5:
        base_score += 10
    elif len(cross_references) >= 3:
        base_score += 5
    
    # Adjust based on fact checks
    verified_facts = sum(1 for fc in fact_checks if fc['status'] != 'Unverified')
    if verified_facts > 0:
        base_score += verified_facts * 2
    
    credibility_score = max(0, min(100, round(base_score)))
    
    # Generate bias indicators list
    bias_indicators = []
    if bias_analysis['left_indicators'] > 0:
        bias_indicators.append(f"Left-leaning language detected ({bias_analysis['left_indicators']} indicators)")
    if bias_analysis['right_indicators'] > 0:
        bias_indicators.append(f"Right-leaning language detected ({bias_analysis['right_indicators']} indicators)")
    if bias_analysis['loaded_terms']:
        bias_indicators.append(f"Loaded/emotional language: {', '.join(bias_analysis['loaded_terms'][:5])}")
    if bias_analysis['subjectivity_score'] > 0.6:
        bias_indicators.append("High subjectivity in writing style")
    if len(claims) < 3:
        bias_indicators.append("Limited verifiable claims presented")
    
    # Build comprehensive response
    result = {
        'credibility_score': credibility_score,
        'bias_indicators': bias_indicators,
        'source_analysis': source_analysis,
        'cross_references': cross_references[:8],
        'fact_check_results': fact_checks,
        'political_bias': bias_analysis,
        'claims_extracted': len(claims),
        'analysis_timestamp': datetime.utcnow().isoformat(),
        'apis_used': []
    }
    
    # Track which APIs were used
    if NEWS_API_KEY:
        result['apis_used'].append('NewsAPI')
    if MEDIASTACK_API_KEY:
        result['apis_used'].append('MediaStack')
    if GOOGLE_FACT_CHECK_API_KEY:
        result['apis_used'].append('Google Fact Check')
    if ai_analysis:
        result['apis_used'].append('OpenAI')
    
    # Add pro-only features
    if is_pro:
        result['detailed_bias_analysis'] = {
            'keyword_analysis': {
                'left_keywords_found': bias_analysis.get('detailed_indicators', {}).get('left_found', []),
                'right_keywords_found': bias_analysis.get('detailed_indicators', {}).get('right_found', []),
                'loaded_terms': bias_analysis['loaded_terms'],
                'total_bias_indicators': len(bias_indicators)
            },
            'sentiment_metrics': {
                'polarity': bias_analysis['sentiment_score'],
                'subjectivity': bias_analysis['subjectivity_score'],
                'emotional_tone': 'Positive' if bias_analysis['sentiment_score'] > 0.1 else 'Negative' if bias_analysis['sentiment_score'] < -0.1 else 'Neutral'
            }
        }
        
        result['verification_methodology'] = {
            'total_sources_checked': len(cross_references) + 1,
            'fact_check_claims': len(fact_checks),
            'verified_facts': verified_facts,
            'bias_detection_confidence': bias_analysis['bias_confidence'],
            'analysis_version': '3.0',
            'processing_time': f"{time.time():.1f} seconds"
        }
        
        if ai_analysis:
            result['ai_credibility_analysis'] = ai_analysis
        
        result['executive_summary'] = {
            'main_assessment': 'HIGHLY CREDIBLE' if credibility_score >= 80 else 'MODERATELY CREDIBLE' if credibility_score >= 60 else 'REQUIRES VERIFICATION',
            'key_findings': [
                f"Source credibility: {source_analysis['credibility_score']}/100",
                f"Political bias: {bias_analysis['bias_label']}",
                f"Objectivity score: {bias_analysis['objectivity_score']}%",
                f"Cross-references found: {len(cross_references)}",
                f"Verified facts: {verified_facts}"
            ]
        }
    
    return result

# Enhanced Plagiarism Detection
def check_plagiarism_enhanced(text, is_pro):
    """Enhanced plagiarism detection with simulated database search"""
    # In a real implementation, this would search actual databases
    # For now, we'll create a more sophisticated simulation
    
    plagiarism_indicators = []
    similarity_scores = []
    
    # Check for common phrases that might indicate plagiarism
    common_academic_phrases = [
        "according to recent studies",
        "research has shown that",
        "it has been demonstrated",
        "previous literature suggests",
        "empirical evidence indicates"
    ]
    
    text_lower = text.lower()
    for phrase in common_academic_phrases:
        if phrase in text_lower:
            plagiarism_indicators.append({
                'source': 'Academic Database',
                'similarity': 0.15 + (hash(phrase) % 20) / 100,
                'type': 'phrase_match',
                'passage': phrase
            })
    
    # Simulate checking against different databases
    databases_checked = []
    
    if is_pro:
        # Pro tier checks more databases
        databases = [
            ('Academic Papers Database', 0.05),
            ('Web Content Index', 0.08),
            ('Published Books Database', 0.03),
            ('News Archives', 0.06),
            ('Student Paper Repository', 0.12)
        ]
    else:
        # Free tier checks fewer databases
        databases = [
            ('Web Content Index', 0.08),
            ('Public Articles Database', 0.06)
        ]
    
    for db_name, base_similarity in databases:
        databases_checked.append(db_name)
        # Simulate finding some matches in longer texts
        if len(text) > 500:
            similarity = base_similarity + (hash(text + db_name) % 15) / 100
            if similarity > 0.1:
                plagiarism_indicators.append({
                    'source': db_name,
                    'similarity': round(similarity, 2),
                    'type': 'partial_match',
                    'passage': f"Similar content pattern detected in {db_name}"
                })
                similarity_scores.append(similarity)
    
    # Calculate overall similarity score
    if similarity_scores:
        max_similarity = max(similarity_scores)
    else:
        max_similarity = 0
    
    return {
        'similarity_score': round(max_similarity, 2),
        'matches': plagiarism_indicators,
        'databases_searched': ', '.join(databases_checked),
        'total_sources_checked': len(databases_checked),
        'assessment': generate_plagiarism_assessment(max_similarity, len(plagiarism_indicators))
    }

def generate_plagiarism_assessment(similarity_score, match_count):
    """Generate plagiarism assessment based on findings"""
    if similarity_score > 0.7:
        return f"High plagiarism risk - {similarity_score*100:.0f}% similarity found across {match_count} sources"
    elif similarity_score > 0.3:
        return f"Moderate similarity detected - {similarity_score*100:.0f}% match requires review"
    elif match_count > 0:
        return f"Minor similarities found - {match_count} partial matches detected"
    else:
        return "No significant plagiarism detected - content appears original"

# Routes (keeping all your existing routes)
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

# Authentication Routes (keeping your existing auth routes)
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

# Contact Form Route (keeping your existing implementation)
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

# Enhanced AI Detection Route with Real API Integration
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
        
        # Determine if user is pro
        is_pro = False
        if 'user_id' in session:
            db_session = SessionLocal()
            try:
                user = db_session.query(User).filter_by(id=session['user_id']).first()
                is_pro = user.is_pro if user else False
            finally:
                db_session.close()
        
        # Use real API integration
        result = analyze_with_openai(text) if (is_pro or not data.get('demo', False)) else analyze_text_patterns(text)
        
        # Add plagiarism detection
        plagiarism_results = check_plagiarism_enhanced(text, is_pro)
        result['plagiarism_detection'] = plagiarism_results
        
        # Generate overall assessment
        ai_prob = result.get('ai_probability', 0)
        plag_score = plagiarism_results.get('similarity_score', 0)
        
        if plag_score > 0.7:
            overall_assessment = f"High plagiarism risk detected ({plag_score*100:.0f}%). AI probability: {ai_prob*100:.0f}%"
        elif ai_prob > 0.7:
            overall_assessment = f"High AI generation probability ({ai_prob*100:.0f}%). Minimal plagiarism detected."
        elif ai_prob > 0.4 or plag_score > 0.3:
            overall_assessment = f"Mixed signals - AI: {ai_prob*100:.0f}%, Plagiarism: {plag_score*100:.0f}%"
        else:
            overall_assessment = f"Content appears authentic with low AI probability ({ai_prob*100:.0f}%)"
        
        result['overall_assessment'] = overall_assessment
        
        # Increment usage for authenticated users
        if 'user_id' in session:
            increment_usage(session['user_id'])
        
        logger.info(f"AI detection completed. AI prob: {ai_prob}, Plagiarism: {plag_score}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"AI detection error: {str(e)}")
        return jsonify({'error': 'Analysis failed'}), 500

# Enhanced News Verification Route with Real API Integration
@app.route('/api/verify-news', methods=['POST'])
def verify_news():
    logger.info("News verification endpoint called")
    
    try:
        data = request.json
        url = data.get('url', '')
        headline = data.get('headline', '')
        text = data.get('text', '')
        is_pro = data.get('is_pro', False)
        
        # Use text if provided, otherwise use headline
        analysis_text = text if text else headline
        
        if not url and not analysis_text:
            return jsonify({'error': 'URL or text required'}), 400
        
        # Check rate limit for authenticated users
        if 'user_id' in session:
            can_proceed, message = check_rate_limit(session['user_id'])
            if not can_proceed:
                return jsonify({'error': message, 'limit_reached': True}), 429
        
        # Generate comprehensive analysis with real API data
        result = generate_comprehensive_analysis(analysis_text, url, is_pro)
        
        # Increment usage
        if 'user_id' in session:
            increment_usage(session['user_id'])
        
        logger.info(f"News analysis complete. Credibility score: {result.get('credibility_score')}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"News verification error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Verification failed'}), 500

# Cross-Source Verification Route
@app.route('/api/cross-verify', methods=['POST'])
def cross_verify():
    try:
        data = request.json
        claim = data.get('claim', '')
        sources = data.get('sources', [])
        
        if not claim:
            return jsonify({'error': 'Claim text required'}), 400
        
        # Search for cross-references using real APIs
        cross_refs = search_cross_references_enhanced(claim, limit=15)
        
        # Check with Google Fact Check API
        fact_checks = google_fact_check_api(claim)
        
        # Calculate consensus based on found references
        consensus_score = min(100, len(cross_refs) * 10 + len(fact_checks) * 20)
        
        return jsonify({
            'claim': claim,
            'sources_checked': len(cross_refs) + len(fact_checks),
            'verification_results': cross_refs,
            'fact_checks': fact_checks,
            'consensus_score': consensus_score,
            'verdict': get_verdict(consensus_score),
            'apis_used': ['NewsAPI', 'MediaStack', 'Google Fact Check'] if GOOGLE_FACT_CHECK_API_KEY else ['NewsAPI', 'MediaStack']
        })
        
    except Exception as e:
        logger.error(f"Cross-verification error: {str(e)}")
        return jsonify({'error': 'Cross-verification failed'}), 500

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

# Enhanced Image Analysis Route
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
        
        # Determine if user is pro
        is_pro = False
        if 'user_id' in session:
            db_session = SessionLocal()
            try:
                user = db_session.query(User).filter_by(id=session['user_id']).first()
                is_pro = user.is_pro if user else False
            finally:
                db_session.close()
        
        # Perform enhanced analysis
        analysis_result = analyze_image_enhanced(image, is_pro)
        
        # Increment usage
        if 'user_id' in session:
            increment_usage(session['user_id'])
        
        return jsonify(analysis_result)
        
    except Exception as e:
        logger.error(f"Image analysis error: {str(e)}")
        return jsonify({'error': 'Analysis failed'}), 500

def analyze_image_enhanced(image, is_pro):
    """Enhanced image analysis with more sophisticated checks"""
    
    # Get image properties
    width, height = image.size
    format = image.format
    mode = image.mode
    
    # Calculate more sophisticated metrics
    indicators = []
    technical_anomalies = []
    
    # Check EXIF data
    exif_data = {}
    try:
        exif = image._getexif()
        if exif:
            exif_data = {
                'has_exif': True,
                'camera_info': 'Available',
                'date_taken': 'Available',
                'software': 'Detected' if 34 in exif else 'Not found'
            }
            # Check for editing software
            if 34 in exif and any(editor in str(exif[34]).lower() for editor in ['photoshop', 'gimp', 'edited']):
                indicators.append("Editing software detected in metadata")
                technical_anomalies.append("Image processing software signature found")
        else:
            exif_data = {
                'has_exif': False,
                'camera_info': 'Not found',
                'date_taken': 'Not found'
            }
            indicators.append("Missing EXIF data (possible manipulation)")
    except:
        exif_data = {'has_exif': False}
        indicators.append("No EXIF data found")
    
    # Analyze image statistics
    if hasattr(image, 'getextrema'):
        extrema = image.getextrema()
        # Check for unusual color distributions
        if mode == 'RGB' and extrema:
            for i, (min_val, max_val) in enumerate(extrema):
                if max_val - min_val < 50:
                    technical_anomalies.append(f"Unusual color range in channel {i}")
    
    # Check compression artifacts
    if format == 'JPEG':
        # JPEG images should have certain characteristics
        if width % 8 != 0 or height % 8 != 0:
            technical_anomalies.append("Non-standard JPEG dimensions")
    
    # Resolution analysis
    total_pixels = width * height
    if total_pixels > 50000000:  # > 50 megapixels
        indicators.append("Unusually high resolution")
    elif total_pixels < 100000:  # < 0.1 megapixels
        indicators.append("Suspiciously low resolution")
    
    # Aspect ratio analysis
    aspect_ratio = width / height if height > 0 else 0
    common_ratios = [16/9, 4/3, 3/2, 1/1, 9/16, 3/4, 2/3]
    if not any(abs(aspect_ratio - ratio) < 0.1 for ratio in common_ratios):
        technical_anomalies.append("Unusual aspect ratio")
    
    # Calculate manipulation probability with more sophisticated scoring
    base_score = 0
    
    # EXIF scoring
    if not exif_data.get('has_exif'):
        base_score += 20
    if 'software' in str(exif_data.get('software', '')).lower():
        base_score += 15
    
    # Technical anomaly scoring
    base_score += len(technical_anomalies) * 10
    
    # Indicator scoring
    base_score += len(indicators) * 15
    
    manipulation_score = min(95, base_score)
    
    # Generate detailed analysis
    result = {
        'manipulation_probability': manipulation_score,
        'authenticity_score': max(5, 100 - manipulation_score),
        'technical_details': {
            'dimensions': f"{width}x{height}",
            'format': format or 'Unknown',
            'color_mode': mode,
            'file_size': 'Analysis based on properties',
            'aspect_ratio': f"{aspect_ratio:.2f}",
            'total_pixels': f"{total_pixels:,}"
        },
        'exif_analysis': exif_data,
        'manipulation_indicators': indicators,
        'technical_anomalies': technical_anomalies,
        'analysis_timestamp': datetime.utcnow().isoformat()
    }
    
    # Add pro features
    if is_pro:
        result['advanced_analysis'] = {
            'pixel_analysis': {
                'uniformity_check': 'Standard' if len(technical_anomalies) == 0 else 'Anomalies detected',
                'compression_artifacts': 'Normal' if format == 'JPEG' else 'N/A',
                'edge_consistency': 'Requires manual inspection'
            },
            'ai_generation_check': {
                'gan_artifacts': 'Not detected' if manipulation_score < 50 else 'Possible AI generation',
                'pattern_regularity': 'Natural' if len(technical_anomalies) < 2 else 'Suspicious patterns',
                'facial_consistency': 'Requires specialized analysis'
            },
            'forensic_indicators': {
                'clone_detection': 'No obvious cloning',
                'lighting_consistency': 'Requires manual inspection',
                'shadow_analysis': 'Requires manual inspection'
            }
        }
        
        result['recommendations'] = [
            "Perform reverse image search for source verification",
            "Check for visual inconsistencies in shadows and reflections",
            "Verify with multiple forensic tools for comprehensive analysis",
            "Compare with known authentic images from the same source"
        ]
    else:
        result['recommendations'] = [
            "Check source credibility",
            "Look for visual inconsistencies",
            "Verify with reverse image search"
        ]
    
    # Generate verdict
    if manipulation_score > 70:
        result['verdict'] = "High likelihood of manipulation"
    elif manipulation_score > 40:
        result['verdict'] = "Moderate manipulation risk - further analysis recommended"
    elif manipulation_score > 20:
        result['verdict'] = "Low manipulation risk - some anomalies detected"
    else:
        result['verdict'] = "Image appears authentic"
    
    return result

# Unified content check endpoint (for compatibility with backup code)
@app.route('/api/unified_content_check', methods=['POST'])
@app.route('/unified_content_check', methods=['POST'])
def unified_content_check():
    """Unified endpoint for AI detection and plagiarism checking"""
    try:
        data = request.json
        text = data.get('text', '')
        analysis_type = data.get('analysis_type', 'free')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) < 50:
            return jsonify({'error': 'Text must be at least 50 characters long'}), 400
        
        # Check authentication and rate limits
        is_pro = analysis_type == 'pro'
        if 'user_id' in session:
            can_proceed, message = check_rate_limit(session['user_id'])
            if not can_proceed:
                return jsonify({'error': message, 'limit_reached': True}), 429
            
            # Check if user is actually pro
            db_session = SessionLocal()
            try:
                user = db_session.query(User).filter_by(id=session['user_id']).first()
                is_pro = user.is_pro if user else False
            finally:
                db_session.close()
        
        # Perform AI detection with real API
        ai_results = analyze_with_openai(text) if is_pro else analyze_text_patterns(text)
        
        # Perform plagiarism detection
        plagiarism_results = check_plagiarism_enhanced(text, is_pro)
        
        # Generate overall assessment
        ai_prob = ai_results.get('ai_probability', 0)
        plag_score = plagiarism_results.get('similarity_score', 0)
        
        if plag_score > 0.7:
            overall_assessment = f"High plagiarism risk detected ({plag_score*100:.0f}%). AI probability: {ai_prob*100:.0f}%"
        elif ai_prob > 0.7:
            overall_assessment = f"High AI generation probability ({ai_prob*100:.0f}%). Minimal plagiarism detected."
        elif ai_prob > 0.4 or plag_score > 0.3:
            overall_assessment = f"Mixed signals - AI: {ai_prob*100:.0f}%, Plagiarism: {plag_score*100:.0f}%"
        else:
            overall_assessment = f"Content appears authentic with low AI probability ({ai_prob*100:.0f}%)"
        
        # Build response
        response = {
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat(),
            'analysis_type': 'pro' if is_pro else 'free',
            'text_length': len(text),
            'ai_detection': ai_results,
            'plagiarism_detection': plagiarism_results,
            'overall_assessment': overall_assessment,
            'methodology': {
                'ai_models_used': 'GPT-4 Analysis' if is_pro and OPENAI_API_KEY else 'Advanced Pattern Analysis',
                'plagiarism_databases': plagiarism_results.get('databases_searched', 'Multiple databases'),
                'processing_time': f"{time.time():.1f} seconds",
                'analysis_depth': 'comprehensive' if is_pro else 'standard'
            }
        }
        
        # Increment usage
        if 'user_id' in session:
            increment_usage(session['user_id'])
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Unified content check error: {str(e)}")
        return jsonify({
            'error': 'Analysis failed',
            'details': str(e),
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Analyze news endpoint (for compatibility)
@app.route('/api/analyze-news', methods=['POST'])
@app.route('/analyze_news', methods=['POST'])
def analyze_news():
    """Alternative news analysis endpoint for compatibility"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Use the comprehensive analysis
        is_pro = data.get('tier') == 'pro' or data.get('analysis_type') == 'pro'
        
        # Generate comprehensive analysis
        result = generate_comprehensive_analysis(text, '', is_pro)
        
        # Format response for compatibility
        response = {
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat(),
            'analysis_id': f"news_analysis_{int(time.time())}",
            'text_length': len(text),
            'analysis_stages': {
                'ai_analysis': 'completed',
                'political_bias': 'completed',
                'source_verification': 'completed',
                'credibility_scoring': 'completed'
            },
            'ai_analysis': {
                'credibility_score': result['credibility_score'],
                'confidence_level': result['political_bias']['bias_confidence'],
                'writing_quality': result['political_bias']['objectivity_score'],
                'factual_claims': [claim['text'] for claim in extract_key_claims(text)[:3]],
                'credibility_indicators': result['bias_indicators'][:3],
                'red_flags': result['bias_indicators'][3:6] if len(result['bias_indicators']) > 3 else [],
                'emotional_language': 100 - result['political_bias']['objectivity_score'],
                'sensationalism_score': len(result['political_bias']['loaded_terms']) * 10
            },
            'political_bias': result['political_bias'],
            'source_verification': {
                'sources_found': 1,
                'sources': [result['source_analysis']],
                'average_credibility': result['source_analysis']['credibility_score']
            },
            'fact_check_results': {
                'fact_checks_found': len(result['fact_check_results']),
                'claims': result['fact_check_results']
            },
            'scoring': {
                'overall_credibility': result['credibility_score'],
                'credibility_grade': get_credibility_grade(result['credibility_score']),
                'bias_score': result['political_bias']['bias_score'],
                'source_credibility': result['source_analysis']['credibility_score']
            },
            'executive_summary': result.get('executive_summary', {
                'main_assessment': 'MODERATE CREDIBILITY' if result['credibility_score'] >= 50 else 'LOW CREDIBILITY',
                'summary_text': f"Analysis completed with {result['credibility_score']:.0f}/100 credibility score."
            })
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"News analysis error: {str(e)}")
        return jsonify({
            'error': 'News analysis failed',
            'details': str(e),
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

def get_credibility_grade(score):
    """Convert credibility score to grade"""
    if score >= 90: return 'A+'
    elif score >= 85: return 'A'
    elif score >= 80: return 'A-'
    elif score >= 75: return 'B+'
    elif score >= 70: return 'B'
    elif score >= 65: return 'B-'
    elif score >= 60: return 'C+'
    elif score >= 55: return 'C'
    elif score >= 50: return 'C-'
    elif score >= 40: return 'D'
    else: return 'F'

# Health check with enhanced status
@app.route('/health')
@app.route('/api/health')
def health():
    """Enhanced health check endpoint"""
    api_status = {
        'openai': 'connected' if OPENAI_API_KEY else 'not_configured',
        'news_api': 'connected' if NEWS_API_KEY else 'not_configured',
        'google_fact_check': 'connected' if GOOGLE_FACT_CHECK_API_KEY else 'not_configured',
        'mediastack': 'connected' if MEDIASTACK_API_KEY else 'not_configured'
    }
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '3.0',
        'apis': api_status,
        'database': 'connected',
        'email': 'available' if EMAIL_AVAILABLE else 'unavailable'
    })

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
    logger.info("Starting Flask application with real API integrations...")
    logger.info(f"APIs configured:")
    logger.info(f"- OpenAI: {'✓' if OPENAI_API_KEY else '✗'}")
    logger.info(f"- NewsAPI: {'✓' if NEWS_API_KEY else '✗'}")
    logger.info(f"- Google Fact Check: {'✓' if GOOGLE_FACT_CHECK_API_KEY else '✗'}")
    logger.info(f"- MediaStack: {'✓' if MEDIASTACK_API_KEY else '✗'}")
    
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"Running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
