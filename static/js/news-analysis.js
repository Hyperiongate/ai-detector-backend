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
    updateSummaryTab(results.summary);
    updateBiasTab(results.bias);
    updateSourcesTab(results.sources);
    updateCredibilityTab(results.credibility);
    updateVerificationTab(results.verification);
    updateAuthorTab(results.author);
    updateStyleTab(results.style);
    updateTemporalTab(results.temporal);
    updateProTab();
}

// Load tab content dynamically
function loadTabContent(tabName) {
    const contentDiv = document.getElementById(tabName + '-content');
    
    // Skip if already loaded or is summary (loaded by default)
    if (contentDiv.innerHTML.trim() !== '' || tabName === 'summary') {
        return;
    }
    
    // Load content based on tab
    switch(tabName) {
        case 'bias':
            contentDiv.innerHTML = getBiasContent();
            break;
        case 'sources':
            contentDiv.innerHTML = getSourcesContent();
            break;
        case 'credibility':
            contentDiv.innerHTML = getCredibilityContent();
            break;
        case 'verification':
            contentDiv.innerHTML = getVerificationContent();
            break;
        case 'author':
            contentDiv.innerHTML = getAuthorContent();
            break;
        case 'style':
            contentDiv.innerHTML = getStyleContent();
            break;
        case 'temporal':
            contentDiv.innerHTML = getTemporalContent();
            break;
        case 'pro':
            contentDiv.innerHTML = getProContent();
            break;
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
