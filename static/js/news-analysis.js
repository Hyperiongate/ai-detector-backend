// news-analysis.js - SIMPLIFIED VERSION - NO CONTAINERS
console.log('news-analysis.js loading...');

// Global variable for current analysis results
let currentAnalysisData = null;
let analysisInProgress = false;
let progressInterval = null;

// =============================================================================
// ANALYSIS FUNCTIONS
// =============================================================================

async function runAnalysis(url, tier = 'pro') {
    console.log('Running analysis for URL:', url);
    
    if (analysisInProgress) {
        console.log('Analysis already in progress');
        return;
    }
    
    analysisInProgress = true;
    
    try {
        startProgressAnimation();
        
        const response = await fetch('/api/analyze-news', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: url,
                type: 'url',
                is_pro: tier === 'pro'
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Analysis failed');
        }
        
        currentAnalysisData = data;
        await completeProgressAnimation();
        displayRealResults(data);
        
    } catch (error) {
        console.error('Analysis error:', error);
        handleError(error.message);
    } finally {
        analysisInProgress = false;
    }
}

async function runAnalysisText(text, tier = 'pro') {
    console.log('Running analysis for text');
    
    if (analysisInProgress) {
        console.log('Analysis already in progress');
        return;
    }
    
    analysisInProgress = true;
    
    try {
        startProgressAnimation();
        
        const response = await fetch('/api/analyze-news', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: text,
                type: 'text',
                is_pro: tier === 'pro'
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Analysis failed');
        }
        
        currentAnalysisData = data;
        await completeProgressAnimation();
        displayRealResults(data);
        
    } catch (error) {
        console.error('Analysis error:', error);
        handleError(error.message);
    } finally {
        analysisInProgress = false;
    }
}

function startProgressAnimation() {
    const loadingSection = document.getElementById('loading-section');
    const resultsSection = document.getElementById('results-section');
    
    if (loadingSection) {
        loadingSection.style.display = 'block';
    }
    if (resultsSection) {
        resultsSection.style.display = 'none';
    }
    
    // Reset all stages
    document.querySelectorAll('.analysis-stage').forEach(stage => {
        stage.classList.remove('active', 'complete');
    });
    
    // Animate stages
    let currentStage = 0;
    const stages = ['stage-1', 'stage-2', 'stage-3', 'stage-4', 'stage-5', 'stage-6'];
    
    progressInterval = setInterval(() => {
        if (currentStage < stages.length) {
            if (currentStage > 0) {
                const prevStage = document.getElementById(stages[currentStage - 1]);
                if (prevStage) {
                    prevStage.classList.remove('active');
                    prevStage.classList.add('complete');
                }
            }
            
            const currentStageEl = document.getElementById(stages[currentStage]);
            if (currentStageEl) {
                currentStageEl.classList.add('active');
            }
            
            currentStage++;
        }
    }, 1000);
}

async function completeProgressAnimation() {
    return new Promise((resolve) => {
        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }
        
        document.querySelectorAll('.analysis-stage').forEach(stage => {
            stage.classList.remove('active');
            stage.classList.add('complete');
        });
        
        setTimeout(resolve, 500);
    });
}

function handleError(message) {
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
    
    const loadingSection = document.getElementById('loading-section');
    if (loadingSection) {
        loadingSection.style.display = 'none';
    }
    
    showError(message);
}

function clearAnalysis() {
    currentAnalysisData = null;
    analysisInProgress = false;
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
}

// =============================================================================
// UI FUNCTIONS - THESE ARE CALLED BY ONCLICK
// =============================================================================

function analyzeArticle() {
    console.log('analyzeArticle called');
    const urlInput = document.getElementById('news-url');
    const textInput = document.getElementById('news-text');
    const isUrlMode = document.getElementById('url-input-section').style.display !== 'none';
    
    if (isUrlMode) {
        const url = urlInput.value.trim();
        if (!url) {
            alert('Please enter a URL');
            return;
        }
        runAnalysis(url, 'pro');
    } else {
        const text = textInput.value.trim();
        if (!text) {
            alert('Please paste article text');
            return;
        }
        runAnalysisText(text, 'pro');
    }
}

function resetForm() {
    console.log('resetForm called');
    document.getElementById('news-url').value = '';
    document.getElementById('news-text').value = '';
    
    switchInputType('url');
    
    const errorContainer = document.getElementById('error-container');
    if (errorContainer) {
        errorContainer.style.display = 'none';
    }
    
    const resultsSection = document.getElementById('results-section');
    if (resultsSection) {
        resultsSection.style.display = 'none';
    }
    
    clearAnalysis();
    
    document.querySelector('.input-section').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
    });
}

function switchInputType(type) {
    console.log('switchInputType called:', type);
    const urlSection = document.getElementById('url-input-section');
    const textSection = document.getElementById('text-input-section');
    const tabs = document.querySelectorAll('.input-tab');
    
    tabs.forEach(tab => tab.classList.remove('active'));
    
    if (type === 'url') {
        urlSection.style.display = 'block';
        textSection.style.display = 'none';
        tabs[0].classList.add('active');
    } else {
        urlSection.style.display = 'none';
        textSection.style.display = 'block';
        tabs[1].classList.add('active');
    }
}

function togglePlanComparison() {
    console.log('togglePlanComparison called');
    const content = document.getElementById('plan-comparison-content');
    const chevron = document.getElementById('plan-chevron');
    
    if (content && chevron) {
        content.classList.toggle('show');
        chevron.style.transform = content.classList.contains('show') ? 'rotate(180deg)' : 'rotate(0deg)';
    }
}

