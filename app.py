from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import requests
import re
import base64
import io
from PIL import Image
from PIL.ExifTags import TAGS
import os
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# API Keys - replace with your actual keys
openai.api_key = os.environ.get('OPENAI_API_KEY')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
GOOGLE_FACT_CHECK_API_KEY = os.environ.get('GOOGLE_FACT_CHECK_API_KEY')

@app.route('/')
def home():
    return jsonify({
        "message": "Facts & Fakes AI Backend - Professional v8.0",
        "status": "operational",
        "tools": [
            "News Misinformation Detector",
            "Unified Content Authenticity Checker", 
            "AI Image Analysis Tool"
        ],
        "version": "8.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/analyze-news', methods=['POST'])
def analyze_news():
    try:
        data = request.json
        article_text = data.get('article_text', '')
        source_url = data.get('source_url', '')
        
        if not article_text:
            return jsonify({"error": "Article text is required"}), 400
        
        # OpenAI Analysis
        prompt = f"""
        Analyze this news article for misinformation, bias, and credibility. Provide a comprehensive assessment:

        Article: {article_text[:3000]}
        Source URL: {source_url}

        Please analyze:
        1. Factual accuracy and potential misinformation
        2. Political bias (left, center, right, or mixed)
        3. Source credibility assessment
        4. Emotional manipulation techniques
        5. Overall credibility score (0-100)

        Provide specific examples and reasoning for each assessment.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.3
        )
        
        analysis = response.choices[0].message.content
        
        # Extract domain for source verification
        domain = None
        if source_url:
            import urllib.parse
            domain = urllib.parse.urlparse(source_url).netloc
        
        # Basic credibility scoring based on analysis
        credibility_score = 75  # Default middle score
        if "high credibility" in analysis.lower() or "reliable" in analysis.lower():
            credibility_score = 85
        elif "low credibility" in analysis.lower() or "unreliable" in analysis.lower():
            credibility_score = 40
        elif "questionable" in analysis.lower() or "biased" in analysis.lower():
            credibility_score = 55
        
        return jsonify({
            "analysis": analysis,
            "credibility_score": credibility_score,
            "source_domain": domain,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze-content-authenticity', methods=['POST'])
def analyze_content_authenticity():
    try:
        data = request.json
        content = data.get('content', '')
        
        if not content:
            return jsonify({"error": "Content is required"}), 400
        
        # Stage 1: AI Pattern Analysis
        ai_prompt = f"""
        Analyze this text for AI generation patterns. Look for:
        1. Repetitive phrases or structures
        2. Overly formal or unnatural language
        3. Generic or template-like content
        4. Lack of personal voice or unique perspective
        5. Perfect grammar with no natural errors
        
        Text: {content[:2000]}
        
        Rate the likelihood this is AI-generated (0-100%) and explain your reasoning.
        """
        
        ai_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": ai_prompt}],
            max_tokens=800,
            temperature=0.3
        )
        
        ai_analysis = ai_response.choices[0].message.content
        
        # Stage 2: Linguistic Analysis
        linguistic_prompt = f"""
        Perform linguistic analysis on this text:
        1. Sentence structure variety
        2. Vocabulary sophistication and range
        3. Natural flow and coherence
        4. Personal voice indicators
        5. Cultural/contextual references
        
        Text: {content[:2000]}
        
        Assess authenticity based on linguistic patterns (0-100% authentic).
        """
        
        linguistic_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": linguistic_prompt}],
            max_tokens=800,
            temperature=0.3
        )
        
        linguistic_analysis = linguistic_response.choices[0].message.content
        
        # Stage 3: Plagiarism Check (basic web search)
        plagiarism_results = "No exact matches found in web search."
        try:
            if NEWS_API_KEY:
                search_query = content[:100].replace('"', '').replace('\n', ' ')
                search_url = f"https://newsapi.org/v2/everything?q=\"{search_query}\"&apiKey={NEWS_API_KEY}&pageSize=5"
                search_response = requests.get(search_url, timeout=10)
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    if search_data.get('articles'):
                        plagiarism_results = f"Found {len(search_data['articles'])} potentially related articles. Manual verification recommended."
        except Exception:
            plagiarism_results = "Plagiarism check unavailable."
        
        # Stage 4: Overall Authenticity Scoring
        scoring_prompt = f"""
        Based on these analyses, provide an overall authenticity score (0-100%):
        
        AI Analysis: {ai_analysis[:500]}
        Linguistic Analysis: {linguistic_analysis[:500]}
        Plagiarism Check: {plagiarism_results}
        
        Consider:
        - Lower scores = likely AI-generated or plagiarized
        - Higher scores = likely authentic human content
        - Provide reasoning for the final score
        
        Give a single authenticity score (0-100%) and brief explanation.
        """
        
        scoring_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": scoring_prompt}],
            max_tokens=400,
            temperature=0.3
        )
        
        final_scoring = scoring_response.choices[0].message.content
        
        # Extract numerical score
        score_match = re.search(r'(\d+)%', final_scoring)
        authenticity_score = int(score_match.group(1)) if score_match else 50
        
        return jsonify({
            "authenticity_score": authenticity_score,
            "ai_analysis": ai_analysis,
            "linguistic_analysis": linguistic_analysis,
            "plagiarism_check": plagiarism_results,
            "final_assessment": final_scoring,
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "analysis_stages": 4
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze-ai-content', methods=['POST'])
def analyze_ai_content():
    # Redirect to unified content authenticity checker
    return analyze_content_authenticity()

@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    try:
        # Handle file upload or base64 data
        image_data = None
        filename = None
        
        if 'image' in request.files:
            # File upload
            file = request.files['image']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            filename = file.filename
            image_data = file.read()
        elif request.json and 'image_data' in request.json:
            # Base64 data
            try:
                image_data = base64.b64decode(request.json['image_data'])
                filename = request.json.get('filename', 'uploaded_image.jpg')
            except Exception:
                return jsonify({"error": "Invalid base64 image data"}), 400
        else:
            return jsonify({"error": "No image provided"}), 400
        
        # Validate image
        try:
            image = Image.open(io.BytesIO(image_data))
            image_format = image.format
            image_size = image.size
        except Exception:
            return jsonify({"error": "Invalid image file"}), 400
        
        # Stage 1: Metadata Analysis
        metadata_analysis = analyze_image_metadata(image_data)
        
        # Stage 2: OpenAI Vision Analysis
        base64_image = base64.b64encode(image_data).decode('utf-8')
        vision_analysis = analyze_with_openai_vision(base64_image)
        
        # Stage 3: Technical Analysis
        technical_analysis = analyze_image_technical(image)
        
        # Stage 4: Overall Authenticity Assessment
        overall_assessment = calculate_image_authenticity(
            metadata_analysis, vision_analysis, technical_analysis
        )
        
        return jsonify({
            "filename": filename,
            "image_format": image_format,
            "image_size": image_size,
            "metadata_analysis": metadata_analysis,
            "vision_analysis": vision_analysis,
            "technical_analysis": technical_analysis,
            "overall_assessment": overall_assessment,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def analyze_image_metadata(image_data):
    """Analyze image metadata for authenticity indicators"""
    try:
        image = Image.open(io.BytesIO(image_data))
        exifdata = image.getexif()
        
        metadata_info = {}
        suspicious_indicators = []
        authenticity_indicators = []
        
        if exifdata:
            for tag_id in exifdata:
                tag = TAGS.get(tag_id, tag_id)
                data = exifdata.get(tag_id)
                metadata_info[tag] = str(data)
        
        # Check for common AI generation indicators
        if not exifdata or len(exifdata) < 5:
            suspicious_indicators.append("Limited or missing EXIF metadata (common in AI-generated images)")
        
        if 'Software' in metadata_info:
            software = metadata_info['Software'].lower()
            ai_software_keywords = ['artificial', 'ai', 'generated', 'midjourney', 'dalle', 'stable diffusion']
            if any(keyword in software for keyword in ai_software_keywords):
                suspicious_indicators.append(f"AI generation software detected: {metadata_info['Software']}")
        
        if 'Camera' in metadata_info or 'Make' in metadata_info:
            authenticity_indicators.append("Camera/device information present")
        
        if 'DateTime' in metadata_info:
            authenticity_indicators.append("Timestamp information present")
        
        if 'GPS' in str(metadata_info):
            authenticity_indicators.append("GPS location data present")
        
        confidence_score = max(20, 80 - len(suspicious_indicators) * 15 + len(authenticity_indicators) * 10)
        
        return {
            "metadata_present": len(metadata_info) > 0,
            "metadata_count": len(metadata_info),
            "suspicious_indicators": suspicious_indicators,
            "authenticity_indicators": authenticity_indicators,
            "confidence_score": min(95, confidence_score),
            "key_metadata": {k: v for k, v in list(metadata_info.items())[:10]}
        }
        
    except Exception as e:
        return {
            "error": f"Metadata analysis failed: {str(e)}",
            "confidence_score": 50
        }

def analyze_with_openai_vision(base64_image):
    """Use OpenAI Vision API to analyze image for AI generation indicators"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this image for signs of AI generation. Look for:
                            1. Unnatural lighting or shadows
                            2. Inconsistent textures or patterns
                            3. Facial or anatomical irregularities
                            4. Background inconsistencies
                            5. Digital artifacts or unusual smoothness
                            6. Perfect symmetry where natural variation is expected
                            
                            Rate the likelihood this is AI-generated (0-100%) and explain your reasoning with specific visual details."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=800
        )
        
        analysis_text = response.choices[0].message.content
        
        # Extract confidence score
        score_match = re.search(r'(\d+)%', analysis_text)
        ai_likelihood = int(score_match.group(1)) if score_match else 50
        authenticity_score = 100 - ai_likelihood
        
        return {
            "analysis": analysis_text,
            "ai_likelihood": ai_likelihood,
            "authenticity_score": authenticity_score,
            "model_used": "gpt-4-vision-preview"
        }
        
    except Exception as e:
        # Fallback to standard GPT if Vision API fails
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user", 
                    "content": "Image analysis unavailable. Provide general guidance on detecting AI-generated images."
                }],
                max_tokens=400
            )
            
            return {
                "analysis": response.choices[0].message.content,
                "ai_likelihood": 50,
                "authenticity_score": 50,
                "note": "Vision analysis unavailable - using general guidance",
                "model_used": "gpt-3.5-turbo"
            }
        except Exception:
            return {
                "analysis": "Visual analysis unavailable at this time.",
                "ai_likelihood": 50,
                "authenticity_score": 50,
                "error": str(e)
            }

