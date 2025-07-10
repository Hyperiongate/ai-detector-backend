"""
Plagiarism Service - Integration with multiple plagiarism detection APIs
Now using the new base service architecture
Supports Copyscape, Copyleaks, and custom web search
"""
import os
import requests
import hashlib
import json
from datetime import datetime
from urllib.parse import quote
import time
from typing import Dict, Any, List, Optional

from .base_service import BaseAnalysisService

class PlagiarismService(BaseAnalysisService):
    """
    Professional plagiarism detection service with multiple API providers
    Inherits from BaseAnalysisService for consistent interface
    """
    
    def __init__(self, config: Dict[str, Any]):
        # Initialize with the base class
        super().__init__(config)
        
        # API credentials from config
        self.copyscape_key = config.get('copyscape_api_key', '')
        self.copyscape_user = config.get('copyscape_username', '')
        self.copyleaks_key = config.get('copyleaks_api_key', '')
        self.copyleaks_email = config.get('copyleaks_email', '')
        
        # Google Custom Search for fallback
        self.google_api_key = config.get('google_api_key', '')
        self.google_cx = config.get('google_cx', '')
        
        # Service URLs
        self.copyscape_url = "https://www.copyscape.com/api/"
        self.copyleaks_url = "https://api.copyleaks.com/v3"
        self.google_search_url = "https://www.googleapis.com/customsearch/v1"
    
    def _initialize_service(self) -> bool:
        """
        Check if at least one plagiarism service is properly configured
        """
        available_services = []
        
        # Check Copyscape
        if self.copyscape_key and self.copyscape_user:
            available_services.append('Copyscape')
            self.logger.info("Copyscape API credentials found")
        
        # Check Copyleaks
        if self.copyleaks_key and self.copyleaks_email:
            available_services.append('Copyleaks')
            self.logger.info("Copyleaks API credentials found")
        
        # Check Google Custom Search
        if self.google_api_key and self.google_cx:
            available_services.append('Google Search')
            self.logger.info("Google Custom Search credentials found")
        
        if available_services:
            self.logger.info(f"Plagiarism service initialized with: {', '.join(available_services)}")
            return True
        else:
            self.logger.warning("No plagiarism service APIs configured - will use pattern analysis only")
            return False  # Still functional but limited
    
    def analyze(self, content: str, **kwargs) -> Dict[str, Any]:
        """
        Main plagiarism analysis function
        """
        # Validate content
        is_valid, error_message = self._validate_content(content)
        if not is_valid:
            return self._create_error_response(error_message, "validation_error")
        
        try:
            # Get options
            use_real_apis = kwargs.get('use_real_apis', True) and self.is_available
            
            # Perform analysis
            results = self.check_plagiarism(content, use_real_apis)
            
            # Standardize response format
            return self._create_success_response(results)
            
        except Exception as e:
            self.logger.error(f"Plagiarism analysis failed: {str(e)}")
            return self._create_error_response(f"Analysis failed: {str(e)}")
    
    def check_plagiarism(self, text: str, use_real_apis: bool = True) -> Dict[str, Any]:
        """
        Main plagiarism checking function that tries multiple services
        """
        results = {
            'score': 0,
            'originality_score': 100,
            'sources_checked': 0,
            'matches': [],
            'highest_match': 0,
            'scan_time': 0,
            'databases_queried': [],
            'source_breakdown': {
                'Academic': 0,
                'Web Content': 0,
                'News': 0,
                'Encyclopedia': 0,
                'Social Media': 0
            },
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
        
        start_time = time.time()
        
        if not use_real_apis or not self.is_available:
            self.logger.info("Using pattern-based plagiarism analysis")
            results = self._enhanced_pattern_analysis(text)
            results['scan_time'] = round(time.time() - start_time, 2)
            return results
        
        # Try real APIs in order of preference
        
        # 1. Try Copyleaks first (most comprehensive)
        if self.copyleaks_key and self.copyleaks_email:
            try:
                self.logger.info("Attempting Copyleaks analysis")
                copyleaks_results = self._check_copyleaks(text)
                if copyleaks_results:
                    results = self._merge_results(results, copyleaks_results)
                    results['databases_queried'].append('Copyleaks')
            except Exception as e:
                self.logger.error(f"Copyleaks error: {e}")
        
        # 2. Try Copyscape for web content
        if self.copyscape_key and self.copyscape_user and results['score'] < 20:
            try:
                self.logger.info("Attempting Copyscape analysis")
                copyscape_results = self._check_copyscape(text)
                if copyscape_results:
                    results = self._merge_results(results, copyscape_results)
                    results['databases_queried'].append('Copyscape')
            except Exception as e:
                self.logger.error(f"Copyscape error: {e}")
        
        # 3. Fallback to Google Custom Search for specific phrases
        if self.google_api_key and self.google_cx and results['score'] < 15:
            try:
                self.logger.info("Attempting Google Custom Search analysis")
                google_results = self._check_google_search(text)
                if google_results:
                    results = self._merge_results(results, google_results)
                    results['databases_queried'].append('Google Search')
            except Exception as e:
                self.logger.error(f"Google search error: {e}")
        
        # If no real APIs worked, use enhanced pattern analysis
        if not results['databases_queried']:
            self.logger.warning("All API attempts failed, using pattern analysis")
            results = self._enhanced_pattern_analysis(text)
            results['databases_queried'] = ['Pattern Analysis']
        
        # Calculate final scores
        results['scan_time'] = round(time.time() - start_time, 2)
        if results['matches']:
            avg_similarity = sum(m['percentage'] for m in results['matches']) / len(results['matches'])
            results['score'] = min(avg_similarity, results['score'])
        
        results['originality_score'] = max(0, 100 - results['score'])
        results['sources_checked'] = self._estimate_sources_checked(results['databases_queried'])
        
        return results
    
    def _check_copyleaks(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Check plagiarism using Copyleaks API
        """
        try:
            # Authenticate with Copyleaks
            auth_url = f"{self.copyleaks_url}/account/login/api"
            auth_data = {
                'email': self.copyle
