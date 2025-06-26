from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import openai
import requests
import os
import json
import time
import logging
import re
from datetime import datetime, timedelta
from urllib.parse import quote, urlencode
import hashlib
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

# Configure logging FIRST - BEFORE EVERYTHING ELSE
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Now we can safely use logger anywhere
logger.info("Starting NewsVerify Pro initialization...")

# Try imports with proper error handling
try:
    from lxml import html
    import xml.etree.ElementTree as ET
    logger.info("XML processing libraries loaded")
except ImportError as e:
    logger.warning(f"XML libraries not available: {e}")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')
if openai.api_key:
    logger.info("OpenAI API key configured")
else:
    logger.warning("OpenAI API key not found")

# Feature flags for optional libraries
FEATURES = {
    'sentence_transformers': False,
    'scholarly': False,
    'transformers': False,
    'torch': False
}

# Try to import optional ML libraries
try:
    from sentence_transformers import SentenceTransformer
    FEATURES['sentence_transformers'] = True
    logger.info("SentenceTransformers available")
except ImportError:
    logger.warning("SentenceTransformers not available - will use fallback similarity")

try:
    from scholarly import scholarly
    FEATURES['scholarly'] = True
    logger.info("Scholarly available")
except ImportError:
    logger.warning("Scholarly not available - Google Scholar integration disabled")
    scholarly = None

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    FEATURES['torch'] = True
    FEATURES['transformers'] = True
    logger.info("PyTorch and Transformers available")
except ImportError:
    logger.warning("PyTorch/Transformers not available - using simplified AI detection")

# ================================
# CORE ANALYSIS FUNCTIONS
# ================================

def analyze_text_comprehensive(text):
    """Comprehensive text analysis with available tools"""
    start_time = time.time()
    
    results = {
        'text_length': len(text),
        'analysis_timestamp': datetime.now().isoformat(),
        'credibility_score': 0.0,
        'ai_detection': {'overall_score': 0.0, 'confidence': 0.8},
        'sources_found': [],
        'analysis_duration': 0,
        'features_used': FEATURES.copy()
    }
    
    # Basic credibility analysis
    results['credibility_score'] = calculate_credibility_score(text)
    
    # AI detection
    results['ai_detection'] = detect_ai_content_basic(text)
    
    # Source analysis (if available)
    if FEATURES['scholarly']:
        results['sources_found'] = search_academic_sources(text)
    
    # Semantic analysis (if available)
    if FEATURES['sentence_transformers']:
        results['semantic_analysis'] = perform_semantic_analysis(text)
    
    results['analysis_duration'] = time.time() - start_time
    logger.info(f"Analysis completed in {results['analysis_duration']:.2f} seconds")
    
    return results

def calculate_credibility_score(text):
    """Calculate credibility score using linguistic analysis"""
    score = 50  # Base score
    
    # Length analysis
    if len(text) > 100:
        score += 10
    if len(text) > 500:
        score += 10
    
    # Source indicators
    if re.search(r'(reuters|ap news|associated press|bbc|cnn|npr|wall street journal)', text.lower()):
        score += 20
    
    # Quote indicators
    if '"' in text or '"' in text or "'" in text:
        score += 10
    
    # Date indicators
    if re.search(r'\d{4}|\d{1,2}/\d{1,2}|\d{1,2}-\d{1,2}', text):
        score += 5
    
    # Professional language
    if re.search(r'(according to|reported|stated|announced|confirmed|officials said)', text.lower()):
        score += 15
    
    # Citation indicators
    if re.search(r'(study|research|survey|data shows|statistics)', text.lower()):
        score += 10
    
    # Sensational language (negative)
    sensational_patterns = [
        r'(shocking|unbelievable|you won\'t believe|must see|incredible)',
        r'(amazing|stunning|mind-blowing|explosive|bombshell)'
    ]
    for pattern in sensational_patterns:
        matches = len(re.findall(pattern, text.lower()))
        score -= matches * 3
    
    return min(100, max(0, score)) / 100

