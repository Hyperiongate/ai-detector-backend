// news-analysis.js - SIMPLE WORKING VERSION
// This version makes all functions globally available for onclick handlers

console.log('news-analysis.js loading...');

// Create namespace
window.NewsApp = window.NewsApp || {};

// Create analysis object
NewsApp.analysis = {
    currentAnalysisData: null,
    analysisInProgress: false,
    progressInterval: null,
    
    runAnalysis: async function(url, tier = 'pro') {
        console.log('Running analysis for URL:', url);
        
        if (this.analysisInProgress) {
            console.log('Analysis already in progress');
            return;
        }
        
        this.analysisInProgress = true;
        
        try {
            this.startProgressAnimation();
            
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
            
            this.currentAnalysisData = data;
            await this.completeProgressAnimation();
            window.displayRealResults(data);
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.handleError(error.message);
        } finally {
            this.analysisInProgress = false;
        }
    },
    
    runAnalysisText: async function(text, tier = 'pro') {
        console.log('Running analysis for text');
        
        if (this.analysisInProgress) {
            console.log('Analysis already in progress');
            return;
        }
        
        this.analysisInProgress = true;
        
        try {
            this.startProgressAnimation();
            
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
            
            this.currentAnalysisData = data;
            await this.completeProgressAnimation();
            window.displayRealResults(data);
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.handleError(error.message);
        } finally {
            this.analysisInProgress = false;
        }
    },
    
    startProgressAnimation: function() {
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
        
        this.progressInterval = setInterval(() => {
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
    },
    
    completeProgressAnimation: async function() {
        return new Promise((resolve) => {
            if (this.progressInterval) {
                clearInterval(this.progressInterval);
                this.progressInterval = null;
            }
            
            document.querySelectorAll('.analysis-stage').forEach(stage => {
                stage.classList.remove('active');
                stage.classList.add('complete');
            });
            
            setTimeout(resolve, 500);
        });
    },
    
    handleError: function(message) {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
        
        const loadingSection = document.getElementById('loading-section');
        if (loadingSection) {
            loadingSection.style.display = 'none';
        }
        
        window.showError(message);
    },
    
    clearAnalysis: function() {
        this.currentAnalysisData = null;
        this.analysisInProgress = false;
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
    }
};

// =============================================================================
// GLOBAL FUNCTIONS - These MUST be on window object for onclick to work
// =============================================================================

window.analyzeArticle = async function() {
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
        await NewsApp.analysis.runAnalysis(url, 'pro');
    } else {
        const text = textInput.value.trim();
        if (!text) {
            alert('Please paste article text');
            return;
        }
        await NewsApp.analysis.runAnalysisText(text, 'pro');
    }
};

window.resetForm = function() {
    console.log('resetForm called');
    document.getElementById('news-url').value = '';
    document.getElementById('news-text').value = '';
    
    window.switchInputType('url');
    
    const errorContainer = document.getElementById('error-container');
    if (errorContainer) {
        errorContainer.style.display = 'none';
    }
    
    const resultsSection = document.getElementById('results-section');
    if (resultsSection) {
        resultsSection.style.display = 'none';
    }
    
    NewsApp.analysis.clearAnalysis();
    
    document.querySelector('.input-section').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
    });
};

window.switchInputType = function(type) {
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
};

window.togglePlanComparison = function() {
    console.log('togglePlanComparison called');
    const content = document.getElementById('plan-comparison-content');
    const chevron = document.getElementById('plan-chevron');
    
    if (content && chevron) {
        content.classList.toggle('show');
        chevron.style.transform = content.classList.contains('show') ? 'rotate(180deg)' : 'rotate(0deg)';
    }
};

window.toggleResources = function() {
    console.log('toggleResources called');
    const content = document.getElementById('resources-content');
    const chevron = document.querySelector('.resources-header .chevron-icon');
    
    if (content && chevron) {
        content.classList.toggle('show');
        chevron.style.transform = content.classList.contains('show') ? 'rotate(180deg)' : 'rotate(0deg)';
    }
};

window.toggleFeaturePreview = function() {
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
};

window.showError = function(message) {
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
};

window.retryAnalysis = function() {
    console.log('retryAnalysis called');
    const errorContainer = document.getElementById('error-container');
    if (errorContainer) {
        errorContainer.style.display = 'none';
    }
    window.analyzeArticle();
};

window.toggleDropdown = function(header) {
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
};

window.showAnalysisProcess = function() {
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
};

window.generatePDF = async function() {
    console.log('generatePDF called');
    const analysisData = NewsApp.analysis.currentAnalysisData;
    
    if (!analysisData) {
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
                results: analysisData
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
};

window.downloadFullReport = function() {
    console.log('downloadFullReport called');
    window.generatePDF();
};

window.displayRealResults = function(results) {
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
};

// Navigation functions
window.ffNav = {
    checkAuthStatus: async function() {
        try {
            const response = await fetch('/api/user/status');
            if (!response.ok) return;
            
            const data = await response.json();
            
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
        } catch (error) {
            console.log('Auth check skipped:', error.message);
        }
    },
    
    init: function() {
        this.checkAuthStatus();
        
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
    }
};

// Global navigation functions
window.ffToggleMobileMenu = function() {
    const navLinks = document.getElementById('ffNavLinks');
    navLinks.classList.toggle('active');
};

window.ffToggleUserDropdown = function() {
    const dropdown = document.getElementById('ffUserDropdown');
    dropdown.classList.toggle('active');
};

window.ffLogout = async function() {
    try {
        await fetch('/api/logout', { method: 'POST' });
        window.location.href = '/';
    } catch (error) {
        console.error('Logout failed:', error);
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing...');
    
    // Initialize navigation
    if (window.ffNav) {
        window.ffNav.init();
    }
    
    // Verify all functions are available
    console.log('Function availability check:', {
        togglePlanComparison: typeof window.togglePlanComparison,
        toggleResources: typeof window.toggleResources,
        toggleFeaturePreview: typeof window.toggleFeaturePreview,
        analyzeArticle: typeof window.analyzeArticle,
        switchInputType: typeof window.switchInputType,
        resetForm: typeof window.resetForm,
        showError: typeof window.showError,
        retryAnalysis: typeof window.retryAnalysis,
        toggleDropdown: typeof window.toggleDropdown,
        showAnalysisProcess: typeof window.showAnalysisProcess,
        generatePDF: typeof window.generatePDF,
        downloadFullReport: typeof window.downloadFullReport,
        displayRealResults: typeof window.displayRealResults,
        ffToggleMobileMenu: typeof window.ffToggleMobileMenu,
        ffToggleUserDropdown: typeof window.ffToggleUserDropdown,
        ffLogout: typeof window.ffLogout
    });
});

console.log('news-analysis.js loaded successfully - all functions should be available');
