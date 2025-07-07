"""
Facts & Fakes AI - Main Application
Modular structure for better maintainability
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
import traceback
from datetime import datetime

# Import configuration
import config

# Import services
from services.database import db, DB_AVAILABLE, User, Contact, BetaSignup
from services.auth_service import login_required, get_current_user
from services.email_service import send_email, send_welcome_email
from services.openai_service import OPENAI_AVAILABLE, client

# Import analysis modules
from analysis.text_analysis import perform_realistic_unified_text_analysis, perform_basic_text_analysis, perform_advanced_text_analysis
from analysis.news_analysis import perform_basic_news_analysis, perform_advanced_news_analysis, perform_realistic_unified_news_check
from analysis.image_analysis import perform_realistic_image_analysis, perform_basic_image_analysis
from analysis.speech_analysis import (
    extract_claims_from_speech,
    speech_to_text,
    stream_transcript,
    batch_factcheck,
    get_youtube_transcript,
    export_speech_report
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Apply configuration
app.config.from_object(config)

# Initialize database
if DB_AVAILABLE:
    db.init_app(app)
    with app.app_context():
        try:
            db.create_all()
            print("✓ Database initialized successfully")
        except Exception as e:
            print(f"⚠ Database initialization warning: {e}")

# ============================================================================
# PAGE ROUTES
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html', user=get_current_user())

@app.route('/news')
def news():
    return render_template('news.html', user=get_current_user())

@app.route('/unified')
def unified():
    return render_template('unified.html', user=get_current_user())

@app.route('/imageanalysis')
def imageanalysis():
    return render_template('imageanalysis.html', user=get_current_user())

@app.route('/contact')
def contact():
    return render_template('contact.html', user=get_current_user())

@app.route('/missionstatement')
def missionstatement():
    return render_template('missionstatement.html', user=get_current_user())

@app.route('/pricingplan')
def pricingplan():
    return render_template('pricingplan.html', user=get_current_user())

@app.route('/speech')
@app.route('/speechcheck')
def speechcheck():
    """Speech fact-check page route"""
    return render_template('speech.html', user=get_current_user())

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    # DEVELOPMENT MODE: Always return success
    data = request.get_json()
    email = data.get('email', 'dev@factsandfakes.ai')
    
    return jsonify({
        'success': True,
        'user': {
            'email': email,
            'subscription_tier': 'pro',
            'daily_limit': 999,
            'analyses_today': 0
        }
    })

@app.route('/api/signup', methods=['POST'])
def api_signup():
    # DEVELOPMENT MODE: Always return success
    data = request.get_json()
    email = data.get('email', 'dev@factsandfakes.ai')
    
    return jsonify({
        'success': True,
        'user': {
            'email': email,
            'subscription_tier': 'pro',
            'daily_limit': 999
        }
    })

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/user/status', methods=['GET'])
def user_status():
    # DEVELOPMENT MODE: Always return authenticated
    return jsonify({
        'authenticated': True,
        'user': {
            'email': 'dev@factsandfakes.ai',
            'subscription_tier': 'pro',
            'daily_limit': 999,
            'analyses_today': 0,
            'can_analyze': True
        }
    })

# ============================================================================
# ANALYSIS API ROUTES
# ============================================================================

@app.route('/api/analyze-unified', methods=['POST'])
def analyze_unified():
    """Unified analysis endpoint - NO LOGIN REQUIRED"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        text = data.get('text', content)
        analysis_type = data.get('type', 'all')
        
        if not text and not content:
            return jsonify({'error': 'No content provided'}), 400
        
        result = {}
        
        if analysis_type in ['text', 'ai', 'all']:
            result['ai_analysis'] = perform_realistic_unified_text_analysis(text)
        
        if analysis_type in ['news', 'all']:
            result['news_analysis'] = perform_realistic_unified_news_check(text)
        
        if analysis_type in ['image'] and data.get('image'):
            result['image_analysis'] = perform_basic_image_analysis(data.get('image'))
        
        result['analysis_complete'] = True
        result['timestamp'] = datetime.utcnow().isoformat()
        result['is_pro'] = True
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Unified analysis error: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Analysis failed', 'details': str(e)}), 500

