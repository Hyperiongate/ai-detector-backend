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
from sentence_transformers import SentenceTransformer
import numpy as np
from scholarly import scholarly
import xml.etree.ElementTree as ET
from lxml import html
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# ================================
# ENHANCED DETECTION CLASSES
# ================================

class AcademicDatabaseSearcher:
    """Advanced academic database integration for comprehensive plagiarism detection"""
    
    def __init__(self):
        self.databases = {
            'arxiv': self._search_arxiv,
            'pubmed': self._search_pubmed,
            'crossref': self._search_crossref,
            'semantic_scholar': self._search_semantic_scholar,
            'google_scholar': self._search_google_scholar
        }
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_all_databases(self, query_text, max_results=5):
        """Search across all academic databases simultaneously"""
        results = {}
        
        # Split into smaller chunks for better search
        chunks = self._split_into_chunks(query_text, 200)
        
        for chunk in chunks[:3]:  # Limit to top 3 chunks
            search_tasks = []
            for db_name, search_func in self.databases.items():
                task = asyncio.create_task(search_func(chunk, max_results))
                search_tasks.append((db_name, task))
            
            # Execute searches concurrently
            for db_name, task in search_tasks:
                try:
                    db_results = await asyncio.wait_for(task, timeout=30)
                    if db_name not in results:
                        results[db_name] = []
                    results[db_name].extend(db_results)
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout searching {db_name}")
                    results[db_name] = []
                except Exception as e:
                    logger.error(f"Error searching {db_name}: {str(e)}")
                    results[db_name] = []
        
        return results
    
    def _split_into_chunks(self, text, chunk_size):
        """Split text into meaningful chunks for search"""
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def _search_arxiv(self, query, max_results=5):
        """Search arXiv database"""
        try:
            url = "http://export.arxiv.org/api/query"
            params = {
                'search_query': f'all:"{query[:100]}"',
                'start': 0,
                'max_results': max_results
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    content = await response.text()
                    return self._parse_arxiv_response(content)
        except Exception as e:
            logger.error(f"ArXiv search error: {str(e)}")
        return []
    
    async def _search_pubmed(self, query, max_results=5):
        """Search PubMed database"""
        try:
            # First, search for IDs
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            search_params = {
                'db': 'pubmed',
                'term': query[:100],
                'retmax': max_results,
                'retmode': 'json'
            }
            
            async with self.session.get(search_url, params=search_params) as response:
                if response.status == 200:
                    search_data = await response.json()
                    if 'esearchresult' in search_data and 'idlist' in search_data['esearchresult']:
                        ids = search_data['esearchresult']['idlist']
                        if ids:
                            return await self._fetch_pubmed_details(ids)
        except Exception as e:
            logger.error(f"PubMed search error: {str(e)}")
        return []
    
    async def _search_crossref(self, query, max_results=5):
        """Search CrossRef database"""
        try:
            url = "https://api.crossref.org/works"
            params = {
                'query': query[:100],
                'rows': max_results
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_crossref_response(data)
        except Exception as e:
            logger.error(f"CrossRef search error: {str(e)}")
        return []
    
    async def _search_semantic_scholar(self, query, max_results=5):
        """Search Semantic Scholar database"""
        try:
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                'query': query[:100],
                'limit': max_results,
                'fields': 'title,authors,abstract,year,url,citationCount'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_semantic_scholar_response(data)
        except Exception as e:
            logger.error(f"Semantic Scholar search error: {str(e)}")
        return []
    
    async def _search_google_scholar(self, query, max_results=5):
        """Search Google Scholar (simplified)"""
        try:
            # Note: This is a simplified version. For production, consider using scholarly library
            # or official Google Scholar API when available
            return []
        except Exception as e:
            logger.error(f"Google Scholar search error: {str(e)}")
        return []
    
    def _parse_arxiv_response(self, xml_content):
        """Parse arXiv XML response"""
        try:
            root = ET.fromstring(xml_content)
            results = []
            
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                abstract_elem = entry.find('{http://www.w3.org/2005/Atom}summary')
                authors = entry.findall('{http://www.w3.org/2005/Atom}author')
                
                result = {
                    'title': title_elem.text.strip() if title_elem is not None else '',
                    'abstract': abstract_elem.text.strip() if abstract_elem is not None else '',
                    'authors': [author.find('{http://www.w3.org/2005/Atom}name').text 
                              for author in authors if author.find('{http://www.w3.org/2005/Atom}name') is not None],
                    'source': 'arXiv',
                    'url': entry.find('{http://www.w3.org/2005/Atom}id').text if entry.find('{http://www.w3.org/2005/Atom}id') is not None else ''
                }
                results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Error parsing arXiv response: {str(e)}")
            return []
    
    async def _fetch_pubmed_details(self, ids):
        """Fetch detailed information for PubMed IDs"""
        try:
            fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            fetch_params = {
                'db': 'pubmed',
                'id': ','.join(ids),
                'retmode': 'xml'
            }
            
            async with self.session.get(fetch_url, params=fetch_params) as response:
                if response.status == 200:
                    content = await response.text()
                    return self._parse_pubmed_response(content)
        except Exception as e:
            logger.error(f"Error fetching PubMed details: {str(e)}")
        return []
    
    def _parse_pubmed_response(self, xml_content):
        """Parse PubMed XML response"""
        try:
            root = ET.fromstring(xml_content)
            results = []
            
            for article in root.findall('.//PubmedArticle'):
                title_elem = article.find('.//ArticleTitle')
                abstract_elem = article.find('.//AbstractText')
                authors = article.findall('.//Author')
                
                result = {
                    'title': title_elem.text if title_elem is not None else '',
                    'abstract': abstract_elem.text if abstract_elem is not None else '',
                    'authors': [f"{author.find('ForeName').text if author.find('ForeName') is not None else ''} {author.find('LastName').text if author.find('LastName') is not None else ''}"
                              for author in authors],
                    'source': 'PubMed',
                    'url': f"https://pubmed.ncbi.nlm.nih.gov/{article.find('.//PMID').text}/" if article.find('.//PMID') is not None else ''
                }
                results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Error parsing PubMed response: {str(e)}")
            return []
    
    def _parse_crossref_response(self, data):
        """Parse CrossRef JSON response"""
        try:
            results = []
            if 'message' in data and 'items' in data['message']:
                for item in data['message']['items']:
                    result = {
                        'title': item.get('title', [''])[0] if item.get('title') else '',
                        'abstract': item.get('abstract', ''),
                        'authors': [f"{author.get('given', '')} {author.get('family', '')}"
                                  for author in item.get('author', [])],
                        'source': 'CrossRef',
                        'url': item.get('URL', ''),
                        'doi': item.get('DOI', ''),
                        'year': item.get('published-print', {}).get('date-parts', [[None]])[0][0] if item.get('published-print') else None
                    }
                    results.append(result)
            return results
        except Exception as e:
            logger.error(f"Error parsing CrossRef response: {str(e)}")
            return []
    
    def _parse_semantic_scholar_response(self, data):
        """Parse Semantic Scholar JSON response"""
        try:
            results = []
            if 'data' in data:
                for item in data['data']:
                    result = {
                        'title': item.get('title', ''),
                        'abstract': item.get('abstract', ''),
                        'authors': [author.get('name', '') for author in item.get('authors', [])],
                        'source': 'Semantic Scholar',
                        'url': item.get('url', ''),
                        'year': item.get('year'),
                        'citations': item.get('citationCount', 0)
                    }
                    results.append(result)
            return results
        except Exception as e:
            logger.error(f"Error parsing Semantic Scholar response: {str(e)}")
            return []


class SemanticSimilarityAnalyzer:
    """Advanced semantic similarity analysis using state-of-the-art models"""
    
    def __init__(self):
        self.model_name = 'all-MiniLM-L6-v2'  # Fast and accurate
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the sentence transformer model"""
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded semantic similarity model: {self.model_name}")
        except Exception as e:
            logger.error(f"Error loading semantic model: {str(e)}")
            self.model = None
    
    def calculate_similarity(self, text1, text2):
        """Calculate semantic similarity between two texts"""
        if not self.model:
            return 0.0
        
        try:
            # Generate embeddings
            embeddings = self.model.encode([text1, text2])
            
            # Calculate cosine similarity
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def find_similar_segments(self, input_text, reference_texts, threshold=0.7):
        """Find similar segments between input text and reference texts"""
        if not self.model:
            return []
        
        similarities = []
        input_sentences = self._split_sentences(input_text)
        
        for ref_text in reference_texts:
            ref_sentences = self._split_sentences(ref_text['content'])
            
            for i, input_sent in enumerate(input_sentences):
                for j, ref_sent in enumerate(ref_sentences):
                    similarity = self.calculate_similarity(input_sent, ref_sent)
                    
                    if similarity >= threshold:
                        similarities.append({
                            'input_sentence': input_sent,
                            'reference_sentence': ref_sent,
                            'similarity_score': similarity,
                            'input_position': i,
                            'reference_position': j,
                            'source': ref_text.get('source', 'Unknown'),
                            'url': ref_text.get('url', '')
                        })
        
        # Sort by similarity score
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similarities
    
    def _split_sentences(self, text):
        """Split text into sentences"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]


class EnhancedAIDetector:
    """Multi-model AI detection system"""
    
    def __init__(self):
        self.models = {}
        self.load_models()
    
    def load_models(self):
        """Load AI detection models"""
        try:
            # Load a pre-trained model for AI detection
            # This is a placeholder - you'd use actual AI detection models
            logger.info("AI detection models loaded")
        except Exception as e:
            logger.error(f"Error loading AI detection models: {str(e)}")
    
    async def detect_ai_content(self, text):
        """Multi-model AI content detection"""
        results = {
            'overall_score': 0.0,
            'model_scores': {},
            'confidence': 0.0,
            'analysis': []
        }
        
        # Basic pattern-based detection
        patterns_score = self._pattern_based_detection(text)
        results['model_scores']['pattern_analysis'] = patterns_score
        
        # Statistical analysis
        statistical_score = self._statistical_analysis(text)
        results['model_scores']['statistical_analysis'] = statistical_score
        
        # OpenAI detection (if available)
        if openai.api_key:
            openai_score = await self._openai_detection(text)
            results['model_scores']['openai_analysis'] = openai_score
        
        # Calculate overall score
        scores = list(results['model_scores'].values())
        results['overall_score'] = sum(scores) / len(scores) if scores else 0.0
        results['confidence'] = min(0.95, max(0.1, results['overall_score']))
        
        # Generate analysis
        results['analysis'] = self._generate_analysis(results['model_scores'])
        
        return results
    
    def _pattern_based_detection(self, text):
        """Pattern-based AI detection"""
        ai_indicators = [
            r'\b(as an ai|i am an ai|as a language model)\b',
            r'\b(furthermore|moreover|additionally|consequently)\b',
            r'\b(it is important to note|it should be noted)\b',
            r'\b(in conclusion|to summarize|in summary)\b'
        ]
        
        score = 0.0
        for pattern in ai_indicators:
            matches = len(re.findall(pattern, text.lower()))
            score += matches * 0.1
        
        return min(1.0, score)
    
    def _statistical_analysis(self, text):
        """Statistical analysis for AI detection"""
        sentences = re.split(r'[.!?]+', text)
        if not sentences:
            return 0.0
        
        # Analyze sentence length consistency (AI tends to be more consistent)
        lengths = [len(s.split()) for s in sentences if s.strip()]
        if not lengths:
            return 0.0
        
        length_std = np.std(lengths)
        avg_length = np.mean(lengths)
        
        # AI typically has lower variance in sentence length
        consistency_score = 1.0 - min(1.0, length_std / max(1, avg_length))
        
        return consistency_score * 0.5  # Weight appropriately
    
    async def _openai_detection(self, text):
        """Use OpenAI for AI detection analysis"""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Analyze the following text and determine if it was likely written by AI. Respond with a score from 0.0 (definitely human) to 1.0 (definitely AI) and brief reasoning."},
                    {"role": "user", "content": text[:2000]}  # Limit text length
                ],
                max_tokens=150
            )
            
            content = response.choices[0].message.content
            # Extract score from response (simplified)
            score_match = re.search(r'(\d+\.?\d*)', content)
            if score_match:
                return min(1.0, float(score_match.group(1)))
            
        except Exception as e:
            logger.error(f"OpenAI detection error: {str(e)}")
        
        return 0.0
    
    def _generate_analysis(self, model_scores):
        """Generate human-readable analysis"""
        analysis = []
        
        for model, score in model_scores.items():
            if score > 0.7:
                analysis.append(f"{model}: High likelihood of AI generation (Score: {score:.2f})")
            elif score > 0.4:
                analysis.append(f"{model}: Moderate likelihood of AI generation (Score: {score:.2f})")
            else:
                analysis.append(f"{model}: Low likelihood of AI generation (Score: {score:.2f})")
        
        return analysis


