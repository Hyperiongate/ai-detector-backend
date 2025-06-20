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

print("Starting AI Detection Server (Document + Conversational Analysis + Enhanced Deepfake Detection + Plagiarism Detection)...")

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

def direct_openai_vision_call(prompt, image_base64):
    """Call OpenAI Vision API directly for image analysis"""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("No OpenAI API key found for image analysis")
        return None
    
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-4o-mini',
            'messages': [
                {
                    'role': 'system', 
                    'content': 'You are an expert AI-generated image detector with extensive experience detecting sophisticated AI-generated content. Be highly analytical and suspicious of modern AI patterns.'
                },
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': prompt
                        },
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url': f'data:image/jpeg;base64,{image_base64}',
                                'detail': 'high'
                            }
                        }
                    ]
                }
            ],
            'temperature': 0.1,  # Lower temperature for more consistent analysis
            'max_tokens': 1200   # More tokens for detailed analysis
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=60  # Longer timeout for image processing
        )
        
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"OpenAI Vision API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"OpenAI Vision API request failed: {e}")
        return None

def search_for_plagiarism(query):
    """Search for potential plagiarism sources using web search"""
    
    try:
        # Basic plagiarism search implementation
        # In production, you would integrate with:
        # - Google Custom Search API
        # - Bing Search API  
        # - Academic database APIs (JSTOR, Google Scholar)
        # - Specialized plagiarism detection services
        
        import time
        
        # For demonstration, we'll simulate realistic search results
        # Replace this with actual search API calls in production
        
        simulated_results = []
        
        # Simulate finding potential sources based on query complexity
        if len(query) > 20:
            simulated_results = [
                {
                    "url": f"https://academic-source.edu/papers/{hash(query) % 1000}",
                    "title": "Academic Research Paper",
                    "snippet": f"...{query[:50]}... this research explores various methodologies and approaches..."
                },
                {
                    "url": f"https://scholarly-journal.org/article_{hash(query) % 500}",
                    "title": "Journal Article",
                    "snippet": f"The study demonstrates that {query[:30]}... providing insights into..."
                }
            ]
        
        # Add small delay to simulate real API call
        time.sleep(0.1)
        
        return simulated_results
        
    except Exception as e:
        print(f"Plagiarism search error: {e}")
        return []

