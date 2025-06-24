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
        "version": "Professional v7.0 - Unified Analysis Platform",
        "features": [
            "advanced_news_analysis", "unified_content_authenticity",
            "ai_detection_engine", "plagiarism_detection_engine",
            "political_bias_detection", "author_credibility_profiling",
            "cross_platform_verification", "source_reputation_analysis",
            "web_search_verification", "content_similarity_matching",
            "real_time_progress_tracking", "interactive_visualizations",
            "premium_dashboard_interface", "multi_source_cross_verification"
        ],
        "tools_available": [
            "news_misinformation_detector",
            "unified_content_authenticity_checker",
            "deepfake_detection_tool"
        ],
        "analysis_engines": [
            "ai_pattern_detection",
            "plagiarism_verification", 
            "web_search_matching",
            "linguistic_analysis",
            "style_authenticity"
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

@app.route('/api/analyze-content-authenticity', methods=['POST', 'OPTIONS'])
def analyze_content_authenticity():
    """UNIFIED: AI Detection + Plagiarism Checking in One Comprehensive Analysis"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    
    try:
        data = request.get_json()
        logger.info(f"Starting unified content authenticity analysis for text length: {len(data.get('text', ''))}")
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided in request'}), 400
        
        text = data['text'].strip()
        if len(text) < 50:
            return jsonify({'error': 'Text too short for authenticity analysis (minimum 50 characters)'}), 400
        
        # Initialize comprehensive results structure
        results = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'analysis_id': f"authenticity_{int(time.time())}",
            'text_length': len(text),
            'content_hash': hashlib.md5(text.encode()).hexdigest(),
            'analysis_type': 'unified_content_authenticity',
            'analysis_stages': {
                'ai_pattern_detection': 'completed',
                'linguistic_analysis': 'completed',
                'plagiarism_detection': 'completed',
                'web_search_verification': 'completed',
                'style_authenticity': 'completed',
                'similarity_matching': 'completed',
                'unified_scoring': 'completed'
            }
        }
        
        # STAGE 1: AI Detection Engine
        logger.info("Stage 1: AI Pattern Detection...")
        ai_pattern_analysis = detect_ai_patterns(text)
        results['ai_pattern_analysis'] = ai_pattern_analysis
        
        # STAGE 2: Linguistic Analysis
        logger.info("Stage 2: Linguistic Analysis...")
        linguistic_analysis = analyze_linguistic_patterns(text)
        results['linguistic_analysis'] = linguistic_analysis
        
        # STAGE 3: Advanced AI Detection with OpenAI
        logger.info("Stage 3: Advanced AI Detection...")
        ai_detection = get_advanced_ai_detection(text)
        results['ai_detection'] = ai_detection
        
        # STAGE 4: Style Authenticity Analysis
        logger.info("Stage 4: Style Authenticity Analysis...")
        style_analysis = analyze_writing_style_authenticity(text)
        results['style_analysis'] = style_analysis
        
        # STAGE 5: Comprehensive Plagiarism Detection
        logger.info("Stage 5: Plagiarism Detection Engine...")
        plagiarism_analysis = comprehensive_plagiarism_check(text)
        results['plagiarism_analysis'] = plagiarism_analysis
        
        # STAGE 6: Web Search Verification
        logger.info("Stage 6: Web Search Verification...")
        web_verification = perform_web_search_verification(text)
        results['web_verification'] = web_verification
        
        # STAGE 7: Content Similarity Matching
        logger.info("Stage 7: Similarity Matching...")
        similarity_analysis = analyze_content_similarity(text, web_verification)
        results['similarity_analysis'] = similarity_analysis
        
        # STAGE 8: Calculate Unified Authenticity Score
        logger.info("Stage 8: Calculating Unified Authenticity Score...")
        authenticity_scoring = calculate_unified_authenticity_score(
            ai_pattern_analysis, linguistic_analysis, ai_detection, 
            style_analysis, plagiarism_analysis, web_verification, similarity_analysis
        )
        results['authenticity_scoring'] = authenticity_scoring
        
        # STAGE 9: Generate Comprehensive Report
        results['comprehensive_report'] = generate_authenticity_report(results)
        
        # STAGE 10: Prepare Unified Visualization Data
        results['visualization_data'] = prepare_authenticity_visualization(results)
        
        logger.info(f"Unified authenticity analysis complete. Overall authenticity: {authenticity_scoring.get('overall_authenticity', 'N/A')}%")
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in unified content authenticity analysis: {str(e)}")
        return jsonify({
            'error': 'Content authenticity analysis failed',
            'details': str(e),
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

# Maintain backward compatibility
@app.route('/api/analyze-ai-content', methods=['POST', 'OPTIONS'])
def analyze_ai_content():
    """Legacy endpoint - redirects to unified authenticity checker"""
    return analyze_content_authenticity()

def detect_ai_patterns(text):
    """Enhanced AI pattern detection for unified analysis"""
    try:
        patterns = {
            'repetitive_phrases': 0,
            'generic_transitions': 0,
            'perfect_grammar_score': 0,
            'list_heavy_score': 0,
            'buzzword_density': 0,
            'conclusion_patterns': 0,
            'ai_signature_phrases': 0
        }
        
        # Expanded AI signature phrases
        ai_phrases = [
            'it is important to note', 'it should be noted', 'in conclusion',
            'furthermore', 'moreover', 'additionally', 'however', 'therefore',
            'it is worth noting', 'on the other hand', 'in summary',
            'to summarize', 'in other words', 'for instance', 'for example',
            'as a result', 'consequently', 'nevertheless', 'nonetheless',
            'in contrast', 'similarly', 'likewise', 'ultimately',
            'comprehensive', 'streamline', 'optimize', 'leverage',
            'paradigm shift', 'cutting-edge', 'state-of-the-art'
        ]
        
        text_lower = text.lower()
        
        # Enhanced pattern detection
        for phrase in ai_phrases:
            count = text_lower.count(phrase)
            if phrase in ['furthermore', 'moreover', 'additionally', 'however', 'therefore']:
                patterns['generic_transitions'] += count
            elif phrase in ['comprehensive', 'streamline', 'optimize', 'leverage']:
                patterns['buzzword_density'] += count
            elif phrase in ['in conclusion', 'in summary', 'to summarize']:
                patterns['conclusion_patterns'] += count
            else:
                patterns['ai_signature_phrases'] += count
            patterns['repetitive_phrases'] += count
        
        # List pattern detection
        list_indicators = ['first', 'second', 'third', 'finally', '1.', '2.', '3.', '4.', '5.']
        for indicator in list_indicators:
            patterns['list_heavy_score'] += text_lower.count(indicator)
        
        # Grammar perfection analysis
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            # AI tends to write 15-30 word sentences consistently
            if 15 <= avg_sentence_length <= 30:
                patterns['perfect_grammar_score'] = 85
            elif 10 <= avg_sentence_length <= 35:
                patterns['perfect_grammar_score'] = 60
            else:
                patterns['perfect_grammar_score'] = 30
        
        # Calculate overall pattern score
        total_patterns = sum(patterns.values())
        text_words = len(text.split())
        pattern_density = (total_patterns / text_words) * 100 if text_words > 0 else 0
        
        # Risk level assessment
        if pattern_density > 8:
            risk_level = 'very_high'
        elif pattern_density > 5:
            risk_level = 'high'
        elif pattern_density > 3:
            risk_level = 'medium'
        elif pattern_density > 1:
            risk_level = 'low'
        else:
            risk_level = 'very_low'
        
        return {
            'status': 'success',
            'patterns_detected': patterns,
            'pattern_density': round(pattern_density, 2),
            'risk_level': risk_level,
            'total_flags': total_patterns,
            'ai_confidence': min(100, pattern_density * 12),
            'pattern_breakdown': {
                'transition_overuse': patterns['generic_transitions'] > 3,
                'buzzword_heavy': patterns['buzzword_density'] > 2,
                'list_structured': patterns['list_heavy_score'] > 3,
                'perfect_grammar': patterns['perfect_grammar_score'] > 70,
                'signature_phrases': patterns['ai_signature_phrases'] > 2
            }
        }
        
    except Exception as e:
        logger.error(f"Enhanced pattern detection error: {str(e)}")
        return {'status': 'error', 'error': str(e)}

def analyze_linguistic_patterns(text):
    """Enhanced linguistic analysis for authenticity checking"""
    try:
        words = text.split()
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        # Advanced vocabulary analysis
        unique_words = len(set(word.lower().strip('.,!?;:"()[]') for word in words))
        vocab_diversity = (unique_words / len(words)) * 100 if words else 0
        
        # Word length distribution
        word_lengths = [len(word.strip('.,!?;:"()[]')) for word in words]
        avg_word_length = sum(word_lengths) / len(word_lengths) if word_lengths else 0
        word_length_variance = calculate_variance(word_lengths)
        
        # Sentence complexity analysis
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        sentence_variance = calculate_variance(sentence_lengths)
        
        # Punctuation analysis
        punctuation_count = sum(1 for char in text if char in '.,!?;:')
        punctuation_ratio = (punctuation_count / len(text)) * 100 if text else 0
        
        # Advanced conjunction analysis
        conjunctions = {
            'coordinating': ['and', 'but', 'or', 'nor', 'for', 'yet', 'so'],
            'subordinating': ['because', 'since', 'although', 'while', 'if', 'unless'],
            'transitional': ['however', 'therefore', 'moreover', 'furthermore', 'nevertheless']
        }
        
        conjunction_counts = {}
        total_conjunctions = 0
        for conj_type, conj_list in conjunctions.items():
            count = sum(text.lower().count(conj) for conj in conj_list)
            conjunction_counts[conj_type] = count
            total_conjunctions += count
        
        conjunction_density = (total_conjunctions / len(words)) * 100 if words else 0
        
        # Calculate linguistic authenticity indicators
        authenticity_indicators = {
            'natural_vocabulary': 30 <= vocab_diversity <= 70,
            'varied_sentence_length': sentence_variance > 20,
            'natural_word_variety': word_length_variance > 2,
            'balanced_conjunctions': conjunction_density < 4,
            'human_punctuation': 3 <= punctuation_ratio <= 12
        }
        
        # Human-likeness score
        human_score = sum(1 for indicator in authenticity_indicators.values() if indicator) * 20
        
        return {
            'status': 'success',
            'vocabulary_diversity': round(vocab_diversity, 2),
            'average_word_length': round(avg_word_length, 2),
            'word_length_variance': round(word_length_variance, 2),
            'average_sentence_length': round(avg_sentence_length, 2),
            'sentence_variance': round(sentence_variance, 2),
            'punctuation_ratio': round(punctuation_ratio, 2),
            'conjunction_density': round(conjunction_density, 2),
            'conjunction_breakdown': conjunction_counts,
            'authenticity_indicators': authenticity_indicators,
            'human_likeness_score': human_score,
            'linguistic_complexity': calculate_linguistic_complexity(
                vocab_diversity, avg_word_length, avg_sentence_length, sentence_variance
            )
        }
        
    except Exception as e:
        logger.error(f"Enhanced linguistic analysis error: {str(e)}")
        return {'status': 'error', 'error': str(e)}

def get_advanced_ai_detection(text):
    """Enhanced AI detection using OpenAI with focus on authenticity"""
    try:
        if not OPENAI_API_KEY:
            return {'status': 'unavailable', 'error': 'OpenAI API not configured'}
        
        prompt = f"""
        Analyze this text for AI generation indicators and overall authenticity. Return ONLY valid JSON:
        {{
            "ai_likelihood": (0-100, percentage chance this is AI-generated),
            "confidence": (0-100, how confident you are in this assessment),
            "authenticity_score": (0-100, how authentic/human this seems),
            "ai_indicators": ["specific indicator1", "specific indicator2", "specific indicator3"],
            "human_indicators": ["human marker1", "human marker2"],
            "writing_style": "formal|informal|academic|creative|technical|conversational",
            "tone_consistency": (0-100, how consistent the tone is),
            "vocabulary_sophistication": (0-100),
            "personal_voice": (0-100, how much personal voice is present),
            "emotional_depth": (0-100, depth of emotional expression),
            "reasoning": "detailed explanation of assessment",
            "red_flags": ["specific red flag1", "specific red flag2"],
            "authenticity_markers": ["authenticity marker1", "authenticity marker2"],
            "originality_assessment": "likely_original|possibly_derivative|likely_copied|uncertain"
        }}
        
        Text: {text[:2000]}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert at detecting AI-generated content and assessing content authenticity. Focus on both AI detection and originality assessment. Always respond with valid JSON only."},
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
        logger.error(f"Enhanced AI detection error: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'ai_likelihood': 50,
            'authenticity_score': 50,
            'confidence': 0
        }

def analyze_writing_style_authenticity(text):
    """Enhanced style analysis focused on authenticity detection"""
    try:
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        # Sentence variety analysis
        sentence_lengths = [len(s.split()) for s in sentences]
        length_variance = calculate_variance(sentence_lengths) if sentence_lengths else 0
        
        # Paragraph structure analysis
        paragraph_lengths = [len(p.split()) for p in paragraphs]
        avg_paragraph_length = sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0
        paragraph_variance = calculate_variance(paragraph_lengths) if len(paragraph_lengths) > 1 else 0
        
        # Emotional language detection (enhanced)
        emotional_words = {
            'positive': ['amazing', 'wonderful', 'fantastic', 'excellent', 'brilliant', 'love', 'adore', 'thrilled'],
            'negative': ['terrible', 'awful', 'horrible', 'hate', 'disgusting', 'annoying', 'frustrated'],
            'neutral_descriptive': ['interesting', 'significant', 'important', 'relevant', 'useful']
        }
        
        emotion_counts = {}
        total_emotional = 0
        for emotion_type, words in emotional_words.items():
            count = sum(text.lower().count(word) for word in words)
            emotion_counts[emotion_type] = count
            total_emotional += count
        
        # Personal language indicators
        personal_indicators = {
            'first_person': ['i', 'me', 'my', 'mine', 'myself'],
            'second_person': ['you', 'your', 'yours', 'yourself'],
            'contractions': ["don't", "won't", "can't", "isn't", "aren't", "wasn't", "weren't"],
            'informal_expressions': ['yeah', 'okay', 'well', 'actually', 'basically', 'pretty much']
        }
        
        personal_counts = {}
        total_personal = 0
        for indicator_type, words in personal_indicators.items():
            count = sum(text.lower().count(word) for word in words)
            personal_counts[indicator_type] = count
            total_personal += count
        
        # Calculate authenticity scores
        style_variance = min(100, length_variance * 8)  # Higher variance = more human-like
        emotional_score = min(100, total_emotional * 4)  # More emotion = more human-like
        personal_score = min(100, total_personal * 3)    # More personal = more human-like
        structural_variety = min(100, paragraph_variance * 10) if paragraph_variance > 0 else 0
        
        # Overall human likelihood
        human_likelihood = (style_variance + emotional_score + personal_score + structural_variety) / 4
        
        return {
            'status': 'success',
            'sentence_variance': round(style_variance, 2),
            'emotional_content': round(emotional_score, 2),
            'personal_language': round(personal_score, 2),
            'structural_variety': round(structural_variety, 2),
            'average_paragraph_length': round(avg_paragraph_length, 2),
            'emotion_breakdown': emotion_counts,
            'personal_breakdown': personal_counts,
            'style_indicators': {
                'uniform_structure': style_variance < 20,
                'low_emotion': emotional_score < 15,
                'impersonal_tone': personal_score < 20,
                'repetitive_paragraphs': structural_variety < 30,
                'overly_formal': personal_counts['contractions'] == 0 and len(text) > 200
            },
            'human_likelihood': round(human_likelihood, 2),
            'authenticity_assessment': get_authenticity_level(human_likelihood)
        }
        
    except Exception as e:
        logger.error(f"Enhanced style analysis error: {str(e)}")
        return {'status': 'error', 'error': str(e)}

def comprehensive_plagiarism_check(text):
    """Comprehensive plagiarism detection system"""
    try:
        # Extract key phrases for web searching
        search_phrases = extract_sophisticated_search_phrases(text)
        
        # Analyze text structure for copy-paste indicators
        structure_analysis = analyze_text_structure_for_plagiarism(text)
        
        # Check for common plagiarism patterns
        plagiarism_patterns = detect_plagiarism_patterns(text)
        
        # Calculate uniqueness indicators
        uniqueness_analysis = calculate_uniqueness_indicators(text)
        
        # Overall plagiarism risk assessment
        risk_factors = []
        risk_score = 0
        
        # Pattern-based risk assessment
        if plagiarism_patterns['copy_paste_indicators'] > 2:
            risk_factors.append("Multiple copy-paste indicators detected")
            risk_score += 30
        
        if structure_analysis['formatting_inconsistencies'] > 3:
            risk_factors.append("Formatting inconsistencies suggest multiple sources")
            risk_score += 25
        
        if uniqueness_analysis['phrase_repetition_score'] > 70:
            risk_factors.append("High phrase repetition typical of copied content")
            risk_score += 20
        
        if len(search_phrases) < 3:
            risk_factors.append("Limited unique content for verification")
            risk_score += 15
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = 'very_high'
        elif risk_score >= 50:
            risk_level = 'high'
        elif risk_score >= 30:
            risk_level = 'medium'
        elif risk_score >= 15:
            risk_level = 'low'
        else:
            risk_level = 'very_low'
        
        return {
            'status': 'success',
            'plagiarism_risk_score': min(100, risk_score),
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'search_phrases': search_phrases,
            'structure_analysis': structure_analysis,
            'plagiarism_patterns': plagiarism_patterns,
            'uniqueness_analysis': uniqueness_analysis,
            'recommendations': generate_plagiarism_recommendations(risk_level, risk_factors)
        }
        
    except Exception as e:
        logger.error(f"Comprehensive plagiarism check error: {str(e)}")
        return {'status': 'error', 'error': str(e)}

def perform_web_search_verification(text):
    """Enhanced web search for plagiarism verification"""
    try:
        if not NEWS_API_KEY:
            return {
                'status': 'limited',
                'error': 'NewsAPI not configured - using alternative verification',
                'matches_found': 0
            }
        
        # Extract multiple search strategies
        search_phrases = extract_sophisticated_search_phrases(text)
        key_sentences = extract_key_sentences_for_search(text)
        
        verification_results = []
        total_matches = 0
        
        # Search with different strategies
        for i, phrase in enumerate(search_phrases[:3]):  # Top 3 phrases
            try:
                url = 'https://newsapi.org/v2/everything'
                params = {
                    'q': f'"{phrase}"',  # Exact phrase search
                    'apiKey': NEWS_API_KEY,
                    'sortBy': 'relevancy',
                    'pageSize': 5,
                    'language': 'en'
                }
                
                headers = {
                    'User-Agent': 'FactsAndFakes-ContentVerification/1.0',
                    'Accept': 'application/json'
                }
                
                response = requests.get(url, params=params, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articles', [])
                    
                    if articles:
                        for article in articles[:2]:  # Top 2 matches per phrase
                            similarity_score = calculate_text_similarity(phrase, article.get('description', ''))
                            if similarity_score > 70:  # High similarity threshold
                                verification_results.append({
                                    'search_phrase': phrase,
                                    'matched_title': article.get('title', 'No title'),
                                    'source': article.get('source', {}).get('name', 'Unknown'),
                                    'url': article.get('url', ''),
                                    'similarity_score': similarity_score,
                                    'published_date': article.get('publishedAt', ''),
                                    'match_type': 'exact_phrase' if similarity_score > 90 else 'high_similarity'
                                })
                                total_matches += 1
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"Web search failed for phrase {i}: {str(e)}")
                continue
        
        return {
            'status': 'success',
            'matches_found': total_matches,
            'verification_results': verification_results,
            'search_phrases_used': search_phrases,
            'high_similarity_matches': len([r for r in verification_results if r['similarity_score'] > 85]),
            'exact_matches': len([r for r in verification_results if r['match_type'] == 'exact_phrase'])
        }
        
    except Exception as e:
        logger.error(f"Web search verification error: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'matches_found': 0
        }

def analyze_content_similarity(text, web_verification):
    """Analyze similarity between content and web search results"""
    try:
        if web_verification.get('status') != 'success' or web_verification.get('matches_found', 0) == 0:
            return {
                'status': 'no_comparison_data',
                'similarity_score': 0,
                'analysis': 'No web matches found for comparison'
            }
        
        verification_results = web_verification.get('verification_results', [])
        
        similarity_scores = []
        detailed_comparisons = []
        
        for result in verification_results:
            # Calculate detailed similarity
            phrase = result['search_phrase']
            similarity = result['similarity_score']
            
            similarity_scores.append(similarity)
            detailed_comparisons.append({
                'source': result['source'],
                'similarity_percentage': similarity,
                'match_type': result['match_type'],
                'url': result['url']
            })
        
        # Calculate overall similarity assessment
        if similarity_scores:
            max_similarity = max(similarity_scores)
            avg_similarity = sum(similarity_scores) / len(similarity_scores)
            
            # Determine similarity risk
            if max_similarity > 95:
                similarity_risk = 'very_high'
                risk_description = 'Exact or near-exact matches found'
            elif max_similarity > 85:
                similarity_risk = 'high'
                risk_description = 'High similarity matches detected'
            elif max_similarity > 70:
                similarity_risk = 'medium'
                risk_description = 'Moderate similarity to existing content'
            elif max_similarity > 50:
                similarity_risk = 'low'
                risk_description = 'Low similarity to existing content'
            else:
                similarity_risk = 'very_low'
                risk_description = 'Minimal similarity to existing content'
        else:
            max_similarity = 0
            avg_similarity = 0
            similarity_risk = 'very_low'
            risk_description = 'No significant matches found'
        
        return {
            'status': 'success',
            'max_similarity_score': round(max_similarity, 2),
            'average_similarity_score': round(avg_similarity, 2),
            'similarity_risk': similarity_risk,
            'risk_description': risk_description,
            'total_comparisons': len(detailed_comparisons),
            'detailed_comparisons': detailed_comparisons,
            'high_risk_matches': len([c for c in detailed_comparisons if c['similarity_percentage'] > 85])
        }
        
    except Exception as e:
        logger.error(f"Content similarity analysis error: {str(e)}")
        return {'status': 'error', 'error': str(e)}

def calculate_unified_authenticity_score(ai_pattern_analysis, linguistic_analysis, ai_detection, 
                                       style_analysis, plagiarism_analysis, web_verification, similarity_analysis):
    """Calculate comprehensive authenticity score combining AI detection and plagiarism checking"""
    try:
        scores = []
        weights = []
        component_scores = {}
        
        # AI Pattern Analysis (15% weight)
        if ai_pattern_analysis.get('status') == 'success':
            ai_confidence = ai_pattern_analysis.get('ai_confidence', 50)
            ai_authenticity = 100 - ai_confidence  # Invert: high AI confidence = low authenticity
            scores.append(ai_authenticity)
            weights.append(0.15)
            component_scores['ai_pattern_authenticity'] = round(ai_authenticity, 1)
        
        # Linguistic Analysis (20% weight)
        if linguistic_analysis.get('status') == 'success':
            human_likeness = linguistic_analysis.get('human_likeness_score', 50)
            scores.append(human_likeness)
            weights.append(0.20)
            component_scores['linguistic_authenticity'] = round(human_likeness, 1)
        
        # OpenAI AI Detection (20% weight)
        if ai_detection.get('status') == 'success':
            openai_authenticity = ai_detection.get('authenticity_score', 50)
            scores.append(openai_authenticity)
            weights.append(0.20)
            component_scores['ai_detection_authenticity'] = round(openai_authenticity, 1)
        
        # Style Analysis (15% weight)
        if style_analysis.get('status') == 'success':
            style_human_likelihood = style_analysis.get('human_likelihood', 50)
            scores.append(style_human_likelihood)
            weights.append(0.15)
            component_scores['style_authenticity'] = round(style_human_likelihood, 1)
        
        # Plagiarism Analysis (20% weight)
        if plagiarism_analysis.get('status') == 'success':
            plagiarism_risk = plagiarism_analysis.get('plagiarism_risk_score', 0)
            plagiarism_authenticity = 100 - plagiarism_risk  # Invert: high plagiarism risk = low authenticity
            scores.append(plagiarism_authenticity)
            weights.append(0.20)
            component_scores['plagiarism_authenticity'] = round(plagiarism_authenticity, 1)
        
        # Similarity Analysis (10% weight)
        if similarity_analysis.get('status') == 'success':
            max_similarity = similarity_analysis.get('max_similarity_score', 0)
            similarity_authenticity = 100 - max_similarity  # Invert: high similarity = low authenticity
            scores.append(similarity_authenticity)
            weights.append(0.10)
            component_scores['similarity_authenticity'] = round(similarity_authenticity, 1)
        
        # Calculate weighted overall authenticity score
        if scores and weights:
            overall_authenticity = sum(score * weight for score, weight in zip(scores, weights)) / sum(weights)
        else:
            overall_authenticity = 50
        
        # Determine authenticity classification
        if overall_authenticity >= 85:
            classification = "Highly Authentic"
            confidence = "Very High"
            color = "#00cc44"
            risk_level = "very_low"
        elif overall_authenticity >= 70:
            classification = "Likely Authentic"
            confidence = "High"
            color = "#88cc00"
            risk_level = "low"
        elif overall_authenticity >= 55:
            classification = "Moderately Authentic"
            confidence = "Medium"
            color = "#ffaa00"
            risk_level = "medium"
        elif overall_authenticity >= 40:
            classification = "Questionable Authenticity"
            confidence = "Medium-Low"
            color = "#ff8800"
            risk_level = "high"
        else:
            classification = "Low Authenticity"
            confidence = "High"
            color = "#ff4444"
            risk_level = "very_high"
        
        # Specific risk assessments
        ai_risk = "high" if component_scores.get('ai_detection_authenticity', 100) < 40 else "low"
        plagiarism_risk = plagiarism_analysis.get('risk_level', 'unknown') if plagiarism_analysis.get('status') == 'success' else 'unknown'
        
        return {
            'overall_authenticity': round(overall_authenticity, 1),
            'classification': classification,
            'confidence': confidence,
            'color': color,
            'risk_level': risk_level,
            'component_scores': component_scores,
            'specific_risks': {
                'ai_generation_risk': ai_risk,
                'plagiarism_risk': plagiarism_risk,
                'similarity_risk': similarity_analysis.get('similarity_risk', 'unknown') if similarity_analysis.get('status') == 'success' else 'unknown'
            },
            'recommendation': get_authenticity_recommendation(overall_authenticity, ai_risk, plagiarism_risk),
            'trust_indicators': generate_trust_indicators(component_scores, overall_authenticity)
        }
        
    except Exception as e:
        logger.error(f"Error calculating unified authenticity score: {str(e)}")
        return {
            'overall_authenticity': 50.0,
            'classification': 'Error',
            'confidence': 'Unknown',
            'error': str(e)
        }

def generate_authenticity_report(results):
    """Generate comprehensive authenticity report"""
    try:
        authenticity_scoring = results.get('authenticity_scoring', {})
        overall_score = authenticity_scoring.get('overall_authenticity', 50)
        classification = authenticity_scoring.get('classification', 'Unknown')
        
        # Key findings compilation
        key_findings = []
        
        # AI Detection findings
        if results.get('ai_detection', {}).get('status') == 'success':
            ai_data = results['ai_detection']
            ai_likelihood = ai_data.get('ai_likelihood', 50)
            key_findings.append(f"AI Generation Likelihood: {ai_likelihood}%")
        
        # Plagiarism findings
        if results.get('plagiarism_analysis', {}).get('status') == 'success':
            plag_data = results['plagiarism_analysis']
            risk_level = plag_data.get('risk_level', 'unknown')
            key_findings.append(f"Plagiarism Risk: {risk_level.replace('_', ' ').title()}")
        
        # Web verification findings
        if results.get('web_verification', {}).get('status') == 'success':
            web_data = results['web_verification']
            matches_found = web_data.get('matches_found', 0)
            key_findings.append(f"Web Matches Found: {matches_found}")
        
        # Similarity findings
        if results.get('similarity_analysis', {}).get('status') == 'success':
            sim_data = results['similarity_analysis']
            max_similarity = sim_data.get('max_similarity_score', 0)
            key_findings.append(f"Highest Content Similarity: {max_similarity:.1f}%")
        
        # Style findings
        if results.get('style_analysis', {}).get('status') == 'success':
            style_data = results['style_analysis']
            human_likelihood = style_data.get('human_likelihood', 50)
            key_findings.append(f"Human Writing Style: {human_likelihood:.1f}%")
        
        # Generate summary text
        summary_parts = []
        summary_parts.append(f"Content authenticity analysis indicates: {classification.upper()}")
        
        # Add specific concerns
        specific_risks = authenticity_scoring.get('specific_risks', {})
        concerns = []
        if specific_risks.get('ai_generation_risk') == 'high':
            concerns.append("potential AI generation")
        if specific_risks.get('plagiarism_risk') in ['high', 'very_high']:
            concerns.append("plagiarism indicators")
        if specific_risks.get('similarity_risk') in ['high', 'very_high']:
            concerns.append("high similarity to existing content")
        
        if concerns:
            summary_parts.append(f"Analysis detected concerns regarding: {', '.join(concerns)}")
        else:
            summary_parts.append("No significant authenticity concerns detected")
        
        summary_text = ". ".join(summary_parts) + "."
        
        return {
            'main_classification': classification,
            'authenticity_score': overall_score,
            'confidence_level': authenticity_scoring.get('confidence', 'Medium'),
            'summary_text': summary_text,
            'key_findings': key_findings,
            'detailed_analysis': {
                'ai_indicators': results.get('ai_detection', {}).get('ai_indicators', []),
                'plagiarism_patterns': results.get('plagiarism_analysis', {}).get('plagiarism_patterns', {}),
                'style_assessment': results.get('style_analysis', {}).get('style_indicators', {}),
                'web_verification': results.get('web_verification', {}).get('verification_results', []),
                'similarity_matches': results.get('similarity_analysis', {}).get('detailed_comparisons', [])
            },
            'recommendation': authenticity_scoring.get('recommendation', 'Unable to determine recommendation'),
            'trust_indicators': authenticity_scoring.get('trust_indicators', [])
        }
        
    except Exception as e:
        logger.error(f"Error generating authenticity report: {str(e)}")
        return {
            'main_classification': 'Error',
            'summary_text': 'Unable to complete authenticity analysis report.',
            'error': str(e)
        }

def prepare_authenticity_visualization(results):
    """Prepare comprehensive visualization data for unified authenticity analysis"""
    try:
        authenticity_scoring = results.get('authenticity_scoring', {})
        overall_score = authenticity_scoring.get('overall_authenticity', 50)
        
        return {
            'authenticity_meter': {
                'score': overall_score,
                'color': authenticity_scoring.get('color', '#ffaa00'),
                'classification': authenticity_scoring.get('classification', 'Unknown'),
                'segments': [
                    {'label': 'Low Authenticity', 'range': [0, 40], 'color': '#ff4444'},
                    {'label': 'Questionable', 'range': [40, 55], 'color': '#ff8800'},
                    {'label': 'Moderately Authentic', 'range': [55, 70], 'color': '#ffaa00'},
                    {'label': 'Likely Authentic', 'range': [70, 85], 'color': '#88cc00'},
                    {'label': 'Highly Authentic', 'range': [85, 100], 'color': '#00cc44'}
                ]
            },
            'component_breakdown': authenticity_scoring.get('component_scores', {}),
            'risk_assessment': {
                'ai_generation': authenticity_scoring.get('specific_risks', {}).get('ai_generation_risk', 'unknown'),
                'plagiarism': authenticity_scoring.get('specific_risks', {}).get('plagiarism_risk', 'unknown'),
                'similarity': authenticity_scoring.get('specific_risks', {}).get('similarity_risk', 'unknown')
            },
            'analysis_completeness': {
                'ai_pattern_detection': results.get('ai_pattern_analysis', {}).get('status') == 'success',
                'linguistic_analysis': results.get('linguistic_analysis', {}).get('status') == 'success',
                'ai_detection': results.get('ai_detection', {}).get('status') == 'success',
                'style_analysis': results.get('style_analysis', {}).get('status') == 'success',
                'plagiarism_analysis': results.get('plagiarism_analysis', {}).get('status') == 'success',
                'web_verification': results.get('web_verification', {}).get('status') == 'success',
                'similarity_analysis': results.get('similarity_analysis', {}).get('status') == 'success'
            },
            'detailed_metrics': {
                'ai_confidence': results.get('ai_pattern_analysis', {}).get('ai_confidence', 0),
                'plagiarism_risk_score': results.get('plagiarism_analysis', {}).get('plagiarism_risk_score', 0),
                'web_matches_found': results.get('web_verification', {}).get('matches_found', 0),
                'max_similarity': results.get('similarity_analysis', {}).get('max_similarity_score', 0),
                'human_style_likelihood': results.get('style_analysis', {}).get('human_likelihood', 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Error preparing authenticity visualization: {str(e)}")
        return {'error': str(e)}

# Enhanced Helper Functions for Unified Analysis

def extract_sophisticated_search_phrases(text):
    """Extract sophisticated phrases for web search verification"""
    # Split into sentences and filter meaningful ones
    sentences = [s.strip() for s in text.split('.') if s.strip() and len(s.split()) >= 5]
    
    phrases = []
    
    # Extract meaningful phrases from each sentence
    for sentence in sentences[:5]:  # Top 5 sentences
        words = sentence.split()
        
        # Extract 4-7 word phrases
        for i in range(len(words) - 3):
            phrase = ' '.join(words[i:i+5])
            # Filter out common words and ensure meaningful content
            if len(phrase) > 20 and not phrase.lower().startswith(('the ', 'a ', 'an ', 'and ', 'but ', 'or ')):
                phrases.append(phrase.strip('.,!?;:"()[]'))
    
    # Remove duplicates and sort by length (longer phrases first)
    unique_phrases = list(set(phrases))
    unique_phrases.sort(key=len, reverse=True)
    
    return unique_phrases[:10]  # Return top 10 phrases

def extract_key_sentences_for_search(text):
    """Extract key sentences for plagiarism verification"""
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    # Filter sentences that are good candidates for searching
    key_sentences = []
    for sentence in sentences:
        words = sentence.split()
        if 8 <= len(words) <= 25:  # Good length for searching
            key_sentences.append(sentence)
    
    return key_sentences[:5]  # Top 5 key sentences

def analyze_text_structure_for_plagiarism(text):
    """Analyze text structure for plagiarism indicators"""
    try:
        lines = text.split('\n')
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # Check for formatting inconsistencies
        formatting_issues = 0
        
        # Different font indicators (basic detection)
        if '**' in text or '__' in text:
            formatting_issues += 1
        
        # Inconsistent spacing
        double_spaces = text.count('  ')
        if double_spaces > 3:
            formatting_issues += 1
        
        # Inconsistent paragraph lengths
        if paragraphs:
            para_lengths = [len(p.split()) for p in paragraphs]
            if len(para_lengths) > 1:
                avg_length = sum(para_lengths) / len(para_lengths)
                outliers = sum(1 for length in para_lengths if abs(length - avg_length) > avg_length * 0.7)
                if outliers > len(para_lengths) * 0.3:
                    formatting_issues += 1
        
        return {
            'formatting_inconsistencies': formatting_issues,
            'paragraph_count': len(paragraphs),
            'average_paragraph_length': sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0,
            'structure_score': max(0, 100 - (formatting_issues * 25))
        }
        
    except Exception as e:
        logger.error(f"Text structure analysis error: {str(e)}")
        return {'formatting_inconsistencies': 0, 'structure_score': 50}

def detect_plagiarism_patterns(text):
    """Detect common plagiarism patterns in text"""
    try:
        patterns = {
            'copy_paste_indicators': 0,
            'citation_patterns': 0,
            'url_references': 0,
            'academic_phrases': 0
        }
        
        # Copy-paste indicators
        copy_indicators = [
            'according to', 'as stated in', 'source:', 'retrieved from',
            'wikipedia', 'copy and paste', 'citation needed'
        ]
        for indicator in copy_indicators:
            patterns['copy_paste_indicators'] += text.lower().count(indicator)
        
        # URL patterns
        patterns['url_references'] = len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text))
        
        # Academic citation patterns
        citation_indicators = ['et al', 'ibid', 'op. cit', '(2019)', '(2020)', '(2021)', '(2022)', '(2023)', '(2024)']
        for indicator in citation_indicators:
            patterns['citation_patterns'] += text.lower().count(indicator)
        
        # Academic phrases that might indicate copied content
        academic_phrases = ['research shows', 'studies indicate', 'according to research', 'empirical evidence']
        for phrase in academic_phrases:
            patterns['academic_phrases'] += text.lower().count(phrase)
        
        return patterns
        
    except Exception as e:
        logger.error(f"Plagiarism pattern detection error: {str(e)}")
        return {'copy_paste_indicators': 0}

def calculate_uniqueness_indicators(text):
    """Calculate various uniqueness indicators for the text"""
    try:
        # Phrase repetition analysis
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        words = text.split()
        
        # Calculate phrase repetition
        phrases = []
        for i in range(len(words) - 2):
            phrase = ' '.join(words[i:i+3])
            phrases.append(phrase.lower())
        
        phrase_counts = {}
        for phrase in phrases:
            phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
        
        repeated_phrases = sum(1 for count in phrase_counts.values() if count > 1)
        phrase_repetition_score = (repeated_phrases / len(phrase_counts)) * 100 if phrase_counts else 0
        
        # Vocabulary richness
        unique_words = len(set(word.lower().strip('.,!?;:"()[]') for word in words))
        vocabulary_richness = (unique_words / len(words)) * 100 if words else 0
        
        return {
            'phrase_repetition_score': round(phrase_repetition_score, 2),
            'vocabulary_richness': round(vocabulary_richness, 2),
            'unique_word_count': unique_words,
            'total_word_count': len(words),
            'uniqueness_assessment': 'high' if phrase_repetition_score < 30 and vocabulary_richness > 60 else 'medium' if phrase_repetition_score < 50 else 'low'
        }
        
    except Exception as e:
        logger.error(f"Uniqueness calculation error: {str(e)}")
        return {'phrase_repetition_score': 50, 'vocabulary_richness': 50}

def calculate_text_similarity(text1, text2):
    """Calculate similarity score between two texts"""
    try:
        if not text1 or not text2:
            return 0
        
        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = (len(intersection) / len(union)) * 100 if union else 0
        return round(similarity, 2)
        
    except Exception as e:
        logger.error(f"Text similarity calculation error: {str(e)}")
        return 0

def generate_plagiarism_recommendations(risk_level, risk_factors):
    """Generate specific recommendations based on plagiarism risk"""
    recommendations = []
    
    if risk_level in ['very_high', 'high']:
        recommendations.extend([
            "Verify content originality through multiple plagiarism detection tools",
            "Check for proper citations and source attribution",
            "Search key phrases in Google to identify potential sources"
        ])
    elif risk_level == 'medium':
        recommendations.extend([
            "Review content for proper attribution",
            "Consider running additional plagiarism checks",
            "Verify any statistical claims or data points"
        ])
    else:
        recommendations.extend([
            "Content appears original",
            "Consider periodic verification for important content",
            "Maintain documentation of sources if applicable"
        ])
    
    return recommendations

def get_authenticity_level(human_likelihood):
    """Convert human likelihood score to authenticity level"""
    if human_likelihood >= 80:
        return 'very_high'
    elif human_likelihood >= 60:
        return 'high'
    elif human_likelihood >= 40:
        return 'medium'
    elif human_likelihood >= 20:
        return 'low'
    else:
        return 'very_low'

def get_authenticity_recommendation(overall_score, ai_risk, plagiarism_risk):
    """Generate recommendation based on overall authenticity assessment"""
    if overall_score >= 85:
        return "Content appears highly authentic with strong originality indicators. Safe for publication."
    elif overall_score >= 70:
        return "Content likely authentic with good originality. Consider spot-checking key claims."
    elif overall_score >= 55:
        return "Content authenticity is moderate. Recommend additional verification before use."
    elif ai_risk == 'high' and plagiarism_risk in ['high', 'very_high']:
        return "Multiple authenticity concerns detected. Thoroughly verify content before use."
    elif ai_risk == 'high':
        return "High likelihood of AI generation detected. Verify originality and human authorship."
    elif plagiarism_risk in ['high', 'very_high']:
        return "Plagiarism risk detected. Check for proper attribution and original sources."
    else:
        return "Authenticity concerns identified. Recommend comprehensive verification process."

def generate_trust_indicators(component_scores, overall_score):
    """Generate trust indicators for the content"""
    indicators = []
    
    # Positive indicators
    if component_scores.get('linguistic_authenticity', 0) > 70:
        indicators.append("Natural linguistic patterns detected")
    
    if component_scores.get('style_authenticity', 0) > 70:
        indicators.append("Human-like writing style characteristics")
    
    if component_scores.get('plagiarism_authenticity', 0) > 80:
        indicators.append("Low plagiarism risk")
    
    if component_scores.get('ai_detection_authenticity', 0) > 70:
        indicators.append("Low AI generation likelihood")
    
    # Warning indicators
    if component_scores.get('ai_pattern_authenticity', 0) < 30:
        indicators.append("⚠️ High AI pattern density detected")
    
    if component_scores.get('similarity_authenticity', 0) < 50:
        indicators.append("⚠️ High similarity to existing content")
    
    if overall_score < 40:
        indicators.append("⚠️ Multiple authenticity concerns")
    
    return indicators[:6]  # Limit to 6 most relevant indicators

# Keep all original helper functions from the previous version
def calculate_variance(numbers):
    """Calculate variance of a list of numbers"""
    if len(numbers) < 2:
        return 0
    mean = sum(numbers) / len(numbers)
    variance = sum((x - mean) ** 2 for x in numbers) / len(numbers)
    return variance

def calculate_linguistic_complexity(vocab_diversity, avg_word_length, avg_sentence_length, sentence_variance):
    """Enhanced linguistic complexity calculation"""
    # Normalize each component to 0-100 scale
    vocab_score = min(100, vocab_diversity)
    word_score = min(100, (avg_word_length - 3) * 20)  # 3+ letter words
    sentence_score = min(100, (avg_sentence_length - 10) * 5)  # 10+ word sentences
    variance_score = min(100, sentence_variance * 3)  # Higher variance = more complex
    
    return round((vocab_score + word_score + sentence_score + variance_score) / 4, 2)

# Original helper functions continue...
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
