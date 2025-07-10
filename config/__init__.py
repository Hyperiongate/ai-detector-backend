"""
Configuration package for Facts & Fakes AI
Handles configuration validation and management
"""

from .validator import ConfigurationValidator

# Import specific items from root config.py to avoid circular imports
try:
    # Import the root config module directly
    import sys
    import os
    
    # Get the parent directory (project root)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    # Temporarily add parent to path
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    # Import the root config as a module
    import importlib.util
    config_path = os.path.join(parent_dir, 'config.py')
    
    if os.path.exists(config_path):
        spec = importlib.util.spec_from_file_location("root_config", config_path)
        root_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(root_config)
        
        # Export specific variables that are commonly used
        if hasattr(root_config, 'FAMOUS_QUOTES'):
            FAMOUS_QUOTES = root_config.FAMOUS_QUOTES
        if hasattr(root_config, 'OPENAI_API_KEY'):
            OPENAI_API_KEY = root_config.OPENAI_API_KEY
        if hasattr(root_config, 'SECRET_KEY'):
            SECRET_KEY = root_config.SECRET_KEY
        if hasattr(root_config, 'DATABASE_URL'):
            DATABASE_URL = root_config.DATABASE_URL
        if hasattr(root_config, 'SQLALCHEMY_DATABASE_URI'):
            SQLALCHEMY_DATABASE_URI = root_config.SQLALCHEMY_DATABASE_URI
        if hasattr(root_config, 'SQLALCHEMY_TRACK_MODIFICATIONS'):
            SQLALCHEMY_TRACK_MODIFICATIONS = root_config.SQLALCHEMY_TRACK_MODIFICATIONS
        
        # Export all uppercase attributes (configuration variables)
        for attr_name in dir(root_config):
            if attr_name.isupper() and not attr_name.startswith('_'):
                globals()[attr_name] = getattr(root_config, attr_name)
        
        print("✓ Root config variables imported successfully")
    else:
        print("⚠ Root config.py not found")
        
except Exception as e:
    print(f"⚠ Could not import root config: {e}")
    # Define fallback values
    FAMOUS_QUOTES = []

__all__ = ['ConfigurationValidator']
