/**
 * Speech UI Module
 * Handles all UI interactions and animations for speech analysis
 */

window.SpeechApp = window.SpeechApp || {};

window.SpeechApp.ui = (function() {
    'use strict';
    
    // UI Elements cache
    let elements = {};
    let particlesAnimation = null;
    
    /**
     * Initialize the UI module
     */
    function initialize() {
        console.log('Speech UI module initialized');
        cacheElements();
        setupEventListeners();
        initializeAnimations();
        setupTooltips();
    }
    
    /**
     * Cache commonly used elements
     */
    function cacheElements() {
        elements = {
            analysisForm: document.getElementById('speechAnalysisForm'),
            resultsSection: document.getElementById('speechResults'),
            loadingOverlay: document.getElementById('speechLoadingOverlay'),
            progressBar: document.querySelector('.speech-progress-bar'),
            progressText: document.querySelector('.speech-progress-text'),
            errorMessage: document.getElementById('speechErrorMessage'),
            successMessage: document.getElementById('speechSuccessMessage'),
            fileInput: document.getElementById('speechFile'),
            youtubeInput: document.getElementById('youtubeUrl'),
            analyzeButton: document.getElementById('analyzeSpeechBtn')
        };
    }
    
    /**
     * Set up event listeners
     */
    function setupEventListeners() {
        // Input type radio buttons
        const inputRadios = document.querySelectorAll('input[name="input-type"]');
        inputRadios.forEach(radio => {
            radio.addEventListener('change', handleInputTypeChange);
        });
        
        // File input
        if (elements.fileInput) {
            elements.fileInput.addEventListener('change', updateFileLabel);
        }
        
        // Drag and drop
        setupDragAndDrop();
        
        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', smoothScroll);
        });
        
        // Dropdown toggles
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('dropdown-toggle')) {
                toggleDropdown(e.target);
            }
        });
    }
    
    /**
     * Initialize animations
     */
    function initializeAnimations() {
        // Create floating particles
        createFloatingParticles();
        
        // Animate elements on scroll
        setupScrollAnimations();
        
        // Add hover effects
        addHoverEffects();
    }
    
    /**
     * Create floating particles background
     */
    function createFloatingParticles() {
        const particlesContainer = document.getElementById('speechParticles');
        if (!particlesContainer) return;
        
        const particleCount = 50;
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'floating-particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.top = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 20 + 's';
            particle.style.animationDuration = (20 + Math.random() * 20) + 's';
            particlesContainer.appendChild(particle);
        }
    }
    
    /**
     * Setup scroll animations
     */
    function setupScrollAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, { threshold: 0.1 });
        
        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            observer.observe(el);
        });
    }
    
    /**
     * Add hover effects to interactive elements
     */
    function addHoverEffects() {
        document.querySelectorAll('.analysis-card, .feature-item, .info-card').forEach(el => {
            el.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px)';
            });
            el.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });
    }
    
    /**
     * Setup tooltips
     */
    function setupTooltips() {
        document.querySelectorAll('[data-tooltip]').forEach(el => {
            el.addEventListener('mouseenter', showTooltip);
            el.addEventListener('mouseleave', hideTooltip);
        });
    }
    
    /**
     * Show tooltip
     */
    function showTooltip(e) {
        const tooltip = document.createElement('div');
        tooltip.className = 'custom-tooltip';
        tooltip.textContent = e.target.getAttribute('data-tooltip');
        
        document.body.appendChild(tooltip);
        
        const rect = e.target.getBoundingClientRect();
        tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
        tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
        
        setTimeout(() => tooltip.classList.add('show'), 10);
    }
    
    /**
     * Hide tooltip
     */
    function hideTooltip() {
        document.querySelectorAll('.custom-tooltip').forEach(tooltip => {
            tooltip.classList.remove('show');
            setTimeout(() => tooltip.remove(), 300);
        });
    }
    
    /**
     * Handle input type change
     */
    function handleInputTypeChange(e) {
        const type = e.target.value;
        window.switchSpeechInputType(type);
    }
    
    /**
     * Update file label
     */
    function updateFileLabel(e) {
        const fileName = e.target.files[0]?.name || 'No file chosen';
        const label = document.querySelector('.file-label-text');
        if (label) {
            label.textContent = fileName;
        }
    }
    
    /**
     * Setup drag and drop
     */
    function setupDragAndDrop() {
        const dropZone = document.querySelector('.file-upload-wrapper');
        if (!dropZone) return;
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('drag-over');
            });
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('drag-over');
            });
        });
        
        dropZone.addEventListener('drop', handleDrop);
    }
    
    /**
     * Handle file drop
     */
    function handleDrop(e) {
        const files = e.dataTransfer.files;
        if (files.length > 0 && elements.fileInput) {
            elements.fileInput.files = files;
            updateFileLabel({ target: elements.fileInput });
        }
    }
    
    /**
     * Smooth scroll
     */
    function smoothScroll(e) {
        e.preventDefault();
        const targetId = e.target.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
            targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
    
    /**
     * Toggle dropdown
     */
    function toggleDropdown(button) {
        const content = button.nextElementSibling;
        const isOpen = content.classList.contains('show');
        
        // Close all dropdowns
        document.querySelectorAll('.dropdown-content').forEach(dropdown => {
            dropdown.classList.remove('show');
        });
        
        // Toggle this dropdown
        if (!isOpen) {
            content.classList.add('show');
            button.querySelector('i').style.transform = 'rotate(180deg)';
        } else {
            button.querySelector('i').style.transform = 'rotate(0deg)';
        }
    }
    
    /**
     * Show analysis progress
     */
    function showAnalysisProgress() {
        if (elements.loadingOverlay) {
            elements.loadingOverlay.style.display = 'flex';
            elements.loadingOverlay.classList.add('fade-in');
        }
        
        // Disable form
        if (elements.analysisForm) {
            elements.analysisForm.classList.add('analyzing');
        }
        
        // Reset progress
        updateProgress(0, 'Starting analysis...');
    }
    
    /**
     * Hide analysis progress
     */
    function hideAnalysisProgress() {
        if (elements.loadingOverlay) {
            elements.loadingOverlay.classList.remove('fade-in');
            setTimeout(() => {
                elements.loadingOverlay.style.display = 'none';
            }, 300);
        }
        
        // Enable form
        if (elements.analysisForm) {
            elements.analysisForm.classList.remove('analyzing');
        }
    }
    
    /**
     * Update progress bar
     */
    function updateProgress(percentage, text) {
        if (elements.progressBar) {
            elements.progressBar.style.width = percentage + '%';
        }
        if (elements.progressText) {
            elements.progressText.textContent = text;
        }
    }
    
    /**
     * Show error message
     */
    function showError(message) {
        const errorEl = document.createElement('div');
        errorEl.className = 'alert alert-error fade-in';
        errorEl.innerHTML = `
            <i class="fas fa-exclamation-circle"></i>
            <span>${message}</span>
            <button class="alert-close" onclick="this.parentElement.remove()">×</button>
        `;
        
        const container = document.querySelector('.alerts-container') || document.body;
        container.appendChild(errorEl);
        
        setTimeout(() => errorEl.remove(), 5000);
    }
    
    /**
     * Show success message
     */
    function showSuccess(message) {
        const successEl = document.createElement('div');
        successEl.className = 'alert alert-success fade-in';
        successEl.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>${message}</span>
            <button class="alert-close" onclick="this.parentElement.remove()">×</button>
        `;
        
        const container = document.querySelector('.alerts-container') || document.body;
        container.appendChild(successEl);
        
        setTimeout(() => successEl.remove(), 5000);
    }
    
    /**
     * Show info message
     */
    function showInfo(message) {
        const infoEl = document.createElement('div');
        infoEl.className = 'alert alert-info fade-in';
        infoEl.innerHTML = `
            <i class="fas fa-info-circle"></i>
            <span>${message}</span>
            <button class="alert-close" onclick="this.parentElement.remove()">×</button>
        `;
        
        const container = document.querySelector('.alerts-container') || document.body;
        container.appendChild(infoEl);
        
        setTimeout(() => infoEl.remove(), 5000);
    }
    
    /**
     * Clear error messages
     */
    function clearError() {
        document.querySelectorAll('.alert-error').forEach(el => el.remove());
    }
    
    /**
     * Show loading state
     */
    function showLoading(message = 'Loading...') {
        const loadingEl = document.createElement('div');
        loadingEl.className = 'loading-indicator';
        loadingEl.innerHTML = `
            <div class="spinner"></div>
            <span>${message}</span>
        `;
        loadingEl.id = 'globalLoading';
        
        document.body.appendChild(loadingEl);
    }
    
    /**
     * Hide loading state
     */
    function hideLoading() {
        const loadingEl = document.getElementById('globalLoading');
        if (loadingEl) {
            loadingEl.remove();
        }
    }
    
    /**
     * Reset UI to initial state
     */
    function reset() {
        // Clear messages
        clearError();
        document.querySelectorAll('.alert').forEach(el => el.remove());
        
        // Reset form
        if (elements.analysisForm) {
            elements.analysisForm.reset();
        }
        
        // Reset file label
        const fileLabel = document.querySelector('.file-label-text');
        if (fileLabel) {
            fileLabel.textContent = 'Choose file or drag here';
        }
        
        // Hide results
        if (elements.resultsSection) {
            elements.resultsSection.style.display = 'none';
        }
        
        // Clear YouTube preview
        const preview = document.getElementById('youtubePreview');
        if (preview) {
            preview.style.display = 'none';
            preview.innerHTML = '';
        }
    }
    
    // Public API
    return {
        initialize: initialize,
        showAnalysisProgress: showAnalysisProgress,
        hideAnalysisProgress: hideAnalysisProgress,
        updateProgress: updateProgress,
        showError: showError,
        showSuccess: showSuccess,
        showInfo: showInfo,
        showLoading: showLoading,
        hideLoading: hideLoading,
        clearError: clearError,
        reset: reset
    };
})();

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        window.SpeechApp.ui.initialize();
    });
} else {
    window.SpeechApp.ui.initialize();
}

console.log('Speech UI Module Loaded');
