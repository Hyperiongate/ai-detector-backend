// news-analysis.js - News Analysis Module with Fixed Namespace
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
                
                const response = await fetch('/api/analyze-news', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: url, tier: tier })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                console.log('Analysis results:', data);
                
                if (data.success && data.results) {
                    // Store the analysis data
                    this.currentAnalysisData = data;
                    
                    // Complete progress animation
                    await this.completeProgressAnimation();
                    
                    // Display results
                    if (NewsApp.results && NewsApp.results.displayResults) {
                        NewsApp.results.displayResults(data);
                    } else {
                        console.error('Results display module not loaded');
                    }
                } else {
                    throw new Error(data.error || 'Analysis failed');
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
            } else {
                alert('Analysis failed: ' + message);
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