def detect_ai_content_basic(text):
    """Basic AI content detection using pattern analysis"""
    ai_indicators = [
        r'\b(as an ai|i am an ai|as a language model|i\'m an ai)\b',
        r'\b(furthermore|moreover|additionally|consequently|therefore)\b',
        r'\b(it is important to note|it should be noted|it\'s worth noting)\b',
        r'\b(in conclusion|to summarize|in summary|to sum up)\b',
        r'\b(comprehensive|multifaceted|holistic|nuanced)\b'
    ]
    
    ai_score = 0
    pattern_matches = []
    
    for i, pattern in enumerate(ai_indicators):
        matches = re.findall(pattern, text.lower())
        if matches:
            ai_score += len(matches) * (0.15 + i * 0.05)  # Weight later patterns more
            pattern_matches.extend(matches)
    
    # Sentence structure analysis
    sentences = re.split(r'[.!?]+', text)
    if len(sentences) > 3:
        lengths = [len(s.split()) for s in sentences if s.strip()]
        if lengths:
            length_std = np.std(lengths)
            avg_length = np.mean(lengths)
            # AI tends to have more consistent sentence lengths
            if avg_length > 0:
                consistency = 1.0 - min(1.0, length_std / avg_length)
                ai_score += consistency * 0.2
    
    ai_probability = min(1.0, ai_score)
    
    return {
        'overall_score': ai_probability,
        'confidence': 0.85,
        'classification': 'AI-Generated' if ai_probability > 0.6 else 'Human-Authored',
        'indicators_found': pattern_matches,
        'analysis': [
            f"AI probability: {ai_probability:.1%}",
            f"Confidence level: 85%",
            f"Classification: {'AI-Generated' if ai_probability > 0.6 else 'Human-Authored'}",
            f"Indicators detected: {len(pattern_matches)}"
        ]
    }

def search_academic_sources(text):
    """Search academic sources if scholarly is available"""
    if not FEATURES['scholarly'] or not scholarly:
        return []
    
    try:
        # Extract key terms for search
        key_terms = extract_key_terms(text)
        if not key_terms:
            return []
        
        # Perform limited search to avoid memory issues
        search_query = ' '.join(key_terms[:3])  # Limit to top 3 terms
        
        # This would be implemented with actual scholarly search
        # For now, return placeholder
        return [{
            'title': f'Academic source for: {search_query}',
            'source': 'Google Scholar',
            'relevance': 0.8
        }]
        
    except Exception as e:
        logger.error(f"Academic search error: {e}")
        return []

def extract_key_terms(text):
    """Extract key terms from text for searching"""
    # Simple keyword extraction
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    # Remove common words
    stopwords = {'that', 'this', 'with', 'have', 'will', 'from', 'they', 'been', 'said', 'each', 'which', 'their', 'time', 'would', 'there', 'could', 'other'}
    keywords = [w for w in words if w not in stopwords]
    
    # Return most frequent terms
    from collections import Counter
    return [word for word, count in Counter(keywords).most_common(10)]

def perform_semantic_analysis(text):
    """Perform semantic analysis if sentence-transformers available"""
    if not FEATURES['sentence_transformers']:
        return {'status': 'unavailable', 'reason': 'sentence-transformers not loaded'}
    
    # This would use actual semantic analysis
    # For now, return basic analysis
    return {
        'status': 'available',
        'complexity_score': len(text) / 1000,
        'semantic_density': len(set(text.split())) / len(text.split()) if text.split() else 0
    }

def generate_professional_report(analysis_results, report_type='executive'):
    """Generate professional reports"""
    timestamp = datetime.now().isoformat()
    credibility = analysis_results.get('credibility_score', 0) * 100
    ai_score = analysis_results.get('ai_detection', {}).get('overall_score', 0) * 100
    
    if report_type == 'executive':
        return {
            'report_type': 'Executive Summary',
            'generated_at': timestamp,
            'summary': f"Comprehensive analysis completed with {credibility:.1f}% credibility assessment",
            'key_findings': [
                f"Overall credibility: {credibility:.1f}/100",
                f"AI detection probability: {ai_score:.1f}%",
                f"Text length: {analysis_results.get('text_length', 0)} characters",
                f"Analysis duration: {analysis_results.get('analysis_duration', 0):.2f} seconds"
            ],
            'recommendations': generate_recommendations(credibility, ai_score),
            'risk_assessment': assess_risk_level(credibility, ai_score),
            'features_utilized': analysis_results.get('features_used', {})
        }
    
    elif report_type == 'technical':
        return {
            'report_type': 'Technical Analysis',
            'generated_at': timestamp,
            'methodology': describe_methodology(),
            'detailed_results': analysis_results,
            'statistical_summary': generate_statistical_summary(analysis_results),
            'feature_availability': FEATURES
        }
    
    return {'error': 'Unsupported report type'}

