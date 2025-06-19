from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import time
import os
from datetime import datetime
import sqlite3
import json

app = Flask(__name__)
CORS(app)

print("Starting AI Detection Server (Enhanced Pattern Analysis)...")

# Initialize database
def init_db():
    conn = sqlite3.connect('analyses.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_hash TEXT UNIQUE,
            content_type TEXT,
            confidence_score REAL,
            verdict TEXT,
            analysis_details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_content_hash(content):
    return hashlib.md5(content.encode()).hexdigest()

def enhanced_pattern_analysis(text):
    """Enhanced pattern-based AI detection"""
    words = text.lower().split()
    sentences = text.split('.')
    
    ai_indicators = 0
    total_checks = 0
    
    # AI-typical phrases
    ai_phrases = [
        'furthermore', 'consequently', 'additionally', 'moreover',
        'implementation', 'optimization', 'systematic', 'comprehensive',
        'paradigm', 'methodology', 'facilitate', 'utilize',
        'seamlessly', 'efficiently', 'effectively', 'significantly',
        'innovative', 'revolutionary', 'transformative', 'cutting-edge',
        'streamline', 'optimize', 'maximize', 'enhance', 'elevate'
    ]
    
    for phrase in ai_phrases:
        if phrase in text.lower():
            ai_indicators += 2
        total_checks += 1
    
    # Sentence structure analysis
    avg_sentence_length = len(words) / max(len(sentences), 1)
    if avg_sentence_length > 20:  # Very long sentences
        ai_indicators += 1
    total_checks += 1
    
    # Vocabulary diversity
    unique_words = set(words)
    diversity = len(unique_words) / len(words) if words else 0
    if diversity < 0.6:  # Low diversity suggests AI
        ai_indicators += 1
    total_checks += 1
    
    # Repetitive patterns
    repetitive_starters = ['the implementation', 'it is important', 'furthermore', 'in conclusion']
    for starter in repetitive_starters:
        if starter in text.lower():
            ai_indicators += 1
        total_checks += 1
    
    # Personal markers (reduce AI score)
    personal_markers = ['i think', 'i feel', 'in my opinion', 'personally', 'i believe']
    personal_count = 0
    for marker in personal_markers:
        if marker in text.lower():
            personal_count += 1
    
    # Adjust score based on personal markers
    if personal_count > 0:
        ai_indicators -= personal_count
    
    # Calculate confidence
    confidence = (ai_indicators / max(total_checks, 1)) * 100
    confidence = min(95, max(5, confidence))  # Keep between 5-95%
    
    return confidence

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/analyze/text', methods=['POST'])
def analyze_text():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'success': False, 'error': 'No text provided'}), 400
        
        text = data['text'].strip()
        if len(text) < 100:
            return jsonify({
                'success': False, 
                'error': 'Text must be at least 100 characters for accurate analysis'
            }), 400
        
        start_time = time.time()
        
        # Enhanced pattern-based detection
        confidence_score = enhanced_pattern_analysis(text)
        
        processing_time = time.time() - start_time
        
        # Determine verdict
        if confidence_score >= 75:
            verdict = "High AI Probability"
            verdict_emoji = "🤖"
        elif confidence_score >= 50:
            verdict = "Mixed Signals"
            verdict_emoji = "🤔"
        elif confidence_score >= 25:
            verdict = "Likely Human with AI Elements"
            verdict_emoji = "📝"
        else:
            verdict = "Likely Human Content"
            verdict_emoji = "✅"
        
        # Analysis details
        words = text.split()
        sentences = text.split('.')
        
        analysis_details = {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_words_per_sentence': round(len(words) / max(len(sentences), 1), 1),
            'processing_time_ms': round(processing_time * 1000, 2),
            'method': 'Enhanced Pattern Analysis v2.0',
            'verdict_emoji': verdict_emoji,
            'note': 'Real pattern-based detection - much more accurate than random!'
        }
        
        response = {
            'success': True,
            'confidence_score': round(confidence_score, 1),
            'verdict': f"{verdict_emoji} {verdict}",
            'analysis_details': analysis_details,
            'analysis_id': f'FA-{get_content_hash(text)[:8]}',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in text analysis: {e}")
        return jsonify({
            'success': False,
            'error': 'Analysis failed. Please try again.'
        }), 500

@app.route('/api/analyze/image', methods=['POST'])
def analyze_image():
    return jsonify({
        'success': False,
        'error': 'Image detection coming soon! Currently only text analysis is available.'
    }), 501

@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = sqlite3.connect('analyses.db')
    cursor = conn.execute('SELECT COUNT(*), AVG(confidence_score) FROM analyses')
    result = cursor.fetchone()
    conn.close()
    
    return jsonify({
        'total_analyses': result[0] if result else 0,
        'average_confidence': round(result[1], 1) if result and result[1] else 0
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)