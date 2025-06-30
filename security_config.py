"""
Security configuration for Facts & Fakes AI Platform
COPY THIS ENTIRE FILE AS security_config.py
"""

# SAFE Python 3.13 compatible imports with fallbacks
try:
    from flask_talisman import Talisman
    TALISMAN_AVAILABLE = True
except ImportError:
    TALISMAN_AVAILABLE = False
    Talisman = None

try:
    from flask_wtf.csrf import CSRFProtect
    CSRF_AVAILABLE = True
except ImportError:
    CSRF_AVAILABLE = False
    CSRFProtect = None

# Content Security Policy - tells browsers what's safe to load
CSP_POLICY = {
    'default-src': ['\'self\''],
    'script-src': [
        '\'self\'',
        'https://cdnjs.cloudflare.com',
        'https://www.googletagmanager.com',
        'https://www.google-analytics.com',
        '\'unsafe-inline\'',
    ],
    'style-src': [
        '\'self\'',
        'https://cdnjs.cloudflare.com',
        'https://fonts.googleapis.com',
        '\'unsafe-inline\'',
    ],
    'font-src': [
        '\'self\'',
        'https://fonts.gstatic.com',
        'https://cdnjs.cloudflare.com',
        'data:',
    ],
    'img-src': [
        '\'self\'',
        'data:',
        'https:',
        'blob:',
    ],
    'connect-src': [
        '\'self\'',
        'https://api.openai.com',
        'https://newsapi.org',
        'https://www.googleapis.com',
        'https://factchecktools.googleapis.com',
        'https://*.onrender.com',
        'https://factsandfakes.ai',
    ],
    'frame-src': ['\'self\''],
    'object-src': ['\'none\''],
    'media-src': ['\'self\'', 'data:', 'https:'],
    'worker-src': ['\'self\'', 'blob:'],
}

# Security headers configuration
TALISMAN_CONFIG = {
    'force_https': True,
    'force_https_permanent': False,
    'strict_transport_security': True,
    'strict_transport_security_max_age': 31536000,
    'strict_transport_security_include_subdomains': True,
    'strict_transport_security_preload': True,
    'frame_options': 'SAMEORIGIN',
    'content_security_policy': CSP_POLICY,
    'content_security_policy_nonce_in': ['script-src', 'style-src'],
    'session_cookie_secure': True,
    'session_cookie_http_only': True,
    'session_cookie_samesite': 'Lax',
    'referrer_policy': 'strict-origin-when-cross-origin',
    'feature_policy': {
        'geolocation': '\'none\'',
        'camera': '\'none\'',
        'microphone': '\'none\'',
        'payment': '\'none\'',
    },
}

def init_security_headers(app):
    """Initialize security headers"""
    if not TALISMAN_AVAILABLE:
        app.logger.warning("Talisman not available - security headers not enabled")
        return None
    
    config = TALISMAN_CONFIG.copy()
    if app.debug:
        config['force_https'] = False
        config['session_cookie_secure'] = False
        app.logger.info("Security: HTTPS enforcement disabled in debug mode")
    
    try:
        talisman = Talisman(app, **config)
        app.logger.info("Security: Talisman security headers initialized")
        return talisman
    except Exception as e:
        app.logger.error(f"Failed to initialize Talisman: {e}")
        return None

def init_csrf_protection(app):
    """Initialize CSRF protection"""
    if CSRF_AVAILABLE:
        try:
            csrf = CSRFProtect(app)
            app.logger.info("Security: CSRF protection initialized")
            return csrf
        except Exception as e:
            app.logger.error(f"Failed to initialize CSRF: {e}")
    
    app.logger.warning("No CSRF protection available")
    return None

def configure_security_settings(app):
    """Configure security settings"""
    app.config.update(
        SESSION_COOKIE_SECURE=not app.debug,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=1800,
        WTF_CSRF_TIME_LIMIT=3600,
        WTF_CSRF_SSL_STRICT=not app.debug,
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
        SEND_FILE_MAX_AGE_DEFAULT=31536000,
    )
    app.logger.info("Security: Additional security settings configured")

def init_all_security(app):
    """Initialize all security components"""
    app.logger.info("Initializing security components...")
    
    configure_security_settings(app)
    talisman = init_security_headers(app)
    csrf = init_csrf_protection(app)
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        from flask import request, jsonify
        app.logger.warning(f"Bad request from IP: {request.remote_addr}")
        if request.is_json:
            return jsonify({'error': 'Bad request'}), 400
        return 'Bad Request', 400

    @app.errorhandler(403)
    def forbidden(error):
        from flask import request, jsonify
        app.logger.warning(f"Forbidden access from IP: {request.remote_addr}")
        if request.is_json:
            return jsonify({'error': 'Forbidden'}), 403
        return 'Forbidden', 403
    
    return {'talisman': talisman, 'csrf': csrf}

def sanitize_text_input(text, max_length=10000):
    """Sanitize text input"""
    if not text or not text.strip():
        return False, "Text cannot be empty"
    
    text = text.strip()
    
    if len(text) > max_length:
        return False, f"Text too long (max {max_length:,} characters)"
    
    import re
    suspicious_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'onload\s*=',
        r'onerror\s*=',
        r'onclick\s*=',
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
            return False, "Invalid characters detected"
    
    return True, text

def validate_file_upload(file):
    """Validate uploaded files"""
    if not file or file.filename == '':
        return False, "No file selected"
    
    allowed_extensions = {'.txt', '.pdf', '.png', '.jpg', '.jpeg', '.gif', '.docx'}
    filename = file.filename.lower()
    
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        return False, f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"
    
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    
    if size > 16 * 1024 * 1024:
        return False, "File too large (max 16MB)"
    
    return True, None

def log_security_event(app, event_type, details, ip_address=None):
    """Log security events"""
    from flask import request
    ip = ip_address or (request.remote_addr if request else 'unknown')
    app.logger.warning(f"SECURITY EVENT - {event_type}: {details} | IP: {ip}")

def validate_security_config(app):
    """Validate security configuration"""
    issues = []
    
    if not app.config.get('SECRET_KEY'):
        issues.append("SECRET_KEY not configured")
    
    if app.config.get('SECRET_KEY') == 'dev' and not app.debug:
        issues.append("Using development SECRET_KEY in production")
    
    if issues:
        for issue in issues:
            app.logger.error(f"Security configuration issue: {issue}")
        return False
    
    app.logger.info("Security configuration validation passed")
    return True
