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
    
    // Show animated loading in first tab
    showLoadingAnimation();
    
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

// Animated loading state
function showLoadingAnimation() {
    const container = document.getElementById('summary-content');
    let progress = 0;
    const loadingStages = [
        { progress: 10, status: "Initializing Neural Network...", substatus: "Loading AI models" },
        { progress: 25, status: "Fetching Article Content...", substatus: "Extracting text and metadata" },
        { progress: 40, status: "Analyzing Political Bias...", substatus: "Scanning for partisan language" },
        { progress: 55, status: "Verifying Credibility...", substatus: "Checking source reliability" },
        { progress: 70, status: "Cross-Referencing Sources...", substatus: "Comparing with database" },
        { progress: 85, status: "Generating Insights...", substatus: "Compiling final analysis" },
        { progress: 95, status: "Finalizing Report...", substatus: "Almost there!" }
    ];
    
    container.innerHTML = `
        <div class="loading-container">
            <div class="ai-brain">
                <div class="brain-core"></div>
                <div class="brain-ring"></div>
                <div class="brain-ring"></div>
                <div class="brain-ring"></div>
            </div>
            
            <div class="loading-status" id="loading-status">Initializing Neural Network...</div>
            <div class="loading-substatus" id="loading-substatus">Loading AI models</div>
            
            <div class="progress-bar-container">
                <div class="progress-bar" id="progress-bar" style="width: 0%"></div>
            </div>
            
            <div style="color: rgba(255,255,255,0.6); margin-top: 20px;">
                <small>🧠 Processing with advanced AI algorithms...</small>
            </div>
        </div>
    `;
    
    // Animate progress bar
    let stageIndex = 0;
    const progressInterval = setInterval(() => {
        if (stageIndex < loadingStages.length) {
            const stage = loadingStages[stageIndex];
            updateProgress(stage.progress, stage.status, stage.substatus);
            stageIndex++;
        } else {
            clearInterval(progressInterval);
        }
    }, 2000); // Update every 2 seconds
}

function updateProgress(percent, status, substatus) {
    const progressBar = document.getElementById('progress-bar');
    const statusText = document.getElementById('loading-status');
    const substatusText = document.getElementById('loading-substatus');
    
    if (progressBar) progressBar.style.width = percent + '%';
    if (statusText) statusText.textContent = status;
    if (substatusText) substatusText.textContent = substatus;
}

// Switch tabs
function switchTab(tabName) {
    // Remove active class from all tabs and contents
    document.querySelectorAll('.tab').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Add active class to selected tab and content
    const activeButton = Array.from(document.querySelectorAll('.tab')).find(
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
            <div style="color: #ff0066; font-size: 48px; margin-bottom: 20px;">⚠️</div>
            <h3 style="color: #ff0066;">Analysis Error</h3>
            <p style="color: rgba(255,255,255,0.8);">${message}</p>
            <button class="analyze-button" onclick="resetAnalysis()" style="margin-top: 20px;">Try Again</button>
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
    
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.analyze-button, .reset-button');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
});
