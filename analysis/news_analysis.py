"""
Speech Analysis Module for Facts & Fakes AI
Handles speech-to-text conversion, claim extraction, and fact-checking
Enhanced with YouTube transcript support
"""

import logging
import json
import re
from datetime import datetime
from io import BytesIO

# YouTube transcript support
from youtube_transcript_api import YouTubeTranscriptApi

# PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch

# Other imports
import requests
import os

logger = logging.getLogger(__name__)

# Configuration
GOOGLE_FACT_CHECK_API_KEY = os.environ.get('GOOGLE_FACT_CHECK_API_KEY')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')

def get_youtube_transcript(video_url):
    """
    Extract transcript from YouTube video with enhanced error handling
    
    Args:
        video_url: YouTube video URL
        
    Returns:
        str: Full transcript text or None if unavailable
    """
    try:
        # Extract video ID from various YouTube URL formats
        video_id = extract_video_id(video_url)
        
        if not video_id:
            logger.error(f"Could not extract video ID from URL: {video_url}")
            return None
        
        logger.info(f"Fetching transcript for video ID: {video_id}")
        
        # Try to get transcript in order of preference
        transcript_list = None
        
        try:
            # First try to get manually created captions
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to find manual captions in English first
            for transcript in transcript_list:
                if transcript.language_code.startswith('en') and not transcript.is_generated:
                    logger.info(f"Found manual English transcript")
                    transcript_data = transcript.fetch()
                    return format_transcript(transcript_data)
            
            # If no manual English captions, try auto-generated English
            for transcript in transcript_list:
                if transcript.language_code.startswith('en') and transcript.is_generated:
                    logger.info(f"Using auto-generated English transcript")
                    transcript_data = transcript.fetch()
                    return format_transcript(transcript_data)
            
            # If no English, try to get any manual transcript and translate
            for transcript in transcript_list:
                if not transcript.is_generated:
                    logger.info(f"Found manual transcript in {transcript.language}, translating...")
                    try:
                        translated = transcript.translate('en')
                        transcript_data = translated.fetch()
                        return format_transcript(transcript_data)
                    except:
                        continue
                        
            # Last resort: any auto-generated transcript translated to English
            for transcript in transcript_list:
                try:
                    logger.info(f"Using auto-generated transcript in {transcript.language}, translating...")
                    translated = transcript.translate('en')
                    transcript_data = translated.fetch()
                    return format_transcript(transcript_data)
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"Error fetching transcript list: {str(e)}")
            
            # Fallback: try direct fetch
            try:
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
                return format_transcript(transcript_data)
            except:
                pass
        
        logger.error(f"No transcript available for video: {video_id}")
        return None
        
    except Exception as e:
        logger.error(f"YouTube transcript error: {str(e)}")
        return None

def extract_video_id(url):
    """
    Extract video ID from various YouTube URL formats
    
    Args:
        url: YouTube URL
        
    Returns:
        str: Video ID or None
    """
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def format_transcript(transcript_data):
    """
    Format transcript data into clean text
    
    Args:
        transcript_data: List of transcript segments
        
    Returns:
        str: Formatted transcript text
    """
    try:
        # Join all text segments with proper spacing
        formatted_text = ' '.join([segment['text'] for segment in transcript_data])
        
        # Clean up common transcript issues
        formatted_text = re.sub(r'\s+', ' ', formatted_text)  # Multiple spaces to single
        formatted_text = re.sub(r'\n+', ' ', formatted_text)  # Newlines to spaces
        formatted_text = formatted_text.strip()
        
        # Add basic punctuation if missing (simple heuristic)
        if formatted_text and not formatted_text[-1] in '.!?':
            formatted_text += '.'
            
        return formatted_text
        
    except Exception as e:
        logger.error(f"Error formatting transcript: {str(e)}")
        return ' '.join([str(segment.get('text', '')) for segment in transcript_data])