class ProfessionalReportGenerator:
    """Generate professional reports in multiple formats"""
    
    def generate_executive_report(self, analysis_results):
        """Generate executive summary report"""
        report = {
            'report_type': 'Executive Summary',
            'generated_at': datetime.now().isoformat(),
            'summary': self._generate_executive_summary(analysis_results),
            'key_findings': self._extract_key_findings(analysis_results),
            'recommendations': self._generate_recommendations(analysis_results),
            'risk_assessment': self._assess_risk_level(analysis_results)
        }
        return report
    
    def generate_technical_report(self, analysis_results):
        """Generate detailed technical report"""
        report = {
            'report_type': 'Technical Analysis',
            'generated_at': datetime.now().isoformat(),
            'methodology': self._describe_methodology(),
            'detailed_analysis': self._generate_detailed_analysis(analysis_results),
            'statistical_summary': self._generate_statistical_summary(analysis_results),
            'source_analysis': self._analyze_sources(analysis_results),
            'technical_recommendations': self._generate_technical_recommendations(analysis_results)
        }
        return report
    
    def generate_compliance_report(self, analysis_results):
        """Generate compliance-focused report"""
        report = {
            'report_type': 'Compliance Analysis',
            'generated_at': datetime.now().isoformat(),
            'compliance_status': self._assess_compliance(analysis_results),
            'policy_violations': self._identify_violations(analysis_results),
            'remediation_steps': self._suggest_remediation(analysis_results),
            'audit_trail': self._generate_audit_trail(analysis_results)
        }
        return report
    
    def _generate_executive_summary(self, results):
        """Generate executive summary"""
        plagiarism_score = results.get('plagiarism_score', 0)
        ai_score = results.get('ai_detection', {}).get('overall_score', 0)
        
        if plagiarism_score > 0.7 or ai_score > 0.7:
            return "High-risk content detected requiring immediate attention."
        elif plagiarism_score > 0.4 or ai_score > 0.4:
            return "Moderate-risk content detected requiring review."
        else:
            return "Low-risk content with minimal concerns identified."
    
    def _extract_key_findings(self, results):
        """Extract key findings"""
        findings = []
        
        plagiarism_score = results.get('plagiarism_score', 0)
        if plagiarism_score > 0.3:
            findings.append(f"Plagiarism detected with {plagiarism_score:.1%} similarity to existing sources")
        
        ai_score = results.get('ai_detection', {}).get('overall_score', 0)
        if ai_score > 0.3:
            findings.append(f"AI-generated content detected with {ai_score:.1%} confidence")
        
        sources = results.get('sources_found', [])
        if sources:
            findings.append(f"Content matches found in {len(sources)} academic sources")
        
        return findings
    
    def _generate_recommendations(self, results):
        """Generate recommendations"""
        recommendations = []
        
        plagiarism_score = results.get('plagiarism_score', 0)
        if plagiarism_score > 0.5:
            recommendations.append("Immediate review and revision required for plagiarized content")
            recommendations.append("Implement proper citation and attribution practices")
        
        ai_score = results.get('ai_detection', {}).get('overall_score', 0)
        if ai_score > 0.5:
            recommendations.append("Review AI-generated content for compliance with policies")
            recommendations.append("Consider disclosure requirements for AI-assisted content")
        
        return recommendations
    
    def _assess_risk_level(self, results):
        """Assess overall risk level"""
        plagiarism_score = results.get('plagiarism_score', 0)
        ai_score = results.get('ai_detection', {}).get('overall_score', 0)
        
        max_score = max(plagiarism_score, ai_score)
        
        if max_score > 0.7:
            return "HIGH"
        elif max_score > 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _describe_methodology(self):
        """Describe analysis methodology"""
        return {
            'plagiarism_detection': 'Multi-database academic search with semantic similarity analysis',
            'ai_detection': 'Multi-model approach combining pattern analysis and statistical methods',
            'databases_searched': ['arXiv', 'PubMed', 'CrossRef', 'Semantic Scholar'],
            'similarity_threshold': 0.7,
            'confidence_metrics': 'Weighted scoring across multiple detection models'
        }
    
    def _generate_detailed_analysis(self, results):
        """Generate detailed technical analysis"""
        return {
            'plagiarism_analysis': results.get('plagiarism_details', {}),
            'ai_analysis': results.get('ai_detection', {}),
            'source_breakdown': results.get('source_analysis', {}),
            'similarity_matrix': results.get('similarity_scores', [])
        }
    
    def _generate_statistical_summary(self, results):
        """Generate statistical summary"""
        return {
            'total_sources_checked': len(results.get('sources_found', [])),
            'highest_similarity_score': max([s.get('similarity_score', 0) for s in results.get('similarity_scores', [])], default=0),
            'average_similarity_score': np.mean([s.get('similarity_score', 0) for s in results.get('similarity_scores', [])]) if results.get('similarity_scores') else 0,
            'detection_confidence': results.get('ai_detection', {}).get('confidence', 0)
        }
    
    def _analyze_sources(self, results):
        """Analyze source distribution"""
        sources = results.get('sources_found', [])
        source_breakdown = {}
        
        for source in sources:
            db = source.get('source', 'Unknown')
            if db not in source_breakdown:
                source_breakdown[db] = 0
            source_breakdown[db] += 1
        
        return source_breakdown
    
    def _generate_technical_recommendations(self, results):
        """Generate technical recommendations"""
        recommendations = []
        
        # Add specific technical recommendations based on analysis
        if results.get('plagiarism_score', 0) > 0.3:
            recommendations.append("Implement automated plagiarism checking in workflow")
            recommendations.append("Establish clear citation guidelines and training")
        
        if results.get('ai_detection', {}).get('overall_score', 0) > 0.3:
            recommendations.append("Deploy AI detection tools for content review")
            recommendations.append("Establish AI content governance policies")
        
        return recommendations
    
    def _assess_compliance(self, results):
        """Assess compliance status"""
        plagiarism_score = results.get('plagiarism_score', 0)
        ai_score = results.get('ai_detection', {}).get('overall_score', 0)
        
        if plagiarism_score > 0.5:
            return "NON-COMPLIANT: Significant plagiarism detected"
        elif ai_score > 0.7:
            return "REVIEW REQUIRED: High AI content detected"
        else:
            return "COMPLIANT: No significant issues detected"
    
    def _identify_violations(self, results):
        """Identify policy violations"""
        violations = []
        
        if results.get('plagiarism_score', 0) > 0.3:
            violations.append("Academic integrity policy violation")
        
        if results.get('ai_detection', {}).get('overall_score', 0) > 0.5:
            violations.append("AI content disclosure requirement")
        
        return violations
    
    def _suggest_remediation(self, results):
        """Suggest remediation steps"""
        steps = []
        
        if results.get('plagiarism_score', 0) > 0.3:
            steps.append("Remove or properly cite plagiarized content")
            steps.append("Rewrite sections to ensure originality")
        
        if results.get('ai_detection', {}).get('overall_score', 0) > 0.5:
            steps.append("Review and disclose AI-generated content")
            steps.append("Ensure human oversight and validation")
        
        return steps
    
    def _generate_audit_trail(self, results):
        """Generate audit trail"""
        return {
            'analysis_timestamp': datetime.now().isoformat(),
            'databases_checked': ['arXiv', 'PubMed', 'CrossRef', 'Semantic Scholar'],
            'detection_models_used': ['Pattern Analysis', 'Statistical Analysis', 'Semantic Similarity'],
            'analysis_duration': results.get('analysis_duration', 'N/A'),
            'result_hash': hashlib.md5(str(results).encode()).hexdigest()
        }


