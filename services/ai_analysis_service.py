"""
AI Analysis Service for Facts & Fakes AI
Professional AI detection using OpenAI GPT-4 and pattern analysis
"""
import os
import json
import time
import re
import math
from datetime import datetime
from collections import Counter
import statistics
from typing import Dict, Any, Optional, List

from .base_service import BaseAnalysisService

# Try to import OpenAI with proper error handling
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

class AIAnalysisService(BaseAnalysisService):
    """
    Professional AI detection service with OpenAI integration and pattern fallback
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # OpenAI configuration
        self.api_key = config.get('openai_api_key', '')
        self.model = config.get('openai_model', 'gpt-4')
        self.fallback_model = config.get('openai_fallback_model', 'gpt-3.5-turbo')
        self.client: Optional[OpenAI] = None
        
        # Analysis settings
        self.max_text_length = config.get('max_text_length', 3000)
        self.confidence_threshold = config.get('confidence_threshold', 70)
        
    def _initialize_service(self) -> bool:
        """
        Initialize OpenAI client and validate configuration
        """
        if not OPENAI_AVAILABLE:
            self.logger.warning("OpenAI library not available - install with: pip install openai>=1.0.0")
            return False
        
        if not self.api_key:
            self.logger.warning("OpenAI API key not provided")
            return False
        
        if not self.api_key.startswith('sk-'):
            self.logger.error("Invalid OpenAI API key format")
            return False
        
        try:
            # Initialize OpenAI client
            self.client = OpenAI(api_key=self.api_key)
            
            # Test the connection with a minimal request
            test_response = self.client.models.list()
            if test_response and test_response.data:
                self.logger.info("OpenAI client initialized and tested successfully")
                return True
            else:
                self.logger.error("OpenAI API test failed - no models returned")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            return False
    
    def analyze(self, content: str, **kwargs) -> Dict[str, Any]:
        """
        Main AI analysis function
        """
        # Validate content
        is_valid, error_message = self._validate_content(content)
        if not is_valid:
            return self._create_error_response(error_message, "validation_error")
        
        try:
            start_time = time.time()
            
            # Get analysis options
            use_openai = kwargs.get('use_openai', True) and self.is_available
            analysis_depth = kwargs.get('analysis_depth', 'comprehensive')
            
            # Perform analysis
            if use_openai and self.client:
                self.logger.info("Performing OpenAI-powered AI analysis")
                ai_analysis = self._openai_analysis(content, analysis_depth)
            else:
                self.logger.info("Performing pattern-based AI analysis")
                ai_analysis = None
            
            # Always perform pattern analysis for comparison and fallback
            pattern_analysis = self._comprehensive_pattern_analysis(content)
            
            # Combine results
            results = self._combine_analysis_results(ai_analysis, pattern_analysis)
            
            # Add metadata
            results['processing_time'] = round(time.time() - start_time, 2)
            results['analysis_method'] = 'OpenAI + Pattern Analysis' if ai_analysis else 'Pattern Analysis Only'
            results['service_available'] = self.is_available
            
            return self._create_success_response(results)
            
        except Exception as e:
            self.logger.error(f"AI analysis failed: {str(e)}")
            return self._create_error_response(f"Analysis failed: {str(e)}")
    
    def _openai_analysis(self, content: str, analysis_depth: str) -> Optional[Dict[str, Any]]:
        """
        Perform AI detection using OpenAI GPT-4
        """
        if not self.client:
            return None
        
        try:
            # Prepare content for analysis (limit length)
            analysis_text = content[:self.max_text_length] if len(content) > self.max_text_length else content
            
            # Create comprehensive prompt based on analysis depth
            prompt = self._create_analysis_prompt(analysis_text, analysis_depth)
            
            # Make API request with retry logic
            response = self._make_openai_request(prompt, analysis_text)
            
            if response:
                return self._parse_openai_response(response, analysis_text)
            
            return None
            
        except Exception as e:
            self.logger.error(f"OpenAI analysis error: {str(e)}")
            return None
    
    def _create_analysis_prompt(self, text: str, analysis_depth: str) -> str:
        """
        Create a comprehensive analysis prompt for OpenAI
        """
        base_prompt = f"""
Analyze this text for AI generation patterns. Focus on:
1. Perplexity (predictability of word choices)
2. Burstiness (sentence length and complexity variation)
3. Vocabulary patterns typical of AI models
4. Structural consistency and flow
5. Writing style authenticity

Text to analyze: "{text}"

