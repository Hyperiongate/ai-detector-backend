/**
 * Speech Helpers Module
 * Utility functions for speech analysis
 */

window.SpeechApp = window.SpeechApp || {};

window.SpeechApp.helpers = (function() {
    'use strict';
    
    /**
     * Initialize the helpers module
     */
    function initialize() {
        console.log('Speech helpers module initialized');
    }
    
    /**
     * Validate YouTube URL
     */
    function isValidYouTubeUrl(url) {
        const patterns = [
            /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)[\w-]+(&.*)?$/,
            /^(https?:\/\/)?(www\.)?(m\.)?youtube\.com\/watch\?.*v=[\w-]+.*$/
        ];
        
        return patterns.some(pattern => pattern.test(url));
    }
    
    /**
     * Extract YouTube video ID
     */
    function extractYouTubeId(url) {
        const patterns = [
            /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([\w-]+)/,
            /youtube\.com\/watch\?.*v=([\w-]+)/
        ];
        
        for (const pattern of patterns) {
            const match = url.match(pattern);
            if (match && match[1]) {
                return match[1];
            }
        }
        
        return null;
    }
    
    /**
     * Format file size
     */
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    /**
     * Format duration
     */
    function formatDuration(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        } else {
            return `${minutes}:${secs.toString().padStart(2, '0')}`;
        }
    }
    
    /**
     * Validate audio file
     */
    function isValidAudioFile(file) {
        const validTypes = [
            'audio/mp3',
            'audio/mpeg',
            'audio/wav',
            'audio/wave',
            'audio/x-wav',
            'audio/ogg',
            'audio/webm',
            'audio/flac',
            'audio/x-flac',
            'audio/mp4',
            'audio/x-m4a'
        ];
        
        return validTypes.includes(file.type) || 
               file.name.match(/\.(mp3|wav|ogg|flac|m4a|webm)$/i);
    }
    
    /**
     * Validate video file
     */
    function isValidVideoFile(file) {
        const validTypes = [
            'video/mp4',
            'video/webm',
            'video/ogg',
            'video/quicktime',
            'video/x-msvideo',
            'video/x-matroska',
            'video/avi'
        ];
        
        return validTypes.includes(file.type) || 
               file.name.match(/\.(mp4|webm|ogg|mov|avi|mkv)$/i);
    }
    
    /**
     * Get file type icon
     */
    function getFileTypeIcon(file) {
        if (isValidAudioFile(file)) {
            return '<i class="fas fa-file-audio"></i>';
        } else if (isValidVideoFile(file)) {
            return '<i class="fas fa-file-video"></i>';
        } else {
            return '<i class="fas fa-file"></i>';
        }
    }
    
    /**
     * Debounce function
     */
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
    
    /**
     * Throttle function
     */
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
    
    /**
     * Copy to clipboard
     */
    function copyToClipboard(text) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            return navigator.clipboard.writeText(text);
        } else {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            
            try {
                const success = document.execCommand('copy');
                document.body.removeChild(textarea);
                return success ? Promise.resolve() : Promise.reject();
            } catch (err) {
                document.body.removeChild(textarea);
                return Promise.reject(err);
            }
        }
    }
    
    /**
     * Get share URL
     */
    function getShareUrl(analysisId) {
        const baseUrl = window.location.origin + window.location.pathname;
        return `${baseUrl}?id=${analysisId}`;
    }
    
    /**
     * Create social share URL
     */
    function createSocialShareUrl(platform, text, url) {
        const encodedText = encodeURIComponent(text);
        const encodedUrl = encodeURIComponent(url);
        
        const shareUrls = {
            twitter: `https://twitter.com/intent/tweet?text=${encodedText}&url=${encodedUrl}`,
            facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`,
            linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`,
            reddit: `https://reddit.com/submit?url=${encodedUrl}&title=${encodedText}`,
            email: `mailto:?subject=${encodedText}&body=${encodedUrl}`
        };
        
        return shareUrls[platform] || '';
    }
    
    /**
     * Download data as file
     */
    function downloadFile(content, filename, mimeType = 'text/plain') {
        const blob = new Blob([content], { type: mimeType });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    }
    
    /**
     * Parse time string to seconds
     */
    function parseTimeToSeconds(timeString) {
        const parts = timeString.split(':').reverse();
        let seconds = 0;
        
        for (let i = 0; i < parts.length; i++) {
            seconds += parseInt(parts[i]) * Math.pow(60, i);
        }
        
        return seconds;
    }
    
    /**
     * Generate unique ID
     */
    function generateUniqueId(prefix = 'id') {
        return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }
    
    /**
     * Check if mobile device
     */
    function isMobileDevice() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }
    
    /**
     * Get browser info
     */
    function getBrowserInfo() {
        const userAgent = navigator.userAgent;
        let browser = 'Unknown';
        let version = 'Unknown';
        
        if (userAgent.indexOf('Firefox') > -1) {
            browser = 'Firefox';
            version = userAgent.match(/Firefox\/(\d+)/)[1];
        } else if (userAgent.indexOf('Chrome') > -1) {
            browser = 'Chrome';
            version = userAgent.match(/Chrome\/(\d+)/)[1];
        } else if (userAgent.indexOf('Safari') > -1) {
            browser = 'Safari';
            version = userAgent.match(/Version\/(\d+)/)[1];
        } else if (userAgent.indexOf('Edge') > -1) {
            browser = 'Edge';
            version = userAgent.match(/Edge\/(\d+)/)[1];
        }
        
        return { browser, version };
    }
    
    /**
     * Check feature support
     */
    function checkFeatureSupport() {
        return {
            webAudio: 'AudioContext' in window || 'webkitAudioContext' in window,
            getUserMedia: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
            speechRecognition: 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window,
            clipboard: 'clipboard' in navigator,
            share: 'share' in navigator,
            notifications: 'Notification' in window
        };
    }
    
    /**
     * Request notification permission
     */
    function requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            return Notification.requestPermission();
        }
        return Promise.resolve(Notification.permission);
    }
    
    /**
     * Show notification
     */
    function showNotification(title, options = {}) {
        if ('Notification' in window && Notification.permission === 'granted') {
            const notification = new Notification(title, {
                icon: '/static/images/icon-192.png',
                badge: '/static/images/badge-72.png',
                ...options
            });
            
            return notification;
        }
        return null;
    }
    
    /**
     * Format percentage
     */
    function formatPercentage(value, decimals = 0) {
        return `${(value * 100).toFixed(decimals)}%`;
    }
    
    /**
     * Get confidence level
     */
    function getConfidenceLevel(score) {
        if (score >= 90) return { level: 'Very High', class: 'very-high' };
        if (score >= 80) return { level: 'High', class: 'high' };
        if (score >= 70) return { level: 'Medium', class: 'medium' };
        if (score >= 60) return { level: 'Low', class: 'low' };
        return { level: 'Very Low', class: 'very-low' };
    }
    
    /**
     * Sanitize HTML
     */
    function sanitizeHtml(html) {
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    }
    
    /**
     * Track event (for analytics)
     */
    function trackEvent(category, action, label = null, value = null) {
        // Google Analytics tracking
        if (typeof gtag !== 'undefined') {
            gtag('event', action, {
                event_category: category,
                event_label: label,
                value: value
            });
        }
        
        // Custom analytics
        console.log('Event tracked:', { category, action, label, value });
    }
    
    /**
     * Get relative time
     */
    function getRelativeTime(date) {
        const now = new Date();
        const past = new Date(date);
        const diffMs = now - past;
        const diffSecs = Math.floor(diffMs / 1000);
        const diffMins = Math.floor(diffSecs / 60);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffSecs < 60) return 'just now';
        if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        if (diffDays < 30) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
        
        return past.toLocaleDateString();
    }
    
    /**
     * Validate email
     */
    function isValidEmail(email) {
        const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return pattern.test(email);
    }
    
    /**
     * Get query parameters
     */
    function getQueryParams() {
        const params = {};
        const searchParams = new URLSearchParams(window.location.search);
        
        for (const [key, value] of searchParams) {
            params[key] = value;
        }
        
        return params;
    }
    
    /**
     * Update query parameters
     */
    function updateQueryParams(params) {
        const url = new URL(window.location);
        
        Object.keys(params).forEach(key => {
            if (params[key] === null || params[key] === undefined) {
                url.searchParams.delete(key);
            } else {
                url.searchParams.set(key, params[key]);
            }
        });
        
        window.history.pushState({}, '', url);
    }
    
    // Public API
    return {
        initialize: initialize,
        isValidYouTubeUrl: isValidYouTubeUrl,
        extractYouTubeId: extractYouTubeId,
        formatFileSize: formatFileSize,
        formatDuration: formatDuration,
        isValidAudioFile: isValidAudioFile,
        isValidVideoFile: isValidVideoFile,
        getFileTypeIcon: getFileTypeIcon,
        debounce: debounce,
        throttle: throttle,
        copyToClipboard: copyToClipboard,
        getShareUrl: getShareUrl,
        createSocialShareUrl: createSocialShareUrl,
        downloadFile: downloadFile,
        parseTimeToSeconds: parseTimeToSeconds,
        generateUniqueId: generateUniqueId,
        isMobileDevice: isMobileDevice,
        getBrowserInfo: getBrowserInfo,
        checkFeatureSupport: checkFeatureSupport,
        requestNotificationPermission: requestNotificationPermission,
        showNotification: showNotification,
        formatPercentage: formatPercentage,
        getConfidenceLevel: getConfidenceLevel,
        sanitizeHtml: sanitizeHtml,
        trackEvent: trackEvent,
        getRelativeTime: getRelativeTime,
        isValidEmail: isValidEmail,
        getQueryParams: getQueryParams,
        updateQueryParams: updateQueryParams
    };
})();

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        window.SpeechApp.helpers.initialize();
    });
} else {
    window.SpeechApp.helpers.initialize();
}

console.log('Speech Helpers Module Loaded');