def extract_claims_from_speech(transcript):
    """
    Enhanced claim extraction specifically for speech/video transcripts
    
    Args:
        transcript: Full transcript text
        
    Returns:
        list: Extracted factual claims
    """
    if not transcript:
        return []
    
    claims = []
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', transcript)
    
    # Keywords that often indicate factual claims
    claim_indicators = [
        r'\b\d+\s*(?:percent|%)',  # Percentages
        r'\b\d+\s*(?:million|billion|thousand)',  # Large numbers
        r'\b(?:studies show|research shows|data shows)',  # Research claims
        r'\b(?:according to|based on|as reported)',  # Source references
        r'\b(?:increased by|decreased by|grew by|fell by)',  # Change metrics
        r'\b(?:costs?|prices?|rates?)\s*(?:is|are|was|were)',  # Economic claims
        r'\b(?:in \d{4}|last year|this year)',  # Time-based claims
        r'\b(?:first|largest|smallest|best|worst)\b',  # Superlatives
        r'\b(?:always|never|every|all|none)\b',  # Absolute statements
    ]
    
    # Process each sentence
    for sentence in sentences:
        sentence = sentence.strip()
        
        # Skip very short sentences
        if len(sentence) < 20:
            continue
            
        # Check if sentence contains claim indicators
        is_claim = False
        for pattern in claim_indicators:
            if re.search(pattern, sentence, re.IGNORECASE):
                is_claim = True
                break
        
        # Also include sentences with specific structures
        if not is_claim:
            # Check for "X is Y" structures with proper nouns
            if re.search(r'^[A-Z][a-z]+.*(?:is|are|was|were)\s+\w+', sentence):
                is_claim = True
        
        if is_claim and len(sentence) < 300:  # Avoid overly long claims
            claims.append(sentence)
    
    # If too few claims found, extract key statements
    if len(claims) < 3:
        # Extract longer, more substantive sentences
        substantive_sentences = [
            s.strip() for s in sentences 
            if 30 < len(s.strip()) < 200
        ]
        
        # Add up to 5 substantive sentences as potential claims
        for sentence in substantive_sentences[:5]:
            if sentence not in claims:
                claims.append(sentence)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_claims = []
    for claim in claims:
        if claim not in seen:
            seen.add(claim)
            unique_claims.append(claim)
    
    logger.info(f"Extracted {len(unique_claims)} claims from transcript")
    return unique_claims[:20]  # Limit to 20 claims for performance

