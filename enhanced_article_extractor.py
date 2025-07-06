# enhanced_article_extractor.py
"""
Enhanced Article Extraction System
Comprehensive solution for extracting article data from news websites
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from datetime import datetime
import json
from typing import Dict, List, Optional, Tuple
import traceback

class ArticleExtractor:
    """
    Comprehensive article extraction with fallback strategies
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
    def extract_from_url(self, url: str) -> Optional[Dict]:
        """
        Main extraction method with comprehensive fallbacks
        """
        try:
            # Fetch the page
            response = requests.get(url, headers=self.headers, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Parse domain
            parsed_url = urlparse(response.url)  # Use final URL after redirects
            domain = parsed_url.netloc.replace('www.', '')
            
            # Extract all components
            title = self._extract_title(soup, domain)
            authors = self._extract_authors(soup, response.text)
            date = self._extract_date(soup, response.text)
            content = self._extract_content(soup)
            description = self._extract_description(soup)
            
            # Extract structured data if available
            structured_data = self._extract_structured_data(soup)
            
            # Determine article topic
            topic = self._determine_topic(title, content, description)
            
            # Validate extraction
            extraction_quality = self._assess_extraction_quality(content, title, authors, date)
            
            return {
                'content': content,
                'title': title,
                'authors': authors,
                'date': date,
                'domain': domain,
                'url': response.url,
                'description': description,
                'topic': topic,
                'structured_data': structured_data,
                'extraction_quality': extraction_quality,
                'extraction_success': extraction_quality['overall_score'] > 0.5
            }
            
        except Exception as e:
            print(f"Extraction error for {url}: {str(e)}")
            traceback.print_exc()
            return None
    
    def _extract_title(self, soup: BeautifulSoup, domain: str) -> str:
        """
        Extract article title with multiple strategies
        """
        # Strategy 1: Meta tags (most reliable)
        meta_selectors = [
            ('meta[property="og:title"]', 'content'),
            ('meta[name="twitter:title"]', 'content'),
            ('meta[property="article:title"]', 'content'),
            ('meta[name="title"]', 'content'),
            ('meta[itemprop="headline"]', 'content')
        ]
        
        for selector, attr in meta_selectors:
            elem = soup.select_one(selector)
            if elem and elem.get(attr):
                title = elem[attr].strip()
                if title and len(title) > 10:
                    return self._clean_title(title, domain)
        
        # Strategy 2: Structured data
        json_ld = soup.find('script', type='application/ld+json')
        if json_ld:
            try:
                data = json.loads(json_ld.string)
                if isinstance(data, dict):
                    if 'headline' in data:
                        return self._clean_title(data['headline'], domain)
                    if '@graph' in data:
                        for item in data['@graph']:
                            if isinstance(item, dict) and 'headline' in item:
                                return self._clean_title(item['headline'], domain)
            except:
                pass
        
        # Strategy 3: H1 tags with priority
        h1_candidates = []
        for h1 in soup.find_all('h1'):
            text = h1.get_text(strip=True)
            if text and len(text) > 10:
                # Score based on location and attributes
                score = 0
                
                # Check parent containers
                parent_classes = ' '.join(h1.parent.get('class', []))
                if any(marker in parent_classes.lower() for marker in ['article', 'content', 'main', 'story', 'post']):
                    score += 10
                
                # Check h1 classes
                h1_classes = ' '.join(h1.get('class', []))
                if any(marker in h1_classes.lower() for marker in ['title', 'headline', 'article']):
                    score += 5
                
                # Length bonus
                if 20 < len(text) < 200:
                    score += 3
                
                h1_candidates.append((score, text))
        
        if h1_candidates:
            h1_candidates.sort(reverse=True)
            return self._clean_title(h1_candidates[0][1], domain)
        
        # Strategy 4: Title tag (last resort)
        title_tag = soup.find('title')
        if title_tag:
            return self._clean_title(title_tag.get_text(strip=True), domain)
        
        return "Title not found"
    
    def _clean_title(self, title: str, domain: str) -> str:
        """
        Clean title by removing site names and common suffixes
        """
        # Common separators and site name patterns
        separators = [' - ', ' | ', ' — ', ' :: ', ' » ', ' • ']
        
        for sep in separators:
            if sep in title:
                parts = title.split(sep)
                # Usually the site name is at the end
                if len(parts) >= 2:
                    # Check if last part looks like a site name
                    last_part = parts[-1].lower()
                    if any(indicator in last_part for indicator in ['news', 'times', 'post', 'journal', domain.split('.')[0]]):
                        title = sep.join(parts[:-1])
                    # Sometimes it's at the beginning
                    elif len(parts[0]) < 20 and len(parts[1]) > len(parts[0]):
                        title = sep.join(parts[1:])
        
        return title.strip()
    
    def _extract_authors(self, soup: BeautifulSoup, html_text: str) -> List[str]:
        """
        Extract authors with comprehensive strategies
        """
        authors = set()
        
        # Strategy 1: Meta tags
        meta_selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            'meta[name="byl"]',
            'meta[property="author"]',
            'meta[name="parsely-author"]',
            'meta[name="sailthru.author"]'
        ]
        
        for selector in meta_selectors:
            elements = soup.select(selector)
            for elem in elements:
                content = elem.get('content', '').strip()
                if content:
                    authors.update(self._parse_author_string(content))
        
        # Strategy 2: Structured data
        json_ld = soup.find_all('script', type='application/ld+json')
        for script in json_ld:
            try:
                data = json.loads(script.string)
                authors.update(self._extract_authors_from_json_ld(data))
            except:
                continue
        
        # Strategy 3: Semantic HTML
        semantic_selectors = [
            '[rel="author"]',
            '[itemprop="author"]',
            '[itemtype*="schema.org/Person"]',
            'address[rel="author"]',
            'span[itemprop="name"]'
        ]
        
        for selector in semantic_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text(strip=True)
                if self._is_valid_author(text):
                    authors.add(self._clean_author_name(text))
        
        # Strategy 4: Class-based selectors
        class_patterns = [
            r'class="[^"]*(?:author|byline|writer|reporter|journalist|correspondent)[^"]*"',
            r'class="[^"]*(?:by-line|article-author|post-author|entry-author)[^"]*"',
            r'class="[^"]*(?:author-name|author-link|author-bio)[^"]*"'
        ]
        
        for pattern in class_patterns:
            matches = re.finditer(pattern, html_text, re.IGNORECASE)
            for match in matches:
                # Extract the element
                start = html_text.rfind('<', 0, match.start())
                end = html_text.find('>', match.end())
                if start != -1 and end != -1:
                    element_html = html_text[start:end+1]
                    # Find the closing tag
                    tag_match = re.match(r'<(\w+)', element_html)
                    if tag_match:
                        tag_name = tag_match.group(1)
                        close_tag = f'</{tag_name}>'
                        close_pos = html_text.find(close_tag, end)
                        if close_pos != -1:
                            full_element = html_text[start:close_pos+len(close_tag)]
                            elem_soup = BeautifulSoup(full_element, 'html.parser')
                            text = elem_soup.get_text(strip=True)
                            if self._is_valid_author(text):
                                authors.add(self._clean_author_name(text))
        
        # Strategy 5: Text patterns
        text_patterns = [
            r'By\s+([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)+)',
            r'Written by\s+([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)+)',
            r'Author:\s*([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)+)',
            r'Reporter:\s*([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)+)',
            r'^\s*([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)+)\s+is a (?:reporter|journalist|correspondent)',
        ]
        
        # Search in first 1000 characters
        search_text = soup.get_text()[:1000]
        for pattern in text_patterns:
            matches = re.finditer(pattern, search_text, re.MULTILINE)
            for match in matches:
                author = match.group(1).strip()
                if self._is_valid_author(author):
                    authors.add(author)
        
        # Convert to list and limit
        return list(authors)[:5]  # Max 5 authors
    
    def _extract_authors_from_json_ld(self, data: dict) -> set:
        """
        Extract authors from JSON-LD structured data
        """
        authors = set()
        
        if isinstance(data, dict):
            # Direct author field
            if 'author' in data:
                author_data = data['author']
                if isinstance(author_data, str):
                    authors.update(self._parse_author_string(author_data))
                elif isinstance(author_data, dict) and 'name' in author_data:
                    authors.add(author_data['name'])
                elif isinstance(author_data, list):
                    for author in author_data:
                        if isinstance(author, str):
                            authors.add(author)
                        elif isinstance(author, dict) and 'name' in author:
                            authors.add(author['name'])
            
            # Check @graph
            if '@graph' in data and isinstance(data['@graph'], list):
                for item in data['@graph']:
                    if isinstance(item, dict):
                        authors.update(self._extract_authors_from_json_ld(item))
        
        return authors
    
    def _parse_author_string(self, author_string: str) -> set:
        """
        Parse author string that might contain multiple authors
        """
        authors = set()
        
        # Clean the string
        author_string = self._clean_author_name(author_string)
        
        # Split by common separators
        separators = [' and ', ' & ', ', ', ' with ']
        
        current_parts = [author_string]
        for separator in separators:
            new_parts = []
            for part in current_parts:
                new_parts.extend(part.split(separator))
            current_parts = new_parts
        
        for part in current_parts:
            part = part.strip()
            if self._is_valid_author(part):
                authors.add(part)
        
        return authors
    
    def _clean_author_name(self, name: str) -> str:
        """
        Clean author name
        """
        # Remove common prefixes
        prefixes = ['By', 'by', 'Written by', 'Author:', 'Reporter:', 'Journalist:']
        for prefix in prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):].strip()
        
        # Remove email patterns
        name = re.sub(r'\S+@\S+', '', name).strip()
        
        # Remove social media handles
        name = re.sub(r'@\w+', '', name).strip()
        
        # Remove parenthetical additions
        name = re.sub(r'\([^)]+\)', '', name).strip()
        
        return name
    
    def _is_valid_author(self, text: str) -> bool:
        """
        Check if text is a valid author name
        """
        if not text or len(text) < 3 or len(text) > 100:
            return False
        
        # Exclude common non-author strings
        exclude_terms = [
            'staff', 'admin', 'editor', 'team', 'newsroom', 'correspondent',
            'associated press', 'reuters', 'afp', 'contributor', 'special',
            'news service', 'wire', 'desk', 'bureau', 'editorial'
        ]
        
        text_lower = text.lower()
        if any(term in text_lower for term in exclude_terms):
            return False
        
        # Should have at least one space (first and last name)
        if ' ' not in text and '.' not in text:
            return False
        
        # Should start with capital letter
        if not text[0].isupper():
            return False
        
        # Should not be all caps (unless it's initials)
        if text.isupper() and not all(len(part) <= 3 for part in text.split()):
            return False
        
        return True
    
    def _extract_date(self, soup: BeautifulSoup, html_text: str) -> Optional[str]:
        """
        Extract publication date with multiple strategies
        """
        # Strategy 1: Meta tags
        meta_selectors = [
            ('meta[property="article:published_time"]', 'content'),
            ('meta[name="publish_date"]', 'content'),
            ('meta[name="publication_date"]', 'content'),
            ('meta[property="article:published"]', 'content'),
            ('meta[name="date"]', 'content'),
            ('meta[itemprop="datePublished"]', 'content'),
            ('meta[name="parsely-pub-date"]', 'content'),
            ('meta[name="sailthru.date"]', 'content'),
            ('meta[property="og:article:published_time"]', 'content'),
            ('meta[name="DC.date.issued"]', 'content')
        ]
        
        for selector, attr in meta_selectors:
            elem = soup.select_one(selector)
            if elem and elem.get(attr):
                date = elem[attr].strip()
                if date:
                    return self._normalize_date(date)
        
        # Strategy 2: Structured data
        json_ld = soup.find_all('script', type='application/ld+json')
        for script in json_ld:
            try:
                data = json.loads(script.string)
                date = self._extract_date_from_json_ld(data)
                if date:
                    return self._normalize_date(date)
            except:
                continue
        
        # Strategy 3: Time elements
        time_selectors = [
            'time[datetime]',
            'time[itemprop="datePublished"]',
            'time[pubdate]',
            '[datetime]'
        ]
        
        for selector in time_selectors:
            elem = soup.select_one(selector)
            if elem:
                datetime_attr = elem.get('datetime')
                if datetime_attr:
                    return self._normalize_date(datetime_attr)
        
        # Strategy 4: Class-based selectors
        date_selectors = [
            '[class*="publish-date"]',
            '[class*="published-date"]',
            '[class*="article-date"]',
            '[class*="post-date"]',
            '[class*="entry-date"]',
            '[class*="timestamp"]',
            '[class*="time-stamp"]',
            '[class*="date-time"]',
            '[class*="article-time"]',
            '[class*="published-time"]',
            '.date',
            '.time',
            '.published',
            '.timestamp'
        ]
        
        for selector in date_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text(strip=True)
                if self._looks_like_date(text):
                    return self._normalize_date(text)
        
        # Strategy 5: Text patterns in article
        date_patterns = [
            r'Published:?\s*([A-Za-z]+ \d{1,2},? \d{4})',
            r'Updated:?\s*([A-Za-z]+ \d{1,2},? \d{4})',
            r'Posted:?\s*([A-Za-z]+ \d{1,2},? \d{4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
            r'([A-Za-z]+ \d{1,2},? \d{4} at \d{1,2}:\d{2})',
            r'(\d{1,2} [A-Za-z]+ \d{4})'
        ]
        
        search_text = soup.get_text()[:2000]  # First 2000 chars
        for pattern in date_patterns:
            match = re.search(pattern, search_text)
            if match:
                date_text = match.group(1)
                if self._looks_like_date(date_text):
                    return self._normalize_date(date_text)
        
        return None
    
    def _extract_date_from_json_ld(self, data: dict) -> Optional[str]:
        """
        Extract date from JSON-LD structured data
        """
        if isinstance(data, dict):
            # Direct date fields
            date_fields = ['datePublished', 'dateCreated', 'publishedDate', 'date']
            for field in date_fields:
                if field in data:
                    return data[field]
            
            # Check @graph
            if '@graph' in data and isinstance(data['@graph'], list):
                for item in data['@graph']:
                    if isinstance(item, dict):
                        date = self._extract_date_from_json_ld(item)
                        if date:
                            return date
        
        return None
    
    def _looks_like_date(self, text: str) -> bool:
        """
        Check if text looks like a date
        """
        if not text or len(text) > 50:
            return False
        
        # Must contain a year
        if not re.search(r'\b(19|20)\d{2}\b', text):
            return False
        
        # Should contain month or number patterns
        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        has_month = any(month in text.lower() for month in months)
        has_numbers = bool(re.search(r'\d{1,2}[/-]\d{1,2}', text))
        
        return has_month or has_numbers
    
    def _normalize_date(self, date_str: str) -> str:
        """
        Normalize date to consistent format
        """
        # For now, return as-is
        # In production, you'd parse and format to ISO 8601
        return date_str.strip()
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """
        Extract main article content
        """
        # Remove script and style elements
        for element in soup(['script', 'style', 'noscript']):
            element.decompose()
        
        # Strategy 1: Article containers
        content_selectors = [
            'article[itemtype*="Article"]',
            'article[itemtype*="NewsArticle"]',
            '[itemprop="articleBody"]',
            '[class*="article-body"]',
            '[class*="article-content"]',
            '[class*="story-body"]',
            '[class*="entry-content"]',
            '[class*="post-content"]',
            '[class*="content-body"]',
            '[class*="article-text"]',
            'article',
            'main[role="main"]',
            'main',
            '.content',
            '#content',
            '.story'
        ]
        
        article_text = []
        
        for selector in content_selectors:
            container = soup.select_one(selector)
            if container:
                # Extract paragraphs
                paragraphs = self._extract_paragraphs(container)
                if len(paragraphs) >= 3 and sum(len(p) for p in paragraphs) > 200:
                    article_text = paragraphs
                    break
        
        # Strategy 2: If no container found, get all paragraphs
        if not article_text:
            all_paragraphs = self._extract_paragraphs(soup)
            # Filter to likely article paragraphs
            article_text = [p for p in all_paragraphs if len(p) > 50]
        
        # Join paragraphs
        content = '\n\n'.join(article_text)
        
        return content
    
    def _extract_paragraphs(self, container) -> List[str]:
        """
        Extract clean paragraphs from container
        """
        paragraphs = []
        
        # Get text elements
        for elem in container.find_all(['p', 'h2', 'h3', 'h4', 'blockquote', 'li']):
            # Skip if inside unwanted containers
            if elem.find_parent(['nav', 'header', 'footer', 'aside']):
                continue
            
            text = elem.get_text(strip=True)
            
            # Filter out non-content
            if self._is_content_paragraph(text):
                # Clean the text
                text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
                paragraphs.append(text)
        
        return paragraphs
    
    def _is_content_paragraph(self, text: str) -> bool:
        """
        Check if text is likely article content
        """
        if not text or len(text) < 20:
            return False
        
        # Filter out common non-content patterns
        exclude_patterns = [
            'cookie', 'subscribe', 'newsletter', 'sign up', 'advertisement',
            'related articles', 'read more', 'share this', 'follow us',
            'comments', 'leave a reply', 'copyright', 'terms of service',
            'privacy policy', 'sponsored content', 'paid partnership'
        ]
        
        text_lower = text.lower()
        if any(pattern in text_lower for pattern in exclude_patterns):
            return False
        
        # Should look like a sentence
        if not any(text.endswith(p) for p in ['.', '!', '?', '"', '"', ''']) and len(text) < 100:
            return False
        
        return True
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """
        Extract article description/summary
        """
        # Try meta descriptions
        desc_selectors = [
            ('meta[property="og:description"]', 'content'),
            ('meta[name="description"]', 'content'),
            ('meta[name="twitter:description"]', 'content'),
            ('meta[itemprop="description"]', 'content'),
            ('meta[name="sailthru.description"]', 'content')
        ]
        
        for selector, attr in desc_selectors:
            elem = soup.select_one(selector)
            if elem and elem.get(attr):
                desc = elem[attr].strip()
                if desc and len(desc) > 20:
                    return desc
        
        # Try structured data
        json_ld = soup.find('script', type='application/ld+json')
        if json_ld:
            try:
                data = json.loads(json_ld.string)
                if isinstance(data, dict) and 'description' in data:
                    return data['description']
            except:
                pass
        
        return ""
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> dict:
        """
        Extract structured data (JSON-LD, microdata, etc.)
        """
        structured = {}
        
        # Extract JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    # Extract relevant fields
                    if '@type' in data:
                        structured['type'] = data['@type']
                    if 'publisher' in data:
                        structured['publisher'] = data['publisher']
                    if 'keywords' in data:
                        structured['keywords'] = data['keywords']
            except:
                continue
        
        return structured
    
    def _determine_topic(self, title: str, content: str, description: str) -> str:
        """
        Determine article topic based on content analysis
        """
        full_text = f"{title} {description} {content[:500]}".lower()
        
        topic_keywords = {
            'politics': ['election', 'vote', 'campaign', 'democrat', 'republican', 'congress', 'senate', 'president', 'political', 'government', 'policy', 'legislation'],
            'technology': ['tech', 'ai', 'artificial intelligence', 'software', 'app', 'digital', 'cyber', 'data', 'algorithm', 'startup', 'innovation'],
            'business': ['company', 'ceo', 'profit', 'revenue', 'stock', 'market', 'investor', 'business', 'corporate', 'merger', 'acquisition'],
            'health': ['health', 'medical', 'doctor', 'patient', 'treatment', 'disease', 'vaccine', 'hospital', 'medicine', 'clinical', 'diagnosis'],
            'science': ['research', 'study', 'scientist', 'discovery', 'experiment', 'data', 'evidence', 'theory', 'hypothesis', 'laboratory'],
            'sports': ['game', 'player', 'team', 'score', 'win', 'championship', 'tournament', 'athlete', 'coach', 'season', 'match'],
            'entertainment': ['movie', 'film', 'actor', 'actress', 'music', 'singer', 'album', 'concert', 'celebrity', 'hollywood', 'netflix'],
            'world': ['international', 'global', 'country', 'nation', 'foreign', 'diplomat', 'embassy', 'united nations', 'treaty', 'border'],
            'climate': ['climate', 'environment', 'carbon', 'emission', 'renewable', 'sustainability', 'pollution', 'conservation', 'ecology'],
            'crime': ['police', 'crime', 'arrest', 'investigation', 'court', 'judge', 'prison', 'criminal', 'victim', 'suspect', 'trial']
        }
        
        topic_scores = {}
        for topic, keywords in topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in full_text)
            if score > 0:
                topic_scores[topic] = score
        
        if topic_scores:
            return max(topic_scores, key=topic_scores.get)
        
        return 'general news'
    
    def _assess_extraction_quality(self, content: str, title: str, authors: List[str], date: str) -> dict:
        """
        Assess the quality of extraction
        """
        scores = {
            'content_score': 1.0 if len(content) > 500 else (len(content) / 500),
            'title_score': 1.0 if title and title != "Title not found" else 0.0,
            'author_score': 1.0 if authors else 0.0,
            'date_score': 1.0 if date else 0.0
        }
        
        overall_score = sum(scores.values()) / len(scores)
        
        return {
            **scores,
            'overall_score': overall_score,
            'grade': 'excellent' if overall_score > 0.8 else 'good' if overall_score > 0.6 else 'fair' if overall_score > 0.4 else 'poor'
        }


# Create a wrapper function for backwards compatibility
def fetch_article_from_url(url: str) -> Optional[Dict]:
    """
    Wrapper function to maintain compatibility with existing code
    """
    extractor = ArticleExtractor()
    result = extractor.extract_from_url(url)
    
    if result:
        # Map to expected format
        return {
            'content': result['content'],
            'domain': result['domain'],
            'title': result['title'],
            'authors': result['authors'],
            'date': result['date'],
            'url': result['url'],
            'description': result.get('description', ''),
            'topic': result.get('topic', 'general news'),
            'extraction_success': result.get('extraction_success', False)
        }
    
    return None
