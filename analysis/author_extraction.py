"""
Enhanced Author Extraction Module for Facts & Fakes AI
Implements publisher-specific rules and intelligent fallbacks
"""

import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import json
from typing import Optional, List, Dict, Union

class AuthorExtractor:
    def __init__(self):
        self.publisher_rules = self._initialize_publisher_rules()
        
    def _initialize_publisher_rules(self) -> Dict:
        """Initialize extraction rules for major news publishers"""
        return {
            'politico.com': {
                'selectors': [
                    {'name': 'meta', 'attrs': {'name': 'author'}},
                    {'name': 'meta', 'attrs': {'property': 'article:author'}},
                    {'name': 'span', 'attrs': {'class': 'story-meta__authors'}},
                    {'name': 'div', 'attrs': {'class': 'byline'}},
                    {'name': 'a', 'attrs': {'class': 'username'}},
                    {'name': 'p', 'attrs': {'class': 'story-meta__credit'}},
                ],
                'patterns': [
                    r'By\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})(?:\s*\||\s*$)',
                    r'^\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})\s*\|',
                ],
                'json_ld_paths': ['author.name', 'author[0].name'],
                'exclude_patterns': [
                    r'bill\s+by', r'photo\s+by', r'illustration\s+by', 
                    r'compiled\s+by', r'sponsored\s+by', r'introduced\s+by'
                ]
            },
            'cnn.com': {
                'selectors': [
                    {'name': 'meta', 'attrs': {'name': 'author'}},
                    {'name': 'span', 'attrs': {'class': 'byline__name'}},
                    {'name': 'div', 'attrs': {'class': 'metadata__byline__author'}},
                ],
                'patterns': [
                    r'By\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})(?:,\s+CNN)?',
                    r'^\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3}),\s+CNN',
                ],
                'json_ld_paths': ['author.name', 'author[0].name'],
            },
            'nytimes.com': {
                'selectors': [
                    {'name': 'meta', 'attrs': {'name': 'byl'}},
                    {'name': 'span', 'attrs': {'itemprop': 'name'}},
                    {'name': 'span', 'attrs': {'class': 'last-byline'}},
                ],
                'patterns': [
                    r'By\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})',
                ],
                'json_ld_paths': ['author.name', 'author[0].name'],
                'content_property': 'content',  # NYT often uses content attribute
            },
            'foxnews.com': {
                'selectors': [
                    {'name': 'meta', 'attrs': {'name': 'dc.creator'}},
                    {'name': 'span', 'attrs': {'class': 'author-byline__name'}},
                    {'name': 'a', 'attrs': {'class': 'author'}},
                ],
                'patterns': [
                    r'By\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})',
                ],
                'json_ld_paths': ['author.name'],
            },
            'washingtonpost.com': {
                'selectors': [
                    {'name': 'meta', 'attrs': {'name': 'author'}},
                    {'name': 'span', 'attrs': {'class': 'author-name'}},
                    {'name': 'a', 'attrs': {'class': 'author-name-link'}},
                ],
                'patterns': [
                    r'By\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})',
                ],
                'json_ld_paths': ['author.name', 'author[0].name'],
            },
            'msnbc.com': {
                'selectors': [
                    {'name': 'meta', 'attrs': {'name': 'author'}},
                    {'name': 'span', 'attrs': {'class': 'article-author__name'}},
                    {'name': 'div', 'attrs': {'class': 'byline'}},
                ],
                'patterns': [
                    r'By\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})',
                ],
                'json_ld_paths': ['author.name'],
            },
            'reuters.com': {
                'selectors': [
                    {'name': 'meta', 'attrs': {'name': 'Author'}},
                    {'name': 'meta', 'attrs': {'property': 'og:article:author'}},
                    {'name': 'a', 'attrs': {'class': 'author-name'}},
                ],
                'patterns': [
                    r'By\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})',
                ],
                'json_ld_paths': ['author.name', 'author[0].name'],
            },
            'apnews.com': {
                'selectors': [
                    {'name': 'meta', 'attrs': {'name': 'author'}},
                    {'name': 'span', 'attrs': {'class': 'Component-bylines'}},
                ],
                'patterns': [
                    r'By\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})',
                ],
                'json_ld_paths': ['author.name'],
            },
            'bbc.com': {
                'selectors': [
                    {'name': 'meta', 'attrs': {'name': 'article:author'}},
                    {'name': 'span', 'attrs': {'class': 'byline__name'}},
                    {'name': 'p', 'attrs': {'class': 'story-body__byline'}},
                ],
                'patterns': [
                    r'By\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})',
                ],
                'json_ld_paths': ['author.name'],
            },
            'wsj.com': {
                'selectors': [
                    {'name': 'meta', 'attrs': {'name': 'author'}},
                    {'name': 'span', 'attrs': {'class': 'byline'}},
                    {'name': 'meta', 'attrs': {'name': 'article.author'}},
                ],
                'patterns': [
                    r'By\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})',
                ],
                'json_ld_paths': ['author.name'],
            }
        }
    
    def extract_author(self, html: str, url: str) -> Optional[str]:
        """
        Main extraction method that tries multiple strategies
        """
        soup = BeautifulSoup(html, 'html.parser')
        domain = self._get_domain(url)
        
        # Try publisher-specific rules first
        if domain in self.publisher_rules:
            author = self._apply_publisher_rules(soup, html, self.publisher_rules[domain])
            if author:
                return author
        
        # Fall back to generic extraction
        return self._generic_extraction(soup, html)
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    
    def _apply_publisher_rules(self, soup: BeautifulSoup, html: str, rules: Dict) -> Optional[str]:
        """Apply publisher-specific extraction rules"""
        
        # 1. Try CSS selectors
        if 'selectors' in rules:
            for selector in rules['selectors']:
                elements = soup.find_all(**selector)
                for element in elements:
                    author = self._extract_from_element(element, rules.get('content_property'))
                    if author and self._validate_author(author, rules):
                        return author
        
        # 2. Try JSON-LD structured data
        if 'json_ld_paths' in rules:
            author = self._extract_from_json_ld(soup, rules['json_ld_paths'])
            if author and self._validate_author(author, rules):
                return author
        
        # 3. Try regex patterns on text
        if 'patterns' in rules:
            # Look in first 1000 characters for byline
            text_start = soup.get_text()[:1000]
            for pattern in rules['patterns']:
                matches = re.findall(pattern, text_start, re.MULTILINE)
                for match in matches:
                    if self._validate_author(match, rules):
                        return match
        
        return None
    
    def _extract_from_element(self, element, content_property: str = None) -> Optional[str]:
        """Extract author from HTML element"""
        if element.name == 'meta':
            return element.get('content', '')
        elif content_property:
            return element.get(content_property, '')
        else:
            return element.get_text(strip=True)
    
    def _extract_from_json_ld(self, soup: BeautifulSoup, paths: List[str]) -> Optional[str]:
        """Extract author from JSON-LD structured data"""
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                for path in paths:
                    author = self._get_nested_value(data, path)
                    if author:
                        return author
            except json.JSONDecodeError:
                continue
        return None
    
    def _get_nested_value(self, data: Dict, path: str) -> Optional[str]:
        """Get value from nested dictionary using dot notation"""
        keys = path.split('.')
        value = data
        for key in keys:
            if '[' in key and ']' in key:
                # Handle array notation like author[0]
                base_key = key[:key.index('[')]
                index = int(key[key.index('[')+1:key.index(']')])
                if base_key in value and isinstance(value[base_key], list):
                    if len(value[base_key]) > index:
                        value = value[base_key][index]
                    else:
                        return None
                else:
                    return None
            else:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
        return str(value) if value else None
    
    def _validate_author(self, author: str, rules: Dict) -> bool:
        """Validate that extracted string is likely an author name"""
        if not author or len(author) < 3:
            return False
        
        # Check exclusion patterns
        if 'exclude_patterns' in rules:
            text_lower = author.lower()
            for pattern in rules['exclude_patterns']:
                if re.search(pattern, text_lower):
                    return False
        
        # Remove common titles that indicate false positives
        invalid_indicators = [
            'sen.', 'rep.', 'dr.', 'bill', 'act', 'section',
            'article', 'photo', 'illustration', 'compiled'
        ]
        author_lower = author.lower()
        if any(indicator in author_lower for indicator in invalid_indicators):
            return False
        
        # Must have at least first and last name
        parts = author.strip().split()
        if len(parts) < 2 or len(parts) > 4:
            return False
        
        # Each part should start with capital letter
        for part in parts:
            if not part[0].isupper():
                return False
        
        return True
    
    def _generic_extraction(self, soup: BeautifulSoup, html: str) -> Optional[str]:
        """Generic extraction methods when publisher-specific rules fail"""
        
        # Common meta tags
        meta_names = ['author', 'dc.creator', 'byl', 'sailthru.author']
        for name in meta_names:
            meta = soup.find('meta', attrs={'name': name})
            if meta and meta.get('content'):
                author = meta['content']
                if self._validate_author(author, {}):
                    return author
        
        # Common class names
        class_names = ['author', 'byline', 'by-line', 'writer', 'journalist']
        for class_name in class_names:
            elements = soup.find_all(class_=re.compile(class_name, re.I))
            for element in elements:
                text = element.get_text(strip=True)
                # Try to extract name from byline text
                match = re.search(r'By\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})', text)
                if match and self._validate_author(match.group(1), {}):
                    return match.group(1)
        
        return None


# Integration function for use in news_analysis.py
def extract_author_enhanced(html: str, url: str) -> Optional[str]:
    """
    Enhanced author extraction with publisher-specific rules
    
    Args:
        html: The HTML content of the article
        url: The URL of the article
        
    Returns:
        Author name if found, None otherwise
    """
    extractor = AuthorExtractor()
    return extractor.extract_author(html, url)
