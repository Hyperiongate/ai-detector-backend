// news-analysis.js - Fixed Analysis Module
// Handles the analysis process and API calls

let currentInputType = 'url';  // Default to URL since that's the first tab
let currentAnalysisData = null;
let isAnalyzing = false;

// Initialize the module
function initializeAnalysis() {
    // Set up event listeners
    setupEventListeners();
    
    // Check for any saved state
    const savedArticle = sessionStorage.getItem('lastArticle');
    if (savedArticle) {
        const textArea = document.getElementById('news-text');
        if (textArea) {
            textArea.value = savedArticle;
        }
    }
}

// Set up all event listeners
function setupEventListeners() {
    // Tab switching is handled by news-main.js
    
    // Test data button
    const testBtn = document.querySelector('.btn-test');
    if (testBtn) {
        testBtn.addEventListener('click', loadTestData);
    }
    
    // Reset button
    const resetBtn = document.querySelector('.reset-button');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetForm);
    }
}

// Switch input type (called from main)
function switchInputType(type) {
    currentInputType = type;
}

// Load test data
function loadTestData() {
    const testContent = `By David Rising
    Associated Press
    
    BANGKOK -- President Donald Trump has threatened to impose sweeping tariffs on Mexico, Canada and China, some of the United States' largest trading partners. The move could spark a global trade war and drive up prices for American consumers.
    
    Trump announced Monday he would impose a 25% tariff on all goods from Mexico and Canada on his first day in office. He also threatened an additional 10% tariff on Chinese imports.
    
    "These tariffs will remain in effect until such time as Drugs, in particular Fentanyl, and all Illegal Aliens stop this Invasion of our Country!" Trump wrote on social media.
    
    Economic experts warn the tariffs could significantly impact the U.S. economy. "Tariffs are paid by importers, not foreign countries, and those costs are typically passed on to consumers," said Mary Johnson, an economist at Georgetown University.
    
    The announcement sent shockwaves through financial markets, with the dollar rising against major currencies and stock futures falling. Mexico and Canada, which are part of the USMCA trade agreement with the United States, expressed concern about the potential impact on their economies.
    
    This represents a return to Trump's first-term trade policies, when he imposed tariffs on various countries that led to retaliatory measures and strained international relationships.`;
    
    document.getElementById('news-text').value = testContent;
    document.getElementById('articleUrl').value = 'https://apnews.com/article/trump-tariffs-mexico-canada-china-trade';
    document.getElementById('fullArticle').value = testContent;
    
    switchInputType('text');
    showNotification('Sample news content loaded. This is more realistic test data with author, specific claims, and sources.', 'success');
}

// Reset form
function resetForm() {
    document.getElementById('news-text').value = '';
    document.getElementById('articleUrl').value = '';
    document.getElementById('fullArticle').value = '';
    document.getElementById('results').style.display = 'none';
    document.getElementById('results').innerHTML = '';
    currentAnalysisData = null;
    isAnalyzing = false;
    
    // Reset button text
    updateAnalyzeButtons(false);
    
    showNotification('Form reset successfully', 'success');
}

// Update analyze button text
function updateAnalyzeButtons(analyzed = true) {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const analyzeBtnPro = document.getElementById('analyzeBtnPro');
    
    if (analyzeBtn) {
        if (analyzed) {
            analyzeBtn.innerHTML = '🔄 Analyze Another';
        } else {
            analyzeBtn.innerHTML = '⚡ Analyze';
        }
    }
    
    if (analyzeBtnPro) {
        if (analyzed) {
            analyzeBtnPro.innerHTML = '🔄 Pro Analysis';
        } else {
            analyzeBtnPro.innerHTML = '👑 Pro Analysis';
        }
    }
}

