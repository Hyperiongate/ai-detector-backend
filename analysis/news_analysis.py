"""
News Analysis Module for Facts & Fakes AI
Uses OpenAI GPT-4 for intelligent article analysis
Compatible with OpenAI 0.28.1
"""

import os
import json
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

# OLD OpenAI import style (for version 0.28.1)
import openai

# Set up logging
logger = logging.getLogger(__name__)

# Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
GOOGLE_FACT_CHECK_API_KEY = os.environ.get('GOOGLE_FACT_CHECK_API_KEY')

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
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
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
                article_data = self.extract_from_url(content)
                if not article_data:
                    return {
                        'success': False,
                        'error': 'Could not extract article content'
                    }
            else:
                article_data = {
                    'title': 'Direct Text Analysis',
                    'text': content,
                    'url': None,
                    'domain': None,
                    'publish_date': None
                }
            
            # Perform analysis
            if is_pro and OPENAI_API_KEY:
                analysis = self.get_ai_analysis(article_data)
            else:
                analysis = self.fallback_analysis(article_data)
            
            # Add source credibility
            if article_data.get('domain'):
                analysis['source_credibility'] = self.check_source_credibility(article_data['domain'])
            
            return {
                'success': True,
                'article': article_data,
                'analysis': analysis,
                'is_pro': is_pro
            }
            
        except Exception as e:
            logger.error(f"News analysis error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_from_url(self, url):
        """Extract article content from URL"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract domain
            domain = urlparse(url).netloc.replace('www.', '')
            
            # Extract title
            title = None
            if soup.find('h1'):
                title = soup.find('h1').get_text().strip()
            elif soup.find('title'):
                title = soup.find('title').get_text().strip()
            
            # Extract article text
            article_text = ""
            
            # Try different content selectors
            content_selectors = [
                'article', 
                '[role="main"]',
                '.article-body',
                '.story-body',
                '.entry-content',
                '.post-content',
                'main'
            ]
            
            for selector in content_selectors:
                content = soup.select_one(selector)
                if content:
                    # Get all paragraphs
                    paragraphs = content.find_all('p')
                    if paragraphs:
                        article_text = ' '.join([p.get_text().strip() for p in paragraphs])
                        break
            
            # Fallback to all paragraphs
            if not article_text:
                paragraphs = soup.find_all('p')
                article_text = ' '.join([p.get_text().strip() for p in paragraphs[:20]])  # Limit to first 20
            
            # Extract publish date
            publish_date = None
            date_selectors = [
                'time',
                '[property="article:published_time"]',
                '.publish-date',
                '.posted-on'
            ]
            
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    if date_elem.get('datetime'):
                        publish_date = date_elem['datetime']
                    elif date_elem.get('content'):
                        publish_date = date_elem['content']
                    break
            
            return {
                'url': url,
                'domain': domain,
                'title': title,
                'text': article_text[:5000],  # Limit text length
                'publish_date': publish_date
            }
            
        except Exception as e:
            logger.error(f"URL extraction error: {str(e)}")
            return None
    
    def get_ai_analysis(self, article_data):
        """
        Use OpenAI GPT-4 to analyze article - OLD API style for 0.28.1
        """
        if not OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured")
            return self.fallback_analysis(article_data)
        
        try:
            # Prepare the analysis prompt
            prompt = self._create_analysis_prompt(article_data)
            
            # OLD OpenAI API call style (for version 0.28.1)
            response = openai.ChatCompletion.create(
                model="gpt-4",
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
                max_tokens=1500
            )
            
            # Extract response - OLD style
            analysis_text = response.choices[0].message.content
            
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
        Source: {article_data.get('domain', 'Unknown')}
        
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
                    'trust_score': 50
                }
        except:
            return {
                'summary': response_text,
                'bias_score': 0,
                'credibility_score': 0.5,
                'trust_score': 50
            }
    
    def fallback_analysis(self, article_data):
        """Basic analysis when AI is not available"""
        text = article_data.get('text', '')
        
        # Basic bias detection
        bias_score = 0
        left_keywords = ['progressive', 'liberal', 'democrat', 'left-wing', 'socialist']
        right_keywords = ['conservative', 'republican', 'right-wing', 'traditional', 'libertarian']
        
        text_lower = text.lower()
        left_count = sum(1 for keyword in left_keywords if keyword in text_lower)
        right_count = sum(1 for keyword in right_keywords if keyword in text_lower)
        
        if left_count > right_count:
            bias_score = -0.5
        elif right_count > left_count:
            bias_score = 0.5
        
        # Basic credibility check
        credibility_score = 0.5
        if article_data.get('domain'):
            source_info = SOURCE_CREDIBILITY.get(article_data['domain'], {})
            if source_info.get('credibility') == 'High':
                credibility_score = 0.8
            elif source_info.get('credibility') == 'Low':
                credibility_score = 0.3
        
        # Detect manipulation tactics
        manipulation_tactics = []
        if len(re.findall(r'[A-Z]{2,}', text)) > 10:
            manipulation_tactics.append('Excessive capitalization')
        if len(re.findall(r'!{2,}', text)) > 0:
            manipulation_tactics.append('Multiple exclamation marks')
        if any(word in text_lower for word in ['breaking', 'urgent', 'alert', 'shocking']):
            manipulation_tactics.append('Sensational language')
        
        # Extract key claims (simple extraction)
        sentences = text.split('.')[:5]  # First 5 sentences
        key_claims = [s.strip() for s in sentences if len(s.strip()) > 50][:3]
        
        # Calculate trust score
        trust_score = int((credibility_score * 100 + (1 - abs(bias_score)) * 50) / 2)
        
        return {
            'bias_score': bias_score,
            'credibility_score': credibility_score,
            'factual_accuracy': credibility_score,
            'manipulation_tactics': manipulation_tactics,
            'key_claims': key_claims,
            'fact_checks': [],
            'summary': f"Basic analysis completed. Source credibility: {credibility_score*100:.0f}%. Bias detected: {'Left' if bias_score < 0 else 'Right' if bias_score > 0 else 'Center'}.",
            'trust_score': trust_score
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
    results = analyzer.analyze(content, content_type, is_pro)
    
    # Format for API response
    if results['success']:
        analysis = results['analysis']
        return {
            'success': True,
            'bias_score': analysis.get('bias_score', 0),
            'credibility_score': analysis.get('credibility_score', 0.5),
            'trust_score': analysis.get('trust_score', 50),
            'summary': analysis.get('summary', ''),
            'manipulation_tactics': analysis.get('manipulation_tactics', []),
            'key_claims': analysis.get('key_claims', []),
            'fact_checks': analysis.get('fact_checks', []),
            'source_credibility': results.get('source_credibility', {}),
            'article_info': results.get('article', {})
        }
    else:
        return results
