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

print("Starting AI Detection Server (OpenAI-Powered Analysis)...")

# DEBUG: Print all environment variables related to OpenAI
print("DEBUG: Checking environment variables...")
api_key_value = os.getenv('OPENAI_API_KEY')
print(f"DEBUG: OPENAI_API_KEY exists: {api_key_value is not None}")
if api_key_value:
    print(f"DEBUG: API key starts with: {api_key_value[:10]}...")
    print(f"DEBUG: API key length: {len(api_key_value)}")
else:
    print("DEBUG: OPENAI_API_KEY is None or empty")
    print("DEBUG: Available environment variables:")
    for key in os.environ.keys():
        if 'OPENAI' in key.upper() or 'API' in key.upper():
            print(f"DEBUG: Found env var: {key}")

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

def get_openai_client():
    """Initialize OpenAI client safely"""
    try:
        import openai
        api_key = os.getenv('OPENAI_API_KEY')
        print(f"DEBUG: In get_openai_client, api_key exists: {api_key is not None}")
        
        if not api_key:
            print("DEBUG: No OpenAI API key found in get_openai_client")
            return None
        
        if len(api_key.strip()) == 0:
            print("DEBUG: OpenAI API key is empty string")
            return None
            
        print(f"DEBUG: API key first 10 chars: {api_key[:10]}")
        
        # Initialize client with minimal parameters to avoid compatibility issues
        client = openai.OpenAI(api_key=api_key.strip())
        print("DEBUG: OpenAI client created successfully")
        return client
    except Exception as e:
        print(f"DEBUG: Failed to initialize OpenAI client: {e}")
        return None

def openai_ai_detection(text):
    """Real OpenAI-powered AI detection with high accuracy"""
    client = get_openai_client()
    
    if not client:
        print("DEBUG: OpenAI client not available, using fallback")
        return fallback_pattern_analysis(text)
    
    try:
        print("DEBUG: Attempting OpenAI API call...")
        # Craft a sophisticated prompt for AI detection
        prompt = f"""You are an expert AI detection system. Analyze the following text and determine if it was written by AI or a human.

Consider these factors:
1. Writing style and flow
2. Vocabulary patterns and word choice
3. Sentence structure consistency
4. Personal voice and authenticity
5. Error patterns (humans make small mistakes, AI tends to be too perfect)
6. Emotional expression and subjectivity
7. Conversational markers and informalities
8. Knowledge presentation style

Text to analyze:
"{text}"

Respond with ONLY a JSON object containing:
{{"confidence_score": [number from 0-100], "reasoning": "[brief explanation]", "indicators": ["specific indicator 1", "specific indicator 2"], "human_markers": ["human trait 1"], "ai_markers": ["ai trait 1"]}}

Be precise and analytical. 0 = definitely human, 100 = definitely AI."""

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Most cost-effective while maintaining high accuracy
            messages=[
                {"role": "system", "content": "You are an expert AI detection system. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Low temperature for consistent results
            max_tokens=500
        )
        
        print("DEBUG: OpenAI API call successful!")
        
        # Parse the response
        analysis_text = response.choices[0].message.content.strip()
        print(f"DEBUG: OpenAI response: {analysis_text}")
        
        # Try to extract JSON from the response
        try:
            # Clean up the response text
            if analysis_text.startswith('```json'):
                analysis_text = analysis_text.replace('```json', '').replace('```', '')
            
            # Try to parse as JSON
            analysis_data = json.loads(analysis_text)
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"DEBUG: JSON parsing failed: {e}")
            # Fallback: extract confidence score manually
            import re
            confidence_match = re.search(r'"confidence_score":\s*(\d+)', analysis_text)
            if confidence_match:
                confidence_score = int(confidence_match.group(1))
            else:
                confidence_score = 50  # Default if parsing fails
            
            analysis_data = {
                "confidence_score": confidence_score,
                "reasoning": "OpenAI analysis completed (parsing fallback)",
                "indicators": ["OpenAI GPT-4o-mini analysis"],
                "human_markers": [],
                "ai_markers": []
            }
        
        return {
            "confidence_score": analysis_data.get("confidence_score", 50),
            "reasoning": analysis_data.get("reasoning", "Analysis completed"),
            "indicators": analysis_data.get("indicators", []),
            "human_markers": analysis_data.get("human_markers", []),
            "ai_markers": analysis_data.get("ai_markers", []),
            "method": "OpenAI GPT-4o-mini Detection",
            "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0
        }
        
    except Exception as e:
        print(f"DEBUG: OpenAI API Error: {e}")
        # Fallback to enhanced pattern analysis if OpenAI fails
        return fallback_pattern_analysis(text)