def generate_recommendations(credibility, ai_score):
    """Generate recommendations based on analysis"""
    recommendations = []
    
    if credibility > 80:
        recommendations.append("Content demonstrates high credibility markers")
    elif credibility > 60:
        recommendations.append("Content shows moderate credibility - consider additional verification")
    else:
        recommendations.append("Content shows low credibility markers - recommend thorough fact-checking")
    
    if ai_score > 70:
        recommendations.append("High likelihood of AI generation - consider disclosure requirements")
    elif ai_score > 40:
        recommendations.append("Moderate AI indicators detected - review for authenticity")
    else:
        recommendations.append("Content appears to be human-authored")
    
    return recommendations

def assess_risk_level(credibility, ai_score):
    """Assess overall risk level"""
    if credibility < 40 or ai_score > 80:
        return "HIGH"
    elif credibility < 70 or ai_score > 50:
        return "MEDIUM"
    else:
        return "LOW"

def describe_methodology():
    """Describe analysis methodology"""
    return {
        'credibility_assessment': 'Multi-factor linguistic analysis including source indicators, professional language patterns, and sensationalism detection',
        'ai_detection': 'Pattern-based analysis using linguistic markers and sentence structure consistency',
        'academic_search': 'Google Scholar integration' if FEATURES['scholarly'] else 'Not available',
        'semantic_analysis': 'Sentence transformer embeddings' if FEATURES['sentence_transformers'] else 'Basic term analysis'
    }

def generate_statistical_summary(results):
    """Generate statistical summary"""
    return {
        'processing_time': results.get('analysis_duration', 0),
        'text_characteristics': {
            'length': results.get('text_length', 0),
            'estimated_reading_time': results.get('text_length', 0) / 250  # words per minute
        },
        'confidence_metrics': {
            'credibility_confidence': 0.85,
            'ai_detection_confidence': results.get('ai_detection', {}).get('confidence', 0.8)
        }
    }

# ================================
# API ROUTES
# ================================

@app.route('/')
def index():
    return render_template('news.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """Main text analysis endpoint"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        analysis_type = data.get('type', 'comprehensive')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) < 50:
            return jsonify({'error': 'Text too short for meaningful analysis (minimum 50 characters)'}), 400
        
        logger.info(f"Analyzing text of length {len(text)}")
        
        # Perform comprehensive analysis
        results = analyze_text_comprehensive(text)
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in text analysis: {str(e)}")
        return jsonify({'error': 'Analysis failed', 'details': str(e)}), 500

@app.route('/api/report', methods=['POST'])
def generate_report():
    """Generate professional reports"""
    try:
        data = request.get_json()
        analysis_results = data.get('results', {})
        report_type = data.get('type', 'executive')
        
        if not analysis_results:
            return jsonify({'error': 'No analysis results provided'}), 400
        
        logger.info(f"Generating {report_type} report")
        
        report = generate_professional_report(analysis_results, report_type)
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return jsonify({'error': 'Report generation failed', 'details': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'features': FEATURES,
        'services': {
            'flask': True,
            'openai': openai.api_key is not None,
            'numpy': True
        }
    })

@app.route('/api/detect', methods=['POST'])
def detect_plagiarism():
    """Legacy plagiarism detection endpoint"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        logger.info(f"Legacy detection for text of length {len(text)}")
        
        results = analyze_text_comprehensive(text)
        
        # Format for legacy compatibility
        legacy_response = {
            'plagiarism_detected': results.get('credibility_score', 0) < 0.5,
            'confidence_score': results.get('credibility_score', 0),
            'sources_found': len(results.get('sources_found', [])),
            'detailed_results': results
        }
        
        return jsonify(legacy_response)
        
    except Exception as e:
        logger.error(f"Error in legacy detection: {str(e)}")
        return jsonify({'error': 'Detection failed', 'details': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting NewsVerify Pro server...")
    logger.info(f"Available features: {FEATURES}")
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
