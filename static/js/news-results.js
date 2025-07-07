function displayResults(results) {
    // Update each tab with results
    
    // Make sure all the update functions exist before calling them
    if (typeof updateSummaryTab === 'function' && results.summary) {
        updateSummaryTab(results.summary);
    }
    
    if (typeof updateBiasTab === 'function' && results.bias) {
        updateBiasTab(results.bias);
    }
    
    if (typeof updateSourcesTab === 'function' && results.sources) {
        updateSourcesTab(results.sources);
    }
    
    if (typeof updateCredibilityTab === 'function' && results.credibility) {
        updateCredibilityTab(results.credibility);
    }
    
    if (typeof updateVerificationTab === 'function' && results.verification) {
        updateVerificationTab(results.verification);
    }
    
    if (typeof updateAuthorTab === 'function' && results.author) {
        updateAuthorTab(results.author);
    }
    
    if (typeof updateStyleTab === 'function' && results.style) {
        updateStyleTab(results.style);
    }
    
    if (typeof updateTemporalTab === 'function' && results.temporal) {
        updateTemporalTab(results.temporal);
    }
    
    if (typeof updateProTab === 'function') {
        updateProTab();
    }
    
    // Show the results container
    const resultsContainer = document.getElementById('results');
    if (resultsContainer) {
        resultsContainer.style.display = 'block';
    }
}
