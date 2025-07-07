"""
Authentication service - Login decorators and user management
"""
from functools import wraps
from flask import session, jsonify
from services.database import DB_AVAILABLE

def login_required(f):
    """Authentication decorator - DISABLED FOR DEVELOPMENT"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # DEVELOPMENT MODE: Always allow access
        print("🔓 Login requirement bypassed for development")
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Helper function to get current user"""
    # DEVELOPMENT MODE: Return a mock user
    if DB_AVAILABLE:
        class MockUser:
            email = "dev@factsandfakes.ai"
            subscription_tier = "pro"
            daily_analyses_count = 0
            
            def get_daily_limit(self):
                return 999
            
            def can_analyze(self):
                return True
            
            def increment_analysis_count(self):
                pass
        
        return MockUser()
    return None
