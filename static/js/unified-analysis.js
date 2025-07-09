// unified-analysis.js - AI Detection and Plagiarism Check
(function() {
    'use strict';
    
    // Initialize namespace
    window.UnifiedApp = window.UnifiedApp || {};
    window.UnifiedApp.analysis = {};
    
    // Analysis stages for progress tracking
    const ANALYSIS_STAGES = [
        { stage: 'Preparing text for analysis...', progress: 15 },
        { stage: 'Analyzing writing patterns...', progress: 30 },
        { stage: 'Detecting AI signatures...', progress: 45 },
        { stage: 'Checking for plagiarism...', progress: 60 },
        { stage: 'Comparing with sources...', progress: 80 },
        { stage: 'Finalizing report...', progress: 100 }
    ];
    
    // Main analysis function
    window.UnifiedApp.analysis.runAnalysis = async function(text, tier = 'pro') {
        try {
            // Show loading overlay
            UnifiedApp.ui.showLoading();
            
            // Validate input
            if (!text || text.trim().length < 50) {
                throw new Error('Please enter at least 50 characters for analysis');
            }
            
            // Prepare analysis data
            const analysisData = {
                content: text.trim(),
                type: 'text',
                is_pro: tier === 'pro',
                analysis_type: 'ai_plagiarism' // New analysis type for backend
            };
            
            // Simulate progress stages
            let stageIndex = 0;
            const progressInterval = setInterval(() => {
                if (stageIndex < ANALYSIS_STAGES.length) {
                    const stage = ANALYSIS_STAGES[stageIndex];
                    UnifiedApp.ui.updateProgress(stage.stage, stage.progress);
                    stageIndex++;
                }
            }, 800);
            
            // Call API
            const response = await window.ffAPI.analyzeUnified(analysisData);
            
            // Clear progress interval
            clearInterval(progressInterval);
            
            // Ensure we're at 100%
            UnifiedApp.ui.updateProgress('Analysis complete!', 100);
            
            // Process response
            if (response.success && response.results) {
                // Add analysis metadata
                response.results.timestamp = new Date().toISOString();
                response.results.textLength = text.length;
                response.results.wordCount = text.trim().split(/\s+/).length;
                
                // Display results
                setTimeout(() => {
                    UnifiedApp.ui.hideLoading();
                    UnifiedApp.results.displayResults(response.results);
                }, 500);
                
                return response.results;
            } else {
                throw new Error(response.error || 'Analysis failed');
            }
            
        } catch (error) {
            console.error('Analysis error:', error);
            UnifiedApp.ui.hideLoading();
            UnifiedApp.ui.showError(error.message || 'An error occurred during analysis');
            return null;
        }
    };
    
    // Export PDF report
    window.UnifiedApp.analysis.generatePDF = async function() {
        try {
            UnifiedApp.ui.showToast('Generating PDF report...');
            
            const results = UnifiedApp.results.getCurrentResults();
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
            const results = UnifiedApp.results.getCurrentResults();
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
        document.getElementById('textInput').value = '';
        document.getElementById('charCount').textContent = '0';
        document.getElementById('resultsSection').style.display = 'none';
        UnifiedApp.results.clearResults();
        UnifiedApp.ui.showToast('Form cleared', 'info');
    };
    
})();
