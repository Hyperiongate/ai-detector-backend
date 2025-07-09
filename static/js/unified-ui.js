// unified-ui.js - UI Interactions for AI & Plagiarism Detector
(function() {
    'use strict';
    
    // Initialize namespace
    window.UnifiedApp = window.UnifiedApp || {};
    window.UnifiedApp.ui = {};
    
    // Loading overlay management
    window.UnifiedApp.ui.showLoading = function() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = 'flex';
        
        // Reset progress
        document.getElementById('progressBar').style.width = '0%';
        document.getElementById('loadingStage').textContent = 'Initializing Analysis...';
    };
    
    window.UnifiedApp.ui.hideLoading = function() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = 'none';
    };
    
    // Update progress
    window.UnifiedApp.ui.updateProgress = function(stage, progress) {
        document.getElementById('loadingStage').textContent = stage;
        document.getElementById('progressBar').style.width = progress + '%';
    };
    
    // Toast notifications
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
    
    // Show error modal
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
    
    // Add CSS animations
    if (!document.getElementById('toastAnimations')) {
        const style = document.createElement('style');
        style.id = 'toastAnimations';
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
            
            // Escape to close modals
            if (e.key === 'Escape') {
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
