# Facts & Fakes AI Platform - Complete Backend with Smart Content Preprocessing
# Enhanced version with all features integrated

import os 
import re
import json
import uuid
import hashlib
import logging
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
from functools import wraps

# Flask and web framework imports
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

# Database imports
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

# Environment and configuration
from dotenv import load_dotenv
load_dotenv()

# Email imports with Python 3.13 compatibility
EMAIL_AVAILABLE = False
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

# AI and API imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Smart Content Preprocessing imports with fallbacks
try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False

try:
    from newspaper import Article
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False

try:
    from goose3 import Goose
    GOOSE_AVAILABLE = True
except ImportError:
    GOOSE_AVAILABLE = False

try:
    from readability import Document
    READABILITY_AVAILABLE = True
except ImportError:
    READABILITY_AVAILABLE = False

try:
    import html2text
    HTML2TEXT_AVAILABLE = True
except ImportError:
    HTML2TEXT_AVAILABLE = False

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Email configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'mail.factsandfakes.ai')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    CONTACT_EMAIL = os.getenv('CONTACT_EMAIL', 'contact@factsandfakes.ai')
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    GOOGLE_FACT_CHECK_API_KEY = os.getenv('GOOGLE_FACT_CHECK_API_KEY')
    
    # App settings
    DAILY_FREE_LIMIT = 5
    DAILY_PRO_LIMIT = 5
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)

# Initialize OpenAI
if OPENAI_AVAILABLE and Config.OPENAI_API_KEY:
    openai.api_key = Config.OPENAI_API_KEY

# Database connection pool
connection_pool = None
if Config.DATABASE_URL:
    try:
        connection_pool = ConnectionPool(...)
            1, 20,
            Config.DATABASE_URL
        )
        logger.info("Database connection pool initialized")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")

