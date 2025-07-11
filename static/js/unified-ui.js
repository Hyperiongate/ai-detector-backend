// unified-ui.js - UI Interactions for AI & Plagiarism Detector with Real-Time Updates
(function() {
    'use strict';
    
    // Initialize namespace
    window.UnifiedApp = window.UnifiedApp || {};
    window.UnifiedApp.ui = {};
    
    // Store UI state
    let uiState = {
        partialResultsShown: false,
        progressStages: []
    };
    
    // Loading overlay management
    window.UnifiedApp.ui.showLoading = function() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = 'flex';
        
        // Reset progress
        document.getElementById('progressBar').style.width = '0%';
        document.getElementById('loadingStage').textContent = 'Initializing Analysis...';
        
        // Clear previous stages
        uiState.progressStages = [];
        uiState.partialResultsShown = false;
        
        // Add cancel button if not exists
        addCancelButton();
    };
    
    window.UnifiedApp.ui.hideLoading = function() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = 'none';
        removeCancelButton();
    };
    
    // Update progress with enhanced visuals
    window.UnifiedApp.ui.updateProgress = function(stage, progress) {
        const progressBar = document.getElementById('progressBar');
        const stageText = document.getElementById('loadingStage');
        
        // Update progress bar with smooth transition
        progressBar.style.width = progress + '%';
        
        // Update stage text with fade effect
        stageText.style.opacity = '0';
        setTimeout(() => {
            stageText.textContent = stage;
            stageText.style.opacity = '1';
        }, 200);
        
        // Add to progress history
        uiState.progressStages.push({
            stage: stage,
            progress: progress,
            timestamp: new Date()
        });
        
        // Show stage history
        updateStageHistory();
        
        // Add completion checkmark for finished stages
        if (progress === 100) {
            stageText.innerHTML = `<i class="fas fa-check-circle" style="color: #10b981;"></i> ${stage}`;
        }
    };
    
    // Show partial results during analysis
    window.UnifiedApp.ui.showPartialResults = function(partialResults) {
        if (!uiState.partialResultsShown) {
            createPartialResultsContainer();
            uiState.partialResultsShown = true;
        }
        
        const container = document.getElementById('partialResultsContainer');
        if (!container) return;
        
        let html = '<h4><i class="fas fa-chart-line"></i> Live Analysis Preview</h4>';
        
        // AI Detection Preview
        if (partialResults.ai_indicators) {
            html += `
                <div class="partial-result-item">
                    <span class="label">AI Patterns Detected:</span>
                    <span class="value">${partialResults.ai_indicators.length} indicators</span>
                </div>
            `;
        }
        
        // Plagiarism Preview
        if (partialResults.plagiarism_matches !== undefined) {
            html += `
                <div class="partial-result-item">
                    <span class="label">Potential Matches:</span>
                    <span class="value">${partialResults.plagiarism_matches} sources</span>
                </div>
            `;
        }
        
        // Confidence Preview
        if (partialResults.confidence_level) {
            html += `
                <div class="partial-result-item">
                    <span class="label">Analysis Confidence:</span>
                    <span class="value">${partialResults.confidence_level}%</span>
                </div>
            `;
        }
        
        container.innerHTML = html;
    };
    
    // Create partial results container
    function createPartialResultsContainer() {
        const overlay = document.getElementById('loadingOverlay');
        const container = document.createElement('div');
        container.id = 'partialResultsContainer';
        container.className = 'partial-results-container';
        container.style.cssText = `
            position: absolute;
            bottom: 2rem;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(255, 255, 255, 0.95);
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            min-width: 300px;
            max-width: 500px;
            backdrop-filter: blur(10px);
        `;
        
        overlay.appendChild(container);
    }
    
    // Update stage history display
    function updateStageHistory() {
        let historyContainer = document.getElementById('stageHistory');
        if (!historyContainer) {
            const loadingContent = document.querySelector('.loading-content');
            historyContainer = document.createElement('div');
            historyContainer.id = 'stageHistory';
            historyContainer.className = 'stage-history';
            historyContainer.style.cssText = `
                margin-top: 2rem;
                padding: 1rem;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                max-height: 150px;
                overflow-y: auto;
            `;
            loadingContent.appendChild(historyContainer);
        }
        
        const recentStages = uiState.progressStages.slice(-5);
        historyContainer.innerHTML = recentStages.map(stage => `
            <div class="stage-item" style="
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.25rem 0;
                opacity: 0.8;
                font-size: 0.875rem;
            ">
                <i class="fas fa-check" style="color: #10b981; font-size: 0.75rem;"></i>
                <span>${stage.stage}</span>
            </div>
        `).join('');
    }
    
    // Add cancel analysis button
    function addCancelButton() {
        const loadingContent = document.querySelector('.loading-content');
        if (!document.getElementById('cancelAnalysisBtn')) {
            const cancelBtn = document.createElement('button');
            cancelBtn.id = 'cancelAnalysisBtn';
            cancelBtn.innerHTML = '<i class="fas fa-times-circle"></i> Cancel Analysis';
            cancelBtn.className = 'btn-cancel';
            cancelBtn.style.cssText = `
                margin-top: 1.5rem;
                background: #ef4444;
                color: white;
                border: none;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 500;
                transition: background 0.3s ease;
            `;
            cancelBtn.onclick = () => UnifiedApp.analysis.cancelAnalysis();
            loadingContent.appendChild(cancelBtn);
        }
    }
    
    function removeCancelButton() {
        const cancelBtn = document.getElementById('cancelAnalysisBtn');
        if (cancelBtn) cancelBtn.remove();
        
        const partialResults = document.getElementById('partialResultsContainer');
        if (partialResults) partialResults.remove();
        
        const stageHistory = document.getElementById('stageHistory');
        if (stageHistory) stageHistory.remove();
    }
    
    // Toast notifications (keeping existing implementation)
    window.UnifiedApp.ui.showToast = function(message, type = 'info') {
        // Remove existing toasts
        const existingToast = document.querySelector('.toast-notification');
        if (existingToast) {
            existingToast.remove();
        }
        
        // Create toast
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.innerHTML = `
            <i class="fas ${getToastIcon(type)}"></i>
            <span>${message}</span>
        `;
        
        // Add styles
        toast.style.cssText = `
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: ${getToastColor(type)};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-weight: 500;
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(toast);
        
        // Remove after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    };
    
    // Show error modal (keeping existing implementation)
    window.UnifiedApp.ui.showError = function(message) {
        // Create error modal if it doesn't exist
        let modal = document.getElementById('errorModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'errorModal';
            modal.className = 'modal-overlay';
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h3><i class="fas fa-exclamation-circle"></i> Analysis Error</h3>
                        <button class="modal-close" onclick="UnifiedApp.ui.closeModal('errorModal')">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body" id="errorMessage"></div>
                    <div class="modal-footer">
                        <button class="btn-primary" onclick="UnifiedApp.ui.closeModal('errorModal')">
                            Got it
                        </button>
                    </div>
                </div>
            `;
            
            // Add styles
            modal.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                display: none;
                justify-content: center;
                align-items: center;
                z-index: 10000;
            `;
            
            document.body.appendChild(modal);
        }
        
        // Update message and show
        document.getElementById('errorMessage').textContent = message;
        modal.style.display = 'flex';
    };
    
    // Close modal
    window.UnifiedApp.ui.closeModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
        }
    };
    
    // Helper functions
    function getToastIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }
    
    function getToastColor(type) {
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };
        return colors[type] || colors.info;
    }
    
    // Add enhanced CSS animations
    if (!document.getElementById('enhancedToastAnimations')) {
        const style = document.createElement('style');
        style.id = 'enhancedToastAnimations';
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            .modal-overlay {
                animation: fadeIn 0.3s ease-out;
            }
            
            .modal-content {
                background: white;
                border-radius: 12px;
                padding: 2rem;
                max-width: 500px;
                width: 90%;
                animation: scaleIn 0.3s ease-out;
            }
            
            .modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
            }
            
            .modal-header h3 {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                color: var(--danger-color);
            }
            
            .modal-close {
                background: none;
                border: none;
                font-size: 1.5rem;
                cursor: pointer;
                color: var(--text-secondary);
                transition: color 0.3s ease;
            }
            
            .modal-close:hover {
                color: var(--text-primary);
            }
            
            .modal-body {
                margin-bottom: 1.5rem;
                color: var(--text-secondary);
            }
            
            .modal-footer {
                display: flex;
                justify-content: flex-end;
            }
            
            .btn-primary {
                background: var(--primary-color);
                color: white;
                border: none;
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: background 0.3s ease;
            }
            
            .btn-primary:hover {
                background: #1d4ed8;
            }
            
            .btn-cancel:hover {
                background: #dc2626 !important;
            }
            
            .partial-result-item {
                display: flex;
                justify-content: space-between;
                padding: 0.5rem 0;
                border-bottom: 1px solid rgba(0, 0, 0, 0.1);
            }
            
            .partial-result-item:last-child {
                border-bottom: none;
            }
            
            .partial-result-item .label {
                color: #6b7280;
                font-weight: 500;
            }
            
            .partial-result-item .value {
                color: #1f2937;
                font-weight: 600;
            }
            
            @keyframes scaleIn {
                from {
                    transform: scale(0.9);
                    opacity: 0;
                }
                to {
                    transform: scale(1);
                    opacity: 1;
                }
            }
            
            #loadingStage {
                transition: opacity 0.3s ease;
            }
            
            #progressBar {
                transition: width 0.5s ease-out;
            }
        `;
        document.head.appendChild(style);
    }
    
    // Initialize UI elements
    window.UnifiedApp.ui.init = function() {
        // Add input validation
        const textInput = document.getElementById('textInput');
        const analyzeBtn = document.getElementById('analyzeBtn');
        
        textInput.addEventListener('input', function() {
            const hasContent = this.value.trim().length >= 50;
            analyzeBtn.disabled = !hasContent;
            
            if (!hasContent && this.value.trim().length > 0) {
                analyzeBtn.textContent = `Need ${50 - this.value.trim().length} more characters`;
            } else {
                analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Content';
            }
        });
        
        // Add keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + Enter to analyze
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                const analyzeBtn = document.getElementById('analyzeBtn');
                if (!analyzeBtn.disabled) {
                    window.analyzeUnified();
                }
            }
            
            // Escape to close modals or cancel analysis
            if (e.key === 'Escape') {
                // First try to cancel analysis
                if (UnifiedApp.analysis && UnifiedApp.analysis.cancelAnalysis) {
                    const overlay = document.getElementById('loadingOverlay');
                    if (overlay && overlay.style.display === 'flex') {
                        UnifiedApp.analysis.cancelAnalysis();
                        return;
                    }
                }
                
                // Then close modals
                const modals = document.querySelectorAll('.modal-overlay');
                modals.forEach(modal => {
                    if (modal.style.display === 'flex') {
                        modal.style.display = 'none';
                    }
                });
            }
        });
    };
    
    // Initialize on load
    document.addEventListener('DOMContentLoaded', function() {
        UnifiedApp.ui.init();
    });
    
})();