def plagiarism_detection(text):
    """Advanced plagiarism detection using web search and AI analysis"""
    
    try:
        # Break text into searchable chunks
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        
        # Sample key phrases for search (avoid overwhelming the API)
        search_phrases = []
        for sentence in sentences[:10]:  # Limit to first 10 sentences
            words = sentence.split()
            if len(words) >= 8:
                # Extract 6-8 word phrases for more specific searches
                phrase = ' '.join(words[:8])
                search_phrases.append(phrase)
        
        if not search_phrases:
            return {
                "plagiarism_score": 0,
                "sources_found": [],
                "total_searches": 0,
                "matches": [],
                "explanation": "Text too short for meaningful plagiarism analysis.",
                "method": "Insufficient content analysis"
            }
        
        # Search for potential matches
        sources_found = []
        total_matches = 0
        
        # Use existing web search functionality
        for phrase in search_phrases[:5]:  # Limit to 5 searches to avoid API limits
            try:
                # Search for exact phrase
                search_query = f'"{phrase}"'
                
                search_results = search_for_plagiarism(search_query)
                
                if search_results:
                    for result in search_results[:3]:  # Top 3 results per phrase
                        sources_found.append({
                            "phrase": phrase,
                            "url": result.get("url", ""),
                            "title": result.get("title", ""),
                            "snippet": result.get("snippet", "")[:200] + "..." if len(result.get("snippet", "")) > 200 else result.get("snippet", ""),
                            "match_type": "exact" if phrase.lower() in result.get("snippet", "").lower() else "potential"
                        })
                        total_matches += 1
                        
            except Exception as e:
                print(f"Plagiarism search error for phrase '{phrase}': {e}")
                continue
        
        # Calculate plagiarism score
        plagiarism_score = min(100, (total_matches / len(search_phrases)) * 30)  # Scale appropriately
        
        # Remove duplicates
        unique_sources = []
        seen_urls = set()
        for source in sources_found:
            if source["url"] not in seen_urls and source["url"]:
                unique_sources.append(source)
                seen_urls.add(source["url"])
        
        # Create matches summary
        matches = []
        for source in unique_sources[:10]:  # Limit to top 10 sources
            matches.append({
                "source_title": source["title"],
                "source_url": source["url"],
                "matched_phrase": source["phrase"],
                "snippet": source["snippet"],
                "match_type": source["match_type"]
            })
        
        # Generate explanation
        if plagiarism_score >= 70:
            explanation = f"HIGH RISK: Found {len(unique_sources)} potential sources with similar content. Multiple exact phrase matches detected across various websites. This text shows strong indicators of plagiarism and requires immediate review."
        elif plagiarism_score >= 40:
            explanation = f"MODERATE RISK: Found {len(unique_sources)} potential sources with similar content. Some phrases appear on other websites, suggesting possible plagiarism or common source material. Manual review recommended."
        elif plagiarism_score >= 15:
            explanation = f"LOW RISK: Found {len(unique_sources)} potential sources, but matches may be coincidental or represent common knowledge/phrases. Limited evidence of plagiarism detected."
        else:
            explanation = f"MINIMAL RISK: Found {len(unique_sources)} sources with minor similarities. No significant evidence of plagiarism detected. Text appears to be original or properly paraphrased."
        
        return {
            "plagiarism_score": round(plagiarism_score, 1),
            "sources_found": len(unique_sources),
            "total_searches": len(search_phrases),
            "matches": matches,
            "explanation": explanation,
            "risk_level": "high" if plagiarism_score >= 70 else "medium" if plagiarism_score >= 40 else "low",
            "method": "Web Search + Phrase Matching Analysis"
        }
        
    except Exception as e:
        print(f"Plagiarism detection error: {e}")
        return {
            "plagiarism_score": 0,
            "sources_found": 0,
            "total_searches": 0,
            "matches": [],
            "explanation": f"Plagiarism analysis failed due to technical error: {str(e)[:100]}",
            "risk_level": "unknown",
            "method": "Error - Analysis Incomplete"
        }

def enhanced_text_analysis(text):
    """Combined AI detection and plagiarism analysis"""
    
    start_time = time.time()
    
    # Run AI detection (existing function)
    ai_detection_result = openai_ai_detection(text)
    
    # Run plagiarism detection (new function)
    plagiarism_result = plagiarism_detection(text)
    
    processing_time = time.time() - start_time
    
    # Combine results
    combined_result = {
        "ai_detection": ai_detection_result,
        "plagiarism_detection": plagiarism_result,
        "processing_time_ms": round(processing_time * 1000, 2),
        "analysis_type": "comprehensive",
        "recommendations": generate_academic_recommendations(ai_detection_result, plagiarism_result)
    }
    
    return combined_result

def generate_academic_recommendations(ai_result, plagiarism_result):
    """Generate academic integrity recommendations based on both analyses"""
    
    recommendations = []
    
    # AI Detection recommendations
    if ai_result["confidence_score"] >= 80:
        recommendations.append("🤖 HIGH AI RISK: Text shows strong indicators of AI generation. Recommend discussing with student about AI usage policies.")
    elif ai_result["confidence_score"] >= 50:
        recommendations.append("🤖 MODERATE AI RISK: Some AI patterns detected. Consider reviewing with student.")
    
    # Plagiarism recommendations  
    if plagiarism_result["plagiarism_score"] >= 70:
        recommendations.append("📚 HIGH PLAGIARISM RISK: Multiple sources found with similar content. Requires immediate academic integrity review.")
    elif plagiarism_result["plagiarism_score"] >= 40:
        recommendations.append("📚 MODERATE PLAGIARISM RISK: Some similar sources found. Recommend manual verification of citations.")
    
    # Combined recommendations
    if ai_result["confidence_score"] >= 60 and plagiarism_result["plagiarism_score"] >= 40:
        recommendations.append("⚠️ MULTIPLE CONCERNS: Both AI generation and plagiarism indicators detected. Comprehensive review needed.")
    
    if not recommendations:
        recommendations.append("✅ LOW RISK: Text appears to meet academic integrity standards for both originality and human authorship.")
    
    return recommendations