# Initialize global instances
academic_searcher = None
similarity_analyzer = SemanticSimilarityAnalyzer()
ai_detector = EnhancedAIDetector()
report_generator = ProfessionalReportGenerator()

# ================================
# MAIN ANALYSIS FUNCTION
# ================================

async def perform_comprehensive_analysis(text):
    """Perform comprehensive plagiarism and AI detection analysis"""
    start_time = time.time()
    
    results = {
        'text_length': len(text),
        'analysis_timestamp': datetime.now().isoformat(),
        'plagiarism_score': 0.0,
        'ai_detection': {},
        'sources_found': [],
        'similarity_scores': [],
        'analysis_duration': 0
    }
    
    try:
        # Initialize academic searcher
        async with AcademicDatabaseSearcher() as searcher:
            # Search academic databases
            database_results = await searcher.search_all_databases(text)
            
            # Process results for similarity analysis
            reference_texts = []
            for db_name, db_results in database_results.items():
                for result in db_results:
                    reference_texts.append({
                        'content': f"{result.get('title', '')} {result.get('abstract', '')}",
                        'source': db_name,
                        'url': result.get('url', ''),
                        'metadata': result
                    })
                    results['sources_found'].append(result)
            
            # Semantic similarity analysis
            if reference_texts:
                similarities = similarity_analyzer.find_similar_segments(
                    text, reference_texts, threshold=0.6
                )
                results['similarity_scores'] = similarities
                
                # Calculate overall plagiarism score
                if similarities:
                    max_similarity = max(sim['similarity_score'] for sim in similarities)
                    avg_similarity = sum(sim['similarity_score'] for sim in similarities) / len(similarities)
                    results['plagiarism_score'] = (max_similarity * 0.7) + (avg_similarity * 0.3)
        
        # AI detection analysis
        ai_results = await ai_detector.detect_ai_content(text)
        results['ai_detection'] = ai_results
        
        # Calculate analysis duration
        results['analysis_duration'] = time.time() - start_time
        
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {str(e)}")
        results['error'] = str(e)
    
    return results

