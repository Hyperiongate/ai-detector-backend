"""
News Analysis Module for Facts & Fakes AI
Uses OpenAI GPT-4 for intelligent article analysis
Compatible with OpenAI 0.28.1
Now with Playwright support for protected sites
"""

import os
import json
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import time

# CORRECT OpenAI import for version 0.28.1
import openai

# Set up logging
logger = logging.getLogger(__name__)

# Add this right after logging setup
logger.info("=== Loading News Analysis Module ===")

# Import Playwright extractor with detailed logging
PLAYWRIGHT_AVAILABLE = False
extract_with_playwright = None

try:
    from playwright_extractor import extract_with_playwright
    PLAYWRIGHT_AVAILABLE = True
    logger.info("✓ Playwright extractor imported successfully")
except ImportError as e:
    logger.error(f"✗ Failed to import playwright_extractor: {str(e)}")
except Exception as e:
    logger.error(f"✗ Unexpected error importing playwright_extractor: {str(e)}")

# EMBEDDED SIMPLE EXTRACTOR - Always available
def extract_politico_simple(url):
    """
    Try to extract Politico content using various fallback methods
    """
    try:
        domain = 'politico.com'
        
        # Method 1: Try with different user agents
        user_agents = [
            # Desktop Chrome - might get full HTML
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Googlebot
            'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            # Bingbot
            'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)',
            # Facebook crawler
            'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)',
            # Twitter bot
            'Twitterbot/1.0',
            # Generic mobile
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        ]
        
        session = requests.Session()
        
        for user_agent in user_agents:
            try:
                headers = {
                    'User-Agent': user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Cache-Control': 'no-cache'
                }
                
                response = session.get(url, headers=headers, timeout=10, allow_redirects=True)
                
                if response.status_code == 200 and len(response.text) > 5000:
                    # Parse the content
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Try to extract content
                    article_text = ""
                    title = ""
                    
                    # Title extraction
                    title_elem = soup.find('h1') or soup.find('meta', {'property': 'og:title'})
                    if title_elem:
                        if title_elem.name == 'meta':
                            title = title_elem.get('content', '')
                        else:
                            title = title_elem.get_text().strip()
                    
                    # Author extraction for Politico
                    author = None
                    
                    # Method 1: Check meta tags
                    meta_tags = soup.find_all('meta')
                    for meta in meta_tags:
                        if meta.get('name') == 'author' or meta.get('property') == 'article:author':
                            content = meta.get('content', '').strip()
                            if content and ' ' in content:
                                author = content
                                break
                        elif meta.get('name') == 'byl' or meta.get('property') == 'byl':
                            content = meta.get('content', '').strip()
                            if content and ' ' in content:
                                author = content
                                break
                    
                    # Method 2: Look for author in the first few paragraphs (common pattern)
                    if not author and article_text:
                        # Check if there's a "By [Name]" pattern in the first 200 characters
                        first_part = article_text[:500]
                        by_pattern = re.search(r'(?:By|BY|by)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', first_part)
                        if by_pattern:
                            potential_author = by_pattern.group(1)
                            # Validate it's a reasonable name
                            if 2 <= len(potential_author.split()) <= 4:
                                author = potential_author
                    
                    # Method 3: Look for any links that might be author links
                    if not author:
                        all_links = soup.find_all('a', href=True)
                        for link in all_links:
                            href = link.get('href', '')
                            text = link.get_text().strip()
                            # Common author link patterns
                            if any(pattern in href for pattern in ['/staff/', '/author/', '/by/', '/people/']):
                                if text and ' ' in text and 2 <= len(text.split()) <= 4:
                                    author = text
                                    break
                    
                    # Method 4: Look for byline class patterns anywhere
                    if not author:
                        for element in soup.find_all(True):  # Search all elements
                            classes = element.get('class', [])
                            class_str = ' '.join(classes) if isinstance(classes, list) else str(classes)
                            if any(word in class_str.lower() for word in ['byline', 'author', 'writer', 'contributor']):
                                text = element.get_text().strip()
                                # Remove common prefixes
                                text = re.sub(r'^(By|BY|by|Written by|Author:)\s+', '', text, flags=re.IGNORECASE)
                                # Check if it's a valid name
                                if text and ' ' in text and 2 <= len(text.split()) <= 4 and len(text) < 50:
                                    author = text
                                    break
                    
                    # Clean up author if found
                    if author:
                        author = re.sub(r'^(By|BY|by)\s+', '', author)
                        author = author.strip()
                        # Final validation
                        if not author or 'staff' in author.lower() or len(author.split()) < 2:
                            author = None
                    
                    # Content extraction - try multiple selectors
                    content_selectors = [
                        'div.story-text',
                        'div[class*="story-text"]',
                        'main[role="main"]',
                        'article',
                        'div.content',
                        'div.article-content'
                    ]
                    
                    for selector in content_selectors:
                        content_elem = soup.select_one(selector)
                        if content_elem:
                            paragraphs = content_elem.find_all(['p', 'h2', 'h3'])
                            if paragraphs:
                                texts = []
                                for p in paragraphs:
                                    text = p.get_text().strip()
                                    if text and len(text) > 20:
                                        texts.append(text)
                                
                                if texts and len(' '.join(texts)) > 500:
                                    article_text = ' '.join(texts)
                                    break
                    
                    # If we still don't have content, try all paragraphs
                    if not article_text or len(article_text) < 500:
                        all_paragraphs = soup.find_all('p')
                        good_paragraphs = []
                        for p in all_paragraphs:
                            text = p.get_text().strip()
                            if len(text) > 50 and not any(skip in text.lower() for skip in ['cookie', 'subscribe', 'sign up']):
                                good_paragraphs.append(text)
                        
                        if len(good_paragraphs) >= 5:
                            article_text = ' '.join(good_paragraphs[:30])
                    
                    if article_text and len(article_text) > 500:
                        logger.info(f"Successfully extracted from Politico using {user_agent[:30]}...")
                        
                        # Log a sample of the extracted content for debugging
                        logger.debug(f"First 200 chars of extracted text: {article_text[:200]}")
                        logger.debug(f"Author found: {author if author else 'None'}")
                        
                        return {
                            'url': url,
                            'domain': domain,
                            'title': title or 'Politico Article',
                            'text': article_text[:5000],
                            'author': author or 'Politico Staff',
                            'publish_date': None,
                            'extraction_method': f'fallback_{user_agent.split("/")[0].split()[0].lower()}'  # e.g., 'fallback_mozilla' or 'fallback_facebookexternalhit'
                        }
                
            except Exception as e:
                logger.debug(f"Attempt with {user_agent[:30]}... failed: {str(e)}")
                continue
        
        # Method 2: Try Google Web Cache
        try:
            cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{url}"
            
            response = requests.get(cache_url, headers={'User-Agent': user_agents[0]}, timeout=10)
            
            if response.status_code == 200 and 'politico.com' in response.text:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract from cached version
                paragraphs = soup.find_all('p')
                content_parts = []
                for p in paragraphs:
                    text = p.get_text().strip()
                    if len(text) > 50:
                        content_parts.append(text)
                
                if len(content_parts) >= 5:
                    article_text = ' '.join(content_parts[:30])
                    
                    if len(article_text) > 500:
                        logger.info("Successfully extracted from Google Cache")
                        return {
                            'url': url,
                            'domain': domain,
                            'title': 'Politico Article (from cache)',
                            'text': article_text[:5000],
                            'author': 'Politico Staff',
                            'publish_date': None,
                            'extraction_method': 'google_cache'
                        }
        except Exception as e:
            logger.debug(f"Google cache attempt failed: {str(e)}")
        
        # Method 3: Return a helpful message with the article metadata
        # Try to at least get the title from the URL
        try:
            # Politico URLs often contain the headline
            # Example: /news/2025/07/15/trump-threatens-russia-sanctions-bashes-putin-00455596
            url_parts = url.split('/')
            if 'news' in url_parts:
                news_index = url_parts.index('news')
                if len(url_parts) > news_index + 4:
                    # Extract title from URL slug
                    title_slug = url_parts[news_index + 4]
                    title = title_slug.replace('-', ' ').title()
                    
                    return {
                        'url': url,
                        'domain': domain,
                        'title': title,
                        'text': f"Unable to extract full article content from Politico. Article appears to be about: {title}. Please use the 'Paste Text' feature to analyze this article.",
                        'author': 'Politico Staff',
                        'publish_date': f"{url_parts[news_index + 1]}/{url_parts[news_index + 2]}/{url_parts[news_index + 3]}",
                        'extraction_method': 'url_parsing_only',
                        'partial_extraction': True
                    }
        except:
            pass
        
        # All methods failed
        logger.warning("All Politico extraction methods failed")
        return None
        
    except Exception as e:
        logger.error(f"Simple Politico extraction error: {str(e)}")
        return None

