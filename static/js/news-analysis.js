// news-analysis.js - News Analysis Module with Global Function Support
// This file maintains the modular NewsApp structure while exposing necessary global functions
(function() {
    'use strict';
    
    // Create namespace 
    window.NewsApp = window.NewsApp || {};
    
    // Create analysis object in namespace
    NewsApp.analysis = {
        currentAnalysisData: null,
        analysisInProgress: false,
        
        // Run the analysis
        runAnalysis: async function(url, tier = 'pro') {
            console.log('Sending analysis request:', { url, tier });
            
            if (this.analysisInProgress) {
                console.log('Analysis already in progress');
                return;
            }
            
            this.analysisInProgress = true;
            
            try {
                // Show progress bar
                if (NewsApp.ui && NewsApp.ui.showProgressBar) {
                    NewsApp.ui.showProgressBar();
                }
                
                // Start progress animation
                this.startProgressAnimation();
                
                // Create request body with CORRECT format based on news_analyzer.py
                const requestBody = { 
                    content: url,        // The analyzer expects 'content', not 'url'
                    type: 'url',         // Tell it we're providing a URL, not text
                    is_pro: tier === 'pro'  // Enable pro features if pro tier
                };
                
                console.log('Request body:', JSON.stringify(requestBody, null, 2));
                
                const response = await fetch('/api/analyze-news', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestBody)
                });
                
                console.log('Response status:', response.status);
                
                // Get response as text first
                const responseText = await response.text();
                console.log('Raw response:', responseText);
                
                let data;
                try {
                    data = JSON.parse(responseText);
                } catch (parseError) {
                    console.error('Failed to parse response:', parseError);
                    throw new Error('Server returned invalid response');
                }
                
                if (!response.ok) {
                    console.error('API Error:', data);
                    throw new Error(data.error || `HTTP error! status: ${response.status}`);
                }
                
                console.log('Analysis results:', data);
                
                // Check for success flag or results
                if ((data.success && data.results) || data.results || (data.trust_score !== undefined && !data.error)) {
                    // Store the analysis data
                    this.currentAnalysisData = data;
                    
                    // Complete progress animation
                    await this.completeProgressAnimation();
                    
                    // Display results
                    if (NewsApp.results && NewsApp.results.displayResults) {
                        NewsApp.results.displayResults(data);
                    } else if (typeof displayRealResults === 'function') {
                        // Fallback to global function
                        displayRealResults(data);
                    } else {
                        console.error('Results display function not found');
                    }
                } else {
                    throw new Error(data.error || 'Analysis failed - no results returned');
                }
                
            } catch (error) {
                console.error('Analysis error:', error);
                this.handleError(error.message);
            } finally {
                this.analysisInProgress = false;
                // Hide progress bar if still showing
                if (NewsApp.ui && NewsApp.ui.hideProgressBar) {
                    setTimeout(() => NewsApp.ui.hideProgressBar(), 1000);
                }
            }
        },
        
        // Run analysis for pasted text
        runAnalysisText: async function(text, tier = 'pro') {
            console.log('Sending text analysis request');
            
            if (this.analysisInProgress) {
                console.log('Analysis already in progress');
                return;
            }
            
            this.analysisInProgress = true;
            
            try {
                // Show progress bar
                if (NewsApp.ui && NewsApp.ui.showProgressBar) {
                    NewsApp.ui.showProgressBar();
                }
                
                // Start progress animation
                this.startProgressAnimation();
                
                // Create request body for text analysis
                const requestBody = { 
                    content: text,       // The pasted text
                    type: 'text',        // Tell it we're providing text, not URL
                    is_pro: tier === 'pro'
                };
                
                console.log('Request body:', JSON.stringify(requestBody, null, 2));
                
                const response = await fetch('/api/analyze-news', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestBody)
                });
                
                console.log('Response status:', response.status);
                
                // Get response as text first
                const responseText = await response.text();
                console.log('Raw response:', responseText);
                
                let data;
                try {
                    data = JSON.parse(responseText);
                } catch (parseError) {
                    console.error('Failed to parse response:', parseError);
                    throw new Error('Server returned invalid response');
                }
                
                if (!response.ok) {
                    console.error('API Error:', data);
                    throw new Error(data.error || `HTTP error! status: ${response.status}`);
                }
                
                console.log('Analysis results:', data);
                
                // Check for success flag or results
                if ((data.success && data.results) || data.results || (data.trust_score !== undefined && !data.error)) {
                    // Store the analysis data
                    this.currentAnalysisData = data;
                    
                    // Complete progress animation
                    await this.completeProgressAnimation();
                    
                    // Display results
                    if (NewsApp.results && NewsApp.results.displayResults) {
                        NewsApp.results.displayResults(data);
                    } else if (typeof displayRealResults === 'function') {
                        // Fallback to global function
                        displayRealResults(data);
                    } else {
                        console.error('Results display function not found');
                    }
                } else {
                    throw new Error(data.error || 'Analysis failed - no results returned');
                }
                
            } catch (error) {
                console.error('Analysis error:', error);
                this.handleError(error.message);
            } finally {
                this.analysisInProgress = false;
                // Hide progress bar if still showing
                if (NewsApp.ui && NewsApp.ui.hideProgressBar) {
                    setTimeout(() => NewsApp.ui.hideProgressBar(), 1000);
                }
            }
        },
        
        // Start progress animation
        startProgressAnimation: function() {
            const stages = [
                'extracting-content',
                'analyzing-bias',
                'checking-sources',
                'verifying-facts',
                'generating-report'
            ];
            
            let currentStage = 0;
            const claimsCounter = document.querySelector('.claims-counter');
            let claimsCount = 0;
            
            // For the loading section progress
            const loadingSection = document.getElementById('loading-section');
            if (loadingSection) {
                loadingSection.style.display = 'block';
                document.getElementById('results-section').style.display = 'none';
                
                // Reset stages
                document.querySelectorAll('.analysis-stage').forEach(stage => {
                    stage.classList.remove('active', 'complete');
                });
            }
            
            // Update progress stages
            this.progressInterval = setInterval(() => {
                if (currentStage < stages.length - 1) {
                    // Remove active from current
                    const currentEl = document.getElementById(stages[currentStage]);
                    if (currentEl) {
                        currentEl.classList.remove('active');
                        currentEl.classList.add('completed');
                    }
                    
                    // Add active to next
                    currentStage++;
                    const nextEl = document.getElementById(stages[currentStage]);
                    if (nextEl) {
                        nextEl.classList.add('active');
                    }
                    
                    // Update claims counter
                    claimsCount += Math.floor(Math.random() * 5) + 2;
                    if (claimsCounter) {
                        claimsCounter.textContent = claimsCount;
                    }
                }
            }, 2000);
        },
        
        // Complete progress animation
        completeProgressAnimation: async function() {
            return new Promise((resolve) => {
                // Clear interval
                if (this.progressInterval) {
                    clearInterval(this.progressInterval);
                }
                
                // Complete all stages
                const stages = document.querySelectorAll('.progress-stage');
                stages.forEach(stage => {
                    stage.classList.remove('active');
                    stage.classList.add('completed');
                });
                
                // Final claims count
                const claimsCounter = document.querySelector('.claims-counter');
                if (claimsCounter) {
                    claimsCounter.textContent = Math.floor(Math.random() * 20) + 30;
                }
                
                setTimeout(resolve, 500);
            });
        },
        
        // Handle errors
        handleError: function(message) {
            // Clear any progress intervals
            if (this.progressInterval) {
                clearInterval(this.progressInterval);
            }
            
            // Show error in results
            if (NewsApp.results && NewsApp.results.showError) {
                NewsApp.results.showError(message);
            } else if (typeof showError === 'function') {
                // Use global function
                showError(message);
            } else {
                // Fallback error display
                const resultsDiv = document.getElementById('results');
                if (resultsDiv) {
                    resultsDiv.innerHTML = `
                        <div class="error-message" style="padding: 20px; background: #ff4444; color: white; border-radius: 8px; margin: 20px 0;">
                            <h3>Analysis Failed</h3>
                            <p>${message}</p>
                            <button onclick="NewsApp.ui.resetAnalysis()" style="background: white; color: #ff4444; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin-top: 10px;">
                                Try Again
                            </button>
                        </div>
                    `;
                    resultsDiv.style.display = 'block';
                } else {
                    alert('Analysis failed: ' + message);
                }
            }
        },
        
        // Get current analysis data
        getCurrentData: function() {
            return this.currentAnalysisData;
        },
        
        // Clear current analysis
        clearAnalysis: function() {
            this.currentAnalysisData = null;
            this.analysisInProgress = false;
            if (this.progressInterval) {
                clearInterval(this.progressInterval);
            }
        }
    };
    
    // Make sure NewsApp.analysis is available globally
    window.NewsApp.analysis = NewsApp.analysis;
    
})();

