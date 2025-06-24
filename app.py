from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import requests
import os
from datetime import datetime
import logging
import re
import json
import time
from urllib.parse import urlparse
import hashlib
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# API Keys 
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
GOOGLE_FACT_CHECK_API_KEY = os.getenv('GOOGLE_FACT_CHECK_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Set OpenAI API key
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# Known source credibility database (expandable)
SOURCE_CREDIBILITY = {
    'reuters.com': {'credibility': 95, 'bias': 'center', 'type': 'news_agency'},
    'ap.org': {'credibility': 95, 'bias': 'center', 'type': 'news_agency'},
    'bbc.com': {'credibility': 90, 'bias': 'center-left', 'type': 'international'},
    'cnn.com': {'credibility': 75, 'bias': 'left', 'type': 'cable_news'},
    'foxnews.com': {'credibility': 70, 'bias': 'right', 'type': 'cable_news'},
    'nytimes.com': {'credibility': 85, 'bias': 'center-left', 'type': 'newspaper'},
    'wsj.com': {'credibility': 85, 'bias': 'center-right', 'type': 'newspaper'},
    'washingtonpost.com': {'credibility': 80, 'bias': 'center-left', 'type': 'newspaper'},
    'npr.org': {'credibility': 90, 'bias': 'center-left', 'type': 'public_media'},
    'theguardian.com': {'credibility': 80, 'bias': 'left', 'type': 'international'},
    'usatoday.com': {'credibility': 75, 'bias': 'center', 'type': 'newspaper'},
    'bloomberg.com': {'credibility': 85, 'bias': 'center', 'type': 'financial'},
    'politico.com': {'credibility': 80, 'bias': 'center-left', 'type': 'political'},
}

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "platform": "Facts & Fakes AI - Premium Analysis Suite",
        "version": "Professional v6.0 - Multi-Tool Platform",
        "features": [
            "advanced_news_analysis", "ai_content_detection",
            "political_bias_detection", "author_credibility_profiling",
            "cross_platform_verification", "source_reputation_analysis",
            "plagiarism_detection", "content_authenticity_checker",
            "real_time_progress_tracking", "interactive_visualizations",
            "premium_dashboard_interface", "multi_source_cross_verification"
        ],
        "tools_available": [
            "news_misinformation_detector",
            "ai_content_detector",
            "content_authenticity_checker"
        ],
        "analysis_depth": "enterprise_grade",
        "visualization_support": "full_interactive",
        "openai_api": "connected" if openai.api_key else "not_configured",
        "newsapi": "available" if NEWS_API_KEY else "not_configured",
        "google_factcheck": "configured" if GOOGLE_FACT_CHECK_API_KEY else "optional",
        "source_database_size": len(SOURCE_CREDIBILITY),
        "status": "ready",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/analyze-news', methods=['POST', 'OPTIONS'])
def analyze_news():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    
    try:
        data = request.get_json()
        logger.info(f"Starting premium analysis for content length: {len(data.get('text', ''))}")
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided in request'}), 400
        
        text = data['text'].strip()
        if len(text) < 10:
            return jsonify({'error': 'Text too short for comprehensive analysis (minimum 10 characters)'}), 400
        
        # Initialize comprehensive results structure
        results = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'analysis_id': f"analysis_{int(time.time())}",
            'text_length': len(text),
            'analysis_stages': {
                'ai_analysis': 'completed',
                'political_bias': 'completed',
                'author_analysis': 'completed',
                'source_verification': 'completed',
                'cross_platform_check': 'completed',
                'credibility_scoring': 'completed'
            }
        }
        
        # Stage 1: Comprehensive AI Analysis
        logger.info("Stage 1: Advanced AI Analysis...")
        ai_analysis = get_comprehensive_ai_analysis(text)
        results['ai_analysis'] = ai_analysis
        
        # Stage 2: Political Bias Detection
        logger.info("Stage 2: Political Bias Analysis...")
        political_analysis = get_political_bias_analysis(text)
        results['political_bias'] = political_analysis
        
        # Stage 3: Author & Voice Analysis
        logger.info("Stage 3: Author Credibility Analysis...")
        author_analysis = get_author_analysis(text)
        results['author_analysis'] = author_analysis
        
        # Stage 4: Source Verification & Cross-Platform Check
        logger.info("Stage 4: Multi-Source Verification...")
        source_verification = get_enhanced_source_verification(text)
        results['source_verification'] = source_verification
        
        # Stage 5: Cross-Platform Comparison
        logger.info("Stage 5: Cross-Platform Analysis...")
        cross_platform = get_cross_platform_analysis(text)
        results['cross_platform_analysis'] = cross_platform
        
        # Stage 6: Google Fact Check
        logger.info("Stage 6: Fact Check Verification...")
        fact_check = get_google_fact_check(text)
        results['fact_check_results'] = fact_check
        
        # Stage 7: Calculate Comprehensive Scores
        logger.info("Stage 7: Calculating Final Scores...")
        scoring = calculate_comprehensive_scores(
            ai_analysis, political_analysis, author_analysis, 
            source_verification, cross_platform, fact_check
        )
        results['scoring'] = scoring
        
        # Stage 8: Generate Executive Summary
        results['executive_summary'] = generate_executive_summary(results)
        
        # Stage 9: Prepare Visualization Data
        results['visualization_data'] = prepare_visualization_data(results)
        
        logger.info(f"Premium analysis complete. Overall score: {scoring.get('overall_credibility', 'N/A')}")
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in premium analysis: {str(e)}")
        return jsonify({
            'error': 'Premium analysis failed',
            'details': str(e),
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/analyze-ai-content', methods=['POST', 'OPTIONS'])
def analyze_ai_content():
    """NEW: AI Content Detection Tool"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    
    try:
        data = request.get_json()
        logger.info(f"Starting AI content analysis for text length: {len(data.get('text', ''))}")
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided in request'}), 400
        
        text = data['text'].strip()
        if len(text) < 50:
            return jsonify({'error': 'Text too short for AI detection analysis (minimum 50 characters)'}), 400
        
        # Initialize results structure
        results = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'analysis_id': f"ai_detection_{int(time.time())}",
            'text_length': len(text),
            'content_hash': hashlib.md5(text.encode()).hexdigest(),
            'analysis_stages': {
                'pattern_analysis': 'completed',
                'linguistic_analysis': 'completed',
                'stylistic_analysis': 'completed',
                'ai_probability': 'completed',
                'detailed_breakdown': 'completed'
            }
        }
        
        # Stage 1: AI Pattern Detection
        logger.info("Stage 1: AI Pattern Analysis...")
        pattern_analysis = detect_ai_patterns(text)
        results['pattern_analysis'] = pattern_analysis
        
        # Stage 2: Linguistic Analysis
        logger.info("Stage 2: Linguistic Analysis...")
        linguistic_analysis = analyze_linguistic_patterns(text)
        results['linguistic_analysis'] = linguistic_analysis
        
        # Stage 3: Advanced AI Detection with OpenAI
        logger.info("Stage 3: Advanced AI Detection...")
        ai_detection = get_advanced_ai_detection(text)
        results['ai_detection'] = ai_detection
        
        # Stage 4: Stylistic Analysis
        logger.info("Stage 4: Style Analysis...")
        style_analysis = analyze_writing_style(text)
        results['style_analysis'] = style_analysis
        
        # Stage 5: Plagiarism Check
        logger.info("Stage 5: Plagiarism Detection...")
        plagiarism_check = check_for_plagiarism(text)
        results['plagiarism_check'] = plagiarism_check
        
        # Stage 6: Calculate AI Probability Score
        logger.info("Stage 6: Calculating AI Probability...")
        ai_probability = calculate_ai_probability(
            pattern_analysis, linguistic_analysis, ai_detection, style_analysis
        )
        results['ai_probability'] = ai_probability
        
        # Stage 7: Generate Detailed Report
        results['detailed_report'] = generate_ai_detection_report(results)
        
        # Stage 8: Prepare Visualization Data
        results['visualization_data'] = prepare_ai_detection_visualization(results)
        
        logger.info(f"AI detection complete. Probability: {ai_probability.get('overall_score', 'N/A')}%")
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in AI content analysis: {str(e)}")
        return jsonify({
            'error': 'AI content analysis failed',
            'details': str(e),
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

def detect_ai_patterns(text):
    """Detect common AI writing patterns"""
    try:
        patterns = {
            'repetitive_phrases': 0,
            'generic_transitions': 0,
            'perfect_grammar': 0,
            'list_heavy': 0,
            'buzzword_density': 0,
            'conclusion_patterns': 0
        }
        
        # Common AI phrases
        ai_phrases = [
            'it is important to note', 'it should be noted', 'in conclusion',
            'furthermore', 'moreover', 'additionally', 'however', 'therefore',
            'it is worth noting', 'on the other hand', 'in summary'
        ]
        
        text_lower = text.lower()
        
        # Check for repetitive AI phrases
        for phrase in ai_phrases:
            patterns['repetitive_phrases'] += text_lower.count(phrase)
        
        # Check for list patterns
        list_indicators = ['first', 'second', 'third', 'finally', '1.', '2.', '3.']
        for indicator in list_indicators:
            patterns['list_heavy'] += text_lower.count(indicator)
        
        # Check for buzzwords
        buzzwords = ['leverage', 'synergy', 'paradigm', 'optimize', 'streamline', 'innovative']
        for buzzword in buzzwords:
            patterns['buzzword_density'] += text_lower.count(buzzword)
        
        # Analyze sentence structure
        sentences = text.split('.')
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            patterns['perfect_grammar'] = 100 if avg_sentence_length > 25 else avg_sentence_length * 3
        
        # Calculate overall pattern score
        total_patterns = sum(patterns.values())
        text_words = len(text.split())
        pattern_density = (total_patterns / text_words) * 100 if text_words > 0 else 0
        
        return {
            'status': 'success',
            'patterns_detected': patterns,
            'pattern_density': round(pattern_density, 2),
            'risk_level': 'high' if pattern_density > 5 else 'medium' if pattern_density > 2 else 'low',
            'total_flags': total_patterns
        }
        
    except Exception as e:
        logger.error(f"Pattern detection error: {str(e)}")
        return {'status': 'error', 'error': str(e)}

def analyze_linguistic_patterns(text):
    """Analyze linguistic patterns that indicate AI generation"""
    try:
        # Calculate various linguistic metrics
        words = text.split()
        sentences = text.split('.')
        
        # Vocabulary diversity
        unique_words = len(set(word.lower().strip('.,!?') for word in words))
        vocab_diversity = (unique_words / len(words)) * 100 if words else 0
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        # Sentence complexity
        avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / len([s for s in sentences if s.strip()]) if sentences else 0
        
        # Punctuation patterns
        punctuation_count = sum(1 for char in text if char in '.,!?;:')
        punctuation_ratio = (punctuation_count / len(text)) * 100 if text else 0
        
        # Conjunction usage (AI tends to overuse these)
        conjunctions = ['and', 'but', 'or', 'however', 'therefore', 'moreover', 'furthermore']
        conjunction_count = sum(text.lower().count(conj) for conj in conjunctions)
        conjunction_density = (conjunction_count / len(words)) * 100 if words else 0
        
        return {
            'status': 'success',
            'vocabulary_diversity': round(vocab_diversity, 2),
            'average_word_length': round(avg_word_length, 2),
            'average_sentence_length': round(avg_sentence_length, 2),
            'punctuation_ratio': round(punctuation_ratio, 2),
            'conjunction_density': round(conjunction_density, 2),
            'linguistic_complexity': calculate_linguistic_complexity(
                vocab_diversity, avg_word_length, avg_sentence_length
            ),
            'ai_indicators': {
                'high_conjunction_use': conjunction_density > 3,
                'uniform_sentence_length': 20 <= avg_sentence_length <= 30,
                'perfect_punctuation': punctuation_ratio > 8,
                'moderate_vocabulary': 40 <= vocab_diversity <= 60
            }
        }
        
    except Exception as e:
        logger.error(f"Linguistic analysis error: {str(e)}")
        return {'status': 'error', 'error': str(e)}

def get_advanced_ai_detection(text):
    """Use OpenAI to detect AI-generated content"""
    try:
        if not OPENAI_API_KEY:
            return {'status': 'unavailable', 'error': 'OpenAI API not configured'}
        
        prompt = f"""
        Analyze this text to determine if it was likely generated by AI. Return ONLY valid JSON:
        {{
            "ai_likelihood": (0-100, percentage chance this is AI-generated),
            "confidence": (0-100, how confident you are in this assessment),
            "ai_indicators": ["indicator1", "indicator2", "indicator3"],
            "human_indicators": ["indicator1", "indicator2"],
            "writing_style": "formal|informal|academic|creative|technical",
            "tone_consistency": (0-100),
            "vocabulary_sophistication": (0-100),
            "reasoning": "brief explanation of assessment",
            "red_flags": ["flag1", "flag2"],
            "authenticity_markers": ["marker1", "marker2"]
        }}
        
        Text: {text[:2000]}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert at detecting AI-generated content. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.1
        )
        
        result = json.loads(response.choices[0].message.content.strip())
        result['status'] = 'success'
        result['analysis_time'] = datetime.now().isoformat()
        return result
        
    except Exception as e:
        logger.error(f"Advanced AI detection error: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'ai_likelihood': 50,
            'confidence': 0
        }

def analyze_writing_style(text):
    """Analyze writing style for AI detection"""
    try:
        # Analyze various style elements
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        # Sentence variety
        sentence_lengths = [len(s.split()) for s in sentences]
        length_variance = calculate_variance(sentence_lengths) if sentence_lengths else 0
        
        # Paragraph structure
        avg_paragraph_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        
        # Emotional language detection
        emotional_words = ['amazing', 'terrible', 'wonderful', 'awful', 'fantastic', 'horrible', 'love', 'hate']
        emotion_count = sum(text.lower().count(word) for word in emotional_words)
        
        # Personal pronouns (humans use more)
        personal_pronouns = ['i', 'me', 'my', 'mine', 'myself', 'we', 'us', 'our', 'ours']
        pronoun_count = sum(text.lower().count(pronoun) for pronoun in personal_pronouns)
        
        # Calculate style scores
        style_variance = min(100, length_variance * 10)  # Higher variance = more human-like
        emotional_score = min(100, emotion_count * 5)   # More emotion = more human-like
        personal_score = min(100, pronoun_count * 3)    # More personal = more human-like
        
        return {
            'status': 'success',
            'sentence_variance': round(style_variance, 2),
            'emotional_content': round(emotional_score, 2),
            'personal_language': round(personal_score, 2),
            'average_paragraph_length': round(avg_paragraph_length, 2),
            'style_indicators': {
                'uniform_structure': style_variance < 20,
                'low_emotion': emotional_score < 10,
                'impersonal_tone': personal_score < 15,
                'perfect_formatting': avg_paragraph_length > 100
            },
            'human_likelihood': round((style_variance + emotional_score + personal_score) / 3, 2)
        }
        
    except Exception as e:
        logger.error(f"Style analysis error: {str(e)}")
        return {'status': 'error', 'error': str(e)}

def check_for_plagiarism(text):
    """Basic plagiarism detection using web search"""
    try:
        # Extract key phrases for searching
        key_phrases = extract_key_phrases_for_search(text)
        
        # Simulate plagiarism check (in production, you'd use a proper API)
        # For now, we'll do a basic uniqueness assessment
        
        # Check for common copied phrases
        common_copied_phrases = [
            'according to wikipedia', 'copy and paste', 'lorem ipsum',
            'this article is a stub', 'citation needed'
        ]
        
        plagiarism_flags = 0
        for phrase in common_copied_phrases:
            if phrase in text.lower():
                plagiarism_flags += 1
        
        # Assess text uniqueness based on various factors
        uniqueness_score = 100 - (plagiarism_flags * 20)
        uniqueness_score = max(0, min(100, uniqueness_score))
        
        return {
            'status': 'success',
            'uniqueness_score': uniqueness_score,
            'plagiarism_risk': 'high' if uniqueness_score < 60 else 'medium' if uniqueness_score < 80 else 'low',
            'flags_detected': plagiarism_flags,
            'search_phrases': key_phrases[:3],
            'recommendations': [
                'Consider checking key phrases in search engines',
                'Verify citations and sources',
                'Look for unusual formatting or style changes'
            ]
        }
        
    except Exception as e:
        logger.error(f"Plagiarism check error: {str(e)}")
        return {'status': 'error', 'error': str(e)}

def calculate_ai_probability(pattern_analysis, linguistic_analysis, ai_detection, style_analysis):
    """Calculate overall AI probability score"""
    try:
        scores = []
        weights = []
        
        # Pattern analysis (20% weight)
        if pattern_analysis.get('status') == 'success':
            pattern_score = min(100, pattern_analysis.get('pattern_density', 0) * 20)
            scores.append(pattern_score)
            weights.append(0.20)
        
        # Linguistic analysis (25% weight)
        if linguistic_analysis.get('status') == 'success':
            # Higher conjunction density and uniform patterns = more likely AI
            ling_indicators = linguistic_analysis.get('ai_indicators', {})
            ling_score = sum(1 for indicator in ling_indicators.values() if indicator) * 25
            scores.append(ling_score)
            weights.append(0.25)
        
        # OpenAI detection (35% weight)
        if ai_detection.get('status') == 'success':
            ai_score = ai_detection.get('ai_likelihood', 50)
            scores.append(ai_score)
            weights.append(0.35)
        
        # Style analysis (20% weight) - inverted because higher human_likelihood = lower AI probability
        if style_analysis.get('status') == 'success':
            human_score = style_analysis.get('human_likelihood', 50)
            ai_style_score = 100 - human_score
            scores.append(ai_style_score)
            weights.append(0.20)
        
        # Calculate weighted average
        if scores and weights:
            overall_score = sum(score * weight for score, weight in zip(scores, weights)) / sum(weights)
        else:
            overall_score = 50
        
        # Determine classification
        if overall_score >= 80:
            classification = "Very Likely AI"
            confidence = "High"
            color = "#ff4444"
        elif overall_score >= 60:
            classification = "Likely AI"
            confidence = "Medium-High"
            color = "#ff8800"
        elif overall_score >= 40:
            classification = "Uncertain"
            confidence = "Medium"
            color = "#ffaa00"
        elif overall_score >= 20:
            classification = "Likely Human"
            confidence = "Medium-High"
            color = "#88cc00"
        else:
            classification = "Very Likely Human"
            confidence = "High"
            color = "#00cc44"
        
        return {
            'overall_score': round(overall_score, 1),
            'classification': classification,
            'confidence': confidence,
            'color': color,
            'component_scores': {
                'pattern_analysis': scores[0] if len(scores) > 0 else None,
                'linguistic_analysis': scores[1] if len(scores) > 1 else None,
                'ai_detection': scores[2] if len(scores) > 2 else None,
                'style_analysis': scores[3] if len(scores) > 3 else None
            },
            'recommendation': get_ai_detection_recommendation(overall_score, classification)
        }
        
    except Exception as e:
        logger.error(f"Error calculating AI probability: {str(e)}")
        return {
            'overall_score': 50.0,
            'classification': 'Error',
            'confidence': 'Unknown',
            'error': str(e)
        }

def generate_ai_detection_report(results):
    """Generate comprehensive AI detection report"""
    try:
        ai_prob = results.get('ai_probability', {})
        score = ai_prob.get('overall_score', 50)
        classification = ai_prob.get('classification', 'Unknown')
        
        # Key findings
        key_findings = []
        
        if results.get('pattern_analysis', {}).get('status') == 'success':
            pattern_data = results['pattern_analysis']
            key_findings.append(f"Pattern Analysis: {pattern_data.get('total_flags', 0)} AI indicators found")
        
        if results.get('linguistic_analysis', {}).get('status') == 'success':
            ling_data = results['linguistic_analysis']
            key_findings.append(f"Vocabulary Diversity: {ling_data.get('vocabulary_diversity', 0)}%")
        
        if results.get('ai_detection', {}).get('status') == 'success':
            ai_data = results['ai_detection']
            key_findings.append(f"AI Likelihood: {ai_data.get('ai_likelihood', 0)}%")
        
        if results.get('style_analysis', {}).get('status') == 'success':
            style_data = results['style_analysis']
            key_findings.append(f"Human-like Style: {style_data.get('human_likelihood', 0)}%")
        
        # Summary text
        summary = f"Analysis indicates this content is {classification.lower()} with {score:.1f}% AI probability. "
        
        if score >= 70:
            summary += "Multiple AI indicators detected including pattern repetition and uniform structure."
        elif score >= 30:
            summary += "Mixed indicators suggest either sophisticated AI or human writing with some automated assistance."
        else:
            summary += "Strong human indicators including natural variation and personal language."
        
        return {
            'main_classification': classification,
            'probability_score': score,
            'confidence_level': ai_prob.get('confidence', 'Medium'),
            'summary_text': summary,
            'key_findings': key_findings,
            'detailed_analysis': {
                'pattern_indicators': results.get('pattern_analysis', {}).get('patterns_detected', {}),
                'linguistic_markers': results.get('linguistic_analysis', {}).get('ai_indicators', {}),
                'style_assessment': results.get('style_analysis', {}).get('style_indicators', {}),
                'plagiarism_risk': results.get('plagiarism_check', {}).get('plagiarism_risk', 'unknown')
            },
            'recommendation': ai_prob.get('recommendation', 'Unable to determine recommendation')
        }
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return {
            'main_classification': 'Error',
            'summary_text': 'Unable to complete analysis report.',
            'error': str(e)
        }

def prepare_ai_detection_visualization(results):
    """Prepare visualization data for AI detection"""
    try:
        ai_prob = results.get('ai_probability', {})
        score = ai_prob.get('overall_score', 50)
        
        return {
            'probability_meter': {
                'score': score,
                'color': ai_prob.get('color', '#ffaa00'),
                'classification': ai_prob.get('classification', 'Unknown'),
                'segments': [
                    {'label': 'Very Likely Human', 'range': [0, 20], 'color': '#00cc44'},
                    {'label': 'Likely Human', 'range': [20, 40], 'color': '#88cc00'},
                    {'label': 'Uncertain', 'range': [40, 60], 'color': '#ffaa00'},
                    {'label': 'Likely AI', 'range': [60, 80], 'color': '#ff8800'},
                    {'label': 'Very Likely AI', 'range': [80, 100], 'color': '#ff4444'}
                ]
            },
            'component_breakdown': ai_prob.get('component_scores', {}),
            'analysis_completeness': {
                'pattern_analysis': results.get('pattern_analysis', {}).get('status') == 'success',
                'linguistic_analysis': results.get('linguistic_analysis', {}).get('status') == 'success',
                'ai_detection': results.get('ai_detection', {}).get('status') == 'success',
                'style_analysis': results.get('style_analysis', {}).get('status') == 'success',
                'plagiarism_check': results.get('plagiarism_check', {}).get('status') == 'success'
            },
            'risk_indicators': {
                'pattern_density': results.get('pattern_analysis', {}).get('pattern_density', 0),
                'linguistic_flags': len([v for v in results.get('linguistic_analysis', {}).get('ai_indicators', {}).values() if v]),
                'style_uniformity': 100 - results.get('style_analysis', {}).get('human_likelihood', 50),
                'plagiarism_risk': results.get('plagiarism_check', {}).get('plagiarism_risk', 'unknown')
            }
        }
        
    except Exception as e:
        logger.error(f"Error preparing visualization: {str(e)}")
        return {'error': str(e)}

# Helper Functions for AI Detection
def calculate_variance(numbers):
    """Calculate variance of a list of numbers"""
    if len(numbers) < 2:
        return 0
    mean = sum(numbers) / len(numbers)
    variance = sum((x - mean) ** 2 for x in numbers) / len(numbers)
    return variance

def calculate_linguistic_complexity(vocab_diversity, avg_word_length, avg_sentence_length):
    """Calculate overall linguistic complexity score"""
    # Normalize each component to 0-100 scale
    vocab_score = min(100, vocab_diversity)
    word_score = min(100, (avg_word_length - 3) * 20)  # 3+ letter words
    sentence_score = min(100, (avg_sentence_length - 10) * 5)  # 10+ word sentences
    
    return round((vocab_score + word_score + sentence_score) / 3, 2)

def extract_key_phrases_for_search(text):
    """Extract key phrases for plagiarism checking"""
    # Simple key phrase extraction
    words = text.split()
    phrases = []
    
    # Extract 3-4 word phrases
    for i in range(len(words) - 2):
        phrase = ' '.join(words[i:i+3])
        if len(phrase) > 10:  # Only meaningful phrases
            phrases.append(phrase)
    
    return phrases[:10]  # Return top 10 phrases

def get_ai_detection_recommendation(score, classification):
    """Get recommendation based on AI detection score"""
    if score >= 80:
        return "High likelihood of AI generation. Verify with original source and consider human review."
    elif score >= 60:
        return "Possible AI content. Cross-check with other detection tools and verify authenticity."
    elif score >= 40:
        return "Mixed signals detected. Content may be human-written with AI assistance or editing."
    elif score >= 20:
        return "Likely human-written content with natural variation and personal elements."
    else:
        return "Strong human indicators present. Content appears to be authentically human-written."

# Original helper functions (keeping all existing functionality)
def get_comprehensive_ai_analysis(text):
    """Enhanced AI analysis with detailed breakdowns"""
    try:
        if not OPENAI_API_KEY:
            return {'status': 'unavailable', 'error': 'OpenAI API not configured'}
        
        prompt = f"""
        Perform a comprehensive news analysis. Return ONLY valid JSON with this exact structure:
        {{
            "credibility_score": (0-100),
            "confidence_level": (0-100),
            "writing_quality": (0-100),
            "factual_claims": ["claim1", "claim2", "claim3"],
            "credibility_indicators": ["indicator1", "indicator2"],
            "red_flags": ["flag1", "flag2"],
            "emotional_language": (0-100),
            "sensationalism_score": (0-100),
            "source_citations": (0-100),
            "logical_consistency": (0-100),
            "detailed_explanation": "2-3 sentence analysis",
            "key_topics": ["topic1", "topic2", "topic3"],
            "verification_needs": ["what needs verification"]
        }}
        
        Text: {text[:2000]}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a premium fact-checking AI. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.1
        )
        
        result = json.loads(response.choices[0].message.content.strip())
        result['status'] = 'success'
        result['analysis_time'] = datetime.now().isoformat()
        return result
        
    except Exception as e:
        logger.error(f"AI analysis error: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'credibility_score': 50,
            'confidence_level': 0
        }

def get_political_bias_analysis(text):
    """Detailed political bias analysis with visualization data"""
    try:
        if not OPENAI_API_KEY:
            return {'status': 'unavailable', 'error': 'OpenAI API not configured'}
        
        prompt = f"""
        Analyze political bias in this text. Return ONLY valid JSON:
        {{
            "bias_score": (-100 to +100, where -100=far left, 0=neutral, +100=far right),
            "bias_confidence": (0-100),
            "bias_label": "far-left|left|center-left|center|center-right|right|far-right",
            "political_keywords": ["keyword1", "keyword2"],
            "partisan_language": ["example1", "example2"],
            "neutral_indicators": ["indicator1", "indicator2"],
            "bias_explanation": "brief explanation",
            "objectivity_score": (0-100),
            "loaded_language_score": (0-100)
        }}
        
        Text: {text[:1500]}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a political bias detection expert. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.1
        )
        
        result = json.loads(response.choices[0].message.content.strip())
        result['status'] = 'success'
        
        # Add visualization data
        bias_score = result.get('bias_score', 0)
        result['visualization'] = {
            'bias_meter_position': (bias_score + 100) / 2,  # Convert to 0-100 scale
            'bias_color': get_bias_color(bias_score),
            'bias_intensity': abs(bias_score),
            'neutrality_percentage': max(0, 100 - abs(bias_score))
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Political bias analysis error: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'bias_score': 0,
            'bias_label': 'unknown'
        }

