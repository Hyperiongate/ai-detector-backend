"""
Text utility functions
"""
import re
from urllib.parse import urlparse

def extract_author_from_text(text):
    """
    Extract author name from text with improved detection
    """
    # First, try common byline patterns
    patterns = [
        # Standard "By" patterns
        r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
        r'by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
        r'BY\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
        
        # With punctuation
        r'By:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
        r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\s*[,\.|]',
        
        # Other patterns
        r'Written by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
        r'Article by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
        r'Story by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
        r'Reported by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
        
        # Email pattern (extract name part)
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})@',
        
        # Pattern at start of line
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\s*[-–—]',
        
        # Pattern with credentials
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}),\s*(?:Reporter|Journalist|Writer|Correspondent)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            author_name = match.group(1).strip()
            # Validate it looks like a real name
            if 2 <= len(author_name.split()) <= 4 and len(author_name) < 50:
                return author_name
    
    return None

def extract_dates_from_text(text):
    """
    Extract dates with improved patterns
    """
    dates_found = []
    
    # Date patterns
    date_patterns = [
        # Full dates
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
        
        # Relative dates
        r'\b(today|yesterday|tomorrow)\b',
        r'\b(last|this|next)\s+(week|month|year)\b',
        r'\b\d+\s+(days?|weeks?|months?|years?)\s+ago\b',
        
        # Time references
        r'\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
        r'\b(morning|afternoon|evening|night)\b',
        r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\b',
    ]
    
    for pattern in date_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            dates_found.append(match.group(0))
    
    return dates_found

def extract_source_from_url(url):
    """
    Extract source domain from URL
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return None

def extract_youtube_video_id(url):
    """
    Extract video ID from various YouTube URL formats
    """
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*&v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None
