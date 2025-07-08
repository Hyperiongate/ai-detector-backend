// news-analysis.js - Fixed Analysis Module
// Handles the analysis process and API calls

let currentInputType = 'text';
let currentAnalysisData = null;
let isAnalyzing = false;

// Initialize the module
function initializeAnalysis() {
    // Set up event listeners
    setupEventListeners();
    
    // Check for any saved state
    const savedArticle = sessionStorage.getItem('lastArticle');
    if (savedArticle) {
        document.getElementById('news-text').value = savedArticle;
    }
}

// Set up all event listeners
function setupEventListeners() {
    // Tab switching
    document.querySelectorAll('.input-tab').forEach((tab, index) => {
        tab.addEventListener('click', () => {
            switchInputType(['text', 'url', 'article'][index]);
        });
    });
    
    // Analysis buttons
    document.querySelectorAll('.btn-primary').forEach(btn => {
        if (btn.textContent.includes('Start') || btn.textContent.includes('Analyze Another')) {
            btn.addEventListener('click', (e) => {
                const tier = btn.textContent.toLowerCase().includes('pro') ? 'pro' : 'free';
                runAnalysis(tier);
            });
        }
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
}

// Load test data
function loadTestData() {
    const testContent = `By David Rising
    Associated Press
    
    BANGKOK -- President Donald Trump has threatened to impose sweeping tariffs on Mexico, Canada and China, some of the United States' largest trading partners. The move c
