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
        isAnalyzing: false
    };
    
    // Main analysis function with streaming
    window.UnifiedApp.analysis.runAnalysis = async function(text, tier = 'pro') {
        try {
            // Prevent multiple simultaneous analyses
            if (currentAnalysis.isAnalyzing) {
                UnifiedApp.ui.showToast('Analysis already in progress', 'warning');
                return;
            }
            
            // Validate input
            if (!text || text.trim().length < 50) {
                throw new Error('Please enter at least 50 characters for analysis');
            }
            
            // Show loading overlay
            UnifiedApp.ui.showLoading();
            currentAnalysis.isAnalyzing = true;
            
            // Close any existing connection
            if (currentAnalysis.eventSource) {
                currentAnalysis.eventSource.close();
            }
            
            // Prepare analysis data
            const analysisData = {
                content: text.trim(),
                type: 'text',
                is_pro: tier === 'pro',
                analysis_type: 'ai_plagiarism'
            };
            
            // Create EventSource for streaming
            const eventSource = new EventSource('/api/analyze-unified/stream?' + new URLSearchParams({
                data: JSON.stringify(analysisData)
            }));
            
            currentAnalysis.eventSource = eventSource;
            
            // Handle progress updates
            eventSource.addEventListener('progress', function(event) {
                const data = JSON.parse(event.data);
                UnifiedApp.ui.updateProgress(data.stage, data.progress);
                
                // Show partial results if available
                if (data.partial_results) {
                    UnifiedApp.ui.showPartialResults(data.partial_results);
                }
            });
            
            // Handle completion
            eventSource.addEventListener('complete', function(event) {
                const data = JSON.parse(event.data);
                
                // Add analysis metadata
                data.results.timestamp = new Date().toISOString();
                data.results.textLength = text.length;
                data.results.wordCount = text.trim().split(/\s+/).length;
                
                currentAnalysis.results = data.results;
                
                // Ensure we're at 100%
                UnifiedApp.ui.updateProgress('Analysis complete!', 100);
                
                // Display results
                setTimeout(() => {
                    UnifiedApp.ui.hideLoading();
                    UnifiedApp.results.displayResults(data.results);
                    currentAnalysis.isAnalyzing = false;
                }, 500);
                
                eventSource.close();
            });
            
            // Handle errors
            eventSource.addEventListener('error', function(event) {
                console.error('SSE error:', event);
                eventSource.close();
                currentAnalysis.isAnalyzing = false;
                
                let errorMessage = 'Connection lost. Trying fallback method...';
                if (event.data) {
                    try {
                        const errorData = JSON.parse(event.data);
                        errorMessage = errorData.error || errorMessage;
                    } catch (e) {
                        // Ignore parse errors
                    }
                }
                
                // Fallback to regular API call
                UnifiedApp.ui.showToast(errorMessage, 'warning');
                fallbackAnalysis(text, tier);
            });
            
            // Connection opened successfully
            eventSource.addEventListener('open', function() {
                console.log('Streaming connection established');
            });
            
        } catch (error) {
            console.error('Analysis error:', error);
            UnifiedApp.ui.hideLoading();
            UnifiedApp.ui.showError(error.message || 'An error occurred during analysis');
            currentAnalysis.isAnalyzing = false;
            return null;
        }
    };
    
    // Fallback to regular API if streaming fails
    async function fallbackAnalysis(text, tier) {
        try {
            UnifiedApp.ui.showToast('Using standard analysis method...', 'info');
            
            const response = await window.ffAPI.analyzeUnified({
                content: text.trim(),
                type: 'text',
                is_pro: tier === 'pro',
                analysis_type: 'ai_plagiarism'
            });
            
            if (response.success && response.results) {
                // Add metadata
                response.results.timestamp = new Date().toISOString();
                response.results.textLength = text.length;
                response.results.wordCount = text.trim().split(/\s+/).length;
                
                currentAnalysis.results = response.results;
                
                UnifiedApp.ui.updateProgress('Analysis complete!', 100);
                
                setTimeout(() => {
                    UnifiedApp.ui.hideLoading();
                    UnifiedApp.results.displayResults(response.results);
                    currentAnalysis.isAnalyzing = false;
                }, 500);
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
    
    // Global functions
    window.analyzeUnified = function() {
        const text = document.getElementById('textInput').value;
        UnifiedApp.analysis.runAnalysis(text, 'pro');
    };
    
    window.downloadUnifiedPDF = function() {
        UnifiedApp.analysis.generatePDF();
    };
    
    window.shareUnifiedResults = function() {
        UnifiedApp.analysis.shareResults();
    };
    
    window.resetUnifiedAnalysis = function() {
        // Cancel any ongoing analysis
        if (currentAnalysis.isAnalyzing) {
            UnifiedApp.analysis.cancelAnalysis();
        }
        
        document.getElementById('textInput').value = '';
        document.getElementById('charCount').textContent = '0';
        document.getElementById('resultsSection').style.display = 'none';
        UnifiedApp.results.clearResults();
        currentAnalysis.results = null;
        UnifiedApp.ui.showToast('Form cleared', 'info');
    };
    
})();
