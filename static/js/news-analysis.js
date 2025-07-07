// News Analysis Main Functions

// Reset function
function resetAnalysis() {
    // Clear the URL input
    document.getElementById('articleUrl').value = '';
    
    // Hide results
    document.getElementById('results').style.display = 'none';
    
    // Show analyze button, hide reset button
    document.getElementById('analyzeBtn').style.display = 'inline-block';
    document.getElementById('resetBtn').style.display = 'none';
    
    // Reset to first tab
    switchTab('summary');
}

// Analyze article
function analyzeArticle() { 
    const url = document.getElementById('articleUrl').value;
    if (!url) {
        alert('Please enter a URL to analyze');
        return;
    }
    
    // Hide analyze button, show reset button
    document.getElementById('analyzeBtn').style.display = 'none';
    document.getElementById('resetBtn').style.display = 'inline-block';
    
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
            analysis_type: 'url'  // Always use URL analysis
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

// Switch tabs
function switchTab(tabName) {
    // Remove active class from all tabs and contents
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Add active class to selected tab and content
    const activeButton = Array.from(document.querySelectorAll('.tab-button')).find(
        btn => btn.textContent.toLowerCase().includes(tabName.toLowerCase()) || 
               btn.onclick.toString().includes(tabName)
    );
    if (activeButton) {
        activeButton.classList.add('active');
    }
    
    const activeContent = document.getElementById(tabName + '-content');
    if (activeContent) {
        activeContent.classList.add('active');
    }
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
    
    if (typeof updateCrossSourceTab === 'function' && results.cross_source) {
        updateCrossSourceTab(results.cross_source);
    }
    
    if (typeof updateAuthorTab === 'function' && results.author) {
        updateAuthorTab(results.author);
    }
    
    if (typeof updateWritingStyleTab === 'function' && results.writing_style) {
        updateWritingStyleTab(results.writing_style);
    }
    
    if (typeof updateTemporalTab === 'function' && results.temporal) {
        updateTemporalTab(results.temporal);
    }
    
    if (typeof updateProFeaturesTab === 'function') {
        updateProFeaturesTab();
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
            <button class="analyze-button" onclick="resetAnalysis()">Try Again</button>
        </div>
    `;
    
    // Show reset button on error
    document.getElementById('analyzeBtn').style.display = 'none';
    document.getElementById('resetBtn').style.display = 'inline-block';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Add enter key support
    document.getElementById('articleUrl').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            analyzeArticle();
        }
    });
});
