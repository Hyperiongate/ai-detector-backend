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

// You'll need to add these functions from your news-analyzer.js:
// - animateTrustMeter
// - updateOverallAssessment  
// - populateRealSections
// - etc.

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
