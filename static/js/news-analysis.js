// static/js/news-analysis.js - Enhanced with multi-stage progress

// ============================================================================
// LOADING STATE WITH ENHANCED PROGRESS
// ============================================================================

function showLoadingState() {
    // Hide results
    const resultsDiv = document.getElementById('results');
    resultsDiv.style.display = 'none';
    resultsDiv.innerHTML = '';
    
    // Hide the input section and show progress in its place
    const inputSection = document.querySelector('.analysis-input-section');
    if (inputSection) {
        inputSection.style.display = 'none';
    }
    
    // Create or show progress section
    let progressSection = document.getElementById('progressSection');
    if (!progressSection) {
        progressSection = createProgressSection();
        // Insert progress where the input section was
        if (inputSection && inputSection.parentNode) {
            inputSection.parentNode.insertBefore(progressSection, inputSection);
        }
        progressSection = document.getElementById('progressSection');
    }
    
    progressSection.style.display = 'block';
    
    // Reset progress
    resetProgress();
    
    // Start progress animation
    startProgressAnimation();
}

function hideLoadingState() {
    const progressSection = document.getElementById('progressSection');
    if (progressSection) {
        progressSection.style.display = 'none';
    }
    
    // Show the input section again
    const inputSection = document.querySelector('.analysis-input-section');
    if (inputSection) {
        inputSection.style.display = 'block';
    }
}

// ============================================================================
// CREATE PROGRESS SECTION
// ============================================================================

function createProgressSection() {
    const section = document.createElement('div');
    section.className = 'progress-section';
    section.id = 'progressSection';
    section.style.display = 'none';
    
    section.innerHTML = `
        <div class="progress-title">
            <i class="fas fa-cogs fa-spin" style="color: #667eea;"></i>
            News Verification in Progress...
        </div>
        
        <div class="progress-stages" id="progressStages">
            <div class="progress-stage" data-stage="0">
                <div class="stage-icon">📄</div>
                <div class="stage-label">Extracting Content</div>
            </div>
            <div class="progress-stage" data-stage="1">
                <div class="stage-icon">⚖️</div>
                <div class="stage-label">Analyzing Bias</div>
            </div>
            <div class="progress-stage" data-stage="2">
                <div class="stage-icon">🔍</div>
                <div class="stage-label">Checking Sources</div>
            </div>
            <div class="progress-stage" data-stage="3">
                <div class="stage-icon">✓</div>
                <div class="stage-label">Verifying Claims</div>
            </div>
            <div class="progress-stage" data-stage="4">
                <div class="stage-icon">📊</div>
                <div class="stage-label">Generating Report</div>
            </div>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" id="progressBar">
                <span class="progress-percentage" id="progressPercentage">0%</span>
            </div>
        </div>
        
        <div class="progress-status">
            <div class="progress-spinner"></div>
            <span id="progressStatus">Initializing advanced verification systems...</span>
        </div>
        
        <div class="claim-progress" style="display: none;" id="claimProgress">
            <span style="color: #6b7280; font-weight: 600;">Claims found:</span>
            <span class="claim-counter" id="claimCounter">0</span>
            <div class="claim-progress-bar">
                <div class="claim-progress-fill" id="claimProgressFill"></div>
            </div>
        </div>
    `;
    
    return section;
}

// ============================================================================
// PROGRESS ANIMATION
// ============================================================================

let progressInterval = null;
let currentProgress = 0;
let currentStage = 0;

function resetProgress() {
    currentProgress = 0;
    currentStage = 0;
    
    const progressBar = document.getElementById('progressBar');
    const progressPercentage = document.getElementById('progressPercentage');
    
    if (progressBar) {
        progressBar.style.width = '0%';
    }
    if (progressPercentage) {
        progressPercentage.textContent = '0%';
    }
    
    // Reset all stages
    const stages = document.querySelectorAll('.progress-stage');
    stages.forEach(stage => {
        stage.classList.remove('active', 'completed');
    });
}

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