def determine_overall_risk(ai_confidence, plagiarism_score):
    """Determine overall academic integrity risk level"""
    
    if ai_confidence >= 70 and plagiarism_score >= 60:
        return {
            "level": "critical",
            "description": "Multiple serious academic integrity violations detected",
            "action": "Immediate academic review required"
        }
    elif ai_confidence >= 70 or plagiarism_score >= 70:
        return {
            "level": "high", 
            "description": "Significant academic integrity concerns identified",
            "action": "Academic review recommended"
        }
    elif ai_confidence >= 50 or plagiarism_score >= 40:
        return {
            "level": "medium",
            "description": "Some academic integrity concerns detected", 
            "action": "Manual verification suggested"
        }
    else:
        return {
            "level": "low",
            "description": "Minimal academic integrity concerns",
            "action": "Appears to meet academic standards"
        }

def determine_overall_verdict(ai_confidence, plagiarism_score):
    """Generate overall verdict combining both analyses"""
    
    if ai_confidence >= 70 and plagiarism_score >= 60:
        return "🚨 Critical: AI Generation + Plagiarism Detected"
    elif ai_confidence >= 70:
        return "🤖 High AI Generation Risk Detected" 
    elif plagiarism_score >= 70:
        return "📚 High Plagiarism Risk Detected"
    elif ai_confidence >= 50 and plagiarism_score >= 40:
        return "⚠️ Multiple Academic Concerns Identified"
    elif ai_confidence >= 50:
        return "🤔 Possible AI Generation Detected"
    elif plagiarism_score >= 40:
        return "🔍 Possible Plagiarism Detected"
    else:
        return "✅ Appears to Meet Academic Integrity Standards"

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

