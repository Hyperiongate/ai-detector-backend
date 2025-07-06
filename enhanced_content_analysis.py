"""
Enhanced Content Analysis Module for NewsVerify Pro
This module provides sophisticated content analysis features for news articles
"""

import re
import json
from typing import Dict, List, Tuple, Any
from collections import Counter, defaultdict
from datetime import datetime
import nltk
from textstat import flesch_reading_ease, flesch_kincaid_grade, gunning_fog
from transformers import pipeline
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('vader_lexicon', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('maxent_ne_chunker', quiet=True)
nltk.download('words', quiet=True)

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag


class EnhancedContentAnalyzer:
    """
    Enhanced content analyzer with sophisticated NLP capabilities
    """
    
    def __init__(self):
        # Initialize models
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
        
        # Initialize spaCy for advanced NLP
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            # Fallback if spaCy model not installed
            self.nlp = None
            
        # Initialize transformer models for advanced analysis
        try:
            # Only load if explicitly needed to save memory
            self.emotion_classifier = None
        except:
            self.emotion_classifier = None
            
    def analyze_article(self, text: str, url: str = "") -> Dict[str, Any]:
        """
        Perform comprehensive analysis on news article
        """
        analysis_results = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "content_summary": self._generate_summary(text),
            "topic_detection": self._detect_topics(text),
            "key_claims": self._extract_key_claims(text),
            "quote_analysis": self._analyze_quotes(text),
            "statistical_claims": self._extract_statistical_claims(text),
            "story_structure": self._analyze_story_structure(text),
            "source_attribution": self._analyze_sources(text),
            "readability": self._calculate_readability(text),
            "emotional_tone": self._analyze_emotional_tone(text),
            "overall_metrics": self._calculate_overall_metrics(text)
        }
        
        return analysis_results
    
    def _generate_summary(self, text: str) -> Dict[str, Any]:
        """
        Generate content summary with key points
        """
        sentences = sent_tokenize(text)
        
        # Extract first paragraph as lead
        lead_paragraph = sentences[0] if sentences else ""
        
        # Extract key sentences using TF-IDF
        if len(sentences) > 3:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(sentences)
            scores = tfidf_matrix.sum(axis=1).A1
            top_indices = scores.argsort()[-3:][::-1]
            key_sentences = [sentences[i] for i in top_indices]
        else:
            key_sentences = sentences
            
        return {
            "lead_paragraph": lead_paragraph,
            "key_sentences": key_sentences,
            "word_count": len(word_tokenize(text)),
            "sentence_count": len(sentences),
            "average_sentence_length": len(word_tokenize(text)) / len(sentences) if sentences else 0
        }
    
    def _detect_topics(self, text: str) -> Dict[str, Any]:
        """
        Enhanced topic detection using multiple methods
        """
        topics = {
            "keyword_topics": self._keyword_based_topics(text),
            "entity_topics": self._entity_based_topics(text),
            "lda_topics": self._lda_topic_modeling(text),
            "category_scores": self._calculate_category_scores(text)
        }
        
        return topics
    
    def _keyword_based_topics(self, text: str) -> List[str]:
        """
        Extract topics based on keyword frequency
        """
        # Define topic keywords
        topic_keywords = {
            "politics": ["election", "president", "congress", "senate", "policy", "government", "political", "democrat", "republican"],
            "economy": ["economy", "stock", "market", "finance", "trade", "gdp", "inflation", "recession", "investment"],
            "health": ["health", "medical", "disease", "vaccine", "hospital", "doctor", "patient", "treatment", "covid"],
            "technology": ["technology", "ai", "software", "internet", "cyber", "data", "digital", "computer", "innovation"],
            "climate": ["climate", "environment", "pollution", "carbon", "renewable", "sustainability", "global warming"],
            "crime": ["crime", "police", "arrest", "criminal", "investigation", "murder", "theft", "justice"],
            "education": ["education", "school", "student", "teacher", "university", "college", "learning", "academic"],
            "sports": ["sports", "game", "team", "player", "championship", "tournament", "athlete", "coach"]
        }
        
        text_lower = text.lower()
        detected_topics = []
        topic_scores = {}
        
        for topic, keywords in topic_keywords.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            if score > 0:
                topic_scores[topic] = score
                
        # Return top 3 topics
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, score in sorted_topics[:3]]
    
    def _entity_based_topics(self, text: str) -> Dict[str, List[str]]:
        """
        Extract topics based on named entities
        """
        if self.nlp:
            doc = self.nlp(text)
            entities = {
                "people": [ent.text for ent in doc.ents if ent.label_ == "PERSON"],
                "organizations": [ent.text for ent in doc.ents if ent.label_ == "ORG"],
                "locations": [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]],
                "dates": [ent.text for ent in doc.ents if ent.label_ == "DATE"],
                "money": [ent.text for ent in doc.ents if ent.label_ == "MONEY"],
                "percentages": [ent.text for ent in doc.ents if ent.label_ == "PERCENT"]
            }
        else:
            # Fallback to NLTK
            entities = self._nltk_entity_extraction(text)
            
        return entities
    
    def _nltk_entity_extraction(self, text: str) -> Dict[str, List[str]]:
        """
        Fallback entity extraction using NLTK
        """
        tokens = word_tokenize(text)
        pos_tags = pos_tag(tokens)
        chunks = ne_chunk(pos_tags, binary=False)
        
        entities = defaultdict(list)
        for chunk in chunks:
            if hasattr(chunk, 'label'):
                entity_text = ' '.join(c[0] for c in chunk)
                entities[chunk.label()].append(entity_text)
                
        return dict(entities)
    
    def _lda_topic_modeling(self, text: str, n_topics: int = 3) -> List[Dict[str, Any]]:
        """
        Use Latent Dirichlet Allocation for topic modeling
        """
        try:
            # Tokenize into sentences for LDA
            sentences = sent_tokenize(text)
            if len(sentences) < 5:
                return []
                
            # Vectorize
            vectorizer = TfidfVectorizer(max_features=50, stop_words='english')
            doc_term_matrix = vectorizer.fit_transform(sentences)
            
            # Apply LDA
            lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
            lda.fit(doc_term_matrix)
            
            # Extract topics
            feature_names = vectorizer.get_feature_names_out()
            topics = []
            
            for topic_idx, topic in enumerate(lda.components_):
                top_indices = topic.argsort()[-10:][::-1]
                top_words = [feature_names[i] for i in top_indices]
                topics.append({
                    "topic_id": topic_idx,
                    "top_words": top_words[:5],
                    "weight": float(np.max(topic))
                })
                
            return topics
        except:
            return []
    
    def _calculate_category_scores(self, text: str) -> Dict[str, float]:
        """
        Calculate probability scores for different news categories
        """
        # This would ideally use a trained classifier
        # For now, using keyword density as a proxy
        categories = {
            "hard_news": ["breaking", "urgent", "official", "statement", "announced"],
            "opinion": ["believe", "think", "should", "must", "opinion", "argue"],
            "analysis": ["analysis", "examine", "investigate", "study", "research"],
            "feature": ["story", "journey", "experience", "life", "personal"]
        }
        
        text_lower = text.lower()
        scores = {}
        
        for category, keywords in categories.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            scores[category] = score / len(text_lower.split()) if text_lower.split() else 0
            
        return scores
    
    def _extract_key_claims(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract main claims and statements from the article
        """
        sentences = sent_tokenize(text)
        claims = []
        
        # Patterns for identifying claims
        claim_patterns = [
            r"(?:study|research|report|survey|poll) (?:shows|finds|reveals|indicates|suggests)",
            r"according to (?:the )?\w+",
            r"(?:experts?|scientists?|researchers?|analysts?) (?:say|believe|claim|argue)",
            r"(?:will|would|could|may|might) (?:lead to|result in|cause)",
            r"(?:increased?|decreased?|rose|fell|jumped|dropped) by \d+",
            r"(?:is|are|was|were) (?:the )?\w+ (?:cause|reason|factor)",
        ]
        
        for idx, sentence in enumerate(sentences):
            sentence_lower = sentence.lower()
            
            # Check if sentence contains claim patterns
            is_claim = any(re.search(pattern, sentence_lower) for pattern in claim_patterns)
            
            # Also check for factual statements with numbers
            contains_numbers = bool(re.search(r'\d+', sentence))
            
            # Check for attribution
            has_attribution = bool(re.search(r'(?:said|says|stated|according to|reported)', sentence_lower))
            
            if is_claim or (contains_numbers and has_attribution):
                # Classify claim type
                claim_type = "statistical" if contains_numbers else "qualitative"
                if "will" in sentence_lower or "would" in sentence_lower:
                    claim_type = "predictive"
                elif "caused" in sentence_lower or "because" in sentence_lower:
                    claim_type = "causal"
                    
                claims.append({
                    "text": sentence,
                    "position": idx,
                    "type": claim_type,
                    "has_attribution": has_attribution,
                    "confidence": 0.8 if is_claim else 0.6
                })
                
        return claims[:10]  # Return top 10 claims
    
    def _analyze_quotes(self, text: str) -> Dict[str, Any]:
        """
        Analyze quotes in the article
        """
        # Patterns for detecting quotes
        direct_quote_pattern = r'"([^"]+)"(?:\s*(?:said|says|stated|added|explained|told|according to)\s+(.+?)(?:\.|,))?'
        indirect_quote_pattern = r'(?:(.+?)\s+(?:said|says|stated|added|explained|told)\s+(?:that\s+)?(.+?)(?:\.|,))'
        
        direct_quotes = re.findall(direct_quote_pattern, text, re.IGNORECASE)
        indirect_quotes = re.findall(indirect_quote_pattern, text, re.IGNORECASE)
        
        # Extract speakers
        speakers = []
        for quote, speaker in direct_quotes:
            if speaker:
                speakers.append(speaker.strip())
                
        for speaker, quote in indirect_quotes:
            if speaker and len(speaker.split()) < 10:  # Avoid false positives
                speakers.append(speaker.strip())
                
        # Clean and count speakers
        speaker_counts = Counter(speakers)
        
        # Analyze quote distribution
        sentences = sent_tokenize(text)
        quote_positions = []
        for idx, sent in enumerate(sentences):
            if '"' in sent or re.search(r'\b(?:said|says|stated|told)\b', sent, re.IGNORECASE):
                quote_positions.append(idx / len(sentences))  # Normalize position
                
        return {
            "total_quotes": len(direct_quotes) + len(indirect_quotes),
            "direct_quotes": len(direct_quotes),
            "indirect_quotes": len(indirect_quotes),
            "unique_speakers": len(set(speakers)),
            "top_speakers": dict(speaker_counts.most_common(5)),
            "quote_density": len(quote_positions) / len(sentences) if sentences else 0,
            "quote_distribution": {
                "first_third": sum(1 for p in quote_positions if p < 0.33),
                "middle_third": sum(1 for p in quote_positions if 0.33 <= p < 0.66),
                "last_third": sum(1 for p in quote_positions if p >= 0.66)
            }
        }
    
    def _extract_statistical_claims(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract statistical claims and data points
        """
        statistical_patterns = [
            (r'(\d+(?:\.\d+)?)\s*(?:percent|%)', 'percentage'),
            (r'\$\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:billion|million|thousand)?', 'monetary'),
            (r'(\d+(?:,\d+)*)\s+(?:people|deaths|cases|incidents)', 'count'),
            (r'(?:increased?|decreased?|rose|fell|jumped|dropped)\s+(?:by\s+)?(\d+(?:\.\d+)?)\s*(?:percent|%)?', 'change'),
            (r'(\d+)\s+(?:out of|of)\s+(\d+)', 'ratio'),
            (r'(?:between|from)\s+(\d+)\s+(?:and|to)\s+(\d+)', 'range'),
        ]
        
        statistical_claims = []
        sentences = sent_tokenize(text)
        
        for sent_idx, sentence in enumerate(sentences):
            for pattern, claim_type in statistical_patterns:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    # Extract context
                    context_start = max(0, sentence.find(str(match[0] if isinstance(match, tuple) else match)) - 50)
                    context_end = min(len(sentence), context_start + 100)
                    context = sentence[context_start:context_end]
                    
                    statistical_claims.append({
                        "value": match,
                        "type": claim_type,
                        "context": context,
                        "sentence": sentence,
                        "position": sent_idx,
                        "needs_verification": True
                    })
                    
        return statistical_claims
    
    def _analyze_story_structure(self, text: str) -> Dict[str, Any]:
        """
        Analyze the structure of the news story
        """
        sentences = sent_tokenize(text)
        paragraphs = text.split('\n\n')
        
        # Check for 5W1H in first few paragraphs
        first_paragraphs = ' '.join(paragraphs[:3]) if len(paragraphs) >= 3 else text
        
        five_w1h = {
            "who": bool(re.search(r'\b(?:who|person|people|official|president|ceo|minister)\b', first_paragraphs, re.IGNORECASE)),
            "what": bool(re.search(r'\b(?:what|happened|occurred|announced|decided|discovered)\b', first_paragraphs, re.IGNORECASE)),
            "when": bool(re.search(r'\b(?:when|today|yesterday|monday|tuesday|wednesday|thursday|friday|saturday|sunday|january|february|march|april|may|june|july|august|september|october|november|december|\d{4})\b', first_paragraphs, re.IGNORECASE)),
            "where": bool(re.search(r'\b(?:where|location|city|country|state|building|street)\b', first_paragraphs, re.IGNORECASE)),
            "why": bool(re.search(r'\b(?:why|because|reason|cause|due to)\b', first_paragraphs, re.IGNORECASE)),
            "how": bool(re.search(r'\b(?:how|method|process|way|means)\b', first_paragraphs, re.IGNORECASE))
        }
        
        # Check for inverted pyramid structure
        paragraph_lengths = [len(word_tokenize(p)) for p in paragraphs if p.strip()]
        is_inverted_pyramid = False
        if len(paragraph_lengths) >= 3:
            # Check if first paragraph is substantial and later ones are shorter
            is_inverted_pyramid = paragraph_lengths[0] > np.mean(paragraph_lengths[1:])
            
        # Analyze sections
        has_conclusion = bool(re.search(r'\b(?:in conclusion|finally|ultimately|in summary)\b', text[-500:], re.IGNORECASE))
        has_background = bool(re.search(r'\b(?:background|history|previously|context)\b', text, re.IGNORECASE))
        
        return {
            "total_paragraphs": len(paragraphs),
            "average_paragraph_length": np.mean(paragraph_lengths) if paragraph_lengths else 0,
            "five_w1h_coverage": five_w1h,
            "five_w1h_score": sum(five_w1h.values()) / 6,
            "follows_inverted_pyramid": is_inverted_pyramid,
            "has_clear_lead": len(paragraphs[0].split()) > 20 if paragraphs else False,
            "has_conclusion": has_conclusion,
            "has_background_context": has_background,
            "structure_type": self._determine_structure_type(text, paragraphs)
        }
    
    def _determine_structure_type(self, text: str, paragraphs: List[str]) -> str:
        """
        Determine the type of article structure
        """
        if len(paragraphs) < 3:
            return "brief"
            
        # Check for different article types
        if re.search(r'\b(?:opinion|editorial|commentary)\b', text[:200], re.IGNORECASE):
            return "opinion"
        elif re.search(r'\b(?:analysis|examine|investigate)\b', text[:200], re.IGNORECASE):
            return "analysis"
        elif re.search(r'\b(?:breaking|urgent|just in)\b', text[:200], re.IGNORECASE):
            return "breaking_news"
        elif re.search(r'\b(?:feature|profile|story of)\b', text[:200], re.IGNORECASE):
            return "feature"
        else:
            return "standard_news"
    
    def _analyze_sources(self, text: str) -> Dict[str, Any]:
        """
        Analyze source attribution in the article
        """
        # Patterns for source attribution
        source_patterns = [
            r'according to\s+(?:the\s+)?([^,\.\n]+)',
            r'([^,\.\n]+?)\s+(?:said|says|stated|told|confirmed|announced)',
            r'(?:spokesperson|representative|official)\s+(?:for|from)\s+([^,\.\n]+)',
            r'(?:study|report|survey|research)\s+(?:by|from)\s+([^,\.\n]+)',
            r'([^,\.\n]+?),\s+(?:a|an|the)\s+(?:expert|analyst|professor|researcher)',
        ]
        
        sources = []
        anonymous_patterns = [
            r'(?:sources?|officials?|insiders?)\s+(?:said|say|told)',
            r'(?:someone|people)\s+familiar with',
            r'on condition of anonymity',
            r'who asked not to be (?:named|identified)',
            r'speaking on background'
        ]
        
        for pattern in source_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            sources.extend([m.strip() for m in matches if isinstance(m, str) and len(m.split()) < 10])
            
        # Count anonymous sources
        anonymous_count = sum(1 for pattern in anonymous_patterns if re.search(pattern, text, re.IGNORECASE))
        
        # Categorize sources
        source_types = {
            "government": [],
            "academic": [],
            "corporate": [],
            "expert": [],
            "witness": [],
            "document": []
        }
        
        for source in sources:
            source_lower = source.lower()
            if any(word in source_lower for word in ["government", "minister", "department", "agency", "official"]):
                source_types["government"].append(source)
            elif any(word in source_lower for word in ["university", "professor", "researcher", "study"]):
                source_types["academic"].append(source)
            elif any(word in source_lower for word in ["company", "corporation", "ceo", "executive"]):
                source_types["corporate"].append(source)
            elif any(word in source_lower for word in ["expert", "analyst", "specialist"]):
                source_types["expert"].append(source)
            elif any(word in source_lower for word in ["witness", "resident", "victim"]):
                source_types["witness"].append(source)
            elif any(word in source_lower for word in ["report", "document", "filing", "statement"]):
                source_types["document"].append(source)
                
        # Calculate diversity score
        active_categories = sum(1 for cat in source_types.values() if cat)
        diversity_score = active_categories / len(source_types) if source_types else 0
        
        return {
            "total_sources": len(set(sources)),
            "named_sources": len(set(sources)) - anonymous_count,
            "anonymous_sources": anonymous_count,
            "source_diversity_score": diversity_score,
            "source_categories": {k: len(set(v)) for k, v in source_types.items()},
            "top_cited_sources": dict(Counter(sources).most_common(5)),
            "attribution_density": len(sources) / len(sent_tokenize(text)) if sent_tokenize(text) else 0
        }
    
    def _calculate_readability(self, text: str) -> Dict[str, Any]:
        """
        Calculate various readability metrics
        """
        # Basic metrics
        words = word_tokenize(text)
        sentences = sent_tokenize(text)
        syllables = self._count_syllables(text)
        
        # Calculate various readability scores
        readability_scores = {
            "flesch_reading_ease": flesch_reading_ease(text),
            "flesch_kincaid_grade": flesch_kincaid_grade(text),
            "gunning_fog": gunning_fog(text),
            "avg_words_per_sentence": len(words) / len(sentences) if sentences else 0,
            "avg_syllables_per_word": syllables / len(words) if words else 0,
            "complex_word_percentage": self._calculate_complex_words(words) / len(words) * 100 if words else 0
        }
        
        # Interpret scores
        fre = readability_scores["flesch_reading_ease"]
        if fre >= 90:
            difficulty = "very_easy"
            education_level = "5th grade"
        elif fre >= 80:
            difficulty = "easy"
            education_level = "6th grade"
        elif fre >= 70:
            difficulty = "fairly_easy"
            education_level = "7th grade"
        elif fre >= 60:
            difficulty = "standard"
            education_level = "8th-9th grade"
        elif fre >= 50:
            difficulty = "fairly_difficult"
            education_level = "10th-12th grade"
        elif fre >= 30:
            difficulty = "difficult"
            education_level = "college"
        else:
            difficulty = "very_difficult"
            education_level = "graduate"
            
        readability_scores.update({
            "difficulty_level": difficulty,
            "education_level": education_level,
            "sentence_variety": self._calculate_sentence_variety(sentences),
            "vocabulary_richness": len(set(words)) / len(words) if words else 0
        })
        
        return readability_scores
    
    def _count_syllables(self, text: str) -> int:
        """
        Count syllables in text
        """
        vowels = "aeiouAEIOU"
        syllable_count = 0
        words = word_tokenize(text)
        
        for word in words:
            word_syllables = 0
            previous_was_vowel = False
            
            for char in word:
                if char in vowels:
                    if not previous_was_vowel:
                        word_syllables += 1
                    previous_was_vowel = True
                else:
                    previous_was_vowel = False
                    
            # Adjust for silent e
            if word.endswith('e') and word_syllables > 1:
                word_syllables -= 1
                
            # Ensure at least one syllable per word
            if word_syllables == 0:
                word_syllables = 1
                
            syllable_count += word_syllables
            
        return syllable_count
    
    def _calculate_complex_words(self, words: List[str]) -> int:
        """
        Count words with 3+ syllables
        """
        complex_count = 0
        for word in words:
            if self._count_syllables(word) >= 3:
                complex_count += 1
        return complex_count
    
    def _calculate_sentence_variety(self, sentences: List[str]) -> float:
        """
        Calculate variety in sentence lengths
        """
        if len(sentences) < 2:
            return 0.0
            
        lengths = [len(word_tokenize(sent)) for sent in sentences]
        return float(np.std(lengths))
    
    def _analyze_emotional_tone(self, text: str) -> Dict[str, Any]:
        """
        Analyze emotional tone and sentiment
        """
        # Basic sentiment analysis
        sentiment_scores = self.sia.polarity_scores(text)
        
        # Sentence-level sentiment
        sentences = sent_tokenize(text)
        sentence_sentiments = [self.sia.polarity_scores(sent) for sent in sentences]
        
        # Calculate sentiment trajectory
        positive_trajectory = [sent['pos'] for sent in sentence_sentiments]
        negative_trajectory = [sent['neg'] for sent in sentence_sentiments]
        
        # Emotion analysis
        emotions = self._detect_emotions(text)
        
        # Emotional language patterns
        emotional_patterns = {
            "fear": ["fear", "afraid", "scared", "terrified", "worried", "anxious", "panic"],
            "anger": ["angry", "furious", "outraged", "enraged", "mad", "irritated"],
            "sadness": ["sad", "depressed", "tragic", "mourning", "grief", "sorrow"],
            "joy": ["happy", "joyful", "excited", "delighted", "pleased", "cheerful"],
            "surprise": ["surprised", "shocked", "astonished", "amazed", "stunned"],
            "disgust": ["disgusted", "revolted", "repulsed", "sickened"]
        }
        
        emotion_counts = {}
        text_lower = text.lower()
        for emotion, words in emotional_patterns.items():
            count = sum(text_lower.count(word) for word in words)
            emotion_counts[emotion] = count
            
        # Calculate overall tone
        if sentiment_scores['compound'] > 0.5:
            overall_tone = "very_positive"
        elif sentiment_scores['compound'] > 0.1:
            overall_tone = "positive"
        elif sentiment_scores['compound'] > -0.1:
            overall_tone = "neutral"
        elif sentiment_scores['compound'] > -0.5:
            overall_tone = "negative"
        else:
            overall_tone = "very_negative"
            
        return {
            "overall_sentiment": sentiment_scores,
            "overall_tone": overall_tone,
            "emotion_distribution": emotions,
            "emotion_word_counts": emotion_counts,
            "sentiment_consistency": float(np.std([s['compound'] for s in sentence_sentiments])),
            "positive_percentage": sum(1 for s in sentence_sentiments if s['compound'] > 0.1) / len(sentence_sentiments) * 100 if sentence_sentiments else 0,
            "negative_percentage": sum(1 for s in sentence_sentiments if s['compound'] < -0.1) / len(sentence_sentiments) * 100 if sentence_sentiments else 0,
            "emotional_intensity": abs(sentiment_scores['compound']),
            "subjectivity_score": self._calculate_subjectivity(text)
        }
    
    def _detect_emotions(self, text: str) -> Dict[str, float]:
        """
        Detect emotions using transformer model or fallback
        """
        if self.emotion_classifier:
            try:
                # Use transformer model for emotion detection
                results = self.emotion_classifier(text[:512])  # Limit text length
                emotions = {}
                for result in results[0]:
                    emotions[result['label']] = result['score']
                return emotions
            except:
                pass
                
        # Fallback to keyword-based emotion detection
        return {
            "joy": 0.0,
            "sadness": 0.0,
            "anger": 0.0,
            "fear": 0.0,
            "surprise": 0.0,
            "disgust": 0.0
        }
    
    def _calculate_subjectivity(self, text: str) -> float:
        """
        Calculate subjectivity score based on opinion words
        """
        opinion_words = [
            "believe", "think", "feel", "opinion", "seems", "appears",
            "probably", "maybe", "perhaps", "might", "could", "should",
            "best", "worst", "better", "worse", "good", "bad",
            "unfortunately", "fortunately", "hopefully"
        ]
        
        words = word_tokenize(text.lower())
        opinion_count = sum(1 for word in words if word in opinion_words)
        
        return opinion_count / len(words) * 100 if words else 0
    
    def _calculate_overall_metrics(self, text: str) -> Dict[str, Any]:
        """
        Calculate overall quality metrics
        """
        # Combine various metrics for overall scores
        sentences = sent_tokenize(text)
        
        metrics = {
            "article_length": len(word_tokenize(text)),
            "information_density": len(set(word_tokenize(text))) / len(word_tokenize(text)) if word_tokenize(text) else 0,
            "fact_to_opinion_ratio": self._calculate_fact_opinion_ratio(text),
            "objectivity_score": 1 - (self._calculate_subjectivity(text) / 100),
            "comprehensiveness_score": self._calculate_comprehensiveness(text),
            "clarity_score": self._calculate_clarity_score(text),
            "balance_score": self._calculate_balance_score(text)
        }
        
        # Calculate overall quality score
        quality_components = [
            metrics["objectivity_score"] * 0.2,
            metrics["comprehensiveness_score"] * 0.2,
            metrics["clarity_score"] * 0.2,
            metrics["balance_score"] * 0.2,
            (1 - abs(self.sia.polarity_scores(text)['compound'])) * 0.2  # Neutrality
        ]
        
        metrics["overall_quality_score"] = sum(quality_components)
        
        return metrics
    
    def _calculate_fact_opinion_ratio(self, text: str) -> float:
        """
        Calculate ratio of factual vs opinion statements
        """
        sentences = sent_tokenize(text)
        fact_count = 0
        opinion_count = 0
        
        fact_indicators = ["according to", "data shows", "research finds", "study reveals", "reported", "confirmed"]
        opinion_indicators = ["believe", "think", "feel", "seems", "appears", "opinion", "should", "could"]
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in fact_indicators):
                fact_count += 1
            elif any(indicator in sentence_lower for indicator in opinion_indicators):
                opinion_count += 1
                
        total = fact_count + opinion_count
        return fact_count / total if total > 0 else 0.5
    
    def _calculate_comprehensiveness(self, text: str) -> float:
        """
        Calculate how comprehensive the article is
        """
        # Check for various elements
        has_quotes = bool(re.search(r'"[^"]+"', text))
        has_statistics = bool(re.search(r'\d+\.?\d*\s*%', text))
        has_sources = bool(re.search(r'according to|said|reported', text, re.IGNORECASE))
        has_context = bool(re.search(r'background|history|previously', text, re.IGNORECASE))
        has_multiple_viewpoints = self._check_multiple_viewpoints(text)
        
        score = sum([
            has_quotes * 0.2,
            has_statistics * 0.2,
            has_sources * 0.2,
            has_context * 0.2,
            has_multiple_viewpoints * 0.2
        ])
        
        return score
    
    def _check_multiple_viewpoints(self, text: str) -> bool:
        """
        Check if article presents multiple viewpoints
        """
        contrast_indicators = [
            "however", "but", "on the other hand", "alternatively",
            "critics say", "supporters argue", "opponents", "proponents",
            "debate", "controversy", "disputed"
        ]
        
        text_lower = text.lower()
        return sum(1 for indicator in contrast_indicators if indicator in text_lower) >= 2
    
    def _calculate_clarity_score(self, text: str) -> float:
        """
        Calculate clarity based on readability and structure
        """
        # Use readability scores
        fre = flesch_reading_ease(text)
        
        # Normalize to 0-1 scale (FRE ranges from 0-100)
        clarity = fre / 100
        
        # Adjust for very long sentences
        sentences = sent_tokenize(text)
        avg_sentence_length = np.mean([len(word_tokenize(s)) for s in sentences])
        if avg_sentence_length > 25:
            clarity *= 0.8
        elif avg_sentence_length < 10:
            clarity *= 0.9
            
        return min(clarity, 1.0)
    
    def _calculate_balance_score(self, text: str) -> float:
        """
        Calculate how balanced the article is
        """
        # Check for balanced language
        positive_words = ["success", "improve", "benefit", "positive", "growth", "achievement"]
        negative_words = ["failure", "decline", "negative", "problem", "crisis", "threat"]
        
        text_lower = text.lower()
        positive_count = sum(text_lower.count(word) for word in positive_words)
        negative_count = sum(text_lower.count(word) for word in negative_words)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.5
            
        # Calculate balance (closer to 0.5 is more balanced)
        ratio = positive_count / total
        balance = 1 - abs(ratio - 0.5) * 2
        
        # Factor in multiple viewpoints
        if self._check_multiple_viewpoints(text):
            balance = (balance + 1) / 2
            
        return balance


