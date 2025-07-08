# news_analyzer.py - Enhanced News Analysis Backend
# This module handles the actual analysis of news content

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime
import json
from typing import Dict, List, Tuple, Optional

# Source credibility database
SOURCE_CREDIBILITY = {
    'apnews.com': {'name': 'Associated Press', 'credibility': 90, 'bias': 'center'},
    'reuters.com': {'name': 'Reuters', 'credibility': 90, 'bias': 'center'},
    'bbc.com': {'name': 'BBC News', 'credibility': 85, 'bias': 'center-left'},
    'cnn.com': {'name': 'CNN', 'credibility': 70, 'bias': 'left'},
    'foxnews.com': {'name': 'Fox News', 'credibility': 65, 'bias': 'right'},
    'nytimes.com': {'name': 'The New York Times', 'credibility': 80, 'bias': 'left-center'},
    'washingtonpost.com': {'name': 'The Washington Post', 'credibility': 80, 'bias': 'left-center'},
    'wsj.com': {'name': 'The Wall Street Journal', 'credibility': 85, 'bias': 'right-center'},
    'npr.org': {'name': 'NPR', 'credibility': 85, 'bias': 'left-center'},
    'politico.com': {'name': 'Politico', 'credibility': 75, 'bias': 'center'},
}

class NewsAnalyzer:
    """Enhanced news analyzer with real content extraction and analysis"""
    
    def __init__(self):
        self.bias_keywords = {
            'left': ['progressive', 'inequality', 'social justice', 'climate crisis', 'systemic'],
            'right': ['conservative', 'freedom', 'traditional', 'free market', 'patriotic'],
            'emotional': ['shocking', 'outrageous', 'devastating', 'horrifying', 'unbelievable']
        }
    
    def analyze(self, content: str, content_type: str = 'text', is_pro: bool = False) -> Dict:
        """Main analysis function"""
        
        # Extract content based on type
        if content_type == 'url':
            article_data = self.extract_from_url(content)
            if not article_data['success']:
                return self._generate_error_response(article_data['error'])
            
            text = article_data['text']
            metadata = article_data['metadata']
        else:
            text = content
            metadata = self.extract_metadata_from_text(text)
        
        # Perform comprehensive analysis
        analysis_results = {
            'success': True,
            'results': {
                'credibility': self.calculate_credibility(text, metadata),
                'bias': self.analyze_bias(text),
                'sources': self.analyze_sources(metadata, content if content_type == 'url' else None),
                'author': self.extract_author(text, metadata),
                'style': self.analyze_writing_style(text),
                'claims': self.extract_claims(text) if is_pro else [],
                'cross_references': self.find_cross_references(text) if is_pro else []
            },
            'original_content': text[:500] + '...' if len(text) > 500 else text
        }
        
        return analysis_results
    
    def extract_from_url(self, url: str) -> Dict:
        """Extract article content from URL"""
        try:
            # Add headers to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text content
            # Try different selectors for different news sites
            article_text = ""
            
            # Common article selectors
            selectors = [
                'article',
                'main',
                '[role="main"]',
                '.article-body',
                '.story-body',
                '.entry-content',
                'div[itemprop="articleBody"]'
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
            '[rel="author"]',
            '.author-name',
            '.by-author',
            '.ArticleHeader-byline',
            'span[itemprop="author"]',
            '.author'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return ''
    
    def _extract_date_from_html(self, soup: BeautifulSoup) -> str:
        """Extract publication date from HTML"""
        # Try meta tags
        date_meta = soup.find('meta', {'property': 'article:published_time'}) or \
                   soup.find('meta', {'name': 'publication_date'})
        if date_meta:
            return date_meta.get('content', '')
        
        # Try time elements
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
        
        # Extract author - improved patterns
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
    
    def extract_author(self, text: str, metadata: Dict) -> str:
        """Extract and return author name"""
        if metadata.get('author'):
            return metadata['author']
        
        # Try to extract from text
        author_match = re.search(r'By\s+([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)*)', text)
        if author_match:
            return author_match.group(1)
        
        return 'Unknown Author'
    
    def calculate_credibility(self, text: str, metadata: Dict) -> int:
        """Calculate overall credibility score"""
        score = 50  # Base score
        
        # Check source credibility
        domain = metadata.get('domain', '')
        if domain in SOURCE_CREDIBILITY:
            score = SOURCE_CREDIBILITY[domain]['credibility']
        
        # Adjust based on content analysis
        # Has author attribution
        if metadata.get('author') and metadata['author'] != 'Unknown Author':
            score += 5
        
        # Has date
        if metadata.get('date'):
            score += 5
        
        # Has quotes (check for quotation marks)
        quote_count = text.count('"')
        if quote_count >= 4:  # At least 2 quotes
            score += 10
        
        # Has statistics/numbers
        numbers = re.findall(r'\b\d+(?:,\d+)*(?:\.\d+)?%?\b', text)
        if len(numbers) >= 3:
            score += 5
        
        # Check for balanced language (not too emotional)
        emotional_words = sum(1 for word in self.bias_keywords['emotional'] if word.lower() in text.lower())
        if emotional_words < 2:
            score += 5
        
        # Cap at 95
        return min(score, 95)
    
    def analyze_bias(self, text: str) -> Dict:
        """Analyze political bias"""
        text_lower = text.lower()
        
        # Count bias indicators
        left_count = sum(1 for word in self.bias_keywords['left'] if word in text_lower)
        right_count = sum(1 for word in self.bias_keywords['right'] if word in text_lower)
        
        # Calculate bias score (-10 to +10)
        bias_score = (right_count - left_count) * 2
        bias_score = max(-10, min(10, bias_score))
        
        # Determine bias label
        if bias_score <= -7:
            bias_label = 'far-left'
        elif bias_score <= -3:
            bias_label = 'left'
        elif bias_score <= -1:
            bias_label = 'left-center'
        elif bias_score <= 1:
            bias_label = 'center'
        elif bias_score <= 3:
            bias_label = 'right-center'
        elif bias_score <= 7:
            bias_label = 'right'
        else:
            bias_label = 'far-right'
        
        # Calculate objectivity (inverse of emotional content)
        emotional_count = sum(1 for word in self.bias_keywords['emotional'] if word in text_lower)
        objectivity = max(0, 100 - (emotional_count * 10))
        
        return {
            'label': bias_label,
            'score': bias_score,
            'objectivity': objectivity,
            'left_indicators': left_count,
            'right_indicators': right_count,
            'emotional_indicators': emotional_count
        }
    
    def analyze_sources(self, metadata: Dict, url: Optional[str] = None) -> Dict:
        """Analyze source credibility"""
        domain = metadata.get('domain', '')
        
        # Check if it's a known source
        if domain in SOURCE_CREDIBILITY:
            source_info = SOURCE_CREDIBILITY[domain]
            return {
                'name': source_info['name'],
                'credibility': source_info['credibility'],
                'bias': source_info['bias'],
                'domain': domain,
                'matches': 3  # Mock data - in production, actually search for matches
            }
        
        # For unknown sources
        return {
            'name': domain or 'Unknown Source',
            'credibility': 50,
            'bias': 'unknown',
            'domain': domain,
            'matches': 0
        }
    
    def analyze_writing_style(self, text: str) -> Dict:
        """Analyze writing style and patterns"""
        # Count quotes
        quote_count = len(re.findall(r'"[^"]{10,}"', text))
        
        # Count statistics
        stats_count = len(re.findall(r'\b\d+(?:,\d+)*(?:\.\d+)?%?\b', text))
        
        # Calculate reading level (simple approximation)
        sentences = re.split(r'[.!?]+', text)
        words = text.split()
        avg_words_per_sentence = len(words) / max(len(sentences), 1)
        
        if avg_words_per_sentence > 25:
            reading_level = 12
        elif avg_words_per_sentence > 20:
            reading_level = 11
        elif avg_words_per_sentence > 15:
            reading_level = 10
        else:
            reading_level = 9
        
        # Check for balanced coverage
        balanced = quote_count >= 2 and stats_count >= 2
        
        return {
            'quotes': quote_count,
            'statistics': stats_count,
            'readingLevel': reading_level,
            'balanced': balanced
        }
    
    def extract_claims(self, text: str) -> List[Dict]:
        """Extract factual claims from text"""
        claims = []
        
        # Look for sentences with numbers or definitive statements
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences[:10]:  # Limit to first 10 for performance
            sentence = sentence.strip()
            
            # Skip short sentences
            if len(sentence) < 20:
                continue
            
            # Check if it contains a claim indicator
            if any(indicator in sentence.lower() for indicator in ['will', 'would', 'has', 'have', 'announced', 'said', 'according']):
                claims.append({
                    'claim': sentence,
                    'confidence': 80 if re.search(r'\d+', sentence) else 60,
                    'status': 'Identified for verification'
                })
        
        return claims[:5]  # Return top 5 claims
    
    def find_cross_references(self, text: str) -> List[Dict]:
        """Find cross-references (mock data for now)"""
        # In production, this would actually search for similar articles
        # For now, return mock data based on content
        
        references = []
        
        # Check for major topics
        if 'tariff' in text.lower():
            references.extend([
                {'source': 'Reuters', 'title': 'Analysis: Trump tariff threats', 'relevance': 85},
                {'source': 'BBC', 'title': 'US trade policy updates', 'relevance': 75}
            ])
        
        if 'trump' in text.lower():
            references.append({'source': 'CNN', 'title': 'Trump administration policies', 'relevance': 70})
        
        return references
    
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
