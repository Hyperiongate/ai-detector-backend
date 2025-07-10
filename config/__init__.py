"""
Configuration package for Facts & Fakes AI
Handles configuration validation and management
"""

from .validator import ConfigurationValidator

# Import everything from the root config.py file to maintain compatibility
import sys
import os

# Add the parent directory to the path to import from root config.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Import all configuration from root config.py
    import config as root_config
    
    # Export all attributes from root config
    for attr in dir(root_config):
        if not attr.startswith('_'):
            globals()[attr] = getattr(root_config, attr)
    
    print("✓ Root config imported successfully")
    
except ImportError as e:
    print(f"⚠ Could not import root config: {e}")

__all__ = ['ConfigurationValidator']
