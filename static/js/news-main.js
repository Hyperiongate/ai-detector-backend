// news-main.js - Main integration file for news verification
// This file coordinates all the news analysis modules

// Only declare if not already declared
if (typeof window.newsAnalysisApp === 'undefined') {
    window.newsAnalysisApp = {};
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('News verification platform initialized');
    
    // Initialize all modules
    initializeUI();
    initializeEventListeners();
    
    // Set up global error handler
    window.addEventListener('error', function(event) {
        console.error('Global error:', event);
    });
});

// Initialize UI components
function initializeUI() {
    // Initialize tooltips
    initializeTooltips();
    
    // Set up smooth scrolling
    setupSmoothScrolling();
}

// Initialize all event listeners
function initializeEventListeners() {
    // Event listeners are set up in individual modules
}

// Main analysis function (called by buttons)
window.analyzeArticle = function(tier = 'free') {
    console.log('analyzeArticle called with tier:', tier);
    
    // Call the analysis function from news-analysis.js
    if (typeof runAnalysis === 'function') {
        runAnalysis(tier);
    } else if (typeof window.runAnalysis === 'function') {
        window.runAnalysis(tier);
    } else if (typeof window.runNewsAnalysis === 'function') {
        window.runNewsAnalysis(tier);
    } else {
        console.error('Analysis function not found');
        if (typeof showNotification === 'function') {
            showNotification('Analysis system not ready. Please refresh the page.', 'error');
        } else {
            alert('Analysis system not ready. Please refresh the page.');
        }
    }
};

// Switch input type - use the one from news-analysis.js
window.switchInputType = function(type) {
    console.log('Switching to input type:', type);
    
    // Update tabs
    document.querySelectorAll('.input-tab').forEach((tab, index) => {
        const tabTypes = ['url', 'text', 'article'];
        tab.classList.toggle('active', tabTypes[index] === type);
    });
    
    // Update content
    document.querySelectorAll('.input-content').forEach(content => {
        content.classList.remove('active');
    });
    
    const targetContent = document.getElementById(type + 'Input');
    if (targetContent) {
        targetContent.classList.add('active');
    }
    
    // Call the module function if available
    if (typeof window.switchNewsInputType === 'function') {
        window.switchNewsInputType(type);
    }
};

// Reset form - use the one from news-analysis.js
window.resetForm = function() {
    if (typeof window.resetNewsForm === 'function') {
        window.resetNewsForm();
    } else {
        // Fallback reset
        document.getElementById('news-text').value = '';
        document.getElementById('articleUrl').value = '';
        document.getElementById('fullArticle').value = '';
        
        const resultsDiv = document.getElementById('results');
        if (resultsDiv) {
            resultsDiv.style.display = 'none';
            resultsDiv.innerHTML = '';
        }
        
        console.log('Form reset');
    }
};

// Initialize tooltips
function initializeTooltips() {
    // Add tooltips to elements with title attribute
    document.querySelectorAll('[title]').forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.dataset.originalTitle = this.title;
            this.title = '';
        });
        
        element.addEventListener('mouseleave', function() {
            this.title = this.dataset.originalTitle || '';
        });
    });
}

// Set up smooth scrolling
function setupSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Make sure functions are available globally
console.log('News main.js loaded - functions available:', {
    analyzeArticle: typeof window.analyzeArticle,
    switchInputType: typeof window.switchInputType,
    resetForm: typeof window.resetForm
});
