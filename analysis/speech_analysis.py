"""
Speech analysis module - Fact-checking and transcript processing
"""
import re
import secrets
from datetime import datetime
from flask import request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from utils.text_utils import extract_youtube_video_id
from analysis.news_analysis import perform_basic_news_analysis

def extract_claims_from_speech(text, mode='balanced'):
    """
    Extract factual claims from speech transcript
    More aggressive than news analysis for real-time checking
    """
    claims = []
    sentences = re.split(r'[.!?]+', text)
    
    # Claim indicators for speech
    indicators = {
        'statistics': [r'\d+\.?\d*\s*(?:percent|%)', r'\d+\.?\d*\s*(?:million|billion|trillion)'],
        'comparisons': ['more than', 'less than', 'increased', 'decreased', 'doubled', 'tripled'],
        'absolutes': ['always', 'never', 'every', 'none', 'all', 'no one'],
        'citations': ['according to', 'studies show', 'research indicates', 'data shows'],
        'temporal': ['first', 'last', 'newest', 'oldest', 'recently', 'historically'],
        'records': ['highest', 'lowest', 'biggest', 'smallest', 'record', 'unprecedented']
    }
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence.split()) < 5:  # Skip very short sentences
            continue
            
        # Check for claim indicators
        claim_score = 0
        for category, patterns in indicators.items():
            for pattern in patterns:
                if isinstance(pattern, str):
                    if pattern.lower() in sentence.lower():
                        claim_score += 1
                else:  # regex pattern
                    if re.search(pattern, sentence, re.IGNORECASE):
                        claim_score += 2
        
        # Add claim based on mode
        if mode == 'aggressive' and claim_score > 0:
            claims.append(sentence)
        elif mode == 'balanced' and claim_score > 1:
            claims.append(sentence)
        elif mode == 'conservative' and claim_score > 2:
            claims.append(sentence)
    
    return claims[:20]  # Limit to prevent overload

def speech_to_text():
    """
    Process audio and convert to text (placeholder for actual implementation)
    In production, this would integrate with speech recognition services
    """
    try:
        data = request.get_json()
        audio_data = data.get('audio')
        language = data.get('language', 'en-US')
        
        # In production, this would process the audio using speech recognition
        # For now, return a placeholder response
        return jsonify({
            'success': True,
            'transcript': 'Placeholder transcript text',
            'confidence': 0.95,
            'language': language
        })
        
    except Exception as e:
        print(f"Speech to text error: {e}")
        return jsonify({'error': 'Speech processing failed'}), 500

def stream_transcript():
    """
    Handle streaming audio transcription
    This would typically use WebSockets in production
    """
    try:
        data = request.get_json()
        stream_url = data.get('stream_url')
        
        # Placeholder for stream processing
        return jsonify({
            'success': True,
            'message': 'Stream processing started',
            'stream_id': secrets.token_urlsafe(16)
        })
        
    except Exception as e:
        print(f"Stream processing error: {e}")
        return jsonify({'error': 'Stream processing failed'}), 500

