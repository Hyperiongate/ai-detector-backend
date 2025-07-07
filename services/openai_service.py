"""
OpenAI service - AI integration for advanced analysis
"""
import time
import json
import re
import config

# OpenAI import for Phase 2 - Updated for v1.0+ API
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None
    print("⚠ OpenAI module not available - will use basic analysis")

# Configure OpenAI if available - Updated for v1.0+ API
client = None
if config.OPENAI_API_KEY and OPENAI_AVAILABLE:
    try:
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        print("✓ OpenAI API configured")
    except Exception as e:
        print(f"⚠ OpenAI configuration error: {e}")
        OPENAI_AVAILABLE = False
else:
    print("⚠ OpenAI API key not found - will use basic analysis")

def analyze_with_openai(content, analysis_type='news'):
    """
    Use OpenAI for advanced content analysis with robust error handling
    Updated for OpenAI v1.0+ API with better JSON parsing
    """
    if not config.OPENAI_API_KEY or not OPENAI_AVAILABLE or not client:
        print("OpenAI API not available")
        return None
    
    try:
        # Create appropriate prompt based on analysis type
        if analysis_type == 'news':
            prompt = f"""Analyze this news content for bias, credibility, and quality. 
            
Content: {content[:2000]}  # Limit to manage tokens

Provide a detailed analysis in JSON format with these exact fields:
{{
    "political_bias": {{
        "label": "left/center-left/center/center-right/right",
        "score": -10 to +10 (negative=left, positive=right),
        "confidence": 0-100,
        "reasoning": "brief explanation"
    }},
    "credibility_analysis": {{
        "score": 0-100,
        "strengths": ["list of credibility strengths"],
        "weaknesses": ["list of credibility weaknesses"],
        "missing_elements": ["what's missing for better credibility"]
    }},
    "emotional_language": {{
        "score": 0-100,
        "loaded_terms": ["specific loaded/emotional words found"],
        "tone": "neutral/positive/negative/mixed"
    }},
    "factual_claims": {{
        "count": number,
        "verifiable_claims": ["list of specific claims that could be fact-checked"],
        "unsupported_statements": ["statements presented as fact without support"]
    }},
    "source_quality": {{
        "attribution_present": true/false,
        "source_diversity": "high/medium/low",
        "transparency": "high/medium/low"
    }}
}}

Be objective and specific in your analysis. Return ONLY valid JSON, no additional text."""

        # Make API call with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert news analyst. Always return valid JSON only, no markdown or extra text."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,  # Lower temperature for more consistent analysis
                    max_tokens=800,
                    timeout=30
                )
                
                # Parse the response
                result_text = response.choices[0].message.content.strip()
                
                # Debug logging
                print(f"OpenAI raw response length: {len(result_text)}")
                
                # Try to extract JSON from the response
                # Remove any markdown formatting
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0].strip()
                
                # Remove any text before the first { or after the last }
                first_brace = result_text.find('{')
                last_brace = result_text.rfind('}')
                if first_brace != -1 and last_brace != -1:
                    result_text = result_text[first_brace:last_brace + 1]
                
                # Try to parse JSON
                try:
                    analysis_result = json.loads(result_text)
                    print("✓ OpenAI analysis completed successfully")
                    return analysis_result
                except json.JSONDecodeError as je:
                    print(f"JSON parse error: {je}")
                    print(f"Failed JSON (first 200 chars): {result_text[:200]}")
                    
                    # Try to fix common JSON issues
                    # Replace single quotes with double quotes
                    result_text = result_text.replace("'", '"')
                    # Remove trailing commas
                    result_text = re.sub(r',\s*}', '}', result_text)
                    result_text = re.sub(r',\s*]', ']', result_text)
                    
                    try:
                        analysis_result = json.loads(result_text)
                        print("✓ OpenAI analysis completed with JSON fixes")
                        return analysis_result
                    except:
                        if attempt < max_retries - 1:
                            print(f"Retrying due to JSON error...")
                            continue
                        else:
                            print("Failed to parse OpenAI response as JSON after fixes")
                            return None
                
            except Exception as e:
                if "rate_limit" in str(e).lower():
                    print(f"Rate limit hit, retrying in {2 ** attempt} seconds...")
                    time.sleep(2 ** attempt)
                elif attempt < max_retries - 1:
                    print(f"OpenAI API error (attempt {attempt + 1}): {e}")
                    time.sleep(1)
                    continue
                else:
                    print(f"OpenAI API error: {e}")
                    break
                
        return None
        
    except Exception as e:
        print(f"Error in analyze_with_openai: {e}")
        return None