def analyze_image_technical(image):
    """Perform technical analysis of image properties"""
    try:
        width, height = image.size
        mode = image.mode
        
        # Calculate aspect ratio
        aspect_ratio = width / height
        
        # Check for common AI generation resolutions
        common_ai_resolutions = [
            (512, 512), (1024, 1024), (768, 768),
            (512, 768), (768, 512), (1024, 1536),
            (640, 640), (896, 896)
        ]
        
        suspicious_technical = []
        authenticity_technical = []
        
        if (width, height) in common_ai_resolutions:
            suspicious_technical.append(f"Common AI generation resolution: {width}x{height}")
        
        if width == height:
            suspicious_technical.append("Perfect square aspect ratio (common in AI generation)")
        
        if width % 64 == 0 and height % 64 == 0:
            suspicious_technical.append("Dimensions divisible by 64 (AI model optimization)")
        
        # Check for unusual aspect ratios
        if 0.8 <= aspect_ratio <= 1.2:
            # Normal range
            authenticity_technical.append("Standard aspect ratio")
        elif aspect_ratio < 0.5 or aspect_ratio > 2.0:
            authenticity_technical.append("Unusual aspect ratio (suggests authentic capture)")
        
        # Image quality indicators
        if width >= 2000 or height >= 2000:
            authenticity_technical.append("High resolution (less common in AI generation)")
        
        technical_score = 60 - len(suspicious_technical) * 15 + len(authenticity_technical) * 10
        technical_score = max(10, min(90, technical_score))
        
        return {
            "dimensions": f"{width}x{height}",
            "aspect_ratio": round(aspect_ratio, 2),
            "color_mode": mode,
            "suspicious_indicators": suspicious_technical,
            "authenticity_indicators": authenticity_technical,
            "technical_score": technical_score
        }
        
    except Exception as e:
        return {
            "error": f"Technical analysis failed: {str(e)}",
            "technical_score": 50
        }