def batch_factcheck():
    """
    Perform batch fact-checking on multiple claims
    Optimized for real-time speech fact-checking
    """
    try:
        data = request.get_json()
        claims = data.get('claims', [])
        priority = data.get('priority', 'balanced')
        
        results = []
        
        for claim in claims[:10]:  # Limit to 10 claims per batch
            # Use existing news analysis with some modifications for claims
            analysis = perform_basic_news_analysis(claim)
            
            # Extract key fact-check data
            credibility = analysis.get('credibility_score', 50)
            
            # Determine verdict based on credibility
            if credibility > 80:
                verdict = 'true'
                confidence = credibility / 100
            elif credibility < 40:
                verdict = 'false'
                confidence = (100 - credibility) / 100
            else:
                verdict = 'unverified'
                confidence = 0.5
            
            results.append({
                'claim': claim,
                'verdict': verdict,
                'confidence': confidence,
                'credibility_score': credibility,
                'sources': analysis.get('cross_references', []),
                'bias': analysis.get('bias_indicators', {}).get('political_bias', 'unknown'),
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return jsonify({
            'success': True,
            'results': results,
            'processed': len(results),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"Batch fact-check error: {e}")
        return jsonify({'error': 'Batch fact-check failed'}), 500

def get_youtube_transcript():
    """
    Extract transcript from YouTube video
    """
    try:
        data = request.get_json()
        url = data.get('url', '')
        language = data.get('language', 'en')
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Extract video ID
        video_id = extract_youtube_video_id(url)
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400
        
        try:
            # Get transcript
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to find a transcript
            transcript = None
            try:
                transcript = transcript_list.find_manually_created_transcript([language.split('-')[0]])
            except:
                try:
                    transcript = transcript_list.find_transcript([language.split('-')[0]])
                except:
                    for t in transcript_list:
                        transcript = t
                        break
            
            if not transcript:
                return jsonify({'error': 'No transcript available for this video'}), 404
            
            # Fetch the actual transcript
            transcript_data = transcript.fetch()
            
            # Combine all text segments
            full_text = ' '.join([segment['text'] for segment in transcript_data])
            
            # Also create a version with timestamps
            segments_with_time = []
            for segment in transcript_data:
                segments_with_time.append({
                    'text': segment['text'],
                    'start': segment['start'],
                    'duration': segment.get('duration', 0)
                })
            
            return jsonify({
                'success': True,
                'transcript': full_text,
                'segments': segments_with_time[:100],
                'video_id': video_id,
                'video_url': f"https://www.youtube.com/watch?v={video_id}",
                'language': transcript.language,
                'language_code': transcript.language_code,
                'is_generated': transcript.is_generated,
                'word_count': len(full_text.split()),
                'duration_estimate': segments_with_time[-1]['start'] if segments_with_time else 0
            })
            
        except TranscriptsDisabled:
            return jsonify({'error': 'Transcripts are disabled for this video'}), 403
        except NoTranscriptFound:
            return jsonify({'error': 'No transcript found for this video'}), 404
        except VideoUnavailable:
            return jsonify({'error': 'Video is unavailable'}), 404
        except Exception as e:
            print(f"YouTube transcript error: {e}")
            return jsonify({'error': f'Failed to fetch transcript: {str(e)}'}), 500
            
    except Exception as e:
        print(f"YouTube endpoint error: {e}")
        return jsonify({'error': 'Failed to process request'}), 500

def export_speech_report():
    """
    Export speech fact-check report
    """
    try:
        data = request.get_json()
        transcript = data.get('transcript', '')
        fact_checks = data.get('fact_checks', [])
        statistics = data.get('statistics', {})
        duration = data.get('duration', '00:00')
        
        # Generate report
        report = {
            'title': 'Speech Fact-Check Report',
            'generated_at': datetime.utcnow().isoformat(),
            'duration': duration,
            'statistics': {
                'total_words': statistics.get('wordCount', 0),
                'claims_checked': statistics.get('claimsChecked', 0),
                'true_claims': statistics.get('trueCount', 0),
                'false_claims': statistics.get('falseCount', 0),
                'accuracy_rate': f"{(statistics.get('trueCount', 0) / max(statistics.get('claimsChecked', 1), 1) * 100):.1f}%"
            },
            'transcript': transcript,
            'fact_checks': fact_checks,
            'methodology': {
                'fact_check_sources': ['News Database', 'Fact-Check APIs', 'AI Analysis'],
                'confidence_threshold': 0.7,
                'bias_detection': True
            }
        }
        
        return jsonify({
            'success': True,
            'report': report,
            'download_url': f'/download/report/{secrets.token_urlsafe(16)}'  # Placeholder
        })
        
    except Exception as e:
        print(f"Export report error: {e}")
        return jsonify({'error': 'Export failed'}), 500