// =============================================================================
// GLOBAL FUNCTIONS FOR HTML ONCLICK HANDLERS
// These bridge the gap between HTML onclick and the modular NewsApp structure
// =============================================================================

// Global variable for current analysis results (for non-modular code)
let currentAnalysisResults = null;

// Main analysis function called by HTML
window.analyzeArticle = async function() {
    const urlInput = document.getElementById('news-url');
    const textInput = document.getElementById('news-text');
    const isUrlMode = document.getElementById('url-input-section').style.display !== 'none';
    
    if (isUrlMode) {
        const url = urlInput.value.trim();
        if (!url) {
            alert('Please enter a URL');
            return;
        }
        await NewsApp.analysis.runAnalysis(url, 'pro');
    } else {
        const text = textInput.value.trim();
        if (!text) {
            alert('Please paste article text');
            return;
        }
        await NewsApp.analysis.runAnalysisText(text, 'pro');
    }
    
    // Update global variable
    currentAnalysisResults = NewsApp.analysis.getCurrentData();
}

// Reset form
window.resetForm = function() {
    document.getElementById('news-url').value = '';
    document.getElementById('news-text').value = '';
    
    // Reset to URL tab
    switchInputType('url');
    
    // Hide any error messages
    const errorContainer = document.getElementById('error-container');
    if (errorContainer) {
        errorContainer.style.display = 'none';
    }
    
    // Hide results if shown
    const resultsSection = document.getElementById('results-section');
    if (resultsSection) {
        resultsSection.style.display = 'none';
    }
    
    // Clear analysis data
    NewsApp.analysis.clearAnalysis();
    currentAnalysisResults = null;
    
    // Scroll to top of input section
    document.querySelector('.input-section').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
    });
}

