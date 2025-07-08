// news-main.js - Main coordination module for news analysis
(function() {
    'use strict';
    
    // Initialize namespace
    window.NewsApp = window.NewsApp || {};
    
    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        console.log('News main.js loaded - functions available:', window.NewsApp);
        
        // Initialize UI components
        if (window.NewsApp.ui && window.NewsApp.ui.init) {
            window.NewsApp.ui.init();
        }
        
        // Set up analyze button click handlers
        const analyzeButtons = document.querySelectorAll('.analyze-btn');
        analyzeButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const tier = this.getAttribute('data-tier') || 'free';
                window.analyzeArticle(tier);
            });
        });
        
        // Set up Enter key handler for URL input
        const urlInput = document.getElementById('articleUrl');
        if (urlInput) {
            urlInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    window.analyzeArticle('pro');
                }
            });
        }
    });
    
    // Global analyze function
    window.analyzeArticle = function(tier = 'free') {
        console.log('analyzeArticle called with tier:', tier);
        
        const urlInput = document.getElementById('articleUrl');
        if (!urlInput || !urlInput.value.trim()) {
            alert('Please enter a news article URL');
            return;
        }
        
        // Call the analysis function with proper namespace
        if (window.NewsApp && window.NewsApp.analysis && window.NewsApp.analysis.runAnalysis) {
            window.NewsApp.analysis.runAnalysis(urlInput.value.trim(), tier);
        } else {
            console.error('Analysis function not found. NewsApp structure:', window.NewsApp);
            alert('Analysis module not loaded properly. Please refresh the page.');
        }
    };
    
    // Helper function to reset analysis
    window.resetAnalysis = function() {
        if (window.NewsApp && window.NewsApp.ui && window.NewsApp.ui.resetAnalysis) {
            window.NewsApp.ui.resetAnalysis();
        }
        
        // Clear any stored analysis data
        if (window.NewsApp && window.NewsApp.analysis && window.NewsApp.analysis.clearAnalysis) {
            window.NewsApp.analysis.clearAnalysis();
        }
    };
    
    // Initialize on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            console.log('News verification platform initialized');
        });
    } else {
        console.log('News verification platform initialized');
    }
    
})();
