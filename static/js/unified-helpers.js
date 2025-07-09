/**
 * Facts & Fakes AI - Unified Helpers Module
 * Utility functions for unified analysis
 */

(function() {
    'use strict';
    
    // Unified Helpers Module
    const UnifiedHelpers = {
        
        /**
         * Validate URL format
         */
        isValidUrl(string) {
            try {
                const url = new URL(string);
                return url.protocol === 'http:' || url.protocol === 'https:';
            } catch (_) {
                return false;
            }
        },
        
        /**
         * Format file size for display
         */
        formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        },
        
        /**
         * Extract domain from URL
         */
        extractDomain(url) {
            try {
                const urlObj = new URL(url);
                return urlObj.hostname.replace('www.', '');
            } catch (e) {
                return 'Unknown';
            }
        },
        
        /**
         * Validate image file type
         */
        isValidImageType(file) {
            const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'];
            return validTypes.includes(file.type);
        },
        
        /**
         * Show toast notification
         */
        showToast(message, type = 'info', duration = 5000) {
            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            toast.innerHTML = `
                <div class="toast-content">
                    <i class="fas ${this.getToastIcon(type)}"></i>
                    <span class="toast-message">${message}</span>
                </div>
                <button class="toast-close" onclick="this.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            `;
            
            // Add to page
            let container = document.getElementById('toastContainer');
            if (!container) {
                container = document.createElement('div');
                container.id = 'toastContainer';
                container.className = 'toast-container';
                document.body.appendChild(container);
            }
            
            container.appendChild(toast);
            
            // Show with animation
            setTimeout(() => toast.classList.add('show'), 100);
            
            // Auto-remove
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => {
                    if (toast.parentElement) {
                        toast.remove();
                    }
                }, 300);
            }, duration);
        },
        
        /**
         * Get toast icon based on type
         */
        getToastIcon(type) {
            switch (type) {
                case 'success': return 'fa-check-circle';
                case 'warning': return 'fa-exclamation-triangle';
                case 'error': return 'fa-times-circle';
                default: return 'fa-info-circle';
            }
        },
        
        /**
         * Copy text to clipboard
         */
        async copyToClipboard(text) {
            try {
                await navigator.clipboard.writeText(text);
                this.showToast('Copied to clipboard!', 'success');
                return true;
            } catch (err) {
                console.error('Failed to copy text: ', err);
                this.showToast('Failed to copy to clipboard', 'error');
                return false;
            }
        },
        
        /**
         * Copy share link to clipboard
         */
        copyShareLink() {
            const shareLink = document.getElementById('unifiedShareLink');
            if (shareLink) {
                this.copyToClipboard(shareLink.value);
            }
        },
        
        /**
         * Share on Twitter
         */
        shareOnTwitter() {
            const shareLink = document.getElementById('unifiedShareLink');
            if (shareLink) {
                const text = 'Check out this multi-modal content analysis from Facts & Fakes AI';
                const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(shareLink.value)}`;
                window.open(twitterUrl, '_blank', 'width=600,height=400');
            }
        },
        
        /**
         * Share on Facebook
         */
        shareOnFacebook() {
            const shareLink = document.getElementById('unifiedShareLink');
            if (shareLink) {
                const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareLink.value)}`;
                window.open(facebookUrl, '_blank', 'width=600,height=400');
            }
        },
        
        /**
         * Share on LinkedIn
         */
        shareOnLinkedIn() {
            const shareLink = document.getElementById('unifiedShareLink');
            if (shareLink) {
                const title = 'Multi-Modal Content Analysis Results';
                const summary = 'Comprehensive AI-powered analysis of text, news, and image content';
                const linkedinUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareLink.value)}&title=${encodeURIComponent(title)}&summary=${encodeURIComponent(summary)}`;
                window.open(linkedinUrl, '_blank', 'width=600,height=400');
            }
        },
        
        /**
         * Generate PDF report
         */
        async generatePDF() {
            try {
                if (!window.UnifiedApp.state.lastResults) {
                    this.showToast('No analysis results to export', 'warning');
                    return;
                }
                
                this.showToast('Generating PDF report...', 'info');
                
                // Prepare data for PDF generation
                const reportData = {
                    results: window.UnifiedApp.state.lastResults,
                    timestamp: new Date().toISOString(),
                    analysisType: 'unified'
                };
                
                // Make request to PDF generation endpoint
                const response = await fetch('/api/generate-unified-pdf', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify(reportData)
                });
                
                if (!response.ok) {
                    throw new Error(`PDF generation failed: ${response.status}`);
                }
                
                // Download the PDF
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `unified-analysis-report-${Date.now()}.pdf`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.showToast('PDF report downloaded successfully!', 'success');
                
            } catch (error) {
                console.error('PDF generation error:', error);
                this.showToast('Failed to generate PDF report', 'error');
            }
        },
        
        /**
         * Get file extension from filename
         */
        getFileExtension(filename) {
            return filename.slice((filename.lastIndexOf('.') - 1 >>> 0) + 2).toLowerCase();
        },
        
        /**
         * Sanitize filename for display
         */
        sanitizeFilename(filename) {
            return filename.replace(/[^a-z0-9.-]/gi, '_').substring(0, 50);
        },
        
        /**
         * Format timestamp for display
         */
        formatTimestamp(timestamp) {
            const date = new Date(timestamp);
            return date.toLocaleString();
        },
        
        /**
         * Calculate reading time for text
         */
        calculateReadingTime(text) {
            const wordsPerMinute = 200;
            const words = text.trim().split(/\s+/).length;
            const minutes = Math.ceil(words / wordsPerMinute);
            return minutes;
        },
        
        /**
         * Truncate text with ellipsis
         */
        truncateText(text, maxLength = 100) {
            if (text.length <= maxLength) return text;
            return text.substring(0, maxLength).trim() + '...';
        },
        
        /**
         * Debounce function for search inputs
         */
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },
        
        /**
         * Check if device supports feature
         */
        checkBrowserSupport() {
            const support = {
                clipboard: !!navigator.clipboard,
                fileAPI: !!(window.File && window.FileReader && window.FileList && window.Blob),
                dragDrop: 'draggable' in document.createElement('div'),
                webGL: !!window.WebGLRenderingContext,
                localStorage: !!window.localStorage
            };
            
            return support;
        },
        
        /**
         * Track analytics event
         */
        trackEvent(eventName, properties = {}) {
            try {
                // In a real implementation, this would send to analytics service
                console.log('Analytics Event:', eventName, properties);
                
                // Store in local analytics if available
                if (window.localStorage) {
                    const events = JSON.parse(localStorage.getItem('ffai_events') || '[]');
                    events.push({
                        event: eventName,
                        properties: properties,
                        timestamp: new Date().toISOString(),
                        page: 'unified-analysis'
                    });
                    localStorage.setItem('ffai_events', JSON.stringify(events.slice(-100))); // Keep last 100 events
                }
            } catch (error) {
                console.error('Analytics tracking error:', error);
            }
        },
        
        /**
         * Get device information
         */
        getDeviceInfo() {
            return {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                screenResolution: `${screen.width}x${screen.height}`,
                viewport: `${window.innerWidth}x${window.innerHeight}`,
                cookieEnabled: navigator.cookieEnabled,
                onLine: navigator.onLine
            };
        },
        
        /**
         * Generate unique session ID
         */
        generateSessionId() {
            return 'unified_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        },
        
        /**
         * Validate form data before submission
         */
        validateFormData(inputData) {
            const errors = [];
            
            // Check if at least one input type is provided
            const hasText = inputData.textContent && inputData.textContent.trim().length > 0;
            const hasUrl = inputData.urlContent && inputData.urlContent.trim().length > 0;
            const hasImage = inputData.imageFile !== null;
            
            if (!hasText && !hasUrl && !hasImage) {
                errors.push('Please provide at least one type of content to analyze');
            }
            
            // Validate URL if provided
            if (hasUrl && !this.isValidUrl(inputData.urlContent)) {
                errors.push('Please enter a valid URL (must include http:// or https://)');
            }
            
            // Validate text length
            if (hasText && inputData.textContent.length > 10000) {
                errors.push('Text content must be less than 10,000 characters');
            }
            
            // Validate image file
            if (hasImage) {
                if (!this.isValidImageType(inputData.imageFile)) {
                    errors.push('Please select a valid image file (JPG, PNG, GIF, WebP, BMP)');
                }
                
                if (inputData.imageFile.size > 50 * 1024 * 1024) { // 50MB
                    errors.push('Image file must be less than 50MB');
                }
            }
            
            return {
                isValid: errors.length === 0,
                errors: errors
            };
        },
        
        /**
         * Log performance metrics
         */
        logPerformance(startTime, endTime, operation) {
            const duration = endTime - startTime;
            console.log(`Performance: ${operation} took ${duration}ms`);
            
            // Track performance analytics
            this.trackEvent('performance', {
                operation: operation,
                duration: duration,
                timestamp: new Date().toISOString()
            });
        },
        
        /**
         * Handle network errors gracefully
         */
        handleNetworkError(error) {
            console.error('Network error:', error);
            
            if (!navigator.onLine) {
                this.showToast('No internet connection. Please check your network and try again.', 'error');
            } else if (error.name === 'AbortError') {
                this.showToast('Request was cancelled. Please try again.', 'warning');
            } else if (error.message.includes('timeout')) {
                this.showToast('Request timed out. Please try again.', 'warning');
            } else {
                this.showToast('Network error occurred. Please try again.', 'error');
            }
        },
        
        /**
         * Initialize error handling
         */
        initializeErrorHandling() {
            // Global error handler
            window.addEventListener('error', (event) => {
                console.error('Global error:', event.error);
                this.trackEvent('javascript_error', {
                    message: event.error.message,
                    filename: event.filename,
                    lineno: event.lineno,
                    colno: event.colno
                });
            });
            
            // Unhandled promise rejection handler
            window.addEventListener('unhandledrejection', (event) => {
                console.error('Unhandled promise rejection:', event.reason);
                this.trackEvent('promise_rejection', {
                    reason: event.reason.toString()
                });
            });
        }
    };
    
    // Attach to UnifiedApp namespace when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            if (window.UnifiedApp) {
                window.UnifiedApp.helpers = UnifiedHelpers;
                
                // Initialize error handling
                UnifiedHelpers.initializeErrorHandling();
                
                console.log('Unified Helpers module loaded');
            }
        });
    } else {
        if (window.UnifiedApp) {
            window.UnifiedApp.helpers = UnifiedHelpers;
            
            // Initialize error handling
            UnifiedHelpers.initializeErrorHandling();
            
            console.log('Unified Helpers module loaded');
        }
    }
    
})();