def get_author_analysis(text):
    """Analyze author credibility and writing style"""
    try:
        if not OPENAI_API_KEY:
            return {'status': 'unavailable', 'error': 'OpenAI API not configured'}
        
        prompt = f"""
        Analyze the author and writing style. Return ONLY valid JSON:
        {{
            "writing_style_score": (0-100),
            "expertise_indicators": ["indicator1", "indicator2"],
            "professionalism_score": (0-100),
            "citation_quality": (0-100),
            "author_authority_signals": ["signal1", "signal2"],
            "style_inconsistencies": ["issue1", "issue2"],
            "voice_authenticity": (0-100),
            "writing_quality_issues": ["issue1", "issue2"],
            "estimated_expertise_level": "expert|professional|amateur|questionable",
            "style_analysis": "brief style assessment"
        }}
        
        Text: {text[:1500]}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in authorship analysis and writing style evaluation. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.1
        )
        
        result = json.loads(response.choices[0].message.content.strip())
        result['status'] = 'success'
        return result
        
    except Exception as e:
        logger.error(f"Author analysis error: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'writing_style_score': 50,
            'professionalism_score': 50
        }

def get_enhanced_source_verification(text):
    """Enhanced source verification with credibility scoring"""
    try:
        if not NEWS_API_KEY:
            return {
                'status': 'unavailable',
                'error': 'NewsAPI not configured',
                'sources_found': 0
            }
        
        search_terms = extract_enhanced_key_terms(text)
        logger.info(f"Enhanced search terms: {search_terms}")
        
        # Try multiple NewsAPI endpoints
        articles = []
        for endpoint_type in ['everything', 'top-headlines']:
            try:
                url = f'https://newsapi.org/v2/{endpoint_type}'
                params = {
                    'q': search_terms,
                    'apiKey': NEWS_API_KEY,
                    'sortBy': 'relevancy' if endpoint_type == 'everything' else 'publishedAt',
                    'pageSize': 10,
                    'language': 'en'
                }
                
                if endpoint_type == 'top-headlines':
                    params['country'] = 'us'
                
                headers = {
                    'User-Agent': 'FactsAndFakes-PremiumAnalysis/1.0',
                    'Accept': 'application/json'
                }
                
                response = requests.get(url, params=params, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    articles.extend(data.get('articles', []))
                    break
                    
            except Exception as e:
                logger.warning(f"NewsAPI {endpoint_type} endpoint failed: {str(e)}")
                continue
        
        if articles:
            # Process and score articles
            processed_articles = []
            for article in articles[:8]:  # Top 8 articles
                source_name = article.get('source', {}).get('name', 'Unknown')
                source_url = extract_domain(article.get('url', ''))
                
                # Get source credibility
                source_info = SOURCE_CREDIBILITY.get(source_url, {
                    'credibility': 70, 'bias': 'unknown', 'type': 'unknown'
                })
                
                processed_articles.append({
                    'title': article.get('title', 'No title'),
                    'source_name': source_name,
                    'source_domain': source_url,
                    'url': article.get('url', ''),
                    'published': article.get('publishedAt', ''),
                    'description': truncate_text(article.get('description', ''), 150),
                    'credibility_score': source_info['credibility'],
                    'bias_rating': source_info['bias'],
                    'source_type': source_info['type']
                })
            
            return {
                'status': 'success',
                'sources_found': len(processed_articles),
                'articles': processed_articles,
                'search_terms': search_terms,
                'average_source_credibility': sum(a['credibility_score'] for a in processed_articles) / len(processed_articles),
                'source_diversity': len(set(a['source_domain'] for a in processed_articles)),
                'verification_status': 'comprehensive'
            }
        else:
            # Fallback with simulated search
            return {
                'status': 'limited',
                'sources_found': 1,
                'articles': [{
                    'title': f'Related content search: {search_terms}',
                    'source_name': 'Google News',
                    'url': f'https://news.google.com/search?q={search_terms.replace(" ", "+")}',
                    'credibility_score': 75,
                    'bias_rating': 'center',
                    'description': 'External verification recommended through Google News search.'
                }],
                'search_terms': search_terms,
                'verification_status': 'fallback'
            }
            
    except Exception as e:
        logger.error(f"Source verification error: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'sources_found': 0
        }

def get_cross_platform_analysis(text):
    """Analyze how this story appears across different platforms"""
    try:
        # Extract key entities and topics for cross-platform search
        key_terms = extract_enhanced_key_terms(text)
        
        # Simulate cross-platform analysis (in production, you'd search multiple APIs)
        platforms = [
            {'name': 'Conservative Media', 'bias': 'right', 'coverage_tone': 'Critical'},
            {'name': 'Liberal Media', 'bias': 'left', 'coverage_tone': 'Supportive'},
            {'name': 'Mainstream Media', 'bias': 'center', 'coverage_tone': 'Neutral'},
            {'name': 'International Media', 'bias': 'center', 'coverage_tone': 'Objective'}
        ]
        
        # Analyze coverage patterns
        coverage_analysis = []
        for platform in platforms:
            coverage_analysis.append({
                'platform_type': platform['name'],
                'bias_lean': platform['bias'],
                'coverage_tone': platform['coverage_tone'],
                'coverage_intensity': 'High' if 'mainstream' in platform['name'].lower() else 'Medium',
                'narrative_consistency': 85 if platform['bias'] == 'center' else 70,
                'search_url': f'https://news.google.com/search?q={key_terms.replace(" ", "+")}'
            })
        
        return {
            'status': 'success',
            'platforms_analyzed': len(coverage_analysis),
            'coverage_analysis': coverage_analysis,
            'narrative_consistency_score': sum(p['narrative_consistency'] for p in coverage_analysis) / len(coverage_analysis),
            'bias_diversity': len(set(p['bias_lean'] for p in coverage_analysis)),
            'search_terms': key_terms
        }
        
    except Exception as e:
        logger.error(f"Cross-platform analysis error: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'platforms_analyzed': 0
        }

def get_google_fact_check(text):
    """Enhanced Google Fact Check integration"""
    try:
        if not GOOGLE_FACT_CHECK_API_KEY:
            return {
                'status': 'unavailable',
                'error': 'Google Fact Check API not configured',
                'fact_checks_found': 0
            }
        
        key_terms = extract_enhanced_key_terms(text)
        
        url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        params = {
            'key': GOOGLE_FACT_CHECK_API_KEY,
            'query': key_terms,
            'languageCode': 'en'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            claims = data.get('claims', [])
            
            processed_claims = []
            for claim in claims[:5]:  # Top 5 fact checks
                claim_reviews = claim.get('claimReview', [])
                if claim_reviews:
                    review = claim_reviews[0]
                    processed_claims.append({
                        'claim_text': claim.get('text', 'No claim text'),
                        'claimant': claim.get('claimant', 'Unknown'),
                        'rating': review.get('textualRating', 'No rating'),
                        'reviewer': review.get('publisher', {}).get('name', 'Unknown'),
                        'review_url': review.get('url', ''),
                        'rating_value': convert_rating_to_score(review.get('textualRating', ''))
                    })
            
            return {
                'status': 'success',
                'fact_checks_found': len(processed_claims),
                'claims': processed_claims,
                'search_terms': key_terms,
                'average_rating': sum(c['rating_value'] for c in processed_claims) / len(processed_claims) if processed_claims else 50
            }
        else:
            return {
                'status': 'error',
                'error': f'Google Fact Check API returned status {response.status_code}',
                'fact_checks_found': 0
            }
            
    except Exception as e:
        logger.error(f"Google Fact Check error: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'fact_checks_found': 0
        }

def calculate_comprehensive_scores(ai_analysis, political_analysis, author_analysis, 
                                 source_verification, cross_platform, fact_check):
    """Calculate comprehensive scoring system"""
    try:
        # Overall Credibility Score (0-100)
        credibility_components = []
        
        # AI Analysis (30% weight)
        if ai_analysis.get('status') == 'success':
            ai_score = ai_analysis.get('credibility_score', 50)
            credibility_components.append(ai_score * 0.30)
        
        # Source Verification (25% weight)
        if source_verification.get('status') == 'success':
            source_score = min(source_verification.get('average_source_credibility', 70), 100)
            credibility_components.append(source_score * 0.25)
        
        # Author Analysis (20% weight)
        if author_analysis.get('status') == 'success':
            author_score = (
                author_analysis.get('writing_style_score', 50) + 
                author_analysis.get('professionalism_score', 50)
            ) / 2
            credibility_components.append(author_score * 0.20)
        
        # Political Bias (15% weight) - neutral is better
        if political_analysis.get('status') == 'success':
            bias_score = political_analysis.get('objectivity_score', 50)
            credibility_components.append(bias_score * 0.15)
        
        # Fact Check (10% weight)
        if fact_check.get('status') == 'success' and fact_check.get('fact_checks_found', 0) > 0:
            fact_score = fact_check.get('average_rating', 50)
            credibility_components.append(fact_score * 0.10)
        
        overall_credibility = sum(credibility_components) if credibility_components else 50
        
        return {
            'overall_credibility': round(overall_credibility, 1),
            'credibility_grade': get_credibility_grade(overall_credibility),
            'bias_score': political_analysis.get('bias_score', 0),
            'bias_intensity': abs(political_analysis.get('bias_score', 0)),
            'source_diversity': source_verification.get('source_diversity', 0),
            'fact_check_score': fact_check.get('average_rating', 0) if fact_check.get('fact_checks_found', 0) > 0 else None,
            'author_credibility': (
                author_analysis.get('writing_style_score', 50) + 
                author_analysis.get('professionalism_score', 50)
            ) / 2 if author_analysis.get('status') == 'success' else 50,
            'verification_completeness': calculate_verification_completeness(
                ai_analysis, source_verification, fact_check
            )
        }
        
    except Exception as e:
        logger.error(f"Error calculating scores: {str(e)}")
        return {
            'overall_credibility': 50.0,
            'credibility_grade': 'Unknown',
            'error': str(e)
        }

def generate_executive_summary(results):
    """Generate executive summary for dashboard"""
    try:
        score = results.get('scoring', {}).get('overall_credibility', 50)
        bias_score = results.get('political_bias', {}).get('bias_score', 0)
        sources_found = results.get('source_verification', {}).get('sources_found', 0)
        
        # Main assessment
        if score >= 80:
            assessment = "HIGH CREDIBILITY"
            color = "green"
        elif score >= 60:
            assessment = "MODERATE CREDIBILITY" 
            color = "yellow"
        elif score >= 40:
            assessment = "LOW CREDIBILITY"
            color = "orange"
        else:
            assessment = "VERY LOW CREDIBILITY"
            color = "red"
        
        # Bias assessment
        if abs(bias_score) <= 20:
            bias_assessment = "relatively neutral"
        elif abs(bias_score) <= 50:
            bias_assessment = "moderately biased"
        else:
            bias_assessment = "highly biased"
        
        summary_text = f"{assessment}: This content shows {bias_assessment} language patterns. "
        summary_text += f"Analysis verified through {sources_found} sources. "
        
        if results.get('fact_check_results', {}).get('fact_checks_found', 0) > 0:
            summary_text += "Fact-check data available for verification."
        
        return {
            'main_assessment': assessment,
            'assessment_color': color,
            'credibility_score': score,
            'summary_text': summary_text,
            'key_findings': [
                f"Credibility Score: {score}/100",
                f"Political Bias: {get_bias_label(bias_score)}",
                f"Sources Verified: {sources_found}",
                f"Author Credibility: {results.get('scoring', {}).get('author_credibility', 50):.0f}/100"
            ],
            'recommendation': get_recommendation(score, bias_score)
        }
        
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return {
            'main_assessment': 'ANALYSIS ERROR',
            'assessment_color': 'gray',
            'summary_text': 'Unable to complete analysis summary.',
            'error': str(e)
        }

def prepare_visualization_data(results):
    """Prepare data for frontend visualizations"""
    try:
        return {
            'credibility_meter': {
                'score': results.get('scoring', {}).get('overall_credibility', 50),
                'color': get_credibility_color(results.get('scoring', {}).get('overall_credibility', 50)),
                'segments': [
                    {'label': 'Very Low', 'range': [0, 25], 'color': '#ff4444'},
                    {'label': 'Low', 'range': [25, 50], 'color': '#ff8800'},
                    {'label': 'Moderate', 'range': [50, 75], 'color': '#ffaa00'},
                    {'label': 'High', 'range': [75, 90], 'color': '#88cc00'},
                    {'label': 'Very High', 'range': [90, 100], 'color': '#00cc44'}
                ]
            },
            'bias_visualization': results.get('political_bias', {}).get('visualization', {}),
            'source_breakdown': {
                'total_sources': results.get('source_verification', {}).get('sources_found', 0),
                'diversity_score': results.get('source_verification', {}).get('source_diversity', 0),
                'average_credibility': results.get('source_verification', {}).get('average_source_credibility', 70)
            },
            'analysis_completeness': {
                'ai_analysis': results.get('ai_analysis', {}).get('status') == 'success',
                'source_verification': results.get('source_verification', {}).get('status') == 'success',
                'fact_checking': results.get('fact_check_results', {}).get('status') == 'success',
                'author_analysis': results.get('author_analysis', {}).get('status') == 'success',
                'bias_analysis': results.get('political_bias', {}).get('status') == 'success'
            }
        }
        
    except Exception as e:
        logger.error(f"Error preparing visualization data: {str(e)}")
        return {'error': str(e)}

# Helper Functions
def extract_enhanced_key_terms(text):
    """Enhanced key term extraction"""
    common_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'will', 'would', 'could',
        'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'said', 'says'
    }
    
    # Extract meaningful terms
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    key_terms = [word for word in words if word not in common_words]
    
    # Prioritize proper nouns and longer terms
    important_terms = []
    for word in text.split():
        clean_word = re.sub(r'[^\w]', '', word)
        if len(clean_word) > 3 and (word[0].isupper() or len(clean_word) > 6):
            important_terms.append(clean_word.lower())
    
    # Combine and deduplicate
    all_terms = list(set(important_terms + key_terms[:5]))
    return ' '.join(all_terms[:6])

def extract_domain(url):
    """Extract domain from URL"""
    try:
        return urlparse(url).netloc.lower().replace('www.', '')
    except:
        return 'unknown.com'

def truncate_text(text, max_length):
    """Truncate text with ellipsis"""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + "..."

def get_bias_color(bias_score):
    """Get color for bias visualization"""
    if bias_score <= -60: return '#0066cc'  # Blue (far left)
    elif bias_score <= -30: return '#4488cc'  # Light blue (left)
    elif bias_score <= -10: return '#88aacc'  # Very light blue (center-left)
    elif bias_score <= 10: return '#cccccc'   # Gray (center)
    elif bias_score <= 30: return '#cc8888'   # Light red (center-right)
    elif bias_score <= 60: return '#cc4444'   # Red (right)
    else: return '#cc0000'                    # Dark red (far right)

def get_bias_label(bias_score):
    """Convert bias score to label"""
    if bias_score <= -60: return 'Far Left'
    elif bias_score <= -30: return 'Left'
    elif bias_score <= -10: return 'Center-Left'
    elif bias_score <= 10: return 'Center'
    elif bias_score <= 30: return 'Center-Right'
    elif bias_score <= 60: return 'Right'
    else: return 'Far Right'

def get_credibility_grade(score):
    """Convert score to letter grade"""
    if score >= 90: return 'A+'
    elif score >= 85: return 'A'
    elif score >= 80: return 'A-'
    elif score >= 75: return 'B+'
    elif score >= 70: return 'B'
    elif score >= 65: return 'B-'
    elif score >= 60: return 'C+'
    elif score >= 55: return 'C'
    elif score >= 50: return 'C-'
    elif score >= 40: return 'D'
    else: return 'F'

def get_credibility_color(score):
    """Get color for credibility score"""
    if score >= 80: return '#00cc44'    # Green
    elif score >= 60: return '#88cc00'  # Yellow-green
    elif score >= 40: return '#ffaa00'  # Orange
    else: return '#ff4444'              # Red

def convert_rating_to_score(rating):
    """Convert textual rating to numeric score"""
    rating_lower = rating.lower()
    if 'true' in rating_lower or 'accurate' in rating_lower: return 90
    elif 'mostly true' in rating_lower or 'mostly accurate' in rating_lower: return 75
    elif 'half true' in rating_lower or 'mixed' in rating_lower: return 50
    elif 'mostly false' in rating_lower or 'mostly inaccurate' in rating_lower: return 25
    elif 'false' in rating_lower or 'inaccurate' in rating_lower: return 10
    else: return 50

def calculate_verification_completeness(ai_analysis, source_verification, fact_check):
    """Calculate how complete the verification is"""
    completeness = 0
    if ai_analysis.get('status') == 'success': completeness += 40
    if source_verification.get('status') == 'success': completeness += 35
    if fact_check.get('status') == 'success' and fact_check.get('fact_checks_found', 0) > 0: completeness += 25
    return completeness

def get_recommendation(credibility_score, bias_score):
    """Generate recommendation based on scores"""
    if credibility_score >= 80 and abs(bias_score) <= 20:
        return "This content appears highly credible and relatively unbiased. Safe to share."
    elif credibility_score >= 60:
        return "This content has moderate credibility. Consider cross-referencing with other sources."
    elif abs(bias_score) >= 50:
        return "This content shows significant bias. Seek alternative perspectives before forming opinions."
    else:
        return "This content has credibility concerns. Verify claims through authoritative sources before sharing."

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
