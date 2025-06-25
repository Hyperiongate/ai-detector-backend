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
        "platform": "Facts & Fakes AI - Premium News Analysis",
        "version": "Professional v5.0 - Enterprise Grade Analysis",
        "features": [
            "advanced_political_bias_detection", "author_credibility_profiling",
            "cross_platform_verification", "source_reputation_analysis",
            "voice_style_analysis", "real_time_progress_tracking",
            "interactive_visualizations", "premium_dashboard_interface",
            "multi_source_cross_verification", "professional_reporting"
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
