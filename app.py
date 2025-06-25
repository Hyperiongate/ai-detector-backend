from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import openai
import requests
import re
import base64
import os
from datetime import datetime
import json
from werkzeug.utils import secure_filename
import PyPDF2
from docx import Document
import io
import time
import urllib.parse
from difflib import SequenceMatcher

app = Flask(__name__)
CORS(app)

# API Keys - with better error handling
openai.api_key = os.environ.get('OPENAI_API_KEY')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
GOOGLE_FACT_CHECK_API_KEY = os.environ.get('GOOGLE_FACT_CHECK_API_KEY')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
GOOGLE_SEARCH_ENGINE_ID = os.environ.get('GOOGLE_SEARCH_ENGINE_ID')

 
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')
@app.route('/unified_content_check', methods=['POST'])
def unified_content_check_frontend():
    """Enhanced unified content analysis with better error handling"""
    try:
        data = request.json
        content = data.get('text', '') or data.get('content', '')
        analysis_type = data.get('analysis_type', 'free')
        
        if not content:
            return jsonify({"error": "Content is required"}), 400
        
        print(f"Starting analysis for {len(content)} characters, type: {analysis_type}")
        
        # Stage 1: AI Analysis with error handling
        ai_detection_result = perform_safe_ai_analysis(content, analysis_type)
        
        # Stage 2: Plagiarism Detection with error handling
        if analysis_type == 'pro':
            plagiarism_results = perform_safe_plagiarism_scan(content, 'pro')
        else:
            plagiarism_results = perform_safe_plagiarism_scan(content, 'free')
        
        # Stage 3: Overall Assessment
        ai_probability = ai_detection_result.get('ai_probability', 0.5) * 100
        similarity_score = plagiarism_results.get('similarity_score', 0.1) * 100
        overall_score = 100 - ((ai_probability + similarity_score) / 2)
        
        if overall_score >= 80:
            overall_assessment = "Content appears authentic with high confidence"
        elif overall_score >= 60:
            overall_assessment = "Content shows mixed signals - further verification recommended"
        elif overall_score >= 40:
            overall_assessment = "Content raises authenticity concerns - human review suggested"
        else:
            overall_assessment = "Content shows significant red flags for authenticity"
        
        return jsonify({
            "ai_detection": ai_detection_result,
            "plagiarism_detection": plagiarism_results,
            "overall_assessment": overall_assessment,
            "analysis_tier": analysis_type,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        })
        
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        return jsonify({
            "error": f"Analysis failed: {str(e)}",
            "ai_detection": create_fallback_ai_detection(content),
            "plagiarism_detection": create_fallback_plagiarism_result(),
            "overall_assessment": "Analysis completed in demo mode",
            "status": "demo_mode"
        }), 200

def perform_safe_ai_analysis(content, analysis_type):
    """AI analysis with comprehensive error handling"""
    try:
        if not openai.api_key:
            print("OpenAI API key not configured, using fallback")
            return create_fallback_ai_detection(content)
        
        # Enhanced AI analysis prompt
        ai_prompt = f"""
        Analyze this text for AI generation indicators. Look for:
        1. Repetitive phrases and transition words
        2. Overly formal or robotic language
        3. Generic business/academic jargon
        4. Perfect grammar without natural errors
        5. Predictable sentence structures
        
        Text: {content[:1500]}
        
        Provide:
        - AI probability (0-100%)
        - Classification (Human-Written, Possibly AI-Generated, or Likely AI-Generated)
        - Confidence level (0-100%)
        - Brief explanation of key indicators found
        """
        
        model = "gpt-4" if analysis_type == 'pro' and openai.api_key else "gpt-3.5-turbo"
        print(f"Using model: {model}")
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": ai_prompt}],
            max_tokens=800,
            temperature=0.3,
            timeout=30
        )
        
        analysis_text = response.choices[0].message.content
        ai_probability = extract_percentage(analysis_text, "ai", 30)
        confidence = extract_percentage(analysis_text, "confidence", 80)
        
        # Classification
        if ai_probability >= 70:
            classification = "Likely AI-Generated"
        elif ai_probability >= 40:
            classification = "Possibly AI-Generated"
        else:
            classification = "Likely Human-Written"
        
        return {
            "ai_probability": ai_probability / 100,
            "classification": classification,
            "confidence": confidence / 100,
            "explanation": analysis_text,
            "model_used": model,
            "status": "success"
        }
        
    except Exception as e:
        print(f"AI analysis error: {str(e)}")
        return create_fallback_ai_detection(content)

def perform_safe_plagiarism_scan(content, tier):
    """Plagiarism scanning with comprehensive error handling"""
    try:
        if tier == 'pro' and GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID:
            return perform_google_plagiarism_scan(content)
        elif NEWS_API_KEY:
            return perform_news_plagiarism_scan(content)
        else:
            return create_fallback_plagiarism_result()
            
    except Exception as e:
        print(f"Plagiarism scan error: {str(e)}")
        return create_fallback_plagiarism_result()

