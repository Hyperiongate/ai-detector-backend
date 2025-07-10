"""
Service Registry for Facts & Fakes AI
Central management system for all analysis services
"""
import logging
from typing import Dict, Type, Any, Optional, List
from datetime import datetime
from .base_service import BaseAnalysisService

class ServiceRegistry:
    """
    Central registry that manages all analysis services
    Handles service initialization, health monitoring, and access
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._service_classes: Dict[str, Type[BaseAnalysisService]] = {}
        self._services: Dict[str, BaseAnalysisService] = {}
        self._initialization_order: List[str] = []
        self.registry_created = datetime.utcnow()
        
        self.logger.info("Service Registry initialized")
    
    def register_service_class(self, service_name: str, service_class: Type[BaseAnalysisService]):
        """
        Register a service class for later initialization
        
        Args:
            service_name: Unique identifier for the service
            service_class: The service class that inherits from BaseAnalysisService
        """
        if not issubclass(service_class, BaseAnalysisService):
            raise ValueError(f"Service class {service_class.__name__} must inherit from BaseAnalysisService")
        
        if service_name in self._service_classes:
            self.logger.warning(f"Service {service_name} is already registered. Overwriting.")
        
        self._service_classes[service_name] = service_class
        self.logger.info(f"Registered service class: {service_name} ({service_class.__name__})")
    
    def initialize_service(self, service_name: str, config: Dict[str, Any]) -> bool:
        """
        Initialize a registered service with the provided configuration
        
        Args:
            service_name: Name of the service to initialize
            config: Configuration dictionary for the service
            
        Returns:
            True if initialization successful, False otherwise
        """
        if service_name not in self._service_classes:
            self.logger.error(f"Service {service_name} not registered. Available services: {list(self._service_classes.keys())}")
            return False
        
        try:
            service_class = self._service_classes[service_name]
            self.logger.info(f"Initializing service: {service_name}")
            
            # Create service instance
            service_instance = service_class(config)
            
            # Store the service
            self._services[service_name] = service_instance
            
            # Track initialization order
            if service_name not in self._initialization_order:
                self._initialization_order.append(service_name)
            
            if service_instance.is_available:
                self.logger.info(f"Service {service_name} initialized successfully and is available")
                return True
            else:
                self.logger.warning(f"Service {service_name} initialized but is not available (likely configuration issue)")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize service {service_name}: {str(e)}")
            return False
    
    def get_service(self, service_name: str) -> Optional[BaseAnalysisService]:
        """
        Get an initialized service instance
        
        Args:
            service_name: Name of the service to retrieve
            
        Returns:
            Service instance if available, None otherwise
        """
        service = self._services.get(service_name)
        
        if service is None:
            self.logger.warning(f"Service {service_name} not found. Available services: {list(self._services.keys())}")
            return None
        
        if not service.is_available:
            self.logger.warning(f"Service {service_name} is not available")
            return None
        
        return service
    
    def is_service_available(self, service_name: str) -> bool:
        """
        Check if a service is available for use
        
        Args:
            service_name: Name of the service to check
            
        Returns:
            True if service is available, False otherwise
        """
        service = self._services.get(service_name)
        return service is not None and service.is_available
    
    def get_available_services(self) -> List[str]:
        """
        Get list of all available service names
        
        Returns:
            List of service names that are available
        """
        return [
            name for name, service in self._services.items() 
            if service.is_available
        ]
    
    def get_all_services(self) -> List[str]:
        """
        Get list of all registered service names (available or not)
        
        Returns:
            List of all registered service names
        """
        return list(self._services.keys())
    
    def get_service_health_status(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Get health status for a specific service
        
        Args:
            service_name: Name of the service
            
        Returns:
            Health status dictionary or None if service not found
        """
        service = self._services.get(service_name)
        if service:
            return service.get_health_status()
        return None
    
    def get_registry_health_status(self) -> Dict[str, Any]:
        """
        Get comprehensive health status for all services and the registry
        
        Returns:
            Complete health status report
        """
        status = {
            'registry_status': 'operational',
            'registry_created': self.registry_created.isoformat(),
            'total_registered_classes': len(self._service_classes),
            'total_initialized_services': len(self._services),
            'available_services': len(self.get_available_services()),
            'initialization_order': self._initialization_order.copy(),
            'services': {}
        }
        
        # Get status for each service
        for service_name, service in self._services.items():
            try:
                status['services'][service_name] = service.get_health_status()
            except Exception as e:
                status['services'][service_name] = {
                    'service_name': service_name,
                    'error': f"Failed to get health status: {str(e)}",
                    'is_available': False
                }
        
        # Add registered but uninitialized services
        for class_name in self._service_classes:
            if class_name not in self._services:
                status['services'][class_name] = {
                    'service_name': class_name,
                    'status': 'registered_but_not_initialized',
                    'is_available': False
                }
        
        return status
    
    def reinitialize_service(self, service_name: str, config: Dict[str, Any]) -> bool:
        """
        Reinitialize an existing service with new configuration
        
        Args:
            service_name: Name of the service to reinitialize
            config: New configuration for the service
            
        Returns:
            True if reinitialization successful, False otherwise
        """
        if service_name not in self._service_classes:
            self.logger.error(f"Cannot reinitialize unregistered service: {service_name}")
            return False
        
        # Remove existing service if present
        if service_name in self._services:
            self.logger.info(f"Removing existing service instance: {service_name}")
            del self._services[service_name]
        
        # Initialize with new config
        return self.initialize_service(service_name, config)
    
    def shutdown_service(self, service_name: str):
        """
        Shutdown and remove a service from the registry
        
        Args:
            service_name: Name of the service to shutdown
        """
        if service_name in self._services:
            self.logger.info(f"Shutting down service: {service_name}")
            # If the service has a shutdown method, call it
            service = self._services[service_name]
            if hasattr(service, 'shutdown'):
                try:
                    service.shutdown()
                except Exception as e:
                    self.logger.error(f"Error during service shutdown: {e}")
            
            del self._services[service_name]
            
            # Remove from initialization order
            if service_name in self._initialization_order:
                self._initialization_order.remove(service_name)
    
    def shutdown_all_services(self):
        """
        Shutdown all services in reverse initialization order
        """
        self.logger.info("Shutting down all services")
