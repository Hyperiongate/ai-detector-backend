// News Analysis Main Functions

// Analyze article
function analyzeArticle() { 
    const url = document.getElementById('articleUrl').value;
    if (!url) {
        alert('Please enter a URL or topic to analyze');
        return;
    }
    
    // Show loading state
    const results = document.getElementById('results');
    results.style.display = 'block';
    
    // Show spinner in first tab
    document.getElementById('summary-content').innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>Analyzing article...</p>
        </div>
    `;
    
    // Make API call to Flask backend
    fetch('/api/analyze-news', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            url: url,
            analysis_type: getSelectedAnalysisType()
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayResults(data.results);
        } else {
            showError(data.error || 'Analysis failed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Network error. Please try again.');
    });
}

// Get selected analysis type
function getSelectedAnalysisType() {
    const activeOption = document.querySelector('.input-option.active');
    if (activeOption.textContent.includes('Article URL')) return 'url';
    if (activeOption.textContent.includes('Topic Search')) return 'topic';
    if (activeOption.textContent.includes('Compare Sources')) return 'comparison';
    return 'url';
}

// Display results
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

// Show error message
function showError(message) {
    document.getElementById('summary-content').innerHTML = `
        <div style="text-align: center; padding: 40px;">
            <div style="color: #dc3545; font-size: 48px; margin-bottom: 20px;">⚠️</div>
            <h3>Analysis Error</h3>
            <p>${message}</p>
            <button class="analyze-button" onclick="location.reload()">Try Again</button>
        </div>
    `;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Add any initialization code here
});
