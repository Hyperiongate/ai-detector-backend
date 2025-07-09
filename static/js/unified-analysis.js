/**
 * Facts & Fakes AI - Unified Analysis Module
 * Handles multi-modal content analysis processing
 */

(function() {
    'use strict';
    
    // Unified Analysis Module
    const UnifiedAnalysis = {
        
        /**
         * Run comprehensive multi-modal analysis
         */
        async runAnalysis(inputData, tier = 'free') {
            console.log('Starting unified analysis...', { inputData, tier });
            
            try {
                // Show loading modal
                this.showLoadingModal();
                
                // Prepare form data
                const formData = await this.prepareFormData(inputData, tier);
                
                // Start progress animation
                this.startProgressAnimation();
                
                // Make API request
                const response = await this.makeAPIRequest(formData);
                
                // Process results
                if (response.success) {
                    console.log('Analysis completed successfully');
                    window.UnifiedApp.state.lastResults = response.results;
                    
                    // Hide loading modal
                    this.hideLoadingModal();
                    
                    // Display results
                    if (window.UnifiedApp.results && window.UnifiedApp.results.displayResults) {
                        window.UnifiedApp.results.displayResults(response.results);
                    }
                    
                } else {
                    throw new Error(response.error || 'Analysis failed');
                }
                
            } catch (error) {
                console.error('Analysis error:', error);
                this.hideLoadingModal();
                this.showErrorModal(error.message);
            }
        },
        
        /**
         * Prepare form data for API request
         */
        async prepareFormData(inputData, tier) {
            const formData = new FormData();
            
            // Add analysis tier
            formData.append('tier', tier);
            formData.append('is_pro', tier === 'pro');
            
            // Determine analysis types needed
            const analysisTypes = [];
            
            if (inputData.textContent && inputData.textContent.trim()) {
                analysisTypes.push('text');
                formData.append('text_content', inputData.textContent.trim());
            }
            
            if (inputData.urlContent && inputData.urlContent.trim()) {
                analysisTypes.push('news');
                formData.append('url_content', inputData.urlContent.trim());
            }
            
            if (inputData.imageFile) {
                analysisTypes.push('image');
                formData.append('image_file', inputData.imageFile);
                formData.append('image_filename', inputData.imageFile.name);
            }
            
            formData.append('analysis_types', JSON.stringify(analysisTypes));
            formData.append('timestamp', Date.now().toString());
            
            console.log('Form data prepared for analysis types:', analysisTypes);
            return formData;
        },
        
        /**
         * Make API request to unified analysis endpoint
         */
        async makeAPIRequest(formData) {
            const response = await fetch(window.UnifiedApp.config.apiEndpoint, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) {
                if (response.status === 403) {
                    throw new Error('Access forbidden. Please check your subscription status.');
                } else if (response.status === 429) {
                    throw new Error('Rate limit exceeded. Please try again later.');
                } else if (response.status >= 500) {
                    throw new Error('Server error. Please try again later.');
                } else {
                    throw new Error(`Request failed with status ${response.status}`);
                }
            }
            
            const data = await response.json();
            console.log('API response received:', data);
            return data;
        },
        
        /**
         * Show loading modal with progress animation
         */
        showLoadingModal() {
            const modal = document.getElementById('unifiedLoadingModal');
            if (modal) {
                modal.style.display = 'flex';
                
                // Reset progress
                const progressFill = document.getElementById('unifiedProgressFill');
                const progressText = document.getElementById('unifiedProgressText');
                
                if (progressFill) progressFill.style.width = '0%';
                if (progressText) progressText.textContent = 'Initializing analysis...';
                
                // Reset stages
                const stages = document.querySelectorAll('.stage');
                stages.forEach(stage => {
                    stage.classList.remove('active', 'completed');
                });
            }
        },
        
        /**
         * Hide loading modal
         */
        hideLoadingModal() {
            const modal = document.getElementById('unifiedLoadingModal');
            if (modal) {
                modal.style.display = 'none';
            }
        },
        
        /**
         * Start progress animation
         */
        startProgressAnimation() {
            let currentStage = 0;
            const stages = window.UnifiedApp.config.progressStages;
            
            const interval = setInterval(() => {
                if (currentStage >= stages.length) {
                    clearInterval(interval);
                    return;
                }
                
                const stage = stages[currentStage];
                
                // Update progress bar
                const progressFill = document.getElementById('unifiedProgressFill');
                const progressText = document.getElementById('unifiedProgressText');
                
                if (progressFill) {
                    progressFill.style.width = stage.progress + '%';
                }
                
                if (progressText) {
                    progressText.textContent = stage.text;
                }
                
                // Update stage indicators
                const stageElement = document.getElementById(stage.id);
                if (stageElement) {
                    // Mark previous stages as completed
                    for (let i = 0; i < currentStage; i++) {
                        const prevStage = document.getElementById(stages[i].id);
                        if (prevStage) {
                            prevStage.classList.remove('active');
                            prevStage.classList.add('completed');
                        }
                    }
                    
                    // Mark current stage as active
                    stageElement.classList.add('active');
                }
                
                currentStage++;
            }, 1000); // Update every second
            
            // Store interval for cleanup
            this.progressInterval = interval;
        },
        
        /**
         * Show error modal
         */
        showErrorModal(message) {
            const modal = document.getElementById('unifiedErrorModal');
            const errorMessage = document.getElementById('unifiedErrorMessage');
            
            if (modal && errorMessage) {
                errorMessage.textContent = message;
                modal.style.display = 'flex';
            }
        },
        
        /**
         * Retry analysis
         */
        async retryAnalysis() {
            if (window.UnifiedApp.ui && window.UnifiedApp.ui.closeErrorModal) {
                window.UnifiedApp.ui.closeErrorModal();
            }
            
            // Retry with current input data
            await this.runAnalysis(
                window.UnifiedApp.state.inputData,
                window.UnifiedApp.state.currentTier
            );
        },
        
        /**
         * Process and validate analysis results
         */
        processResults(results) {
            const processedResults = {
                timestamp: new Date().toISOString(),
                overall: {
                    trustScore: 0,
                    riskLevel: 'low',
                    summary: 'Analysis completed'
                },
                textAnalysis: null,
                newsAnalysis: null,
                imageAnalysis: null,
                combinedInsights: []
            };
            
            // Process text analysis results
            if (results.text_analysis) {
                processedResults.textAnalysis = {
                    aiDetected: results.text_analysis.ai_detected || false,
                    confidence: results.text_analysis.confidence || 0,
                    aiProbability: results.text_analysis.ai_probability || 0,
                    patterns: results.text_analysis.patterns || [],
                    recommendations: results.text_analysis.recommendations || []
                };
            }
            
            // Process news analysis results
            if (results.news_analysis) {
                processedResults.newsAnalysis = {
                    trustScore: results.news_analysis.trust_score || 0,
                    biasScore: results.news_analysis.bias_score || 0,
                    factChecks: results.news_analysis.fact_checks || [],
                    sourceCredibility: results.news_analysis.source_credibility || {},
                    claims: results.news_analysis.claims || []
                };
            }
            
            // Process image analysis results
            if (results.image_analysis) {
                processedResults.imageAnalysis = {
                    trustScore: results.image_analysis.trust_score || 0,
                    aiGenerated: results.image_analysis.ai_generated || false,
                    manipulated: results.image_analysis.manipulated || false,
                    confidence: results.image_analysis.confidence || 0,
                    metadata: results.image_analysis.metadata || {},
                    forensics: results.image_analysis.forensics || {}
                };
            }
            
            // Calculate overall trust score
            const trustScores = [];
            if (processedResults.textAnalysis) {
                trustScores.push(100 - (processedResults.textAnalysis.aiProbability * 100));
            }
            if (processedResults.newsAnalysis) {
                trustScores.push(processedResults.newsAnalysis.trustScore);
            }
            if (processedResults.imageAnalysis) {
                trustScores.push(processedResults.imageAnalysis.trustScore);
            }
            
            if (trustScores.length > 0) {
                processedResults.overall.trustScore = Math.round(
                    trustScores.reduce((a, b) => a + b, 0) / trustScores.length
                );
            }
            
            // Determine risk level
            if (processedResults.overall.trustScore >= 80) {
                processedResults.overall.riskLevel = 'low';
            } else if (processedResults.overall.trustScore >= 60) {
                processedResults.overall.riskLevel = 'medium';
            } else {
                processedResults.overall.riskLevel = 'high';
            }
            
            // Generate combined insights
            processedResults.combinedInsights = this.generateCombinedInsights(processedResults);
            
            return processedResults;
        },
        
        /**
         * Generate combined insights from multi-modal analysis
         */
        generateCombinedInsights(results) {
            const insights = [];
            
            // Cross-reference text and news analysis
            if (results.textAnalysis && results.newsAnalysis) {
                if (results.textAnalysis.aiDetected && results.newsAnalysis.trustScore < 70) {
                    insights.push({
                        type: 'warning',
                        title: 'AI Content in Low-Trust Source',
                        description: 'The text appears to be AI-generated and comes from a source with credibility concerns.'
                    });
                }
            }
            
            // Cross-reference image and news analysis
            if (results.imageAnalysis && results.newsAnalysis) {
                if (results.imageAnalysis.manipulated && results.newsAnalysis.factChecks.some(fc => fc.verdict === 'false')) {
                    insights.push({
                        type: 'alert',
                        title: 'Manipulated Image with False Claims',
                        description: 'The image shows signs of manipulation and the associated claims have been fact-checked as false.'
                    });
                }
            }
            
            // Overall consistency check
            const scores = [results.textAnalysis?.confidence, results.newsAnalysis?.trustScore, results.imageAnalysis?.trustScore]
                .filter(score => score !== null && score !== undefined);
            
            if (scores.length > 1) {
                const variance = this.calculateVariance(scores);
                if (variance > 30) {
                    insights.push({
                        type: 'info',
                        title: 'Inconsistent Content Quality',
                        description: 'Different aspects of the content show varying levels of trustworthiness.'
                    });
                }
            }
            
            return insights;
        },
        
        /**
         * Calculate variance for consistency checking
         */
        calculateVariance(values) {
            const mean = values.reduce((a, b) => a + b, 0) / values.length;
            const squaredDifferences = values.map(value => Math.pow(value - mean, 2));
            return Math.sqrt(squaredDifferences.reduce((a, b) => a + b, 0) / values.length);
        }
    };
    
    // Attach to UnifiedApp namespace when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            if (window.UnifiedApp) {
                window.UnifiedApp.analysis = UnifiedAnalysis;
                console.log('Unified Analysis module loaded');
            }
        });
    } else {
        if (window.UnifiedApp) {
            window.UnifiedApp.analysis = UnifiedAnalysis;
            console.log('Unified Analysis module loaded');
        }
    }
    
})();
