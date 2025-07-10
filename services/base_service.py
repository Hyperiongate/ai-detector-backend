"""
Base Service Architecture for Facts & Fakes AI
All analysis services inherit from this base class
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
import time
from datetime import datetime

class BaseAnalysisService(ABC):
    """
    Abstract base class for all analysis services
    Provides common functionality and enforces consistent interface
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.service_name = self.__class__.__name__
        self.logger = logging.getLogger(self.service_name)
        self.initialization_time = datetime.utcnow()
        self.is_available = False
        self.last_health_check = None
        
        # Initialize the service
        try:
            self.is_available = self._initialize_service()
            if self.is_available:
                self.logger.info(f"{self.service_name} initialized successfully")
            else:
                self.logger.warning(f"{self.service_name} initialization failed")
        except Exception as e:
            self.logger.error(f"{self.service_name} initialization error: {e}")
            self.is_available = False
    
    @abstractmethod
    def _initialize_service(self) -> bool:
        """
        Initialize the specific service (API clients, validation, etc.)
        Returns True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def analyze(self, content: str, **kwargs) -> Dict[str, Any]:
        """
        Perform analysis on the provided content
        Must return a standardized result format
        """
        pass
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Return comprehensive health information about this service
        """
        self.last_health_check = datetime.utcnow()
        
        return {
            'service_name': self.service_name,
            'is_available': self.is_available,
            'initialization_time': self.initialization_time.isoformat(),
            'last_health_check': self.last_health_check.isoformat(),
            'config_keys_present': list(self.config.keys()),
            'uptime_seconds': (datetime.utcnow() - self.initialization_time).total_seconds()
        }
    
    def _create_error_response(self, error_message: str, error_type: str = "service_error") -> Dict[str, Any]:
        """
        Create standardized error response
        """
        return {
            'success': False,
            'error': error_message,
            'error_type': error_type,
            'service': self.service_name,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _create_success_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create standardized success response
        """
        return {
            'success': True,
            'data': data,
            'service': self.service_name,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _validate_content(self, content: str) -> tuple[bool, str]:
        """
        Validate input content
        Returns (is_valid, error_message)
        """
        if not content:
            return False, "No content provided"
        
        if not isinstance(content, str):
            return False, "Content must be a string"
        
        if len(content.strip()) < 10:
            return False, "Content too short (minimum 10 characters)"
        
        if len(content) > 100000:  # 100k character limit
            return False, "Content too long (maximum 100,000 characters)"
        
        return True, ""