def extract_claims_with_ai(content):
    """
    Use OpenAI to extract specific factual claims from content
    Updated for OpenAI v1.0+ API
    """
    if not config.OPENAI_API_KEY or not OPENAI_AVAILABLE or not client:
        return []
    
    try:
        prompt = f"""Extract specific factual claims from this content that could be fact-checked.

Content: {content[:1500]}

Return a JSON array of claims, each with:
{{
    "claim": "the specific claim text",
    "context": "brief context around the claim",
    "type": "statistical/quote/event/policy",
    "checkable": true/false
}}

Focus on concrete, verifiable claims. Limit to the 5 most important claims. Return ONLY valid JSON."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a fact-checking expert who identifies specific claims that can be verified. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=500,
            timeout=20
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Extract JSON
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        # Remove any text before [ or after ]
        first_bracket = result_text.find('[')
        last_bracket = result_text.rfind(']')
        if first_bracket != -1 and last_bracket != -1:
            result_text = result_text[first_bracket:last_bracket + 1]
        
        claims = json.loads(result_text)
        return claims if isinstance(claims, list) else []
        
    except Exception as e:
        print(f"Error extracting claims with AI: {e}")
        return []

def enhance_with_openai_analysis(basic_results, content, is_pro=False):
    """
    Enhance basic analysis results with OpenAI insights
    """
    ai_analysis = analyze_with_openai(content, 'news')
    
    if not ai_analysis:
        print("OpenAI analysis failed, using enhanced basic analysis")
        return basic_results
    
    # Merge AI insights with basic results
    try:
        # Update credibility score with AI insights
        if 'credibility_analysis' in ai_analysis:
            ai_cred = ai_analysis['credibility_analysis']
            # Average basic and AI credibility scores
            basic_score = basic_results['credibility_score']
            ai_score = ai_cred.get('score', basic_score)
            basic_results['credibility_score'] = int((basic_score + ai_score) / 2)
            
            # Add AI insights if pro tier
            if is_pro:
                basic_results['credibility_insights'] = {
                    'strengths': ai_cred.get('strengths', []),
                    'weaknesses': ai_cred.get('weaknesses', []),
                    'missing_elements': ai_cred.get('missing_elements', [])
                }
        
        # Update political bias with AI analysis
        if 'political_bias' in ai_analysis:
            ai_bias = ai_analysis['political_bias']
            basic_results['political_bias'].update({
                'bias_score': ai_bias.get('score', basic_results['political_bias']['bias_score']),
                'bias_label': ai_bias.get('label', basic_results['political_bias']['bias_label']),
                'confidence': ai_bias.get('confidence', 85),
                'ai_reasoning': ai_bias.get('reasoning', '') if is_pro else ''
            })
        
        # Update emotional language analysis
        if 'emotional_language' in ai_analysis:
            ai_emotional = ai_analysis['emotional_language']
            basic_results['bias_indicators']['emotional_language'] = ai_emotional.get('score', 
                basic_results['bias_indicators']['emotional_language'])
            
            # Update loaded terms with AI findings
            ai_loaded_terms = ai_emotional.get('loaded_terms', [])
            existing_terms = basic_results['political_bias'].get('loaded_terms', [])
            combined_terms = list(set(existing_terms + ai_loaded_terms))[:10]  # Limit to 10
            basic_results['political_bias']['loaded_terms'] = combined_terms
        
        # Update factual claims with AI analysis
        if 'factual_claims' in ai_analysis:
            ai_facts = ai_analysis['factual_claims']
            basic_results['bias_indicators']['factual_claims'] = ai_facts.get('count', 
                basic_results['bias_indicators']['factual_claims'])
            
            # For pro tier, add verifiable claims
            if is_pro and ai_facts.get('verifiable_claims'):
                claims = ai_facts['verifiable_claims'][:5]  # Limit to 5
                basic_results['fact_check_results'] = [
                    {
                        'claim': claim,
                        'status': 'Pending verification',
                        'confidence': 0,
                        'sources': ['Awaiting fact-check']
                    }
                    for claim in claims
                ]
        
        # Add source quality insights
        if 'source_quality' in ai_analysis and is_pro:
            basic_results['source_analysis'].update({
                'attribution_quality': 'High' if ai_analysis['source_quality'].get('attribution_present') else 'Low',
                'source_diversity': ai_analysis['source_quality'].get('source_diversity', 'Unknown'),
                'transparency': ai_analysis['source_quality'].get('transparency', 'Unknown')
            })
        
        # Update methodology to reflect AI enhancement
        basic_results['methodology']['ai_enhanced'] = True
        basic_results['methodology']['models_used'] = ['GPT-3.5-turbo', 'Pattern matching']
        basic_results['methodology']['confidence_level'] = 90 if is_pro else 85
        
        print("✓ Successfully enhanced analysis with OpenAI")
        return basic_results
        
    except Exception as e:
        print(f"Error merging AI analysis: {e}")
        return basic_results