def perform_google_plagiarism_scan(content):
    """Google Custom Search plagiarism detection"""
    try:
        print("Starting Google Custom Search plagiarism scan...")
        
        matches = []
        max_similarity = 0.0
        search_phrases = extract_search_phrases(content)
        
        for i, phrase in enumerate(search_phrases[:3]):  # Limit to 3 searches
            print(f"Searching phrase {i+1}: {phrase[:50]}...")
            
            try:
                search_results = google_custom_search(phrase)
                
                for result in search_results:
                    similarity = calculate_text_similarity(content, result.get('snippet', ''))
                    
                    if similarity > 0.25:  # Lower threshold for testing
                        matches.append({
                            "title": result.get('title', 'Unknown Source'),
                            "similarity": similarity,
                            "source": result.get('displayLink', 'Unknown Domain'),
                            "url": result.get('link', '#'),
                            "snippet": result.get('snippet', '')[:100] + "..."
                        })
                        max_similarity = max(max_similarity, similarity)
                
                time.sleep(0.2)  # Rate limiting
                
            except Exception as search_error:
                print(f"Search error for phrase: {search_error}")
                continue
        
        # Remove duplicates and sort
        unique_matches = []
        seen_urls = set()
        
        for match in sorted(matches, key=lambda x: x['similarity'], reverse=True):
            if match['url'] not in seen_urls:
                unique_matches.append(match)
                seen_urls.add(match['url'])
                if len(unique_matches) >= 5:
                    break
        
        # Assessment
        if max_similarity >= 0.7:
            assessment = f"HIGH SIMILARITY - Found {len(unique_matches)} matches (up to {int(max_similarity * 100)}%)"
        elif max_similarity >= 0.4:
            assessment = f"MODERATE SIMILARITY - Found {len(unique_matches)} matches (up to {int(max_similarity * 100)}%)"
        elif len(unique_matches) > 0:
            assessment = f"LOW SIMILARITY - Found {len(unique_matches)} weak matches (up to {int(max_similarity * 100)}%)"
        else:
            assessment = "NO SIGNIFICANT MATCHES - Content appears original"
        
        print(f"Google scan complete: {len(unique_matches)} matches found")
        
        return {
            "similarity_score": max_similarity,
            "assessment": assessment,
            "matches": unique_matches,
            "sources_scanned": "Google Custom Search (500+ databases)",
            "scan_type": "google_custom_search",
            "phrases_searched": len(search_phrases)
        }
        
    except Exception as e:
        print(f"Google plagiarism scan error: {str(e)}")
        return create_fallback_plagiarism_result()