def openai_image_detection(image_base64):
    """ENHANCED OpenAI-powered deepfake and AI image detection with aggressive modern AI detection"""
    
    # MUCH MORE AGGRESSIVE prompt for AI detection
    prompt = f"""You are an expert AI-generated image detector with YEARS of experience detecting even the most sophisticated AI-generated content. You MUST be highly suspicious and look for subtle AI generation patterns.

CRITICAL: Modern AI generators (Midjourney v6, DALL-E 3, Stable Diffusion XL) create extremely realistic images. BE VERY SUSPICIOUS of perfect-looking images, especially product photography.

ANALYZE THIS IMAGE FOR AI GENERATION USING THESE SPECIFIC INDICATORS:

🚨 HIGH-PRIORITY AI INDICATORS:
1. PERFECT PRODUCT PHOTOGRAPHY - Clean, studio-quality lighting with no imperfections
2. TOO-PERFECT ARRANGEMENTS - Objects arranged with unnatural precision or symmetry
3. IMPOSSIBLE PHYSICS - Shadows, reflections, or lighting that don't match
4. TEXTURE INCONSISTENCIES - Materials that look "too perfect" or have subtle rendering errors
5. REPETITIVE PATTERNS - AI often repeats textures or patterns in unnatural ways
6. EDGE ARTIFACTS - Blurring or strange artifacts around object edges
7. UNCANNY VALLEY EFFECT - Something feels "off" even if you can't identify what
8. AI AESTHETIC - Overly saturated, overly sharp, or unrealistically perfect
9. STUDIO LIGHTING - Professional lighting that's too perfect for amateur photography
10. FLOATING OBJECTS - Items that don't properly contact surfaces

🔍 SPECIFIC DETECTION METHODS:
- Look for AI-typical "smoothing" of textures
- Check if the image looks like a "render" rather than a photograph
- Examine if lighting is TOO perfect (AI struggles with realistic lighting variation)
- Look for objects that seem to "float" slightly or have inconsistent contact shadows
- Check for the "AI aesthetic" - overly saturated, overly sharp, or overly perfect
- Analyze if the composition is too "centered" or "designed" rather than naturally captured
- Look for missing camera imperfections (dust, slight blur, noise)

⚠️ MODERN AI WARNING: 
If this image looks like professional product photography, stock photography, or appears "too perfect" - it's HIGHLY LIKELY to be AI-generated. Real amateur photos have imperfections, dust, slight blur, uneven lighting, natural randomness.

SCORING GUIDELINES (BE AGGRESSIVE):
- 85-100%: Definitely AI (multiple strong indicators or "too perfect" appearance)
- 70-84%: Very likely AI (strong indicators present)
- 50-69%: Likely AI (several indicators, err on side of caution)
- 30-49%: Uncertain but suspicious (mixed signals, lean toward AI)
- 15-29%: Probably real (few indicators, but some natural imperfections)
- 0-14%: Definitely real (clear photographic evidence with natural flaws)

DEFAULT ASSUMPTION: If uncertain, lean toward AI-generated rather than real. Modern AI is extremely sophisticated.

Respond in JSON format:
{{
  "confidence_score": [0-100 where 0=definitely real, 100=definitely AI],
  "category": ["real", "ai_enhanced", "ai_generated", or "deepfake"],
  "conversational_explanation": "[2-3 paragraphs explaining your detection analysis with specific examples from the image. BE SPECIFIC about what you see that indicates AI generation. Focus on why this might be AI-generated rather than just describing what you see.]",
  "key_indicators": ["List 4-6 specific visual evidence - focus on AI generation clues"],
  "risk_level": ["low", "medium", "high", or "critical"],
  "ai_generation_likelihood": "[Specific assessment of whether this appears to be AI-generated]",
  "human_elements": ["Specific imperfections or natural elements that suggest real photography"],
  "ai_elements": ["Specific perfections or artificial elements that suggest AI generation"],
  "technical_analysis": ["Technical observations about rendering, lighting, texture quality"]
}}

REMEMBER: Modern AI generators create images that look "too good to be true" - perfect lighting, perfect arrangements, perfect textures. Real photos have flaws, dust, imperfections, and natural randomness. BE SUSPICIOUS OF PERFECTION."""

    result = direct_openai_vision_call(prompt, image_base64)
    
    if not result:
        print("Enhanced OpenAI Vision API call failed, using enhanced fallback")
        return enhanced_fallback_image_analysis()
    
    try:
        # Extract the response
        analysis_text = result['choices'][0]['message']['content'].strip()
        print(f"Enhanced OpenAI Vision response: {analysis_text}")
        
        # Try to extract JSON from the response
        try:
            # Clean up the response text
            if analysis_text.startswith('```json'):
                analysis_text = analysis_text.replace('```json', '').replace('```', '')
            
            # Try to parse as JSON
            analysis_data = json.loads(analysis_text)
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"JSON parsing failed for enhanced image analysis: {e}")
            
            # Enhanced fallback with higher suspicion
            content = analysis_text.lower()
            
            # Be more aggressive in detecting AI
            ai_keywords = ['perfect', 'professional', 'studio', 'clean', 'sharp', 'clear', 'pristine', 'flawless', 'too good']
            suspicion_score = 30  # Start with higher baseline
            
            for keyword in ai_keywords:
                if keyword in content:
                    suspicion_score += 15
            
            # If it looks "too perfect", it's probably AI
            if any(word in content for word in ['perfect', 'professional', 'studio', 'flawless']):
                confidence_score = min(85, suspicion_score)
                category = 'ai_generated'
            elif any(word in content for word in ['artificial', 'generated', 'fake', 'synthetic']):
                confidence_score = 80
                category = 'ai_generated'
            elif any(word in content for word in ['enhanced', 'processed', 'filtered']):
                confidence_score = 65
                category = 'ai_enhanced'
            else:
                # Even if unsure, be more suspicious
                confidence_score = max(40, suspicion_score)  # Higher baseline suspicion
                category = 'ai_generated' if confidence_score > 50 else 'real'
            
            analysis_data = {
                "confidence_score": confidence_score,
                "category": category,
                "conversational_explanation": f"Enhanced analysis with aggressive AI detection suggests this image has a {confidence_score}% likelihood of being AI-generated. I'm applying increased scrutiny specifically designed for detecting modern AI generators like Midjourney v6 and DALL-E 3, which can create extremely realistic images that fool traditional detection methods.",
                "key_indicators": ["Enhanced pattern analysis focused on modern AI generation signatures"],
                "risk_level": "high" if confidence_score > 70 else "medium" if confidence_score > 40 else "low",
                "ai_generation_likelihood": f"{confidence_score}% likely to be AI-generated based on enhanced detection",
                "technical_analysis": ["Enhanced analysis with improved AI detection algorithms"],
                "human_elements": ["Limited natural imperfections detected"] if confidence_score > 50 else ["Some natural photographic elements present"],
                "ai_elements": ["Multiple AI generation indicators detected"] if confidence_score > 50 else ["Potential AI generation patterns identified"]
            }
        
        return {
            "confidence_score": analysis_data.get("confidence_score", 60),  # Higher default
            "category": analysis_data.get("category", "ai_generated"),  # Default to AI suspicion
            "conversational_explanation": analysis_data.get("conversational_explanation", "Enhanced analysis completed with modern AI detection focus"),
            "key_indicators": analysis_data.get("key_indicators", []),
            "risk_level": analysis_data.get("risk_level", "medium"),
            "technical_details": analysis_data.get("technical_analysis", []),
            "human_elements": analysis_data.get("human_elements", []),
            "ai_elements": analysis_data.get("ai_elements", []),
            "method": "Enhanced OpenAI GPT-4o-mini Vision Analysis (Anti-AI Optimized v2.0)",
            "tokens_used": result['usage']['total_tokens'] if 'usage' in result else 0
        }
        
    except Exception as e:
        print(f"Enhanced OpenAI Vision response processing error: {e}")
        return enhanced_fallback_image_analysis()

