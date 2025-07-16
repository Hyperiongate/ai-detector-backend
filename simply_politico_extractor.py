"""
Simple fallback extractor for Politico and other protected sites
Uses alternative methods when Playwright isn't available
"""

import logging
import requests
from bs4 import BeautifulSoup
import time
import json

logger = logging.getLogger(__name__)

def extract_politico_simple(url):
    """
    Try to extract Politico content using various fallback methods
    """
    try:
        domain = 'politico.com'
        
        # Method 1: Try with different user agents
        user_agents = [
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
                        return {
                            'url': url,
                            'domain': domain,
                            'title': title or 'Politico Article',
                            'text': article_text[:5000],
                            'author': 'Politico',
                            'publish_date': None,
                            'extraction_method': f'fallback_{user_agent.split("/")[0]}'
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
                            'author': 'Politico',
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
                        'author': 'Politico',
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
