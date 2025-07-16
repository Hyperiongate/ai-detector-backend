# Implementing Playwright on Render.com with GitHub

## Overview
You're using Render.com to host your app and GitHub to store your code. We'll add Playwright to fix the Politico extraction issue. This guide assumes you're using the Render dashboard and GitHub's web interface.

## Step 1: Update Your Requirements File

### 1.1 Go to your GitHub repository
- Open your browser and go to your Facts & Fakes repository on GitHub
- Find the file `requirements.txt` (it should be in the root directory)

### 1.2 Edit requirements.txt
- Click on `requirements.txt`
- Click the pencil icon (✏️) to edit
- Add these lines to the file:
```
playwright==1.40.0
beautifulsoup4==4.12.2
lxml==4.9.3
```

### 1.3 Commit the changes
- Scroll down to "Commit changes"
- Add commit message: "Add Playwright for enhanced news extraction"
- Click "Commit changes"

## Step 2: Create Render Build Script

### 2.1 Create a new file in your repository
- In your GitHub repository, click "Add file" → "Create new file"
- Name it: `build.sh`

### 2.2 Add this content to build.sh:
```bash
#!/usr/bin/env bash
# Build script for Render

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Install system dependencies for Playwright
playwright install-deps
```

### 2.3 Commit the file
- Add commit message: "Add Render build script for Playwright"
- Click "Commit new file"

## Step 3: Update Render Configuration

### 3.1 Create render.yaml
- In GitHub, create another new file named `render.yaml`
- Add this content:

```yaml
services:
  - type: web
    name: factsandfakes
    env: python
    buildCommand: "./build.sh"
    startCommand: "python app.py"
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.16
      - key: PLAYWRIGHT_BROWSERS_PATH
        value: /opt/render/project/.cache/ms-playwright
    autoDeploy: true
```

### 3.2 Commit the file
- Commit message: "Add Render configuration for Playwright support"
- Click "Commit new file"

## Step 4: Create the Enhanced Extractor

### 4.1 Create a new Python file
- In GitHub, create new file: `enhanced_extractor.py`
- Copy this simplified version that works well with Render:

```python
"""
Enhanced News Extractor using Playwright for Render.com
Simplified version optimized for serverless deployment
"""

import logging
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import time

logger = logging.getLogger(__name__)

class EnhancedExtractor:
    @staticmethod
    def extract_article(url):
        """Extract article using Playwright (synchronous version for Render)"""
        browser = None
        try:
            # Launch Playwright
            with sync_playwright() as p:
                # Launch browser with Render-friendly options
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--no-first-run',
                        '--no-zygote',
                        '--single-process',
                        '--disable-gpu'
                    ]
                )
                
                # Create context
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                )
                
                # Create page
                page = context.new_page()
                
                # Set headers
                page.set_extra_http_headers({
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': 'https://www.google.com/'
                })
                
                # Navigate to URL
                logger.info(f"Navigating to {url} with Playwright")
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait for content
                page.wait_for_timeout(2000)
                
                # Get domain
                domain = urlparse(url).netloc.replace('www.', '')
                
                # Handle cookie popups
                try:
                    # Try to click accept cookies button
                    accept_button = page.get_by_role("button", name=re.compile("accept|agree|got it", re.I))
                    if accept_button.is_visible():
                        accept_button.click()
                        page.wait_for_timeout(1000)
                except:
                    pass
                
                # Get page content
                content = page.content()
                
                # Close browser
                browser.close()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract data
                return EnhancedExtractor._parse_content(soup, domain, url)
                
        except Exception as e:
            logger.error(f"Playwright extraction error: {str(e)}")
            if browser:
                browser.close()
            return None
    
    @staticmethod
    def _parse_content(soup, domain, url):
        """Parse content from soup"""
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Extract title
        title = None
        title_selectors = ['h1', 'meta[property="og:title"]', 'title']
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
                    if title:
                        break
        
        if not title:
            title = 'Article Title Not Found'
        
        # Extract content based on domain
        article_text = ""
        
        # Domain-specific selectors
        if domain == 'politico.com':
            selectors = ['div.story-text p', 'main[role="main"] p', 'article p']
        elif domain == 'nytimes.com':
            selectors = ['section[name="articleBody"] p', 'article section p']
        elif domain == 'washingtonpost.com':
            selectors = ['div.article-body p', 'main article p']
        else:
            selectors = ['article p', 'main p', '[role="main"] p', '.article-body p']
        
        for selector in selectors:
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
        
        # Extract author
        author = None
        author_selectors = ['.byline', '.author', 'meta[name="author"]']
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
        
        if not article_text or len(article_text) < 200:
            logger.warning(f"Insufficient content from {domain}")
            return None
        
        return {
            'url': url,
            'domain': domain,
            'title': title,
            'text': article_text[:5000],
            'publish_date': None,
            'author': author
        }

# Simple function for easy import
def extract_with_playwright(url):
    """Simple wrapper function"""
    return EnhancedExtractor.extract_article(url)
```

