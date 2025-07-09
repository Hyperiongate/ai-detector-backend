/**
 * Facts & Fakes AI - Unified UI Module
 * Handles user interface interactions and animations
 */

(function() {
    'use strict';
    
    // Unified UI Module
    const UnifiedUI = {
        
        // Animation and particle system
        particles: [],
        animationId: null,
        
        /**
         * Initialize floating particles background
         */
        initializeParticles() {
            const canvas = document.getElementById('unifiedParticleCanvas');
            if (!canvas) return;
            
            const ctx = canvas.getContext('2d');
            
            // Set canvas size
            this.resizeCanvas(canvas);
            
            // Initialize particles
            this.createParticles(canvas);
            
            // Start animation
            this.animateParticles(canvas, ctx);
            
            // Handle window resize
            window.addEventListener('resize', () => this.resizeCanvas(canvas));
        },
        
        /**
         * Resize canvas to match container
         */
        resizeCanvas(canvas) {
            const container = canvas.parentElement;
            canvas.width = container.offsetWidth;
            canvas.height = container.offsetHeight;
        },
        
        /**
         * Create floating particles
         */
        createParticles(canvas) {
            this.particles = [];
            const particleCount = Math.floor((canvas.width * canvas.height) / 15000);
            
            for (let i = 0; i < particleCount; i++) {
                this.particles.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    size: Math.random() * 3 + 1,
                    speedX: (Math.random() - 0.5) * 0.5,
                    speedY: (Math.random() - 0.5) * 0.5,
                    opacity: Math.random() * 0.5 + 0.2
                });
            }
        },
        
        /**
         * Animate floating particles
         */
        animateParticles(canvas, ctx) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            this.particles.forEach(particle => {
                // Update position
                particle.x += particle.speedX;
                particle.y += particle.speedY;
                
                // Wrap around edges
                if (particle.x > canvas.width) particle.x = 0;
                if (particle.x < 0) particle.x = canvas.width;
                if (particle.y > canvas.height) particle.y = 0;
                if (particle.y < 0) particle.y = canvas.height;
                
                // Draw particle
                ctx.beginPath();
                ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(102, 126, 234, ${particle.opacity})`;
                ctx.fill();
            });
            
            this.animationId = requestAnimationFrame(() => this.animateParticles(canvas, ctx));
        },
        
        /**
         * Show loading animation with smooth transitions
         */
        showLoadingAnimation() {
            const container = document.querySelector('.unified-container');
            if (container) {
                container.classList.add('analyzing');
            }
            
            // Add pulse effect to analyze button
            const analyzeBtn = document.getElementById('unifiedAnalyzeBtn');
            if (analyzeBtn) {
                analyzeBtn.classList.add('analyzing');
            }
        },
        
        /**
         * Hide loading animation
         */
        hideLoadingAnimation() {
            const container = document.querySelector('.unified-container');
            if (container) {
                container.classList.remove('analyzing');
            }
            
            const analyzeBtn = document.getElementById('unifiedAnalyzeBtn');
            if (analyzeBtn) {
                analyzeBtn.classList.remove('analyzing');
            }
        },
        
        /**
         * Show error modal
         */
        showError(message) {
            const modal = document.getElementById('unifiedErrorModal');
            const errorMessage = document.getElementById('unifiedErrorMessage');
            
            if (modal && errorMessage) {
                errorMessage.textContent = message;
                modal.style.display = 'flex';
                
                // Add entrance animation
                modal.classList.add('modal-enter');
                setTimeout(() => modal.classList.remove('modal-enter'), 300);
            }
        },
        
        /**
         * Close error modal
         */
        closeErrorModal() {
            const modal = document.getElementById('unifiedErrorModal');
            if (modal) {
                modal.style.display = 'none';
            }
        },
        
        /**
         * Retry analysis
         */
        retryAnalysis() {
            this.closeErrorModal();
            if (window.UnifiedApp && window.UnifiedApp.analysis) {
                window.UnifiedApp.analysis.retryAnalysis();
            }
        },
        
        /**
         * Show share modal
         */
        showShareModal() {
            const modal = document.getElementById('unifiedShareModal');
            if (modal) {
                modal.style.display = 'flex';
                
                // Generate share link
                this.generateShareLink();
                
                // Add entrance animation
                modal.classList.add('modal-enter');
                setTimeout(() => modal.classList.remove('modal-enter'), 300);
            }
        },
        
        /**
         * Close share modal
         */
        closeShareModal() {
            const modal = document.getElementById('unifiedShareModal');
            if (modal) {
                modal.style.display = 'none';
            }
        },
        
        /**
         * Generate shareable link
         */
        generateShareLink() {
            const shareLink = document.getElementById('unifiedShareLink');
            if (shareLink && window.UnifiedApp.state.lastResults) {
                // In a real implementation, this would generate a unique share ID
                const shareId = 'unified_' + Date.now();
                const baseUrl = window.location.origin;
                shareLink.value = `${baseUrl}/shared/${shareId}`;
            }
        },
        
        /**
         * Show help modal
         */
        showHelpModal() {
            const modal = document.getElementById('unifiedHelpModal');
            if (modal) {
                modal.style.display = 'flex';
                
                // Add entrance animation
                modal.classList.add('modal-enter');
                setTimeout(() => modal.classList.remove('modal-enter'), 300);
            }
        },
        
        /**
         * Close help modal
         */
        closeHelpModal() {
            const modal = document.getElementById('unifiedHelpModal');
            if (modal) {
                modal.style.display = 'none';
            }
        },
        
        /**
         * Toggle input section expansion
         */
        toggleInputSection(sectionId) {
            const section = document.getElementById(sectionId);
            if (section) {
                section.classList.toggle('expanded');
                
                // Smooth scroll to section if expanding
                if (section.classList.contains('expanded')) {
                    section.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }
            }
        },
        
        /**
         * Initialize tooltips
         */
        initializeTooltips() {
            const tooltipElements = document.querySelectorAll('[data-tooltip]');
            
            tooltipElements.forEach(element => {
                element.addEventListener('mouseenter', (e) => this.showTooltip(e));
                element.addEventListener('mouseleave', () => this.hideTooltip());
                element.addEventListener('mousemove', (e) => this.moveTooltip(e));
            });
        },
        
        /**
         * Show tooltip
         */
        showTooltip(event) {
            const text = event.target.getAttribute('data-tooltip');
            if (!text) return;
            
            // Create tooltip element
            const tooltip = document.createElement('div');
            tooltip.className = 'custom-tooltip';
            tooltip.textContent = text;
            tooltip.id = 'unifiedTooltip';
            
            document.body.appendChild(tooltip);
            
            // Position tooltip
            this.moveTooltip(event);
            
            // Show with animation
            setTimeout(() => tooltip.classList.add('visible'), 10);
        },
        
        /**
         * Move tooltip to follow cursor
         */
        moveTooltip(event) {
            const tooltip = document.getElementById('unifiedTooltip');
            if (tooltip) {
                const offset = 10;
                tooltip.style.left = (event.pageX + offset) + 'px';
                tooltip.style.top = (event.pageY - tooltip.offsetHeight - offset) + 'px';
            }
        },
        
        /**
         * Hide tooltip
         */
        hideTooltip() {
            const tooltip = document.getElementById('unifiedTooltip');
            if (tooltip) {
                tooltip.classList.remove('visible');
                setTimeout(() => tooltip.remove(), 200);
            }
        },
        
        /**
         * Initialize smooth scrolling for anchor links
         */
        initializeSmoothScrolling() {
            const anchorLinks = document.querySelectorAll('a[href^="#"]');
            
            anchorLinks.forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    const targetId = link.getAttribute('href').substring(1);
                    const targetElement = document.getElementById(targetId);
                    
                    if (targetElement) {
                        targetElement.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                });
            });
        },
        
        /**
         * Initialize hover effects
         */
        initializeHoverEffects() {
            // Card hover effects
            const cards = document.querySelectorAll('.info-card, .feature-card, .analysis-section');
            
            cards.forEach(card => {
                card.addEventListener('mouseenter', () => {
                    card.style.transform = 'translateY(-5px)';
                });
                
                card.addEventListener('mouseleave', () => {
                    card.style.transform = 'translateY(0)';
                });
            });
            
            // Button hover effects
            const buttons = document.querySelectorAll('.btn, .social-btn, .export-btn');
            
            buttons.forEach(button => {
                button.addEventListener('mouseenter', () => {
                    if (!button.disabled) {
                        button.style.transform = 'translateY(-2px)';
                    }
                });
                
                button.addEventListener('mouseleave', () => {
                    button.style.transform = 'translateY(0)';
                });
            });
        },
        
        /**
         * Initialize progressive disclosure
         */
        initializeProgressiveDisclosure() {
            const expandableElements = document.querySelectorAll('.expandable');
            
            expandableElements.forEach(element => {
                const trigger = element.querySelector('.expand-trigger');
                const content = element.querySelector('.expand-content');
                
                if (trigger && content) {
                    trigger.addEventListener('click', () => {
                        const isExpanded = element.classList.contains('expanded');
                        
                        if (isExpanded) {
                            content.style.maxHeight = '0';
                            element.classList.remove('expanded');
                        } else {
                            content.style.maxHeight = content.scrollHeight + 'px';
                            element.classList.add('expanded');
                        }
                    });
                }
            });
        },
        
        /**
         * Update progress with smooth animations
         */
        updateProgress(percentage, text) {
            const progressFill = document.getElementById('unifiedProgressFill');
            const progressText = document.getElementById('unifiedProgressText');
            
            if (progressFill) {
                progressFill.style.width = percentage + '%';
            }
            
            if (progressText && text) {
                progressText.textContent = text;
            }
        },
        
        /**
         * Show success notification
         */
        showSuccessNotification(message) {
            this.showNotification(message, 'success');
        },
        
        /**
         * Show warning notification
         */
        showWarningNotification(message) {
            this.showNotification(message, 'warning');
        },
        
        /**
         * Show error notification
         */
        showErrorNotification(message) {
            this.showNotification(message, 'error');
        },
        
        /**
         * Show notification with type
         */
        showNotification(message, type = 'info') {
            const notification = document.createElement('div');
            notification.className = `notification notification-${type}`;
            notification.innerHTML = `
                <div class="notification-content">
                    <i class="fas ${this.getNotificationIcon(type)}"></i>
                    <span>${message}</span>
                </div>
                <button class="notification-close" onclick="this.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            `;
            
            // Add to page
            let container = document.getElementById('notificationContainer');
            if (!container) {
                container = document.createElement('div');
                container.id = 'notificationContainer';
                container.className = 'notification-container';
                document.body.appendChild(container);
            }
            
            container.appendChild(notification);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 5000);
            
            // Add entrance animation
            setTimeout(() => notification.classList.add('visible'), 10);
        },
        
        /**
         * Get notification icon based on type
         */
        getNotificationIcon(type) {
            switch (type) {
                case 'success': return 'fa-check-circle';
                case 'warning': return 'fa-exclamation-triangle';
                case 'error': return 'fa-times-circle';
                default: return 'fa-info-circle';
            }
        }
    };
    
    // Attach to UnifiedApp namespace when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            if (window.UnifiedApp) {
                window.UnifiedApp.ui = UnifiedUI;
                
                // Initialize UI components
                UnifiedUI.initializeTooltips();
                UnifiedUI.initializeSmoothScrolling();
                UnifiedUI.initializeHoverEffects();
                UnifiedUI.initializeProgressiveDisclosure();
                
                console.log('Unified UI module loaded');
            }
        });
    } else {
        if (window.UnifiedApp) {
            window.UnifiedApp.ui = UnifiedUI;
            
            // Initialize UI components
            UnifiedUI.initializeTooltips();
            UnifiedUI.initializeSmoothScrolling();
            UnifiedUI.initializeHoverEffects();
            UnifiedUI.initializeProgressiveDisclosure();
            
            console.log('Unified UI module loaded');
        }
    }
    
})();
