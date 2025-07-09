# news_analysis.py - AI-Powered News Analysis with GPT-4
# This module uses OpenAI's GPT-4 for intelligent news analysis

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime
import json
import os
from typing import Dict, List, Tuple, Optional
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Source credibility database (keep this for quick lookups)
SOURCE_CREDIBILITY = {
    'apnews.com': {'name': 'Associated Press', 'credibility': 90, 'bias': 'center'},
    'reuters.com': {'name': 'Reuters', 'credibility': 90, 'bias': 'center'},
    'bbc.com': {'name': 'BBC News', 'credibility': 85, 'bias': 'center-left'},
    'bbc.co.uk': {'name': 'BBC News', 'credibility': 85, 'bias': 'center-left'},
    'cnn.com': {'name': 'CNN', 'credibility': 70, 'bias': 'left'},
    'foxnews.com': {'name': 'Fox News', 'credibility': 65, 'bias': 'right'},
    'nytimes.com': {'name': 'The New York Times', 'credibility': 80, 'bias': 'left-center'},
    'washingtonpost.com': {'name': 'The Washington Post', 'credibility': 80, 'bias': 'left-center'},
    'wsj.com': {'name': 'The Wall Street Journal', 'credibility': 85, 'bias': 'right-center'},
    'npr.org': {'name': 'NPR', 'credibility': 85, 'bias': 'left-center'},
    'politico.com': {'name': 'Politico', 'credibility': 75, 'bias': 'center'},
    'theguardian.com': {'name': 'The Guardian', 'credibility': 75, 'bias': 'left'},
    'dailywire.com': {'name': 'The Daily Wire', 'credibility': 55, 'bias': 'right'},
    'huffpost.com': {'name': 'HuffPost', 'credibility': 60, 'bias': 'left'},
}