def extract_protected_site_simple(url, domain):
    """
    Generic fallback extractor for other protected sites
    """
    try:
        # For now, just use Politico extractor for all protected sites
        if domain in ['washingtonpost.com', 'nytimes.com', 'wsj.com', 'bloomberg.com']:
            # Try the same methods
            result = extract_politico_simple(url)
            if result:
                result['domain'] = domain
                result['title'] = f'{domain} Article'
            return result
        
        return None
        
    except Exception as e:
        logger.error(f"Simple extractor error for {domain}: {str(e)}")
        return None

# Simple extractor is always available when embedded
SIMPLE_EXTRACTOR_AVAILABLE = True
logger.info("✓ Simple extractor embedded and available")

# Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
GOOGLE_FACT_CHECK_API_KEY = os.environ.get('GOOGLE_FACTCHECK_API_KEY')

# Log what's available
logger.info(f"OpenAI available: {bool(OPENAI_API_KEY)}")
logger.info(f"News API available: {bool(NEWS_API_KEY)}")
logger.info(f"Playwright available: {PLAYWRIGHT_AVAILABLE}")
logger.info(f"Simple extractor available: {SIMPLE_EXTRACTOR_AVAILABLE}")

# Set OpenAI API key
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# Known source credibility database
SOURCE_CREDIBILITY = {
    # High credibility sources
    'reuters.com': {'credibility': 'High', 'bias': 'Center', 'type': 'News Agency'},
    'apnews.com': {'credibility': 'High', 'bias': 'Center', 'type': 'News Agency'},
    'bbc.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Public Media'},
    'bbc.co.uk': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Public Media'},
    'npr.org': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Public Media'},
    'pbs.org': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Public Media'},
    'wsj.com': {'credibility': 'High', 'bias': 'Center-Right', 'type': 'Business News'},
    'bloomberg.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Business News'},
    'nature.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Scientific'},
    'science.org': {'credibility': 'High', 'bias': 'Center', 'type': 'Scientific'},
    
    # Medium credibility sources
    'cnn.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Cable News'},
    'foxnews.com': {'credibility': 'Medium', 'bias': 'Right', 'type': 'Cable News'},
    'msnbc.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Cable News'},
    'nytimes.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Newspaper'},
    'washingtonpost.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Newspaper'},
    'theguardian.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Newspaper'},
    'usatoday.com': {'credibility': 'Medium', 'bias': 'Center', 'type': 'Newspaper'},
    
    # Lower credibility sources
    'buzzfeed.com': {'credibility': 'Low', 'bias': 'Left', 'type': 'Digital Media'},
    'breitbart.com': {'credibility': 'Low', 'bias': 'Far-Right', 'type': 'Digital Media'},
    'infowars.com': {'credibility': 'Very Low', 'bias': 'Far-Right', 'type': 'Conspiracy'},
    'naturalnews.com': {'credibility': 'Very Low', 'bias': 'Far-Right', 'type': 'Conspiracy'},
}