# Smart Content Preprocessing Class
class SmartContentPreprocessor:
    """Advanced web content extraction and cleaning system"""
    
    def __init__(self):
        if REQUESTS_AVAILABLE:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
        else:
            self.session = None
        
    def extract_clean_content(self, url_or_text):
        """
        Extract clean, readable content from URL or raw HTML
        Returns: {
            'success': bool,
            'clean_text': str,
            'title': str,
            'author': str,
            'publish_date': str,
            'source_url': str,
            'word_count': int,
            'extraction_method': str,
            'confidence_score': float
        }
        """
        try:
            if self._is_url(url_or_text):
                return self._extract_from_url(url_or_text)
            else:
                return self._extract_from_text(url_or_text)
        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            return {
                'success': False,
                'error': f'Content extraction failed: {str(e)}',
                'clean_text': url_or_text if not self._is_url(url_or_text) else '',
                'title': '',
                'author': '',
                'publish_date': '',
                'source_url': url_or_text if self._is_url(url_or_text) else '',
                'word_count': 0,
                'extraction_method': 'error',
                'confidence_score': 0.0
            }
    
    def _is_url(self, text):
        """Check if input is a URL"""
        try:
            result = urlparse(text.strip())
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _extract_from_url(self, url):
        """Extract content from URL using multiple methods"""
        if not REQUESTS_AVAILABLE:
            return self._create_error_response("Requests library not available", url)
        
        results = []
        
        # Method 1: Newspaper3k (best for news articles)
        if NEWSPAPER_AVAILABLE:
            try:
                article = Article(url)
                article.download()
                article.parse()
                
                if article.text and len(article.text) > 100:
                    results.append({
                        'method': 'newspaper3k',
                        'text': article.text,
                        'title': article.title or '',
                        'author': ', '.join(article.authors) if article.authors else '',
                        'publish_date': str(article.publish_date) if article.publish_date else '',
                        'confidence': 0.9
                    })
            except Exception as e:
                logger.warning(f"Newspaper3k extraction failed: {e}")
        
        # Method 2: Goose3 (alternative news extractor)
        if GOOSE_AVAILABLE:
            try:
                g = Goose()
                article = g.extract(url=url)
                
                if article.cleaned_text and len(article.cleaned_text) > 100:
                    results.append({
                        'method': 'goose3',
                        'text': article.cleaned_text,
                        'title': article.title or '',
                        'author': article.authors[0] if article.authors else '',
                        'publish_date': str(article.publish_date) if article.publish_date else '',
                        'confidence': 0.8
                    })
            except Exception as e:
                logger.warning(f"Goose3 extraction failed: {e}")
        
        # Method 3: Readability + BeautifulSoup (fallback)
        if READABILITY_AVAILABLE and BEAUTIFULSOUP_AVAILABLE:
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                # Use readability to extract main content
                doc = Document(response.text)
                clean_html = doc.summary()
                
                # Parse with BeautifulSoup for additional cleaning
                soup = BeautifulSoup(clean_html, 'html.parser')
                
                # Remove unwanted elements
                for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'advertisement']):
                    element.decompose()
                
                # Extract text
                text = soup.get_text(separator=' ', strip=True)
                text = self._clean_extracted_text(text)
                
                # Extract metadata
                original_soup = BeautifulSoup(response.text, 'html.parser')
                title = self._extract_title(original_soup)
                author = self._extract_author(original_soup)
                
                if text and len(text) > 100:
                    results.append({
                        'method': 'readability',
                        'text': text,
                        'title': title,
                        'author': author,
                        'publish_date': '',
                        'confidence': 0.7
                    })
                    
            except Exception as e:
                logger.warning(f"Readability extraction failed: {e}")
        
        # Method 4: Basic BeautifulSoup (last resort)
        if BEAUTIFULSOUP_AVAILABLE:
            try:
                response = self.session.get(url, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try common article selectors
                content = None
                selectors = [
                    'article', '[role="main"]', '.article-content', '.post-content',
                    '.entry-content', '.content', 'main', '.article-body'
                ]
                
                for selector in selectors:
                    elements = soup.select(selector)
                    if elements:
                        content = elements[0]
                        break
                
                if not content:
                    content = soup.body or soup
                
                # Clean unwanted elements
                for element in content.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                    element.decompose()
                
                text = content.get_text(separator=' ', strip=True)
                text = self._clean_extracted_text(text)
                
                if text and len(text) > 100:
                    results.append({
                        'method': 'basic_soup',
                        'text': text,
                        'title': self._extract_title(soup),
                        'author': self._extract_author(soup),
                        'publish_date': '',
                        'confidence': 0.5
                    })
                    
            except Exception as e:
                logger.warning(f"Basic extraction failed: {e}")
        
        # Return best result
        if results:
            best_result = max(results, key=lambda x: x['confidence'])
            return {
                'success': True,
                'clean_text': best_result['text'],
                'title': best_result['title'],
                'author': best_result['author'],
                'publish_date': best_result['publish_date'],
                'source_url': url,
                'word_count': len(best_result['text'].split()),
                'extraction_method': best_result['method'],
                'confidence_score': best_result['confidence']
            }
        else:
            return self._create_error_response('Failed to extract readable content from URL', url)
    
    def _extract_from_text(self, raw_text):
        """Clean raw text/HTML input"""
        try:
            # Check if it's HTML
            if '<' in raw_text and '>' in raw_text and BEAUTIFULSOUP_AVAILABLE:
                soup = BeautifulSoup(raw_text, 'html.parser')
                
                # Remove unwanted elements
                for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                    element.decompose()
                
                text = soup.get_text(separator=' ', strip=True)
                title = self._extract_title(soup)
                author = self._extract_author(soup)
            else:
                text = raw_text
                title = ''
                author = ''
            
            clean_text = self._clean_extracted_text(text)
            
            return {
                'success': True,
                'clean_text': clean_text,
                'title': title,
                'author': author,
                'publish_date': '',
                'source_url': '',
                'word_count': len(clean_text.split()),
                'extraction_method': 'text_cleaning',
                'confidence_score': 0.8
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Text cleaning failed: {str(e)}',
                'clean_text': raw_text,  # Return original as fallback
                'title': '',
                'author': '',
                'publish_date': '',
                'source_url': '',
                'word_count': len(raw_text.split()) if raw_text else 0,
                'extraction_method': 'none',
                'confidence_score': 0.3
            }
    
    def _clean_extracted_text(self, text):
        """Advanced text cleaning and normalization"""
        if not text:
            return ''
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common web artifacts
        text = re.sub(r'(Cookie|Privacy Policy|Terms of Service|Subscribe|Newsletter).*?(?=\.|$)', '', text, flags=re.IGNORECASE)
        
        # Remove social media artifacts
        text = re.sub(r'(Share on|Follow us|Like us|Tweet|Facebook|Instagram|LinkedIn).*?(?=\.|$)', '', text, flags=re.IGNORECASE)
        
        # Remove advertisement indicators
        text = re.sub(r'(Advertisement|Sponsored|Ad|Promoted Content).*?(?=\.|$)', '', text, flags=re.IGNORECASE)
        
        # Remove navigation artifacts
        text = re.sub(r'(Home|Menu|Search|Login|Sign up|Register)(?=\s|$)', '', text, flags=re.IGNORECASE)
        
        # Remove common website elements
        text = re.sub(r'(Click here|Read more|Continue reading|Load more|Show more)', '', text, flags=re.IGNORECASE)
        
        # Clean up punctuation
        text = re.sub(r'([.!?])\s*([.!?])+', r'\1', text)  # Remove duplicate punctuation
        
        # Remove isolated single characters (except 'I' and 'a')
        text = re.sub(r'\b(?![Ia])[a-zA-Z]\b\s*', '', text)
        
        # Final cleanup
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_title(self, soup):
        """Extract article title from HTML"""
        if not BEAUTIFULSOUP_AVAILABLE or not soup:
            return ''
        
        # Try various title selectors
        selectors = [
            'h1.article-title', 'h1.post-title', 'h1.entry-title',
            '.article-header h1', '.post-header h1',
            'h1', 'title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text().strip():
                return element.get_text().strip()
        
        return ''
    
    def _extract_author(self, soup):
        """Extract author from HTML"""
        if not BEAUTIFULSOUP_AVAILABLE or not soup:
            return ''
        
        # Try various author selectors
        selectors = [
            '.author', '.byline', '.author-name', '.post-author',
            '[rel="author"]', '.article-author', '.writer'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text().strip():
                return element.get_text().strip()
        
        # Try meta tags
        meta_author = soup.find('meta', {'name': 'author'})
        if meta_author and meta_author.get('content'):
            return meta_author['content'].strip()
        
        return ''
    
    def _create_error_response(self, error_message, url=''):
        """Create standardized error response"""
        return {
            'success': False,
            'error': error_message,
            'clean_text': '',
            'title': '',
            'author': '',
            'publish_date': '',
            'source_url': url,
            'word_count': 0,
            'extraction_method': 'none',
            'confidence_score': 0.0
        }

# Initialize preprocessor
preprocessor = SmartContentPreprocessor()

# Database helper functions
def get_db_connection():
    """Get database connection from pool"""
    if connection_pool:
        try:
            return connection_pool.getconn()
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return None
    return None

def return_db_connection(conn):
    """Return connection to pool"""
    if connection_pool and conn:
        connection_pool.putconn(conn)

def execute_db_query(query, params=None, fetch=False):
    """Execute database query with connection pooling"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            if fetch:
                result = cur.fetchall()
            else:
                result = cur.rowcount
            conn.commit()
            return result
    except Exception as e:
        logger.error(f"Database query error: {e}")
        conn.rollback()
        return None
    finally:
        return_db_connection(conn)

# User management functions
def create_user_tables():
    """Create user management tables"""
    queries = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            subscription_tier VARCHAR(50) DEFAULT 'free',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS user_usage (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            usage_date DATE DEFAULT CURRENT_DATE,
            feature_type VARCHAR(100) NOT NULL,
            usage_count INTEGER DEFAULT 1,
            UNIQUE(user_id, usage_date, feature_type)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS contact_submissions (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255) NOT NULL,
            subject VARCHAR(500),
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(50) DEFAULT 'pending'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS analysis_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            analysis_type VARCHAR(100) NOT NULL,
            input_content TEXT,
            result_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]
    
    for query in queries:
        execute_db_query(query)

# Initialize database
create_user_tables()

def hash_password(password):
    """Hash password securely"""
    return generate_password_hash(password)

def verify_password(password, hash):
    """Verify password against hash"""
    return check_password_hash(hash, password)

def create_user(email, password):
    """Create new user account"""
    try:
        password_hash = hash_password(password)
        result = execute_db_query(
            "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id",
            (email, password_hash),
            fetch=True
        )
        return result[0]['id'] if result else None
    except Exception as e:
        logger.error(f"User creation error: {e}")
        return None

def authenticate_user(email, password):
    """Authenticate user login"""
    result = execute_db_query(
        "SELECT id, password_hash, subscription_tier FROM users WHERE email = %s AND is_active = TRUE",
        (email,),
        fetch=True
    )
    
    if result and verify_password(password, result[0]['password_hash']):
        # Update last login
        execute_db_query(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
            (result[0]['id'],)
        )
        return {
            'id': result[0]['id'],
            'email': email,
            'subscription_tier': result[0]['subscription_tier']
        }
    return None

def log_user_action(user_id, feature_type, metadata=None):
    """Log user action for usage tracking"""
    try:
        # Update usage count
        execute_db_query(
            """
            INSERT INTO user_usage (user_id, feature_type, usage_count)
            VALUES (%s, %s, 1)
            ON CONFLICT (user_id, usage_date, feature_type)
            DO UPDATE SET usage_count = user_usage.usage_count + 1
            """,
            (user_id, feature_type)
        )
        
        # Store detailed analysis history if metadata provided
        if metadata:
            execute_db_query(
                "INSERT INTO analysis_history (user_id, analysis_type, result_data) VALUES (%s, %s, %s)",
                (user_id, feature_type, json.dumps(metadata))
            )
    except Exception as e:
        logger.error(f"Usage logging error: {e}")

def get_user_usage(user_id, feature_type):
    """Get user's daily usage for a feature"""
    result = execute_db_query(
        "SELECT usage_count FROM user_usage WHERE user_id = %s AND usage_date = CURRENT_DATE AND feature_type = %s",
        (user_id, feature_type),
        fetch=True
    )
    return result[0]['usage_count'] if result else 0

def check_usage_limit(user_id, feature_type, subscription_tier):
    """Check if user has exceeded usage limits"""
    usage_count = get_user_usage(user_id, feature_type)
    
    if subscription_tier == 'pro':
        limit = Config.DAILY_FREE_LIMIT + Config.DAILY_PRO_LIMIT
    else:
        limit = Config.DAILY_FREE_LIMIT
    
    return usage_count < limit

# Email functions
def send_email(to_email, subject, body, is_html=False):
    """Send email using SMTP"""
    if not EMAIL_AVAILABLE or not Config.SMTP_USERNAME:
        logger.warning("Email not available or not configured")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = Config.SMTP_USERNAME
        msg['To'] = to_email
        msg['Subject'] = subject
        
        if is_html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
        server.starttls()
        server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        return False

def send_welcome_email(email):
    """Send welcome email to new users"""
    subject = "Welcome to Facts & Fakes AI - Your News Verification Platform"
    body = f"""
    Welcome to Facts & Fakes AI!
    
    Thank you for joining our beta program. You now have access to:
    
    ✅ Advanced AI-powered news verification
    ✅ Real-time fact-checking and bias detection
    ✅ Source credibility analysis
    ✅ Smart content preprocessing
    ✅ Daily usage limits: {Config.DAILY_FREE_LIMIT} free + {Config.DAILY_PRO_LIMIT} pro analyses
    
    Get started at: https://factsandfakes.ai
    
    Questions? Reply to this email or contact us at {Config.CONTACT_EMAIL}
    
    Best regards,
    The Facts & Fakes AI Team
    """
    
    return send_email(email, subject, body)

def send_contact_notification(name, email, subject, message):
    """Send notification email for contact form submissions"""
    notification_subject = f"New Contact Form Submission: {subject}"
    notification_body = f"""
    New contact form submission received:
    
    Name: {name}
    Email: {email}
    Subject: {subject}
    
    Message:
    {message}
    
    Submitted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    # Send to admin
    send_email(Config.CONTACT_EMAIL, notification_subject, notification_body)
    
    # Send auto-reply to user
    auto_reply_subject = "Thank you for contacting Facts & Fakes AI"
    auto_reply_body = f"""
    Hi {name},
    
    Thank you for reaching out to Facts & Fakes AI. We've received your message and will respond within 24 hours.
    
    Your message:
    Subject: {subject}
    Message: {message}
    
    Best regards,
    The Facts & Fakes AI Team
    """
    
    return send_email(email, auto_reply_subject, auto_reply_body)

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def usage_limit_required(feature_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' in session:
                user_id = session['user_id']
                subscription_tier = session.get('subscription_tier', 'free')
                
                if not check_usage_limit(user_id, feature_type, subscription_tier):
                    return jsonify({
                        'error': 'Daily usage limit exceeded',
                        'upgrade_required': subscription_tier == 'free'
                    }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# AI Analysis Functions
def analyze_with_openai(prompt, content, model="gpt-4"):
    """Analyze content using OpenAI API"""
    if not OPENAI_AVAILABLE or not Config.OPENAI_API_KEY:
        return "OpenAI API not available"
    
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": content}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return f"Analysis temporarily unavailable: {str(e)}"

def get_news_api_data(query, api_key=None):
    """Fetch data from News API"""
    if not REQUESTS_AVAILABLE:
        return None
    
    api_key = api_key or Config.NEWS_API_KEY
    if not api_key:
        return None
    
    try:
        url = f"https://newsapi.org/v2/everything"
        params = {
            'q': query,
            'apiKey': api_key,
            'sortBy': 'relevancy',
            'pageSize': 10
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"News API error: {e}")
        return None

def check_google_fact_check(query):
    """Check Google Fact Check API"""
    if not REQUESTS_AVAILABLE or not Config.GOOGLE_FACT_CHECK_API_KEY:
        return None
    
    try:
        url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        params = {
            'query': query,
            'key': Config.GOOGLE_FACT_CHECK_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Google Fact Check API error: {e}")
        return None

# Route handlers
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/unified')
def unified():
    return render_template('unified.html')

@app.route('/imageanalysis')
def imageanalysis():
    return render_template('imageanalysis.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/missionstatement')
def missionstatement():
    return render_template('missionstatement.html')

@app.route('/pricingplan')
def pricingplan():
    return render_template('pricingplan.html')

# Authentication routes
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Check if user exists
        existing_user = execute_db_query(
            "SELECT id FROM users WHERE email = %s",
            (email,),
            fetch=True
        )
        
        if existing_user:
            return jsonify({'error': 'User already exists'}), 409
        
        # Create user
        user_id = create_user(email, password)
        if user_id:
            # Send welcome email
            send_welcome_email(email)
            
            # Log user in
            session['user_id'] = user_id
            session['email'] = email
            session['subscription_tier'] = 'free'
            
            return jsonify({
                'message': 'Registration successful',
                'user': {
                    'id': user_id,
                    'email': email,
                    'subscription_tier': 'free'
                }
            })
        else:
            return jsonify({'error': 'Registration failed'}), 500
            
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = authenticate_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['subscription_tier'] = user['subscription_tier']
            
            return jsonify({
                'message': 'Login successful',
                'user': user
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout successful'})

@app.route('/api/user-status')
def user_status():
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': session['user_id'],
                'email': session['email'],
                'subscription_tier': session.get('subscription_tier', 'free')
            }
        })
    else:
        return jsonify({'authenticated': False})

# Contact form
@app.route('/api/contact', methods=['POST'])
def submit_contact():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()
        
        if not email or not message:
            return jsonify({'error': 'Email and message are required'}), 400
        
        # Store in database
        execute_db_query(
            "INSERT INTO contact_submissions (name, email, subject, message) VALUES (%s, %s, %s, %s)",
            (name, email, subject, message)
        )
        
        # Send email notifications
        send_contact_notification(name, email, subject, message)
        
        return jsonify({'message': 'Contact form submitted successfully'})
        
    except Exception as e:
        logger.error(f"Contact form error: {e}")
        return jsonify({'error': 'Submission failed'}), 500

# Smart Content Preprocessing API
@app.route('/api/preprocess-content', methods=['POST'])
@usage_limit_required('content_preprocessing')
def preprocess_content():
    """API endpoint for content preprocessing"""
    try:
        data = request.get_json()
        content_input = data.get('content', '').strip()
        
        if not content_input:
            return jsonify({
                'success': False,
                'error': 'No content provided'
            }), 400
        
        # Extract and clean content
        result = preprocessor.extract_clean_content(content_input)
        
        # Log usage if user is authenticated
        if 'user_id' in session:
            log_user_action(session['user_id'], 'content_preprocessing', {
                'input_type': 'url' if preprocessor._is_url(content_input) else 'text',
                'word_count': result.get('word_count', 0),
                'extraction_method': result.get('extraction_method', 'unknown'),
                'confidence_score': result.get('confidence_score', 0.0)
            })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Content preprocessing error: {e}")
        return jsonify({
            'success': False,
            'error': 'Content preprocessing failed',
            'clean_text': data.get('content', '') if 'data' in locals() else '',
            'title': '',
            'author': '',
            'publish_date': '',
            'source_url': '',
            'word_count': 0,
            'extraction_method': 'error',
            'confidence_score': 0.0
        }), 500

@app.route('/api/preview-preprocessing', methods=['POST'])
def preview_preprocessing():
    """API endpoint for real-time preprocessing preview"""
    try:
        data = request.get_json()
        content_input = data.get('content', '').strip()
        
        if not content_input:
            return jsonify({
                'success': False,
                'error': 'No content provided'
            })
        
        # Quick preview extraction (lighter processing)
        if preprocessor._is_url(content_input):
            if not REQUESTS_AVAILABLE:
                return jsonify({
                    'success': False,
                    'error': 'URL processing not available',
                    'is_url': True
                })
            
            try:
                response = requests.get(content_input, timeout=5)
                if BEAUTIFULSOUP_AVAILABLE:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Quick title extraction
                    title_elem = soup.find('title')
                    title = title_elem.get_text().strip() if title_elem else 'No title found'
                    
                    # Quick content preview (first 500 chars)
                    for script in soup(["script", "style"]):
                        script.decompose()
                    text = soup.get_text()
                    text = re.sub(r'\s+', ' ', text).strip()
                    preview = text[:500] + ('...' if len(text) > 500 else '')
                else:
                    title = 'Preview unavailable'
                    preview = 'BeautifulSoup library not available'
                
                return jsonify({
                    'success': True,
                    'title': title,
                    'preview_text': preview,
                    'full_length': len(text) if 'text' in locals() else 0,
                    'is_url': True
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Could not preview URL: {str(e)}',
                    'is_url': True
                })
        else:
            # Text input preview
            text = content_input
            if '<' in text and '>' in text and BEAUTIFULSOUP_AVAILABLE:
                soup = BeautifulSoup(text, 'html.parser')
                text = soup.get_text()
            
            text = re.sub(r'\s+', ' ', text).strip()
            preview = text[:500] + ('...' if len(text) > 500 else '')
            
            return jsonify({
                'success': True,
                'title': 'Text Input',
                'preview_text': preview,
                'full_length': len(text),
                'is_url': False
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Preview failed: {str(e)}'
        })

# News analysis API
@app.route('/api/analyze-news', methods=['POST'])
@usage_limit_required('news_analysis')
def analyze_news():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        analysis_type = data.get('analysis_type', 'comprehensive')
        
        if not text:
            return jsonify({'error': 'No text provided for analysis'}), 400
        
        # Prepare analysis based on type
        if analysis_type == 'bias_detection':
            prompt = """Analyze the following news article for political bias, tone, and perspective. Provide:
            1. Overall bias rating (left, center-left, center, center-right, right)
            2. Confidence score (0-100%)
            3. Key indicators of bias
            4. Emotional tone analysis
            5. Recommendations for balanced perspective"""
            
        elif analysis_type == 'fact_checking':
            prompt = """Fact-check the following news article. Provide:
            1. Factual accuracy assessment
            2. Verifiable claims identification
            3. Potential misinformation flags
            4. Source credibility evaluation
            5. Overall reliability score (0-100%)"""
            
        elif analysis_type == 'source_analysis':
            prompt = """Analyze the credibility and reliability of this news content. Provide:
            1. Source authority assessment
            2. Publication quality indicators
            3. Editorial standards evaluation
            4. Transparency and accountability metrics
            5. Trust score (0-100%)"""
            
        else:  # comprehensive
            prompt = """Provide a comprehensive analysis of this news article including:
            1. Bias detection and political leaning
            2. Fact-checking and accuracy assessment
            3. Source credibility evaluation
            4. Emotional tone and rhetoric analysis
            5. Overall trustworthiness score
            6. Recommendations for readers"""
        
        # Get AI analysis
        analysis_result = analyze_with_openai(prompt, text)
        
        # Get related news and fact-checks
        news_data = get_news_api_data(text[:100])  # Use first 100 chars as query
        fact_check_data = check_google_fact_check(text[:100])
        
        result = {
            'analysis': analysis_result,
            'analysis_type': analysis_type,
            'related_news': news_data,
            'fact_checks': fact_check_data,
            'word_count': len(text.split()),
            'timestamp': datetime.now().isoformat()
        }
        
        # Log the analysis
        if 'user_id' in session:
            log_user_action(session['user_id'], 'news_analysis', result)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"News analysis error: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

# Unified analysis API
@app.route('/api/analyze-unified', methods=['POST'])
@usage_limit_required('unified_analysis')
def analyze_unified():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'No text provided for analysis'}), 400
        
        # Multi-layered analysis
        analyses = {}
        
        # AI Detection
        ai_prompt = """Analyze if this text was likely generated by AI. Consider:
        1. Writing patterns typical of AI
        2. Repetitive phrases or structures
        3. Lack of human nuances
        4. Confidence score (0-100% human vs AI)
        5. Specific indicators found"""
        
        analyses['ai_detection'] = analyze_with_openai(ai_prompt, text)
        
        # Plagiarism check (simplified)
        plagiarism_prompt = """Assess potential plagiarism in this text:
        1. Common phrases that might be copied
        2. Generic language patterns
        3. Lack of original thought indicators
        4. Originality score (0-100%)
        5. Recommendations for verification"""
        
        analyses['plagiarism_check'] = analyze_with_openai(plagiarism_prompt, text)
        
        # Content quality
        quality_prompt = """Evaluate the quality of this content:
        1. Clarity and coherence
        2. Grammar and syntax
        3. Factual accuracy indicators
        4. Overall quality score (0-100%)
        5. Improvement suggestions"""
        
        analyses['quality_assessment'] = analyze_with_openai(quality_prompt, text)
        
        result = {
            'analyses': analyses,
            'word_count': len(text.split()),
            'character_count': len(text),
            'timestamp': datetime.now().isoformat()
        }
        
        # Log the analysis
        if 'user_id' in session:
            log_user_action(session['user_id'], 'unified_analysis', result)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Unified analysis error: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

# Image analysis API
@app.route('/api/analyze-image', methods=['POST'])
@usage_limit_required('image_analysis')
def analyze_image():
    try:
        data = request.get_json()
        image_url = data.get('image_url', '').strip()
        
        if not image_url:
            return jsonify({'error': 'No image URL provided'}), 400
        
        # Simplified image analysis (would need proper image AI integration)
        analysis_prompt = f"""Analyze this image URL for potential manipulation or deepfake indicators:
        URL: {image_url}
        
        Provide assessment of:
        1. Potential digital manipulation signs
        2. Image quality and authenticity indicators
        3. Reverse image search recommendations
        4. Credibility score (0-100%)
        5. Verification steps suggested"""
        
        analysis_result = analyze_with_openai(analysis_prompt, f"Image URL: {image_url}")
        
        result = {
            'analysis': analysis_result,
            'image_url': image_url,
            'timestamp': datetime.now().isoformat()
        }
        
        # Log the analysis
        if 'user_id' in session:
            log_user_action(session['user_id'], 'image_analysis', result)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

# Usage statistics
@app.route('/api/usage-stats')
@login_required
def usage_stats():
    try:
        user_id = session['user_id']
        
        # Get today's usage
        usage_data = execute_db_query(
            """
            SELECT feature_type, usage_count 
            FROM user_usage 
            WHERE user_id = %s AND usage_date = CURRENT_DATE
            """,
            (user_id,),
            fetch=True
        )
        
        usage_dict = {row['feature_type']: row['usage_count'] for row in usage_data} if usage_data else {}
        
        subscription_tier = session.get('subscription_tier', 'free')
        total_limit = Config.DAILY_FREE_LIMIT + (Config.DAILY_PRO_LIMIT if subscription_tier == 'pro' else 0)
        
        return jsonify({
            'usage': usage_dict,
            'limits': {
                'daily_total': total_limit,
                'subscription_tier': subscription_tier
            }
        })
        
    except Exception as e:
        logger.error(f"Usage stats error: {e}")
        return jsonify({'error': 'Failed to fetch usage stats'}), 500

# Health check
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'database': bool(connection_pool),
            'email': EMAIL_AVAILABLE,
            'openai': OPENAI_AVAILABLE,
            'requests': REQUESTS_AVAILABLE,
            'preprocessing': BEAUTIFULSOUP_AVAILABLE
        }
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