function toggleResources() {
    console.log('toggleResources called');
    const content = document.getElementById('resources-content');
    const chevron = document.querySelector('.resources-header .chevron-icon');
    
    if (content && chevron) {
        content.classList.toggle('show');
        chevron.style.transform = content.classList.contains('show') ? 'rotate(180deg)' : 'rotate(0deg)';
    }
}

function toggleFeaturePreview() {
    console.log('toggleFeaturePreview called');
    const content = document.getElementById('feature-preview-content');
    const header = document.querySelector('.feature-preview-header');
    
    if (content) {
        if (content.classList.contains('show')) {
            content.classList.remove('show');
            if (header) header.classList.remove('active');
        } else {
            content.classList.add('show');
            if (header) header.classList.add('active');
        }
    }
}

function showError(message) {
    console.log('showError called:', message);
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');
    
    if (errorMessage) {
        errorMessage.innerHTML = message.replace(/\n/g, '<br>').replace(/•/g, '<br>•');
    }
    
    if (errorContainer) {
        errorContainer.style.display = 'block';
        errorContainer.scrollIntoView({ behavior: 'smooth' });
    }
    
    const resultsSection = document.getElementById('results-section');
    if (resultsSection) {
        resultsSection.style.display = 'none';
    }
}

function retryAnalysis() {
    console.log('retryAnalysis called');
    const errorContainer = document.getElementById('error-container');
    if (errorContainer) {
        errorContainer.style.display = 'none';
    }
    analyzeArticle();
}

function toggleDropdown(header) {
    console.log('toggleDropdown called');
    const content = header.nextElementSibling;
    const isOpen = content.classList.contains('show');
    
    if (isOpen) {
        content.classList.remove('show');
        header.style.borderColor = 'transparent';
    } else {
        content.classList.add('show');
        header.style.borderColor = 'var(--primary-blue)';
    }
}

function showAnalysisProcess() {
    console.log('showAnalysisProcess called');
    const modal = document.getElementById('analysisProcessModal');
    if (modal) {
        if (typeof bootstrap !== 'undefined') {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        } else {
            modal.style.display = 'block';
            modal.classList.add('show');
        }
    }
}

async function generatePDF() {
    console.log('generatePDF called');
    
    if (!currentAnalysisData) {
        alert('Please run an analysis first');
        return;
    }
    
    const btn = event.target;
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
    btn.disabled = true;
    
    try {
        const response = await fetch('/api/generate-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                analysis_type: 'news',
                results: currentAnalysisData
            })
        });
        
        if (!response.ok) {
            throw new Error('PDF generation failed');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `news-analysis-${Date.now()}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        
    } catch (error) {
        console.error('PDF generation error:', error);
        alert('PDF generation failed. Please try again.');
    } finally {
        btn.innerHTML = originalHTML;
        btn.disabled = false;
    }
}

function downloadFullReport() {
    console.log('downloadFullReport called');
    generatePDF();
}

function displayRealResults(results) {
    console.log('displayRealResults called', results);
    
    // Hide loading, show results
    document.getElementById('loading-section').style.display = 'none';
    document.getElementById('results-section').style.display = 'block';
    
    // Update basic info
    const now = new Date();
    document.getElementById('analysis-time').textContent = now.toLocaleString();
    document.getElementById('analysis-id').textContent = results.analysis_id || 'AN-' + Date.now().toString(36).toUpperCase();
    
    // Update trust score
    const trustScore = results.trust_score || 0;
    const trustScoreEl = document.getElementById('trust-score');
    if (trustScoreEl) {
        trustScoreEl.textContent = trustScore;
    }
    
    // Update summary
    const summaryEl = document.getElementById('overall-summary');
    if (summaryEl) {
        summaryEl.textContent = results.summary || `This article scored ${trustScore}% in our trust analysis.`;
    }
    
    // Scroll to results
    document.getElementById('results-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Navigation functions
function ffToggleMobileMenu() {
    const navLinks = document.getElementById('ffNavLinks');
    navLinks.classList.toggle('active');
}

function ffToggleUserDropdown() {
    const dropdown = document.getElementById('ffUserDropdown');
    dropdown.classList.toggle('active');
}

async function ffLogout() {
    try {
        await fetch('/api/logout', { method: 'POST' });
        window.location.href = '/';
    } catch (error) {
        console.error('Logout failed:', error);
    }
}

// Initialize navigation when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded');
    
    // Check auth status
    fetch('/api/user/status')
        .then(response => response.json())
        .then(data => {
            if (data.authenticated) {
                document.getElementById('ffNavAuth').style.display = 'none';
                document.getElementById('ffUserMenu').style.display = 'block';
                
                document.getElementById('ffUserEmail').textContent = data.email || 'User';
                document.getElementById('ffUserEmailDropdown').textContent = data.email || 'User';
                document.getElementById('ffUserPlan').textContent = data.plan === 'pro' ? 'Pro Plan' : 'Free Plan';
                
                const usagePercent = (data.usage_today / data.daily_limit) * 100;
                document.getElementById('ffUsageProgress').style.width = usagePercent + '%';
                document.getElementById('ffUsageText').textContent = `${data.usage_today} / ${data.daily_limit} analyses used`;
            }
        })
        .catch(error => console.log('Auth check skipped:', error));
    
    // Set active nav link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.ff-nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Close dropdown on outside click
    document.addEventListener('click', function(event) {
        const userMenu = document.querySelector('.ff-user-menu');
        if (userMenu && !userMenu.contains(event.target)) {
            const dropdown = document.getElementById('ffUserDropdown');
            if (dropdown) {
                dropdown.classList.remove('active');
            }
        }
    });
});

console.log('news-analysis.js loaded - all functions are now global');
