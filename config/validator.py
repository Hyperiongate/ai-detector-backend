"""
Configuration Validator for Facts & Fakes AI
Validates API keys, environment variables, and service configurations
"""
import os
import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

class ConfigurationValidator:
    """
    Comprehensive configuration validation system
    Checks API keys, environment variables, and service requirements
    """
    
    # Define requirements for each API service
    API_REQUIREMENTS = {
        'OPENAI_API_KEY': {
            'pattern': r'^sk-[a-zA-Z0-9]{20,}',
            'service': 'OpenAI',
            'required': True,
            'description': 'OpenAI API key for AI detection'
        },
        'COPYSCAPE_API_KEY': {
            'pattern': r'^[a-zA-Z0-9]{10,}',
            'service': 'Copyscape',
            'required': False,
            'description': 'Copyscape API key for plagiarism detection'
        },
        'COPYSCAPE_USERNAME': {
            'pattern': r'^[a-zA-Z0-9_-]{3,}',
            'service': 'Copyscape',
            'required': False,
            'description': 'Copyscape username'
        },
        'COPYLEAKS_API_KEY': {
            'pattern': r'^[a-zA-Z0-9-]{20,}',
            'service': 'Copyleaks',
            'required': False,
            'description': 'Copyleaks API key for plagiarism detection'
        },
        'COPYLEAKS_EMAIL': {
            'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'service': 'Copyleaks',
            'required': False,
            'description': 'Copyleaks account email'
        },
        'NEWS_API_KEY': {
            'pattern': r'^[a-zA-Z0-9]{32}$',
            'service': 'NewsAPI',
            'required': False,
            'description': 'News API key for fact checking'
        },
        'GOOGLE_FACT_CHECK_API_KEY': {
            'pattern': r'^[a-zA-Z0-9_-]{35,}',
            'service': 'Google Fact Check',
            'required': False,
            'description': 'Google Fact Check API key'
        }
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validation_timestamp = datetime.utcnow()
        self.results = {}
    
    def validate_all_configuration(self) -> Dict[str, Any]:
        """
        Perform comprehensive validation of all configuration
        Returns detailed validation results
        """
        results = {
            'overall_status': 'unknown',
            'validation_timestamp': self.validation_timestamp.isoformat(),
            'api_keys': {},
            'services': {},
            'errors': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Validate API keys
        self._validate_api_keys(results)
        
        # Validate service availability
        self._validate_service_configurations(results)
        
        # Determine overall status
        self._determine_overall_status(results)
        
        # Generate recommendations
        self._generate_recommendations(results)
        
        self.results = results
        return results
    
    def _validate_api_keys(self, results: Dict[str, Any]):
        """Validate all API keys"""
        for key_name, requirements in self.API_REQUIREMENTS.items():
            validation = self._validate_single_api_key(key_name, requirements)
            results['api_keys'][key_name] = validation
            
            if validation['status'] == 'error' and requirements['required']:
                results['errors'].append(validation['message'])
            elif validation['status'] == 'warning':
                results['warnings'].append(validation['message'])
    
    def _validate_single_api_key(self, key_name: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single API key"""
        value = os.getenv(key_name)
        
        validation = {
            'key_name': key_name,
            'service': requirements['service'],
            'required': requirements['required'],
            'status': 'unknown',
            'message': '',
            'present': bool(value),
            'valid_format': False
        }
        
        if not value:
            if requirements['required']:
                validation['status'] = 'error'
                validation['message'] = f"Required API key {key_name} is missing"
            else:
                validation['status'] = 'warning'
                validation['message'] = f"Optional API key {key_name} is not configured"
            return validation
        
        # Check for placeholder values
        placeholder_patterns = [
            'your-actual-',
            'sk-your-',
            'your-real-',
            'add-your-',
            'insert-your-'
        ]
        
        if any(pattern in value.lower() for pattern in placeholder_patterns):
            validation['status'] = 'error'
            validation['message'] = f"{key_name} contains placeholder value, not real API key"
            return validation
        
        # Validate format with regex
        if requirements['pattern']:
            if re.match(requirements['pattern'], value):
                validation['valid_format'] = True
                validation['status'] = 'success'
                validation['message'] = f"{key_name} is properly configured"
            else:
                validation['status'] = 'error'
                validation['message'] = f"{key_name} has invalid format"
        else:
            # No pattern specified, just check it's not empty
            validation['valid_format'] = True
            validation['status'] = 'success'
            validation['message'] = f"{key_name} is present"
        
        return validation
    
    def _validate_service_configurations(self, results: Dict[str, Any]):
        """Validate service-specific configurations"""
        
        # Group API keys by service
        services = {}
        for key_name, key_data in results['api_keys'].items():
            service_name = key_data['service']
            if service_name not in services:
                services[service_name] = {
                    'name': service_name,
                    'keys': [],
                    'status': 'unknown',
                    'available': False,
                    'message': ''
                }
            services[service_name]['keys'].append(key_data)
        
        # Determine service availability
        for service_name, service_data in services.items():
            if service_name == 'OpenAI':
                # OpenAI requires just the API key
                openai_key = next((k for k in service_data['keys'] if k['key_name'] == 'OPENAI_API_KEY'), None)
                if openai_key and openai_key['status'] == 'success':
                    service_data['available'] = True
                    service_data['status'] = 'available'
                    service_data['message'] = 'OpenAI service ready for AI detection'
                else:
                    service_data['status'] = 'unavailable'
                    service_data['message'] = 'OpenAI API key required for AI detection'
            
            elif service_name == 'Copyscape':
                # Copyscape requires both API key and username
                api_key = next((k for k in service_data['keys'] if k['key_name'] == 'COPYSCAPE_API_KEY'), None)
                username = next((k for k in service_data['keys'] if k['key_name'] == 'COPYSCAPE_USERNAME'), None)
                
                if api_key and username and api_key['status'] == 'success' and username['status'] == 'success':
                    service_data['available'] = True
                    service_data['status'] = 'available'
                    service_data['message'] = 'Copyscape service ready for plagiarism detection'
                else:
                    service_data['status'] = 'unavailable'
                    service_data['message'] = 'Copyscape requires both API key and username'
            
            elif service_name == 'Copyleaks':
                # Copyleaks requires both API key and email
                api_key = next((k for k in service_data['keys'] if k['key_name'] == 'COPYLEAKS_API_KEY'), None)
                email = next((k for k in service_data['keys'] if k['key_name'] == 'COPYLEAKS_EMAIL'), None)
                
                if api_key and email and api_key['status'] == 'success' and email['status'] == 'success':
                    service_data['available'] = True
                    service_data['status'] = 'available'
                    service_data['message'] = 'Copyleaks service ready for plagiarism detection'
                else:
                    service_data['status'] = 'unavailable'
                    service_data['message'] = 'Copyleaks requires both API key and email'
            
            else:
                # For other services, check if any key is valid
                valid_keys = [k for k in service_data['keys'] if k['status'] == 'success']
                if valid_keys:
                    service_data['available'] = True
                    service_data['status'] = 'available'
                    service_data['message'] = f'{service_name} service configured'
                else:
                    service_data['status'] = 'unavailable'
                    service_data['message'] = f'{service_name} service not configured'
        
        results['services'] = services
    
    def _determine_overall_status(self, results: Dict[str, Any]):
        """Determine overall system status"""
        
        # Check if core services are available
        openai_available = results['services'].get('OpenAI', {}).get('available', False)
        plagiarism_available = any(
            service.get('available', False) 
            for name, service in results['services'].items() 
            if name in ['Copyscape', 'Copyleaks']
        )
        
        if openai_available and plagiarism_available:
            results['overall_status'] = 'fully_operational'
        elif openai_available:
            results['overall_status'] = 'ai_only'
        elif plagiarism_available:
            results['overall_status'] = 'plagiarism_only'
        else:
            results['overall_status'] = 'limited_functionality'
    
    def _generate_recommendations(self, results: Dict[str, Any]):
        """Generate actionable recommendations"""
        recommendations = []
        
        # Check OpenAI
        if not results['services'].get('OpenAI', {}).get('available', False):
            recommendations.append({
                'priority': 'high',
                'action': 'Configure OpenAI API key',
                'description': 'Add your OpenAI API key to enable AI detection',
                'url': 'https://platform.openai.com/api-keys'
            })
        
        # Check plagiarism services
        plagiarism_services = ['Copyscape', 'Copyleaks']
        available_plagiarism = [
            name for name in plagiarism_services 
            if results['services'].get(name, {}).get('available', False)
        ]
        
        if not available_plagiarism:
            recommendations.append({
                'priority': 'medium',
                'action': 'Configure plagiarism detection service',
                'description': 'Add Copyscape or Copyleaks API credentials for plagiarism detection',
                'url': 'https://www.copyscape.com/api/'
            })
        
        # Check for placeholder values
        placeholder_keys = [
            key_name for key_name, key_data in results['api_keys'].items()
            if key_data.get('status') == 'error' and 'placeholder' in key_data.get('message', '')
        ]
        
        if placeholder_keys:
            recommendations.append({
                'priority': 'high',
                'action': 'Replace placeholder API keys',
                'description': f'Replace placeholder values with real API keys: {", ".join(placeholder_keys)}'
            })
        
        results['recommendations'] = recommendations
    
    def print_validation_report(self):
        """Print a formatted validation report to console"""
        if not self.results:
            print("No validation results available. Run validate_all_configuration() first.")
            return
        
        results = self.results
        
        print("\n" + "="*60)
        print("FACTS & FAKES AI - CONFIGURATION VALIDATION REPORT")
        print("="*60)
        
        # Overall status
        status_symbols = {
            'fully_operational': '✅',
            'ai_only': '⚠️',
            'plagiarism_only': '⚠️',
            'limited_functionality': '❌'
        }
        
        symbol = status_symbols.get(results['overall_status'], '❓')
        print(f"\nOverall Status: {symbol} {results['overall_status'].replace('_', ' ').title()}")
        
        # Service status
        print(f"\n📋 Service Status:")
        for name, service in results['services'].items():
            status_symbol = '✅' if service['available'] else '❌'
            print(f"   {status_symbol} {name}: {service['message']}")
        
        # API Keys
        print(f"\n🔑 API Key Status:")
        for key_name, key_data in results['api_keys'].items():
            status_symbols = {'success': '✅', 'error': '❌', 'warning': '⚠️'}
            symbol = status_symbols.get(key_data['status'], '❓')
            print(f"   {symbol} {key_name}: {key_data['message']}")
        
        # Recommendations
        if results['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in results['recommendations']:
                priority_symbol = '🔴' if rec['priority'] == 'high' else '🟡'
                print(f"   {priority_symbol} {rec['action']}")
                print(f"      {rec['description']}")
                if 'url' in rec:
                    print(f"      URL: {rec['url']}")
        
        print("\n" + "="*60)
