// Image Helpers Module
window.ImageApp = window.ImageApp || {};

window.ImageApp.helpers = (function() {
    'use strict';

    // Validate image file
    function validateImageFile(file) {
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'];
        return validTypes.includes(file.type.toLowerCase());
    }

    // Format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Generate share text
    function generateShareText(results) {
        const verdict = results.verdict;
        const score = results.trustScore;
        return `I just analyzed an image with Facts & Fakes AI. Verdict: ${verdict} (${score}% authenticity score). Check your images at ${window.location.origin}`;
    }

    // Share to Twitter
    function shareToTwitter() {
        const results = getCurrentResults();
        if (!results) return;

        const text = generateShareText(results);
        const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`;
        window.open(url, '_blank', 'width=550,height=450');
    }

    // Share to Facebook
    function shareToFacebook() {
        const url = window.location.href;
        const fbUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
        window.open(fbUrl, '_blank', 'width=550,height=450');
    }

    // Share to LinkedIn
    function shareToLinkedIn() {
        const results = getCurrentResults();
        if (!results) return;

        const url = window.location.href;
        const title = 'Image Analysis Results';
        const summary = generateShareText(results);
        const linkedInUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}&title=${encodeURIComponent(title)}&summary=${encodeURIComponent(summary)}`;
        window.open(linkedInUrl, '_blank', 'width=550,height=450');
    }

    // Copy share link
    async function copyShareLink() {
        const shareLink = document.getElementById('shareLink');
        if (!shareLink) return;

        try {
            if (navigator.clipboard) {
                await navigator.clipboard.writeText(shareLink.value);
            } else {
                // Fallback for older browsers
                shareLink.select();
                document.execCommand('copy');
            }

            // Show success feedback
            const copyBtn = document.querySelector('.copy-btn');
            if (copyBtn) {
                const originalHTML = copyBtn.innerHTML;
                copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                copyBtn.style.background = '#10b981';
                
                setTimeout(() => {
                    copyBtn.innerHTML = originalHTML;
                    copyBtn.style.background = '';
                }, 2000);
            }

            showToast('Link copied to clipboard!');
        } catch (err) {
            console.error('Failed to copy:', err);
            showToast('Failed to copy link', 'error');
        }
    }

    // Submit feedback
    async function submitFeedback(event) {
        event.preventDefault();

        const form = event.target;
        const formData = {
            type: form.feedbackType.value,
            message: form.feedbackMessage.value,
            email: form.feedbackEmail.value,
            tool: 'image-analysis',
            timestamp: new Date().toISOString()
        };

        try {
            // Show loading
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';

            // Submit feedback
            const response = await fetch('/api/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                showToast('Thank you for your feedback!', 'success');
                form.reset();
                window.ImageApp.ui.closeModal('feedbackModal');
            } else {
                throw new Error('Failed to submit feedback');
            }
        } catch (error) {
            console.error('Feedback submission error:', error);
            showToast('Failed to send feedback. Please try again.', 'error');
        } finally {
            // Reset button
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send Feedback';
        }
    }

    // Get current results
    function getCurrentResults() {
        // This would normally retrieve the actual results from the analysis
        // For now, return mock data
        return {
            verdict: 'AI Generated',
            trustScore: 15,
            confidence: 94
        };
    }

    // Show toast notification
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            <span>${message}</span>
        `;

        document.body.appendChild(toast);

        // Animate in
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);

        // Remove after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 3000);
    }

    // Check browser compatibility
    function checkBrowserCompatibility() {
        const issues = [];

        // Check for required APIs
        if (!window.FileReader) {
            issues.push('FileReader API not supported');
        }

        if (!window.FormData) {
            issues.push('FormData API not supported');
        }

        if (!window.fetch) {
            issues.push('Fetch API not supported');
        }

        // Check for Canvas support (needed for image processing)
        const canvas = document.createElement('canvas');
        if (!canvas.getContext) {
            issues.push('Canvas API not supported');
        }

        return {
            compatible: issues.length === 0,
            issues: issues
        };
    }

    // Track events for analytics
    function trackEvent(action, category = 'Image Analysis', label = '', value = 0) {
        if (typeof gtag !== 'undefined') {
            gtag('event', action, {
                event_category: category,
                event_label: label,
                value: value
            });
        }
    }

    // Generate random analysis ID
    function generateAnalysisId() {
        return 'img_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    // Preload images
    function preloadImages(urls) {
        urls.forEach(url => {
            const img = new Image();
            img.src = url;
        });
    }

    // Debounce function
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Throttle function
    function throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // Export public methods
    return {
        validateImageFile: validateImageFile,
        formatFileSize: formatFileSize,
        shareToTwitter: shareToTwitter,
        shareToFacebook: shareToFacebook,
        shareToLinkedIn: shareToLinkedIn,
        copyShareLink: copyShareLink,
        submitFeedback: submitFeedback,
        showToast: showToast,
        checkBrowserCompatibility: checkBrowserCompatibility,
        trackEvent: trackEvent,
        generateAnalysisId: generateAnalysisId,
        preloadImages: preloadImages,
        debounce: debounce,
        throttle: throttle
    };
})();

// Add toast styles
const toastStyle = document.createElement('style');
toastStyle.textContent = `
    .toast {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        gap: 12px;
        transform: translateY(100px);
        opacity: 0;
        transition: all 0.3s ease;
        z-index: 10000;
        max-width: 400px;
    }

    .toast.show {
        transform: translateY(0);
        opacity: 1;
    }

    .toast-success {
        border-left: 4px solid #10b981;
    }

    .toast-success i {
        color: #10b981;
    }

    .toast-error {
        border-left: 4px solid #ef4444;
    }

    .toast-error i {
        color: #ef4444;
    }

    .toast span {
        color: #1a202c;
        font-size: 16px;
    }

    @media (max-width: 768px) {
        .toast {
            right: 10px;
            left: 10px;
            max-width: none;
        }
    }
`;
document.head.appendChild(toastStyle);
