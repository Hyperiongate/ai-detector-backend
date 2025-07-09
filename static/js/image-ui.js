// Image UI Module
window.ImageApp = window.ImageApp || {};

window.ImageApp.ui = (function() {
    'use strict';

    // UI state
    let floatingParticles = [];
    let particleAnimationFrame = null;

    // Initialize UI components
    function initialize() {
        // Initialize floating particles
        initializeParticles();
        
        // Set up smooth scrolling
        setupSmoothScrolling();
        
        // Initialize tooltips
        initializeTooltips();
        
        // Set up hover effects
        setupHoverEffects();
    }

    // Initialize floating particles background
    function initializeParticles() {
        const container = document.querySelector('.image-analyzer-container');
        if (!container) return;

        // Create particle container
        const particleContainer = document.createElement('div');
        particleContainer.className = 'particle-container';
        container.appendChild(particleContainer);

        // Create particles
        for (let i = 0; i < 30; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 20 + 's';
            particle.style.animationDuration = (20 + Math.random() * 10) + 's';
            particleContainer.appendChild(particle);
            floatingParticles.push(particle);
        }
    }

    // Show loading animation
    function showLoadingAnimation() {
        const loadingContainer = document.getElementById('loadingAnimation');
        const resultsSection = document.getElementById('resultsSection');
        const analyzeBtn = document.getElementById('analyzeImageBtn');

        if (loadingContainer) {
            loadingContainer.style.display = 'flex';
            resetLoadingStages();
        }

        if (resultsSection) {
            resultsSection.style.display = 'none';
        }

        if (analyzeBtn) {
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        }
    }

    // Hide loading animation
    function hideLoadingAnimation() {
        const loadingContainer = document.getElementById('loadingAnimation');
        const analyzeBtn = document.getElementById('analyzeImageBtn');

        if (loadingContainer) {
            loadingContainer.style.display = 'none';
        }

        if (analyzeBtn) {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<i class="fas fa-microscope"></i> <span>Analyze Image</span>';
        }
    }

    // Reset loading stages
    function resetLoadingStages() {
        const steps = document.querySelectorAll('.loading-steps .step');
        steps.forEach(step => {
            step.classList.remove('active', 'completed');
        });

        const progressFill = document.getElementById('progressFill');
        if (progressFill) {
            progressFill.style.width = '0%';
        }

        const progressText = document.getElementById('progressText');
        if (progressText) {
            progressText.textContent = 'Initializing...';
        }
    }

    // Update analysis stage
    function updateAnalysisStage(stageNumber, stageText) {
        const steps = document.querySelectorAll('.loading-steps .step');
        
        // Mark previous steps as completed
        for (let i = 0; i < stageNumber - 1; i++) {
            if (steps[i]) {
                steps[i].classList.remove('active');
                steps[i].classList.add('completed');
            }
        }

        // Mark current step as active
        if (steps[stageNumber - 1]) {
            steps[stageNumber - 1].classList.add('active');
        }

        // Update progress text
        const progressText = document.getElementById('progressText');
        if (progressText) {
            progressText.textContent = stageText;
        }
    }

    // Display file info
    function displayFileInfo(file) {
        const fileInfo = document.getElementById('fileInfo');
        const uploadArea = document.getElementById('uploadArea');
        
        if (fileInfo) {
            // Update file details
            const fileName = fileInfo.querySelector('.file-name');
            const fileSize = fileInfo.querySelector('.file-size');
            
            if (fileName) {
                fileName.textContent = file.name;
            }
            
            if (fileSize) {
                fileSize.textContent = formatFileSize(file.size);
            }
            
            // Show file info, hide upload area
            fileInfo.style.display = 'flex';
            if (uploadArea) {
                uploadArea.style.display = 'none';
            }
            
            // Show image preview if possible
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const fileIcon = fileInfo.querySelector('.file-icon');
                    if (fileIcon) {
                        fileIcon.innerHTML = `<img src="${e.target.result}" alt="Preview" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px;">`;
                    }
                };
                reader.readAsDataURL(file);
            }
        }
    }

    // Hide file info
    function hideFileInfo() {
        const fileInfo = document.getElementById('fileInfo');
        const uploadArea = document.getElementById('uploadArea');
        
        if (fileInfo) {
            fileInfo.style.display = 'none';
        }
        
        if (uploadArea) {
            uploadArea.style.display = 'flex';
        }
    }

    // Show results section
    function showResults() {
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    // Hide results section
    function hideResults() {
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.style.display = 'none';
        }
    }

    // Show error message
    function showError(message) {
        const errorDisplay = document.getElementById('errorDisplay');
        const errorMessage = document.getElementById('errorMessage');
        
        if (errorDisplay && errorMessage) {
            errorMessage.textContent = message;
            errorDisplay.style.display = 'block';
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                errorDisplay.style.display = 'none';
            }, 5000);
        } else {
            // Fallback to alert
            alert(message);
        }
    }

    // Show modal
    function showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    }

    // Close modal
    function closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = '';
        }
    }

    // Close all modals
    function closeAllModals() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.style.display = 'none';
        });
        document.body.style.overflow = '';
    }

    // Show process modal
    function showProcessModal() {
        showModal('processModal');
    }

    // Show share modal
    function showShareModal(analysisId) {
        const shareLink = document.getElementById('shareLink');
        if (shareLink) {
            const url = `${window.location.origin}/analysis/image/${analysisId}`;
            shareLink.value = url;
        }
        showModal('shareModal');
    }

    // Show feedback modal
    function showFeedbackModal() {
        showModal('feedbackModal');
    }

    // Update user status in UI
    function updateUserStatus(user) {
        // Update any user-specific UI elements
        const tierBadges = document.querySelectorAll('.tier-badge');
        tierBadges.forEach(badge => {
            badge.textContent = user.tier.toUpperCase();
            badge.className = `tier-badge ${user.tier}`;
        });
    }

    // Format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Set up smooth scrolling
    function setupSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    }

    // Initialize tooltips
    function initializeTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', showTooltip);
            element.addEventListener('mouseleave', hideTooltip);
        });
    }

    // Show tooltip
    function showTooltip(e) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = e.target.getAttribute('data-tooltip');
        document.body.appendChild(tooltip);

        const rect = e.target.getBoundingClientRect();
        tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
        tooltip.style.left = rect.left + (rect.width - tooltip.offsetWidth) / 2 + 'px';
    }

    // Hide tooltip
    function hideTooltip() {
        const tooltips = document.querySelectorAll('.tooltip');
        tooltips.forEach(tooltip => tooltip.remove());
    }

    // Set up hover effects
    function setupHoverEffects() {
        const hoverElements = document.querySelectorAll('.info-card, .detection-item, .use-case');
        hoverElements.forEach(element => {
            element.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-4px)';
            });
            element.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });
    }

    // Show loading overlay with custom message
    function showLoading(message = 'Loading...') {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p>${message}</p>
            </div>
        `;
        document.body.appendChild(overlay);
    }

    // Hide loading overlay
    function hideLoading() {
        const overlay = document.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }

    // Export public methods
    return {
        initialize: initialize,
        showLoadingAnimation: showLoadingAnimation,
        hideLoadingAnimation: hideLoadingAnimation,
        updateAnalysisStage: updateAnalysisStage,
        displayFileInfo: displayFileInfo,
        hideFileInfo: hideFileInfo,
        showResults: showResults,
        hideResults: hideResults,
        showError: showError,
        showModal: showModal,
        closeModal: closeModal,
        closeAllModals: closeAllModals,
        showProcessModal: showProcessModal,