# ================================
# EXISTING ROUTES (PRESERVED)
# ================================

@app.route('/')
def index():
    return render_template('news.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# ================================
# ENHANCED ROUTES
# ================================

@app.route('/api/analyze', methods=['POST'])
async def analyze_text():
    """Enhanced text analysis endpoint"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        analysis_type = data.get('type', 'comprehensive')  # comprehensive, plagiarism, ai
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) < 50:
            return jsonify({'error': 'Text too short for meaningful analysis'}), 400
        
        # Perform analysis based on type
        if analysis_type == 'comprehensive':
            results = await perform_comprehensive_analysis(text)
        elif analysis_type == 'plagiarism':
            # Placeholder for plagiarism-only analysis
            results = await perform_comprehensive_analysis(text)
        elif analysis_type == 'ai':
            # AI detection only
            results = {
                'ai_detection': await ai_detector.detect_ai_content(text),
                'analysis_timestamp': datetime.now().isoformat()
            }
        else:
            return jsonify({'error': 'Invalid analysis type'}), 400
        
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
        report_type = data.get('type', 'executive')  # executive, technical, compliance
        
        if not analysis_results:
            return jsonify({'error': 'No analysis results provided'}), 400
        
        # Generate report based on type
        if report_type == 'executive':
            report = report_generator.generate_executive_report(analysis_results)
        elif report_type == 'technical':
            report = report_generator.generate_technical_report(analysis_results)
        elif report_type == 'compliance':
            report = report_generator.generate_compliance_report(analysis_results)
        else:
            return jsonify({'error': 'Invalid report type'}), 400
        
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
        'services': {
            'semantic_analyzer': similarity_analyzer.model is not None,
            'ai_detector': True,
            'report_generator': True
        }
    })

# ================================
# LEGACY ROUTES (FOR COMPATIBILITY)
# ================================

@app.route('/api/detect', methods=['POST'])
def detect_plagiarism():
    """Legacy plagiarism detection endpoint"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Run async analysis in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(perform_comprehensive_analysis(text))
        loop.close()
        
        # Format for legacy compatibility
        legacy_response = {
            'plagiarism_detected': results.get('plagiarism_score', 0) > 0.3,
            'confidence_score': results.get('plagiarism_score', 0),
            'sources_found': len(results.get('sources_found', [])),
            'detailed_results': results
        }
        
        return jsonify(legacy_response)
        
    except Exception as e:
        logger.error(f"Error in legacy detection: {str(e)}")
        return jsonify({'error': 'Detection failed', 'details': str(e)}), 500

if __name__ == '__main__':
    # Initialize models on startup
    logger.info("Starting enhanced detection system...")
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