def speech_to_text(file_path):
    """
    Convert speech audio file to text using speech recognition
    
    Args:
        file_path: Path to audio file
        
    Returns:
        str: Transcribed text or None
    """
    try:
        import speech_recognition as sr
        
        recognizer = sr.Recognizer()
        
        # Load audio file
        with sr.AudioFile(file_path) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source)
            audio_data = recognizer.record(source)
        
        # Try multiple recognition engines
        text = None
        
        # Try Google Speech Recognition first (no API key needed)
        try:
            text = recognizer.recognize_google(audio_data)
            logger.info("Successfully transcribed using Google Speech Recognition")
            return text
        except sr.UnknownValueError:
            logger.warning("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            logger.error(f"Google Speech Recognition error: {e}")
        
        # You could add other recognition engines here
        # For example: recognize_sphinx() for offline recognition
        
        return None
        
    except Exception as e:
        logger.error(f"Speech to text error: {str(e)}")
        return None

def batch_factcheck(claims, is_pro=True):
    """
    Fact-check multiple claims in batch
    
    Args:
        claims: List of claims to fact-check
        is_pro: Whether to use professional features
        
    Returns:
        list: Fact-check results for each claim
    """
    results = []
    
    for i, claim in enumerate(claims):
        logger.info(f"Fact-checking claim {i+1}/{len(claims)}: {claim[:100]}...")
        
        # For professional tier, use multiple fact-checking sources
        if is_pro and GOOGLE_FACT_CHECK_API_KEY:
            result = factcheck_with_google(claim)
            if not result or result.get('verdict') == 'UNVERIFIED':
                # Try additional sources
                result = factcheck_with_news_api(claim)
        else:
            # Basic tier - use simpler fact-checking
            result = basic_factcheck(claim)
        
        results.append(result)
    
    return results

def factcheck_with_google(claim):
    """
    Fact-check a claim using Google Fact Check API
    
    Args:
        claim: Claim text to verify
        
    Returns:
        dict: Fact-check result
    """
    if not GOOGLE_FACT_CHECK_API_KEY:
        return basic_factcheck(claim)
    
    try:
        url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        params = {
            'key': GOOGLE_FACT_CHECK_API_KEY,
            'query': claim,
            'languageCode': 'en'
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'claims' in data and len(data['claims']) > 0:
                # Get the first relevant claim review
                claim_review = data['claims'][0]['claimReview'][0] if 'claimReview' in data['claims'][0] else None
                
                if claim_review:
                    rating = claim_review.get('textualRating', 'Unknown')
                    
                    # Map ratings to verdicts
                    verdict_map = {
                        'true': 'TRUE',
                        'mostly true': 'TRUE',
                        'half true': 'PARTIALLY TRUE',
                        'mostly false': 'FALSE',
                        'false': 'FALSE',
                        'pants on fire': 'FALSE'
                    }
                    
                    verdict = 'UNVERIFIED'
                    for key, value in verdict_map.items():
                        if key in rating.lower():
                            verdict = value
                            break
                    
                    return {
                        'claim': claim,
                        'verdict': verdict,
                        'rating': rating,
                        'explanation': claim_review.get('title', ''),
                        'source': claim_review.get('publisher', {}).get('name', 'Google Fact Check'),
                        'url': claim_review.get('url', '')
                    }
        
        return basic_factcheck(claim)
        
    except Exception as e:
        logger.error(f"Google Fact Check API error: {str(e)}")
        return basic_factcheck(claim)

def factcheck_with_news_api(claim):
    """
    Fact-check using News API to find related articles
    
    Args:
        claim: Claim text to verify
        
    Returns:
        dict: Fact-check result
    """
    if not NEWS_API_KEY:
        return basic_factcheck(claim)
    
    try:
        # Extract key terms from claim
        key_terms = extract_key_terms(claim)
        query = ' '.join(key_terms[:3])  # Use top 3 key terms
        
        url = "https://newsapi.org/v2/everything"
        params = {
            'apiKey': NEWS_API_KEY,
            'q': query,
            'language': 'en',
            'sortBy': 'relevancy',
            'pageSize': 5
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if data['articles']:
                # Analyze sentiment of articles
                supporting = 0
                opposing = 0
                
                for article in data['articles']:
                    title = article.get('title', '').lower()
                    description = article.get('description', '').lower()
                    
                    # Simple sentiment analysis
                    if any(word in title + description for word in ['false', 'fake', 'debunk', 'myth', 'wrong']):
                        opposing += 1
                    elif any(word in title + description for word in ['true', 'confirm', 'verify', 'correct']):
                        supporting += 1
                
                # Determine verdict based on article sentiment
                if opposing > supporting:
                    verdict = 'LIKELY FALSE'
                elif supporting > opposing:
                    verdict = 'LIKELY TRUE'
                else:
                    verdict = 'UNVERIFIED'
                
                return {
                    'claim': claim,
                    'verdict': verdict,
                    'explanation': f"Based on {len(data['articles'])} news articles",
                    'source': 'News Analysis',
                    'supporting_articles': supporting,
                    'opposing_articles': opposing
                }
        
        return basic_factcheck(claim)
        
    except Exception as e:
        logger.error(f"News API error: {str(e)}")
        return basic_factcheck(claim)

def basic_factcheck(claim):
    """
    Basic fact-checking using pattern analysis
    
    Args:
        claim: Claim text to verify
        
    Returns:
        dict: Basic fact-check result
    """
    # Pattern-based analysis for common claim types
    
    # Check for obviously false patterns
    false_patterns = [
        r'earth is flat',
        r'vaccines? cause autism',
        r'climate change is (a )?hoax',
        r'moon landing was fake'
    ]
    
    for pattern in false_patterns:
        if re.search(pattern, claim, re.IGNORECASE):
            return {
                'claim': claim,
                'verdict': 'FALSE',
                'explanation': 'This claim contradicts established scientific consensus',
                'source': 'Pattern Analysis'
            }
    
    # Check for verifiable patterns
    verifiable_patterns = [
        r'water boils at 100\s*(?:degrees?\s*)?(?:celsius|c)',
        r'earth (?:revolves around|orbits) the sun',
        r'gravity (?:is|exists)'
    ]
    
    for pattern in verifiable_patterns:
        if re.search(pattern, claim, re.IGNORECASE):
            return {
                'claim': claim,
                'verdict': 'TRUE',
                'explanation': 'This is a well-established scientific fact',
                'source': 'Pattern Analysis'
            }
    
    # Check for specific numerical claims
    if re.search(r'\d+\s*(?:percent|%)', claim):
        return {
            'claim': claim,
            'verdict': 'UNVERIFIED',
            'explanation': 'Statistical claim requires specific source verification',
            'source': 'Pattern Analysis'
        }
    
    # Default response
    return {
        'claim': claim,
        'verdict': 'UNVERIFIED',
        'explanation': 'Unable to verify this claim without additional sources',
        'source': 'Pattern Analysis'
    }

def extract_key_terms(text):
    """
    Extract key terms from text for search queries
    
    Args:
        text: Input text
        
    Returns:
        list: Key terms
    """
    # Remove common words
    stopwords = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
                     'before', 'after', 'above', 'below', 'between', 'under', 'is', 'are',
                     'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did',
                     'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this',
                     'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'])
    
    # Extract words
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filter out stopwords and short words
    key_terms = [word for word in words if word not in stopwords and len(word) > 3]
    
    # Prioritize proper nouns, numbers, and longer words
    scored_terms = []
    for term in key_terms:
        score = len(term)  # Longer words get higher score
        
        # Boost score for capitalized words (proper nouns)
        if term[0].isupper():
            score += 5
        
        # Boost score for numbers
        if re.search(r'\d', term):
            score += 3
        
        scored_terms.append((term, score))
    
    # Sort by score and return top terms
    scored_terms.sort(key=lambda x: x[1], reverse=True)
    
    return [term for term, score in scored_terms]

def export_speech_report(results):
    """
    Export speech analysis results as a PDF report
    
    Args:
        results: Analysis results dictionary
        
    Returns:
        BytesIO: PDF buffer
    """
    try:
        # Create PDF buffer
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#4a90e2'),
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#357abd'),
            spaceAfter=12
        )
        
        normal_style = styles['BodyText']
        
        # Title
        title = Paragraph("Speech Fact-Check Analysis Report", title_style)
        elements.append(title)
        
        # Date
        date_text = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", normal_style)
        elements.append(date_text)
        elements.append(Spacer(1, 20))
        
        # Executive Summary
        elements.append(Paragraph("Executive Summary", heading_style))
        
        trust_score = results.get('trust_score', 50)
        summary_text = f"""
        This analysis evaluated {results.get('claims_analyzed', 0)} factual claims from the provided speech content.
        The overall credibility score is {trust_score}%, with {results.get('claims_verified', 0)} claims verified as accurate
        and {results.get('claims_false', 0)} claims identified as false or misleading.
        """
        
        elements.append(Paragraph(summary_text, normal_style))
        elements.append(Spacer(1, 20))
        
        # Statistics Table
        elements.append(Paragraph("Analysis Statistics", heading_style))
        
        stats_data = [
            ['Metric', 'Value'],
            ['Total Claims Analyzed', str(results.get('claims_analyzed', 0))],
            ['Verified Claims', str(results.get('claims_verified', 0))],
            ['False/Misleading Claims', str(results.get('claims_false', 0))],
            ['Unverified Claims', str(results.get('claims_analyzed', 0) - results.get('claims_verified', 0) - results.get('claims_false', 0))],
            ['Trust Score', f"{trust_score}%"],
            ['Word Count', str(results.get('word_count', 0))],
            ['Analysis Type', results.get('analysis_type', 'Basic').title()]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 30))
        
        # Detailed Fact-Check Results
        if results.get('fact_check_results'):
            elements.append(Paragraph("Detailed Fact-Check Results", heading_style))
            
            for i, fact_check in enumerate(results['fact_check_results'], 1):
                # Claim header
                claim_text = f"<b>Claim {i}:</b> {fact_check.get('claim', 'N/A')}"
                elements.append(Paragraph(claim_text, normal_style))
                
                # Verdict
                verdict = fact_check.get('verdict', 'UNVERIFIED')
                verdict_color = '#27ae60' if verdict in ['TRUE', 'VERIFIED'] else '#e74c3c' if verdict in ['FALSE', 'MISLEADING'] else '#f39c12'
                
                verdict_text = f"<b>Verdict:</b> <font color='{verdict_color}'>{verdict}</font>"
                elements.append(Paragraph(verdict_text, normal_style))
                
                # Explanation
                if fact_check.get('explanation'):
                    elements.append(Paragraph(f"<b>Explanation:</b> {fact_check['explanation']}", normal_style))
                
                # Source
                if fact_check.get('source'):
                    elements.append(Paragraph(f"<b>Source:</b> {fact_check['source']}", normal_style))
                
                elements.append(Spacer(1, 15))
        
        # Recommendations
        elements.append(PageBreak())
        elements.append(Paragraph("Recommendations", heading_style))
        
        if trust_score >= 80:
            recommendations = [
                "This speech demonstrates high credibility with mostly verified claims.",
                "The content appears suitable for citation and sharing.",
                "Consider cross-referencing any remaining unverified claims."
            ]
        elif trust_score >= 60:
            recommendations = [
                "This speech contains a mix of verified and unverified claims.",
                "Exercise caution when sharing or citing this content.",
                "Verify questionable claims with additional sources before use."
            ]
        else:
            recommendations = [
                "This speech contains significant false or misleading claims.",
                "Not recommended for citation without substantial fact-checking.",
                "Seek alternative sources for the information presented."
            ]
        
        for rec in recommendations:
            elements.append(Paragraph(f"• {rec}", normal_style))
        
        # Build PDF
        doc.build(elements)
        
        # Return buffer
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}")
        return None