@app.route('/api/analyze-news', methods=['POST'])
def analyze_news():
    user = get_current_user()
    
    try:
        data = request.get_json()
        content = data.get('content', '')
        is_pro = True
        
        if not content:
            return jsonify({'error': 'No content provided'}), 400
        
        if is_pro:
            analysis_data = perform_advanced_news_analysis(content)
        else:
            analysis_data = perform_basic_news_analysis(content)
        
        return jsonify(analysis_data)
        
    except Exception as e:
        print(f"Analysis error: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Analysis failed'}), 500

@app.route('/api/analyze-text', methods=['POST'])
def analyze_text():
    user = get_current_user()
    
    try:
        data = request.get_json()
        text = data.get('text', '')
        is_pro = True
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if is_pro and config.OPENAI_API_KEY:
            analysis_data = perform_advanced_text_analysis(text)
        else:
            analysis_data = perform_basic_text_analysis(text)
        
        return jsonify(analysis_data)
        
    except Exception as e:
        print(f"Analysis error: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    user = get_current_user()
    
    try:
        data = request.get_json()
        image_data = data.get('image', '')
        is_pro = True
        
        if not image_data:
            return jsonify({'error': 'No image provided'}), 400
        
        analysis_data = perform_realistic_image_analysis(image_data, is_pro)
        
        return jsonify(analysis_data)
        
    except Exception as e:
        print(f"Analysis error: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Analysis failed'}), 500

# ============================================================================
# SPEECH ANALYSIS ROUTES
# ============================================================================

@app.route('/api/speech-to-text', methods=['POST'])
def api_speech_to_text():
    return speech_to_text()

@app.route('/api/stream-transcript', methods=['POST'])
def api_stream_transcript():
    return stream_transcript()

@app.route('/api/batch-factcheck', methods=['POST'])
def api_batch_factcheck():
    return batch_factcheck()

@app.route('/api/youtube-transcript', methods=['POST'])
def api_youtube_transcript():
    return get_youtube_transcript()

@app.route('/api/export-speech-report', methods=['POST'])
def api_export_speech_report():
    return export_speech_report()

# ============================================================================
# CONTACT & BETA SIGNUP
# ============================================================================

@app.route('/api/contact', methods=['POST'])
def api_contact():
    try:
        data = request.get_json()
        
        if DB_AVAILABLE:
            contact = Contact(
                name=data.get('name', ''),
                email=data.get('email', ''),
                subject=data.get('subject', ''),
                message=data.get('message', ''),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )
            db.session.add(contact)
            db.session.commit()
        
        # Send notification emails
        admin_subject = f"New Contact Form: {data.get('subject', 'No Subject')}"
        admin_html = f"""
        <html>
        <body>
            <h2>New Contact Form Submission</h2>
            <p><strong>From:</strong> {data.get('name', '')} ({data.get('email', '')})</p>
            <p><strong>Subject:</strong> {data.get('subject', '')}</p>
            <p><strong>Message:</strong></p>
            <p>{data.get('message', '').replace(chr(10), '<br>')}</p>
            <hr>
            <p><small>IP: {request.remote_addr}<br>
            Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</small></p>
        </body>
        </html>
        """
        
        admin_text = f"""
New Contact Form Submission

From: {data.get('name', '')} ({data.get('email', '')})
Subject: {data.get('subject', '')}

Message:
{data.get('message', '')}

---
IP: {request.remote_addr}
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
        """
        
        send_email(config.CONTACT_EMAIL, admin_subject, admin_html, admin_text)
        
        # Send auto-reply
        user_subject = "Thanks for contacting Facts & Fakes AI"
        user_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">Thank you for reaching out!</h2>
                <p>Hi {data.get('name', '')},</p>
                <p>We've received your message and appreciate you taking the time to contact us. Our team will review your inquiry and get back to you within 24-48 hours.</p>
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Your message:</strong></p>
                    <p style="font-style: italic;">"{data.get('message', '')}"</p>
                </div>
                <p>In the meantime, feel free to explore our platform and try out our AI detection tools.</p>
                <p>Best regards,<br>The Facts & Fakes AI Team</p>
            </div>
        </body>
        </html>
        """
        
        user_text = f"""
Hi {data.get('name', '')},

Thank you for reaching out!

We've received your message and appreciate you taking the time to contact us. Our team will review your inquiry and get back to you within 24-48 hours.

Your message:
"{data.get('message', '')}"

In the meantime, feel free to explore our platform and try out our AI detection tools.

Best regards,
The Facts & Fakes AI Team
        """
        
        send_email(data.get('email', ''), user_subject, user_html, user_text)
        
        return jsonify({'success': True, 'message': 'Thank you! We\'ll respond within 24-48 hours.'})
        
    except Exception as e:
        print(f"Contact form error: {e}")
        return jsonify({'error': 'Failed to process contact form'}), 500

@app.route('/api/beta-signup', methods=['POST'])
def beta_signup():
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        
        if not email:
            return jsonify({'error': 'Email required'}), 400
        
        # DEVELOPMENT MODE: Always return success
        return jsonify({
            'success': True,
            'message': 'Welcome to the beta! Check your email for login details.'
        })
        
    except Exception as e:
        print(f"Beta signup error: {e}")
        return jsonify({'error': 'Signup failed. Please try again.'}), 500

@app.route('/api/register', methods=['POST'])
def api_register():
    """Alternative register endpoint for unified.html"""
    return beta_signup()

# ============================================================================
# DEBUG ENDPOINTS
# ============================================================================

@app.route('/api/debug/cv-status', methods=['GET'])
def cv_status():
    """Debug endpoint to check CV module status"""
    from utils.cv_utils import CV_AVAILABLE, cv2
    
    return jsonify({
        'cv_available': CV_AVAILABLE,
        'opencv_version': cv2.__version__ if CV_AVAILABLE and cv2 else 'Not available',
        'modules_loaded': {
            'cv2': cv2 is not None if 'cv2' in locals() else False,
            'scipy': 'scipy' in globals(),
            'skimage': 'skimage' in globals()
        }
    })

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Endpoint not found'}), 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html'), 500

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