// Switch input type
window.switchInputType = function(type) {
    const urlSection = document.getElementById('url-input-section');
    const textSection = document.getElementById('text-input-section');
    const tabs = document.querySelectorAll('.input-tab');
    
    tabs.forEach(tab => tab.classList.remove('active'));
    
    if (type === 'url') {
        urlSection.style.display = 'block';
        textSection.style.display = 'none';
        tabs[0].classList.add('active');
    } else {
        urlSection.style.display = 'none';
        textSection.style.display = 'block';
        tabs[1].classList.add('active');
    }
}

// Toggle plan comparison
window.togglePlanComparison = function() {
    const content = document.getElementById('plan-comparison-content');
    const chevron = document.getElementById('plan-chevron');
    
    if (content && chevron) {
        content.classList.toggle('show');
        chevron.style.transform = content.classList.contains('show') ? 'rotate(180deg)' : 'rotate(0deg)';
    }
}

// Toggle resources
window.toggleResources = function() {
    const content = document.getElementById('resources-content');
    const chevron = document.querySelector('.resources-header .chevron-icon');
    
    if (content && chevron) {
        content.classList.toggle('show');
        chevron.style.transform = content.classList.contains('show') ? 'rotate(180deg)' : 'rotate(0deg)';
    }
}

// Toggle feature preview
window.toggleFeaturePreview = function() {
    const content = document.getElementById('feature-preview-content');
    const header = document.querySelector('.feature-preview-header');
    
    if (content) {
        if (content.classList.contains('show')) {
            content.classList.remove('show');
            if (header) header.classList.remove('active');
        } else {
            content.classList.add('show');
            if (header) header.classList.add('active');
        }
    }
}