Respond with ONLY valid JSON in this format:
{{
    "ai_probability": <0-100>,
    "confidence": <0-100>,
    "perplexity_score": <float>,
    "burstiness_score": <float>,
    "reasoning": "<detailed explanation>",
    "key_indicators": [
        {{"pattern": "<pattern_name>", "description": "<description>", "severity": "<low/medium/high>", "score": <0-100>}}
    ],
    "human_indicators": [
        {{"pattern": "<pattern_name>", "description": "<description>", "confidence": <0-100>}}
    ],
    "detected_models": ["<model_name_if_detected>"],
    "writing_style": {{
        "formality": "<formal/informal/mixed>",
        "consistency": <0-100>,
        "naturalness": <0-100>
    }}
}}
"""
        
        if analysis_depth == 'detailed':
            base_prompt += """
Also provide:
- Specific examples of AI-like phrases or structures
- Analysis of transition word usage patterns
- Evaluation of sentence structure uniformity
- Assessment of vocabulary sophistication vs. naturalness
"""
        
        return base_prompt
    
    def _make_openai_request(self, prompt: str, text: str, retry_count: int = 2) -> Optional[str]:
        """
        Make OpenAI API request with retry logic
        """
        for attempt in range(retry_count + 1):
            try:
                # Choose model based on attempt (fallback to cheaper model on retry)
                model = self.model if attempt == 0 else self.fallback_model
                
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert AI detection system. Analyze text for AI generation patterns and respond only with valid JSON."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=1000,
                    temperature=0.1,
                    timeout=30
                )
                
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                self.logger.warning(f"OpenAI request attempt {attempt + 1} failed: {str(e)}")
                if attempt == retry_count:
                    self.logger.error("All OpenAI request attempts failed")
                    return None
                time.sleep(1)  # Brief delay before retry
        
        return None
    
    def _parse_openai_response(self, response_text: str, original_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse and validate OpenAI response
        """
        try:
            # Clean response text
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            # Parse JSON
            analysis = json.loads(response_text)
            
            # Validate required fields
            required_fields = ['ai_probability', 'confidence', 'reasoning']
            for field in required_fields:
                if field not in analysis:
                    self.logger.warning(f"OpenAI response missing required field: {field}")
                    return None
            
            # Sanitize and validate values
            analysis['ai_probability'] = max(0, min(100, float(analysis.get('ai_probability', 0))))
            analysis['confidence'] = max(0, min(100, float(analysis.get('confidence', 0))))
            analysis['perplexity_score'] = float(analysis.get('perplexity_score', 0))
            analysis['burstiness_score'] = float(analysis.get('burstiness_score', 0))
            
            # Add metadata
            analysis['analysis_source'] = 'OpenAI GPT-4'
            analysis['text_length'] = len(original_text)
            analysis['model_used'] = self.model
            
            return analysis
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse OpenAI JSON response: {str(e)}")
            self.logger.debug(f"Raw response: {response_text[:500]}...")
            return None
        except (ValueError, TypeError) as e:
            self.logger.error(f"Invalid data in OpenAI response: {str(e)}")
            return None
    
    def _comprehensive_pattern_analysis(self, content: str) -> Dict[str, Any]:
        """
        Comprehensive pattern-based AI detection
        """
        # Calculate basic statistics
        stats = self._calculate_text_statistics(content)
        
        # Detect AI patterns
        patterns = self._detect_ai_patterns(content)
        
        # Calculate linguistic indicators
        indicators = self._calculate_linguistic_indicators(content)
        
        # Calculate advanced metrics
        advanced = self._calculate_advanced_metrics(content)
        
        # Calculate overall AI probability from patterns
        ai_probability = self._calculate_pattern_based_score(patterns, indicators, advanced, stats)
        
        return {
            'ai_probability': ai_probability,
            'confidence': 75,  # Pattern analysis confidence
            'statistics': stats,
            'detected_patterns': patterns,
            'indicators': indicators,
            'advanced_metrics': advanced,
            'analysis_source': 'Pattern Analysis'
        }
    
    def _calculate_text_statistics(self, text: str) -> Dict[str, Any]:
        """Calculate comprehensive text statistics"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'paragraph_count': len(paragraphs),
            'character_count': len(text),
            'average_sentence_length': len(words) / len(sentences) if sentences else 0,
            'average_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'reading_level': self._calculate_reading_level(words, sentences)
        }
    
    def _detect_ai_patterns(self, text: str) -> Dict[str, Any]:
        """Detect specific AI writing patterns"""
        text_lower = text.lower()
        
        # Common AI phrases
        ai_phrases = [
            'furthermore', 'moreover', 'in addition', 'additionally',
            'however', 'nevertheless', 'consequently', 'therefore',
            'it is important to note', 'it should be noted',
            'in conclusion', 'in summary', 'to summarize',
            'significant', 'substantial', 'considerable', 'remarkable',
            'comprehensive', 'extensive', 'various', 'numerous',
            'optimize', 'utilize', 'facilitate', 'implement',
            'unprecedented', 'paradigm', 'leverage', 'holistic'
        ]
        
        # Transition words (AI models overuse these)
        transition_words = [
            'furthermore', 'moreover', 'additionally', 'consequently',
            'nevertheless', 'however', 'therefore', 'thus', 'hence'
        ]
        
        # Count occurrences
        ai_phrase_count = sum(1 for phrase in ai_phrases if phrase in text_lower)
        transition_count = sum(1 for word in transition_words if word in text_lower)
        
        # Human indicators
        contractions = len(re.findall(r"\b\w+'\w+\b", text))
        personal_pronouns = len(re.findall(r'\b(i|me|my|myself|we|us|our|you|your)\b', text_lower))
        exclamations = len(re.findall(r'[!]{1,3}', text))
        questions = len(re.findall(r'[?]', text))
        informal_words = len(re.findall(r'\b(yeah|ok|okay|wow|cool|awesome|totally|basically|actually|literally)\b', text_lower))
        
        # Structural patterns
        repeated_phrases = self._count_repeated_phrases(text)
        quotes = len(re.findall(r'"[^"]*"', text))
        
        return {
            'ai_phrases': ai_phrase_count,
            'transition_words': transition_count,
            'contractions': contractions,
            'personal_pronouns': personal_pronouns,
            'exclamations': exclamations,
            'questions': questions,
            'informal_words': informal_words,
            'repeated_phrases': repeated_phrases,
            'quotes_found': quotes
        }
    
    def _calculate_linguistic_indicators(self, text: str) -> Dict[str, Any]:
        """Calculate advanced linguistic indicators"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not words or not sentences:
            return {}
        
        # Vocabulary diversity
        unique_words = len(set(word.lower().strip('.,!?;:') for word in words))
        vocabulary_diversity = (unique_words / len(words)) * 100
        
        # Sentence complexity variation
        sentence_lengths = [len(s.split()) for s in sentences]
        if len(sentence_lengths) > 1:
            mean_length = statistics.mean(sentence_lengths)
            std_length = statistics.stdev(sentence_lengths)
            sentence_complexity = (std_length / mean_length) * 100 if mean_length > 0 else 0
        else:
            sentence_complexity = 0
        
        # Coherence indicators
        connectors = ['because', 'since', 'although', 'while', 'whereas', 'if', 'unless', 'when', 'after', 'before']
        connector_count = sum(1 for word in words if word.lower() in connectors)
        coherence_score = min(100, (connector_count / len(sentences)) * 100)
        
        # Repetitive patterns
        word_counts = Counter(word.lower().strip('.,!?;:') for word in words)
        repetitive_words = sum(1 for count in word_counts.values() if count > 2)
        repetitive_score = min(100, (repetitive_words / unique_words) * 100) if unique_words > 0 else 0
        
        return {
            'vocabulary_diversity': round(vocabulary_diversity, 2),
            'sentence_complexity': round(sentence_complexity, 2),
            'coherence_score': round(coherence_score, 2),
            'repetitive_patterns': round(repetitive_score, 2)
        }
    
    def _calculate_advanced_metrics(self, text: str) -> Dict[str, Any]:
        """Calculate perplexity and burstiness metrics"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not words or not sentences:
            return {}
        
        # Simplified perplexity calculation
        word_counts = Counter(word.lower().strip('.,!?;:') for word in words)
        total_words = len(words)
        
        entropy = 0
        for count in word_counts.values():
            prob = count / total_words
            if prob > 0:
                entropy -= prob * math.log2(prob)
        
        perplexity_score = min(100, entropy * 8)
        
        # Burstiness calculation
        sentence_lengths = [len(s.split()) for s in sentences]
        
        if len(sentence_lengths) > 1:
            mean_length = statistics.mean(sentence_lengths)
            variance = statistics.variance(sentence_lengths)
            burstiness = variance / (mean_length ** 2) if mean_length > 0 else 0
            burstiness_score = min(100, burstiness * 50)
        else:
            burstiness_score = 0
        
        return {
            'perplexity_score': round(perplexity_score, 2),
            'burstiness_score': round(burstiness_score, 2)
        }
    
    def _calculate_pattern_based_score(self, patterns: Dict, indicators: Dict, advanced: Dict, stats: Dict) -> float:
        """Calculate AI probability based on detected patterns"""
        score = 25  # Base score
        
        # AI indicators (increase score)
        score += patterns.get('ai_phrases', 0) * 6
        score += patterns.get('transition_words', 0) * 4
        
        # Human indicators (decrease score)
        score -= patterns.get('contractions', 0) * 3
        score -= patterns.get('personal_pronouns', 0) * 2
        score -= patterns.get('informal_words', 0) * 3
        score -= patterns.get('exclamations', 0) * 2
        score -= patterns.get('questions', 0) * 1
        
        # Linguistic factors
        vocab_diversity = indicators.get('vocabulary_diversity', 50)
        sentence_complexity = indicators.get('sentence_complexity', 50)
        
        if vocab_diversity < 35:  # Low diversity suggests AI
            score += 12
        if sentence_complexity < 25:  # Low variation suggests AI
            score += 15
        
        # Advanced metrics
        perplexity = advanced.get('perplexity_score', 50)
        burstiness = advanced.get('burstiness_score', 50)
        
        if perplexity < 35:  # Low perplexity suggests AI
            score += 20
        if burstiness < 30:  # Low burstiness suggests AI
            score += 18
        
        # Text length factors
        word_count = stats.get('word_count', 0)
        avg_sentence_length = stats.get('average_sentence_length', 0)
        
        if avg_sentence_length > 22:  # Very long sentences
            score += 8
        if word_count > 500 and patterns.get('repeated_phrases', 0) > 3:
            score += 10
        
        return max(5, min(95, score))
    
    def _combine_analysis_results(self, openai_analysis: Optional[Dict], pattern_analysis: Dict) -> Dict[str, Any]:
        """Combine OpenAI and pattern analysis results"""
        
        if openai_analysis:
            # Use OpenAI as primary, pattern as supporting
            combined = openai_analysis.copy()
            combined['pattern_analysis'] = pattern_analysis
            combined['confidence'] = min(95, openai_analysis.get('confidence', 0) + 10)
            
            # Cross-validate scores
            openai_score = openai_analysis.get('ai_probability', 0)
            pattern_score = pattern_analysis.get('ai_probability', 0)
            score_difference = abs(openai_score - pattern_score)
            
            if score_difference > 30:
                # Large disagreement - reduce confidence
                combined['confidence'] = max(60, combined['confidence'] - 15)
                combined['score_discrepancy'] = {
                    'openai_score': openai_score,
                    'pattern_score': pattern_score,
                    'difference': score_difference,
                    'note': 'Significant disagreement between analysis methods'
                }
            
        else:
            # Use pattern analysis only
            combined = pattern_analysis.copy()
            combined['confidence'] = max(50, pattern_analysis.get('confidence', 0) - 10)
            combined['note'] = 'OpenAI analysis unavailable - pattern analysis only'
        
        return combined
    
    def _count_repeated_phrases(self, text: str) -> int:
        """Count repeated phrases in text"""
        words = text.lower().split()
        bigrams = []
        
        for i in range(len(words) - 1):
            bigrams.append(f"{words[i]} {words[i+1]}")
        
        bigram_counts = Counter(bigrams)
        return sum(1 for count in bigram_counts.values() if count > 1)
    
    def _calculate_reading_level(self, words: List[str], sentences: List[str]) -> str:
        """Calculate Flesch Reading Ease score"""
        if not words or not sentences:
            return "Unknown"
        
        syllables = sum(self._count_syllables(word) for word in words)
        
        # Flesch Reading Ease formula
        score = 206.835 - (1.015 * (len(words) / len(sentences))) - (84.6 * (syllables / len(words)))
        
        if score >= 90:
            return "Very Easy"
        elif score >= 80:
            return "Easy"
        elif score >= 70:
            return "Fairly Easy"
        elif score >= 60:
            return "Standard"
        elif score >= 50:
            return "Fairly Difficult"
        else:
            return "Difficult"
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word"""
        word = word.lower().strip('.,!?;:')
        vowels = "aeiouy"
        count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                count += 1
            prev_was_vowel = is_vowel
        
        if word.endswith('e'):
            count -= 1
        
        return max(1, count)
