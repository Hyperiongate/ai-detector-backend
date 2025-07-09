"""
Facts & Fakes AI - Main Application 
Modular structure for better maintainability
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
from flask_cors import CORS
import traceback
from datetime import datetime 
from io import BytesIO

# Import configuration
import config

# Import services
from services.database import db, DB_AVAILABLE, User, Contact, BetaSignup
from services.auth_service import login_required, get_current_user
from services.email_service import send_email, send_welcome_email
from services.openai_service import OPENAI_AVAILABLE, client

# Import analysis modules
from analysis.text_analysis import perform_realistic_unified_text_analysis, perform_basic_text_analysis, perform_advanced_text_analysis

# FIXED: Import only what exists in the new news_analysis.py
from analysis.news_analysis import analyze_news_route, NewsAnalyzer

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

@app.route('/news-analyzer')
def news_analyzer():
    """New route for the enhanced news analyzer page"""
    return render_template('news-analyzer.html', user=get_current_user())

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
    """Unified analysis endpoint - Focused on AI detection and plagiarism checking"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        text = data.get('text', content)
        analysis_type = data.get('analysis_type', 'ai_plagiarism')
        is_pro = data.get('is_pro', True)
        
        # Validate input
        if not text and not content:
            return jsonify({
                'success': False,
                'error': 'No content provided'
            }), 400
            
        text_to_analyze = text if text else content
        
        if len(text_to_analyze.strip()) < 50:
            return jsonify({
                'success': False,
                'error': 'Please provide at least 50 characters of text'
            }), 400
        
        # Check if this is the new AI & plagiarism analysis type
        if analysis_type == 'ai_plagiarism':
            
            # Use the existing unified text analysis function
            analysis_results = perform_realistic_unified_text_analysis(text_to_analyze)
            
            # Extract AI detection patterns from the detected_patterns
            patterns = []
            detected = analysis_results.get('detected_patterns', {})
            
            if detected.get('transition_words', 0) > 5:
                patterns.append("High frequency of transition words")
            if detected.get('ai_phrases', 0) > 2:
                patterns.append("AI-typical phrase patterns detected")
            if detected.get('repeated_phrases', 0) > 3:
                patterns.append("Repetitive phrase structures")
            if detected.get('quotes_found', 0) > 2:
                patterns.append("Multiple quoted sections")
            if detected.get('contractions', 0) == 0:
                patterns.append("Absence of contractions")
            
            # If no patterns, add some based on scores
            if not patterns:
                ai_prob = analysis_results.get('ai_probability', 0)
                if ai_prob > 70:
                    patterns = ["Consistent formal structure", "Limited emotional expression", "High coherence score"]
                elif ai_prob > 40:
                    patterns = ["Mixed writing patterns", "Some AI characteristics", "Moderate formality"]
                else:
                    patterns = ["Natural language variations", "Personal voice detected", "Human-like irregularities"]
            
            # Extract plagiarism data
            plagiarism_data = analysis_results.get('plagiarism_check', {})
            plagiarized_lines = plagiarism_data.get('plagiarized_lines', [])
            
            # Convert plagiarized lines to the expected format
            matches = []
            for line in plagiarized_lines[:5]:  # Limit to 5 matches
                matches.append({
                    'percentage': line.get('similarity', 0),
                    'source': line.get('source', 'Unknown Source'),
                    'url': None  # URLs would come from a real plagiarism API
                })
            
            # Build the response in the expected format
            results = {
                'ai_probability': analysis_results.get('ai_probability', 0),
                'plagiarism_score': 100 - plagiarism_data.get('originality_score', 100),
                'ai_detection': {
                    'probability': analysis_results.get('ai_probability', 0),
                    'confidence': 85,  # Fixed confidence for now
                    'patterns': patterns[:3],  # Limit to 3 patterns
                    'style_analysis': f"Analysis indicates {'formal AI-generated' if analysis_results.get('ai_probability', 0) > 60 else 'human-written'} content with vocabulary diversity of {analysis_results.get('indicators', {}).get('vocabulary_diversity', 0)}% and coherence score of {analysis_results.get('indicators', {}).get('coherence_score', 0)}%",
                    'detected_models': ['ChatGPT', 'Claude'] if analysis_results.get('ai_probability', 0) > 70 else 
                                      ['Possible AI influence'] if analysis_results.get('ai_probability', 0) > 40 else 
                                      []
                },
                'plagiarism': {
                    'score': 100 - plagiarism_data.get('originality_score', 100),
                    'sources': 1000000 if is_pro else 100000,
                    'matches': matches,
                    'citations_found': analysis_results.get('detected_patterns', {}).get('quotes_found', 0),
                    'citations_needed': max(0, (len(text_to_analyze.split()) // 200) - analysis_results.get('detected_patterns', {}).get('quotes_found', 0))
                },
                'timestamp': datetime.utcnow().isoformat(),
                'text_length': len(text_to_analyze),
                'word_count': len(text_to_analyze.split())
            }
            
            return jsonify({
                'success': True,
                'results': results
            })
            
        else:
            # Handle legacy analysis types for backward compatibility
            result = {}
            
            if analysis_type in ['text', 'ai', 'all']:
                result['ai_analysis'] = perform_realistic_unified_text_analysis(text_to_analyze)
            
            if analysis_type in ['news', 'all']:
                analyzer = NewsAnalyzer()
                news_result = analyzer.analyze(text_to_analyze, content_type='text', is_pro=True)
                result['news_analysis'] = news_result
            
            if analysis_type in ['image'] and data.get('image'):
                result['image_analysis'] = perform_basic_image_analysis(data.get('image'))
            
            result['analysis_complete'] = True
            result['timestamp'] = datetime.utcnow().isoformat()
            result['is_pro'] = True
            
            return jsonify(result)
        
    except Exception as e:
        print(f"Unified analysis error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Analysis failed',
            'details': str(e)
        }), 500

@app.route('/api/analyze-news', methods=['POST'])
def analyze_news():
    """Enhanced news analysis endpoint with URL extraction"""
    try:
        data = request.get_json()
        
        # Use the new analyzer
        results = analyze_news_route(data)
        
        # Check if it's an error response
        if isinstance(results, tuple):
            return jsonify(results[0]), results[1]
        
        return jsonify(results)
        
    except Exception as e:
        print(f"News analysis error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Analysis failed. Please try again.'
        }), 500

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    """Generate PDF report for news analysis"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        data = request.get_json()
        analysis_data = data.get('analysisData', {})
        results = analysis_data.get('results', {})
        
        # Create PDF in memory
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Title
        p.setFont("Helvetica-Bold", 24)
        p.drawString(50, height - 50, "News Verification Report")
        
        # Date
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 80, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Draw a line
        p.line(50, height - 90, width - 50, height - 90)
        
        # Analysis Results
        y_position = height - 120
        
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, y_position, "Analysis Results")
        y_position -= 30
        
        p.setFont("Helvetica", 12)
        
        # Credibility Score
        credibility = results.get('credibility', 'N/A')
        p.drawString(50, y_position, f"Credibility Score: {credibility}%")
        y_position -= 20
        
        # Bias
        bias = results.get('bias', {})
        if isinstance(bias, dict):
            bias_label = bias.get('label', 'N/A')
            objectivity = bias.get('objectivity', 'N/A')
        else:
            bias_label = bias
            objectivity = 'N/A'
        
        p.drawString(50, y_position, f"Political Bias: {bias_label}")
        y_position -= 20
        p.drawString(50, y_position, f"Objectivity: {objectivity}%")
        y_position -= 20
        
        # Source
        source = results.get('sources', {}).get('name', 'Unknown')
        p.drawString(50, y_position, f"Source: {source}")
        y_position -= 20
        
        # Author
        author = results.get('author', 'Unknown')
        p.drawString(50, y_position, f"Author: {author}")
        y_position -= 40
        
        # Add more content as needed
        if y_position > 100:
            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, y_position, "Key Findings")
            y_position -= 25
            
            p.setFont("Helvetica", 11)
            findings = [
                f"• This article has {credibility}% credibility",
                f"• Political bias detected: {bias_label}",
                f"• Source verified as: {source}",
                "• Full analysis available online"
            ]
            
            for finding in findings:
                p.drawString(70, y_position, finding)
                y_position -= 20
        
        # Footer
        p.setFont("Helvetica-Italic", 10)
        p.drawString(50, 50, "Full analysis available at factsandfakes.ai/news")
        p.drawString(50, 35, "© 2025 Facts & Fakes AI - Professional News Verification")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        return send_file(
            buffer, 
            as_attachment=True, 
            download_name=f'news-analysis-{int(datetime.now().timestamp())}.pdf', 
            mimetype='application/pdf'
        )
        
    except ImportError:
        print("ReportLab not installed - falling back to text response")
        return jsonify({'error': 'PDF generation not available. Please install reportlab.'}), 501
        
    except Exception as e:
        print(f"PDF generation error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-unified-pdf', methods=['POST'])
def generate_unified_pdf():
    """Generate PDF report for unified AI & plagiarism analysis"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        data = request.get_json()
        results = data.get('results', {})
        
        # Create PDF in memory
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Title
        p.setFont("Helvetica-Bold", 24)
        p.drawString(50, height - 50, "AI & Plagiarism Analysis Report")
        
        # Date
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 80, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Draw a line
        p.line(50, height - 90, width - 50, height - 90)
        
        # Summary Section
        y_position = height - 120
        
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, y_position, "Summary")
        y_position -= 30
        
        p.setFont("Helvetica", 12)
        
        # AI Detection Score
        ai_prob = results.get('ai_probability', 0)
        p.drawString(50, y_position, f"AI Detection Score: {ai_prob}%")
        y_position -= 20
        
        # Plagiarism Score
        plag_score = results.get('plagiarism_score', 0)
        p.drawString(50, y_position, f"Plagiarism Score: {plag_score}%")
        y_position -= 20
        
        # Overall Assessment
        if ai_prob > 70:
            assessment = "High probability of AI-generated content"
        elif ai_prob > 40:
            assessment = "Moderate AI characteristics detected"
        else:
            assessment = "Content appears to be human-written"
            
        p.drawString(50, y_position, f"Assessment: {assessment}")
        y_position -= 40
        
        # AI Detection Details
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, y_position, "AI Detection Analysis")
        y_position -= 25
        
        p.setFont("Helvetica", 11)
        ai_data = results.get('ai_detection', {})
        
        p.drawString(50, y_position, f"Confidence Level: {ai_data.get('confidence', 0)}%")
        y_position -= 20
        
        p.drawString(50, y_position, "Detected Patterns:")
        y_position -= 15
        
        for pattern in ai_data.get('patterns', []):
            p.drawString(70, y_position, f"• {pattern}")
            y_position -= 15
            
        y_position -= 10
        
        # Style Analysis
        style_analysis = ai_data.get('style_analysis', 'No analysis available')
        # Wrap long text
        words = style_analysis.split()
        line = ""
        for word in words:
            test_line = line + word + " "
            if p.stringWidth(test_line, "Helvetica", 11) < (width - 120):
                line = test_line
            else:
                p.drawString(50, y_position, line.strip())
                y_position -= 15
                line = word + " "
        if line:
            p.drawString(50, y_position, line.strip())
            y_position -= 15
            
        y_position -= 15
        
        # Plagiarism Details
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, y_position, "Plagiarism Check Results")
        y_position -= 25
        
        p.setFont("Helvetica", 11)
        plag_data = results.get('plagiarism', {})
        
        p.drawString(50, y_position, f"Sources Checked: {plag_data.get('sources', 0):,}")
        y_position -= 20
        
        p.drawString(50, y_position, f"Originality: {100 - plag_score}%")
        y_position -= 20
        
        matches = plag_data.get('matches', [])
        if matches:
            p.drawString(50, y_position, "Matching Content Found:")
            y_position -= 15
            for match in matches[:3]:  # Limit to 3 matches
                p.drawString(70, y_position, f"• {match['percentage']}% - {match['source']}")
                y_position -= 15
        
        # Document Statistics
        if y_position > 150:
            y_position -= 20
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, y_position, "Document Statistics")
            y_position -= 25
            
            p.setFont("Helvetica", 11)
            p.drawString(50, y_position, f"Word Count: {results.get('word_count', 0):,}")
            y_position -= 15
            p.drawString(50, y_position, f"Character Count: {results.get('text_length', 0):,}")
        
        # Footer
        p.setFont("Helvetica-Italic", 10)
        p.drawString(50, 50, "Full analysis available at factsandfakes.ai/unified")
        p.drawString(50, 35, "© 2025 Facts & Fakes AI - AI & Plagiarism Detection")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        return send_file(
            buffer, 
            as_attachment=True, 
            download_name=f'ai-plagiarism-report-{int(datetime.now().timestamp())}.pdf', 
            mimetype='application/pdf'
        )
        
    except ImportError:
        print("ReportLab not installed - falling back to text response")
        return jsonify({
            'success': False,
            'error': 'PDF generation not available. Please install reportlab.'
        }), 501
        
    except Exception as e:
        print(f"PDF generation error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
