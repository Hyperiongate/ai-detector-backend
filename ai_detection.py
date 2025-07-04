"""
Real AI Detection Module
Accurate detection of AI-generated content using multiple methods
"""

import numpy as np
from collections import Counter
import re
from typing import Dict, List, Tuple
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from nltk.util import ngrams
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer
import textstat
from scipy import stats
import math

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

class RealAIDetector:
    def __init__(self):
        """Initialize AI detection models and resources"""
        self.sentence_model = None
        self.ai_classifier = None
        self.tokenizer = None
        self.initialize_models()
        
    def initialize_models(self):
        """Load pre-trained models for AI detection"""
        try:
            # Load sentence transformer for embeddings
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Load AI detection model (you can use different models)
            model_name = "Hello-SimpleAI/chatgpt-detector-roberta"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.ai_classifier = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            print("✓ AI detection models loaded successfully")
        except Exception as e:
            print(f"⚠ Warning: Could not load ML models: {e}")
            print("  Falling back to statistical methods only")
    
    def analyze(self, text: str) -> Dict:
        """
        Perform comprehensive AI detection analysis
        Returns detailed metrics and final AI probability
        """
        # Basic text statistics
        stats = self.calculate_text_statistics(text)
        
        # Linguistic features
        linguistic = self.analyze_linguistic_features(text)
        
        # Perplexity and burstiness
        perplexity = self.calculate_perplexity(text)
        burstiness = self.calculate_burstiness(text)
        
        # N-gram analysis
        ngram_score = self.analyze_ngram_patterns(text)
        
        # Repetition and pattern analysis
        patterns = self.detect_ai_patterns(text)
        
        # ML-based detection if available
        ml_score = self.ml_based_detection(text) if self.ai_classifier else None
        
        # Calculate final AI probability
        ai_probability = self.calculate_final_probability(
            stats, linguistic, perplexity, burstiness, 
            ngram_score, patterns, ml_score
        )
        
        return {
            'ai_probability': ai_probability,
            'human_probability': 100 - ai_probability,
            'detailed_metrics': {
                'perplexity': perplexity,
                'burstiness': burstiness,
                'linguistic_features': linguistic,
                'pattern_analysis': patterns,
                'ml_confidence': ml_score,
                'text_statistics': stats
            },
            'indicators': self.generate_indicators(ai_probability, patterns, linguistic),
            'confidence': self.calculate_confidence(perplexity, burstiness, ml_score)
        }
    
    def calculate_text_statistics(self, text: str) -> Dict:
        """Calculate basic text statistics"""
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        
        # Sentence length statistics
        sentence_lengths = [len(word_tokenize(s)) for s in sentences]
        
        # Word length statistics
        word_lengths = [len(w) for w in words if w.isalpha()]
        
        # Vocabulary richness
        unique_words = set(w.lower() for w in words if w.isalpha())
        vocabulary_diversity = len(unique_words) / len(words) if words else 0
        
        # Readability scores
        flesch_score = textstat.flesch_reading_ease(text)
        gunning_fog = textstat.gunning_fog(text)
        
        return {
            'sentence_count': len(sentences),
            'word_count': len(words),
            'avg_sentence_length': np.mean(sentence_lengths) if sentence_lengths else 0,
            'sentence_length_variance': np.var(sentence_lengths) if sentence_lengths else 0,
            'avg_word_length': np.mean(word_lengths) if word_lengths else 0,
            'vocabulary_diversity': vocabulary_diversity,
            'flesch_reading_ease': flesch_score,
            'gunning_fog': gunning_fog,
            'unique_word_ratio': len(unique_words) / len(words) if words else 0
        }
    
    def calculate_perplexity(self, text: str) -> float:
        """
        Calculate perplexity score
        Lower perplexity indicates more predictable text (AI-like)
        """
        words = word_tokenize(text.lower())
        if len(words) < 3:
            return 100.0
        
        # Calculate bigram and trigram frequencies
        bigrams = list(ngrams(words, 2))
        trigrams = list(ngrams(words, 3))
        
        bigram_freq = FreqDist(bigrams)
        trigram_freq = FreqDist(trigrams)
        
        # Calculate conditional probabilities
        perplexity_score = 0
        count = 0
        
        for trigram in trigrams:
            prefix = trigram[:2]
            if bigram_freq[prefix] > 0:
                # P(word3|word1,word2) = count(word1,word2,word3) / count(word1,word2)
                prob = trigram_freq[trigram] / bigram_freq[prefix]
                if prob > 0:
                    perplexity_score += -math.log2(prob)
                    count += 1
        
        # Average perplexity
        avg_perplexity = perplexity_score / count if count > 0 else 100.0
        
        # Normalize to 0-100 scale (lower = more AI-like)
        normalized = min(100, avg_perplexity * 10)
        
        return normalized
    
    def calculate_burstiness(self, text: str) -> float:
        """
        Calculate burstiness (variance in sentence lengths)
        Human text tends to be more bursty
        """
        sentences = sent_tokenize(text)
        if len(sentences) < 2:
            return 50.0
        
        # Get sentence lengths
        lengths = [len(word_tokenize(s)) for s in sentences]
        
        # Calculate mean and variance
        mean_length = np.mean(lengths)
        variance = np.var(lengths)
        
        # Burstiness score (higher = more human-like)
        if mean_length > 0:
            burstiness = (variance / mean_length) * 10
        else:
            burstiness = 0
        
        # Normalize to 0-100 scale
        return min(100, burstiness * 5)
    
    def analyze_linguistic_features(self, text: str) -> Dict:
        """Analyze linguistic features that distinguish human vs AI text"""
        words = word_tokenize(text)
        sentences = sent_tokenize(text)
        
        # Part-of-speech analysis
        pos_tags = nltk.pos_tag(words)
        pos_dist = FreqDist(tag for word, tag in pos_tags)
        
        # Calculate linguistic diversity
        adjective_ratio = (pos_dist['JJ'] + pos_dist['JJR'] + pos_dist['JJS']) / len(words)
        adverb_ratio = (pos_dist['RB'] + pos_dist['RBR'] + pos_dist['RBS']) / len(words)
        
        # Passive voice detection (simplified)
        passive_count = sum(1 for s in sentences if self._is_passive(s))
        passive_ratio = passive_count / len(sentences) if sentences else 0
        
        # Contraction usage (human indicator)
        contractions = ["n't", "'re", "'ve", "'ll", "'d", "'m", "'s"]
        contraction_count = sum(1 for w in words for c in contractions if c in w)
        
        # First person pronouns (human indicator)
        first_person = ['i', 'me', 'my', 'mine', 'myself', 'we', 'us', 'our', 'ours']
        first_person_count = sum(1 for w in words if w.lower() in first_person)
        
        return {
            'adjective_ratio': adjective_ratio,
            'adverb_ratio': adverb_ratio,
            'passive_voice_ratio': passive_ratio,
            'contraction_density': contraction_count / len(words) if words else 0,
            'first_person_density': first_person_count / len(words) if words else 0,
            'pos_diversity': len(pos_dist) / len(set(pos_tags)) if pos_tags else 0
        }
    
    def _is_passive(self, sentence: str) -> bool:
        """Simple passive voice detection"""
        passive_indicators = ['was', 'were', 'been', 'being', 'is', 'are', 'am']
        words = word_tokenize(sentence.lower())
        
        for i, word in enumerate(words[:-1]):
            if word in passive_indicators:
                # Check if followed by past participle (simplified)
                next_word = words[i+1]
                if next_word.endswith('ed') or next_word.endswith('en'):
                    return True
        return False
    
    def analyze_ngram_patterns(self, text: str) -> float:
        """
        Analyze n-gram patterns for AI detection
        AI text often has more predictable n-gram distributions
        """
        words = word_tokenize(text.lower())
        
        # Skip stopwords for better analysis
        from nltk.corpus import stopwords
        try:
            stop_words = set(stopwords.words('english'))
            words = [w for w in words if w.isalpha() and w not in stop_words]
        except:
            words = [w for w in words if w.isalpha()]
        
        if len(words) < 10:
            return 50.0
        
        # Analyze bigrams and trigrams
        bigrams = list(ngrams(words, 2))
        trigrams = list(ngrams(words, 3))
        
        # Calculate entropy (predictability)
        bigram_freq = FreqDist(bigrams)
        trigram_freq = FreqDist(trigrams)
        
        # Shannon entropy for bigrams
        total_bigrams = len(bigrams)
        bigram_entropy = -sum(
            (count/total_bigrams) * math.log2(count/total_bigrams)
            for count in bigram_freq.values()
        ) if total_bigrams > 0 else 0
        
        # Normalize entropy (higher = more human-like)
        max_entropy = math.log2(total_bigrams) if total_bigrams > 1 else 1
        normalized_entropy = (bigram_entropy / max_entropy) * 100 if max_entropy > 0 else 50
        
        return normalized_entropy
    
    def detect_ai_patterns(self, text: str) -> Dict:
        """Detect specific patterns common in AI-generated text"""
        text_lower = text.lower()
        
        # AI-typical phrases and transitions
        ai_phrases = [
            'it is important to note', 'it should be noted', 'it is worth noting',
            'in conclusion', 'in summary', 'to summarize',
            'furthermore', 'moreover', 'additionally', 'however',
            'on the other hand', 'nevertheless', 'consequently',
            'it is crucial', 'it is essential', 'it is vital',
            'delve into', 'dive into', 'explore the depths',
            'in today\'s world', 'in modern society', 'in the digital age',
            'the fact that', 'the idea that', 'the notion that',
            'shed light on', 'bring to light', 'highlight the importance'
        ]
        
        # Count AI phrase occurrences
        ai_phrase_count = sum(1 for phrase in ai_phrases if phrase in text_lower)
        
        # Repetitive structure detection
        sentences = sent_tokenize(text)
        sentence_starters = [s.split()[0].lower() for s in sentences if s.split()]
        starter_freq = FreqDist(sentence_starters)
        
        # Check for repetitive sentence structures
        repetitive_starters = sum(1 for count in starter_freq.values() if count > 2)
        
        # Perfect grammar score (AI tends to have fewer errors)
        grammar_errors = self._estimate_grammar_errors(text)
        
        # List pattern detection (AI loves lists)
        list_indicators = text.count('\n•') + text.count('\n-') + text.count('\n*') + \
                         text.count('\n1.') + text.count('\n2.') + text.count('\n3.')
        
        return {
            'ai_phrase_density': ai_phrase_count / len(sentences) if sentences else 0,
            'repetitive_structures': repetitive_starters,
            'grammar_perfection': 100 - (grammar_errors * 10),
            'list_usage': list_indicators,
            'transition_density': ai_phrase_count,
            'formulaic_score': (ai_phrase_count + repetitive_starters) / len(sentences) if sentences else 0
        }
    
    def _estimate_grammar_errors(self, text: str) -> int:
        """Estimate grammar errors (simplified)"""
        # This is a simplified version - in production, use language_tool_python
        error_patterns = [
            r'\s+[,.]',  # Space before punctuation
            r'[a-z]\.[A-Z]',  # Missing space after period
            r'\b(a)\s+[aeiou]',  # 'a' before vowel
            r'\b(an)\s+[^aeiou]',  # 'an' before consonant
        ]
        
        errors = 0
        for pattern in error_patterns:
            errors += len(re.findall(pattern, text))
        
        return errors
    
    def ml_based_detection(self, text: str) -> float:
        """Use pre-trained transformer model for AI detection"""
        if not self.ai_classifier or not self.tokenizer:
            return None
        
        try:
            # Tokenize and prepare input
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, 
                                   max_length=512, padding=True)
            
            # Get model predictions
            with torch.no_grad():
                outputs = self.ai_classifier(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                
            # Extract AI probability
            ai_prob = predictions[0][1].item() * 100  # Assuming label 1 is AI
            
            return ai_prob
            
        except Exception as e:
            print(f"ML detection error: {e}")
            return None
    
    def calculate_final_probability(self, stats, linguistic, perplexity, 
                                   burstiness, ngram_score, patterns, ml_score):
        """Calculate final AI probability based on all metrics"""
        
        # Weight different factors
        weights = {
            'perplexity': 0.20,
            'burstiness': 0.15,
            'linguistic': 0.15,
            'patterns': 0.20,
            'ngrams': 0.10,
            'ml_model': 0.20
        }
        
        # Calculate component scores
        scores = {}
        
        # Perplexity score (lower = more AI)
        scores['perplexity'] = 100 - perplexity
        
        # Burstiness score (lower = more AI)
        scores['burstiness'] = 100 - burstiness
        
        # Linguistic features score
        ling_score = 0
        if linguistic['contraction_density'] < 0.001:
            ling_score += 30
        if linguistic['first_person_density'] < 0.005:
            ling_score += 30
        if linguistic['passive_voice_ratio'] > 0.3:
            ling_score += 20
        scores['linguistic'] = ling_score
        
        # Pattern score
        pattern_score = min(100, patterns['ai_phrase_density'] * 200 + 
                           patterns['formulaic_score'] * 100)
        scores['patterns'] = pattern_score
        
        # N-gram score (lower entropy = more AI)
        scores['ngrams'] = 100 - ngram_score
        
        # ML model score
        if ml_score is not None:
            scores['ml_model'] = ml_score
        else:
            # Redistribute weight if ML not available
            weights['perplexity'] += 0.04
            weights['burstiness'] += 0.04
            weights['linguistic'] += 0.04
            weights['patterns'] += 0.04
            weights['ngrams'] += 0.04
            scores['ml_model'] = 0
            weights['ml_model'] = 0
        
        # Calculate weighted average
        total_weight = sum(weights.values())
        ai_probability = sum(scores[key] * weights[key] for key in scores) / total_weight
        
        # Apply bounds
        ai_probability = max(5, min(95, ai_probability))
        
        return round(ai_probability)
    
    def generate_indicators(self, ai_prob, patterns, linguistic):
        """Generate human-readable indicators"""
        indicators = []
        
        if ai_prob > 70:
            indicators.append("High AI probability detected")
            if patterns['ai_phrase_density'] > 0.3:
                indicators.append("Excessive use of AI-typical phrases")
            if patterns['formulaic_score'] > 0.5:
                indicators.append("Highly formulaic writing structure")
                
        if linguistic['contraction_density'] < 0.001:
            indicators.append("No contractions found (unusual for human text)")
            
        if linguistic['first_person_density'] < 0.005:
            indicators.append("Lack of personal pronouns")
            
        return indicators
    
    def calculate_confidence(self, perplexity, burstiness, ml_score):
        """Calculate confidence in the detection"""
        confidence_factors = []
        
        # Strong signals increase confidence
        if perplexity < 30 or perplexity > 80:
            confidence_factors.append(20)
        if burstiness < 20 or burstiness > 80:
            confidence_factors.append(20)
        if ml_score is not None:
            confidence_factors.append(30)
            
        base_confidence = 50
        total_confidence = base_confidence + sum(confidence_factors)
        
        return min(95, total_confidence)