// Main analysis function
async function runAnalysis(tier = 'free') {
    if (isAnalyzing) {
        showNotification('Analysis already in progress. Please wait.', 'info');
        return;
    }
    
    // Get input based on current tab
    let inputData = {};
    let inputValue = '';
    
    switch (currentInputType) {
        case 'text':
            inputValue = document.getElementById('news-text').value.trim();
            if (!inputValue) {
                showNotification('Please enter news content to analyze.', 'error');
                return;
            }
            if (inputValue.length < 50) {
                showNotification('Please enter at least 50 characters for comprehensive analysis.', 'error');
                return;
            }
            inputData = {
                type: 'text',
                content: inputValue
            };
            break;
            
        case 'url':
            inputValue = document.getElementById('articleUrl').value.trim();
            if (!inputValue) {
                showNotification('Please enter a news URL to analyze.', 'error');
                return;
            }
            try {
                new URL(inputValue);
            } catch (e) {
                showNotification('Please enter a valid URL (e.g., https://example.com/article).', 'error');
                return;
            }
            inputData = {
                type: 'url',
                content: inputValue
            };
            break;
            
        case 'article':
            inputValue = document.getElementById('fullArticle').value.trim();
            if (!inputValue) {
                showNotification('Please paste the full article for analysis.', 'error');
                return;
            }
            if (inputValue.length < 100) {
                showNotification('Please paste a complete article (at least 100 characters).', 'error');
                return;
            }
            inputData = {
                type: 'article',
                content: inputValue
            };
            break;
    }
    
    // Save to session storage
    sessionStorage.setItem('lastArticle', inputValue);
    
    // Start analysis
    isAnalyzing = true;
    showProgressBar();
    
    try {
        // Prepare request data
        const requestData = {
            ...inputData,
            tier: tier,
            is_pro: tier === 'pro',
            extract_content: currentInputType === 'url' // Tell backend to extract from URL
        };
        
        console.log('Sending analysis request:', requestData);
        
        // Make API call
        const response = await fetch('/api/analyze-news', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            throw new Error(errorData.error || `Analysis failed with status ${response.status}`);
        }
        
        const results = await response.json();
        console.log('Analysis results:', results);
        
        // Store results
        currentAnalysisData = results;
        
        // Complete progress
        completeProgress();
        
        // Hide progress and show results
        setTimeout(() => {
            hideProgressBar();
            if (typeof displayNewsResults === 'function') {
                displayNewsResults(results, tier);
            } else {
                console.error('displayNewsResults function not found');
                showNotification('Error displaying results. Please refresh the page.', 'error');
            }
            updateAnalyzeButtons(true);
            
            // Track event
            if (typeof trackNewsEvent !== 'undefined') {
                trackNewsEvent('analysis_completed', {
                    tier: tier,
                    input_type: currentInputType,
                    credibility_score: results.results?.credibility || 0
                });
            }
        }, 1000);
        
    } catch (error) {
        console.error('Analysis error:', error);
        hideProgressBar();
        isAnalyzing = false;
        
        showNotification(`Analysis failed: ${error.message}. Please try again.`, 'error');
        
        // Track error
        if (typeof trackNewsEvent !== 'undefined') {
            trackNewsEvent('analysis_error', {
                tier: tier,
                error: error.message
            });
        }
    }
}

// Progress bar functions
function showProgressBar() {
    const progressSection = document.getElementById('progressSection');
    const progressBar = document.getElementById('progressBar');
    const progressPercentage = document.getElementById('progressPercentage');
    const progressStatus = document.getElementById('progressStatus');
    
    if (!progressSection) return;
    
    progressSection.style.display = 'block';
    progressBar.style.width = '0%';
    progressPercentage.textContent = '0%';
    
    // Animate progress
    const stages = [
        { percent: 20, message: 'Extracting article content...', stage: 0 },
        { percent: 40, message: 'Analyzing political bias indicators...', stage: 1 },
        { percent: 60, message: 'Checking 500+ news sources database...', stage: 2 },
        { percent: 80, message: 'Verifying claims and statements...', stage: 3 },
        { percent: 100, message: 'Generating comprehensive report...', stage: 4 }
    ];
    
    let currentStage = 0;
    const interval = setInterval(() => {
        if (currentStage < stages.length) {
            const stage = stages[currentStage];
            progressBar.style.width = stage.percent + '%';
            progressPercentage.textContent = stage.percent + '%';
            progressStatus.textContent = stage.message;
            updateProgressStages(stage.stage);
            currentStage++;
        } else {
            clearInterval(interval);
        }
    }, 800);
    
    // Store interval ID for cleanup
    progressSection.dataset.intervalId = interval;
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

function completeProgress() {
    const progressBar = document.getElementById('progressBar');
    const progressPercentage = document.getElementById('progressPercentage');
    const progressStatus = document.getElementById('progressStatus');
    
    if (progressBar) progressBar.style.width = '100%';
    if (progressPercentage) progressPercentage.textContent = '100%';
    if (progressStatus) progressStatus.textContent = 'Analysis complete! Preparing your results...';
    updateProgressStages(4);
}

function hideProgressBar() {
    const progressSection = document.getElementById('progressSection');
    if (progressSection) {
        // Clear any running interval
        const intervalId = progressSection.dataset.intervalId;
        if (intervalId) {
            clearInterval(intervalId);
        }
        progressSection.style.display = 'none';
    }
    isAnalyzing = false;
}

// Notification helper
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.display = 'block';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAnalysis);
} else {
    initializeAnalysis();
}

// Export functions for use in other modules
window.runAnalysis = runAnalysis;
window.runNewsAnalysis = runAnalysis;  // Add both names for compatibility
window.resetNewsForm = resetForm;
window.switchNewsInputType = switchInputType;
