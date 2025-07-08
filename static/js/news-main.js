// news-main.js - Main integration file for news verification
// This file coordinates all the news analysis modules

// Global variables
let currentInputType = 'text';
let currentTier = 'free';

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
    // Enhance UI with the third tab
    if (typeof enhanceNewsUI === 'function') {
        enhanceNewsUI();
    }
    
    // Initialize tooltips
    initializeTooltips();
    
    // Set up smooth scrolling
    setupSmoothScrolling();
}

// Initialize all event listeners
function initializeEventListeners() {
    // Tab switching
    document.querySelectorAll('.input-tab').forEach((tab, index) => {
        tab.addEventListener('click', () => {
            const types = ['text', 'url', 'article'];
            switchInputType(types[index]);
        });
    });
    
    // Test data button
    const testBtn = document.querySelector('.btn-test');
    if (testBtn) {
        testBtn.addEventListener('click', loadTestData);
    }
    
    // Reset button
    const resetBtn = document.querySelector('.btn-secondary');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetForm);
    }
}

// Main analysis function (called by buttons)
function analyzeArticle(tier = 'free') {
    currentTier = tier;
    
    // Call the analysis function from news-analysis.js
    if (typeof runAnalysis === 'function') {
        runAnalysis(tier);
    } else if (typeof runNewsAnalysis === 'function') {
        runNewsAnalysis(tier);
    } else {
        console.error('Analysis function not found');
        showNotification('Analysis system not ready. Please refresh the page.', 'error');
    }
}

// Switch input type
function switchInputType(type) {
    currentInputType = type;
    
    // Update tabs
    document.querySelectorAll('.input-tab').forEach((tab, index) => {
        const tabTypes = ['text', 'url', 'article'];
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
    if (typeof switchNewsInputType === 'function') {
        switchNewsInputType(type);
    }
}

// Load test data
function loadTestData() {
    const testContent = `By David Rising
Associated Press

BANGKOK -- President Donald Trump has threatened to impose sweeping tariffs on Mexico, Canada and China, some of the United States' largest trading partners. The move could spark a global trade war and drive up prices for American consumers.

Trump announced Monday he would impose a 25% tariff on all goods from Mexico and Canada on his first day in office. He also threatened an additional 10% tariff on Chinese imports.

"These tariffs will remain in effect until such time as Drugs, in particular Fentanyl, and all Illegal Aliens stop this Invasion of our Country!" Trump wrote on social media.

Economic experts warn the tariffs could significantly impact the U.S. economy. "Tariffs are paid by importers, not foreign countries, and those costs are typically passed on to consumers," said Mary Johnson, an economist at Georgetown University.`;
    
    // Fill all input fields
    const textArea = document.getElementById('news-text');
    const urlInput = document.getElementById('articleUrl');
    const articleArea = document.getElementById('fullArticle');
    
    if (textArea) textArea.value = testContent;
    if (urlInput) urlInput.value = 'https://apnews.com/article/trump-tariffs-mexico-canada-china-trade';
    if (articleArea) articleArea.value = testContent;
    
    switchInputType('text');
    showNotification('Sample news content loaded!', 'success');
}

// Reset form
function resetForm() {
    // Clear all inputs
    const textArea = document.getElementById('news-text');
    const urlInput = document.getElementById('articleUrl');
    const articleArea = document.getElementById('fullArticle');
    
    if (textArea) textArea.value = '';
    if (urlInput) urlInput.value = '';
    if (articleArea) articleArea.value = '';
    
    // Hide results
    const resultsDiv = document.getElementById('results');
    if (resultsDiv) {
        resultsDiv.style.display = 'none';
        resultsDiv.innerHTML = '';
    }
    
    // Call module reset if available
    if (typeof resetNewsForm === 'function') {
        resetNewsForm();
    }
    
    showNotification('Form reset successfully', 'success');
}

// Show notification
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

// Enhanced back to top functionality
window.addEventListener('scroll', () => {
    const backToTop = document.getElementById('backToTop');
    if (backToTop) {
        if (window.pageYOffset > 300) {
            backToTop.classList.add('visible');
        } else {
            backToTop.classList.remove('visible');
        }
    }
});

// Scroll to top function
window.scrollToTop = function() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
};

// Export global functions
window.analyzeArticle = analyzeArticle;
window.switchInputType = switchInputType;
window.loadTestData = loadTestData;
window.resetForm = resetForm;
window.showNotification = showNotification;
