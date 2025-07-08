// static/js/news-main.js - Main integration file

// ============================================================================
// GLOBAL VARIABLES
// ============================================================================

window.currentTier = 'free';
window.currentInputType = 'text';

// ============================================================================
// MAIN INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all UI components
    initializeUI();
    
    // Setup event listeners
    setupEventListeners();
    
    // Track page load
    if (typeof gtag !== 'undefined') {
        gtag('event', 'page_view', {
            page_title: 'NewsVerify Pro - News Verification Platform',
            page_location: window.location.href,
            content_group1: 'News Verification'
        });
    }
});

// ============================================================================
// UI INITIALIZATION
// ============================================================================

function initializeUI() {
    // UI components are initialized in news-ui.js
    console.log('News verification platform initialized');
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================

function setupEventListeners() {
    // Input type switching
    const inputTabs = document.querySelectorAll('.input-tab');
    inputTabs.forEach((tab, index) => {
        tab.addEventListener('click', () => switchInputType(index === 0 ? 'text' : 'url'));
    });
    
    // Analysis buttons
    const freeAnalysisBtn = document.querySelector('.btn-primary[onclick*="free"]');
    const proAnalysisBtn = document.querySelector('.btn-primary[onclick*="pro"]');
    
    if (freeAnalysisBtn) {
        freeAnalysisBtn.onclick = () => runAnalysis('free');
    }
    if (proAnalysisBtn) {
        proAnalysisBtn.onclick = () => runAnalysis('pro');
    }
    
    // Test data button
    const testBtn = document.querySelector('.btn-test');
    if (testBtn) {
        testBtn.onclick = loadTestData;
    }
    
    // Reset button
    const resetBtn = document.querySelector('.btn-secondary[onclick*="reset"]');
    if (resetBtn) {
        resetBtn.onclick = resetForm;
    }
}

// ============================================================================
// INPUT SWITCHING
// ============================================================================

function switchInputType(type) {
    window.currentInputType = type;
    
    document.querySelectorAll('.input-tab').forEach((tab, index) => {
        tab.classList.remove('active');
        if ((type === 'text' && index === 0) || (type === 'url' && index === 1)) {
            tab.classList.add('active');
        }
    });
    
    document.querySelectorAll('.input-content').forEach(content => {
        content.classList.remove('active');
    });
    
    const targetContent = document.getElementById(type + 'Input');
    if (targetContent) {
        targetContent.classList.add('active');
    }
}

// ============================================================================
// ANALYSIS FUNCTIONS
// ============================================================================

async function runAnalysis(tier) {
    window.currentTier = tier;
    
    // Use the analyze function from news-analysis.js
    if (window.newsAnalysis && window.newsAnalysis.analyzeArticle) {
        await window.newsAnalysis.analyzeArticle();
    } else {
        console.error('Analysis module not loaded');
        showNotification('Analysis system not ready. Please refresh the page.', 'error');
    }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function loadTestData() {
    const testContent = `Breaking: Infrastructure Bill Passes Senate with Bipartisan Support
    
By Sarah Johnson
Washington, D.C. - December 15, 2024

The Department of Transportation announced today the allocation of $2.3 billion for highway improvements across 15 states, according to Transportation Secretary Pete Buttigieg. This initiative will create approximately 45,000 jobs over the next 18 months.

"This represents the largest single infrastructure investment in recent history," Buttigieg stated during a press conference this morning. The announcement comes following strong bipartisan support for the infrastructure bill passed last quarter.

Senator John Smith (R-TX) praised the allocation, saying, "This investment will modernize our aging infrastructure and create good-paying jobs for American workers." However, some critics question the timeline for implementation.

Industry experts predict significant economic impact in rural communities. Dr. Maria Rodriguez, an economist at Georgetown University, estimates the multiplier effect could generate up to $5 billion in economic activity.

The funds will be distributed based on a formula considering population density, infrastructure condition ratings, and economic need. States must submit detailed proposals by March 2025 to qualify for funding.

Environmental groups have expressed concerns about the potential impact on protected wetlands, though the Department maintains all projects will undergo thorough environmental review.

This development marks a significant milestone in the administration's infrastructure agenda, with additional funding packages expected to be announced in the coming months.`;
    
    document.getElementById('news-text').value = testContent;
    switchInputType('text');
    
    showNotification('Sample news content loaded successfully!', 'success');
}

function resetForm() {
    document.getElementById('news-text').value = '';
    document.getElementById('article-url').value = '';
    document.getElementById('results').style.display = 'none';
    document.getElementById('results').innerHTML = '';
    
    if (window.currentAnalysisData) {
        window.currentAnalysisData = null;
    }
    
    showNotification('Form reset successfully', 'success');
}

// ============================================================================
// ERROR HANDLING
// ============================================================================

window.addEventListener('error', function(e) {
    console.error('Global error:', e);
    if (e.message && e.message.includes('showNotification')) {
        // Fallback notification function
        window.showNotification = function(message, type) {
            alert(message);
        };
    }
});
