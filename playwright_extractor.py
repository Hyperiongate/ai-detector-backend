"""
Playwright-based article extractor for Facts & Fakes AI
Handles sites with anti-bot protection like Politico
Fixed version with better error handling
"""

import logging
import os
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# DO NOT SET CUSTOM BROWSER PATH - use Playwright defaults 
# Remove any custom path that might have been set elsewhere
if 'PLAYWRIGHT_BROWSERS_PATH' in os.environ:
    logger.info(f"Found PLAYWRIGHT_BROWSERS_PATH set to: {os.environ['PLAYWRIGHT_BROWSERS_PATH']}")
    del os.environ['PLAYWRIGHT_BROWSERS_PATH']
    logger.info("Removed custom PLAYWRIGHT_BROWSERS_PATH to use defaults")
else:
    logger.info("No custom PLAYWRIGHT_BROWSERS_PATH found")

# Log where Playwright will look for browsers
try:
    from playwright._impl._driver import get_driver_env
    env = get_driver_env()
    logger.info(f"Playwright will use browsers from: {env.get('PLAYWRIGHT_BROWSERS_PATH', 'default location')}")
except:
    logger.info("Could not determine Playwright browser path")

# Check if Playwright is available
PLAYWRIGHT_AVAILABLE = False
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
    logger.info("Playwright module is available")
except ImportError:
    logger.warning("Playwright not available - will use standard extraction")

def extract_with_playwright(url):
    """
    Extract article content using Playwright
    Returns None if extraction fails
    """
    if not PLAYWRIGHT_AVAILABLE:
        logger.error("Playwright not available but was called")
        return None
    
    browser = None
    try:
        with sync_playwright() as p:
            # First, check if browser is actually available
            try:
                # Try to launch with minimal options
                browser = p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox', '--single-process']
                )
                logger.info("Browser launched successfully")
            except Exception as e:
                # If browser launch fails, log the error and return None
                logger.error(f"Failed to launch browser: {str(e)}")
                
                # Check if it's the executable not found error
                if "Executable doesn't exist" in str(e):
                    logger.error("Chrome executable not found. Playwright browsers may not be properly installed.")
                    logger.error("Try running 'playwright install chromium' in your build script.")
                
                return None
            
            # If we get here, browser launched successfully
            try:
                # Create context with real browser settings
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    extra_http_headers={
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1'
                    }
                )
                
                # Create page
                page = context.new_page()
                
                # Set additional headers
                page.set_extra_http_headers({
                    'Referer': 'https://www.google.com/',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'cross-site',
                    'Sec-Fetch-User': '?1'
                })
                
                # Navigate to URL
                logger.info(f"Playwright: Navigating to {url}")
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait for content to load
                page.wait_for_timeout(2000)
                
                # Get domain
                domain = urlparse(url).netloc.replace('www.', '')
                
                # Try to handle cookie consent
                try:
                    # Common cookie accept button selectors
                    cookie_selectors = [
                        'button:has-text("Accept")',
                        'button:has-text("Accept all")',
                        'button:has-text("I agree")',
                        'button:has-text("Got it")',
                        '[id*="cookie"] button',
                        '[class*="cookie-banner"] button'
                    ]
                    
                    for selector in cookie_selectors:
                        try:
                            button = page.locator(selector).first
                            if button.is_visible():
                                button.click()
                                page.wait_for_timeout(1000)
                                break
                        except:
                            continue
                except:
                    pass  # Cookie handling is best-effort
                
                # Get the page content
                html_content = page.content()
                
                # Close browser
                browser.close()
                browser = None
                
                # Now parse the content using BeautifulSoup
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract data using the same logic as the main extractor
                return extract_data_from_soup(soup, domain, url)
                
            except Exception as e:
                logger.error(f"Error during page navigation/extraction: {str(e)}")
                if browser:
                    browser.close()
                return None
            
    except Exception as e:
        logger.error(f"Playwright extraction error for {url}: {str(e)}")
        if browser:
            try:
                browser.close()
            except:
                pass
        return None

def extract_data_from_soup(soup, domain, url):
    """
    Extract article data from BeautifulSoup object
    This uses the same extraction logic as the main news_analysis.py
    """
    import re
    
    # Remove unwanted elements
    for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'button']):
        element.decompose()
    
    # Extract title
    title = None
    title_selectors = [
        'h1',
        'meta[property="og:title"]',
        'meta[name="twitter:title"]',
        'title',
        '.headline',
        '.article-title'
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
                if title and len(title) > 10:
                    break
    
    if not title:
        title = 'Article Title Not Found'
    
    # Extract content - with special handling for Politico
    article_text = ""
    
    if domain == 'politico.com':
        # Politico-specific selectors
        content_selectors = [
            'div.story-text p',
            'div[class*="story-text"] p',
            'main[role="main"] p',
            'article p',
            'div.content-group p',
            'div.story-main-content p',
            '.story-text__paragraph'
        ]
    else:
        # Generic selectors
        content_selectors = [
            'article p',
            'main p',
            '[role="main"] p',
            '.article-body p',
            '.story-body p',
            '.entry-content p'
        ]
    
    for selector in content_selectors:
        paragraphs = soup.select(selector)
        if paragraphs and len(paragraphs) > 3:
            texts = []
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 20:
                    texts.append(text)
            
            if texts:
                article_text = ' '.join(texts)
                if len(article_text) > 500:
                    break
    
    # If still no content, get all paragraphs
    if not article_text or len(article_text) < 200:
        all_paragraphs = soup.find_all('p')
        good_paragraphs = [p.get_text().strip() for p in all_paragraphs 
                         if len(p.get_text().strip()) > 50]
        
        if len(good_paragraphs) >= 3:
            article_text = ' '.join(good_paragraphs[:30])
    
    # Clean up the text
    article_text = ' '.join(article_text.split())
    
    if len(article_text) < 200:
        logger.warning(f"Insufficient content extracted from {domain}: {len(article_text)} chars")
        return None
    
    # Extract author
    author = None
    author_selectors = [
        'meta[name="author"]',
        '.byline',
        '.author',
        'span.byline-name'
    ]
    
    for selector in author_selectors:
        if selector.startswith('meta'):
            elem = soup.select_one(selector)
            if elem and elem.get('content'):
                author = elem['content'].strip()
                author = re.sub(r'^(By|BY|by)\s+', '', author)
                break
        else:
            elem = soup.select_one(selector)
            if elem:
                author = elem.get_text().strip()
                author = re.sub(r'^(By|BY|by)\s+', '', author)
                if author and ' ' in author:
                    break
    
    # Extract publish date
    publish_date = None
    date_selectors = [
        'time[datetime]',
        'meta[property="article:published_time"]'
    ]
    
    for selector in date_selectors:
        if selector.startswith('meta'):
            elem = soup.select_one(selector)
            if elem and elem.get('content'):
                publish_date = elem['content']
                break
        else:
            elem = soup.select_one(selector)
            if elem and elem.get('datetime'):
                publish_date = elem['datetime']
                break
    
    logger.info(f"Playwright extracted {len(article_text)} chars from {domain}")
    
    return {
        'url': url,
        'domain': domain,
        'title': title,
        'text': article_text[:5000],  # Limit text length
        'publish_date': publish_date,
        'author': author
    }