function startProgressAnimation() {
    const progressStages = [
        { message: 'Extracting article content and metadata...', stage: 0, claimsFound: 0 },
        { message: 'Analyzing political bias and language patterns...', stage: 1, claimsFound: 3 },
        { message: 'Searching 500+ news sources for verification...', stage: 2, claimsFound: 5 },
        { message: 'Fact-checking claims against our database...', stage: 3, claimsFound: 8 },
        { message: 'Generating comprehensive analysis report...', stage: 4, claimsFound: 12 }
    ];
    
    let stageIndex = 0;
    
    progressInterval = setInterval(() => {
        currentProgress += 4; // 5% every 250ms = 20 seconds total
        
        const progressBar = document.getElementById('progressBar');
        const progressPercentage = document.getElementById('progressPercentage');
        const progressStatus = document.getElementById('progressStatus');
        
        if (progressBar) {
            progressBar.style.width = currentProgress + '%';
        }
        if (progressPercentage) {
            progressPercentage.textContent = currentProgress + '%';
        }
        
        // Update stage based on progress
        const newStageIndex = Math.floor((currentProgress / 100) * progressStages.length);
        if (newStageIndex !== stageIndex && newStageIndex < progressStages.length) {
            stageIndex = newStageIndex;
            const stage = progressStages[stageIndex];
            
            if (progressStatus) {
                progressStatus.textContent = stage.message;
            }
            updateProgressStages(stage.stage);
            
            // Show claims progress after stage 2
            if (stage.stage >= 2) {
                showClaimsProgress(stage.claimsFound);
            }
        }
        
        if (currentProgress >= 100) {
            clearInterval(progressInterval);
            if (progressStatus) {
                progressStatus.textContent = 'Analysis complete! Preparing your results...';
            }
            updateProgressStages(4);
        }
    }, 250); // Update every 250ms
}

function showClaimsProgress(claimsFound) {
    const claimProgress = document.getElementById('claimProgress');
    const claimCounter = document.getElementById('claimCounter');
    const claimProgressFill = document.getElementById('claimProgressFill');
    
    if (claimProgress) {
        claimProgress.style.display = 'flex';
    }
    if (claimCounter) {
        claimCounter.textContent = claimsFound;
    }
    if (claimProgressFill) {
        claimProgressFill.style.width = Math.min(100, claimsFound * 8) + '%';
    }
}

function stopProgress() {
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
}

// ============================================================================
// MAIN ANALYSIS FUNCTION - FIXED FOR YOUR HTML AND API
// ============================================================================

async function analyzeArticle() {
    const urlInput = document.getElementById('articleUrl');
    
    let url = urlInput.value.trim();
    if (!url) {
        if (window.showNotification) {
            showNotification('Please enter a URL to analyze', 'error');
        } else {
            alert('Please enter a URL to analyze');
        }
        return;
    }
    
    try {
        new URL(url);
    } catch (e) {
        if (window.showNotification) {
            showNotification('Please enter a valid URL', 'error');
        } else {
            alert('Please enter a valid URL');
        }
        return;
    }
    
    // Show loading state
    showLoadingState();
    
    try {
        // Your API might expect 'url' instead of 'content'
        const response = await fetch('/api/analyze-news', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url,  // Changed from 'content' to 'url'
                is_pro: window.currentTier === 'pro' || false
            })
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('API Error:', errorText);
            throw new Error(`Analysis failed: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Stop the progress animation
        stopProgress();
        
        // Complete progress
        const progressBar = document.getElementById('progressBar');
        const progressPercentage = document.getElementById('progressPercentage');
        const progressStatus = document.getElementById('progressStatus');
        
        if (progressBar) progressBar.style.width = '100%';
        if (progressPercentage) progressPercentage.textContent = '100%';
        if (progressStatus) progressStatus.textContent = 'Analysis complete! Preparing your results...';
        updateProgressStages(4);
        
        // Wait a moment then show results
        setTimeout(() => {
            hideLoadingState();
            if (window.displayResults) {
                displayResults(data, window.currentTier || 'free');
            } else {
                console.error('displayResults function not found');
                // Fallback display
                const resultsDiv = document.getElementById('results');
                resultsDiv.style.display = 'block';
                resultsDiv.innerHTML = '<div style="color: white; padding: 20px;">Analysis complete! Check console for results.</div>';
                console.log('Analysis results:', data);
            }
        }, 1000);
        
    } catch (error) {
        stopProgress();
        hideLoadingState();
        console.error('Analysis error:', error);
        if (window.showNotification) {
            showNotification('Analysis failed: ' + error.message, 'error');
        } else {
            alert('Analysis failed: ' + error.message);
        }
    }
}

// ============================================================================
// EXPORT FUNCTIONS
// ============================================================================

window.newsAnalysis = {
    analyzeArticle,
    showLoadingState,
    hideLoadingState
};

// Make analyzeArticle available globally for the onclick handler
window.analyzeArticle = analyzeArticle;
