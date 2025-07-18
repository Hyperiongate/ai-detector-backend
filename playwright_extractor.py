"""
Playwright-based article extractor for Facts & Fakes AI
Handles sites with anti-bot protection like Politico and Axios
Enhanced version with stealth techniques
"""

import logging
import os
import random
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Keep the PLAYWRIGHT_BROWSERS_PATH that's set in the environment
# This tells Playwright where to find the browsers we installed
if 'PLAYWRIGHT_BROWSERS_PATH' in os.environ:
    logger.info(f"Using PLAYWRIGHT_BROWSERS_PATH: {os.environ['PLAYWRIGHT_BROWSERS_PATH']}")

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
    Extract article content using Playwright with stealth techniques
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
                # Launch with stealth options
                browser = p.chromium.launch(
                    headless=True,  # Must be headless on Render
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-infobars',
                        '--window-position=0,0',
                        '--ignore-certificate-errors',
                        '--ignore-certificate-errors-spki-list',
                        '--disable-accelerated-2d-canvas',
                        '--disable-gpu',
                        '--window-size=1920,1080',
                        '--start-maximized',
                        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                    ]
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
                # Create context with enhanced stealth settings
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    screen={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    locale='en-US',
                    timezone_id='America/New_York',
                    permissions=['geolocation'],
                    geolocation={'latitude': 40.7128, 'longitude': -74.0060},
                    color_scheme='light',
                    extra_http_headers={
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Cache-Control': 'max-age=0',
                        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="121", "Google Chrome";v="121"',
                        'Sec-Ch-Ua-Mobile': '?0',
                        'Sec-Ch-Ua-Platform': '"Windows"',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'Upgrade-Insecure-Requests': '1'
                    }
                )
                
                # Create page
                page = context.new_page()
                
                # Remove automation indicators
                page.add_init_script("""
                    // Remove webdriver property
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    
                    // Remove automation indicators
                    window.chrome = {
                        runtime: {}
                    };
                    
                    // Add plugins
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [
                            {
                                0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                                description: "Portable Document Format",
                                filename: "internal-pdf-viewer",
                                length: 1,
                                name: "Chrome PDF Plugin"
                            }
                        ]
                    });
                    
                    // Override permissions
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                    
                    // Add realistic window properties
                    Object.defineProperty(navigator, 'hardwareConcurrency', {
                        get: () => 8
                    });
                    
                    Object.defineProperty(navigator, 'deviceMemory', {
                        get: () => 8
                    });
                """)
                
                # Random delay to appear more human
                page.wait_for_timeout(random.randint(500, 1500))
                
                # Navigate to URL with better timeout handling
                logger.info(f"Playwright: Navigating to {url}")
                try:
                    # Navigate first to a benign page (helps with some anti-bot systems)
                    page.goto('https://www.google.com', wait_until='domcontentloaded', timeout=15000)
                    page.wait_for_timeout(random.randint(1000, 2000))
                    
                    # Now navigate to the target URL
                    page.goto(url, wait_until='domcontentloaded', timeout=45000)
                    
                    # Wait for potential Cloudflare challenge
                    page.wait_for_timeout(5000)
                    
                    # Check if we're still on a challenge page
                    page_text = page.content()
                    if 'challenges.cloudflare.com' in page_text or 'Just a moment' in page_text:
                        logger.info("Cloudflare challenge detected, waiting longer...")
                        # Wait up to 15 seconds for challenge to complete
                        try:
                            page.wait_for_selector('article', timeout=15000)
                        except:
                            # Try waiting for any main content indicator
                            page.wait_for_timeout(10000)
                    
                except Exception as timeout_err:
                    logger.warning(f"Initial page load issue: {timeout_err}")
                    # Try one more time with minimal waiting
                    try:
                        page.goto(url, wait_until='commit', timeout=30000)
                        page.wait_for_timeout(5000)
                    except Exception as retry_err:
                        logger.error(f"Page load failed even with retry: {retry_err}")
                        raise
                
                # Get domain
                domain = urlparse(url).netloc.replace('www.', '')
                
                # Try to handle cookie consent with more human-like behavior
                try:
                    # Move mouse to center first
                    page.mouse.move(960, 540)
                    page.wait_for_timeout(random.randint(500, 1000))
                    
                    # Common cookie accept button selectors
                    cookie_selectors = [
                        'button:has-text("Accept")',
                        'button:has-text("Accept all")',
                        'button:has-text("I agree")',
                        'button:has-text("Got it")',
                        'button:has-text("OK")',
                        '[class*="cookie"] button',
                        '[id*="cookie"] button',
                        '[class*="consent"] button'
                    ]
                    
                    for selector in cookie_selectors:
                        try:
                            buttons = page.locator(selector).all()
                            if buttons:
                                button = buttons[0]
                                if button.is_visible():
                                    # Move mouse to button with human-like movement
                                    box = button.bounding_box()
                                    if box:
                                        page.mouse.move(box['x'] + box['width']/2, box['y'] + box['height']/2)
                                        page.wait_for_timeout(random.randint(200, 500))
                                        button.click()
                                        page.wait_for_timeout(random.randint(1000, 2000))
                                        break
                        except:
                            continue
                except:
                    pass  # Cookie handling is best-effort
                
                # Scroll down a bit to trigger lazy loading
                page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.3)")
                page.wait_for_timeout(1500)
                
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
        '.article-title',
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
                if title and len(title) > 10:
                    break
    
    if not title:
        title = 'Article Title Not Found'
    
    # Extract content - with special handling for different sites
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
    elif domain == 'axios.com':
        # Axios-specific selectors
        content_selectors = [
            '[class*="story-module"] p',
            '[class*="gtm-story-text"] p',
            'div[data-module="story"] p',
            'main article p',
            '[class*="content-area"] p',
            'div.story p'
        ]
    else:
        # Generic selectors
        content_selectors = [
            'article p',
            'main p',
            '[role="main"] p',
            '.article-body p',
            '.story-body p',
            '.entry-content p',
            '[class*="article-content"] p',
            '[class*="story-content"] p'
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
        # Add debugging info
        if len(article_text) == 0:
            logger.info(f"Debug - Page title: {title}")
            logger.info(f"Debug - Total paragraphs found: {len(soup.find_all('p'))}")
            logger.info(f"Debug - Page text preview: {soup.get_text()[:500]}")
        return None
    
    # Extract author
    author = None
    author_selectors = [
        'meta[name="author"]',
        '.byline',
        '.author',
        'span.byline-name',
        '[class*="author"]',
        '[class*="byline"]'
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
        'meta[property="article:published_time"]',
        '[class*="publish-date"]',
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