### 4.2 Commit the file
- Commit message: "Add enhanced extractor with Playwright"
- Click "Commit new file"

## Step 5: Update Your news_analysis.py

### 5.1 Edit news_analysis.py in GitHub
- Find and click on `news_analysis.py`
- Click the pencil icon to edit

### 5.2 Add import at the top
After the other imports, add:
```python
try:
    from enhanced_extractor import extract_with_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not available - using basic extraction only")
```

### 5.3 Find the extract_from_url method
Look for `def extract_from_url(self, url):` and replace the beginning of the method with:

```python
def extract_from_url(self, url):
    """Extract article content from URL with enhanced extraction"""
    start_time = time.time()
    max_duration = 30  # Increased for Playwright
    
    try:
        # Extract domain for early checks
        domain = urlparse(url).netloc.replace('www.', '')
        
        # List of sites that need enhanced extraction
        enhanced_sites = [
            'politico.com',
            'washingtonpost.com',
            'nytimes.com',
            'wsj.com',
            'bloomberg.com',
            'ft.com',
            'economist.com'
        ]
        
        # Use Playwright for difficult sites if available
        if PLAYWRIGHT_AVAILABLE and domain in enhanced_sites:
            logger.info(f"Using Playwright for {domain}")
            article_data = extract_with_playwright(url)
            
            if article_data:
                logger.info(f"Successfully extracted from {domain} using Playwright")
                return article_data
            else:
                logger.warning(f"Playwright extraction failed for {url}, trying standard method")
        
        # Continue with your existing extraction code for other sites
        # [Keep the rest of your existing extract_from_url code here]
```

### 5.4 Commit changes
- Commit message: "Update news analyzer to use Playwright for protected sites"
- Click "Commit changes"

## Step 6: Update Render Environment Variables

### 6.1 Go to Render Dashboard
- Log in to [Render.com](https://render.com)
- Find your Facts & Fakes service
- Click on it to open the service details

### 6.2 Go to Environment
- Click on "Environment" in the left sidebar
- Add these environment variables:
  - `PLAYWRIGHT_BROWSERS_PATH`: `/opt/render/project/.cache/ms-playwright`
  - `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD`: `0`

### 6.3 Save and Deploy
- Click "Save Changes"
- This will trigger a new deployment

## Step 7: Make build.sh Executable

### 7.1 Quick GitHub trick
Since you can't make files executable through GitHub's web interface, update your `build.sh`:

```bash
#!/usr/bin/env bash
# Build script for Render

# Make this script executable
chmod +x build.sh

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Install system dependencies for Playwright
playwright install-deps
```

### 7.2 Commit the change
- Commit message: "Make build script executable"
- Click "Commit changes"

## Step 8: Monitor the Deployment

### 8.1 Watch the deployment
- In Render dashboard, go to "Events" tab
- You'll see the deployment in progress
- Click on it to see the build logs

### 8.2 Check for errors
The build will take 5-10 minutes because it needs to download Chrome. Look for:
- "Successfully installed playwright"
- "Downloading Chromium"
- "Playwright browsers installed"

### 8.3 Common issues
If you see errors:
- **"build.sh not found"**: Make sure the file is in the root of your repository
- **"Permission denied"**: The chmod +x line in build.sh should fix this
- **"Out of memory"**: You may need to upgrade your Render plan

## Step 9: Test Your Implementation

### 9.1 Once deployed successfully
- Go to your Facts & Fakes website
- Try analyzing the Politico article that was failing
- It should now work!

### 9.2 Check logs if it fails
- In Render dashboard, go to "Logs" tab
- Look for error messages
- Common issues:
  - "Playwright not available": Build didn't complete properly
  - "Browser launch failed": Need to check build script
  - "Timeout": Might need to increase timeouts

## You're Done! 🎉

Your app will now:
1. Automatically detect when a site needs Playwright
2. Use a real Chrome browser for those sites
3. Extract content successfully from Politico and similar sites
4. Fall back to fast extraction for simpler sites

## If You Need Help

If something doesn't work:
1. Check the Render logs first
2. Tell me the exact error message
3. Let me know which step you're on

The most common issue is the build taking too long or running out of memory. If this happens, we can optimize the build process.
