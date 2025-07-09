// Image Analysis Main Module
window.ImageApp = window.ImageApp || {};

window.ImageApp.main = (function() {
    'use strict';

    // Module state
    let isInitialized = false;
    let currentAnalysisId = null;
    let analysisInProgress = false;

    // Initialize the application
    function initialize() {
        if (isInitialized) return;

        console.log('Initializing Image Analysis App...');

        // Initialize sub-modules
        window.ImageApp.ui.initialize();
        
        // Set up event listeners
        setupEventListeners();
        
        // Check authentication status
        checkAuthStatus();
        
        // Initialize drag and drop
        initializeDragDrop();
        
        isInitialized = true;
        console.log('Image Analysis App initialized successfully');
    }

    // Set up global event listeners
    function setupEventListeners() {
        // File input change
        const fileInput = document.getElementById('imageFile');
        if (fileInput) {
            fileInput.addEventListener('change', handleFileSelect);
        }

        // Upload area click
        const uploadArea = document.getElementById('uploadArea');
        if (uploadArea) {
            uploadArea.addEventListener('click', () => {
                if (!analysisInProgress) {
                    fileInput.click();
                }
            });
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', handleKeyboardShortcuts);
    }

    // Initialize drag and drop functionality
    function initializeDragDrop() {
        const uploadArea = document.getElementById('uploadArea');
        if (!uploadArea) return;

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.add('drag-hover');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.remove('drag-hover');
            });
        });

        uploadArea.addEventListener('drop', handleDrop);
    }

    // Handle file drop
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            handleFile(files[0]);
        }
    }

    // Handle file selection
    function handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    }

    // Handle file processing
    function handleFile(file) {
        // Validate file type
        if (!window.ImageApp.helpers.validateImageFile(file)) {
            window.ImageApp.ui.showError('Please upload a valid image file (JPG, PNG, GIF, WebP, BMP)');
            return;
        }

        // Validate file size (max 50MB)
        const maxSize = 50 * 1024 * 1024;
        if (file.size > maxSize) {
            window.ImageApp.ui.showError('File size must be less than 50MB');
            return;
        }

        // Display file info
        window.ImageApp.ui.displayFileInfo(file);
        
        // Enable analyze button
        const analyzeBtn = document.getElementById('analyzeImageBtn');
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
        }
    }

    // Check authentication status
    async function checkAuthStatus() {
        try {
            const response = await window.ffAPI.getUserStatus();
            if (response.success && response.authenticated) {
                window.ImageApp.ui.updateUserStatus(response.user);
            }
        } catch (error) {
            console.error('Failed to check auth status:', error);
        }
    }

    // Handle keyboard shortcuts
    function handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + Enter to analyze
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const analyzeBtn = document.getElementById('analyzeImageBtn');
            if (analyzeBtn && !analyzeBtn.disabled && !analysisInProgress) {
                window.analyzeImage();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            window.ImageApp.ui.closeAllModals();
        }
    }

    // Global function to start analysis
    window.analyzeImage = async function(tier = 'pro') {
        if (analysisInProgress) return;

        const fileInput = document.getElementById('imageFile');
        if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
            window.ImageApp.ui.showError('Please select an image to analyze');
            return;
        }

        const file = fileInput.files[0];
        
        // Start analysis
        analysisInProgress = true;
        currentAnalysisId = Date.now().toString();
        
        try {
            await window.ImageApp.analysis.analyzeImage(file, tier);
        } catch (error) {
            console.error('Analysis failed:', error);
            window.ImageApp.ui.showError('Analysis failed. Please try again.');
        } finally {
            analysisInProgress = false;
        }
    };

    // Global function to reset analysis
    window.resetImageAnalysis = function() {
        // Clear file input
        const fileInput = document.getElementById('imageFile');
        if (fileInput) {
            fileInput.value = '';
        }

        // Hide file info
        window.ImageApp.ui.hideFileInfo();

        // Hide results
        window.ImageApp.ui.hideResults();

        // Reset button state
        const analyzeBtn = document.getElementById('analyzeImageBtn');
        if (analyzeBtn) {
            analyzeBtn.disabled = true;
        }

        // Clear current analysis
        currentAnalysisId = null;
        analysisInProgress = false;
    };

    // Global function to remove file
    window.removeImageFile = function() {
        window.resetImageAnalysis();
    };

    // Global function to share results
    window.shareImageResults = function() {
        if (!currentAnalysisId) return;
        
        window.ImageApp.ui.showShareModal(currentAnalysisId);
    };

    // Global function to download PDF
    window.downloadImagePDF = async function() {
        if (!currentAnalysisId) return;
        
        try {
            window.ImageApp.ui.showLoading('Generating PDF report...');
            
            const response = await window.ffAPI.generatePDF({
                analysisId: currentAnalysisId,
                type: 'image'
            });
            
            if (response.success && response.pdfUrl) {
                // Download the PDF
                const link = document.createElement('a');
                link.href = response.pdfUrl;
                link.download = `image-analysis-${currentAnalysisId}.pdf`;
                link.click();
            } else {
                throw new Error('Failed to generate PDF');
            }
        } catch (error) {
            console.error('PDF generation failed:', error);
            window.ImageApp.ui.showError('Failed to generate PDF report');
        } finally {
            window.ImageApp.ui.hideLoading();
        }
    };

    // Export public methods
    return {
        initialize: initialize,
        getCurrentAnalysisId: () => currentAnalysisId,
        isAnalysisInProgress: () => analysisInProgress
    };
})();

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    window.ImageApp.main.initialize();
});
