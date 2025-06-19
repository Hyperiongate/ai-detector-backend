from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import time
import os
from datetime import datetime
import sqlite3
import json
import requests
import io
import base64

app = Flask(__name__)
CORS(app)

print("Starting AI Detection Server (Document Upload + Conversational Analysis)...")

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
            file_metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_content_hash(content):
    return hashlib.md5(content.encode()).hexdigest()

def extract_text_from_pdf(file_content):
    """Extract text from PDF using PyPDF2"""
    try:
        import PyPDF2
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except ImportError:
        return "PDF processing library not available. Please install PyPDF2."
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"

def extract_text_from_docx(file_content):
    """Extract text from Word document using python-docx"""
    try:
        import docx
        doc_file = io.BytesIO(file_content)
        doc = docx.Document(doc_file)
        
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text.strip()
    except ImportError:
        return "Word document processing library not available. Please install python-docx."
    except Exception as e:
        return f"Error extracting Word document text: {str(e)}"

def process_uploaded_file(file_content, filename, file_type):
    """Process uploaded file and extract text"""
    
    file_size = len(file_content)
    
    # File size limit (5MB)
    if file_size > 5 * 1024 * 1024:
        return None, {"error": "File too large. Maximum size is 5MB."}
    
    # Extract text based on file type
    extracted_text = ""
    
    if file_type == 'application/pdf' or filename.lower().endswith('.pdf'):
        extracted_text = extract_text_from_pdf(file_content)
    elif file_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'] or filename.lower().endswith(('.docx', '.doc')):
        extracted_text = extract_text_from_docx(file_content)
    elif file_type == 'text/plain' or filename.lower().endswith('.txt'):
        try:
            extracted_text = file_content.decode('utf-8')
        except:
            try:
                extracted_text = file_content.decode('latin-1')
            except:
                extracted_text = "Error: Could not decode text file."
    else:
        return None, {"error": f"Unsupported file type: {file_type}. Supported types: PDF, Word (.docx, .doc), Plain text (.txt)"}
    
    if not extracted_text or len(extracted_text.strip()) < 100:
        return None, {"error": "Could not extract sufficient text from file. Minimum 100 characters required."}
    
    # File metadata
    metadata = {
        "filename": filename,
        "file_type": file_type,
        "file_size": file_size,
        "word_count": len(extracted_text.split()),
        "character_count": len(extracted_text),
        "extracted_length": len(extracted_text)
    }
    
    return extracted_text, metadata

