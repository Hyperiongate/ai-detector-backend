// unified-analysis.js - AI Detection and Plagiarism Check with Real-Time Progress
(function() {
    'use strict';
    
    // Initialize namespace
    window.UnifiedApp = window.UnifiedApp || {};
    window.UnifiedApp.analysis = {};
    
    // Store current analysis state
    let currentAnalysis = {
        eventSource: null,
        results: null,
        isAnalyzing: false,
        analysisType: null
    };
    
    // Main analysis function with streaming
    window.UnifiedApp.analysis.runAnalysis = async function(content, tier = 'pro') {
        try {
            // Prevent multiple simultaneous analyses
            if (currentAnalysis.isAnalyzing) {
                UnifiedApp.ui.showToast('Analysis already in progress', 'warning');
                return;
            }
            
            // Determine analysis type and validate
            let analysisData = {
                is_pro: tier === 'pro',
                analysis_type: 'ai_plagiarism'
            };
            
            // Check if it's a URL
            if (content.startsWith('http://') || content.startsWith('https://')) {
                analysisData.url = content;
                analysisData.type = 'url';
                currentAnalysis.analysisType = 'url';
            } else if (content.startsWith('File: ')) {
                // File analysis - extract filename
                analysisData.content = content;
                analysisData.type = 'file';
                currentAnalysis.analysisType = 'file';
            } else {
                // Text analysis
                if (!content || content.trim().length < 50) {
                    throw new Error('Please enter at least 50 characters for analysis');
                }
                analysisData.content = content.trim();
                analysisData.type = 'text';
                currentAnalysis.analysisType = 'text';
            }
            
            // Show loading overlay
            UnifiedApp.ui.showLoading();
            currentAnalysis.isAnalyzing = true;
            
            // Close any existing connection
            if (currentAnalysis.eventSource) {
                currentAnalysis.eventSource.close();
            }
            
            // Create query parameters for SSE
            const queryParams = new URLSearchParams();
            Object.keys(analysisData).forEach(key => {
                queryParams.append(key, analysisData[key]);
            });
            
            console.log('Starting analysis with params:', queryParams.toString());
            
            // Create EventSource for streaming
            const eventSource = new EventSource('/api/analyze-unified/stream?' + queryParams.toString());
            
            currentAnalysis.eventSource = eventSource;
            
            // Handle connection open
            eventSource.onopen = function() {
                console.log('Streaming connection established');
            };
            
            // Handle messages
            eventSource.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    
                    if (data.type === 'progress') {
                        UnifiedApp.ui.updateProgress(data.message || data.stage, data.progress);
                        
                        // Update step indicators
                        if (data.step) {
                            updateStepIndicator(data.step);
                        }
                    } else if (data.type === 'partial') {
                        // Show partial results if available
                        if (data.results) {
                            UnifiedApp.ui.showPartialResults(data.results);
                        }
                    } else if (data.type === 'complete') {
                        // Handle completion
                        handleAnalysisComplete(data.results, content);
                        eventSource.close();
                    } else if (data.type === 'error') {
                        throw new Error(data.message || 'Analysis failed');
                    }
                } catch (error) {
                    console.error('Error processing message:', error);
                }
            };
            
            // Handle errors
            eventSource.onerror = function(event) {
                console.error('SSE error:', event);
                eventSource.close();
                currentAnalysis.eventSource = null;
                currentAnalysis.isAnalyzing = false;
                
                // Check if it's a connection error or server error
                if (eventSource.readyState === EventSource.CLOSED) {
                    // Connection closed, try fallback
                    UnifiedApp.ui.showToast('Streaming failed, using standard method...', 'warning');
                    fallbackAnalysis(analysisData);
                } else {
                    // Other error
                    UnifiedApp.ui.hideLoading();
                    UnifiedApp.ui.showError('Connection error. Please try again.');
                }
            };
            
        } catch (error) {
            console.error('Analysis error:', error);
            UnifiedApp.ui.hideLoading();
            UnifiedApp.ui.showError(error.message || 'An error occurred during analysis');
            currentAnalysis.isAnalyzing = false;
            return null;
        }
    };
    
    // Handle analysis completion
    function handleAnalysisComplete(results, originalContent) {
        if (!results) {
            UnifiedApp.ui.showError('No results received');
            currentAnalysis.isAnalyzing = false;
            return;
        }
        
        // Add analysis metadata
        results.timestamp = new Date().toISOString();
        
        if (currentAnalysis.analysisType === 'text') {
            results.textLength = originalContent.length;
            results.wordCount = originalContent.trim().split(/\s+/).length;
        }
        
        currentAnalysis.results = results;
        
        // Ensure we're at 100%
        UnifiedApp.ui.updateProgress('Analysis complete!', 100);
        
        // Display results
        setTimeout(() => {
            UnifiedApp.ui.hideLoading();
            UnifiedApp.results.displayResults(results);
            currentAnalysis.isAnalyzing = false;
        }, 500);
    }
    
    // Update step indicators during progress
    function updateStepIndicator(step) {
        const steps = ['step-1', 'step-2', 'step-3', 'step-4', 'step-5', 'step-6'];
        const stepIndex = parseInt(step) - 1;
        
        steps.forEach((stepId, index) => {
            const stepElement = document.getElementById(stepId);
            if (stepElement) {
                if (index < stepIndex) {
                    stepElement.classList.add('complete');
                    stepElement.classList.remove('active');
                } else if (index === stepIndex) {
                    stepElement.classList.add('active');
                    stepElement.classList.remove('complete');
                } else {
                    stepElement.classList.remove('active', 'complete');
                }
            }
        });
    }
    
    // Fallback to regular API if streaming fails
    async function fallbackAnalysis(analysisData) {
        try {
            UnifiedApp.ui.showToast('Using standard analysis method...', 'info');
            
            const response = await window.ffAPI.analyzeUnified(analysisData);
            
            if (response.success && response.results) {
                handleAnalysisComplete(response.results, analysisData.content || analysisData.url);
            } else {
                throw new Error(response.error || 'Analysis failed');
            }
        } catch (error) {
            console.error('Fallback analysis error:', error);
            UnifiedApp.ui.hideLoading();
            UnifiedApp.ui.showError(error.message || 'Analysis failed');
            currentAnalysis.isAnalyzing = false;
        }
    }
    
    // Export PDF report
    window.UnifiedApp.analysis.generatePDF = async function() {
        try {
            UnifiedApp.ui.showToast('Generating PDF report...', 'info');
            
            const results = currentAnalysis.results || UnifiedApp.results.getCurrentResults();
            if (!results) {
                throw new Error('No results to export');
            }
            
            const response = await window.ffAPI.generateUnifiedPDF({
                results: results,
                analysis_type: 'ai_plagiarism'
            });
            
            if (response.success && response.pdf_url) {
                // Download PDF
                const a = document.createElement('a');
                a.href = response.pdf_url;
                a.download = `AI_Plagiarism_Report_${new Date().getTime()}.pdf`;
                a.click();
                
                UnifiedApp.ui.showToast('PDF downloaded successfully!', 'success');
            } else {
                throw new Error('Failed to generate PDF');
            }
            
        } catch (error) {
            console.error('PDF generation error:', error);
            UnifiedApp.ui.showToast(error.message || 'Failed to generate PDF', 'error');
        }
    };
    
    // Share results
    window.UnifiedApp.analysis.shareResults = async function() {
        try {
            const results = currentAnalysis.results || UnifiedApp.results.getCurrentResults();
            if (!results) {
                UnifiedApp.ui.showToast('No results to share', 'error');
                return;
            }
            
            // Create shareable URL
            const shareData = {
                title: 'AI & Plagiarism Check Results',
                text: `Content Analysis: ${results.ai_probability}% AI probability, ${results.plagiarism_score}% plagiarism detected`,
                url: window.location.href
            };
            
            if (navigator.share) {
                await navigator.share(shareData);
            } else {
                // Fallback to copy link
                await navigator.clipboard.writeText(window.location.href);
                UnifiedApp.ui.showToast('Link copied to clipboard!', 'success');
            }
            
        } catch (error) {
            console.error('Share error:', error);
            UnifiedApp.ui.showToast('Failed to share results', 'error');
        }
    };
    
    // Cancel ongoing analysis
    window.UnifiedApp.analysis.cancelAnalysis = function() {
        if (currentAnalysis.eventSource) {
            currentAnalysis.eventSource.close();
            currentAnalysis.eventSource = null;
        }
        currentAnalysis.isAnalyzing = false;
        UnifiedApp.ui.hideLoading();
        UnifiedApp.ui.showToast('Analysis cancelled', 'info');
    };
    
    // Reset analysis
    window.UnifiedApp.analysis.reset = function() {
        // Cancel any ongoing analysis
        if (currentAnalysis.isAnalyzing) {
            UnifiedApp.analysis.cancelAnalysis();
        }
        
        // Clear all inputs
        const urlInput = document.getElementById('url-input');
        const textInput = document.getElementById('text-input');
        const fileInput = document.getElementById('file-input');
        
        if (urlInput) urlInput.value = '';
        if (textInput) textInput.value = '';
        if (fileInput) fileInput.value = '';
        
        // Clear file preview
        window.clearFileUpload && window.clearFileUpload();
        
        // Hide results
        const resultsContainer = document.getElementById('results-container');
        if (resultsContainer) {
            resultsContainer.style.display = 'none';
        }
        
        // Show input section
        const inputSection = document.getElementById('input-section');
        if (inputSection) {
            inputSection.style.display = 'block';
        }
        
        // Hide progress
        const progressContainer = document.getElementById('progress-container');
        if (progressContainer) {
            progressContainer.style.display = 'none';
        }
        
        // Clear stored results
        currentAnalysis.results = null;
        currentAnalysis.analysisType = null;
        
        if (UnifiedApp.results && UnifiedApp.results.clearResults) {
            UnifiedApp.results.clearResults();
        }
        
        UnifiedApp.ui.showToast('Analysis reset', 'info');
    };
    
    // Legacy compatibility functions
    window.analyzeUnified = function() {
        const text = document.getElementById('text-input').value;
        UnifiedApp.analysis.runAnalysis(text, 'pro');
    };
    
    window.downloadUnifiedPDF = function() {
        UnifiedApp.analysis.generatePDF();
    };
    
    window.shareUnifiedResults = function() {
        UnifiedApp.analysis.shareResults();
    };
    
    window.resetUnifiedAnalysis = function() {
        UnifiedApp.analysis.reset();
    };
    
    console.log('Unified Analysis module loaded');
})();
