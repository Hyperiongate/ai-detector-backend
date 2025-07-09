/**
 * Speech Analysis Main Module
 * Coordinates all speech analysis functionality
 */

// Initialize the SpeechApp namespace
window.SpeechApp = window.SpeechApp || {};

// Main initialization
document.addEventListener('DOMContentLoaded', function() {
    console.log('Speech Analysis App Initializing...');
    
    // Initialize all modules
    initializeSpeechModules();
    
    // Set up global error handling
    setupErrorHandling();
    
    // Check for URL parameters (for sharing)
    checkUrlParameters();
});

/**
 * Initialize all speech analysis modules
 */
function initializeSpeechModules() {
    // Initialize UI module
    if (window.SpeechApp.ui && window.SpeechApp.ui.initialize) {
        window.SpeechApp.ui.initialize();
    }
    
    // Initialize analysis module
    if (window.SpeechApp.analysis && window.SpeechApp.analysis.initialize) {
        window.SpeechApp.analysis.initialize();
    }
    
    // Initialize results module
    if (window.SpeechApp.results && window.SpeechApp.results.initialize) {
        window.SpeechApp.results.initialize();
    }
    
    // Initialize helpers
    if (window.SpeechApp.helpers && window.SpeechApp.helpers.initialize) {
        window.SpeechApp.helpers.initialize();
    }
    
    console.log('All speech modules initialized');
}

/**
 * Global error handling
 */
function setupErrorHandling() {
    window.addEventListener('error', function(event) {
        console.error('Global error:', event.error);
        
        // Show user-friendly error message
        if (window.SpeechApp.ui && window.SpeechApp.ui.showError) {
            window.SpeechApp.ui.showError('An unexpected error occurred. Please try again.');
        }
    });
    
    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', function(event) {
        console.error('Unhandled promise rejection:', event.reason);
        
        if (window.SpeechApp.ui && window.SpeechApp.ui.showError) {
            window.SpeechApp.ui.showError('An error occurred while processing. Please try again.');
        }
    });
}

/**
 * Check URL parameters for shared results
 */
function checkUrlParameters() {
    const urlParams = new URLSearchParams(window.location.search);
    const analysisId = urlParams.get('id');
    
    if (analysisId) {
        // Load shared analysis
        loadSharedAnalysis(analysisId);
    }
}

/**
 * Load a shared analysis by ID
 */
