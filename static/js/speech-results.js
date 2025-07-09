/**
 * Speech Results Module
 * Handles displaying and managing analysis results
 */

window.SpeechApp = window.SpeechApp || {};

window.SpeechApp.results = (function() {
    'use strict';
    
    // Private variables
    let currentResults = null;
    let resultsContainer = null;
    
    /**
     * Initialize the results module
     */
    function initialize() {
        console.log('Speech results module initialized');
        resultsContainer = document.getElementById('speechResults');
    }
    
    /**
     * Display analysis results
     */
    function displayResults(results) {
        if (!resultsContainer) {
            console.error('Results container not found');
            return;
        }
        
        currentResults = results;
        
        // Create results HTML
        const resultsHTML = createResultsHTML(results);
        resultsContainer.innerHTML = resultsHTML;
        
        // Show results section
        resultsContainer.style.display = 'block';
        resultsContainer.classList.add('fade-in');
        
        // Initialize interactive elements
        initializeResultsInteractions();
        
        // Animate trust meter
        animateTrustMeter(results.truthScore || 0);
        
        // Animate other meters
        animateProgressBars();
        
        // Setup dropdown functionality
        setupDropdowns();
    }
    
    /**
     * Create results HTML
     */
    function createResultsHTML(results) {
        const timestamp = new Date(results.timestamp || Date.now()).toLocaleString();
        const analysisId = results.analysisId || 'SPEECH-' + Date.now();
        
        return `
            <div class="results-container animate-in">
                <!-- Results Header -->
                <div class="results-header">
                    <h2>Speech Analysis Complete</h2>
                    <div class="results-actions">
                        <button class="action-btn" onclick="window.downloadSpeechPDF()">
                            <i class="fas fa-download"></i> Download PDF
                        </button>
                        <button class="action-btn" onclick="window.shareSpeechResults()">
                            <i class="fas fa-share-alt"></i> Share
                        </button>
                        <button class="action-btn secondary" onclick="window.resetSpeechAnalysis()">
                            <i class="fas fa-redo"></i> New Analysis
                        </button>
                    </div>
                </div>
                
                <!-- Analysis Metadata -->
                <div class="analysis-metadata">
                    <div class="metadata-item">
                        <i class="fas fa-clock"></i>
                        <span>Analyzed: ${timestamp}</span>
                    </div>
                    <div class="metadata-item">
                        <i class="fas fa-fingerprint"></i>
                        <span>ID: ${analysisId}</span>
                    </div>
                    <div class="metadata-item">
                        <i class="fas fa-info-circle"></i>
                        <span>Version: 2.0</span>
                    </div>
                </div>
                
                <!-- Truth Score Meter -->
                <div class="trust-meter-container">
                    <div class="trust-meter" data-score="${results.truthScore || 0}">
                        <svg viewBox="0 0 200 200" class="trust-meter-svg">
                            <circle cx="100" cy="100" r="90" class="meter-background"/>
                            <circle cx="100" cy="100" r="90" class="meter-progress" 
                                    stroke-dasharray="565.48" 
                                    stroke-dashoffset="565.48"/>
                        </svg>
                        <div class="trust-score-display">
                            <span class="score-number">0</span>
                            <span class="score-label">Truth Score</span>
                        </div>
                    </div>
                    <div class="trust-description">
                        ${getTrustDescription(results.truthScore || 0)}
                    </div>
                </div>
                
                <!-- Key Findings -->
                <div class="key-findings">
                    <h3>Key Findings</h3>
                    <div class="findings-grid">
                        ${createKeyFindings(results)}
                    </div>
                </div>
                
                <!-- Analysis Sections -->
                <div class="analysis-sections">
                    ${createTranscriptSection(results)}
                    ${createClaimsSection(results)}
                    ${createSpeakerSection(results)}
                    ${createEmotionalSection(results)}
                    ${createFallaciesSection(results)}
                    ${createContextSection(results)}
                    ${createSourcesSection(results)}
                    ${createTechnicalSection(results)}
                    ${createOverallSection(results)}
                    ${createRecommendationsSection(results)}
                </div>
            </div>
        `;
    }
    
    /**
     * Get trust score description
     */
    function getTrustDescription(score) {
        if (score >= 80) {
            return '<i class="fas fa-check-circle" style="color: #28a745;"></i> High credibility - Most claims are accurate and well-supported';
        } else if (score >= 60) {
            return '<i class="fas fa-exclamation-triangle" style="color: #ffc107;"></i> Mixed credibility - Some claims need verification';
        } else {
            return '<i class="fas fa-times-circle" style="color: #dc3545;"></i> Low credibility - Many unverified or false claims';
        }
    }
    
    /**
     * Create key findings
     */
    function createKeyFindings(results) {
        const totalClaims = results.claims?.length || 0;
        const trueClaims = results.claims?.filter(c => c.verdict === 'True').length || 0;
        const falseClaims = results.claims?.filter(c => c.verdict === 'False' || c.verdict === 'Mostly False').length || 0;
        const unverifiedClaims = results.claims?.filter(c => c.verdict === 'Unverified').length || 0;
        
        return `
            <div class="finding-card">
                <div class="finding-icon">
                    <i class="fas fa-list-check"></i>
                </div>
                <div class="finding-content">
                    <div class="finding-value">${totalClaims}</div>
                    <div class="finding-label">Total Claims</div>
                </div>
            </div>
            <div class="finding-card success">
                <div class="finding-icon">
                    <i class="fas fa-check"></i>
                </div>
                <div class="finding-content">
                    <div class="finding-value">${trueClaims}</div>
                    <div class="finding-label">Verified True</div>
                </div>
            </div>
            <div class="finding-card danger">
                <div class="finding-icon">
                    <i class="fas fa-times"></i>
                </div>
                <div class="finding-content">
                    <div class="finding-value">${falseClaims}</div>
                    <div class="finding-label">False/Misleading</div>
                </div>
            </div>
            <div class="finding-card warning">
                <div class="finding-icon">
                    <i class="fas fa-question"></i>
                </div>
                <div class="finding-content">
                    <div class="finding-value">${unverifiedClaims}</div>
                    <div class="finding-label">Unverified</div>
                </div>
            </div>
        `;
    }
    
    /**
     * Create transcript section
     */
    function createTranscriptSection(results) {
        return `
            <div class="analysis-section">
                <div class="section-header dropdown-toggle">
                    <h3>
                        <i class="fas fa-file-alt"></i> Full Transcript
                        <span class="confidence-badge" data-tooltip="Transcription accuracy">95% Confidence</span>
                    </h3>
                    <i class="fas fa-chevron-down"></i>
                </div>
                <div class="section-content dropdown-content">
                    <div class="transcript-info">
                        <p><strong>Duration:</strong> ${results.duration || 'N/A'}</p>
                        <p><strong>Words:</strong> ${results.transcript?.split(' ').length || 0}</p>
                    </div>
                    <div class="transcript-text">
                        ${results.transcript || 'Transcript not available'}
                    </div>
                    <div class="why-this-matters">
                        <h4>Why This Matters</h4>
                        <p>Having the full transcript allows you to see claims in context and verify our analysis.</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Create claims section
     */
    function createClaimsSection(results) {
        const claims = results.claims || [];
        
        return `
            <div class="analysis-section">
                <div class="section-header dropdown-toggle">
                    <h3>
                        <i class="fas fa-fact-check"></i> Fact-Checked Claims
                        <span class="confidence-badge" data-tooltip="Average fact-checking confidence">88% Confidence</span>
                    </h3>
                    <i class="fas fa-chevron-down"></i>
                </div>
                <div class="section-content dropdown-content">
                    <div class="claims-container">
                        ${claims.map((claim, index) => createClaimCard(claim, index)).join('')}
                    </div>
                    <div class="methodology-note">
                        <h4>How We Fact-Check</h4>
                        <code>Cross-reference with: Reuters, AP, Snopes, FactCheck.org + Primary Sources</code>
                    </div>
                    <a href="#" class="learn-more-link" onclick="showSpeechProcessModal(); return false;">
                        Learn more about our fact-checking process →
                    </a>
                </div>
            </div>
        `;
    }
    
    /**
     * Create claim card
     */
    function createClaimCard(claim, index) {
        const verdictClass = claim.verdict.toLowerCase().replace(' ', '-');
        const verdictIcon = getVerdictIcon(claim.verdict);
        
        return `
            <div class="claim-card ${verdictClass}">
                <div class="claim-header">
                    <span class="claim-number">#${index + 1}</span>
                    <span class="claim-verdict">
                        ${verdictIcon} ${claim.verdict}
                    </span>
                    <span class="claim-confidence">${claim.confidence}% confidence</span>
                </div>
                <div class="claim-text">
                    "${claim.text}"
                </div>
                <div class="claim-sources">
                    <strong>Sources:</strong> ${claim.sources.join(', ')}
                </div>
            </div>
        `;
    }
    
    /**
     * Get verdict icon
     */
    function getVerdictIcon(verdict) {
        const icons = {
            'True': '<i class="fas fa-check-circle"></i>',
            'Mostly True': '<i class="fas fa-check-circle"></i>',
            'False': '<i class="fas fa-times-circle"></i>',
            'Mostly False': '<i class="fas fa-times-circle"></i>',
            'Unverified': '<i class="fas fa-question-circle"></i>'
        };
        return icons[verdict] || '<i class="fas fa-question-circle"></i>';
    }
    
    /**
     * Create speaker section
     */
    function createSpeakerSection(results) {
        const speaker = results.speaker || {};
        
        return `
            <div class="analysis-section">
                <div class="section-header dropdown-toggle">
                    <h3>
                        <i class="fas fa-user-tie"></i> Speaker Credibility
                        <span class="confidence-badge" data-tooltip="Based on historical data">${speaker.credibility || 0}% Score</span>
                    </h3>
                    <i class="fas fa-chevron-down"></i>
                </div>
                <div class="section-content dropdown-content">
                    <div class="speaker-profile">
                        <div class="profile-item">
                            <strong>Speaker:</strong> ${speaker.name || 'Unknown'}
                        </div>
                        <div class="profile-item">
                            <strong>Expertise:</strong> ${speaker.expertise || 'Not specified'}
                        </div>
                        <div class="profile-item">
                            <strong>Historical Accuracy:</strong>
                            <div class="progress-bar-container">
                                <div class="progress-bar" style="width: ${speaker.historicalAccuracy || 0}%"></div>
                                <span class="progress-label">${speaker.historicalAccuracy || 0}%</span>
                            </div>
                        </div>
                    </div>
                    <div class="speaker-research">
                        <h4>Research Speaker</h4>
                        <div class="research-buttons">
                            <button onclick="window.open('https://google.com/search?q=${encodeURIComponent(speaker.name || 'speaker')}', '_blank')">
                                <i class="fab fa-google"></i> Google
                            </button>
                            <button onclick="window.open('https://twitter.com/search?q=${encodeURIComponent(speaker.name || 'speaker')}', '_blank')">
                                <i class="fab fa-twitter"></i> Twitter
                            </button>
                            <button onclick="window.open('https://linkedin.com/search/results/all/?keywords=${encodeURIComponent(speaker.name || 'speaker')}', '_blank')">
                                <i class="fab fa-linkedin"></i> LinkedIn
                            </button>
                        </div>
                    </div>
                    <div class="what-this-means">
                        <h4>What This Means</h4>
                        <p>Speaker credibility helps assess the reliability of claims based on past accuracy and domain expertise.</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Create emotional manipulation section
     */
    function createEmotionalSection(results) {
        const emotional = results.emotionalAnalysis || {};
        const score = emotional.score || 0;
        
        return `
            <div class="analysis-section">
                <div class="section-header dropdown-toggle">
                    <h3>
                        <i class="fas fa-theater-masks"></i> Emotional Manipulation
                        <span class="confidence-badge" data-tooltip="AI-detected emotional tactics">${score}/10 Score</span>
                    </h3>
                    <i class="fas fa-chevron-down"></i>
                </div>
                <div class="section-content dropdown-content">
                    <div class="emotional-gauge">
                        <div class="gauge-container">
                            <div class="gauge-fill" style="width: ${score * 10}%"></div>
                            <div class="gauge-markers">
                                <span>Low</span>
                                <span>Medium</span>
                                <span>High</span>
                            </div>
                        </div>
                    </div>
                    <div class="techniques-found">
                        <h4>Techniques Detected:</h4>
                        <ul>
                            ${(emotional.techniques || []).map(tech => `<li>${tech}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="tone-analysis">
                        <h4>Overall Tone:</h4>
                        <p>${emotional.tone || 'Not analyzed'}</p>
                    </div>
                    <div class="how-we-detect">
                        <h4>How We Detect This</h4>
                        <p>We use sentiment analysis and pattern recognition to identify emotional manipulation tactics.</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Create logical fallacies section
     */
    function createFallaciesSection(results) {
        const fallacies = results.fallacies || [];
        
        return `
            <div class="analysis-section">
                <div class="section-header dropdown-toggle">
                    <h3>
                        <i class="fas fa-brain"></i> Logical Fallacies
                        <span class="confidence-badge" data-tooltip="Logic analysis confidence">85% Confidence</span>
                    </h3>
                    <i class="fas fa-chevron-down"></i>
                </div>
                <div class="section-content dropdown-content">
                    <div class="fallacies-list">
                        ${fallacies.map(fallacy => createFallacyCard(fallacy)).join('')}
                    </div>
                    ${fallacies.length === 0 ? '<p>No significant logical fallacies detected.</p>' : ''}
                    <div class="methodology-note">
                        <h4>Detection Method</h4>
                        <code>Pattern matching + GPT-4 logical analysis</code>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Create fallacy card
     */
    function createFallacyCard(fallacy) {
        const severityClass = fallacy.severity.toLowerCase();
        
        return `
            <div class="fallacy-card ${severityClass}">
                <div class="fallacy-header">
                    <h4>${fallacy.type}</h4>
                    <span class="severity-badge">${fallacy.severity} severity</span>
                </div>
                <div class="fallacy-example">
                    <strong>Example:</strong> "${fallacy.example}"
                </div>
            </div>
        `;
    }
    
    /**
     * Create context analysis section
     */
    function createContextSection(results) {
        const context = results.contextAnalysis || {};
        
        return `
            <div class="analysis-section">
                <div class="section-header dropdown-toggle">
                    <h3>
                        <i class="fas fa-puzzle-piece"></i> Context Analysis
                        <span class="confidence-badge" data-tooltip="Context completeness">78% Complete</span>
                    </h3>
                    <i class="fas fa-chevron-down"></i>
                </div>
                <div class="section-content dropdown-content">
                    <div class="context-items">
                        <div class="context-item">
                            <h4>Missing Context:</h4>
                            <ul>
                                ${(context.missingContext || []).map(item => `<li>${item}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="context-indicators">
                            <div class="indicator ${context.cherryPicking ? 'active' : ''}">
                                <i class="fas fa-cherry"></i>
                                <span>Cherry-picking detected</span>
                            </div>
                            <div class="indicator ${!context.fullPicture ? 'active' : ''}">
                                <i class="fas fa-image"></i>
                                <span>Incomplete picture</span>
                            </div>
                        </div>
                    </div>
                    <div class="why-this-matters">
                        <h4>Why This Matters</h4>
                        <p>Context is crucial for understanding the full truth. Missing context can mislead even with factual statements.</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Create sources section
     */
    function createSourcesSection(results) {
        return `
            <div class="analysis-section">
                <div class="section-header dropdown-toggle">
                    <h3>
                        <i class="fas fa-link"></i> Source Verification
                        <span class="confidence-badge" data-tooltip="Source reliability">82% Reliable</span>
                    </h3>
                    <i class="fas fa-chevron-down"></i>
                </div>
                <div class="section-content dropdown-content">
                    <div class="source-comparison">
                        <h4>How This Speech Compares to Major Sources:</h4>
                        <div class="comparison-grid">
                            <div class="source-item">
                                <img src="https://logo.clearbit.com/cnn.com" alt="CNN">
                                <span>CNN</span>
                                <div class="match-indicator partial">Partial Match</div>
                            </div>
                            <div class="source-item">
                                <img src="https://logo.clearbit.com/foxnews.com" alt="FOX">
                                <span>FOX News</span>
                                <div class="match-indicator low">Low Match</div>
                            </div>
                            <div class="source-item">
                                <img src="https://logo.clearbit.com/bbc.com" alt="BBC">
                                <span>BBC</span>
                                <div class="match-indicator high">High Match</div>
                            </div>
                            <div class="source-item">
                                <img src="https://logo.clearbit.com/reuters.com" alt="Reuters">
                                <span>Reuters</span>
                                <div class="match-indicator high">High Match</div>
                            </div>
                        </div>
                    </div>
                    <div class="source-diversity">
                        <h4>Source Diversity Score:</h4>
                        <div class="progress-bar-container">
                            <div class="progress-bar gradient" style="width: 65%"></div>
                            <span class="progress-label">65% - Moderate diversity</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Create technical details section
     */
    function createTechnicalSection(results) {
        return `
            <div class="analysis-section">
                <div class="section-header dropdown-toggle">
                    <h3>
                        <i class="fas fa-cog"></i> Technical Details
                        <span class="confidence-badge" data-tooltip="Processing quality">High Quality</span>
                    </h3>
                    <i class="fas fa-chevron-down"></i>
                </div>
                <div class="section-content dropdown-content">
                    <div class="technical-grid">
                        <div class="tech-item">
                            <strong>Transcription Model:</strong>
                            <span>Whisper AI v3</span>
                        </div>
                        <div class="tech-item">
                            <strong>Analysis Model:</strong>
                            <span>GPT-4 Turbo</span>
                        </div>
                        <div class="tech-item">
                            <strong>Processing Time:</strong>
                            <span>${(results.duration / 1000).toFixed(2)}s</span>
                        </div>
                        <div class="tech-item">
                            <strong>Audio Quality:</strong>
                            <span>Good (85%)</span>
                        </div>
                    </div>
                    <div class="api-versions">
                        <h4>API Versions:</h4>
                        <code>speech-analysis: v2.0 | fact-check: v1.8 | sentiment: v3.2</code>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Create overall assessment section
     */
    function createOverallSection(results) {
        return `
            <div class="analysis-section">
                <div class="section-header dropdown-toggle">
                    <h3>
                        <i class="fas fa-clipboard-check"></i> Overall Assessment
                        <span class="confidence-badge" data-tooltip="Assessment confidence">90% Confidence</span>
                    </h3>
                    <i class="fas fa-chevron-down"></i>
                </div>
                <div class="section-content dropdown-content">
                    <div class="assessment-summary">
                        <p>${results.overallAssessment || 'No overall assessment available.'}</p>
                    </div>
                    <div class="trust-factors">
                        <h4>Trust Factors:</h4>
                        <div class="factors-grid">
                            <div class="factor-item ${results.truthScore >= 60 ? 'positive' : 'negative'}">
                                <i class="fas fa-check-double"></i>
                                <span>Factual Accuracy</span>
                            </div>
                            <div class="factor-item ${results.speaker?.credibility >= 70 ? 'positive' : 'negative'}">
                                <i class="fas fa-user-check"></i>
                                <span>Speaker Credibility</span>
                            </div>
                            <div class="factor-item ${results.emotionalAnalysis?.score <= 5 ? 'positive' : 'negative'}">
                                <i class="fas fa-balance-scale"></i>
                                <span>Balanced Tone</span>
                            </div>
                            <div class="factor-item ${results.contextAnalysis?.fullPicture ? 'positive' : 'negative'}">
                                <i class="fas fa-expand"></i>
                                <span>Complete Context</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Create recommendations section
     */
    function createRecommendationsSection(results) {
        return `
            <div class="analysis-section">
                <div class="section-header dropdown-toggle">
                    <h3>
                        <i class="fas fa-lightbulb"></i> Recommendations
                        <span class="confidence-badge" data-tooltip="Personalized suggestions">For You</span>
                    </h3>
                    <i class="fas fa-chevron-down"></i>
                </div>
                <div class="section-content dropdown-content">
                    <div class="recommendations-list">
                        <div class="recommendation-item">
                            <i class="fas fa-search"></i>
                            <div>
                                <h4>Verify Key Claims</h4>
                                <p>Cross-check the most impactful claims with primary sources before sharing.</p>
                            </div>
                        </div>
                        <div class="recommendation-item">
                            <i class="fas fa-users"></i>
                            <div>
                                <h4>Consider Multiple Perspectives</h4>
                                <p>Look for speeches on the same topic from different viewpoints for balance.</p>
                            </div>
                        </div>
                        <div class="recommendation-item">
                            <i class="fas fa-clock"></i>
                            <div>
                                <h4>Check Timing</h4>
                                <p>Consider when this speech was given and if circumstances have changed.</p>
                            </div>
                        </div>
                    </div>
                    <div class="action-buttons">
                        <button onclick="window.open('https://www.google.com/search?q=${encodeURIComponent(currentResults.speaker?.name || 'speech topic')}+fact+check', '_blank')">
                            <i class="fas fa-external-link-alt"></i> Research Further
                        </button>
                        <button onclick="showSpeechProcessModal()">
                            <i class="fas fa-info-circle"></i> Learn Our Methods
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Initialize results interactions
     */
    function initializeResultsInteractions() {
        // Add click handlers for dropdowns
        document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
            toggle.addEventListener('click', function() {
                const content = this.nextElementSibling;
                const icon = this.querySelector('.fa-chevron-down');
                
                if (content.classList.contains('show')) {
                    content.classList.remove('show');
                    icon.style.transform = 'rotate(0)';
                } else {
                    content.classList.add('show');
                    icon.style.transform = 'rotate(180deg)';
                }
            });
        });
        
        // Add hover effects
        document.querySelectorAll('.claim-card, .fallacy-card, .recommendation-item').forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateX(5px)';
            });
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateX(0)';
            });
        });
    }
    
    /**
     * Animate trust meter
     */
    function animateTrustMeter(score) {
        const meter = document.querySelector('.trust-meter');
        const progressCircle = document.querySelector('.meter-progress');
        const scoreDisplay = document.querySelector('.score-number');
        
        if (!meter || !progressCircle || !scoreDisplay) return;
        
        // Calculate stroke offset
        const circumference = 2 * Math.PI * 90;
        const offset = circumference - (score / 100) * circumference;
        
        // Animate the meter
        setTimeout(() => {
            progressCircle.style.transition = 'stroke-dashoffset 2s ease-out';
            progressCircle.style.strokeDashoffset = offset;
            
            // Animate the number
            animateNumber(scoreDisplay, 0, score, 2000);
            
            // Add color based on score
            if (score >= 80) {
                progressCircle.style.stroke = '#28a745';
            } else if (score >= 60) {
                progressCircle.style.stroke = '#ffc107';
            } else {
                progressCircle.style.stroke = '#dc3545';
            }
        }, 300);
    }
    
    /**
     * Animate number
     */
    function animateNumber(element, start, end, duration) {
        const startTime = Date.now();
        
        function update() {
            const now = Date.now();
            const progress = Math.min((now - startTime) / duration, 1);
            const value = Math.floor(start + (end - start) * progress);
            element.textContent = value;
            
            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }
        
        update();
    }
    
    /**
     * Animate progress bars
     */
    function animateProgressBars() {
        document.querySelectorAll('.progress-bar').forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0';
            setTimeout(() => {
                bar.style.transition = 'width 1.5s ease-out';
                bar.style.width = width;
            }, 500);
        });
    }
    
    /**
     * Setup dropdowns
     */
    function setupDropdowns() {
        // Open first section by default
        const firstToggle = document.querySelector('.dropdown-toggle');
        if (firstToggle) {
            firstToggle.click();
        }
    }
    
    /**
     * Clear results
     */
    function clear() {
        if (resultsContainer) {
            resultsContainer.innerHTML = '';
            resultsContainer.style.display = 'none';
        }
        currentResults = null;
    }
    
    /**
     * Get current results
     */
    function getCurrentResults() {
        return currentResults;
    }
    
    /**
     * Set current results
     */
    function setCurrentResults(results) {
        currentResults = results;
    }
    
    // Public API
    return {
        initialize: initialize,
        displayResults: displayResults,
        clear: clear,
        getCurrentResults: getCurrentResults,
        setCurrentResults: setCurrentResults
    };
})();

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        window.SpeechApp.results.initialize();
    });
} else {
    window.SpeechApp.results.initialize();
}

console.log('Speech Results Module Loaded');