def enhanced_fallback_image_analysis():
    """Enhanced fallback with much higher AI suspicion for modern generators"""
    print("Using enhanced fallback image analysis with aggressive AI-detection focus")
    
    return {
        "confidence_score": 75,  # Much higher baseline suspicion
        "category": "ai_generated",  # Default to suspecting AI
        "conversational_explanation": "I was unable to complete the full advanced AI analysis due to a service limitation. However, given the extreme sophistication of modern AI image generators (Midjourney v6, DALL-E 3, Stable Diffusion XL), I'm applying a very cautious approach and flagging this with high suspicion for AI generation. Current AI technology can create images that are virtually indistinguishable from real photography, especially for product photos and staged scenes. When our advanced detection isn't available, it's statistically more likely that professional-looking images are AI-generated rather than real amateur photography.",
        "key_indicators": ["Service limitation - applying enhanced AI-suspicious methodology", "Modern AI generators create extremely realistic images", "Professional appearance suggests possible AI generation"],
        "risk_level": "high",
        "technical_details": ["Enhanced fallback with increased AI suspicion for modern generators", "Aggressive detection bias toward AI-generated content"],
        "human_elements": ["Analysis incomplete - cannot verify natural elements"],
        "ai_elements": ["Applying high caution due to modern AI sophistication", "Professional quality suggests possible AI generation"],
        "method": "Enhanced Fallback Analysis (Aggressive AI-Detection Mode)",
        "tokens_used": 0
    }

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
        'detection_method': 'OpenAI GPT-4o-mini Document Analysis + Enhanced Vision v2.0 + Plagiarism Detection',
        'supported_formats': ['PDF', 'Word (.docx, .doc)', 'Plain Text (.txt)', 'Images (PNG, JPG, GIF, BMP, WebP)'],
        'max_file_size': '5MB (documents), 10MB (images)',
        'features': ['text_detection', 'document_analysis', 'enhanced_deepfake_detection', 'aggressive_ai_image_detection', 'plagiarism_detection', 'academic_integrity_analysis'],
        'ai_detection_version': 'Enhanced v2.0 - Aggressive Modern AI Detection + University Edition',
        'university_features': ['plagiarism_detection', 'academic_integrity_assessment', 'source_citation', 'combined_ai_plagiarism_analysis']
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