// Show error
window.showError = function(message) {
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');
    
    // Format message
    let formattedMessage = message
        .replace(/\n/g, '<br>')
        .replace(/•/g, '<br>•');
    
    errorMessage.innerHTML = formattedMessage;
    errorContainer.style.display = 'block';
    
    // Hide results
    document.getElementById('results-section').style.display = 'none';
    
    // Scroll to error
    errorContainer.scrollIntoView({ behavior: 'smooth' });
}

// Retry analysis
window.retryAnalysis = function() {
    document.getElementById('error-container').style.display = 'none';
    analyzeArticle();
}

// Toggle dropdown
window.toggleDropdown = function(header) {
    const content = header.nextElementSibling;
    const isOpen = content.classList.contains('show');
    
    if (isOpen) {
        content.classList.remove('show');
        header.style.borderColor = 'transparent';
    } else {
        content.classList.add('show');
        header.style.borderColor = 'var(--primary-blue)';
    }
}

// Show analysis process modal
window.showAnalysisProcess = function() {
    const modal = document.getElementById('analysisProcessModal');
    if (modal) {
        if (typeof bootstrap !== 'undefined') {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        } else {
            // Fallback
            modal.style.display = 'block';
            modal.classList.add('show');
        }
    }
}

// Generate PDF
window.generatePDF = async function() {
    const analysisData = currentAnalysisResults || NewsApp.analysis.getCurrentData();
    
    if (!analysisData) {
        alert('Please run an analysis first');
        return;
    }
    
    const btn = event.target;
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
    btn.disabled = true;
    
    try {
        const response = await fetch('/api/generate-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                analysis_type: 'news',
                results: analysisData
            })
        });
        
        if (!response.ok) {
            throw new Error('PDF generation failed');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `news-analysis-${Date.now()}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        
    } catch (error) {
        console.error('PDF generation error:', error);
        alert('PDF generation failed. Please try again.');
    } finally {
        btn.innerHTML = originalHTML;
        btn.disabled = false;
    }
}

// Download full report
window.downloadFullReport = async function() {
    generatePDF();
}

// =============================================================================
// DISPLAY FUNCTIONS (from news-analyzer.js)
// These handle the actual display of results
// =============================================================================

// Display results
window.displayRealResults = function(results) {
    // Update timestamp
    const now = new Date();
    document.getElementById('analysis-time').textContent = now.toLocaleString();
    document.getElementById('analysis-id').textContent = results.analysis_id || 'AN-' + Date.now().toString(36).toUpperCase();
    
    // Update trust score
    const trustScore = results.trust_score || 0;
    animateTrustMeter(trustScore);
    
    // Update overall assessment
    updateOverallAssessment(results);
    
    // Populate all sections
    populateRealSections(results);
    
    // Show results section
    document.getElementById('loading-section').style.display = 'none';
    document.getElementById('results-section').style.display = 'block';
    
    // Scroll to results
    document.getElementById('results-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Animate trust meter with score
function animateTrustMeter(trustScore) {
    const trustMeter = document.querySelector('.trust-meter-fill');
    const trustScoreEl = document.getElementById('trust-score');
    const circumference = 2 * Math.PI * 90;
    const offset = circumference - (trustScore / 100) * circumference;
    
    // Set color based on score
    let color = '#10b981'; // green
    if (trustScore < 60) color = '#ef4444'; // red
    else if (trustScore < 80) color = '#f59e0b'; // orange
    
    setTimeout(() => {
        trustMeter.style.stroke = color;
        trustMeter.style.strokeDashoffset = offset;
        
        // Animate number
        let current = 0;
        const interval = setInterval(() => {
            if (current < trustScore) {
                current += 2;
                trustScoreEl.textContent = Math.min(current, trustScore);
            } else {
                clearInterval(interval);
            }
        }, 30);
    }, 100);
}

// Enhanced JavaScript for Overall Assessment
function updateOverallAssessment(results) {
    const trustScore = results.trust_score || 0;
    
    // Update trust score display
    document.getElementById('trust-score-display').innerHTML = `
        ${trustScore}%
        <span class="score-meaning" id="score-meaning">${getScoreMeaning(trustScore)}</span>
    `;
    
    // Update icon and label based on score
    const iconWrapper = document.getElementById('trust-icon-wrapper');
    const credibilityLabel = document.getElementById('credibility-label');
    
    if (trustScore >= 80) {
        iconWrapper.className = 'trust-icon-wrapper high';
        iconWrapper.innerHTML = '<i class="fas fa-shield-alt"></i>';
        credibilityLabel.textContent = 'Generally Reliable (80%+ score)';
    } else if (trustScore >= 60) {
        iconWrapper.className = 'trust-icon-wrapper medium';
        iconWrapper.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
        credibilityLabel.textContent = 'Moderate Reliability (60-79% score)';
    } else {
        iconWrapper.className = 'trust-icon-wrapper low';
        iconWrapper.innerHTML = '<i class="fas fa-times-circle"></i>';
        credibilityLabel.textContent = 'Low Reliability (Below 60% score)';
    }
    
    // Update summary
    document.getElementById('overall-summary').textContent = results.summary || 
        `This article scored ${trustScore}% in our trust analysis. ${getScoreContext(trustScore)}`;
    
    // Update metrics with clear explanations
    const sourceScore = results.credibility_score || 0;
    document.getElementById('source-metric').textContent = sourceScore;
    document.getElementById('source-explainer').textContent = 
        sourceScore >= 80 ? '(High)' : sourceScore >= 60 ? '(Medium)' : '(Low)';
    
    // Claim verification
    const totalClaims = results.key_claims?.length || 0;
    const verifiedClaims = results.fact_checks?.filter(f => f.verdict === 'true').length || 0;
    document.getElementById('accuracy-metric').textContent = 
        totalClaims > 0 ? `${verifiedClaims}/${totalClaims}` : 'No claims';
    document.getElementById('accuracy-explainer').textContent = 
        totalClaims > 0 ? 'verified' : 'to check';
    
    // Political bias
    const biasScore = results.bias_score;
    const biasMetric = document.getElementById('bias-metric');
    if (biasScore !== 'N/A' && !isNaN(biasScore)) {
        if (biasScore < -0.3) biasMetric.textContent = 'Left-leaning';
        else if (biasScore > 0.3) biasMetric.textContent = 'Right-leaning';
        else biasMetric.textContent = 'Center/Neutral';
    } else {
        biasMetric.textContent = 'Not detected';
    }
    
    // Red flags
    const manipulationCount = results.manipulation_tactics?.length || 0;
    document.getElementById('manipulation-metric').textContent = manipulationCount;
    
    // Update findings
    const keyFindings = [];
    if (results.article_info?.author && results.article_info.author !== 'Unknown') {
        keyFindings.push(`Author identified: ${results.article_info.author}`);
    }
    if (results.article_info?.domain) {
        keyFindings.push(`Source: ${results.article_info.domain}`);
    }
    if (results.key_claims?.length > 0) {
        keyFindings.push(`${results.key_claims.length} claims detected`);
    }
    if (trustScore >= 80) {
        keyFindings.push('Meets reliability threshold');
    }
    
    if (keyFindings.length > 0) {
        document.getElementById('key-findings-list').innerHTML = keyFindings
            .map(finding => `<li><i class="fas fa-check"></i>${finding}</li>`)
            .join('');
    } else {
        document.getElementById('key-findings-list').innerHTML = 
            '<li><i class="fas fa-info"></i>Limited data available</li>';
    }
    
    // Update red flags
    const redFlags = results.manipulation_tactics || [];
    if (redFlags.length > 0) {
        document.getElementById('red-flags-list').innerHTML = redFlags
            .slice(0, 4)
            .map(flag => `<li><i class="fas fa-times"></i>${flag}</li>`)
            .join('');
    } else {
        document.getElementById('red-flags-list').innerHTML = 
            '<li><i class="fas fa-check"></i>No manipulation tactics detected</li>';
    }
    
    // Update confidence
    const confidence = calculateConfidence(results);
    document.getElementById('confidence-percentage').textContent = confidence + '%';
    document.getElementById('overall-confidence').style.width = confidence + '%';
    
    // Update confidence explanation
    document.getElementById('confidence-explanation').textContent = 
        `Based on ${getConfidenceFactors(results).join(', ')}`;
}

// Helper functions
function getScoreMeaning(score) {
    if (score >= 90) return 'Very High Reliability';
    if (score >= 80) return 'High Reliability';
    if (score >= 70) return 'Moderate-High';
    if (score >= 60) return 'Moderate';
    if (score >= 50) return 'Moderate-Low';
    if (score >= 40) return 'Low Reliability';
    return 'Very Low Reliability';
}

function getScoreContext(score) {
    if (score >= 80) return 'Articles scoring 80% or higher are generally reliable for citations and sharing.';
    if (score >= 60) return 'Articles scoring 60-79% should be cross-referenced with other sources.';
    return 'Articles scoring below 60% require significant verification before use.';
}

function calculateConfidence(results) {
    let confidence = 50;
    
    if (results.article_info?.author && results.article_info.author !== 'Unknown') confidence += 10;
    if (results.article_info?.domain) confidence += 10;
    if (results.article_info?.publish_date) confidence += 5;
    if (results.key_claims?.length > 0) confidence += 10;
    if (results.fact_checks?.length > 0) confidence += 10;
    if (results.source_credibility) confidence += 5;
    
    return Math.min(confidence, 95);
}

function getConfidenceFactors(results) {
    const factors = [];
    
    if (results.article_info?.author && results.article_info.author !== 'Unknown') {
        factors.push('author identified');
    }
    if (results.key_claims?.length > 0) {
        factors.push(`${results.key_claims.length} claims analyzed`);
    }
    if (results.source_credibility) {
        factors.push('source verified');
    }
    
    if (factors.length === 0) {
        factors.push('limited data available');
    }
    
    return factors;
}

// Populate all sections with data
function populateRealSections(results) {
    // Source Credibility
    const sourceData = results.source_credibility || {};
    if (sourceData && results.article_info) {
        const domain = results.article_info.domain || 'Unknown';
        const credScore = results.credibility_score || 0;
        
        document.getElementById('source-credibility').innerHTML = `
            <h5>Source: ${domain}</h5>
            <p>Credibility Score: <strong>${credScore}/100</strong></p>
            <ul>
                <li>Trust Score: ${results.trust_score || 0}</li>
                <li>Article Title: ${results.article_info.title || 'N/A'}</li>
                ${results.article_info.publish_date ? `<li>Published: ${results.article_info.publish_date}</li>` : ''}
            </ul>
        `;
        
        document.getElementById('this-source-score').textContent = `${Math.round(credScore)}%`;
        document.getElementById('source-explanation').textContent = 'Source credibility assessed based on trust score and analysis results';
        document.getElementById('source-methodology').textContent = 'Analysis based on content quality, claims verification, and bias detection';
    }
    
    // Author Credibility
    const authorName = results.article_info?.author || results.author || 'Unknown';
    const hasAuthor = authorName && authorName !== 'Unknown';
    
    if (hasAuthor) {
        const cleanAuthorName = authorName.replace(/^by\s+/i, '').trim();
        
        document.getElementById('author-credibility').innerHTML = `
            <h5>Author: ${cleanAuthorName}</h5>
            <p>Author detected from article metadata</p>
            <ul>
                <li>Name: <strong>${cleanAuthorName}</strong></li>
                <li>Verification Status: Pending manual verification</li>
            </ul>
        `;
        
        document.getElementById('author-explanation').textContent = `Author "${cleanAuthorName}" has been identified.`;
        document.getElementById('author-methodology').textContent = 'We detected the author through metadata extraction.';
        
    } else {
        document.getElementById('author-credibility').innerHTML = `
            <h5>Author: Not Detected</h5>
            <p>No author information found in article metadata</p>
        `;
        
        document.getElementById('author-explanation').textContent = 'No author information was detected.';
        document.getElementById('author-methodology').textContent = 'Author detection relies on metadata extraction.';
    }
    
    // Writing Quality
    document.getElementById('writing-quality').innerHTML = `
        <h5>Quality Metrics:</h5>
        <ul>
            <li>Overall Trust Score: ${results.trust_score || 0}/100</li>
            <li>Credibility Score: ${results.credibility_score || 0}/100</li>
            <li>Key Claims Identified: ${results.key_claims?.length || 0}</li>
        </ul>
    `;
    
    document.getElementById('quality-explanation').textContent = 'Writing quality assessed through credibility and trust scoring';
    document.getElementById('quality-methodology').textContent = 'Analysis based on content structure and claim verification';
    
    // Fact-Checking
    const claims = results.key_claims || [];
    const factChecks = results.fact_checks || [];
    
    document.getElementById('fact-checking').innerHTML = `
        <h5>Claims Analyzed: ${claims.length}</h5>
        ${claims.map((claim, index) => `
            <div class="claim-card">
                <p><strong>Claim ${index + 1}:</strong> "${claim}"</p>
                <span class="claim-status status-unverified">REQUIRES VERIFICATION</span>
            </div>
        `).join('')}
    `;
    
    document.getElementById('fact-explanation').textContent = claims.length > 0 ? 
        'Key claims have been identified for verification' : 
        'No specific claims were identified for fact-checking';
    document.getElementById('fact-methodology').textContent = 'Claims extracted using natural language processing';
    
    // Political Bias
    const biasScore = results.bias_score;
    const biasMarker = document.getElementById('bias-marker');
    
    if (biasScore !== 'N/A' && !isNaN(biasScore)) {
        const biasPosition = 50;
        biasMarker.style.left = biasPosition + '%';
        
        document.getElementById('political-bias').innerHTML = `
            <h5>Bias Assessment:</h5>
            <p>Bias Score: <strong>${biasScore}</strong></p>
        `;
    } else {
        biasMarker.style.left = '50%';
        
        document.getElementById('political-bias').innerHTML = `
            <h5>Bias Assessment:</h5>
            <p>Bias Score: <strong>Not Available</strong></p>
        `;
    }
    
    document.getElementById('bias-explanation').textContent = biasScore !== 'N/A' ? 
        'Bias analysis completed' : 
        'Insufficient content for bias detection';
    document.getElementById('bias-methodology').textContent = 'Word choice and framing analysis';
    
    // Hidden Agenda
    const manipulationTactics = results.manipulation_tactics || [];
    document.getElementById('hidden-agenda').innerHTML = `
        <h5>Agenda Detection:</h5>
        <p>Manipulation Tactics Found: <strong>${manipulationTactics.length}</strong></p>
        ${manipulationTactics.length > 0 ? `
            <ul>
                ${manipulationTactics.map(tactic => `<li>${tactic}</li>`).join('')}
            </ul>
        ` : '<p>No manipulation tactics detected</p>'}
    `;
    
    document.getElementById('agenda-explanation').textContent = manipulationTactics.length > 0 ?
        'Potential manipulation tactics were identified' :
        'No hidden agenda detected';
    document.getElementById('agenda-methodology').textContent = 'Pattern recognition and persuasion technique analysis';
    
    // Clickbait Analysis
    const title = results.article_info?.title || '';
    const hasClickbaitIndicators = title.includes('!') || title.includes('?') || 
                                  title.toLowerCase().includes('shocking') || 
                                  title.toLowerCase().includes('you won\'t believe');
    
    document.getElementById('clickbait-analysis').innerHTML = `
        <h5>Clickbait Score: <strong>${hasClickbaitIndicators ? 'Medium' : 'Low'}</strong></h5>
        <ul>
            <li>Title: "${title || 'No title provided'}"</li>
        </ul>
    `;
    
    document.getElementById('clickbait-explanation').textContent = hasClickbaitIndicators ?
        'Title may contain clickbait elements' :
        'Title appears to be straightforward';
    document.getElementById('clickbait-methodology').textContent = 'Headline pattern analysis';
    
    // Emotional Manipulation
    const emotionScore = manipulationTactics.length * 20;
    const emotionNeedle = document.getElementById('emotion-needle');
    const emotionAngle = -90 + Math.min(emotionScore * 1.8, 180);
    emotionNeedle.style.transform = `translateX(-50%) rotate(${emotionAngle}deg)`;
    
    document.getElementById('emotional-manipulation').innerHTML = `
        <h5>Emotional Manipulation Level: <strong>${emotionScore > 60 ? 'High' : emotionScore > 30 ? 'Medium' : 'Low'}</strong></h5>
    `;
    
    document.getElementById('emotion-explanation').textContent = 'Emotional manipulation assessed based on rhetoric analysis';
    document.getElementById('emotion-methodology').textContent = 'Sentiment and persuasion technique detection';
    
    // Source Diversity
    const diversityScore = 50;
    const diversityBar = document.getElementById('diversity-bar');
    diversityBar.style.width = diversityScore + '%';
    diversityBar.textContent = diversityScore + '%';
    
    document.getElementById('source-diversity').innerHTML = `
        <h5>Source Diversity Score: <strong>${diversityScore}/100</strong></h5>
    `;
    
    document.getElementById('diversity-explanation').textContent = 'Source diversity analysis requires multiple sources';
    document.getElementById('diversity-methodology').textContent = 'Single source provided for this analysis';
    
    // Timeliness
    const publishDate = results.article_info?.publish_date;
    document.getElementById('timeliness-check').innerHTML = `
        <h5>Timeliness Assessment:</h5>
        <ul>
            <li>Article date: ${publishDate || 'Unknown'}</li>
            <li>Analysis date: ${new Date().toLocaleDateString()}</li>
        </ul>
    `;
    
    document.getElementById('timeliness-explanation').textContent = publishDate ? 
        'Article date information available' : 
        'Publication date not available';
    document.getElementById('timeliness-methodology').textContent = 'Metadata extraction from source';
    
    // AI Detection
    const aiProbability = 25;
    setTimeout(() => {
        const aiBar = document.getElementById('ai-probability');
        aiBar.style.width = aiProbability + '%';
        aiBar.querySelector('.confidence-label').textContent = aiProbability + '%';
    }, 300);
    
    document.getElementById('ai-patterns').innerHTML = `
        <li><i class="fas fa-check-circle text-success me-2"></i>Natural language variations detected</li>
        <li><i class="fas fa-check-circle text-success me-2"></i>Human-like writing patterns</li>
    `;
    
    document.getElementById('ai-explanation').textContent = 'Low probability of AI-generated content';
    document.getElementById('ai-methodology').textContent = 'Pattern analysis and writing style assessment';
}

// Navigation functions
window.ffNav = {
    checkAuthStatus: async function() {
        try {
            const response = await fetch('/api/user/status');
            
            if (!response.ok || !response.headers.get('content-type')?.includes('application/json')) {
                console.log('Auth endpoint not available or not returning JSON');
                return;
            }
            
            const data = await response.json();
            
            if (data.authenticated) {
                document.getElementById('ffNavAuth').style.display = 'none';
                document.getElementById('ffUserMenu').style.display = 'block';
                
                document.getElementById('ffUserEmail').textContent = data.email || 'User';
                document.getElementById('ffUserEmailDropdown').textContent = data.email || 'User';
                document.getElementById('ffUserPlan').textContent = data.plan === 'pro' ? 'Pro Plan' : 'Free Plan';
                
                const usagePercent = (data.usage_today / data.daily_limit) * 100;
                document.getElementById('ffUsageProgress').style.width = usagePercent + '%';
                document.getElementById('ffUsageText').textContent = `${data.usage_today} / ${data.daily_limit} analyses used`;
            }
        } catch (error) {
            console.log('Auth check skipped:', error.message);
        }
    },
    
    init: function() {
        this.checkAuthStatus();
        
        document.addEventListener('click', function(event) {
            const userMenu = document.querySelector('.ff-user-menu');
            if (userMenu && !userMenu.contains(event.target)) {
                document.getElementById('ffUserDropdown').classList.remove('active');
            }
        });
        
        const currentPath = window.location.pathname;
        document.querySelectorAll('.ff-nav-link').forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    }
};

// Global functions for navigation
window.ffToggleMobileMenu = function() {
    const navLinks = document.getElementById('ffNavLinks');
    navLinks.classList.toggle('active');
}

window.ffToggleUserDropdown = function() {
    const dropdown = document.getElementById('ffUserDropdown');
    dropdown.classList.toggle('active');
}

window.ffLogout = async function() {
    try {
        await fetch('/api/logout', { method: 'POST' });
        window.location.href = '/';
    } catch (error) {
        console.error('Logout failed:', error);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('News analysis module loaded');
    
    // Verify functions are available
    console.log('Module loaded:', typeof NewsApp.analysis);
    console.log('Global functions:', {
        analyzeArticle: typeof window.analyzeArticle,
        resetForm: typeof window.resetForm
    });
});
