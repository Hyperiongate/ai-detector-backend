/**
 * Facts & Fakes AI - Unified Analysis Main Module
 * Multi-modal content analysis coordinator
 */

// Initialize the UnifiedApp namespace
window.UnifiedApp = {
    // Module references (will be populated by other modules)
    analysis: null,
    ui: null,
    results: null,
    helpers: null,
    
    // Application state
    state: {
        isAnalyzing: false,
        currentAnalysis: null,
        uploadedFiles: {
            text: null,
            image: null
        },
        inputData: {
            textContent: '',
            urlContent: '',
            imageFile: null
        },
        lastResults: null,
        currentTier: 'free'
    },
    
    // Configuration
    config: {
        maxFileSize: 50 * 1024 * 1024, // 50MB
        supportedImageTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'],
        supportedTextTypes: ['text/plain', 'text/html'],
        apiEndpoint: '/api/analyze-unified',
        progressStages: [
            { id: 'stage1', text: 'Processing Input', progress: 16 },
            { id: 'stage2', text: 'AI Analysis', progress: 33 },
            { id: 'stage3', text: 'Content Verification', progress: 50 },
            { id: 'stage4', text: 'Bias Detection', progress: 66 },
            { id: 'stage5', text: 'Authenticity Check', progress: 83 },
            { id: 'stage6', text: 'Finalizing Report', progress: 100 }
        ]
    },
    
    /**
     * Initialize the unified analysis application
     */
    init() {
        console.log('Initializing Unified Analysis App...');
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.onDOMReady());
        } else {
            this.onDOMReady();
        }
    },
    
    /**
     * Handle DOM ready event
     */
    onDOMReady() {
        try {
            // Initialize UI components
            this.initializeComponents();
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Initialize drag and drop
            this.initializeDragDrop();
            
            // Check authentication status
            this.checkAuthStatus();
            
            // Initialize floating particles background
            if (this.ui && this.ui.initializeParticles) {
                this.ui.initializeParticles();
            }
            
            console.log('Unified Analysis App initialized successfully');
            
        } catch (error) {
            console.error('Error initializing Unified Analysis App:', error);
        }
    },
    
    /**
     * Initialize UI components
     */
    initializeComponents() {
        // Initialize input areas
        const textArea = document.getElementById('unifiedTextInput');
        const urlInput = document.getElementById('unifiedUrlInput');
        const imageDropzone = document.getElementById('unifiedImageDropzone');
        
        if (textArea) {
            textArea.addEventListener('input', (e) => {
                this.state.inputData.textContent = e.target.value;
                this.updateAnalyzeButtonState();
            });
        }
        
        if (urlInput) {
            urlInput.addEventListener('input', (e) => {
                this.state.inputData.urlContent = e.target.value;
                this.updateAnalyzeButtonState();
            });
        }
        
        // Initialize file input
        const fileInput = document.getElementById('unifiedImageInput');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    this.handleImageFile(e.target.files[0]);
                }
            });
        }
        
        // Initialize analyze button
        this.updateAnalyzeButtonState();
    },
    
    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'Enter':
                        e.preventDefault();
                        if (!this.state.isAnalyzing) {
                            this.startAnalysis();
                        }
                        break;
                    case 'r':
                        e.preventDefault();
                        this.resetAnalysis();
                        break;
                }
            }
        });
        
        // Modal close handlers
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                this.closeAllModals();
            }
        });
        
        // Escape key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    },
    
    /**
     * Initialize drag and drop functionality
     */
    initializeDragDrop() {
        const dropzone = document.getElementById('unifiedImageDropzone');
        if (!dropzone) return;
        
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });
        
        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, () => this.highlight(dropzone), false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, () => this.unhighlight(dropzone), false);
        });
        
        // Handle dropped files
        dropzone.addEventListener('drop', (e) => this.handleDrop(e), false);
    },
    
    /**
     * Prevent default drag behaviors
     */
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    },
    
    /**
     * Highlight dropzone
     */
    highlight(dropzone) {
        dropzone.classList.add('drag-over');
    },
    
    /**
     * Remove highlight from dropzone
     */
    unhighlight(dropzone) {
        dropzone.classList.remove('drag-over');
    },
    
    /**
     * Handle file drop
     */
    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            this.handleImageFile(files[0]);
        }
    },
    
    /**
     * Handle image file selection
     */
    handleImageFile(file) {
        // Validate file type
        if (!this.config.supportedImageTypes.includes(file.type)) {
            if (this.helpers && this.helpers.showToast) {
                this.helpers.showToast('Please select a valid image file (JPG, PNG, GIF, WebP, BMP)', 'error');
            }
            return;
        }
        
        // Validate file size
        if (file.size > this.config.maxFileSize) {
            if (this.helpers && this.helpers.showToast) {
                this.helpers.showToast('File size must be less than 50MB', 'error');
            }
            return;
        }
        
        // Store the file
        this.state.inputData.imageFile = file;
        
        // Update UI
        this.updateImagePreview(file);
        this.updateAnalyzeButtonState();
        
        console.log('Image file selected:', file.name);
    },
    
    /**
     * Update image preview
     */
    updateImagePreview(file) {
        const dropzone = document.getElementById('unifiedImageDropzone');
        const preview = document.getElementById('unifiedImagePreview');
        const fileName = document.getElementById('unifiedImageFileName');
        
        if (dropzone && preview && fileName) {
            // Show preview
            const reader = new FileReader();
            reader.onload = (e) => {
                preview.src = e.target.result;
                preview.style.display = 'block';
                fileName.textContent = file.name;
                fileName.style.display = 'block';
                
                // Update dropzone appearance
                dropzone.classList.add('has-file');
            };
            reader.readAsDataURL(file);
        }
    },
    
    /**
     * Update analyze button state based on input
     */
    updateAnalyzeButtonState() {
        const analyzeBtn = document.getElementById('unifiedAnalyzeBtn');
        if (!analyzeBtn) return;
        
        const hasText = this.state.inputData.textContent.trim().length > 0;
        const hasUrl = this.state.inputData.urlContent.trim().length > 0;
        const hasImage = this.state.inputData.imageFile !== null;
        
        const hasInput = hasText || hasUrl || hasImage;
        
        analyzeBtn.disabled = !hasInput || this.state.isAnalyzing;
        
        // Update button text based on input types
        if (hasText && hasUrl && hasImage) {
            analyzeBtn.innerHTML = '<i class="fas fa-cogs"></i> Analyze All Content';
        } else if (hasText && hasImage) {
            analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Text & Image';
        } else if (hasUrl && hasImage) {
            analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze URL & Image';
        } else if (hasText && hasUrl) {
            analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Text & URL';
        } else if (hasText) {
            analyzeBtn.innerHTML = '<i class="fas fa-font"></i> Analyze Text';
        } else if (hasUrl) {
            analyzeBtn.innerHTML = '<i class="fas fa-link"></i> Analyze URL';
        } else if (hasImage) {
            analyzeBtn.innerHTML = '<i class="fas fa-image"></i> Analyze Image';
        } else {
            analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Start Analysis';
        }
    },
    
    /**
     * Check authentication status
     */
    async checkAuthStatus() {
        try {
            if (window.ffAPI && window.ffAPI.getUserStatus) {
                const status = await window.ffAPI.getUserStatus();
                this.state.currentTier = status.tier || 'free';
                console.log('User tier:', this.state.currentTier);
            }
        } catch (error) {
            console.log('Auth check failed, assuming free tier');
            this.state.currentTier = 'free';
        }
    },
    
    /**
     * Start unified analysis
     */
    async startAnalysis(tier = null) {
        if (this.state.isAnalyzing) return;
        
        // Use provided tier or current user tier
        const analysisTier = tier || this.state.currentTier;
        
        try {
            // Validate input
            if (!this.validateInput()) {
                return;
            }
            
            // Start analysis
            this.state.isAnalyzing = true;
            this.updateAnalyzeButtonState();
            
            if (this.analysis && this.analysis.runAnalysis) {
                await this.analysis.runAnalysis(this.state.inputData, analysisTier);
            } else {
                console.error('Analysis module not loaded');
            }
            
        } catch (error) {
            console.error('Analysis failed:', error);
            if (this.ui && this.ui.showError) {
                this.ui.showError('Analysis failed. Please try again.');
            }
        } finally {
            this.state.isAnalyzing = false;
            this.updateAnalyzeButtonState();
        }
    },
    
    /**
     * Validate input before analysis
     */
    validateInput() {
        const hasText = this.state.inputData.textContent.trim().length > 0;
        const hasUrl = this.state.inputData.urlContent.trim().length > 0;
        const hasImage = this.state.inputData.imageFile !== null;
        
        if (!hasText && !hasUrl && !hasImage) {
            if (this.helpers && this.helpers.showToast) {
                this.helpers.showToast('Please provide at least one type of content to analyze', 'warning');
            }
            return false;
        }
        
        // Validate URL format if provided
        if (hasUrl && !this.helpers.isValidUrl(this.state.inputData.urlContent)) {
            if (this.helpers && this.helpers.showToast) {
                this.helpers.showToast('Please enter a valid URL', 'error');
            }
            return false;
        }
        
        return true;
    },
    
    /**
     * Reset analysis form
     */
    resetAnalysis() {
        if (this.state.isAnalyzing) return;
        
        // Clear input data
        this.state.inputData = {
            textContent: '',
            urlContent: '',
            imageFile: null
        };
        
        // Clear form elements
        const textArea = document.getElementById('unifiedTextInput');
        const urlInput = document.getElementById('unifiedUrlInput');
        const fileInput = document.getElementById('unifiedImageInput');
        const dropzone = document.getElementById('unifiedImageDropzone');
        const preview = document.getElementById('unifiedImagePreview');
        const fileName = document.getElementById('unifiedImageFileName');
        
        if (textArea) textArea.value = '';
        if (urlInput) urlInput.value = '';
        if (fileInput) fileInput.value = '';
        
        if (dropzone) dropzone.classList.remove('has-file');
        if (preview) preview.style.display = 'none';
        if (fileName) fileName.style.display = 'none';
        
        // Hide results
        const resultsContainer = document.getElementById('unifiedResults');
        if (resultsContainer) {
            resultsContainer.style.display = 'none';
        }
        
        // Update button state
        this.updateAnalyzeButtonState();
        
        console.log('Analysis form reset');
    },
    
    /**
     * Close all modals
     */
    closeAllModals() {
        const modals = document.querySelectorAll('.modal-overlay');
        modals.forEach(modal => {
            modal.style.display = 'none';
        });
    }
};