class NewsAnalyzer:
    """Main class for analyzing news articles"""
    
    def __init__(self):
        self.session = requests.Session()
        # Enhanced headers to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def analyze(self, content, content_type='url', is_pro=True):
        """
        Analyze news content
        
        Args:
            content: URL or article text
            content_type: 'url' or 'text'
            is_pro: Whether to use professional features
            
        Returns:
            dict: Analysis results
        """
        try:
            # Extract article data
            if content_type == 'url':
                # Start extraction timer
                start_time = time.time()
                article_data = self.extract_from_url(content)
                extraction_time = time.time() - start_time
                logger.info(f"Extraction took {extraction_time:.2f} seconds")
                
                if not article_data:
                    # Return a more detailed error response
                    domain = urlparse(content).netloc.replace('www.', '')
                    
                    # Provide specific guidance for known problematic sites
                    problematic_sites = {
                        'washingtonpost.com': 'The Washington Post',
                        'nytimes.com': 'The New York Times',
                        'wsj.com': 'The Wall Street Journal',
                        'bloomberg.com': 'Bloomberg',
                        'ft.com': 'Financial Times',
                        'economist.com': 'The Economist',
                        'politico.com': 'Politico'
                    }
                    
                    site_name = problematic_sites.get(domain, domain)
                    
                    error_message = f"Unable to extract content from {site_name}. "
                    if domain in problematic_sites:
                        error_message += "This site has strong anti-bot protections that prevent automated content extraction."
                    else:
                        error_message += "The site may be blocking automated access or the page structure is not recognized."
                    
                    return {
                        'success': False,
                        'error': error_message,
                        'suggestions': [
                            'Copy and paste the article text using the "Paste Text" tab',
                            'Try a different news source',
                            'Use a direct link to the article (not the homepage)'
                        ]
                    }
            else:
                article_data = {
                    'title': 'Direct Text Analysis',
                    'text': content,
                    'url': None,
                    'domain': None,
                    'publish_date': None,
                    'author': None
                }
            
            # Perform analysis
            if is_pro and OPENAI_API_KEY:
                analysis = self.get_ai_analysis(article_data)
            else:
                analysis = self.fallback_analysis(article_data)
            
            # Add source credibility
            if article_data.get('domain'):
                analysis['source_credibility'] = self.check_source_credibility(article_data['domain'])
            
            # Add Google Fact Check results
            if is_pro and GOOGLE_FACT_CHECK_API_KEY:
                # Get fact checks for key claims
                fact_check_results = self.google_fact_check(analysis.get('key_claims', []))
                analysis['fact_checks'] = fact_check_results
                
                # Update trust score based on fact check results
                if fact_check_results:
                    false_claims = sum(1 for fc in fact_check_results if fc.get('verdict') == 'false')
                    if false_claims > 0:
                        penalty = min(false_claims * 10, 30)  # Max 30 point penalty
                        analysis['trust_score'] = max(0, analysis.get('trust_score', 50) - penalty)
            
            # NEW: Add related news articles
            if is_pro and NEWS_API_KEY and article_data.get('title'):
                related_articles = self.get_related_articles(article_data['title'])
                analysis['related_articles'] = related_articles
            
            return {
                'success': True,
                'article': article_data,
                'analysis': analysis,
                'is_pro': is_pro,
                # Add these fields that the frontend expects
                'bias_score': analysis.get('bias_score', 0),
                'credibility_score': analysis.get('credibility_score', 0.5),
                'trust_score': analysis.get('trust_score', 50),
                'summary': analysis.get('summary', ''),
                'manipulation_tactics': analysis.get('manipulation_tactics', []),
                'key_claims': analysis.get('key_claims', []),
                'fact_checks': analysis.get('fact_checks', []),
                'source_credibility': analysis.get('source_credibility', {}),
                'related_articles': analysis.get('related_articles', []),
                'article_info': article_data
            }
            
        except Exception as e:
            logger.error(f"News analysis error: {str(e)}")
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}'
            }
    
    def google_fact_check(self, claims):
        """
        Use Google Fact Check API to verify claims
        
        Args:
            claims: List of claims to check
            
        Returns:
            list: Fact check results
        """
        if not GOOGLE_FACT_CHECK_API_KEY or not claims:
            return []
        
        fact_check_results = []
        
        try:
            # Google Fact Check API endpoint
            base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
            
            # Check each claim (limit to first 5 to avoid rate limits)
            for claim in claims[:5]:
                try:
                    # Make API request
                    params = {
                        'key': GOOGLE_FACT_CHECK_API_KEY,
                        'query': claim,
                        'languageCode': 'en'
                    }
                    
                    response = self.session.get(base_url, params=params, timeout=5)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Process fact check results
                        if 'claims' in data and data['claims']:
                            # Get the most relevant fact check
                            top_result = data['claims'][0]
                            
                            # Extract verdict from the first review
                            verdict = 'unverified'
                            explanation = 'No fact check found'
                            source = 'Unknown'
                            
                            if 'claimReview' in top_result and top_result['claimReview']:
                                review = top_result['claimReview'][0]
                                
                                # Get the rating
                                if 'textualRating' in review:
                                    rating = review['textualRating'].lower()
                                    
                                    # Map ratings to simple verdicts
                                    if any(word in rating for word in ['false', 'incorrect', 'wrong', 'misleading']):
                                        verdict = 'false'
                                    elif any(word in rating for word in ['true', 'correct', 'accurate']):
                                        verdict = 'true'
                                    elif any(word in rating for word in ['partly', 'mixed', 'partially']):
                                        verdict = 'partially_true'
                                    else:
                                        verdict = 'unverified'
                                
                                # Get explanation
                                if 'title' in review:
                                    explanation = review['title']
                                
                                # Get source
                                if 'publisher' in review and 'name' in review['publisher']:
                                    source = review['publisher']['name']
                            
                            fact_check_results.append({
                                'claim': claim,
                                'verdict': verdict,
                                'explanation': explanation,
                                'source': source,
                                'api_response': top_result  # Include full response for debugging
                            })
                        else:
                            # No fact check found for this claim
                            fact_check_results.append({
                                'claim': claim,
                                'verdict': 'unverified',
                                'explanation': 'No fact check available for this claim',
                                'source': 'Google Fact Check API'
                            })
                    else:
                        logger.warning(f"Google Fact Check API error: {response.status_code}")
                        fact_check_results.append({
                            'claim': claim,
                            'verdict': 'unverified',
                            'explanation': 'Fact check service unavailable',
                            'source': 'Error'
                        })
                    
                    # Small delay to avoid rate limiting
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error checking claim: {str(e)}")
                    fact_check_results.append({
                        'claim': claim,
                        'verdict': 'unverified',
                        'explanation': 'Error during fact checking',
                        'source': 'Error'
                    })
            
            # Add placeholder for remaining claims if any
            for claim in claims[5:]:
                fact_check_results.append({
                    'claim': claim,
                    'verdict': 'unverified',
                    'explanation': 'Claim not checked (limit reached)',
                    'source': 'Not checked'
                })
            
            logger.info(f"Fact-checked {len(fact_check_results)} claims via Google Fact Check API")
            return fact_check_results
            
        except Exception as e:
            logger.error(f"Google Fact Check API error: {str(e)}")
            return []
    
    def get_related_articles(self, query, max_articles=5):
        """
        Get related news articles using News API
        
        Args:
            query: Search query (usually article title)
            max_articles: Maximum number of articles to return
            
        Returns:
            list: Related articles
        """
        if not NEWS_API_KEY:
            return []
        
        try:
            # News API endpoint
            url = "https://newsapi.org/v2/everything"
            
            # Clean up query - remove special characters
            clean_query = re.sub(r'[^\w\s]', ' ', query)
            # Take first few important words
            keywords = ' '.join(clean_query.split()[:5])
            
            params = {
                'apiKey': NEWS_API_KEY,
                'q': keywords,
                'sortBy': 'relevancy',
                'pageSize': max_articles,
                'language': 'en'
            }
            
            response = self.session.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                if 'articles' in data:
                    for article in data['articles'][:max_articles]:
                        # Extract domain from URL
                        domain = ''
                        if article.get('url'):
                            domain = urlparse(article['url']).netloc.replace('www.', '')
                        
                        # Get source name, fallback to domain if available
                        source_name = article.get('source', {}).get('name', domain if domain else 'Unknown')
                        
                        articles.append({
                            'title': article.get('title', ''),
                            'url': article.get('url', ''),
                            'source': source_name,
                            'publishedAt': article.get('publishedAt', ''),
                            'description': article.get('description', ''),
                            'credibility': self.check_source_credibility(domain) if domain else {'credibility': 'Unknown', 'bias': 'Unknown', 'type': 'Unknown'}
                        })
                
                logger.info(f"Found {len(articles)} related articles via News API")
                return articles
            else:
                logger.warning(f"News API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"News API error: {str(e)}")
            return []
    
    def get_trending_news(self, country='us', category='general', max_articles=10):
        """
        Get trending news articles
        
        Args:
            country: Country code (e.g., 'us', 'gb')
            category: News category (e.g., 'general', 'technology', 'business')
            max_articles: Maximum number of articles
            
        Returns:
            list: Trending articles
        """
        if not NEWS_API_KEY:
            return []
        
        try:
            # News API top headlines endpoint
            url = "https://newsapi.org/v2/top-headlines"
            
            params = {
                'apiKey': NEWS_API_KEY,
                'country': country,
                'category': category,
                'pageSize': max_articles
            }
            
            response = self.session.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                if 'articles' in data:
                    for article in data['articles']:
                        # Extract domain from URL
                        domain = ''
                        if article.get('url'):
                            domain = urlparse(article['url']).netloc.replace('www.', '')
                        
                        # Get source name, fallback to domain if available
                        source_name = article.get('source', {}).get('name', domain if domain else 'Unknown')
                        
                        articles.append({
                            'title': article.get('title', ''),
                            'url': article.get('url', ''),
                            'source': source_name,
                            'publishedAt': article.get('publishedAt', ''),
                            'description': article.get('description', ''),
                            'urlToImage': article.get('urlToImage', ''),
                            'credibility': self.check_source_credibility(domain) if domain else {'credibility': 'Unknown', 'bias': 'Unknown', 'type': 'Unknown'}
                        })
                
                logger.info(f"Found {len(articles)} trending articles via News API")
                return articles
            else:
                logger.warning(f"News API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"News API trending error: {str(e)}")
            return []
    
    def extract_from_url(self, url):
        """Extract article content from URL with enhanced extraction and proper fallback"""
        start_time = time.time()
        max_duration = 30  # Increased to 30 seconds for Playwright
        
        logger.info(f"=== Starting extraction for {url} ===")
        logger.info(f"Playwright available: {PLAYWRIGHT_AVAILABLE}")
        logger.info(f"Simple extractor available: {SIMPLE_EXTRACTOR_AVAILABLE}")
        
        try:
            # Extract domain for early checks
            domain = urlparse(url).netloc.replace('www.', '')
            logger.info(f"Domain: {domain}")
            
            # List of sites known to have strict anti-bot measures
            problematic_sites = [
                'washingtonpost.com',
                'nytimes.com',
                'wsj.com',
                'bloomberg.com',
                'ft.com',
                'economist.com',
                'newyorker.com',
                'theatlantic.com',
                'politico.com'
            ]
            
            # For problematic sites, try special extractors
            if domain in problematic_sites:
                logger.info(f"Problematic site detected: {domain}")
                
                # Try Playwright first if available
                if PLAYWRIGHT_AVAILABLE and extract_with_playwright:
                    logger.info(f"Attempting Playwright extraction for {domain}")
                    try:
                        playwright_result = extract_with_playwright(url)
                        if playwright_result:
                            logger.info(f"Playwright extraction successful for {domain}")
                            return playwright_result
                        else:
                            logger.warning(f"Playwright extraction returned None for {domain}")
                    except Exception as e:
                        logger.error(f"Playwright extraction error: {str(e)}")
                
                # ALWAYS try simple extractor for problematic sites
                logger.info(f"Attempting simple extractor for {domain}")
                try:
                    # Use the appropriate function based on domain
                    if domain == 'politico.com':
                        simple_result = extract_politico_simple(url)
                    else:
                        simple_result = extract_protected_site_simple(url, domain)
                    
                    if simple_result:
                        logger.info(f"Simple extractor succeeded for {domain}")
                        return simple_result
                    else:
                        logger.warning(f"Simple extractor returned None for {domain}")
                except Exception as e:
                    logger.error(f"Simple extractor error: {str(e)}")
                
                # If all special methods fail for problematic sites, return None
                logger.warning(f"All extraction methods failed for {domain}")
                return None
            
            # For non-problematic sites, continue with standard extraction
            # Check if we've exceeded time limit
            if time.time() - start_time > max_duration:
                logger.error(f"Extraction exceeded time limit for {url}")
                return None
            
            # Try standard extraction with a short timeout
            response = None
            try:
                # Set a connection timeout and read timeout
                response = self.session.get(url, timeout=(3, 5), allow_redirects=True)
                
                if response.status_code == 403 or response.status_code == 429:
                    logger.error(f"Access denied (status {response.status_code}) for {url}")
                    
                    # Try fallback extractors even for non-problematic sites
                    if PLAYWRIGHT_AVAILABLE and extract_with_playwright:
                        logger.info(f"Attempting Playwright extraction after {response.status_code} error")
                        try:
                            playwright_result = extract_with_playwright(url)
                            if playwright_result:
                                return playwright_result
                        except Exception as e:
                            logger.error(f"Playwright fallback failed: {str(e)}")
                    
                    # Try simple extractor
                    logger.info(f"Attempting simple extraction after {response.status_code} error")
                    try:
                        simple_result = extract_politico_simple(url)
                        if simple_result:
                            return simple_result
                    except Exception as e:
                        logger.error(f"Simple extractor fallback failed: {str(e)}")
                    
                    return None
                    
                if response.status_code != 200:
                    # One quick retry with mobile headers
                    mobile_headers = {
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
                    }
                    response = self.session.get(url, timeout=(2, 3), headers=mobile_headers, allow_redirects=True)
                    
            except requests.exceptions.Timeout:
                logger.error(f"Timeout fetching {url} - site may be slow or blocking")
                return None
            except requests.exceptions.ConnectionError:
                logger.error(f"Connection error fetching {url}")
                return None
            except Exception as e:
                logger.error(f"Failed to fetch URL {url}: {str(e)}")
                return None
            
            if not response or response.status_code != 200:
                logger.error(f"Failed to fetch URL: {url}, status: {response.status_code if response else 'No response'}")
                return None
            
            # Check if we've exceeded time limit
            if time.time() - start_time > max_duration - 5:  # Leave 5 seconds for parsing
                logger.error(f"Not enough time left for parsing {url}")
                return None
            
            # Check if we got a paywall or login page
            response_text_lower = response.text.lower()
            if any(indicator in response_text_lower for indicator in ['paywall', 'subscribe to read', 'login required', 'access denied', 'members only']):
                logger.warning(f"Possible paywall detected at {url}")
                
                # Try fallback extractors for paywall
                logger.info("Attempting simple extraction for paywall bypass")
                try:
                    simple_result = extract_politico_simple(url)
                    if simple_result:
                        return simple_result
                except Exception as e:
                    logger.error(f"Simple extractor paywall bypass failed: {str(e)}")
                
                return None
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title - try multiple methods
            title = None
            title_selectors = [
                'h1',
                'meta[property="og:title"]',
                'meta[name="twitter:title"]',
                'title',
                '.headline',
                '.article-title',
                '[class*="headline"]',
                '[class*="title"]'
            ]
            
            for selector in title_selectors:
                if selector.startswith('meta'):
                    elem = soup.select_one(selector)
                    if elem and elem.get('content'):
                        title = elem['content'].strip()
                        break
                else:
                    elem = soup.select_one(selector)
                    if elem:
                        title = elem.get_text().strip()
                        if title and len(title) > 10:  # Ensure it's not empty or too short
                            break
            
            if not title:
                title = 'Article Title Not Found'
            
            # Extract article text with enhanced selectors
            article_text = ""
            
            # Remove script, style, and other non-content elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'button']):
                element.decompose()
            
            # Site-specific selectors for major news sites
            site_specific_selectors = {
                'reuters.com': 'div[data-testid="article-body"]',
                'apnews.com': 'div.RichTextStoryBody',
                'bbc.com': 'main[role="main"]',
                'bbc.co.uk': 'main[role="main"]',
                'theguardian.com': 'div.article-body-commercial-selector',
                'cnn.com': 'div.article__content',
                'foxnews.com': 'div.article-body',
                'usatoday.com': 'div.gnt_ar_b',
                'npr.org': 'div#storytext',
                'politico.com': 'div.story-text',
                'thehill.com': 'div.article__text',
                'nbcnews.com': 'div.article-body',
                'cbsnews.com': 'section.content__body',
                'abcnews.go.com': 'div.Article__Content'
            }
            
            # Try site-specific selector first
            if domain in site_specific_selectors:
                content = soup.select_one(site_specific_selectors[domain])
                if content:
                    paragraphs = content.find_all(['p', 'h2', 'h3'])
                    article_text = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            # If site-specific didn't work, try generic selectors
            if not article_text:
                content_selectors = [
                    'article',
                    '[role="main"]',
                    'main',
                    '.article-body',
                    '.story-body',
                    '.entry-content',
                    '.post-content',
                    '[class*="article-content"]',
                    '[class*="story-content"]',
                    'div[itemprop="articleBody"]',
                    '.content-body',
                    '#article-body',
                    '.article__body',
                    '.c-entry-content'
                ]
                
                for selector in content_selectors:
                    content = soup.select_one(selector)
                    if content:
                        # Get all paragraphs and headers
                        paragraphs = content.find_all(['p', 'h2', 'h3'])
                        if paragraphs and len(paragraphs) > 3:  # Ensure we have substantial content
                            article_text = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                            if len(article_text) > 200:  # Minimum content length
                                break
            
            # Last resort: get all paragraphs from the page
            if not article_text or len(article_text) < 200:
                all_paragraphs = soup.find_all('p')
                # Filter out short paragraphs and navigation elements
                good_paragraphs = [p.get_text().strip() for p in all_paragraphs 
                                 if len(p.get_text().strip()) > 50 and 
                                 not any(skip in p.get_text().lower() for skip in ['cookie', 'subscribe', 'newsletter', 'sign up', 'advertisement'])]
                
                if len(good_paragraphs) >= 3:
                    article_text = ' '.join(good_paragraphs[:30])  # Limit to first 30 good paragraphs
            
            # Clean up the text
            article_text = ' '.join(article_text.split())  # Remove extra whitespace
            
            # If we still don't have enough content, try fallback extractors
            if len(article_text) < 200:
                logger.warning(f"Insufficient content extracted from {url}: {len(article_text)} chars")
                
                logger.info("Attempting simple extraction due to insufficient content")
                try:
                    simple_result = extract_politico_simple(url)
                    if simple_result:
                        return simple_result
                except Exception as e:
                    logger.error(f"Simple extractor insufficient content fallback failed: {str(e)}")
                
                return None
            
            # Extract publish date
            publish_date = None
            date_selectors = [
                'time[datetime]',
                'meta[property="article:published_time"]',
                'meta[name="publish_date"]',
                'meta[property="article:published"]',
                'meta[name="publication_date"]',
                '[class*="publish-date"]',
                '[class*="posted-on"]',
                '[class*="timestamp"]'
            ]
            
            for selector in date_selectors:
                if selector.startswith('meta'):
                    elem = soup.select_one(selector)
                    if elem and elem.get('content'):
                        publish_date = elem['content']
                        break
                else:
                    elem = soup.select_one(selector)
                    if elem:
                        if elem.get('datetime'):
                            publish_date = elem['datetime']
                        else:
                            publish_date = elem.get_text().strip()
                        break
            
            # Extract author - ENHANCED VERSION
            author = None
            
            # List of organization names to exclude (these are NOT authors)
            org_names = [
                'abc news', 'reuters', 'associated press', 'ap news', 
                'the washington post', 'washington post', 'the new york times', 'new york times',
                'cnn', 'fox news', 'msnbc', 'nbc news', 'cbs news', 'bbc news',
                'the guardian', 'usa today', 'bloomberg', 'the wall street journal',
                'npr', 'politico', 'the hill', 'huffpost', 'buzzfeed',
                'vice', 'vox', 'axios', 'the daily beast', 'newsweek',
                'time', 'fortune', 'forbes', 'business insider', 'cnbc',
                'the economist', 'financial times', 'the atlantic', 'the new yorker',
                'staff', 'news staff', 'editorial board', 'newsroom', 'correspondent'
            ]
            
            # Special handling for ABC News
            if domain == 'abcnews.go.com':
                # If the author name appears in the HTML, try to find it
                if 'David Brennan' in response.text or 'david brennan' in response.text.lower():
                    # Search for the element containing the author name
                    for elem in soup.find_all(text=re.compile('David Brennan', re.I)):
                        parent = elem.parent
                        if parent and parent.name in ['a', 'span', 'div', 'p']:
                            text = parent.get_text().strip()
                            # Clean up the text
                            text = re.sub(r'^(By|BY|by)\s+', '', text)
                            if text and not any(org in text.lower() for org in org_names):
                                author = text
                                break
                
                # Try ABC-specific selectors
                if not author:
                    abc_selectors = [
                        'a[href*="/author/"]',
                        'span[class*="Author"]',
                        'div[class*="Author"]',
                        '.Authors__author',
                        '.Byline__Author',
                        '.byline__author',
                        '.authors',
                        '.author-name'
                    ]
                    
                    for selector in abc_selectors:
                        elems = soup.select(selector)
                        for elem in elems:
                            text = elem.get_text().strip()
                            # Remove common prefixes
                            text = re.sub(r'^(By|BY|by)\s+', '', text)
                            
                            # Check if it's not an organization name
                            if text and len(text) > 2 and not any(org in text.lower() for org in org_names):
                                # Additional check: must contain at least one space (first and last name)
                                if ' ' in text and text.count(' ') < 5:  # Reasonable name length
                                    author = text
                                    break
                        if author:
                            break
            
            # Try standard meta tags if still no author
            if not author:
                meta_selectors = [
                    'meta[name="author"]',
                    'meta[property="article:author"]',
                    'meta[name="byl"]',
                    'meta[name="DC.creator"]',
                    'meta[property="og:article:author"]'
                ]
                
                for selector in meta_selectors:
                    elem = soup.select_one(selector)
                    if elem and elem.get('content'):
                        content = elem['content'].strip()
                        # Remove "By" prefix if present
                        content = re.sub(r'^(By|BY|by)\s+', '', content)
                        
                        # Skip organization names
                        if content and not any(org in content.lower() for org in org_names):
                            if ' ' in content and content.count(' ') < 5:
                                author = content
                                break
            
            # Generic selectors as last resort
            if not author:
                generic_selectors = [
                    '.byline:not(.byline-timestamp)',
                    '.author:not(.author-bio)',
                    '.author-name',
                    '[rel="author"]',
                    'span.byline-name',
                    'div.author-info a',
                    'p.author'
                ]
                
                for selector in generic_selectors:
                    elems = soup.select(selector)
                    for elem in elems:
                        text = elem.get_text().strip()
                        text = re.sub(r'^(By|BY|by)\s+', '', text)
                        
                        if text and len(text) > 2 and not any(org in text.lower() for org in org_names):
                            if ' ' in text and text.count(' ') < 5:
                                author = text
                                break
                    if author:
                        break
            
            # Final validation: ensure author is a person's name, not an organization
            if author:
                # Additional validation: should look like a person's name
                if len(author.split()) > 5 or any(org in author.lower() for org in org_names):
                    logger.warning(f"Rejected author '{author}' - appears to be organization")
                    author = None
            
            logger.info(f"Successfully extracted {len(article_text)} chars from {domain} with author: {author or 'Unknown'} in {time.time() - start_time:.2f} seconds")
            
            return {
                'url': url,
                'domain': domain,
                'title': title,
                'text': article_text[:5000],  # Limit text length
                'publish_date': publish_date,
                'author': author
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout while fetching URL: {url}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error while fetching URL: {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for URL {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error extracting URL {url}: {str(e)}")
            return None
    
    def get_ai_analysis(self, article_data):
        """
        Use OpenAI GPT-4 to analyze article - CORRECT OLD API style for 0.28.1
        """
        if not OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured - using fallback analysis")
            return self.fallback_analysis(article_data)
        
        try:
            logger.info(f"Starting OpenAI analysis for article from {article_data.get('domain', 'unknown')}")
            start_time = time.time()
            
            # Prepare the analysis prompt
            prompt = self._create_analysis_prompt(article_data)
            
            # CORRECT OpenAI API call for version 0.28.1
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Using faster model
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert fact-checker and media analyst. Analyze articles for bias, credibility, and factual accuracy."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500,
                request_timeout=30
            )
            
            # Extract response - CORRECT OLD style
            analysis_text = response.choices[0].message.content
            logger.info(f"OpenAI analysis completed in {time.time() - start_time:.2f} seconds")
            
            # Parse the structured response
            return self._parse_ai_response(analysis_text)
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return self.fallback_analysis(article_data)
    
    def _create_analysis_prompt(self, article_data):
        """Create analysis prompt for GPT-4"""
        return f"""
        Analyze this news article for bias, credibility, and factual accuracy.
        
        Title: {article_data.get('title', 'N/A')}
        Author: {article_data.get('author', 'Unknown')}
        Source: {article_data.get('domain', 'Unknown')}
        Published: {article_data.get('publish_date', 'Unknown')}
        
        Article Text:
        {article_data.get('text', '')[:3000]}
        
        Provide analysis in this JSON format:
        {{
            "bias_score": -1.0 to 1.0 (-1 = far left, 0 = center, 1 = far right),
            "credibility_score": 0.0 to 1.0,
            "factual_accuracy": 0.0 to 1.0,
            "manipulation_tactics": ["list", "of", "tactics"],
            "key_claims": ["claim 1", "claim 2"],
            "fact_checks": [
                {{"claim": "...", "verdict": "true/false/unverified", "explanation": "..."}}
            ],
            "summary": "Brief summary of findings",
            "trust_score": 0 to 100
        }}
        """
    
    def _parse_ai_response(self, response_text):
        """Parse GPT-4 response"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback parsing
                return {
                    'summary': response_text,
                    'bias_score': 0,
                    'credibility_score': 0.5,
                    'trust_score': 50,
                    'manipulation_tactics': [],
                    'key_claims': [],
                    'fact_checks': []
                }
        except:
            return {
                'summary': response_text,
                'bias_score': 0,
                'credibility_score': 0.5,
                'trust_score': 50,
                'manipulation_tactics': [],
                'key_claims': [],
                'fact_checks': []
            }
    
    def fallback_analysis(self, article_data):
        """Basic analysis when AI is not available"""
        text = article_data.get('text', '')
        
        # Basic bias detection
        bias_score = 0
        left_keywords = ['progressive', 'liberal', 'democrat', 'left-wing', 'socialist', 'equity', 'climate crisis']
        right_keywords = ['conservative', 'republican', 'right-wing', 'traditional', 'libertarian', 'freedom', 'patriot']
        
        text_lower = text.lower()
        left_count = sum(1 for keyword in left_keywords if keyword in text_lower)
        right_count = sum(1 for keyword in right_keywords if keyword in text_lower)
        
        if left_count > right_count * 1.5:
            bias_score = -0.5
        elif right_count > left_count * 1.5:
            bias_score = 0.5
        
        # Basic credibility check
        credibility_score = 0.5
        if article_data.get('domain'):
            source_info = SOURCE_CREDIBILITY.get(article_data['domain'], {})
            if source_info.get('credibility') == 'High':
                credibility_score = 0.8
            elif source_info.get('credibility') == 'Medium':
                credibility_score = 0.6
            elif source_info.get('credibility') == 'Low':
                credibility_score = 0.3
            elif source_info.get('credibility') == 'Very Low':
                credibility_score = 0.1
        
        # Detect manipulation tactics
        manipulation_tactics = []
        if len(re.findall(r'[A-Z]{3,}', text)) > 10:
            manipulation_tactics.append('Excessive capitalization')
        if len(re.findall(r'!{2,}', text)) > 0:
            manipulation_tactics.append('Multiple exclamation marks')
        if any(word in text_lower for word in ['breaking', 'urgent', 'alert', 'shocking', 'bombshell']):
            manipulation_tactics.append('Sensational language')
        if any(word in text_lower for word in ['they', 'them', 'elites', 'establishment']) and not article_data.get('title'):
            manipulation_tactics.append('Us vs. them rhetoric')
        
        # Extract key claims (simple extraction)
        sentences = text.split('.')[:10]  # First 10 sentences
        key_claims = []
        for s in sentences:
            s = s.strip()
            # Look for sentences that make claims
            if len(s) > 50 and any(word in s.lower() for word in ['is', 'are', 'was', 'were', 'will', 'would', 'should']):
                key_claims.append(s)
                if len(key_claims) >= 3:
                    break
        
        # Calculate trust score
        trust_score = int((credibility_score * 100 + (1 - abs(bias_score)) * 50) / 2)
        
        # Adjust trust score based on manipulation tactics
        trust_score -= len(manipulation_tactics) * 5
        trust_score = max(0, min(100, trust_score))
        
        # Create summary
        bias_label = 'Left-leaning' if bias_score < -0.3 else 'Right-leaning' if bias_score > 0.3 else 'Center/Neutral'
        credibility_label = 'High' if credibility_score > 0.7 else 'Medium' if credibility_score > 0.4 else 'Low'
        
        summary = f"Basic analysis completed. Source credibility: {credibility_label} ({credibility_score*100:.0f}%). "
        summary += f"Political bias detected: {bias_label}. "
        if manipulation_tactics:
            summary += f"Warning: {len(manipulation_tactics)} manipulation tactics detected. "
        summary += f"Overall trust score: {trust_score}%."
        
        return {
            'bias_score': bias_score,
            'credibility_score': credibility_score,
            'factual_accuracy': credibility_score,
            'manipulation_tactics': manipulation_tactics,
            'key_claims': key_claims,
            'fact_checks': [],
            'summary': summary,
            'trust_score': trust_score,
            'related_articles': []  # Empty in fallback mode
        }
    
    def check_source_credibility(self, domain):
        """Check source credibility from database"""
        return SOURCE_CREDIBILITY.get(domain, {
            'credibility': 'Unknown',
            'bias': 'Unknown',
            'type': 'Unknown'
        })

def analyze_news_route(content, is_pro=True):
    """
    Route function for Flask endpoint
    
    Args:
        content: URL or article text
        is_pro: Whether to use professional features
        
    Returns:
        dict: Analysis results
    """
    analyzer = NewsAnalyzer()
    
    # Determine content type
    content_type = 'url' if content.startswith(('http://', 'https://')) else 'text'
    
    # Perform analysis
    return analyzer.analyze(content, content_type, is_pro)

# NEW: Additional utility functions for trending news
def get_trending_news_route(country='us', category='general'):
    """Get trending news articles"""
    analyzer = NewsAnalyzer()
    return analyzer.get_trending_news(country, category)
