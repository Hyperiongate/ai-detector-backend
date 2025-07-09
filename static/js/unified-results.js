// unified-results.js - Results Display for AI Detection & Plagiarism
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
        
        // Show results section
        const resultsSection = document.getElementById('resultsSection');
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Update trust meter
        createTrustMeter(results);
        
        // Update score description
        updateScoreDescription(results);
        
        // Display AI detection results
        displayAIDetection(results.ai_detection || {});
        
        // Display plagiarism results
        displayPlagiarism(results.plagiarism || {});
        
        // Auto-expand first section
        const firstSection = document.querySelector('.analysis-section');
        if (firstSection) {
            const content = firstSection.querySelector('.section-content');
            content.classList.add('expanded');
            firstSection.classList.add('expanded');
        }
    };
    
    // Create animated trust meter
    function createTrustMeter(results) {
        const svg = document.getElementById('trustMeter');
        const aiScore = results.ai_probability || 0;
        const plagiarismScore = results.plagiarism_score || 0;
        
        // Calculate overall trust score (inverse of AI and plagiarism scores)
        const trustScore = Math.max(0, 100 - ((aiScore + plagiarismScore) / 2));
        
        svg.innerHTML = `
            <svg viewBox="0 0 250 250" xmlns="http://www.w3.org/2000/svg">
                <!-- Background circle -->
                <circle cx="125" cy="125" r="110" fill="none" stroke="#e5e7eb" stroke-width="20"/>
                
                <!-- Progress circle -->
                <circle 
                    cx="125" 
                    cy="125" 
                    r="110" 
                    fill="none" 
                    stroke="${getScoreColor(trustScore)}" 
                    stroke-width="20"
                    stroke-linecap="round"
                    stroke-dasharray="${trustScore * 3.46} 346"
                    transform="rotate(-90 125 125)"
                    style="transition: stroke-dasharray 1s ease-in-out;"
                />
                
                <!-- Center text -->
                <text x="125" y="110" text-anchor="middle" font-size="48" font-weight="bold" fill="${getScoreColor(trustScore)}">
                    ${Math.round(trustScore)}%
                </text>
                <text x="125" y="140" text-anchor="middle" font-size="16" fill="#64748b">
                    Trust Score
                </text>
                
                <!-- Sub-scores -->
                <text x="125" y="170" text-anchor="middle" font-size="12" fill="#94a3b8">
                    AI: ${Math.round(aiScore)}% | Plagiarism: ${Math.round(plagiarismScore)}%
                </text>
            </svg>
        `;
    }
    
    // Update score description
    function updateScoreDescription(results) {
        const desc = document.getElementById('scoreDescription');
        const aiScore = results.ai_probability || 0;
        const plagiarismScore = results.plagiarism_score || 0;
        
        let message = '';
        
        if (aiScore > 70) {
            message = 'High probability of AI-generated content detected. ';
        } else if (aiScore > 40) {
            message = 'Moderate AI characteristics found. ';
        } else {
            message = 'Content appears to be human-written. ';
        }
        
        if (plagiarismScore > 30) {
            message += 'Significant plagiarism detected.';
        } else if (plagiarismScore > 10) {
            message += 'Some matching content found.';
        } else {
            message += 'Content appears to be original.';
        }
        
        desc.textContent = message;
    }
    
    // Display AI detection results
    function displayAIDetection(aiData) {
        const container = document.getElementById('aiDetectionResults');
        
        const probability = aiData.probability || 0;
        const patterns = aiData.patterns || [];
        const confidence = aiData.confidence || 0;
        
        let html = `
            <div class="result-card">
                <div class="result-label">AI Probability Score</div>
                <div class="confidence-meter">
                    <div class="meter-bar">
                        <div class="meter-fill ${getConfidenceClass(probability)}" style="width: ${probability}%"></div>
                    </div>
                    <div class="meter-value">${probability}%</div>
                </div>
            </div>
            
            <div class="result-card">
                <div class="result-label">Confidence Level</div>
                <div class="result-value">${confidence}% confidence in this assessment</div>
            </div>
            
            <div class="result-card">
                <div class="result-label">AI Pattern Analysis</div>
                <div class="result-value">
                    <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                        ${patterns.map(pattern => `<li>${pattern}</li>`).join('')}
                    </ul>
                </div>
            </div>
            
            <div class="result-card">
                <div class="result-label">Writing Style Assessment</div>
                <div class="result-value">
                    ${aiData.style_analysis || 'Analysis of sentence structure, vocabulary diversity, and writing patterns'}
                </div>
            </div>
            
            <div class="result-card">
                <div class="result-label">AI Models Detected</div>
                <div class="result-value">
                    ${aiData.detected_models ? aiData.detected_models.join(', ') : 'Pattern matching against ChatGPT, Claude, Gemini, and other models'}
                </div>
            </div>
        `;
        
        container.innerHTML = html;
    }
    
    // Display plagiarism results
    function displayPlagiarism(plagiarismData) {
        const container = document.getElementById('plagiarismResults');
        
        const score = plagiarismData.score || 0;
        const matches = plagiarismData.matches || [];
        const sources = plagiarismData.sources || 0;
        
        let html = `
            <div class="result-card">
                <div class="result-label">Plagiarism Score</div>
                <div class="confidence-meter">
                    <div class="meter-bar">
                        <div class="meter-fill ${getConfidenceClass(score)}" style="width: ${score}%"></div>
                    </div>
                    <div class="meter-value">${score}%</div>
                </div>
            </div>
            
            <div class="result-card">
                <div class="result-label">Sources Checked</div>
                <div class="result-value">Compared against ${sources.toLocaleString()} online sources</div>
            </div>
            
            <div class="result-card">
                <div class="result-label">Matching Content Found</div>
                <div class="result-value">
                    ${matches.length > 0 ? 
                        `<ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                            ${matches.slice(0, 5).map(match => `
                                <li>
                                    <strong>${match.percentage}% match</strong> - ${match.source}
                                    ${match.url ? `<br><a href="${match.url}" target="_blank" style="color: var(--primary-color); font-size: 0.875rem;">View source</a>` : ''}
                                </li>
                            `).join('')}
                        </ul>` : 
                        'No significant matches found'
                    }
                </div>
            </div>
            
            <div class="result-card">
                <div class="result-label">Originality Assessment</div>
                <div class="result-value">
                    ${100 - score}% of the content appears to be original
                </div>
            </div>
            
            <div class="result-card">
                <div class="result-label">Citation Check</div>
                <div class="result-value">
                    ${plagiarismData.citations_found || 0} citations detected. 
                    ${plagiarismData.citations_needed ? `Consider adding ${plagiarismData.citations_needed} more citations.` : 'Citation level appears appropriate.'}
                </div>
            </div>
        `;
        
        container.innerHTML = html;
    }
    
    // Helper functions
    function getScoreColor(score) {
        if (score >= 80) return '#10b981';
        if (score >= 60) return '#f59e0b';
        return '#ef4444';
    }
    
    function getConfidenceClass(value) {
        if (value >= 70) return 'high';
        if (value >= 40) return 'medium';
        return 'low';
    }
    
    // Get current results
    window.UnifiedApp.results.getCurrentResults = function() {
        return currentResults;
    };
    
    // Clear results
    window.UnifiedApp.results.clearResults = function() {
        currentResults = null;
        const resultsSection = document.getElementById('resultsSection');
        resultsSection.style.display = 'none';
    };
    
})();