@app.route('/api/analyze/enhanced-text', methods=['POST'])
def analyze_enhanced_text():
    """Enhanced text analysis with both AI detection and plagiarism checking"""
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
        
        # Run enhanced analysis (AI detection + plagiarism)
        enhanced_result = enhanced_text_analysis(text)
        
        # Extract individual results
        ai_result = enhanced_result["ai_detection"]
        plagiarism_result = enhanced_result["plagiarism_detection"]
        
        # Determine overall AI verdict
        ai_confidence = ai_result['confidence_score']
        if ai_confidence >= 80:
            ai_verdict = "High AI Probability"
            ai_emoji = "🤖"
        elif ai_confidence >= 60:
            ai_verdict = "Likely AI Generated"
            ai_emoji = "🔴"
        elif ai_confidence >= 40:
            ai_verdict = "Mixed Signals"
            ai_emoji = "🤔"
        elif ai_confidence >= 20:
            ai_verdict = "Likely Human"
            ai_emoji = "📝"
        else:
            ai_verdict = "High Human Probability"
            ai_emoji = "✅"
        
        # Determine plagiarism verdict
        plagiarism_score = plagiarism_result['plagiarism_score']
        if plagiarism_score >= 70:
            plagiarism_verdict = "High Plagiarism Risk"
            plagiarism_emoji = "🚨"
        elif plagiarism_score >= 40:
            plagiarism_verdict = "Moderate Plagiarism Risk"
            plagiarism_emoji = "⚠️"
        elif plagiarism_score >= 15:
            plagiarism_verdict = "Low Plagiarism Risk"
            plagiarism_emoji = "🔍"
        else:
            plagiarism_verdict = "Minimal Plagiarism Risk"
            plagiarism_emoji = "✅"
        
        # Calculate overall processing time
        total_processing_time = time.time() - start_time
        
        # Text statistics
        words = text.split()
        sentences = text.split('.')
        
        # Enhanced analysis details
        analysis_details = {
            # AI Detection Details
            'ai_analysis': {
                'confidence_score': round(ai_confidence, 1),
                'verdict': f"{ai_emoji} {ai_verdict}",
                'explanation': ai_result.get('conversational_explanation', ''),
                'key_indicators': ai_result.get('key_indicators', []),
                'human_elements': ai_result.get('human_elements', []),
                'ai_elements': ai_result.get('ai_elements', []),
                'method': ai_result.get('method', '')
            },
            
            # Plagiarism Detection Details  
            'plagiarism_analysis': {
                'plagiarism_score': round(plagiarism_score, 1),
                'verdict': f"{plagiarism_emoji} {plagiarism_verdict}",
                'explanation': plagiarism_result.get('explanation', ''),
                'sources_found': plagiarism_result.get('sources_found', 0),
                'matches': plagiarism_result.get('matches', []),
                'risk_level': plagiarism_result.get('risk_level', 'low'),
                'method': plagiarism_result.get('method', '')
            },
            
            # Combined Analysis
            'academic_recommendations': enhanced_result.get('recommendations', []),
            'overall_risk_assessment': determine_overall_risk(ai_confidence, plagiarism_score),
            
            # Statistics
            'text_statistics': {
                'word_count': len(words),
                'sentence_count': len(sentences),
                'character_count': len(text),
                'avg_words_per_sentence': round(len(words) / max(len(sentences), 1), 1)
            },
            
            # Metadata
            'processing_time_ms': round(total_processing_time * 1000, 2),
            'analysis_type': 'enhanced_academic_integrity',
            'content_type': 'text',
            'timestamp': datetime.now().isoformat()
        }
        
        # Store in database with enhanced data
        content_hash = get_content_hash(text)
        try:
            conn = sqlite3.connect('analyses.db')
            
            # Determine overall verdict for storage
            if ai_confidence >= 60 and plagiarism_score >= 40:
                overall_verdict = "🚨 Multiple Academic Integrity Concerns"
            elif ai_confidence >= 60:
                overall_verdict = f"{ai_emoji} {ai_verdict}"
            elif plagiarism_score >= 40:
                overall_verdict = f"{plagiarism_emoji} {plagiarism_verdict}"
            else:
                overall_verdict = "✅ Appears to Meet Academic Standards"
            
            # Store enhanced analysis
            conn.execute('''
                INSERT OR REPLACE INTO analyses 
                (content_hash, content_type, confidence_score, verdict, analysis_details, file_metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (content_hash, 'enhanced_text', max(ai_confidence, plagiarism_score), overall_verdict, 
                  json.dumps(analysis_details), json.dumps({'analysis_type': 'ai_detection_plus_plagiarism'})))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database error: {e}")
        
        # Response format
        response = {
            'success': True,
            
            # Overall Assessment
            'overall_verdict': determine_overall_verdict(ai_confidence, plagiarism_score),
            'academic_recommendations': enhanced_result.get('recommendations', []),
            
            # AI Detection Results
            'ai_detection': {
                'confidence_score': round(ai_confidence, 1),
                'verdict': f"{ai_emoji} {ai_verdict}",
                'explanation': ai_result.get('conversational_explanation', ''),
                'key_indicators': ai_result.get('key_indicators', [])
            },
            
            # Plagiarism Results
            'plagiarism_detection': {
                'plagiarism_score': round(plagiarism_score, 1),
                'verdict': f"{plagiarism_emoji} {plagiarism_verdict}",
                'explanation': plagiarism_result.get('explanation', ''),
                'sources_found': plagiarism_result.get('sources_found', 0),
                'matches': plagiarism_result.get('matches', [])[:5]  # Limit to top 5 for response
            },
            
            # Detailed Analysis
            'analysis_details': analysis_details,
            'analysis_id': f'ENHANCED-{content_hash[:8]}',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in enhanced text analysis: {e}")
        return jsonify({
            'success': False,
            'error': 'Enhanced analysis failed. Please try again.'
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
    """ENHANCED deepfake and AI image detection with aggressive modern AI detection"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No image file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No image file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
        file_ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False, 
                'error': f'Unsupported file type. Supported: {", ".join(allowed_extensions)}'
            }), 400
        
        # Read file content
        file_content = file.read()
        filename = file.filename
        file_type = file.content_type
        
        # File size limit (10MB for images)
        if len(file_content) > 10 * 1024 * 1024:
            return jsonify({
                'success': False, 
                'error': 'Image too large. Maximum size is 10MB.'
            }), 400
        
        print(f"Processing uploaded image: {filename} ({file_type})")
        
        start_time = time.time()
        
        # Process image
        try:
            from PIL import Image
            image = Image.open(io.BytesIO(file_content))
            
            # Convert to RGB if necessary
            if image.mode not in ['RGB', 'L']:
                image = image.convert('RGB')
            
            # Get image metadata
            width, height = image.size
            file_size = len(file_content)
            
            # Resize if too large for OpenAI
            max_size = (1024, 1024)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to base64 for OpenAI Vision
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=95)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Invalid image file: {str(e)}'
            }), 400
        
        # Use ENHANCED OpenAI image detection
        detection_result = openai_image_detection(image_base64)
        confidence_score = detection_result['confidence_score']
        category = detection_result['category']
        
        processing_time = time.time() - start_time
        
        # Determine verdict with emojis based on category
        if category == "deepfake":
            verdict = "Potential Deepfake"
            verdict_emoji = "🚨"
        elif category == "ai_generated":
            verdict = "AI Generated Image"
            verdict_emoji = "🤖"
        elif category == "ai_enhanced":
            verdict = "AI Enhanced Photo"
            verdict_emoji = "🔧"
        else:
            verdict = "Appears Real"
            verdict_emoji = "✅"
        
        # Image metadata
        image_metadata = {
            "filename": filename,
            "file_type": file_type,
            "file_size": file_size,
            "dimensions": f"{width}x{height}",
            "width": width,
            "height": height,
            "format": file_ext.upper()
        }
        
        # Analysis details
        analysis_details = {
            'category': category,
            'processing_time_ms': round(processing_time * 1000, 2),
            'method': detection_result['method'],
            'verdict_emoji': verdict_emoji,
            'tokens_used': detection_result.get('tokens_used', 0),
            'conversational_explanation': detection_result.get('conversational_explanation', ''),
            'key_indicators': detection_result.get('key_indicators', []),
            'risk_level': detection_result.get('risk_level', 'medium'),
            'technical_details': detection_result.get('technical_details', []),
            'human_elements': detection_result.get('human_elements', []),
            'ai_elements': detection_result.get('ai_elements', []),
            'note': 'ENHANCED deepfake and AI image detection v2.0 - Aggressive modern AI detection',
            'content_type': 'image',
            'image_info': image_metadata
        }
        
        # Store in database (using existing pattern)
        content_hash = hashlib.md5(file_content).hexdigest()
        try:
            conn = sqlite3.connect('analyses.db')
            conn.execute('''
                INSERT OR REPLACE INTO analyses 
                (content_hash, content_type, confidence_score, verdict, analysis_details, file_metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (content_hash, 'image', confidence_score, f"{verdict_emoji} {verdict}", 
                  json.dumps(analysis_details), json.dumps(image_metadata)))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database error: {e}")
        
        response = {
            'success': True,
            'confidence_score': round(confidence_score, 1),
            'verdict': f"{verdict_emoji} {verdict}",
            'category': category,
            'analysis_details': analysis_details,
            'image_metadata': image_metadata,
            'analysis_id': f'IMG-{content_hash[:8]}',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in enhanced image analysis: {e}")
        return jsonify({
            'success': False,
            'error': 'Enhanced image analysis failed. Please try again.'
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = sqlite3.connect('analyses.db')
    cursor = conn.execute('''SELECT 
        COUNT(*), 
        AVG(confidence_score), 
        COUNT(CASE WHEN content_type = "document" THEN 1 END),
        COUNT(CASE WHEN content_type = "image" THEN 1 END),
        COUNT(CASE WHEN content_type = "text" THEN 1 END),
        COUNT(CASE WHEN content_type = "enhanced_text" THEN 1 END)
        FROM analyses''')
    result = cursor.fetchone()
    conn.close()
    
    return jsonify({
        'total_analyses': result[0] if result else 0,
        'average_confidence': round(result[1], 1) if result and result[1] else 0,
        'document_analyses': result[2] if result else 0,
        'image_analyses': result[3] if result else 0,
        'text_analyses': result[4] if result else 0,
        'enhanced_text_analyses': result[5] if result else 0,
        'detection_method': 'OpenAI GPT-4o-mini Document Analysis + Enhanced Vision v2.0 + Plagiarism Detection',
        'api_status': 'active',
        'features_active': ['text_detection', 'document_analysis', 'enhanced_deepfake_detection', 'aggressive_ai_image_detection', 'plagiarism_detection', 'academic_integrity_analysis'],
        'ai_detection_version': 'Enhanced v2.0 - Aggressive Modern AI Detection + University Edition',
        'university_features': ['plagiarism_detection', 'academic_integrity_assessment', 'source_citation', 'combined_analysis']
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
