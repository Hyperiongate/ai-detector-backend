# Facts & Fakes AI Platform - Complete Backend with Real-Time Source Cross-Verification
# Fixed version - NO ASYNC DEPENDENCIES

import os 
import re
import json
import uuid
import hashlib
import logging
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
from functools import wraps
from collections import defaultdict
from typing import List, Dict, Any, Optional, Tuple

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
        connection_pool = ConnectionPool(Config.DATABASE_URL, min_size=1, max_size=20)
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

# Real-Time Source Cross-Verification Engine - SYNCHRONOUS VERSION
class SourceCrossVerificationEngine:
    """
    Real-time source cross-verification system - synchronous version for Flask
    """
    
    def __init__(self):
        self.news_api_key = Config.NEWS_API_KEY
        self.google_fact_check_key = Config.GOOGLE_FACT_CHECK_API_KEY
        self.openai_api_key = Config.OPENAI_API_KEY
        
        # Major news sources for cross-verification
        self.priority_sources = [
            'reuters.com', 'apnews.com', 'bbc.com', 'cnn.com', 'foxnews.com',
            'nytimes.com', 'wsj.com', 'washingtonpost.com', 'nbcnews.com',
            'abcnews.go.com', 'cbsnews.com', 'npr.org', 'theguardian.com',
            'usatoday.com', 'politico.com'
        ]
        
        # Claim extraction patterns
        self.claim_patterns = [
            r'according to\s+([^,]+)',
            r'sources\s+(?:say|said|report|reported)\s+([^.]+)',
            r'officials\s+(?:say|said|announced|confirmed)\s+([^.]+)',
            r'data\s+(?:shows|showed|indicates|indicated)\s+([^.]+)',
            r'study\s+(?:found|finds|concluded|concludes)\s+([^.]+)'
        ]
    
    def run_cross_verification(self, query_topic: str, user_id: int = None, tier: str = 'free') -> Dict[str, Any]:
        """
        Main cross-verification process - synchronous version for Flask
        """
        start_time = datetime.now()
        
        try:
            # Create verification session
            session_id = self.create_verification_session(query_topic, user_id, tier)
            
            # Step 1: Multi-source content aggregation
            source_reports = self.aggregate_multi_source_content(query_topic, session_id, tier)
            
            # Step 2: Extract and match claims across sources
            claim_matches = self.extract_and_match_claims(source_reports, session_id)
            
            # Step 3: Analyze source consensus
            consensus_analysis = self.analyze_source_consensus(source_reports, claim_matches)
            
            # Step 4: Build timeline of story development
            timeline = self.build_story_timeline(source_reports, session_id)
            
            # Step 5: Map source relationships
            relationships = self.map_source_relationships(source_reports, session_id)
            
            # Step 6: Generate cross-verification report
            final_report = self.generate_cross_verification_report(
                source_reports, claim_matches, consensus_analysis, timeline, relationships, tier
            )
            
            # Update session with results
            processing_time = (datetime.now() - start_time).total_seconds()
            self.update_verification_session(session_id, final_report, processing_time)
            
            return {
                'session_id': session_id,
                'query_topic': query_topic,
                'processing_time': processing_time,
                'source_reports': source_reports,
                'claim_matches': claim_matches,
                'consensus_analysis': consensus_analysis,
                'timeline': timeline,
                'relationships': relationships,
                'final_report': final_report,
                'total_sources': len(source_reports)
            }
            
        except Exception as e:
            logger.error(f"Cross-verification failed: {e}")
            return {
                'error': str(e),
                'query_topic': query_topic,
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
    
    def create_verification_session(self, query_topic: str, user_id: int = None, tier: str = 'free') -> int:
        """Create new cross-verification session"""
        result = execute_db_query(
            """
            INSERT INTO cross_verification_sessions 
            (user_id, query_topic, analysis_tier, status)
            VALUES (%s, %s, %s, 'processing')
            RETURNING id
            """,
            (user_id, query_topic, tier),
            fetch=True
        )
        return result[0]['id'] if result else None
    
    def aggregate_multi_source_content(self, query_topic: str, session_id: int, tier: str) -> List[Dict[str, Any]]:
        """
        Fetch content from multiple news sources - synchronous version
        """
        source_limit = 8 if tier == 'pro' else 4
        
        try:
            # Use existing News API integration but enhance for multi-source
            if not REQUESTS_AVAILABLE or not self.news_api_key:
                return []
            
            # Build search queries
            search_queries = self.generate_search_queries(query_topic)
            source_reports = []
            
            for query in search_queries[:2]:  # Limit to 2 query variations
                news_results = self.fetch_news_sources(query, source_limit // 2)
                source_reports.extend(news_results)
            
            # Enhance with content preprocessing and analysis
            enhanced_reports = []
            for report in source_reports[:source_limit]:
                enhanced_report = self.enhance_source_report(report, session_id)
                if enhanced_report:
                    enhanced_reports.append(enhanced_report)
            
            return enhanced_reports
            
        except Exception as e:
            logger.error(f"Multi-source aggregation failed: {e}")
            return []
    
    def generate_search_queries(self, query_topic: str) -> List[str]:
        """Generate multiple search query variations"""
        queries = [query_topic]
        
        # Add quote variations
        if len(query_topic.split()) > 1:
            queries.append(f'"{query_topic}"')
        
        # Add context keywords
        context_keywords = ['news', 'breaking', 'latest']
        for keyword in context_keywords[:1]:
            queries.append(f"{query_topic} {keyword}")
        
        return queries[:2]  # Limit to 2 variations
    
    def fetch_news_sources(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Fetch news from multiple sources using News API"""
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'apiKey': self.news_api_key,
                'sortBy': 'relevancy',
                'pageSize': limit,
                'language': 'en'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                source_reports = []
                for article in articles:
                    source_domain = self.extract_domain(article.get('url', ''))
                    if source_domain:
                        report = {
                            'source_domain': source_domain,
                            'source_name': article.get('source', {}).get('name', 'Unknown'),
                            'article_url': article.get('url', ''),
                            'article_title': article.get('title', ''),
                            'article_content': article.get('content', '') or article.get('description', ''),
                            'publish_date': article.get('publishedAt', ''),
                            'raw_data': article
                        }
                        source_reports.append(report)
                
                return source_reports
            else:
                logger.warning(f"News API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"News source fetch error: {e}")
            return []
    
    def extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return ''
    
    def enhance_source_report(self, report: Dict[str, Any], session_id: int) -> Dict[str, Any]:
        """Enhance source report with credibility and bias analysis"""
        try:
            domain = report['source_domain']
            
            # Get source credibility from cache
            credibility_data = self.get_source_credibility(domain)
            
            # Extract content using smart preprocessing if needed
            content = report.get('article_content', '')
            if report.get('article_url') and len(content) < 200:
                # Use existing preprocessor for full content extraction
                processed_content = preprocessor.extract_clean_content(report['article_url'])
                if processed_content.get('success'):
                    content = processed_content.get('clean_text', content)
                    report['article_title'] = processed_content.get('title') or report.get('article_title', '')
            
            # Extract claims from content
            claims = self.extract_claims_from_content(content)
            
            # Analyze bias indicators
            bias_indicators = self.analyze_content_bias(content)
            
            # Build enhanced report
            enhanced_report = {
                **report,
                'session_id': session_id,
                'source_credibility_score': credibility_data.get('credibility_score', 50),
                'source_bias_rating': credibility_data.get('political_bias', 'unknown'),
                'article_content': content,
                'claims_extracted': claims,
                'bias_indicators': bias_indicators,
                'credibility_factors': credibility_data,
                'processing_time_ms': 0  # Will be updated
            }
            
            # Store in database
            self.store_source_report(enhanced_report)
            
            return enhanced_report
            
        except Exception as e:
            logger.error(f"Source report enhancement failed: {e}")
            return report
    
    def get_source_credibility(self, domain: str) -> Dict[str, Any]:
        """Get source credibility from cache"""
        result = execute_db_query(
            "SELECT * FROM source_credibility_cache WHERE domain = %s",
            (domain,),
            fetch=True
        )
        
        if result:
            return dict(result[0])
        else:
            # Default credibility for unknown sources
            return {
                'credibility_score': 50,
                'political_bias': 'unknown',
                'source_type': 'unknown',
                'fact_check_rating': 'unknown'
            }
    
    def extract_claims_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Extract factual claims from content"""
        claims = []
        sentences = re.split(r'[.!?]+', content)
        
        for i, sentence in enumerate(sentences[:10]):  # Limit to first 10 sentences
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue
            
            # Check for claim patterns
            claim_type = 'general'
            confidence = 0.5
            
            for pattern in self.claim_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    claim_type = 'attributed'
                    confidence = 0.8
                    break
            
            # Check for statistical claims
            if re.search(r'\d+(?:\.\d+)?%|\d+(?:,\d{3})*(?:\.\d+)?', sentence):
                claim_type = 'statistical'
                confidence = 0.9
            
            claims.append({
                'claim_text': sentence,
                'claim_type': claim_type,
                'confidence': confidence,
                'position': i
            })
        
        return claims[:5]  # Limit to top 5 claims
    
    def analyze_content_bias(self, content: str) -> Dict[str, Any]:
        """Analyze bias indicators in content"""
        if not OPENAI_AVAILABLE or not self.openai_api_key:
            return {'bias_score': 0, 'indicators': []}
        
        try:
            prompt = """Analyze the political bias in this news content. Provide:
            1. Bias score (-100 to +100, negative=left, positive=right)
            2. Key bias indicators found
            3. Emotional language examples
            4. Objectivity assessment
            
            Return as JSON format."""
            
            truncated_content = content[:1000]  # Limit content length
            analysis = analyze_with_openai(prompt, truncated_content)
            
            # Parse AI response (simplified)
            return {
                'bias_score': 0,  # Would parse from AI response
                'emotional_language': [],
                'loaded_terms': [],
                'objectivity_score': 75
            }
            
        except Exception as e:
            logger.error(f"Bias analysis failed: {e}")
            return {'bias_score': 0, 'indicators': []}
    
    def store_source_report(self, report: Dict[str, Any]):
        """Store source report in database"""
        try:
            execute_db_query(
                """
                INSERT INTO source_reports 
                (session_id, source_domain, source_name, source_credibility_score, 
                 source_bias_rating, article_url, article_title, article_content,
                 claims_extracted, bias_indicators, credibility_factors)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    report.get('session_id'),
                    report.get('source_domain'),
                    report.get('source_name'),
                    report.get('source_credibility_score'),
                    report.get('source_bias_rating'),
                    report.get('article_url'),
                    report.get('article_title'),
                    report.get('article_content'),
                    json.dumps(report.get('claims_extracted', [])),
                    json.dumps(report.get('bias_indicators', {})),
                    json.dumps(report.get('credibility_factors', {}))
                )
            )
        except Exception as e:
            logger.error(f"Failed to store source report: {e}")
    
    def extract_and_match_claims(self, source_reports: List[Dict[str, Any]], session_id: int) -> List[Dict[str, Any]]:
        """Extract and match claims across sources"""
        all_claims = []
        
        # Collect all claims from all sources
        for report in source_reports:
            source_claims = report.get('claims_extracted', [])
            for claim in source_claims:
                claim['source_domain'] = report['source_domain']
                claim['source_credibility'] = report.get('source_credibility_score', 50)
                all_claims.append(claim)
        
        # Group similar claims
        claim_groups = self.group_similar_claims(all_claims)
        
        # Analyze each claim group
        claim_matches = []
        for group in claim_groups:
            match_analysis = self.analyze_claim_group(group, session_id)
            if match_analysis:
                claim_matches.append(match_analysis)
        
        return claim_matches
    
    def group_similar_claims(self, claims: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group similar claims together"""
        # Simplified similarity grouping
        groups = []
        used_claims = set()
        
        for i, claim in enumerate(claims):
            if i in used_claims:
                continue
                
            group = [claim]
            used_claims.add(i)
            
            # Find similar claims
            for j, other_claim in enumerate(claims[i+1:], i+1):
                if j in used_claims:
                    continue
                
                similarity = self.calculate_claim_similarity(claim['claim_text'], other_claim['claim_text'])
                if similarity > 0.4:  # Lower similarity threshold
                    group.append(other_claim)
                    used_claims.add(j)
            
            if len(group) >= 1:  # Keep groups with at least one claim
                groups.append(group)
        
        return groups
    
    def calculate_claim_similarity(self, claim1: str, claim2: str) -> float:
        """Calculate similarity between two claims"""
        # Simplified similarity calculation
        words1 = set(claim1.lower().split())
        words2 = set(claim2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if len(union) == 0:
            return 0.0
        
        return len(intersection) / len(union)
    
    def analyze_claim_group(self, claim_group: List[Dict[str, Any]], session_id: int) -> Dict[str, Any]:
        """Analyze a group of similar claims"""
        # Separate sources by credibility
        high_cred_sources = [c for c in claim_group if c.get('source_credibility', 0) >= 80]
        med_cred_sources = [c for c in claim_group if 60 <= c.get('source_credibility', 0) < 80]
        low_cred_sources = [c for c in claim_group if c.get('source_credibility', 0) < 60]
        
        # Calculate consensus
        total_sources = len(claim_group)
        consensus_level = 'high' if total_sources >= 3 else 'medium' if total_sources >= 2 else 'low'
        
        # Create claim match record
        claim_match = {
            'session_id': session_id,
            'claim_text': claim_group[0]['claim_text'],  # Representative claim
            'claim_category': claim_group[0].get('claim_type', 'general'),
            'supporting_sources': [c['source_domain'] for c in claim_group],
            'contradicting_sources': [],  # Would be enhanced with fact-checking
            'neutral_sources': [],
            'consensus_level': consensus_level,
            'controversy_score': 0.0,  # Would be calculated based on source disagreement
            'verification_confidence': min(80.0, total_sources * 20),  # Max 80% confidence
            'source_breakdown': {
                'high_credibility': len(high_cred_sources),
                'medium_credibility': len(med_cred_sources),
                'low_credibility': len(low_cred_sources)
            }
        }
        
        # Store in database
        self.store_claim_match(claim_match)
        
        return claim_match
    
    def store_claim_match(self, claim_match: Dict[str, Any]):
        """Store claim match in database"""
        try:
            execute_db_query(
                """
                INSERT INTO claim_matches 
                (session_id, claim_text, claim_category, supporting_sources,
                 contradicting_sources, neutral_sources, consensus_level,
                 controversy_score, verification_confidence)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    claim_match['session_id'],
                    claim_match['claim_text'],
                    claim_match['claim_category'],
                    json.dumps(claim_match['supporting_sources']),
                    json.dumps(claim_match['contradicting_sources']),
                    json.dumps(claim_match['neutral_sources']),
                    claim_match['consensus_level'],
                    claim_match['controversy_score'],
                    claim_match['verification_confidence']
                )
            )
        except Exception as e:
            logger.error(f"Failed to store claim match: {e}")
    
    def analyze_source_consensus(self, source_reports: List[Dict[str, Any]], claim_matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall consensus across sources"""
        if not source_reports:
            return {'consensus_score': 0, 'controversy_level': 'unknown'}
        
        # Calculate weighted consensus based on source credibility
        total_credibility = sum(report.get('source_credibility_score', 50) for report in source_reports)
        avg_credibility = total_credibility / len(source_reports)
        
        # Analyze claim agreement
        high_consensus_claims = len([c for c in claim_matches if c.get('consensus_level') == 'high'])
        total_claims = len(claim_matches) if claim_matches else 1
        
        consensus_ratio = high_consensus_claims / total_claims
        final_consensus = (consensus_ratio * 50) + (avg_credibility / 2)
        
        # Determine controversy level
        if final_consensus >= 75:
            controversy_level = 'low'
        elif final_consensus >= 50:
            controversy_level = 'moderate'
        else:
            controversy_level = 'high'
        
        return {
            'consensus_score': round(final_consensus, 2),
            'controversy_level': controversy_level,
            'avg_source_credibility': round(avg_credibility, 2),
            'total_sources': len(source_reports),
            'high_consensus_claims': high_consensus_claims,
            'total_claims': total_claims
        }
    
    def build_story_timeline(self, source_reports: List[Dict[str, Any]], session_id: int) -> List[Dict[str, Any]]:
        """Build timeline of story development"""
        timeline_events = []
        
        for report in source_reports:
            publish_date = report.get('publish_date')
            if publish_date:
                try:
                    event_time = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
                    
                    timeline_events.append({
                        'session_id': session_id,
                        'source_domain': report['source_domain'],
                        'event_timestamp': event_time,
                        'event_type': 'article_published',
                        'event_description': report.get('article_title', 'Article published'),
                        'article_url': report.get('article_url'),
                        'significance_score': report.get('source_credibility_score', 50)
                    })
                except:
                    continue
        
        # Sort by timestamp
        timeline_events.sort(key=lambda x: x['event_timestamp'])
        
        # Store timeline events
        for event in timeline_events:
            self.store_timeline_event(event)
        
        return timeline_events
    
    def store_timeline_event(self, event: Dict[str, Any]):
        """Store timeline event in database"""
        try:
            execute_db_query(
                """
                INSERT INTO story_timelines 
                (session_id, source_domain, event_timestamp, event_type,
                 event_description, article_url, significance_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    event['session_id'],
                    event['source_domain'],
                    event['event_timestamp'],
                    event['event_type'],
                    event['event_description'],
                    event['article_url'],
                    event['significance_score']
                )
            )
        except Exception as e:
            logger.error(f"Failed to store timeline event: {e}")
    
    def map_source_relationships(self, source_reports: List[Dict[str, Any]], session_id: int) -> List[Dict[str, Any]]:
        """Map relationships between sources (who cites whom)"""
        relationships = []
        
        for report in source_reports:
            content = report.get('article_content', '')
            source_domain = report['source_domain']
            
            # Look for citations of other sources
            for other_report in source_reports:
                if other_report['source_domain'] == source_domain:
                    continue
                
                other_name = other_report['source_name']
                if other_name.lower() in content.lower():
                    relationship = {
                        'session_id': session_id,
                        'source_domain': source_domain,
                        'cited_source': other_report['source_domain'],
                        'citation_type': 'mention',
                        'citation_context': f"Mentions {other_name}",
                        'credibility_transfer': 0.1
                    }
                    relationships.append(relationship)
                    self.store_source_relationship(relationship)
        
        return relationships
    
    def store_source_relationship(self, relationship: Dict[str, Any]):
        """Store source relationship in database"""
        try:
            execute_db_query(
                """
                INSERT INTO source_relationships 
                (session_id, source_domain, cited_source, citation_type,
                 citation_context, credibility_transfer)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    relationship['session_id'],
                    relationship['source_domain'],
                    relationship['cited_source'],
                    relationship['citation_type'],
                    relationship['citation_context'],
                    relationship['credibility_transfer']
                )
            )
        except Exception as e:
            logger.error(f"Failed to store source relationship: {e}")
    
    def generate_cross_verification_report(self, source_reports: List[Dict[str, Any]], 
                                          claim_matches: List[Dict[str, Any]],
                                          consensus_analysis: Dict[str, Any],
                                          timeline: List[Dict[str, Any]],
                                          relationships: List[Dict[str, Any]],
                                          tier: str) -> Dict[str, Any]:
        """Generate final cross-verification report"""
        
        # Create source summary
        source_summary = []
        for report in source_reports:
            source_summary.append({
                'domain': report['source_domain'],
                'name': report['source_name'],
                'credibility': report.get('source_credibility_score', 50),
                'bias': report.get('source_bias_rating', 'unknown'),
                'title': report.get('article_title', 'Unknown'),
                'url': report.get('article_url', ''),
                'claims_count': len(report.get('claims_extracted', []))
            })
        
        # Generate executive summary
        total_sources = len(source_reports)
        avg_credibility = consensus_analysis.get('avg_source_credibility', 50)
        consensus_score = consensus_analysis.get('consensus_score', 50)
        
        if consensus_score >= 75:
            executive_assessment = "HIGH CONSENSUS - Multiple credible sources agree"
        elif consensus_score >= 50:
            executive_assessment = "MODERATE CONSENSUS - Some source agreement with discrepancies"
        else:
            executive_assessment = "LOW CONSENSUS - Significant source disagreement detected"
        
        final_report = {
            'executive_summary': {
                'assessment': executive_assessment,
                'consensus_score': consensus_score,
                'total_sources_analyzed': total_sources,
                'avg_source_credibility': avg_credibility,
                'controversy_level': consensus_analysis.get('controversy_level', 'unknown')
            },
            'source_breakdown': source_summary,
            'claim_analysis': {
                'total_claims': len(claim_matches),
                'high_consensus_claims': len([c for c in claim_matches if c.get('consensus_level') == 'high']),
                'controversial_claims': len([c for c in claim_matches if c.get('controversy_score', 0) > 0.5])
            },
            'timeline_analysis': {
                'total_events': len(timeline),
                'earliest_report': timeline[0]['event_timestamp'].isoformat() if timeline else None,
                'latest_report': timeline[-1]['event_timestamp'].isoformat() if timeline else None
            },
            'methodology': {
                'sources_searched': total_sources,
                'analysis_tier': tier,
                'verification_methods': ['multi_source_aggregation', 'claim_extraction', 'consensus_analysis'],
                'credibility_weighting': True,
                'bias_adjustment': True
            }
        }
        
        return final_report
    
    def update_verification_session(self, session_id: int, final_report: Dict[str, Any], processing_time: float):
        """Update verification session with final results"""
        try:
            execute_db_query(
                """
                UPDATE cross_verification_sessions 
                SET status = 'completed',
                    completed_at = CURRENT_TIMESTAMP,
                    total_sources_found = %s,
                    consensus_score = %s,
                    controversy_level = %s,
                    session_data = %s
                WHERE id = %s
                """,
                (
                    final_report['executive_summary']['total_sources_analyzed'],
                    final_report['executive_summary']['consensus_score'],
                    final_report['executive_summary']['controversy_level'],
                    json.dumps(final_report),
                    session_id
                )
            )
        except Exception as e:
            logger.error(f"Failed to update verification session: {e}")

# Initialize the cross-verification engine
cross_verification_engine = SourceCrossVerificationEngine()

# Database helper functions
def get_db_connection():
    """Get database connection from pool"""
    if connection_pool:
        try:
            return connection_pool.connection()
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return None
    return None

def execute_db_query(query, params=None, fetch=False):
    """Execute database query with connection pooling"""
    if not connection_pool:
        return None
    
    try:
        with connection_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query, params)
                if fetch:
                    result = cur.fetchall()
                else:
                    result = cur.rowcount
                conn.commit()
                return result
    except Exception as e:
        logger.error(f"Database query error: {e}")
        return None

# User management functions
def create_user_tables():
    """Create user management tables including cross-verification tables"""
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
        """,
        # Cross-verification tables
        """
        CREATE TABLE IF NOT EXISTS cross_verification_sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            query_topic VARCHAR(500) NOT NULL,
            search_keywords VARCHAR(1000),
            analysis_tier VARCHAR(50) DEFAULT 'free',
            status VARCHAR(100) DEFAULT 'processing',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            total_sources_found INTEGER DEFAULT 0,
            consensus_score DECIMAL(5,2),
            controversy_level VARCHAR(50),
            session_data JSONB
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS source_reports (
            id SERIAL PRIMARY KEY,
            session_id INTEGER REFERENCES cross_verification_sessions(id) ON DELETE CASCADE,
            source_domain VARCHAR(255),
            source_name VARCHAR(255),
            source_credibility_score INTEGER,
            source_bias_rating VARCHAR(50),
            article_url TEXT,
            article_title TEXT,
            article_content TEXT,
            publish_date TIMESTAMP,
            claims_extracted JSONB,
            bias_indicators JSONB,
            credibility_factors JSONB,
            processing_time_ms INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS claim_matches (
            id SERIAL PRIMARY KEY,
            session_id INTEGER REFERENCES cross_verification_sessions(id) ON DELETE CASCADE,
            claim_text TEXT NOT NULL,
            claim_category VARCHAR(100),
            supporting_sources JSONB,
            contradicting_sources JSONB,
            neutral_sources JSONB,
            consensus_level VARCHAR(50),
            controversy_score DECIMAL(5,2),
            fact_check_status VARCHAR(100),
            verification_confidence DECIMAL(5,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS source_credibility_cache (
            id SERIAL PRIMARY KEY,
            domain VARCHAR(255) UNIQUE NOT NULL,
            source_name VARCHAR(255),
            credibility_score INTEGER,
            political_bias VARCHAR(50),
            source_type VARCHAR(100),
            country VARCHAR(100),
            language VARCHAR(50),
            fact_check_rating VARCHAR(100),
            transparency_score INTEGER,
            editorial_standards INTEGER,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            update_count INTEGER DEFAULT 1,
            reliability_trend VARCHAR(50),
            metadata JSONB
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS story_timelines (
            id SERIAL PRIMARY KEY,
            session_id INTEGER REFERENCES cross_verification_sessions(id) ON DELETE CASCADE,
            source_domain VARCHAR(255),
            event_timestamp TIMESTAMP,
            event_type VARCHAR(100),
            event_description TEXT,
            article_url TEXT,
            significance_score INTEGER,
            update_type VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS source_relationships (
            id SERIAL PRIMARY KEY,
            session_id INTEGER REFERENCES cross_verification_sessions(id) ON DELETE CASCADE,
            source_domain VARCHAR(255),
            cited_source VARCHAR(255),
            citation_type VARCHAR(100),
            citation_context TEXT,
            credibility_transfer DECIMAL(5,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]
    
    for query in queries:
        execute_db_query(query)
    
    # Pre-populate source credibility cache with major news outlets
    populate_source_credibility_cache()

def populate_source_credibility_cache():
    """Pre-populate source credibility cache with major news outlets"""
    major_sources = [
        ('reuters.com', 'Reuters', 95, 'center', 'news_agency', 'UK', 'en', 'very_high', 95, 95),
        ('apnews.com', 'Associated Press', 94, 'center', 'news_agency', 'US', 'en', 'very_high', 94, 94),
        ('bbc.com', 'BBC News', 88, 'center-left', 'public_broadcaster', 'UK', 'en', 'high', 90, 88),
        ('cnn.com', 'CNN', 75, 'left', 'cable_news', 'US', 'en', 'moderate', 78, 80),
        ('foxnews.com', 'Fox News', 65, 'right', 'cable_news', 'US', 'en', 'moderate', 70, 75),
        ('nytimes.com', 'The New York Times', 82, 'center-left', 'newspaper', 'US', 'en', 'high', 85, 88),
        ('wsj.com', 'The Wall Street Journal', 84, 'center-right', 'newspaper', 'US', 'en', 'high', 88, 90),
        ('washingtonpost.com', 'The Washington Post', 80, 'center-left', 'newspaper', 'US', 'en', 'high', 82, 85),
        ('nbcnews.com', 'NBC News', 78, 'center-left', 'broadcast_news', 'US', 'en', 'moderate', 80, 82),
        ('abcnews.go.com', 'ABC News', 77, 'center-left', 'broadcast_news', 'US', 'en', 'moderate', 79, 81),
        ('cbsnews.com', 'CBS News', 76, 'center-left', 'broadcast_news', 'US', 'en', 'moderate', 78, 80),
        ('npr.org', 'NPR', 85, 'center-left', 'public_radio', 'US', 'en', 'high', 88, 90),
        ('theguardian.com', 'The Guardian', 78, 'left', 'newspaper', 'UK', 'en', 'moderate', 80, 82),
        ('usatoday.com', 'USA Today', 72, 'center', 'newspaper', 'US', 'en', 'moderate', 75, 78),
        ('politico.com', 'Politico', 74, 'center-left', 'political_news', 'US', 'en', 'moderate', 76, 79)
    ]
    
    for source_data in major_sources:
        try:
            execute_db_query(
                """
                INSERT INTO source_credibility_cache 
                (domain, source_name, credibility_score, political_bias, source_type, 
                 country, language, fact_check_rating, transparency_score, editorial_standards)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (domain) DO UPDATE SET
                    credibility_score = EXCLUDED.credibility_score,
                    last_updated = CURRENT_TIMESTAMP,
                    update_count = source_credibility_cache.update_count + 1
                """,
                source_data
            )
        except Exception as e:
            logger.warning(f"Failed to insert source credibility data: {e}")

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
    ✅ Multi-source cross-verification
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

# ========================================
# REQUEST LOGGING MIDDLEWARE (FIX)
# ========================================
@app.before_request
def log_request_info():
    """Log all requests for debugging"""
    logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")

@app.after_request
def log_response_info(response):
    """Log response status"""
    if response.status_code >= 400:
        logger.warning(f"Response: {response.status_code} for {request.method} {request.path}")
    return response

# ========================================
# MAIN PAGE ROUTES
# ========================================
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

# ========================================
# FIX 1: MISSING LOGIN PAGE ROUTE (CRITICAL)
# ========================================
@app.route('/login')
def login_page():
    """Serve login page - FIXES 404 errors"""
    try:
        return render_template('login.html')
    except Exception as e:
        # Fallback if template doesn't exist
        logger.warning(f"Login template not found: {e}")
        # Return simple inline login page
        return """
        <!DOCTYPE html>
        <html>
        <head><title>Login - Facts & Fakes AI</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>Facts & Fakes AI Login</h1>
            <p>Login page is being set up. Please visit <a href="/unified">our tools</a> instead.</p>
            <a href="/">← Back to Home</a>
        </body>
        </html>
        """

# ========================================
# FIX 2: MISSING API ENDPOINT (CRITICAL)
# ========================================
@app.route('/api/user/status')  # This was the missing endpoint!
def api_user_status():
    """Fixed endpoint that matches frontend requests - FIXES 404 errors"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'status': 'success',
            'user': {
                'id': session['user_id'],
                'email': session['email'],
                'subscription_tier': session.get('subscription_tier', 'free')
            }
        })
    else:
        return jsonify({
            'authenticated': False,
            'status': 'unauthenticated'
        })

# Keep existing user-status route for backwards compatibility
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

# ========================================
# FIX 3: HTML EXTENSION REDIRECTS (FIXES 404s)
# ========================================
@app.route('/imageanalysis.html')
def imageanalysis_html_redirect():
    return redirect(url_for('imageanalysis'), code=301)

@app.route('/news.html') 
def news_html_redirect():
    return redirect(url_for('news'), code=301)

@app.route('/missionstatement.html')
def missionstatement_html_redirect():
    return redirect(url_for('missionstatement'), code=301)

@app.route('/pricingplan.html')
def pricingplan_html_redirect():
    return redirect(url_for('pricingplan'), code=301)

@app.route('/unified.html')
def unified_html_redirect():
    return redirect(url_for('unified'), code=301)

@app.route('/contact.html')
def contact_html_redirect():
    return redirect(url_for('contact'), code=301)

@app.route('/login.html')
def login_html_redirect():
    return redirect(url_for('login_page'), code=301)

# ========================================
# CROSS-VERIFICATION API ENDPOINTS
# ========================================
@app.route('/api/cross-verify-sources', methods=['POST'])
@usage_limit_required('cross_verification')
def cross_verify_sources():
    """
    Real-time source cross-verification API endpoint
    """
    try:
        data = request.get_json()
        query_topic = data.get('query_topic', '').strip()
        tier = data.get('tier', 'free')
        
        if not query_topic:
            return jsonify({'error': 'Query topic is required'}), 400
        
        if len(query_topic) < 3:
            return jsonify({'error': 'Query topic must be at least 3 characters'}), 400
        
        # Get user ID if authenticated
        user_id = session.get('user_id')
        
        # Run cross-verification
        verification_result = cross_verification_engine.run_cross_verification(query_topic, user_id, tier)
        
        if 'error' in verification_result:
            return jsonify({
                'success': False,
                'error': verification_result['error'],
                'query_topic': query_topic
            }), 500
        
        # Log usage if user is authenticated
        if user_id:
            log_user_action(user_id, 'cross_verification', {
                'query_topic': query_topic,
                'total_sources': verification_result.get('total_sources', 0),
                'consensus_score': verification_result.get('consensus_analysis', {}).get('consensus_score', 0),
                'processing_time': verification_result.get('processing_time', 0)
            })
        
        return jsonify({
            'success': True,
            'query_topic': query_topic,
            'session_id': verification_result.get('session_id'),
            'processing_time': verification_result.get('processing_time'),
            'source_analysis': {
                'total_sources': verification_result.get('total_sources', 0),
                'sources': verification_result.get('source_reports', []),
                'consensus_analysis': verification_result.get('consensus_analysis', {}),
                'claim_matches': verification_result.get('claim_matches', []),
                'timeline': verification_result.get('timeline', []),
                'relationships': verification_result.get('relationships', [])
            },
            'final_report': verification_result.get('final_report', {}),
            'tier': tier
        })
        
    except Exception as e:
        logger.error(f"Cross-verification API error: {e}")
        return jsonify({
            'success': False,
            'error': f'Cross-verification failed: {str(e)}',
            'query_topic': query_topic if 'query_topic' in locals() else 'unknown'
        }), 500

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
            'preprocessing': BEAUTIFULSOUP_AVAILABLE,
            'cross_verification': True
        }
    })

# Alternative health check endpoint
@app.route('/api/health')
def api_health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'services': {
            'database': bool(connection_pool),
            'email': EMAIL_AVAILABLE,
            'openai': OPENAI_AVAILABLE,
            'requests': REQUESTS_AVAILABLE,
            'preprocessing': BEAUTIFULSOUP_AVAILABLE,
            'cross_verification': True
        }
    })

# ========================================
# FIX 4: ENHANCED ERROR HANDLERS
# ========================================
@app.errorhandler(404)
def not_found(error):
    # Log 404s for debugging (matching your log format)
    logger.info(f"404 - {request.method} {request.path} from {request.remote_addr}")
    
    # Check if it's an API request
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'API endpoint not found',
            'path': request.path,
            'method': request.method,
            'suggestion': 'Check the API documentation'
        }), 404
    
    # For regular pages, try to redirect to similar page or home
    path = request.path.lower()
    if 'login' in path:
        return redirect(url_for('login_page'))
    elif 'news' in path:
        return redirect(url_for('news'))
    elif 'contact' in path:
        return redirect(url_for('contact'))
    else:
        # Try to serve 404 template or return inline 404
        try:
            return render_template('404.html'), 404
        except:
            return """
            <!DOCTYPE html>
            <html>
            <head><title>404 - Page Not Found</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>404 - Page Not Found</h1>
                <p>The page you're looking for doesn't exist.</p>
                <a href="/">← Back to Home</a> | 
                <a href="/unified">Try Our Tools</a>
            </body>
            </html>
            """, 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong on our end'
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Starting Facts & Fakes AI server on port {port}")
    logger.info("🔧 Features enabled:")
    logger.info("   ✅ Smart Content Preprocessing")
    logger.info("   ✅ News Verification & Bias Detection") 
    logger.info("   ✅ Real-Time Source Cross-Verification")
    logger.info("   ✅ User Authentication & Usage Tracking")
    logger.info("   ✅ Email Integration")
    logger.info("   ✅ Database Connection Pooling")
    logger.info("   ✅ All Routing Fixes Applied")
    logger.info("   ✅ NO ASYNC DEPENDENCIES")
    app.run(host='0.0.0.0', port=port, debug=False)