def perform_news_plagiarism_scan(content):
    """Basic news API plagiarism scan"""
    try:
        search_query = content[:80].replace('"', '').replace('\n', ' ')
        search_url = f"https://newsapi.org/v2/everything?q=\"{search_query}\"&apiKey={NEWS_API_KEY}&pageSize=3"
        
        response = requests.get(search_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            matches = []
            max_similarity = 0.0
            
            for article in articles:
                article_text = (article.get('title', '') + ' ' + article.get('description', '')).lower()
                similarity = calculate_basic_similarity(content.lower(), article_text)
                
                if similarity > 0.15:
                    matches.append({
                        "title": article.get("title", "News Article"),
                        "similarity": similarity,
                        "source": article.get("source", {}).get("name", "News Source"),
                        "url": article.get("url", "#")
                    })
                    max_similarity = max(max_similarity, similarity)
            
            return {
                "similarity_score": max_similarity,
                "assessment": f"Basic scan found {len(matches)} potential matches" if matches else "No matches in news databases",
                "matches": matches,
                "sources_scanned": "News databases",
                "scan_type": "news_api"
            }
    
    except Exception as e:
        print(f"News API error: {str(e)}")
        return create_fallback_plagiarism_result()
    
    return create_fallback_plagiarism_result()

def google_custom_search(query):
    """Google Custom Search with error handling"""
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': GOOGLE_API_KEY,
            'cx': GOOGLE_SEARCH_ENGINE_ID,
            'q': f'"{query[:100]}"',  # Limit query length
            'num': 3,
            'fields': 'items(title,link,snippet,displayLink)'
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('items', [])
        else:
            print(f"Google API error {response.status_code}: {response.text}")
            return []
            
    except Exception as e:
        print(f"Google search error: {str(e)}")
        return []

def extract_search_phrases(content):
    """Extract meaningful phrases for searching"""
    sentences = re.split(r'[.!?]+', content)
    phrases = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if 25 <= len(sentence) <= 150:
            cleaned = re.sub(r'\b(the|and|or|but|in|on|at|to|for|of|with|by|a|an)\b', '', sentence, flags=re.IGNORECASE)
            cleaned = re.sub(r'[^\w\s]', '', cleaned).strip()
            if len(cleaned) > 20:
                phrases.append(cleaned)
    
    # Also get word chunks
    words = content.split()
    for i in range(0, len(words) - 6, 4):
        phrase = ' '.join(words[i:i+6])
        if len(phrase) > 25:
            phrases.append(phrase)
    
    return phrases[:8]  # Limit phrases

def calculate_text_similarity(text1, text2):
    """Calculate similarity between texts"""
    if not text1 or not text2:
        return 0.0
    
    # Basic sequence similarity
    similarity = SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    # Word overlap similarity
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if len(words1) > 0 and len(words2) > 0:
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        jaccard = intersection / union if union > 0 else 0
        combined = (similarity * 0.6) + (jaccard * 0.4)
        return min(combined, 0.95)
    
    return similarity

def calculate_basic_similarity(text1, text2):
    """Basic similarity calculation"""
    words1 = set(text1.split())
    words2 = set(text2.split())
    if len(words1) == 0:
        return 0.0
    return len(words1.intersection(words2)) / len(words1)

def create_fallback_ai_detection(content):
    """Fallback AI detection when APIs fail"""
    # Pattern-based analysis
    ai_patterns = ['furthermore', 'moreover', 'consequently', 'therefore', 'additionally', 'comprehensive', 'innovative', 'optimization']
    content_lower = content.lower()
    
    pattern_count = sum(1 for pattern in ai_patterns if pattern in content_lower)
    
    # Simple heuristics
    sentences = len(re.split(r'[.!?]+', content))
    avg_sentence_length = len(content.split()) / max(sentences, 1)
    
    ai_probability = 0.2  # Base probability
    ai_probability += pattern_count * 0.08
    ai_probability += max(0, (avg_sentence_length - 15) * 0.02)
    
    ai_probability = min(ai_probability, 0.85)
    
    if ai_probability >= 0.6:
        classification = "Likely AI-Generated"
    elif ai_probability >= 0.35:
        classification = "Possibly AI-Generated"
    else:
        classification = "Likely Human-Written"
    
    return {
        "ai_probability": ai_probability,
        "classification": classification,
        "confidence": 0.7,
        "explanation": f"Demo mode analysis: Found {pattern_count} AI indicators, average sentence length: {avg_sentence_length:.1f} words.",
        "model_used": "pattern_analysis",
        "status": "fallback"
    }

def create_fallback_plagiarism_result():
    """Fallback plagiarism result when APIs fail"""
    return {
        "similarity_score": 0.05,
        "assessment": "Demo mode - limited plagiarism scanning available",
        "matches": [],
        "sources_scanned": "Demo mode",
        "scan_type": "fallback"
    }

def extract_percentage(text, keyword, default=50):
    """Extract percentage from text"""
    pattern = rf'{keyword}.*?(\d+)%|(\d+)%.*?{keyword}'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return int(match.group(1) or match.group(2))
    return default

# Keep existing endpoints for compatibility
@app.route('/analyze_news', methods=['POST'])
def analyze_news_frontend():
    return jsonify({"message": "News analysis endpoint working"}), 200

@app.route('/api/extract-text', methods=['POST'])
def extract_text():
    """File text extraction"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        filename = secure_filename(file.filename)
        file_extension = filename.lower().split('.')[-1] if '.' in filename else ''
        
        extracted_text = ""
        
        if file_extension == 'txt':
            file_content = file.read()
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    extracted_text = file_content.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
        
        elif file_extension == 'pdf':
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        extracted_text += page_text + "\n"
            except Exception as e:
                return jsonify({'error': f'PDF error: {str(e)}'}), 400
        
        elif file_extension == 'docx':
            try:
                doc = Document(io.BytesIO(file.read()))
                for paragraph in doc.paragraphs:
                    if paragraph.text.strip():
                        extracted_text += paragraph.text + "\n"
            except Exception as e:
                return jsonify({'error': f'DOCX error: {str(e)}'}), 400
        
        else:
            return jsonify({'error': f'Unsupported file type: {file_extension}'}), 400
        
        extracted_text = extracted_text.strip()
        
        if not extracted_text:
            return jsonify({'error': 'No text extracted'}), 400
        
        if len(extracted_text) > 50000:
            extracted_text = extracted_text[:50000] + "\n[Text truncated]"
        
        return jsonify({
            'text': extracted_text,
            'filename': filename,
            'length': len(extracted_text),
            'file_type': file_extension.upper(),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': f'File processing error: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting AI Detection & Plagiarism Checker Pro v8.1...")
    print(f"OpenAI API: {'✅ Configured' if openai.api_key else '❌ Missing'}")
    print(f"Google Search: {'✅ Configured' if (GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID) else '❌ Missing'}")
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
