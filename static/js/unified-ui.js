// unified-ui.js - Complete UI Management for AI Detection & Plagiarism Check
(function() {
    'use strict';
    
    // Initialize namespace
    window.UnifiedApp = window.UnifiedApp || {};
    window.UnifiedApp.ui = {};
    
    // UI State management
    let uiState = {
        currentTab: 'url',
        isAnalyzing: false,
        selectedFile: null,
        dragCounter: 0
    };
    
    // Initialize all UI components
    window.UnifiedApp.ui.init = function() {
        console.log('Initializing Unified UI...');
        
        // Initialize input tabs
        initializeInputTabs();
        
        // Initialize file upload
        initializeFileUpload();
        
        // Initialize text counter
        initializeTextCounter();
        
        // Initialize tooltips
        initializeTooltips();
        
        // Initialize keyboard shortcuts
        initializeKeyboardShortcuts();
        
        // Initialize modal handlers
        initializeModals();
        
        // Initialize copy buttons
        initializeCopyButtons();
        
        // Initialize expand/collapse sections
        initializeCollapsibleSections();
        
        // Initialize smooth scrolling
        initializeSmoothScrolling();
        
        // Initialize theme switcher if present
        initializeThemeSwitcher();
        
        // Initialize progress animations
        initializeProgressAnimations();
        
        console.log('Unified UI initialized successfully');
    };
    
    // Initialize input tabs
    function initializeInputTabs() {
        const tabs = document.querySelectorAll('.input-tab');
        const panels = document.querySelectorAll('.input-panel');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const targetTab = this.dataset.tab;
                
                // Update active states
                tabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                
                // Update panels
                panels.forEach(panel => {
                    if (panel.id === targetTab + '-panel') {
                        panel.classList.add('active');
                        fadeIn(panel);
                    } else {
                        panel.classList.remove('active');
                    }
                });
                
                // Update state
                uiState.currentTab = targetTab;
                
                // Focus appropriate input
                focusTabInput(targetTab);
            });
        });
    }
    
    // Focus input based on tab
    function focusTabInput(tab) {
        setTimeout(() => {
            if (tab === 'url') {
                const urlInput = document.getElementById('url-input');
                if (urlInput) urlInput.focus();
            } else if (tab === 'text') {
                const textInput = document.getElementById('text-input');
                if (textInput) textInput.focus();
            }
        }, 100);
    }
    
    // Initialize file upload with drag and drop
    function initializeFileUpload() {
        const fileUploadArea = document.getElementById('file-upload-area');
        const fileInput = document.getElementById('file-input');
        const filePreview = document.getElementById('file-preview');
        const fileAnalyzeButton = document.getElementById('file-analyze-button');
        
        if (!fileUploadArea || !fileInput) return;
        
        // Click to upload
        fileUploadArea.addEventListener('click', (e) => {
            if (e.target === fileUploadArea || e.target.parentElement === fileUploadArea) {
                fileInput.click();
            }
        });
        
        // Drag and drop events
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            fileUploadArea.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        // Highlight drop area
        ['dragenter', 'dragover'].forEach(eventName => {
            fileUploadArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            fileUploadArea.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight(e) {
            fileUploadArea.classList.add('dragover');
        }
        
        function unhighlight(e) {
            fileUploadArea.classList.remove('dragover');
        }
        
        // Handle dropped files
        fileUploadArea.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                handleFileSelect(files[0]);
            }
        }
        
        // Handle file selection
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });
        
        function handleFileSelect(file) {
            const allowedTypes = ['.pdf', '.doc', '.docx', '.txt'];
            const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
            
            if (!allowedTypes.includes(fileExtension)) {
                UnifiedApp.ui.showToast('Please upload a PDF, DOC, DOCX, or TXT file.', 'error');
                return;
            }
            
            if (file.size > 10 * 1024 * 1024) { // 10MB
                UnifiedApp.ui.showToast('File size must be less than 10MB.', 'error');
                return;
            }
            
            // Store file
            uiState.selectedFile = file;
            window.selectedFile = file; // For compatibility
            
            // Show preview with animation
            if (filePreview) {
                filePreview.innerHTML = `
                    <div class="file-preview-content">
                        <div class="file-icon">
                            <i class="fas fa-file-${getFileIcon(fileExtension)}"></i>
                        </div>
                        <div class="file-info">
                            <div class="file-name">${file.name}</div>
                            <div class="file-size">${formatFileSize(file.size)}</div>
                        </div>
                        <button class="file-remove" onclick="UnifiedApp.ui.clearFileUpload()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                `;
                filePreview.style.display = 'block';
                fadeIn(filePreview);
            }
            
            // Enable analyze button
            if (fileAnalyzeButton) {
                fileAnalyzeButton.disabled = false;
                fileAnalyzeButton.classList.add('pulse');
            }
            
            // Update upload area
            fileUploadArea.innerHTML = `
                <i class="fas fa-check-circle" style="color: #27ae60;"></i>
                <p>File ready for analysis</p>
                <small>Click to change file</small>
            `;
        }
    }
    
    // Get appropriate file icon
    function getFileIcon(extension) {
        const iconMap = {
            '.pdf': 'pdf',
            '.doc': 'word',
            '.docx': 'word',
            '.txt': 'alt'
        };
        return iconMap[extension] || 'file';
    }
    
    // Format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Clear file upload
    window.UnifiedApp.ui.clearFileUpload = function() {
        const fileInput = document.getElementById('file-input');
        const filePreview = document.getElementById('file-preview');
        const fileAnalyzeButton = document.getElementById('file-analyze-button');
        const fileUploadArea = document.getElementById('file-upload-area');
        
        if (fileInput) fileInput.value = '';
        if (filePreview) {
            fadeOut(filePreview, () => {
                filePreview.style.display = 'none';
                filePreview.innerHTML = '';
            });
        }
        if (fileAnalyzeButton) {
            fileAnalyzeButton.disabled = true;
            fileAnalyzeButton.classList.remove('pulse');
        }
        if (fileUploadArea) {
            fileUploadArea.innerHTML = `
                <i class="fas fa-cloud-upload-alt"></i>
                <p>Click to upload or drag and drop documents here</p>
                <small>Supported formats: PDF, DOC, DOCX, TXT (Max 10MB)</small>
            `;
        }
        
        uiState.selectedFile = null;
        window.selectedFile = null;
    };
    
    // Initialize text counter
    function initializeTextCounter() {
        const textInput = document.getElementById('text-input');
        if (!textInput) return;
        
        // Create counter element
        const counter = document.createElement('div');
        counter.className = 'text-counter';
        counter.innerHTML = '<span class="char-count">0</span> characters | <span class="word-count">0</span> words';
        
        // Insert after text input
        textInput.parentNode.insertBefore(counter, textInput.nextSibling);
        
        // Update counter on input
        textInput.addEventListener('input', updateTextCounter);
        
        function updateTextCounter() {
            const text = textInput.value;
            const charCount = text.length;
            const wordCount = text.trim().split(/\s+/).filter(word => word.length > 0).length;
            
            counter.querySelector('.char-count').textContent = charCount.toLocaleString();
            counter.querySelector('.word-count').textContent = wordCount.toLocaleString();
            
            // Update color based on length
            if (charCount < 50) {
                counter.style.color = '#e74c3c';
            } else if (charCount < 100) {
                counter.style.color = '#f39c12';
            } else {
                counter.style.color = '#27ae60';
            }
        }
        
        // Add styles
        if (!document.getElementById('text-counter-styles')) {
            const styles = document.createElement('style');
            styles.id = 'text-counter-styles';
            styles.textContent = `
                .text-counter {
                    margin-top: 8px;
                    font-size: 0.85em;
                    color: #7f8c8d;
                    text-align: right;
                    transition: color 0.3s ease;
                }
            `;
            document.head.appendChild(styles);
        }
    }
    
    // Show loading overlay
    window.UnifiedApp.ui.showLoading = function() {
        // Hide input section with fade
        const inputSection = document.getElementById('input-section');
        if (inputSection) {
            fadeOut(inputSection, () => {
                inputSection.style.display = 'none';
            });
        }
        
        // Show progress container with fade
        const progressContainer = document.getElementById('progress-container');
        if (progressContainer) {
            progressContainer.style.display = 'block';
            fadeIn(progressContainer);
            
            // Reset progress bar
            const progressBar = document.getElementById('progress-bar');
            if (progressBar) {
                progressBar.style.width = '0%';
                progressBar.textContent = '0%';
            }
            
            // Reset step indicators
            const steps = document.querySelectorAll('.progress-step');
            steps.forEach(step => {
                step.classList.remove('active', 'complete');
            });
            
            // Start initial animation
            setTimeout(() => {
                if (progressBar) {
                    progressBar.style.width = '5%';
                    progressBar.textContent = '5%';
                }
            }, 100);
        }
        
        uiState.isAnalyzing = true;
    };
    
    // Hide loading overlay
    window.UnifiedApp.ui.hideLoading = function() {
        const progressContainer = document.getElementById('progress-container');
        if (progressContainer) {
            // Ensure we're at 100%
            const progressBar = document.getElementById('progress-bar');
            if (progressBar) {
                progressBar.style.width = '100%';
                progressBar.textContent = '100%';
            }
            
            // Mark all steps complete
            const steps = document.querySelectorAll('.progress-step');
            steps.forEach(step => {
                step.classList.remove('active');
                step.classList.add('complete');
            });
            
            // Hide after delay
            setTimeout(() => {
                fadeOut(progressContainer, () => {
                    progressContainer.style.display = 'none';
                });
            }, 500);
        }
        
        // Show input section
        const inputSection = document.getElementById('input-section');
        if (inputSection) {
            setTimeout(() => {
                inputSection.style.display = 'block';
                fadeIn(inputSection);
            }, 300);
        }
        
        uiState.isAnalyzing = false;
    };
    
    // Update progress with enhanced animations
    window.UnifiedApp.ui.updateProgress = function(message, progress) {
        const progressBar = document.getElementById('progress-bar');
        const progressHeader = document.querySelector('.progress-header h5');
        
        if (progressBar) {
            // Smooth progress update
            const currentProgress = parseInt(progressBar.style.width) || 0;
            if (progress > currentProgress) {
                progressBar.style.width = progress + '%';
                progressBar.textContent = progress + '%';
                
                // Add pulse effect at milestones
                if (progress === 25 || progress === 50 || progress === 75 || progress === 100) {
                    progressBar.classList.add('pulse');
                    setTimeout(() => progressBar.classList.remove('pulse'), 600);
                }
            }
        }
        
        if (progressHeader && message) {
            // Fade transition for message updates
            progressHeader.style.opacity = '0';
            setTimeout(() => {
                progressHeader.innerHTML = `
                    <i class="fas fa-brain fa-pulse me-2 text-primary"></i>
                    ${message}
                `;
                progressHeader.style.opacity = '1';
            }, 200);
        }
        
        // Update step indicators
        updateProgressSteps(progress);
    };
    
    // Update progress steps with animations
    function updateProgressSteps(progress) {
        const steps = [
            { id: 'step-1', threshold: 10, label: 'Extracting' },
            { id: 'step-2', threshold: 25, label: 'AI Detection' },
            { id: 'step-3', threshold: 40, label: 'Pattern Analysis' },
            { id: 'step-4', threshold: 60, label: 'Plagiarism Check' },
            { id: 'step-5', threshold: 80, label: 'Quality Analysis' },
            { id: 'step-6', threshold: 90, label: 'Generating Report' }
        ];
        
        steps.forEach((step, index) => {
            const element = document.getElementById(step.id);
            if (element) {
                if (progress >= step.threshold) {
                    if (!element.classList.contains('active') && !element.classList.contains('complete')) {
                        element.classList.add('active');
                        // Add animation
                        element.style.transform = 'scale(1.2)';
                        setTimeout(() => {
                            element.style.transform = 'scale(1)';
                        }, 300);
                    }
                    
                    // Mark previous steps as complete
                    if (index > 0 && progress > step.threshold + 10) {
                        const prevElement = document.getElementById(steps[index - 1].id);
                        if (prevElement && prevElement.classList.contains('active')) {
                            prevElement.classList.remove('active');
                            prevElement.classList.add('complete');
                        }
                    }
                }
            }
        });
    }
    
    // Show error message with enhanced styling
    window.UnifiedApp.ui.showError = function(message) {
        // Hide progress
        const progressContainer = document.getElementById('progress-container');
        if (progressContainer) {
            fadeOut(progressContainer, () => {
                progressContainer.style.display = 'none';
            });
        }
        
        // Show error container
        const errorContainer = document.getElementById('error-container');
        const errorMessage = document.getElementById('error-message');
        
        if (errorContainer && errorMessage) {
            errorMessage.textContent = message;
            errorContainer.style.display = 'block';
            fadeIn(errorContainer);
            
            // Shake animation
            errorContainer.classList.add('shake');
            setTimeout(() => errorContainer.classList.remove('shake'), 600);
            
            errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            // Fallback to toast
            UnifiedApp.ui.showToast(message, 'error');
        }
        
        // Show input section
        const inputSection = document.getElementById('input-section');
        if (inputSection) {
            inputSection.style.display = 'block';
            fadeIn(inputSection);
        }
        
        uiState.isAnalyzing = false;
    };
    
    // Show toast notification with enhanced animations
    window.UnifiedApp.ui.showToast = function(message, type = 'info', duration = null) {
        // Remove any existing toasts
        const existingToasts = document.querySelectorAll('.ff-toast');
        existingToasts.forEach(toast => {
            toast.style.animation = 'ff-slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        });
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `ff-toast ff-toast-${type}`;
        
        // Set icon based on type
        let icon = 'fa-info-circle';
        if (type === 'success') icon = 'fa-check-circle';
        else if (type === 'warning') icon = 'fa-exclamation-triangle';
        else if (type === 'error') icon = 'fa-times-circle';
        
        toast.innerHTML = `
            <i class="fas ${icon}"></i>
            <span>${message}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add enhanced styles if not already present
        if (!document.getElementById('ff-toast-styles')) {
            const styles = document.createElement('style');
            styles.id = 'ff-toast-styles';
            styles.textContent = `
                .ff-toast {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    padding: 16px 24px;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    font-size: 16px;
                    z-index: 9999;
                    animation: ff-slideIn 0.3s ease;
                    max-width: 400px;
                    min-width: 250px;
                }
                
                .ff-toast i {
                    font-size: 20px;
                    flex-shrink: 0;
                }
                
                .ff-toast span {
                    flex: 1;
                }
                
                .toast-close {
                    background: none;
                    border: none;
                    color: #999;
                    cursor: pointer;
                    padding: 4px;
                    margin-left: 8px;
                    transition: color 0.2s;
                }
                
                .toast-close:hover {
                    color: #333;
                }
                
                .ff-toast-info {
                    border-left: 4px solid #4a90e2;
                }
                
                .ff-toast-info i {
                    color: #4a90e2;
                }
                
                .ff-toast-success {
                    border-left: 4px solid #27ae60;
                    background: #f0fdf4;
                }
                
                .ff-toast-success i {
                    color: #27ae60;
                }
                
                .ff-toast-warning {
                    border-left: 4px solid #f39c12;
                    background: #fffbeb;
                }
                
                .ff-toast-warning i {
                    color: #f39c12;
                }
                
                .ff-toast-error {
                    border-left: 4px solid #e74c3c;
                    background: #fef2f2;
                }
                
                .ff-toast-error i {
                    color: #e74c3c;
                }
                
                @keyframes ff-slideIn {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
                
                @keyframes ff-slideOut {
                    from {
                        transform: translateX(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                }
                
                .shake {
                    animation: shake 0.6s;
                }
                
                @keyframes shake {
                    0%, 100% { transform: translateX(0); }
                    10%, 30%, 50%, 70%, 90% { transform: translateX(-10px); }
                    20%, 40%, 60%, 80% { transform: translateX(10px); }
                }
                
                .pulse {
                    animation: pulse 0.6s;
                }
                
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                    100% { transform: scale(1); }
                }
                
                @media (max-width: 768px) {
                    .ff-toast {
                        left: 20px;
                        right: 20px;
                        bottom: 60px;
                        max-width: none;
                    }
                }
            `;
            document.head.appendChild(styles);
        }
        
        // Add toast to page
        document.body.appendChild(toast);
        
        // Auto-remove after delay
        const displayDuration = duration || (type === 'error' ? 5000 : 3000);
        setTimeout(() => {
            if (toast.parentElement) {
                toast.style.animation = 'ff-slideOut 0.3s ease';
                setTimeout(() => toast.remove(), 300);
            }
        }, displayDuration);
    };
    
    // Initialize tooltips
    function initializeTooltips() {
        // Create tooltip container
        let tooltipContainer = document.getElementById('ff-tooltip-container');
        if (!tooltipContainer) {
            tooltipContainer = document.createElement('div');
            tooltipContainer.id = 'ff-tooltip-container';
            tooltipContainer.style.cssText = `
                position: absolute;
                background: #333;
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 14px;
                z-index: 10000;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.2s;
                white-space: nowrap;
                max-width: 300px;
            `;
            document.body.appendChild(tooltipContainer);
        }
        
        // Add tooltip arrow
        const arrow = document.createElement('div');
        arrow.style.cssText = `
            position: absolute;
            width: 0;
            height: 0;
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-top: 6px solid #333;
            bottom: -6px;
            left: 50%;
            transform: translateX(-50%);
        `;
        tooltipContainer.appendChild(arrow);
        
        // Initialize all elements with data-tooltip
        document.addEventListener('mouseover', function(e) {
            const element = e.target.closest('[data-tooltip]');
            if (element) {
                const text = element.getAttribute('data-tooltip');
                tooltipContainer.textContent = text;
                tooltipContainer.appendChild(arrow);
                
                const rect = element.getBoundingClientRect();
                const tooltipRect = tooltipContainer.getBoundingClientRect();
                
                tooltipContainer.style.left = rect.left + (rect.width / 2) - (tooltipRect.width / 2) + 'px';
                tooltipContainer.style.top = rect.top - tooltipRect.height - 10 + 'px';
                tooltipContainer.style.opacity = '1';
            }
        });
        
        document.addEventListener('mouseout', function(e) {
            const element = e.target.closest('[data-tooltip]');
            if (element) {
                tooltipContainer.style.opacity = '0';
            }
        });
    }
    
    // Initialize keyboard shortcuts
    function initializeKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + Enter to analyze
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                const activeTab = uiState.currentTab;
                
                if (activeTab === 'url') {
                    const urlButton = document.getElementById('analyze-url-button');
                    if (urlButton && !urlButton.disabled) urlButton.click();
                } else if (activeTab === 'text') {
                    const textButton = document.getElementById('analyze-text-button');
                    if (textButton && !textButton.disabled) textButton.click();
                } else if (activeTab === 'file') {
                    const fileButton = document.getElementById('file-analyze-button');
                    if (fileButton && !fileButton.disabled) fileButton.click();
                }
            }
            
            // Escape to close modals
            if (e.key === 'Escape') {
                closeActiveModal();
            }
            
            // Tab to switch between input types
            if (e.key === 'Tab' && !e.shiftKey && !uiState.isAnalyzing) {
                const activeElement = document.activeElement;
                if (activeElement.tagName !== 'INPUT' && activeElement.tagName !== 'TEXTAREA') {
                    e.preventDefault();
                    switchToNextTab();
                }
            }
        });
    }
    
    // Switch to next input tab
    function switchToNextTab() {
        const tabs = ['url', 'text', 'file'];
        const currentIndex = tabs.indexOf(uiState.currentTab);
        const nextIndex = (currentIndex + 1) % tabs.length;
        const nextTab = tabs[nextIndex];
        
        const tabElement = document.querySelector(`.input-tab[data-tab="${nextTab}"]`);
        if (tabElement) tabElement.click();
    }
    
    // Initialize modals
    function initializeModals() {
        // Close modal on backdrop click
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('modal')) {
                closeActiveModal();
            }
        });
        
        // Close buttons
        const closeButtons = document.querySelectorAll('.modal .btn-close, .modal .close');
        closeButtons.forEach(button => {
            button.addEventListener('click', closeActiveModal);
        });
    }
    
    // Close active modal
    function closeActiveModal() {
        const activeModal = document.querySelector('.modal.show');
        if (activeModal) {
            activeModal.classList.remove('show');
            setTimeout(() => {
                activeModal.style.display = 'none';
            }, 300);
        }
        
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
            backdrop.classList.remove('show');
            setTimeout(() => backdrop.remove(), 300);
        }
    }
    
    // Initialize copy buttons
    function initializeCopyButtons() {
        document.addEventListener('click', function(e) {
            if (e.target.matches('[data-copy]') || e.target.closest('[data-copy]')) {
                const button = e.target.closest('[data-copy]');
                const targetId = button.getAttribute('data-copy');
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    const text = targetElement.textContent || targetElement.value;
                    copyToClipboard(text);
                    
                    // Show feedback
                    const originalText = button.innerHTML;
                    button.innerHTML = '<i class="fas fa-check"></i> Copied!';
                    button.classList.add('copied');
                    
                    setTimeout(() => {
                        button.innerHTML = originalText;
                        button.classList.remove('copied');
                    }, 2000);
                }
            }
        });
    }
    
    // Copy to clipboard
    function copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                UnifiedApp.ui.showToast('Copied to clipboard!', 'success');
            }).catch(() => {
                fallbackCopy(text);
            });
        } else {
            fallbackCopy(text);
        }
    }
    
    // Fallback copy method
    function fallbackCopy(text) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        
        try {
            document.execCommand('copy');
            UnifiedApp.ui.showToast('Copied to clipboard!', 'success');
        } catch (err) {
            UnifiedApp.ui.showToast('Failed to copy', 'error');
        }
        
        document.body.removeChild(textarea);
    }
    
    // Initialize collapsible sections
    function initializeCollapsibleSections() {
        const toggles = document.querySelectorAll('[data-toggle="collapse"]');
        
        toggles.forEach(toggle => {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('data-target');
                const target = document.querySelector(targetId);
                
                if (target) {
                    if (target.classList.contains('show')) {
                        collapseElement(target);
                        this.classList.remove('active');
                    } else {
                        expandElement(target);
                        this.classList.add('active');
                    }
                }
            });
        });
    }
    
    // Expand element with animation
    function expandElement(element) {
        element.style.height = '0px';
        element.style.overflow = 'hidden';
        element.classList.add('show');
        
        const height = element.scrollHeight;
        element.style.transition = 'height 0.3s ease';
        element.style.height = height + 'px';
        
        setTimeout(() => {
            element.style.height = 'auto';
            element.style.overflow = '';
        }, 300);
    }
    
    // Collapse element with animation
    function collapseElement(element) {
        element.style.height = element.scrollHeight + 'px';
        element.style.overflow = 'hidden';
        element.style.transition = 'height 0.3s ease';
        
        setTimeout(() => {
            element.style.height = '0px';
        }, 10);
        
        setTimeout(() => {
            element.classList.remove('show');
            element.style.height = '';
            element.style.overflow = '';
        }, 300);
    }
    
    // Initialize smooth scrolling
    function initializeSmoothScrolling() {
        document.addEventListener('click', function(e) {
            const link = e.target.closest('a[href^="#"]');
            if (link) {
                const targetId = link.getAttribute('href');
                if (targetId === '#') return;
                
                const target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    smoothScrollTo(target);
                }
            }
        });
    }
    
    // Smooth scroll to element
    function smoothScrollTo(element) {
        const headerHeight = 80; // Account for fixed header
        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerHeight;
        
        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }
    
    // Initialize theme switcher
    function initializeThemeSwitcher() {
        const themeSwitcher = document.getElementById('theme-switcher');
        if (!themeSwitcher) return;
        
        // Load saved theme
        const savedTheme = localStorage.getItem('ff-theme') || 'light';
        document.body.setAttribute('data-theme', savedTheme);
        
        themeSwitcher.addEventListener('click', function() {
            const currentTheme = document.body.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            document.body.setAttribute('data-theme', newTheme);
            localStorage.setItem('ff-theme', newTheme);
            
            // Update icon
            const icon = this.querySelector('i');
            if (icon) {
                icon.className = newTheme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
            }
            
            // Animate transition
            document.body.style.transition = 'background-color 0.3s, color 0.3s';
        });
    }
    
    // Initialize progress animations
    function initializeProgressAnimations() {
        // Add CSS for progress animations if not present
        if (!document.getElementById('progress-animations')) {
            const styles = document.createElement('style');
            styles.id = 'progress-animations';
            styles.textContent = `
                .progress-step {
                    transition: all 0.3s ease;
                }
                
                .progress-step.active {
                    transform: scale(1.1);
                }
                
                .progress-step.complete i {
                    color: #27ae60;
                }
                
                .progress-bar {
                    position: relative;
                    overflow: hidden;
                }
                
                .progress-bar::after {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    bottom: 0;
                    right: 0;
                    background: linear-gradient(
                        90deg,
                        transparent,
                        rgba(255, 255, 255, 0.3),
                        transparent
                    );
                    animation: shimmer 2s infinite;
                }
                
                @keyframes shimmer {
                    0% { transform: translateX(-100%); }
                    100% { transform: translateX(100%); }
                }
            `;
            document.head.appendChild(styles);
        }
    }
    
    // Utility functions
    function fadeIn(element, callback) {
        element.style.opacity = '0';
        element.style.display = 'block';
        
        setTimeout(() => {
            element.style.transition = 'opacity 0.3s ease';
            element.style.opacity = '1';
            
            if (callback) {
                setTimeout(callback, 300);
            }
        }, 10);
    }
    
    function fadeOut(element, callback) {
        element.style.transition = 'opacity 0.3s ease';
        element.style.opacity = '0';
        
        setTimeout(() => {
            element.style.display = 'none';
            if (callback) callback();
        }, 300);
    }
    
    // Format number with commas
    window.UnifiedApp.ui.formatNumber = function(num) {
        return new Intl.NumberFormat().format(num);
    };
    
    // Format percentage
    window.UnifiedApp.ui.formatPercentage = function(num, decimals = 0) {
        return num.toFixed(decimals) + '%';
    };
    
    // Format date
    window.UnifiedApp.ui.formatDate = function(date) {
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(date));
    };
    
    // Debounce function
    window.UnifiedApp.ui.debounce = function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };
    
    // Throttle function
    window.UnifiedApp.ui.throttle = function(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    };
    
    // Show partial results during streaming
    window.UnifiedApp.ui.showPartialResults = function(partialData) {
        if (window.UnifiedApp.results && window.UnifiedApp.results.showPartialResults) {
            window.UnifiedApp.results.showPartialResults(partialData);
        }
    };
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', window.UnifiedApp.ui.init);
    } else {
        window.UnifiedApp.ui.init();
    }
    
    console.log('Unified UI module loaded - Complete enhanced version');
})();
