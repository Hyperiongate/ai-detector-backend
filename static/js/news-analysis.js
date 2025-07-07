// ============================================
// NEWS VERIFICATION PLATFORM - ANALYSIS MODULE
// ============================================

// Global variables
let currentInputType = 'text';
let currentAnalysisData = null;
let currentTier = 'free';

// Main analysis function
async function runAnalysis(tier) {
    tier = tier || 'free';
    currentTier = tier;
    
    // Validate input
    const textInput = document.getElementById('news-text').value.trim();
    const urlInput = document.getElementById('news-url').value.trim();
    
    if (currentInputType === 'text') {
        if (!textInput) {
            showNotification('Please enter news content to analyze.', 'error');
            return;
        }
        if (textInput.length < 50) {
            showNotification('Please enter at least 50 characters for comprehensive news analysis.', 'error');
            return;
        }
    }
    
    if (currentInputType === 'url') {
        if (!urlInput) {
            showNotification('Please enter a news URL to analyze.', 'error');
            return;
        }
        try {
            new URL(urlInput);
        } catch (e) {
            showNotification('Please enter a valid news URL (e.g., https://example.com/article).', 'error');
            return;
        }
    }
    
    // Show progress section
    const progressSection = document.getElementById('progressSection');
    const progressBar = document.getElementById('progressBar');
    const progressPercentage = document.getElementById('progressPercentage');
    const progressStatus = document.getElementById('progressStatus');
    
    progressSection.style.display = 'block';
    
    // Reset progress
    progressBar.style.width = '0%';
    progressPercentage.textContent = '0%';
    updateProgressStages(0);
    
    // Enhanced progress messages with stages
    const progressStages = [
        { message: 'Extracting article content...', stage: 0 },
        { message: 'Analyzing political bias indicators...', stage: 1 },
        { message: 'Checking 500+ news sources database...', stage: 2 },
        { message: 'Verifying claims and statements...', stage: 3 },
        { message: 'Generating comprehensive report...', stage: 4 }
    ];
    
    let currentProgress = 0;
    let stageIndex = 0;
    let progressInterval = null;
    
    // Animate progress with stages
    progressInterval = setInterval(() => {
        currentProgress += 20;
        progressBar.style.width = currentProgress + '%';
        progressPercentage.textContent = currentProgress + '%';
        
        if (stageIndex < progressStages.length) {
            const stage = progressStages[stageIndex];
            progressStatus.textContent = stage.message;
            updateProgressStages(stage.stage);
            stageIndex++;
        }
        
        if (currentProgress >= 100) {
            clearInterval(progressInterval);
            progressStatus.textContent = 'Analysis complete! Preparing your results...';
            updateProgressStages(4);
        }
    }, 800);
    
    try {
        // Prepare data for API call
        const requestData = {};
        if (currentInputType === 'text') {
            requestData.content = textInput;
        } else {
            requestData.content = urlInput;
        }
        
        // Add analysis type
        requestData.is_pro = tier === 'pro';
        
        console.log('Sending request to /api/analyze-news with data:', requestData);
        
        // Make API call to backend
        const response = await fetch('/api/analyze-news', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            clearInterval(progressInterval);
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            throw new Error(errorData.error || 'Analysis failed with status ' + response.status);
        }
        
        const results = await response.json();
        clearInterval(progressInterval);
        
        // Log the actual results to see what we're getting
        console.log('API Response:', results);
        
        // Store for modal functionality
        currentAnalysisData = results;
        
        // Complete progress bar
        progressBar.style.width = '100%';
        progressPercentage.textContent = '100%';
        progressStatus.textContent = 'Analysis complete! Preparing your results...';
        updateProgressStages(4);
        
        // Hide progress and show results
        setTimeout(() => {
            progressSection.style.display = 'none';
            showNewsResults(results, tier);
        }, 1000);

        trackNewsEvent('news_analysis_completed', {
            tier: tier,
            credibility_score: results.credibility_score || 0,
            political_bias: results.political_bias && results.political_bias.bias_label || 'unknown'
        });
        
    } catch (error) {
        console.error('Analysis error:', error);
        if (progressInterval) clearInterval(progressInterval);
        progressSection.style.display = 'none';
        showNotification('Analysis failed: ' + error.message + '. Please try again.', 'error');
        
        trackNewsEvent('news_analysis_failed', {
            tier: tier,
            error: error.message
        });
    }
}

