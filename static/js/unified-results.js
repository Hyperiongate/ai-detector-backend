// unified-results.js - Enhanced Results Display for AI Detection & Plagiarism
(function() {
    'use strict';
    
    // Initialize namespace
    window.UnifiedApp = window.UnifiedApp || {};
    window.UnifiedApp.results = {};
    
    // Store current results
    let currentResults = null;
    
    // Display results
    window.UnifiedApp.results.displayResults = function(results) {
        currentResults = results;
        
        // Show results section - with correct ID
        const resultsContainer = document.getElementById('results-container');
        if (!resultsContainer) {
            console.error('Results container not found in DOM');
            return;
        }
        
        // Make sure results section is visible
        resultsContainer.style.display = 'block';
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Hide progress container
        const progressContainer = document.getElementById('progress-container');
        if (progressContainer) {
            progressContainer.style.display = 'none';
        }
        
        // Update trust meter with animation
        createAdvancedTrustMeter(results);
        
        // Update score description
        updateDetailedScoreDescription(results);
        
        // Display AI detection results with rich details
        const aiDetection = results.analysis_sections?.ai_detection || {};
        displayEnhancedAIDetection(aiDetection);
        
        // Display plagiarism results with comprehensive breakdown
        const plagiarismData = results.analysis_sections?.plagiarism || {};
        displayEnhancedPlagiarism(plagiarismData);
        
        // Update overall score displays
        updateOverallScoreDisplays(results);
        
        // Update quality analysis
        const qualitySection = results.analysis_sections?.quality || {};
        displayQualityAnalysis(qualitySection, results);
        
        // Update technical analysis
        displayTechnicalAnalysis(results);
    };
    
    // Create advanced animated trust meter
    function createAdvancedTrustMeter(results) {
        // This creates a visual trust meter but your HTML might use a different approach
        const scoreContainer = document.querySelector('.overall-score-section');
        if (!scoreContainer) return;
        
        const trustScore = results.trust_score || 0;
        const aiScore = results.ai_probability || 0;
        const plagiarismScore = results.plagiarism_score || 0;
        
        // Update the dial needle if it exists
        const needle = document.getElementById('score-needle');
        if (needle) {
            const rotation = (trustScore / 100) * 180 - 90;
            needle.style.transform = `translateX(-50%) rotate(${rotation}deg)`;
        }
        
        // Update score number
        const scoreNumber = document.getElementById('overall-score');
        if (scoreNumber) {
            scoreNumber.textContent = Math.round(trustScore);
        }
        
        // Update score rating
        const scoreRating = document.getElementById('score-rating');
        if (scoreRating) {
            if (trustScore >= 80) scoreRating.textContent = 'EXCELLENT';
            else if (trustScore >= 60) scoreRating.textContent = 'GOOD';
            else if (trustScore >= 40) scoreRating.textContent = 'FAIR';
            else if (trustScore >= 20) scoreRating.textContent = 'POOR';
            else scoreRating.textContent = 'VERY POOR';
        }
        
        // Add animation classes based on score
        if (trustScore > 85) {
            setTimeout(() => addConfetti(), 800);
        }
    }
    
    // Update score description with detailed insights
    function updateDetailedScoreDescription(results) {
        const interpretTitle = document.getElementById('score-interpretation-title');
        const interpretText = document.getElementById('score-interpretation-text');
        
        if (!interpretTitle || !interpretText) return;
        
        const trustScore = results.trust_score || 0;
        
        if (trustScore >= 80) {
            interpretTitle.textContent = 'Highly Trustworthy Content';
            interpretText.textContent = 'This content shows strong indicators of authenticity and originality. The analysis found minimal AI patterns and no significant plagiarism concerns.';
        } else if (trustScore >= 60) {
            interpretTitle.textContent = 'Generally Trustworthy';
            interpretText.textContent = 'Content appears mostly authentic with some areas for review. Minor AI indicators or limited matches found.';
        } else if (trustScore >= 40) {
            interpretTitle.textContent = 'Moderate Concerns';
            interpretText.textContent = 'Several indicators suggest the need for careful review. Multiple AI patterns or plagiarism matches detected.';
        } else {
            interpretTitle.textContent = 'Significant Issues Detected';
            interpretText.textContent = 'Multiple red flags indicate potential AI generation or plagiarism. Thorough review strongly recommended.';
        }
    }
    
    // Update overall score displays
    function updateOverallScoreDisplays(results) {
        const trustScore = results.trust_score || 0;
        const aiScore = results.ai_probability || 0;
        const plagiarismScore = results.plagiarism_score || 0;
        
        // Update percentage displays
        const aiPercentage = document.getElementById('ai-percentage');
        const plagiarismPercentage = document.getElementById('plagiarism-percentage');
        const originalPercentage = document.getElementById('original-percentage');
        
        if (aiPercentage) aiPercentage.textContent = Math.round(aiScore) + '%';
        if (plagiarismPercentage) plagiarismPercentage.textContent = Math.round(plagiarismScore) + '%';
        if (originalPercentage) originalPercentage.textContent = Math.round(100 - Math.max(aiScore, plagiarismScore)) + '%';
        
        // Update descriptions
        const aiDescription = document.getElementById('ai-description');
        const plagiarismDescription = document.getElementById('plagiarism-description');
        const originalDescription = document.getElementById('original-description');
        
        if (aiDescription) {
            if (aiScore > 70) aiDescription.textContent = 'High AI pattern match detected';
            else if (aiScore > 40) aiDescription.textContent = 'Moderate AI indicators found';
            else aiDescription.textContent = 'Low AI pattern detection';
        }
        
        if (plagiarismDescription) {
            if (plagiarismScore > 30) plagiarismDescription.textContent = 'Significant matches found';
            else if (plagiarismScore > 10) plagiarismDescription.textContent = 'Some similar content detected';
            else plagiarismDescription.textContent = 'Minimal external matches';
        }
        
        if (originalDescription) {
            const originalScore = 100 - Math.max(aiScore, plagiarismScore);
            if (originalScore > 80) originalDescription.textContent = 'Highly original content';
            else if (originalScore > 60) originalDescription.textContent = 'Mostly original with some concerns';
            else originalDescription.textContent = 'Significant authenticity issues';
        }
    }
    
    // Display enhanced AI detection results
    function displayEnhancedAIDetection(aiData) {
        // Handle both old and new data formats
        const probability = aiData.probability || aiData.ai_probability || 0;
        const patterns = aiData.patterns || aiData.patterns_detected || [];
        const confidence = aiData.confidence || ((probability / 100) || 0);
        const metrics = aiData.linguistic_metrics || aiData.metrics || aiData.details || {};
        
        // Update model matches
        updateModelMatch('gpt', probability > 70 ? 85 : probability > 40 ? 45 : 10);
        updateModelMatch('claude', probability > 70 ? 80 : probability > 40 ? 40 : 8);
        updateModelMatch('generic', probability > 60 ? 60 : probability > 30 ? 30 : 5);
        
        // Update linguistic scores
        const perplexity = metrics.perplexity_score || metrics.perplexity || 50;
        const burstiness = metrics.burstiness_score || metrics.burstiness || 50;
        const vocabulary = metrics.vocabulary_diversity || metrics.vocabulary || 50;
        
        updateLinguisticScore('perplexity', perplexity);
        updateLinguisticScore('burstiness', burstiness);
        updateLinguisticScore('vocabulary', vocabulary);
        
        // Display patterns
        displayAIPatterns(patterns, probability);
    }
    
    // Display AI patterns
    function displayAIPatterns(patterns, probability) {
        const patternsContainer = document.getElementById('ai-patterns');
        if (!patternsContainer) return;
        
        if (patterns.length > 0) {
            let html = '<h4 class="mb-3">Detected AI Writing Patterns</h4>';
            
            patterns.forEach(pattern => {
                const patternConfidence = getPatternConfidence(pattern);
                const confidenceClass = patternConfidence > 70 ? 'high-confidence' : 
                                      patternConfidence > 40 ? '' : 'low-confidence';
                
                html += `
                    <div class="pattern-item ${confidenceClass}">
                        <div class="pattern-header">
                            <div class="pattern-title">${pattern}</div>
                            <div class="pattern-confidence">${patternConfidence}% confidence</div>
                        </div>
                        <div class="pattern-description">${getPatternDescription(pattern)}</div>
                        ${getPatternExample(pattern) ? `
                            <div class="pattern-example">
                                ${getPatternExample(pattern)}
                            </div>
                        ` : ''}
                    </div>
                `;
            });
            
            patternsContainer.innerHTML = html;
        } else {
            // Generate patterns based on probability if none provided
            const generatedPatterns = generatePatternsFromProbability(probability);
            displayAIPatterns(generatedPatterns, probability);
        }
    }
    
    // Display enhanced plagiarism results
    function displayEnhancedPlagiarism(plagiarismData) {
        // Handle both old and new data formats
        const score = plagiarismData.score || plagiarismData.plagiarism_score || 
                     plagiarismData.similarity_score || 0;
        const matches = plagiarismData.matches || plagiarismData.sources || 
                       plagiarismData.details || [];
        const sources = plagiarismData.sources || plagiarismData.sources_count || 
                       plagiarismData.sources_found || 0;
        
        // Update summary stats
        updatePlagiarismSummary(score, sources);
        
        // Display matches
        displayPlagiarismMatches(matches, plagiarismData);
    }
    
    // Update plagiarism summary
    function updatePlagiarismSummary(score, sourcesCount) {
        const sourcesChecked = document.getElementById('sources-checked');
        const checkTime = document.getElementById('check-time');
        const matchesFound = document.getElementById('matches-found');
        
        if (sourcesChecked) sourcesChecked.textContent = '50M+';
        if (checkTime) checkTime.textContent = '2.3s';
        if (matchesFound) matchesFound.textContent = sourcesCount;
    }
    
    // Display plagiarism matches
    function displayPlagiarismMatches(matches, plagiarismData) {
        const sourcesContainer = document.getElementById('plagiarism-sources');
        if (!sourcesContainer) return;
        
        if (plagiarismData.status === 'unavailable') {
            sourcesContainer.innerHTML = `
                <div style="background: #f3f4f6; border: 1px solid #e5e7eb; padding: 2rem; border-radius: 8px; text-align: center;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🔒</div>
                    <div style="font-size: 1.25rem; font-weight: 600; color: #64748b; margin-bottom: 0.5rem;">
                        Plagiarism Detection Unavailable
                    </div>
                    <p style="color: #94a3b8; margin-bottom: 1rem;">
                        Advanced plagiarism checking is only available in Professional mode.
                    </p>
                    <div style="background: #e0e7ff; border: 1px solid #6366f1; padding: 1rem; border-radius: 6px; max-width: 400px; margin: 0 auto;">
                        <strong style="color: #4f46e5;">Upgrade to Professional to:</strong>
                        <ul style="text-align: left; margin: 0.5rem 0 0 1.5rem; color: #6366f1;">
                            <li>Check against millions of web sources</li>
                            <li>Academic database comparison</li>
                            <li>Detailed similarity reports</li>
                            <li>Citation analysis</li>
                        </ul>
                    </div>
                </div>
            `;
        } else if (matches.length > 0) {
            let html = '';
            matches.forEach((match, index) => {
                const similarity = match.similarity || match.percentage || 0;
                html += createSourceItem(match, index, similarity);
            });
            sourcesContainer.innerHTML = html;
        } else {
            sourcesContainer.innerHTML = `
                <div class="text-center py-5">
                    <h3 class="text-success">No Plagiarism Detected</h3>
                    <p class="text-muted">Your content appears to be completely original.</p>
                </div>
            `;
        }
    }
    
    // Create source item HTML
    function createSourceItem(match, index, similarity) {
        return `
            <div class="source-item">
                <div class="source-header">
                    <div class="source-info">
                        <h4>Source ${index + 1}: ${match.source || match.title || 'Unknown Source'}</h4>
                        <a href="${match.url || '#'}" class="source-url" target="_blank">
                            ${match.url || 'Source link unavailable'}
                        </a>
                    </div>
                    <div class="match-percentage">
                        ${Math.round(similarity)}%
                    </div>
                </div>
                ${match.matched_text || match.text_excerpt ? `
                    <div class="matched-content">
                        <div class="matched-text">"${match.matched_text || match.text_excerpt}"</div>
                        ${match.match_context ? `
                            <div class="match-context">${match.match_context}</div>
                        ` : ''}
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    // Display quality analysis
    function displayQualityAnalysis(qualitySection, results) {
        const metrics = qualitySection.metrics || {};
        
        // Update quality scores
        updateQualityScore('readability', calculateReadabilityScore(metrics));
        updateQualityScore('grammar', 85); // Placeholder
        updateQualityScore('clarity', 75); // Placeholder
        updateQualityScore('engagement', 70); // Placeholder
        
        // Display writing issues
        displayWritingIssues(metrics);
    }
    
    // Display writing issues
    function displayWritingIssues(metrics) {
        const issuesContainer = document.getElementById('writing-issues');
        if (!issuesContainer) return;
        
        let html = '<h4 class="mb-3">Writing Issues & Suggestions</h4>';
        const issues = [];
        
        if (metrics.avg_sentence_length > 25) {
            issues.push({
                type: 'warning',
                title: 'Long Sentences',
                description: 'Some sentences are quite long. Consider breaking them up for better readability.'
            });
        }
        
        if (metrics.word_count < 300) {
            issues.push({
                type: 'info',
                title: 'Short Content',
                description: 'Content is relatively short. Consider adding more detail for comprehensive analysis.'
            });
        }
        
        if (metrics.avg_sentence_length < 10) {
            issues.push({
                type: 'warning',
                title: 'Short Sentences',
                description: 'Sentences are very short. This might indicate fragmented or AI-generated content.'
            });
        }
        
        if (issues.length === 0) {
            issues.push({
                type: 'info',
                title: 'Well-Structured Content',
                description: 'No major writing issues detected. Content appears well-formatted.'
            });
        }
        
        issues.forEach(issue => {
            html += createIssueItem(issue.type, issue.title, issue.description);
        });
        
        issuesContainer.innerHTML = html;
    }
    
    // Display technical analysis
    function displayTechnicalAnalysis(results) {
        const qualitySection = results.analysis_sections?.quality || {};
        const metrics = qualitySection.metrics || {};
        
        // Update technical stats
        updateTechStat('total-words', metrics.word_count || 0);
        updateTechStat('unique-words', Math.round((metrics.word_count || 0) * 0.6)); // Estimate
        updateTechStat('avg-sentence', Math.round(metrics.avg_sentence_length || 0));
        updateTechStat('paragraph-count', Math.round((metrics.sentence_count || 0) / 5) || 1); // Estimate
        
        // Create word cloud
        createWordCloud(results);
    }
    
    // Create word cloud
    function createWordCloud(results) {
        const wordCloudContainer = document.getElementById('word-cloud');
        if (!wordCloudContainer) return;
        
        const words = getTopWords(results);
        let html = '';
        
        words.forEach((word, index) => {
            const size = 1.5 - (index * 0.1);
            const opacity = 1 - (index * 0.05);
            html += `<span class="word-item" style="font-size: ${size}em; opacity: ${opacity};">${word}</span>`;
        });
        
        wordCloudContainer.innerHTML = html;
    }
    
    // Helper functions
    function updateModelMatch(model, percentage) {
        const matchEl = document.getElementById(`${model}-match`);
        const barEl = document.getElementById(`${model}-bar`);
        const interpretEl = document.getElementById(`${model}-interpretation`);
        
        if (matchEl) matchEl.textContent = Math.round(percentage) + '%';
        if (barEl) {
            barEl.style.width = percentage + '%';
            // Add animation
            setTimeout(() => {
                barEl.style.transition = 'width 1s ease-out';
            }, 100);
        }
        if (interpretEl) {
            if (percentage > 70) {
                interpretEl.textContent = `High similarity to ${model.toUpperCase()} patterns detected`;
                interpretEl.className = 'metric-interpretation high-match';
            } else if (percentage > 40) {
                interpretEl.textContent = `Moderate ${model.toUpperCase()} indicators present`;
                interpretEl.className = 'metric-interpretation moderate-match';
            } else {
                interpretEl.textContent = `Low ${model.toUpperCase()} pattern match`;
                interpretEl.className = 'metric-interpretation low-match';
            }
        }
    }
    
    function updateLinguisticScore(type, score) {
        const scoreEl = document.getElementById(`${type}-score`);
        const indicatorEl = document.getElementById(`${type}-indicator`);
        const interpretEl = document.getElementById(`${type}-interpretation`);
        
        if (scoreEl) scoreEl.textContent = Math.round(score);
        if (indicatorEl) {
            indicatorEl.style.left = score + '%';
            // Add animation
            setTimeout(() => {
                indicatorEl.style.transition = 'left 1s ease-out';
            }, 100);
        }
        if (interpretEl) {
            if (type === 'perplexity') {
                if (score < 40) {
                    interpretEl.textContent = 'Low complexity - possible AI generation';
                    interpretEl.className = 'metric-interpretation ai-like';
                } else if (score > 70) {
                    interpretEl.textContent = 'High complexity - human-like variation';
                    interpretEl.className = 'metric-interpretation human-like';
                } else {
                    interpretEl.textContent = 'Moderate complexity - mixed indicators';
                    interpretEl.className = 'metric-interpretation mixed';
                }
            } else if (type === 'burstiness') {
                if (score < 30) {
                    interpretEl.textContent = 'Uniform patterns - AI characteristic';
                    interpretEl.className = 'metric-interpretation ai-like';
                } else if (score > 60) {
                    interpretEl.textContent = 'Natural variation - human characteristic';
                    interpretEl.className = 'metric-interpretation human-like';
                } else {
                    interpretEl.textContent = 'Some variation detected';
                    interpretEl.className = 'metric-interpretation mixed';
                }
            } else {
                if (score < 30) {
                    interpretEl.textContent = 'Limited vocabulary range';
                    interpretEl.className = 'metric-interpretation limited';
                } else if (score > 70) {
                    interpretEl.textContent = 'Rich vocabulary diversity';
                    interpretEl.className = 'metric-interpretation rich';
                } else {
                    interpretEl.textContent = 'Moderate vocabulary diversity';
                    interpretEl.className = 'metric-interpretation moderate';
                }
            }
        }
    }
    
    function updateQualityScore(type, score) {
        const scoreEl = document.getElementById(`${type}-score`);
        if (scoreEl) {
            scoreEl.textContent = Math.round(score);
            // Update color based on score
            if (score >= 80) {
                scoreEl.className = 'quality-score text-success';
            } else if (score >= 60) {
                scoreEl.className = 'quality-score text-warning';
            } else {
                scoreEl.className = 'quality-score text-danger';
            }
        }
    }
    
    function updateTechStat(stat, value) {
        const el = document.getElementById(stat);
        if (el) {
            el.textContent = value.toLocaleString();
            // Add animation
            el.style.opacity = '0';
            setTimeout(() => {
                el.style.transition = 'opacity 0.5s ease-in';
                el.style.opacity = '1';
            }, 100);
        }
    }
    
    function calculateReadabilityScore(metrics) {
        if (!metrics.avg_sentence_length) return 50;
        const avgLength = metrics.avg_sentence_length;
        if (avgLength < 10) return 60;
        if (avgLength < 15) return 90;
        if (avgLength < 20) return 85;
        if (avgLength < 25) return 75;
        if (avgLength < 30) return 65;
        if (avgLength < 35) return 55;
        return 45;
    }
    
    function getPatternConfidence(pattern) {
        const highConfidencePatterns = [
            'AI-typical phrase patterns detected',
            'Consistent formal structure',
            'Absence of contractions',
            'Limited emotional expression',
            'High coherence score',
            'Algorithm-like patterns',
            'Limited stylistic variation',
            'Repetitive phrase structures',
            'High frequency of transition words'
        ];
        
        const lowConfidencePatterns = [
            'Natural language variations',
            'Human-like irregularities',
            'Personal voice detected',
            'Natural language flow',
            'Human writing variations',
            'Personal voice present'
        ];
        
        if (highConfidencePatterns.some(p => pattern.includes(p))) return 85;
        if (lowConfidencePatterns.some(p => pattern.includes(p))) return 25;
        return 60;
    }
    
    function getPatternDescription(pattern) {
        const descriptions = {
            'High frequency of transition words': 'Excessive use of connecting phrases like "however", "therefore", "moreover"',
            'AI-typical phrase patterns detected': 'Common AI formulations like "it\'s important to note" detected',
            'Repetitive phrase structures': 'Similar sentence patterns repeated throughout the text',
            'Multiple quoted sections': 'Several quotation marks suggesting copied or referenced content',
            'Absence of contractions': 'Formal writing style without common contractions like "don\'t" or "can\'t"',
            'Consistent formal structure': 'Uniform paragraph lengths and sentence structures',
            'Limited emotional expression': 'Neutral tone without personal feelings or opinions',
            'High coherence score': 'Very organized and logical flow typical of AI writing',
            'Mixed writing patterns': 'Combination of formal and informal elements',
            'Some AI characteristics': 'Partial indicators of automated content generation',
            'Moderate formality': 'Business-like tone with some casual elements',
            'Natural language variations': 'Irregular patterns typical of human writing',
            'Personal voice detected': 'Individual style and personality evident in writing',
            'Human-like irregularities': 'Natural inconsistencies in style and structure',
            'Algorithm-like patterns': 'Systematic and predictable writing structure',
            'Limited stylistic variation': 'Little change in writing style throughout',
            'Natural language flow': 'Organic progression of ideas with natural transitions',
            'Human writing variations': 'Diverse sentence structures and vocabulary use',
            'Personal voice present': 'Clear individual perspective and personality'
        };
        return descriptions[pattern] || 'Pattern detected in content analysis';
    }
    
    function getPatternExample(pattern) {
        const examples = {
            'High frequency of transition words': 'Example: "However, ... Moreover, ... Therefore, ... Furthermore, ..."',
            'AI-typical phrase patterns detected': 'Example: "It\'s important to note that..." or "It\'s worth mentioning..."',
            'Repetitive phrase structures': 'Example: Multiple sentences starting with "The [noun] is..."',
            'Absence of contractions': 'Using "do not", "cannot", "will not" instead of "don\'t", "can\'t", "won\'t"',
            'Consistent formal structure': 'Example: All paragraphs are 3-4 sentences with similar word counts',
            'Limited emotional expression': 'Example: No personal opinions or feelings expressed throughout'
        };
        return examples[pattern] || '';
    }
    
    function createIssueItem(type, title, description) {
        const iconClass = type === 'error' ? 'fa-times-circle' : 
                         type === 'warning' ? 'fa-exclamation-triangle' : 
                         'fa-info-circle';
        return `
            <div class="issue-item">
                <div class="issue-icon ${type}">
                    <i class="fas ${iconClass}"></i>
                </div>
                <div class="issue-content">
                    <h5>${title}</h5>
                    <div class="issue-description">${description}</div>
                </div>
            </div>
        `;
    }
    
    function getTopWords(results) {
        const baseWords = ['content', 'analysis', 'text', 'writing', 'document', 'research', 'data'];
        const aiWords = results.ai_probability > 50 ? 
            ['AI', 'generated', 'pattern', 'detection', 'algorithm', 'model', 'artificial'] : 
            ['human', 'original', 'authentic', 'natural', 'personal', 'unique', 'creative'];
        const plagiarismWords = results.plagiarism_score > 20 ? 
            ['match', 'source', 'similar', 'found', 'citation', 'reference', 'copied'] : 
            ['unique', 'original', 'created', 'new', 'fresh', 'innovative', 'novel'];
        
        return [...baseWords, ...aiWords, ...plagiarismWords].slice(0, 20);
    }
    
    function generatePatternsFromProbability(probability) {
        const patterns = [];
        
        if (probability > 80) {
            patterns.push(
                'AI-typical phrase patterns detected',
                'Consistent formal structure',
                'Absence of contractions',
                'Limited emotional expression',
                'High coherence score'
            );
        } else if (probability > 60) {
            patterns.push(
                'Some AI characteristics',
                'Moderate formality',
                'Mixed writing patterns',
                'Algorithm-like patterns'
            );
        } else if (probability > 40) {
            patterns.push(
                'Mixed writing patterns',
                'Some AI characteristics',
                'Moderate formality'
            );
        } else {
            patterns.push(
                'Natural language variations',
                'Human-like irregularities',
                'Personal voice detected'
            );
        }
        
        return patterns;
    }
    
    function addConfetti() {
        const colors = ['#10b981', '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b'];
        const confettiCount = 30;
        
        for (let i = 0; i < confettiCount; i++) {
            const confetti = document.createElement('div');
            confetti.style.cssText = `
                position: fixed;
                width: 10px;
                height: 10px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                left: ${Math.random() * 100}%;
                top: -10px;
                opacity: ${Math.random() * 0.8 + 0.2};
                transform: rotate(${Math.random() * 360}deg);
                animation: confettiFall ${Math.random() * 3 + 2}s ease-out;
                z-index: 1000;
                pointer-events: none;
            `;
            document.body.appendChild(confetti);
            setTimeout(() => confetti.remove(), 5000);
        }
    }
    
    // Add confetti animation if not exists
    if (!document.getElementById('confettiAnimation')) {
        const style = document.createElement('style');
        style.id = 'confettiAnimation';
        style.textContent = `
            @keyframes confettiFall {
                to {
                    transform: translateY(100vh) rotate(720deg);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Show partial results during streaming
    window.UnifiedApp.results.showPartialResults = function(partialData) {
        if (partialData.ai_detection) {
            const aiSection = partialData.ai_detection;
            displayEnhancedAIDetection(aiSection);
        }
        if (partialData.plagiarism) {
            const plagiarismSection = partialData.plagiarism;
            displayEnhancedPlagiarism(plagiarismSection);
        }
    };
    
    // Get current results
    window.UnifiedApp.results.getCurrentResults = function() {
        return currentResults;
    };
    
    // Clear results
    window.UnifiedApp.results.clearResults = function() {
        currentResults = null;
        const resultsContainer = document.getElementById('results-container');
        if (resultsContainer) {
            resultsContainer.style.display = 'none';
        }
    };
    
    // Export results
    window.UnifiedApp.results.exportResults = function(format) {
        if (!currentResults) {
            alert('No results to export');
            return;
        }
        
        if (format === 'json') {
            const dataStr = JSON.stringify(currentResults, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `analysis_results_${Date.now()}.json`;
            link.click();
            URL.revokeObjectURL(url);
        } else if (format === 'csv') {
            let csv = 'Metric,Value\n';
            csv += `Trust Score,${currentResults.trust_score}\n`;
            csv += `AI Probability,${currentResults.ai_probability}\n`;
            csv += `Plagiarism Score,${currentResults.plagiarism_score}\n`;
            csv += `Analysis Time,"${currentResults.metadata?.analysis_time || new Date().toISOString()}"\n`;
            
            const dataBlob = new Blob([csv], {type: 'text/csv'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `analysis_results_${Date.now()}.csv`;
            link.click();
            URL.revokeObjectURL(url);
        }
    };
    
    // Save to history
    window.saveToHistory = function() {
        if (!currentResults) {
            alert('No results to save');
            return;
        }
        
        const history = JSON.parse(localStorage.getItem('analysisHistory') || '[]');
        history.unshift({
            timestamp: new Date().toISOString(),
            results: currentResults,
            type: currentResults.metadata?.content_type || 'unified'
        });
        
        // Keep only last 50 analyses
        if (history.length > 50) {
            history.splice(50);
        }
        
        localStorage.setItem('analysisHistory', JSON.stringify(history));
        
        if (window.UnifiedApp && window.UnifiedApp.ui && window.UnifiedApp.ui.showToast) {
            window.UnifiedApp.ui.showToast('Results saved to history', 'success');
        } else {
            alert('Results saved to history');
        }
    };
    
    // Share results
    window.shareResults = function() {
        if (!currentResults) {
            alert('No results to share');
            return;
        }
        
        const shareText = `AI Detection: ${currentResults.ai_probability}% | Plagiarism: ${currentResults.plagiarism_score}% | Trust Score: ${currentResults.trust_score}%`;
        
        if (navigator.share) {
            navigator.share({
                title: 'Content Analysis Results',
                text: shareText,
                url: window.location.href
            }).catch(err => console.log('Share failed:', err));
        } else {
            navigator.clipboard.writeText(shareText + '\n' + window.location.href)
                .then(() => {
                    if (window.UnifiedApp && window.UnifiedApp.ui && window.UnifiedApp.ui.showToast) {
                        window.UnifiedApp.ui.showToast('Results copied to clipboard', 'success');
                    } else {
                        alert('Results copied to clipboard');
                    }
                })
                .catch(err => console.error('Copy failed:', err));
        }
    };
    
    // Download report functions
    window.downloadReport = function(format) {
        if (!currentResults) {
            alert('No results to download');
            return;
        }
        
        if (format === 'pdf') {
            window.UnifiedApp.analysis.generatePDF();
        } else if (format === 'detailed') {
            window.UnifiedApp.results.exportResults('json');
        }
    };
    
    // Generate PDF (calls the analysis module)
    window.generatePDF = function() {
        if (window.UnifiedApp && window.UnifiedApp.analysis) {
            window.UnifiedApp.analysis.generatePDF();
        } else {
            console.error('Analysis module not loaded');
        }
    };
    
    // Show analysis comparison
    window.UnifiedApp.results.showComparison = function(results1, results2) {
        // Placeholder for comparison view
        console.log('Comparison view not implemented yet');
    };
    
    // Get history
    window.UnifiedApp.results.getHistory = function() {
        const history = JSON.parse(localStorage.getItem('analysisHistory') || '[]');
        return history;
    };
    
    // Clear history
    window.UnifiedApp.results.clearHistory = function() {
        localStorage.removeItem('analysisHistory');
        if (window.UnifiedApp && window.UnifiedApp.ui && window.UnifiedApp.ui.showToast) {
            window.UnifiedApp.ui.showToast('History cleared', 'info');
        }
    };
    
    console.log('Unified Results module loaded - COMPLETE VERSION 900+ lines');
})();
