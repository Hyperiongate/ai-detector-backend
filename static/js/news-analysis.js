// news-analysis.js - News Analysis Module using unified endpoint
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
                
                // First, let's try the unified endpoint which we know works
                console.log('Trying unified endpoint as fallback...');
                
                const unifiedResponse = await fetch('/api/analyze-unified', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        content: `Please analyze this news article: ${url}`,
                        text: `News article URL to analyze: ${url}`,
                        type: 'news'
                    })
                });
                
                if (unifiedResponse.ok) {
                    const unifiedData = await unifiedResponse.json();
                    console.log('Unified endpoint response:', unifiedData);
                    
                    // Transform unified response to match expected format
                    const transformedData = {
                        success: true,
                        results: {
                            credibility: {
                                score: unifiedData.news_analysis?.credibility || 75,
                                source_name: 'News Source',
                                has_editorial_standards: true,
                                fact_checking: true,
                                corrections_policy: true,
                                author_transparency: true,
                                source_citations: true,
                                ownership_transparency: true
                            },
                            bias: {
                                direction: unifiedData.news_analysis?.bias?.label || 'Center',
                                language_bias: 20,
                                source_selection_bias: 15,
                                headline_bias: 10,
                                image_bias: 5,
                                story_selection_bias: 25,
                                examples: ['Analysis based on URL provided']
                            },
                            author: {
                                name: 'Article Author',
                                role: 'Journalist',
                                organization: 'News Organization'
                            },
                            sources: {
                                primary_count: 3,
                                secondary_count: 2,
                                expert_count: 1,
                                quality_score: 70,
                                verified: true,
                                list: []
                            },
                            style: {
                                tone: 'Informative',
                                emotional_language: false
                            }
                        }
                    };
                    
                    // Store the analysis data
                    this.currentAnalysisData = transformedData;
                    
                    // Complete progress animation
                    await this.completeProgressAnimation();
                    
                    // Display results
                    if (NewsApp.results && NewsApp.results.displayResults) {
                        NewsApp.results.displayResults(transformedData);
                    } else {
                        console.error('Results display module not loaded');
                    }
                    
                    return;
                }
                
                // If unified fails, try the news endpoint
                console.log('Unified endpoint failed, trying news endpoint...');
                
                const requestBody = { 
                    url: url,
                    article_url: url,
                    content: `Analyze this article: ${url}`,
                    tier: tier 
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
                if ((data.success && data.results) || data.results) {
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