def format_analysis_results(results: Dict[str, Any]) -> str:
    """
    Format analysis results for display
    """
    output = []
    
    # Header
    output.append("=" * 80)
    output.append("ENHANCED CONTENT ANALYSIS REPORT")
    output.append("=" * 80)
    output.append(f"URL: {results['url']}")
    output.append(f"Analysis Date: {results['timestamp']}")
    output.append("")
    
    # Content Summary
    output.append("1. CONTENT SUMMARY")
    output.append("-" * 40)
    summary = results['content_summary']
    output.append(f"Word Count: {summary['word_count']}")
    output.append(f"Sentence Count: {summary['sentence_count']}")
    output.append(f"Average Sentence Length: {summary['average_sentence_length']:.1f} words")
    output.append("")
    
    # Topic Detection
    output.append("2. TOPIC DETECTION")
    output.append("-" * 40)
    topics = results['topic_detection']
    output.append(f"Main Topics: {', '.join(topics['keyword_topics'])}")
    if topics['entity_topics']:
        output.append(f"Key People: {', '.join(topics['entity_topics'].get('people', [])[:3])}")
        output.append(f"Organizations: {', '.join(topics['entity_topics'].get('organizations', [])[:3])}")
    output.append("")
    
    # Key Claims
    output.append("3. KEY CLAIMS EXTRACTED")
    output.append("-" * 40)
    for i, claim in enumerate(results['key_claims'][:5], 1):
        output.append(f"{i}. {claim['text'][:100]}...")
        output.append(f"   Type: {claim['type']} | Attribution: {claim['has_attribution']}")
    output.append("")
    
    # Quote Analysis
    output.append("4. QUOTE ANALYSIS")
    output.append("-" * 40)
    quotes = results['quote_analysis']
    output.append(f"Total Quotes: {quotes['total_quotes']} ({quotes['direct_quotes']} direct, {quotes['indirect_quotes']} indirect)")
    output.append(f"Unique Speakers: {quotes['unique_speakers']}")
    output.append(f"Quote Density: {quotes['quote_density']:.2%}")
    output.append("")
    
    # Statistical Claims
    output.append("5. STATISTICAL CLAIMS")
    output.append("-" * 40)
    stats = results['statistical_claims']
    output.append(f"Total Statistical Claims: {len(stats)}")
    for stat in stats[:3]:
        output.append(f"- {stat['type']}: {stat['value']} (Context: {stat['context'][:50]}...)")
    output.append("")
    
    # Story Structure
    output.append("6. STORY STRUCTURE ANALYSIS")
    output.append("-" * 40)
    structure = results['story_structure']
    output.append(f"Structure Type: {structure['structure_type']}")
    output.append(f"5W1H Coverage Score: {structure['five_w1h_score']:.1%}")
    output.append(f"Follows Inverted Pyramid: {structure['follows_inverted_pyramid']}")
    output.append("")
    
    # Source Attribution
    output.append("7. SOURCE ATTRIBUTION")
    output.append("-" * 40)
    sources = results['source_attribution']
    output.append(f"Total Sources: {sources['total_sources']} ({sources['named_sources']} named, {sources['anonymous_sources']} anonymous)")
    output.append(f"Source Diversity Score: {sources['source_diversity_score']:.2f}")
    output.append("")
    
    # Readability
    output.append("8. READABILITY METRICS")
    output.append("-" * 40)
    readability = results['readability']
    output.append(f"Difficulty Level: {readability['difficulty_level']}")
    output.append(f"Education Level: {readability['education_level']}")
    output.append(f"Flesch Reading Ease: {readability['flesch_reading_ease']:.1f}")
    output.append("")
    
    # Emotional Tone
    output.append("9. EMOTIONAL TONE ANALYSIS")
    output.append("-" * 40)
    tone = results['emotional_tone']
    output.append(f"Overall Tone: {tone['overall_tone']}")
    output.append(f"Sentiment Score: {tone['overall_sentiment']['compound']:.3f}")
    output.append(f"Subjectivity Score: {tone['subjectivity_score']:.1f}%")
    output.append("")
    
    # Overall Metrics
    output.append("10. OVERALL QUALITY METRICS")
    output.append("-" * 40)
    metrics = results['overall_metrics']
    output.append(f"Overall Quality Score: {metrics['overall_quality_score']:.2f}/1.0")
    output.append(f"Objectivity Score: {metrics['objectivity_score']:.2f}")
    output.append(f"Clarity Score: {metrics['clarity_score']:.2f}")
    output.append(f"Balance Score: {metrics['balance_score']:.2f}")
    output.append("")
    
    return "\n".join(output)


# Integration function for Flask app
def analyze_article_content(url: str, article_text: str) -> Dict[str, Any]:
    """
    Main function to integrate with Flask app
    """
    analyzer = EnhancedContentAnalyzer()
    results = analyzer.analyze_article(article_text, url)
    
    # Add formatted report
    results['formatted_report'] = format_analysis_results(results)
    
    return results
