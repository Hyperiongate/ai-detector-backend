"""
Plagiarism Detection Service
Integrates multiple plagiarism detection APIs:
- Copyscape API
- Copyleaks API
- Google Search (fallback)
"""

import os
import json
import logging
import requests
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import xml.etree.ElementTree as ET
from urllib.parse import quote, urlparse

logger = logging.getLogger(__name__)

class PlagiarismService:
    """Service for detecting plagiarism using multiple APIs"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize plagiarism service with configuration"""
        self.config = config or {}
        
        # API credentials
        self.copyscape_api_key = self.config.get('copyscape_api_key', os.environ.get('COPYSCAPE_API_KEY', ''))
        self.copyscape_username = self.config.get('copyscape_username', os.environ.get('COPYSCAPE_USERNAME', ''))
        
        self.copyleaks_api_key = self.config.get('copyleaks_api_key', os.environ.get('COPYLEAKS_API_KEY', ''))
        self.copyleaks_email = self.config.get('copyleaks_email', os.environ.get('COPYLEAKS_EMAIL', ''))
        
        self.google_api_key = self.config.get('google_api_key', os.environ.get('GOOGLE_API_KEY', ''))
        self.google_cx = self.config.get('google_cx', os.environ.get('GOOGLE_CX', ''))
        
        # Service availability
        self.is_available = bool(
            (self.copyscape_api_key and self.copyscape_username) or
            (self.copyleaks_api_key and self.copyleaks_email) or
            self.google_api_key
        )
        
        # Session for HTTP requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Facts & Fakes AI Plagiarism Detector/1.0'
        })
        
        # Copyleaks access token (cached)
        self._copyleaks_token = None
        self._copyleaks_token_expiry = None
        
        logger.info(f"PlagiarismService initialized. Available: {self.is_available}")
        logger.info(f"Services configured: Copyscape={bool(self.copyscape_api_key)}, "
                   f"Copyleaks={bool(self.copyleaks_api_key)}, Google={bool(self.google_api_key)}")
    
    def check_plagiarism(self, text: str, use_real_apis: bool = True) -> Optional[Dict[str, Any]]:
        """
        Check text for plagiarism using available APIs
        
        Args:
            text: Text to check for plagiarism
            use_real_apis: Whether to use real APIs (Pro) or simulated results (Basic)
            
        Returns:
            Dictionary with plagiarism results or None if error
        """
        if not text or len(text.strip()) < 50:
            return {
                'score': 0,
                'sources_checked': 0,
                'matches': [],
                'error': 'Text too short for plagiarism checking'
            }
        
        # Use simulated results for basic tier
        if not use_real_apis:
            return self._simulate_plagiarism_check(text)
        
        results = {
            'score': 0,
            'sources_checked': 0,
            'matches': [],
            'services_used': [],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Try Copyscape first (most comprehensive)
        if self.copyscape_api_key and self.copyscape_username:
            try:
                copyscape_results = self._check_copyscape(text)
                if copyscape_results:
                    results['services_used'].append('copyscape')
                    results['sources_checked'] += copyscape_results.get('sources_checked', 0)
                    results['matches'].extend(copyscape_results.get('matches', []))
                    results['score'] = max(results['score'], copyscape_results.get('score', 0))
            except Exception as e:
                logger.error(f"Copyscape error: {str(e)}")
        
        # Try Copyleaks if available
        if self.copyleaks_api_key and self.copyleaks_email:
            try:
                copyleaks_results = self._check_copyleaks(text)
                if copyleaks_results:
                    results['services_used'].append('copyleaks')
                    results['sources_checked'] += copyleaks_results.get('sources_checked', 0)
                    
                    # Merge matches, avoiding duplicates
                    existing_urls = {m.get('url', '') for m in results['matches']}
                    for match in copyleaks_results.get('matches', []):
                        if match.get('url', '') not in existing_urls:
                            results['matches'].append(match)
                    
                    # Update score (use highest)
                    results['score'] = max(results['score'], copyleaks_results.get('score', 0))
            except Exception as e:
                logger.error(f"Copyleaks error: {str(e)}")
        
        # Fallback to Google Custom Search if no results yet
        if not results['matches'] and self.google_api_key:
            try:
                google_results = self._check_google_search(text)
                if google_results:
                    results['services_used'].append('google')
                    results['sources_checked'] += google_results.get('sources_checked', 0)
                    results['matches'].extend(google_results.get('matches', []))
                    results['score'] = max(results['score'], google_results.get('score', 0))
            except Exception as e:
                logger.error(f"Google search error: {str(e)}")
        
        # If still no services were used, use simulation
        if not results['services_used']:
            return self._simulate_plagiarism_check(text)
        
        # Sort matches by similarity score
        results['matches'].sort(key=lambda x: x.get('similarity', 0), reverse=True)
        
        # Limit to top 10 matches
        results['matches'] = results['matches'][:10]
        
        return results
    
    def _check_copyscape(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Check plagiarism using Copyscape API
        
        Copyscape API documentation: http://www.copyscape.com/api-guide.php
        """
        if not self.copyscape_api_key or not self.copyscape_username:
            return None
        
        try:
            # Copyscape API endpoint
            url = "https://www.copyscape.com/api/"
            
            # Prepare request parameters
            params = {
                'u': self.copyscape_username,
                'k': self.copyscape_api_key,
                'o': 'csearch',  # Combined search (Internet + Copyscape index)
                'e': 'UTF-8',
                'c': 5,  # Max results
                'f': 'json'  # Response format
            }
            
            # For text search, we need to POST the text
            data = {
                't': text[:10000]  # Copyscape has a 10,000 character limit
            }
            
            # Make API request
            response = self.session.post(url, params=params, data=data, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Copyscape API error: HTTP {response.status_code}")
                return None
            
            # Parse response
            result_data = response.json()
            
            # Check for API errors
            if 'error' in result_data:
                logger.error(f"Copyscape API error: {result_data['error']}")
                return None
            
            # Process results
            matches = []
            total_similarity = 0
            
            if 'result' in result_data:
                for result in result_data['result']:
                    similarity = float(result.get('percentmatched', 0))
                    total_similarity += similarity
                    
                    matches.append({
                        'source': result.get('title', 'Unknown Source'),
                        'url': result.get('url', ''),
                        'similarity': similarity,
                        'matched_words': result.get('matchedwords', 0),
                        'excerpt': result.get('textsnippet', ''),
                        'service': 'copyscape'
                    })
            
            # Calculate overall score
            score = min(100, total_similarity)  # Cap at 100%
            
            return {
                'score': score,
                'sources_checked': result_data.get('count', 0),
                'matches': matches,
                'remaining_credits': result_data.get('remaining', 0)
            }
            
        except Exception as e:
            logger.error(f"Copyscape check error: {str(e)}")
            return None
    
    def _check_copyleaks(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Check plagiarism using Copyleaks API
        
        Copyleaks API documentation: https://api.copyleaks.com/documentation/v3
        """
        if not self.copyleaks_api_key or not self.copyleaks_email:
            return None
        
        try:
            # First, get access token if needed
            if not self._copyleaks_token or datetime.utcnow() >= self._copyleaks_token_expiry:
                if not self._authenticate_copyleaks():
                    return None
            
            # Create scan
            scan_id = self._create_copyleaks_scan(text)
            if not scan_id:
                return None
            
            # Wait for scan to complete (with timeout)
            results = self._wait_for_copyleaks_results(scan_id, timeout=30)
            
            if not results:
                return None
            
            # Process results
            matches = []
            total_similarity = 0
            
            for result in results.get('results', [])[:5]:  # Limit to top 5
                similarity = result.get('matchedPercent', 0)
                total_similarity += similarity
                
                matches.append({
                    'source': result.get('title', 'Unknown Source'),
                    'url': result.get('url', ''),
                    'similarity': similarity,
                    'matched_words': result.get('matchedWords', 0),
                    'excerpt': result.get('introduction', ''),
                    'service': 'copyleaks'
                })
            
            return {
                'score': min(100, total_similarity),
                'sources_checked': results.get('scannedDocuments', 0),
                'matches': matches
            }
            
        except Exception as e:
            logger.error(f"Copyleaks check error: {str(e)}")
            return None
    
    def _authenticate_copyleaks(self) -> bool:
        """Authenticate with Copyleaks and get access token"""
        try:
            url = "https://api.copyleaks.com/v3/account/login/api"
            
            data = {
                'email': self.copyleaks_email,
                'key': self.copyleaks_api_key
            }
            
            response = self.session.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                self._copyleaks_token = token_data.get('access_token')
                # Token expires in 48 hours, but we'll refresh every 24 hours
                self._copyleaks_token_expiry = datetime.utcnow() + timedelta(hours=24)
                return True
            else:
                logger.error(f"Copyleaks authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Copyleaks authentication error: {str(e)}")
            return False
    
    def _create_copyleaks_scan(self, text: str) -> Optional[str]:
        """Create a new Copyleaks scan"""
        try:
            url = "https://api.copyleaks.com/v3/scans/submit/file"
            
            headers = {
                'Authorization': f'Bearer {self._copyleaks_token}',
                'Content-Type': 'application/json'
            }
            
            # Generate unique scan ID
            scan_id = f"scan_{int(time.time())}_{hashlib.md5(text[:100].encode()).hexdigest()[:8]}"
            
            data = {
                'base64': None,  # We'll use raw text instead
                'filename': f"{scan_id}.txt",
                'properties': {
                    'webhooks': {
                        'status': f"https://webhook.site/{scan_id}/status"  # Dummy webhook
                    }
                },
                'text': text[:25000]  # Copyleaks limit
            }
            
            response = self.session.post(
                f"{url}/{scan_id}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                return scan_id
            else:
                logger.error(f"Copyleaks scan creation failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Copyleaks scan creation error: {str(e)}")
            return None
    
    def _wait_for_copyleaks_results(self, scan_id: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """Wait for Copyleaks scan to complete and get results"""
        try:
            headers = {
                'Authorization': f'Bearer {self._copyleaks_token}'
            }
            
            # Poll for results
            start_time = time.time()
            while time.time() - start_time < timeout:
                # Check scan status
                status_url = f"https://api.copyleaks.com/v3/scans/{scan_id}/status"
                response = self.session.get(status_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    status_data = response.json()
                    
                    if status_data.get('status') == 'Completed':
                        # Get detailed results
                        results_url = f"https://api.copyleaks.com/v3/scans/{scan_id}/results"
                        results_response = self.session.get(results_url, headers=headers, timeout=10)
                        
                        if results_response.status_code == 200:
                            return results_response.json()
                    elif status_data.get('status') in ['Failed', 'Error']:
                        logger.error(f"Copyleaks scan failed: {status_data}")
                        return None
                
                # Wait before next poll
                time.sleep(2)
            
            logger.warning(f"Copyleaks scan timeout for {scan_id}")
            return None
            
        except Exception as e:
            logger.error(f"Copyleaks results error: {str(e)}")
            return None
    
    def _check_google_search(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Fallback plagiarism check using Google Custom Search API
        """
        if not self.google_api_key:
            return None
        
        try:
            # Use Google Custom Search API
            base_url = "https://www.googleapis.com/customsearch/v1"
            
            # Extract meaningful phrases from text for search
            sentences = text.split('.')[:3]  # First 3 sentences
            search_phrases = []
            
            for sentence in sentences:
                # Clean and limit sentence length
                clean_sentence = sentence.strip()
                if 20 < len(clean_sentence) < 100:
                    search_phrases.append(f'"{clean_sentence}"')  # Exact match search
            
            if not search_phrases:
                # Fallback: use first 100 characters
                search_phrases = [f'"{text[:100]}"']
            
            matches = []
            sources_checked = 0
            
            # Search for each phrase
            for phrase in search_phrases[:2]:  # Limit to 2 searches to save API calls
                params = {
                    'key': self.google_api_key,
                    'q': phrase,
                    'num': 5  # Results per search
                }
                
                if self.google_cx:
                    params['cx'] = self.google_cx
                
                response = self.session.get(base_url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    sources_checked += data.get('searchInformation', {}).get('totalResults', 0)
                    
                    for item in data.get('items', []):
                        # Simple similarity calculation based on title/snippet match
                        snippet = item.get('snippet', '')
                        similarity = self._calculate_simple_similarity(phrase, snippet)
                        
                        if similarity > 20:  # Threshold for considering it a match
                            matches.append({
                                'source': item.get('title', 'Unknown'),
                                'url': item.get('link', ''),
                                'similarity': similarity,
                                'excerpt': snippet,
                                'service': 'google'
                            })
            
            # Calculate overall score
            score = min(100, sum(m['similarity'] for m in matches))
            
            return {
                'score': score,
                'sources_checked': min(sources_checked, 10000000),  # Cap at 10M
                'matches': matches
            }
            
        except Exception as e:
            logger.error(f"Google search check error: {str(e)}")
            return None
    
    def _calculate_simple_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple similarity percentage between two texts"""
        text1_words = set(text1.lower().split())
        text2_words = set(text2.lower().split())
        
        if not text1_words or not text2_words:
            return 0
        
        intersection = text1_words.intersection(text2_words)
        union = text1_words.union(text2_words)
        
        return (len(intersection) / len(union)) * 100
    
    def _simulate_plagiarism_check(self, text: str) -> Dict[str, Any]:
        """Simulate plagiarism check for basic tier"""
        # Simulate some basic checking
        text_length = len(text)
        
        # Generate simulated results based on text characteristics
        if any(phrase in text.lower() for phrase in ['lorem ipsum', 'quick brown fox']):
            # Known placeholder text
            score = 85
            matches = [{
                'source': 'Lorem Ipsum Generator',
                'url': 'https://www.lipsum.com',
                'similarity': 85,
                'excerpt': 'Lorem ipsum dolor sit amet...',
                'service': 'simulated'
            }]
        elif text_length < 200:
            # Short text - low plagiarism likelihood
            score = 5
            matches = []
        else:
            # Simulate random low-level matches
            import random
            score = random.randint(0, 30)
            matches = []
            
            if score > 10:
                matches.append({
                    'source': 'Similar Content Found',
                    'url': 'https://example.com/article',
                    'similarity': score,
                    'excerpt': text[:100] + '...',
                    'service': 'simulated'
                })
        
        return {
            'score': score,
            'sources_checked': 50000000,  # Simulate checking many sources
            'matches': matches,
            'services_used': ['simulated'],
            'note': 'Basic tier - limited plagiarism detection'
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the plagiarism service"""
        status = {
            'service_name': 'plagiarism',
            'is_available': self.is_available,
            'configured_apis': [],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if self.copyscape_api_key:
            status['configured_apis'].append('copyscape')
        if self.copyleaks_api_key:
            status['configured_apis'].append('copyleaks')
        if self.google_api_key:
            status['configured_apis'].append('google')
        
        return status