def direct_openai_call(prompt):
    """Call OpenAI API directly using requests to avoid client library issues"""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("No OpenAI API key found")
        return None
    
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-4o-mini',
            'messages': [
                {'role': 'system', 'content': 'You are an expert AI detection analyst who provides detailed, conversational explanations. Be thorough but accessible.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.2,
            'max_tokens': 800
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"OpenAI API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"OpenAI API request failed: {e}")
        return None

def openai_ai_detection(text):
    """Conversational OpenAI-powered AI detection"""
    
    # Enhanced conversational prompt for detailed analysis
    prompt = f"""You are an expert AI detection analyst. Analyze this text to determine if it was written by AI or a human, then provide a conversational, detailed explanation.

Text to analyze:
"{text}"

Please provide your analysis in this JSON format:
{{
  "confidence_score": [number from 0-100 where 0=definitely human, 100=definitely AI],
  "conversational_explanation": "[A detailed, conversational explanation in 2-3 paragraphs that: 1) States your confidence level in plain English, 2) Explains the specific indicators you found with examples from the text, 3) Provides context about why these patterns suggest AI or human authorship. Write like you're explaining to an intelligent person who wants to understand your reasoning.]",
  "key_indicators": ["3-5 specific examples from the text that influenced your decision"],
  "writing_style_notes": "[Brief assessment of the writing style - is it academic, casual, business, creative, etc.]",
  "human_elements": ["Any human-like characteristics you found"],
  "ai_elements": ["Any AI-like characteristics you found"]
}}

Be specific, cite actual phrases from the text, and explain your reasoning clearly. Make it educational and conversational.
"""

    result = direct_openai_call(prompt)
    
    if not result:
        print("OpenAI API call failed, using fallback")
        return fallback_conversational_analysis(text)
    
    try:
        # Extract the response
        analysis_text = result['choices'][0]['message']['content'].strip()
        print(f"OpenAI response: {analysis_text}")
        
        # Try to extract JSON from the response
        try:
            # Clean up the response text
            if analysis_text.startswith('```json'):
                analysis_text = analysis_text.replace('```json', '').replace('```', '')
            
            # Try to parse as JSON
            analysis_data = json.loads(analysis_text)
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"JSON parsing failed: {e}")
            # Fallback: try to extract confidence score and create conversational response
            import re
            confidence_match = re.search(r'"?confidence_score"?\s*:?\s*(\d+)', analysis_text)
            if confidence_match:
                confidence_score = int(confidence_match.group(1))
            else:
                confidence_score = 50
            
            # Create a conversational fallback
            analysis_data = {
                "confidence_score": confidence_score,
                "conversational_explanation": f"I'm {confidence_score}% confident about this analysis. The text shows characteristics that suggest {'AI generation' if confidence_score > 50 else 'human authorship'}, but I encountered some difficulty processing the detailed analysis. The writing style and patterns I can detect point toward this confidence level.",
                "key_indicators": ["Analysis completed with limited detail extraction"],
                "writing_style_notes": "Style analysis partially completed",
                "human_elements": [],
                "ai_elements": []
            }
        
        return {
            "confidence_score": analysis_data.get("confidence_score", 50),
            "conversational_explanation": analysis_data.get("conversational_explanation", "Analysis completed"),
            "key_indicators": analysis_data.get("key_indicators", []),
            "writing_style_notes": analysis_data.get("writing_style_notes", ""),
            "human_elements": analysis_data.get("human_elements", []),
            "ai_elements": analysis_data.get("ai_elements", []),
            "method": "OpenAI GPT-4o-mini Document Analysis",
            "tokens_used": result['usage']['total_tokens'] if 'usage' in result else 0
        }
        
    except Exception as e:
        print(f"OpenAI response processing error: {e}")
        return fallback_conversational_analysis(text)

def fallback_conversational_analysis(text):
    """Conversational fallback analysis if OpenAI API fails"""
    print("Using fallback conversational analysis")
    words = text.lower().split()
    sentences = text.split('.')
    
    ai_score = 0
    ai_indicators = []
    human_indicators = []
    
    # AI indicators with explanations
    ai_phrases = {
        'furthermore': 'formal transition word',
        'consequently': 'formal transition word', 
        'additionally': 'formal transition word',
        'moreover': 'formal transition word',
        'implementation': 'business jargon',
        'optimization': 'technical terminology',
        'systematic': 'formal descriptor',
        'comprehensive': 'corporate language',
        'facilitate': 'business terminology',
        'utilize': 'formal alternative to "use"'
    }
    
    # Check for AI indicators
    for phrase, explanation in ai_phrases.items():
        if phrase in text.lower():
            ai_score += 15
            ai_indicators.append(f"'{phrase}' - {explanation}")
    
    # Check for human indicators
    personal_markers = ['i think', 'i feel', 'honestly', 'in my opinion', 'i believe']
    for marker in personal_markers:
        if marker in text.lower():
            ai_score -= 20
            human_indicators.append(f"Personal expression: '{marker}'")
    
    # Sentence structure
    avg_length = len(words) / max(len(sentences), 1)
    if avg_length > 20:
        ai_score += 20
        ai_indicators.append(f"Very long sentences (avg {avg_length:.1f} words)")
    
    confidence = min(95, max(5, ai_score))
    
    # Create conversational explanation
    if confidence >= 70:
        explanation = f"I'm {confidence:.0f}% confident this text was generated by AI. The writing shows several telltale signs of artificial generation, including formal language patterns and structured presentation that AI models tend to produce. "
    elif confidence >= 30:
        explanation = f"This is a mixed case - I'm {confidence:.0f}% confident it might be AI-generated. The text has some characteristics that could suggest AI, but also retains elements that feel more human. "
    else:
        explanation = f"I'm only {confidence:.0f}% confident this is AI-generated, which means it likely appears more human. The writing style and language patterns suggest human authorship. "
    
    if ai_indicators:
        explanation += f"Key AI indicators I found include: {', '.join(ai_indicators[:3])}. "
    if human_indicators:
        explanation += f"However, I also noticed human elements like: {', '.join(human_indicators)}. "
    
    explanation += "This analysis uses pattern recognition since the advanced AI analysis wasn't available."
    
    return {
        "confidence_score": round(confidence, 1),
        "conversational_explanation": explanation,
        "key_indicators": ai_indicators[:5] if ai_indicators else ["Pattern-based analysis completed"],
        "writing_style_notes": "Analyzed using fallback pattern recognition",
        "human_elements": human_indicators,
        "ai_elements": ai_indicators,
        "method": "Enhanced Conversational Pattern Analysis",
        "tokens_used": 0
    }

@app.route('/api/health', methods=['GET'])
def health_check():
    # Test OpenAI API connection with direct HTTP call
    api_key = os.getenv('OPENAI_API_KEY')
    api_status = "not_available"
    
    if not api_key:
        api_status = "no_api_key"
    else:
        try:
            # Quick test call
            test_result = direct_openai_call("Test connection")
            if test_result and 'choices' in test_result:
                api_status = "connected"
                print("OpenAI API test successful!")
            else:
                api_status = "connection_failed"
        except Exception as e:
            api_status = f"error: {str(e)[:50]}"
            print(f"OpenAI API test failed: {e}")
    
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'openai_api': api_status,
        'detection_method': 'OpenAI GPT-4o-mini Document Analysis',
        'supported_formats': ['PDF', 'Word (.docx, .doc)', 'Plain Text (.txt)'],
        'max_file_size': '5MB'
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
        
        # Use conversational OpenAI analysis
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
            'conversational_explanation': detection_result.get('conversational_explanation', ''),
            'key_indicators': detection_result.get('key_indicators', []),
            'writing_style_notes': detection_result.get('writing_style_notes', ''),
            'human_elements': detection_result.get('human_elements', []),
            'ai_elements': detection_result.get('ai_elements', []),
            'note': 'Advanced conversational AI analysis',
            'content_type': 'text'
        }
        
        # Store in database
        content_hash = get_content_hash(text)
        try:
            conn = sqlite3.connect('analyses.db')
            conn.execute('''
                INSERT OR REPLACE INTO analyses 
                (content_hash, content_type, confidence_score, verdict, analysis_details, file_metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (content_hash, 'text', confidence_score, f"{verdict_emoji} {verdict}", 
                  json.dumps(analysis_details), json.dumps({})))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database error: {e}")
        
        response = {
            'success': True,
            'confidence_score': round(confidence_score, 1),
            'verdict': f"{verdict_emoji} {verdict}",
            'analysis_details': analysis_details,
            'analysis_id': f'CONV-{get_content_hash(text)[:8]}',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in text analysis: {e}")
        return jsonify({
            'success': False,
            'error': 'Analysis failed. Please try again.'
        }), 500

@app.route('/api/analyze/document', methods=['POST'])
def analyze_document():
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Read file content
        file_content = file.read()
        filename = file.filename
        file_type = file.content_type
        
        print(f"Processing uploaded file: {filename} ({file_type})")
        
        # Process the uploaded file
        extracted_text, metadata = process_uploaded_file(file_content, filename, file_type)
        
        if extracted_text is None:
            return jsonify({'success': False, 'error': metadata['error']}), 400
        
        start_time = time.time()
        
        # Use conversational OpenAI analysis on extracted text
        detection_result = openai_ai_detection(extracted_text)
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
        
        # Analysis details with file metadata
        words = extracted_text.split()
        sentences = extracted_text.split('.')
        
        analysis_details = {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_words_per_sentence': round(len(words) / max(len(sentences), 1), 1),
            'processing_time_ms': round(processing_time * 1000, 2),
            'method': detection_result['method'],
            'verdict_emoji': verdict_emoji,
            'tokens_used': detection_result.get('tokens_used', 0),
            'conversational_explanation': detection_result.get('conversational_explanation', ''),
            'key_indicators': detection_result.get('key_indicators', []),
            'writing_style_notes': detection_result.get('writing_style_notes', ''),
            'human_elements': detection_result.get('human_elements', []),
            'ai_elements': detection_result.get('ai_elements', []),
            'note': 'Document analysis with text extraction',
            'content_type': 'document',
            'file_info': metadata
        }
        
        # Store in database
        content_hash = get_content_hash(extracted_text)
        try:
            conn = sqlite3.connect('analyses.db')
            conn.execute('''
                INSERT OR REPLACE INTO analyses 
                (content_hash, content_type, confidence_score, verdict, analysis_details, file_metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (content_hash, 'document', confidence_score, f"{verdict_emoji} {verdict}", 
                  json.dumps(analysis_details), json.dumps(metadata)))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database error: {e}")
        
        response = {
            'success': True,
            'confidence_score': round(confidence_score, 1),
            'verdict': f"{verdict_emoji} {verdict}",
            'analysis_details': analysis_details,
            'file_metadata': metadata,
            'analysis_id': f'DOC-{get_content_hash(extracted_text)[:8]}',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in document analysis: {e}")
        return jsonify({
            'success': False,
            'error': 'Document analysis failed. Please try again.'
        }), 500

@app.route('/api/analyze/image', methods=['POST'])
def analyze_image():
    return jsonify({
        'success': False,
        'error': 'Image detection coming soon! Currently PDF, Word, and text analysis are available.'
    }), 501

@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = sqlite3.connect('analyses.db')
    cursor = conn.execute('SELECT COUNT(*), AVG(confidence_score), COUNT(CASE WHEN content_type = "document" THEN 1 END) FROM analyses')
    result = cursor.fetchone()
    conn.close()
    
    return jsonify({
        'total_analyses': result[0] if result else 0,
        'average_confidence': round(result[1], 1) if result and result[1] else 0,
        'document_analyses': result[2] if result else 0,
        'detection_method': 'OpenAI GPT-4o-mini Document Analysis',
        'api_status': 'active'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