def fallback_pattern_analysis(text):
    """Enhanced fallback pattern analysis if OpenAI API fails"""
    print("DEBUG: Using fallback pattern analysis")
    words = text.lower().split()
    sentences = text.split('.')
    
    ai_score = 0
    
    # Strong AI indicators (more aggressive detection)
    ai_phrases = [
        'furthermore', 'consequently', 'additionally', 'moreover',
        'implementation', 'optimization', 'systematic', 'comprehensive',
        'paradigm', 'methodology', 'facilitate', 'utilize',
        'seamlessly', 'efficiently', 'effectively', 'significantly',
        'innovative', 'revolutionary', 'transformative', 'cutting-edge',
        'streamline', 'optimize', 'maximize', 'enhance', 'elevate',
        'robust', 'scalable', 'versatile', 'dynamic', 'strategic'
    ]
    
    # Count AI indicators
    for phrase in ai_phrases:
        if phrase in text.lower():
            ai_score += 15
    
    # Sentence structure analysis
    avg_sentence_length = len(words) / max(len(sentences), 1)
    if avg_sentence_length > 20:  # Very long sentences
        ai_score += 20
    
    # Repetitive patterns
    repetitive_starters = [
        'the implementation', 'it is important', 'furthermore', 'in conclusion',
        'additionally', 'moreover', 'consequently', 'in summary'
    ]
    for starter in repetitive_starters:
        if starter in text.lower():
            ai_score += 25
    
    # Personal markers (reduce AI score)
    personal_markers = [
        'i think', 'i feel', 'in my opinion', 'personally', 'i believe',
        'honestly', 'my experience', 'i remember', 'i noticed'
    ]
    personal_count = 0
    for marker in personal_markers:
        if marker in text.lower():
            personal_count += 1
    
    # Reduce score for human markers
    ai_score -= personal_count * 20
    
    # Calculate final confidence
    confidence = min(95, max(5, ai_score))
    
    return {
        "confidence_score": round(confidence, 1),
        "reasoning": "Fallback pattern analysis - OpenAI API unavailable",
        "indicators": [f"Pattern analysis: {ai_score} AI indicators"],
        "human_markers": [f"{personal_count} personal markers found"],
        "ai_markers": [f"AI phrases and formal language detected"],
        "method": "Enhanced Pattern Analysis (Fallback)",
        "tokens_used": 0
    }

@app.route('/api/health', methods=['GET'])
def health_check():
    # Test OpenAI API connection
    client = get_openai_client()
    api_status = "not_available"
    debug_info = {}
    
    # Add debug information
    api_key_value = os.getenv('OPENAI_API_KEY')
    debug_info['api_key_exists'] = api_key_value is not None
    debug_info['api_key_length'] = len(api_key_value) if api_key_value else 0
    debug_info['api_key_starts_with'] = api_key_value[:10] if api_key_value else "N/A"
    
    if client:
        try:
            # Quick test call
            print("DEBUG: Testing OpenAI API connection...")
            test_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=1
            )
            api_status = "connected"
            print("DEBUG: OpenAI API test successful!")
        except Exception as e:
            api_status = f"error: {str(e)[:50]}"
            print(f"DEBUG: OpenAI API test failed: {e}")
    else:
        api_status = "no_api_key"
        print("DEBUG: No OpenAI client available")
    
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'openai_api': api_status,
        'detection_method': 'OpenAI GPT-4o-mini with Fallback',
        'debug': debug_info
    })

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
        
        # Use OpenAI for AI detection (with fallback)
        detection_result = openai_ai_detection(text)
        confidence_score = detection_result['confidence_score']
        
        processing_time = time.time() - start_time
        
        # Determine verdict with emojis
        if confidence_score >= 80:
            verdict = "High AI Probability"
            verdict_emoji = "🤖"
        elif confidence_score >= 60:
            verdict = "Likely AI Generated"
            verdict_emoji = "🔴"
        elif confidence_score >= 40:
            verdict = "Mixed Signals"
            verdict_emoji = "🤔"
        elif confidence_score >= 20:
            verdict = "Likely Human"
            verdict_emoji = "📝"
        else:
            verdict = "High Human Probability"
            verdict_emoji = "✅"
        
        # Analysis details
        words = text.split()
        sentences = text.split('.')
        
        analysis_details = {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_words_per_sentence': round(len(words) / max(len(sentences), 1), 1),
            'processing_time_ms': round(processing_time * 1000, 2),
            'method': detection_result['method'],
            'verdict_emoji': verdict_emoji,
            'tokens_used': detection_result.get('tokens_used', 0),
            'reasoning': detection_result.get('reasoning', ''),
            'ai_markers': detection_result.get('ai_markers', []),
            'human_markers': detection_result.get('human_markers', []),
            'note': 'Real OpenAI-powered detection with pattern fallback'
        }
        
        # Store in database
        content_hash = get_content_hash(text)
        try:
            conn = sqlite3.connect('analyses.db')
            conn.execute('''
                INSERT OR REPLACE INTO analyses 
                (content_hash, content_type, confidence_score, verdict, analysis_details)
                VALUES (?, ?, ?, ?, ?)
            ''', (content_hash, 'text', confidence_score, f"{verdict_emoji} {verdict}", 
                  json.dumps(analysis_details)))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database error: {e}")
        
        response = {
            'success': True,
            'confidence_score': round(confidence_score, 1),
            'verdict': f"{verdict_emoji} {verdict}",
            'analysis_details': analysis_details,
            'analysis_id': f'OAI-{get_content_hash(text)[:8]}',
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
        'average_confidence': round(result[1], 1) if result and result[1] else 0,
        'detection_method': 'OpenAI GPT-4o-mini with Enhanced Fallback',
        'api_status': 'active'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