def calculate_image_authenticity(metadata_analysis, vision_analysis, technical_analysis):
    """Calculate overall image authenticity score"""
    try:
        # Weight the different analyses
        metadata_score = metadata_analysis.get('confidence_score', 50)
        vision_score = vision_analysis.get('authenticity_score', 50)
        technical_score = technical_analysis.get('technical_score', 50)
        
        # Weighted average (Vision analysis gets highest weight)
        overall_score = int(
            (vision_score * 0.5) + 
            (metadata_score * 0.3) + 
            (technical_score * 0.2)
        )
        
        # Determine confidence level
        if overall_score >= 80:
            confidence_level = "High confidence - likely authentic"
        elif overall_score >= 60:
            confidence_level = "Moderate confidence - possibly authentic"
        elif overall_score >= 40:
            confidence_level = "Low confidence - uncertain authenticity"
        else:
            confidence_level = "Very low confidence - likely AI-generated"
        
        # Generate summary
        summary_prompt = f"""
        Based on image analysis results:
        - Metadata Score: {metadata_score}/100
        - Visual Analysis Score: {vision_score}/100  
        - Technical Score: {technical_score}/100
        - Overall Score: {overall_score}/100
        
        Provide a concise summary explaining the authenticity assessment and key findings.
        """
        
        try:
            summary_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": summary_prompt}],
                max_tokens=300,
                temperature=0.3
            )
            summary = summary_response.choices[0].message.content
        except Exception:
            summary = f"Overall authenticity score: {overall_score}/100. {confidence_level}"
        
        return {
            "overall_score": overall_score,
            "confidence_level": confidence_level,
            "summary": summary,
            "component_scores": {
                "metadata": metadata_score,
                "visual_analysis": vision_score,
                "technical": technical_score
            }
        }
        
    except Exception as e:
        return {
            "overall_score": 50,
            "confidence_level": "Analysis incomplete",
            "summary": f"Error calculating authenticity: {str(e)}",
            "component_scores": {
                "metadata": 50,
                "visual_analysis": 50, 
                "technical": 50
            }
        }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