function loadSharedAnalysis(analysisId) {
    console.log('Loading shared analysis:', analysisId);
    
    // Show loading state
    if (window.SpeechApp.ui) {
        window.SpeechApp.ui.showLoading('Loading shared analysis...');
    }
    
    // Fetch the analysis
    fetch(`/api/get-analysis/${analysisId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.results) {
                // Display the results
                if (window.SpeechApp.results) {
                    window.SpeechApp.results.displayResults(data.results);
                }
            } else {
                throw new Error('Analysis not found');
            }
        })
        .catch(error => {
            console.error('Error loading shared analysis:', error);
            if (window.SpeechApp.ui) {
                window.SpeechApp.ui.showError('Could not load the shared analysis.');
            }
        });
}

/**
 * Global function to start speech analysis
 * Can be called from HTML
 */
window.analyzeSpeech = function(tier = 'free') {
    console.log('Starting speech analysis with tier:', tier);
    
    // Get the current input type
    const inputType = document.querySelector('input[name="input-type"]:checked')?.value || 'file';
    
    if (inputType === 'file') {
        const fileInput = document.getElementById('speechFile');
        const file = fileInput?.files[0];
        
        if (!file) {
            window.SpeechApp.ui.showError('Please select a file to analyze');
            return;
        }
        
        // Check file size
        const maxSize = 100 * 1024 * 1024; // 100MB for audio
        if (file.type.startsWith('video/')) {
            const maxVideoSize = 500 * 1024 * 1024; // 500MB for video
            if (file.size > maxVideoSize) {
                window.SpeechApp.ui.showError('Video file is too large. Maximum size is 500MB.');
                return;
            }
        } else if (file.size > maxSize) {
            window.SpeechApp.ui.showError('Audio file is too large. Maximum size is 100MB.');
            return;
        }
        
        // Start file analysis
        window.SpeechApp.analysis.analyzeFile(file, tier);
        
    } else if (inputType === 'youtube') {
        const youtubeUrl = document.getElementById('youtubeUrl')?.value;
        
        if (!youtubeUrl) {
            window.SpeechApp.ui.showError('Please enter a YouTube URL');
            return;
        }
        
        // Validate YouTube URL
        if (!window.SpeechApp.helpers.isValidYouTubeUrl(youtubeUrl)) {
            window.SpeechApp.ui.showError('Please enter a valid YouTube URL');
            return;
        }
        
        // Start YouTube analysis
        window.SpeechApp.analysis.analyzeYouTube(youtubeUrl, tier);
    }
};

/**
 * Global function to reset the analysis
 */
window.resetSpeechAnalysis = function() {
    console.log('Resetting speech analysis');
    
    // Reset UI
    if (window.SpeechApp.ui) {
        window.SpeechApp.ui.reset();
    }
    
    // Clear results
    if (window.SpeechApp.results) {
        window.SpeechApp.results.clear();
    }
    
    // Reset form
    const form = document.getElementById('speechAnalysisForm');
    if (form) {
        form.reset();
    }
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
};

/**
 * Global function to download PDF report
 */
window.downloadSpeechPDF = function() {
    console.log('Downloading speech analysis PDF');
    
    const results = window.SpeechApp.results.getCurrentResults();
    if (!results) {
        window.SpeechApp.ui.showError('No analysis results to download');
        return;
    }
    
    // Show loading
    window.SpeechApp.ui.showLoading('Generating PDF report...');
    
    // Call API to generate PDF
    fetch('/api/generate-speech-pdf', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            results: results,
            timestamp: new Date().toISOString(),
            analysisId: results.analysisId || 'SPEECH-' + Date.now()
        })
    })
    .then(response => response.blob())
    .then(blob => {
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `speech-analysis-${Date.now()}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        window.SpeechApp.ui.hideLoading();
        window.SpeechApp.ui.showSuccess('PDF report downloaded successfully!');
    })
    .catch(error => {
        console.error('Error generating PDF:', error);
        window.SpeechApp.ui.hideLoading();
        window.SpeechApp.ui.showError('Failed to generate PDF report');
    });
};

/**
 * Global function to share results
 */
window.shareSpeechResults = function() {
    console.log('Sharing speech results');
    
    const results = window.SpeechApp.results.getCurrentResults();
    if (!results) {
        window.SpeechApp.ui.showError('No analysis results to share');
        return;
    }
    
    // Show share modal
    const truthScore = results.truthScore || 0;
    const verifiedClaims = results.claims?.filter(c => c.verdict === 'True').length || 0;
    
    showSpeechShareModal(truthScore, verifiedClaims);
};

/**
 * Global function to switch input type
 */
window.switchSpeechInputType = function(type) {
    console.log('Switching input type to:', type);
    
    // Hide all input sections
    document.querySelectorAll('.input-section').forEach(section => {
        section.style.display = 'none';
    });
    
    // Show selected input section
    const selectedSection = document.getElementById(`${type}Input`);
    if (selectedSection) {
        selectedSection.style.display = 'block';
    }
    
    // Update radio button
    const radio = document.querySelector(`input[name="input-type"][value="${type}"]`);
    if (radio) {
        radio.checked = true;
    }
    
    // Clear any previous errors
    if (window.SpeechApp.ui) {
        window.SpeechApp.ui.clearError();
    }
};

/**
 * Export functions for use in other modules
 */
window.SpeechApp.main = {
    analyzeSpeech: window.analyzeSpeech,
    resetAnalysis: window.resetSpeechAnalysis,
    downloadPDF: window.downloadSpeechPDF,
    shareResults: window.shareSpeechResults,
    switchInputType: window.switchSpeechInputType
};

console.log('Speech Analysis Main Module Loaded');