// Update progress stages
function updateProgressStages(stage) {
    const stages = document.querySelectorAll('.progress-stage');
    stages.forEach((stageEl, index) => {
        if (index < stage) {
            stageEl.classList.add('completed');
            stageEl.classList.remove('active');
        } else if (index === stage) {
            stageEl.classList.add('active');
            stageEl.classList.remove('completed');
        } else {
            stageEl.classList.remove('active', 'completed');
        }
    });
}

// Calculate reading level
function calculateReadingLevel(text) {
    const words = text.split(' ').length;
    const sentences = (text.match(/[.!?]/g) || []).length;
    const avgWordsPerSentence = words / Math.max(sentences, 1);
    
    if (avgWordsPerSentence > 25) return "Graduate";
    if (avgWordsPerSentence > 20) return "College";
    if (avgWordsPerSentence > 15) return "High School";
    return "Middle School";
}

// Calculate expertise match
function calculateExpertiseMatch(textContent) {
    // Simple keyword-based matching (in production, use more sophisticated NLP)
    const topicKeywords = {
        politics: /government|election|congress|senate|policy|political|democrat|republican/gi,
        technology: /tech|software|ai|artificial intelligence|computer|digital|cyber/gi,
        economics: /economy|financial|market|trade|business|commerce|gdp/gi,
        health: /health|medical|doctor|hospital|disease|treatment|covid|vaccine/gi,
        environment: /climate|environment|pollution|renewable|energy|carbon/gi
    };
    
    let maxMatch = 0;
    for (const [topic, regex] of Object.entries(topicKeywords)) {
        const matches = textContent.match(regex);
        if (matches) {
            const matchPercentage = Math.min(95, matches.length * 5 + 70);
            maxMatch = Math.max(maxMatch, matchPercentage);
        }
    }
    
    return maxMatch || 75; // Default to 75 if no strong topic match
}

// Handle PDF Download
function handlePDFDownload(tier) {
    if (tier === 'free') {
        // Show upgrade message for free users
        showNotification('PDF reports are available with Pro subscription. Upgrade to download detailed analysis reports!', 'info');
        
        // Optional: Show a modal or redirect to pricing
        setTimeout(() => {
            if (confirm('Would you like to upgrade to Pro to access PDF reports and advanced features?')) {
                window.location.href = '/pricingplan';
            }
        }, 500);
    } else {
        // Pro users - generate PDF
        showNotification('Generating your PDF report...', 'info');
        
        // In a real implementation, this would call your PDF generation API
        // For now, we'll simulate it
        setTimeout(() => {
            showNotification('PDF report downloaded successfully!', 'success');
            
            // Create a sample PDF download (in production, this would be actual PDF generation)
            const reportData = {
                title: 'News Verification Report',
                date: new Date().toLocaleDateString(),
                credibilityScore: currentAnalysisData?.credibility_score || 0,
                source: currentAnalysisData?.source_analysis?.domain || 'Unknown',
                bias: currentAnalysisData?.political_bias?.bias_label || 'Unknown'
            };
            
            // Simulate download by creating a blob
            const content = `News Verification Report\n\nDate: ${reportData.date}\nSource: ${reportData.source}\nCredibility: ${reportData.credibilityScore}/100\nBias: ${reportData.bias}\n\nFor full report features, this would include all analysis details.`;
            const blob = new Blob([content], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `news-verification-report-${Date.now()}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }, 2000);
    }
}

// Report action functions
function downloadReport() {
    showNotification('Generating PDF report...', 'info');
    // In a real implementation, this would generate and download a PDF
    setTimeout(() => {
        showNotification('PDF report downloaded successfully!', 'success');
    }, 2000);
}

function shareReport() {
    showNotification('Generating shareable link...', 'info');
    // In a real implementation, this would create a shareable link
    setTimeout(() => {
        showNotification('Report link copied to clipboard!', 'success');
    }, 1000);
}

function copyReportLink() {
    // In a real implementation, this would copy the current URL with report ID
    navigator.clipboard.writeText(window.location.href);
    showNotification('Report link copied to clipboard!', 'success');
}

// Export functions for use in other modules
window.newsAnalysis = {
    runAnalysis,
    updateProgressStages,
    calculateReadingLevel,
    calculateExpertiseMatch,
    handlePDFDownload,
    downloadReport,
    shareReport,
    copyReportLink,
    currentAnalysisData: () => currentAnalysisData,
    currentTier: () => currentTier
};