// Global functions for HTML onclick handlers
window.analyzeUnified = function(tier = null) {
    if (window.UnifiedApp) {
        window.UnifiedApp.startAnalysis(tier);
    }
};

window.resetUnifiedAnalysis = function() {
    if (window.UnifiedApp) {
        window.UnifiedApp.resetAnalysis();
    }
};

window.shareUnifiedResults = function() {
    if (window.UnifiedApp && window.UnifiedApp.ui && window.UnifiedApp.ui.showShareModal) {
        window.UnifiedApp.ui.showShareModal();
    }
};

window.downloadUnifiedPDF = function() {
    if (window.UnifiedApp && window.UnifiedApp.helpers && window.UnifiedApp.helpers.generatePDF) {
        window.UnifiedApp.helpers.generatePDF();
    }
};

window.removeUnifiedImageFile = function() {
    if (window.UnifiedApp) {
        window.UnifiedApp.state.inputData.imageFile = null;
        window.UnifiedApp.updateAnalyzeButtonState();
        
        // Update UI
        const dropzone = document.getElementById('unifiedImageDropzone');
        const preview = document.getElementById('unifiedImagePreview');
        const fileName = document.getElementById('unifiedImageFileName');
        const fileInput = document.getElementById('unifiedImageInput');
        
        if (dropzone) dropzone.classList.remove('has-file');
        if (preview) preview.style.display = 'none';
        if (fileName) fileName.style.display = 'none';
        if (fileInput) fileInput.value = '';
    }
};

// Initialize when the script loads
window.UnifiedApp.init();