class NewsAnalyzer:
    """AI-powered news analyzer using GPT-4 for intelligent analysis"""
    
    def __init__(self):
        self.client = client
        
    def analyze(self, content: str, content_type: str = 'text', is_pro: bool = False) -> Dict:
        """Main analysis function using AI"""
        
        # Extract content based on type
        if content_type == 'url':
            article_data = self.extract_from_url(content)
            if not article_data['success']:
                return self._generate_error_response(article_data['error'])
            
            text = article_data['text']
            metadata = article_data['metadata']
            url = content
        else:
            text = content
            metadata = self.extract_metadata_from_text(text)
            url = None
        
        # Limit text length for API calls (GPT-4 can handle ~8k tokens)
        text_for_analysis = text[:6000] if len(text) > 6000 else text
        
        try:
            # Get AI analysis
            ai_analysis = self.get_ai_analysis(text_for_analysis, metadata, url)
            
            # Combine AI analysis with source database info
            if url and metadata.get('domain') in SOURCE_CREDIBILITY:
                source_info = SOURCE_CREDIBILITY[metadata['domain']]
                ai_analysis['sources']['credibility'] = source_info['credibility']
                ai_analysis['sources']['known_bias'] = source_info['bias']
            
            # Build response
            analysis_results = {
                'success': True,
                'results': ai_analysis,
                'original_content': text[:500] + '...' if len(text) > 500 else text
            }
            
            return analysis_results
            
        except Exception as e:
            print(f"AI Analysis Error: {str(e)}")
            # Fallback to basic analysis if AI fails
            return self.fallback_analysis(text, metadata)
    
    def get_ai_analysis(self, text: str, metadata: Dict, url: Optional[str] = None) -> Dict:
        """Use GPT-4 to analyze the article"""
        
        # Construct the analysis prompt
        prompt = f"""You are an expert news analyst. Analyze this article and provide a detailed assessment.

Article URL: {url or 'Direct text input'}
Source: {metadata.get('domain', 'Unknown')}
Author: {metadata.get('author', 'Not specified')}

Article Text:
{text}

Provide your analysis in the following JSON format (be accurate and specific):
{{
    "credibility": <number 0-100>,
    "bias": {{
        "label": "<one of: far-left, left, left-center, center, right-center, right, far-right>",
        "score": <number -10 to +10, negative=left, positive=right>,
        "objectivity": <number 0-100>,
        "reasoning": "<brief explanation of bias detection>"
    }},
    "sources": {{
        "name": "<source name>",
        "credibility": <number 0-100>,
        "domain": "<domain>",
        "assessment": "<brief source assessment>"
    }},
    "author": "<author name or 'Unknown'>",
    "style": {{
        "quotes": <number of direct quotes found>,
        "statistics": <number of statistics/data points>,
        "readingLevel": <approximate grade level>,
        "balanced": <boolean>,
        "tone": "<professional/casual/sensational/academic>"
    }},
    "fact_check": {{
        "claims": [
            {{
                "claim": "<specific claim from article>",
                "verifiable": <boolean>,
                "confidence": <number 0-100>,
                "assessment": "<brief assessment>"
            }}
        ],
        "overall_accuracy": <number 0-100>
    }},
    "summary": "<2-3 sentence summary of the article>",
    "key_findings": [
        "<finding 1>",
        "<finding 2>",
        "<finding 3>"
    ],
    "red_flags": [
        "<any concerns or issues found>"
    ]
}}

Be objective and thorough in your analysis. Base credibility on:
- Source reputation and track record
- Author credentials
- Use of evidence and citations
- Balanced reporting
- Factual accuracy
- Transparent corrections policy"""

        try:
            # Make API call to GPT-4
            response = self.client.chat.completions.create(
                model="gpt-4",  # or "gpt-3.5-turbo" for faster/cheaper
                messages=[
                    {"role": "system", "content": "You are an expert news analyst providing objective article assessments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=1500
            )
            
            # Parse the response
            analysis_text = response.choices[0].message.content
            
            # Extract JSON from response (GPT sometimes adds extra text)
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group())
            else:
                # If no JSON found, try to parse the whole response
                analysis_data = json.loads(analysis_text)
            
            # Convert to expected format
            return self.format_ai_response(analysis_data, metadata)
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response was: {analysis_text if 'analysis_text' in locals() else 'No response'}")
            raise
        except Exception as e:
            print(f"GPT-4 API error: {e}")
            raise
    
    def format_ai_response(self, ai_data: Dict, metadata: Dict) -> Dict:
        """Format AI response to match expected structure"""
        
        # Ensure all required fields exist with defaults
        return {
            'credibility': ai_data.get('credibility', 50),
            'bias': {
                'label': ai_data.get('bias', {}).get('label', 'unknown'),
                'score': ai_data.get('bias', {}).get('score', 0),
                'objectivity': ai_data.get('bias', {}).get('objectivity', 50),
                'left_indicators': abs(ai_data.get('bias', {}).get('score', 0)) if ai_data.get('bias', {}).get('score', 0) < 0 else 0,
                'right_indicators': ai_data.get('bias', {}).get('score', 0) if ai_data.get('bias', {}).get('score', 0) > 0 else 0,
                'emotional_indicators': max(0, 100 - ai_data.get('bias', {}).get('objectivity', 100)) // 10,
                'reasoning': ai_data.get('bias', {}).get('reasoning', '')
            },
            'sources': {
                'name': ai_data.get('sources', {}).get('name', metadata.get('domain', 'Unknown')),
                'credibility': ai_data.get('sources', {}).get('credibility', 50),
                'bias': ai_data.get('bias', {}).get('label', 'unknown'),
                'domain': ai_data.get('sources', {}).get('domain', metadata.get('domain', '')),
                'assessment': ai_data.get('sources', {}).get('assessment', '')
            },
            'author': ai_data.get('author', metadata.get('author', 'Unknown')),
            'style': {
                'quotes': ai_data.get('style', {}).get('quotes', 0),
                'statistics': ai_data.get('style', {}).get('statistics', 0),
                'readingLevel': ai_data.get('style', {}).get('readingLevel', 10),
                'balanced': ai_data.get('style', {}).get('balanced', False),
                'tone': ai_data.get('style', {}).get('tone', 'unknown')
            },
            'claims': [
                {
                    'claim': claim.get('claim', ''),
                    'confidence': claim.get('confidence', 50),
                    'status': f"{'Verifiable' if claim.get('verifiable', False) else 'Unverifiable'} - {claim.get('assessment', '')}"
                }
                for claim in ai_data.get('fact_check', {}).get('claims', [])[:5]
            ],
            'cross_references': [],  # Would need separate API call
            'summary': ai_data.get('summary', ''),
            'key_findings': ai_data.get('key_findings', []),
            'red_flags': ai_data.get('red_flags', []),
            'overall_accuracy': ai_data.get('fact_check', {}).get('overall_accuracy', 50)
        }
    
    def fallback_analysis(self, text: str, metadata: Dict) -> Dict:
        """Fallback to basic analysis if AI fails"""
        print("Using fallback analysis due to AI error")
        
        # Basic keyword analysis as fallback
        text_lower = text.lower()
        
        # Count basic indicators
        quotes = len(re.findall(r'"[^"]{10,}"', text))
        stats = len(re.findall(r'\b\d+(?:,\d+)*(?:\.\d+)?%?\b', text))
        
        # Very basic bias detection
        left_words = ['progressive', 'inequality', 'social justice', 'climate crisis']
        right_words = ['conservative', 'freedom', 'traditional', 'free market']
        emotional_words = ['shocking', 'outrageous', 'devastating', 'unbelievable']
        
        left_count = sum(1 for word in left_words if word in text_lower)
        right_count = sum(1 for word in right_words if word in text_lower)
        emotional_count = sum(1 for word in emotional_words if word in text_lower)
        
        bias_score = (right_count - left_count) * 2
        bias_label = 'center'
        if bias_score <= -3:
            bias_label = 'left'
        elif bias_score >= 3:
            bias_label = 'right'
        
        return {
            'credibility': 50,  # Default middle score
            'bias': {
                'label': bias_label,
                'score': bias_score,
                'objectivity': max(0, 100 - (emotional_count * 10)),
                'left_indicators': left_count,
                'right_indicators': right_count,
                'emotional_indicators': emotional_count
            },
            'sources': {
                'name': metadata.get('domain', 'Unknown'),
                'credibility': 50,
                'bias': 'unknown',
                'domain': metadata.get('domain', '')
            },
            'author': metadata.get('author', 'Unknown'),
            'style': {
                'quotes': quotes,
                'statistics': stats,
                'readingLevel': 10,
                'balanced': quotes >= 2
            },
            'claims': [],
            'cross_references': []
        }
    
    def extract_from_url(self, url: str) -> Dict:
        """Extract article content from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text content
            article_text = ""
            
            # Common article selectors
            selectors = [
                'article', 'main', '[role="main"]', '.article-body',
                '.story-body', '.entry-content', 'div[itemprop="articleBody"]'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    article_text = ' '.join([elem.get_text(strip=True) for elem in elements])
                    if len(article_text) > 100:
                        break
            
            # If no article found, try paragraphs
            if len(article_text) < 100:
                paragraphs = soup.find_all('p')
                article_text = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
            
            # Extract metadata
            metadata = {
                'title': soup.find('title').get_text() if soup.find('title') else '',
                'author': self._extract_author_from_html(soup),
                'date': self._extract_date_from_html(soup),
                'domain': urlparse(url).netloc.replace('www.', '')
            }
            
            return {
                'success': True,
                'text': article_text,
                'metadata': metadata
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Could not extract content from URL: {str(e)}",
                'text': '',
                'metadata': {}
            }
    
    def _extract_author_from_html(self, soup: BeautifulSoup) -> str:
        """Extract author from HTML"""
        # Try meta tags first
        author_meta = soup.find('meta', {'name': 'author'}) or soup.find('meta', {'property': 'author'})
        if author_meta:
            return author_meta.get('content', '')
        
        # Try common author selectors
        selectors = [
            '[rel="author"]', '.author-name', '.by-author',
            '.ArticleHeader-byline', 'span[itemprop="author"]', '.author'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return ''
    
    def _extract_date_from_html(self, soup: BeautifulSoup) -> str:
        """Extract publication date from HTML"""
        date_meta = soup.find('meta', {'property': 'article:published_time'}) or \
                   soup.find('meta', {'name': 'publication_date'})
        if date_meta:
            return date_meta.get('content', '')
        
        time_elem = soup.find('time')
        if time_elem:
            return time_elem.get('datetime', time_elem.get_text(strip=True))
        
        return ''
    
    def extract_metadata_from_text(self, text: str) -> Dict:
        """Extract metadata from pasted text"""
        metadata = {
            'title': '',
            'author': '',
            'date': '',
            'domain': 'Direct Input'
        }
        
        # Extract author
        author_patterns = [
            r'^By\s+([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)*)',
            r'^([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)*)\n',
            r'By:\s+([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)*)',
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                metadata['author'] = match.group(1).strip()
                break
        
        # Extract date
        date_pattern = r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'
        date_match = re.search(date_pattern, text)
        if date_match:
            metadata['date'] = date_match.group(0)
        
        return metadata
    
    def _generate_error_response(self, error: str) -> Dict:
        """Generate error response"""
        return {
            'success': False,
            'error': error,
            'results': {
                'credibility': 50,
                'bias': {'label': 'unknown', 'score': 0, 'objectivity': 50},
                'sources': {'name': 'Unknown', 'credibility': 50},
                'author': 'Unknown',
                'style': {'quotes': 0, 'statistics': 0, 'readingLevel': 10, 'balanced': False}
            }
        }


# Flask route handler
def analyze_news_route(request_data: Dict) -> Dict:
    """Flask route handler for news analysis"""
    
    analyzer = NewsAnalyzer()
    
    # Extract parameters
    content = request_data.get('content', '')
    content_type = request_data.get('type', 'text')
    is_pro = request_data.get('is_pro', False)
    
    if not content:
        return {'error': 'No content provided'}, 400
    
    # Perform analysis
    try:
        results = analyzer.analyze(content, content_type, is_pro)
        return results
    except Exception as e:
        return {'error': f'Analysis failed: {str(e)}'}, 500
