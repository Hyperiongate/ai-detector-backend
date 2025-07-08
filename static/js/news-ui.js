// news-ui.js - Enhanced UI Module with Full Article Input
// Handles UI enhancements and the new full article input tab

// Add the full article tab and content
function enhanceNewsUI() {
    // Find the input tabs container
    const inputTabs = document.querySelector('.input-tabs');
    if (inputTabs) {
        // Check if we already have 3 tabs
        const existingTabs = inputTabs.querySelectorAll('.input-tab');
        if (existingTabs.length === 2) {
            // Add the third tab for full article
            const articleTab = document.createElement('button');
            articleTab.className = 'input-tab';
            articleTab.innerHTML = '📄 Full Article (Most Accurate)';
            articleTab.onclick = () => switchInputType('article');
            inputTabs.appendChild(articleTab);
        }
    }
    
    // Find the input section
    const inputSection = document.querySelector('.input-section');
    if (inputSection && !document.getElementById('articleInput')) {
        // Add the full article input content
        const articleInputHTML = `
            <div class="input-content" id="articleInput">
                <div class="tab-explanation" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.05), rgba(16, 185, 129, 0.08)); border-color: rgba(16, 185, 129, 0.2);">
                    <h3 style="color: #10b981;">📄 Full Article Analysis</h3>
                    <p><strong style="color: #059669;">RECOMMENDED - Most Accurate Results!</strong></p>
                    <p><strong>What it's for:</strong> Complete news articles with all content, metadata, and context</p>
                    <p><strong>What we analyze:</strong></p>
                    <ul>
                        <li>Complete text for comprehensive bias detection</li>
                        <li>Full context for accurate claim verification</li>
                        <li>All quotes and sources for credibility assessment</li>
                        <li>Complete writing patterns for style analysis</li>
                    </ul>
                    <p><strong>Key benefit:</strong> 95%+ accuracy with full context - no missing information</p>
                    <div style="background: rgba(16, 185, 129, 0.1); padding: 15px; border-radius: 10px; margin-top: 15px;">
                        <p style="color: #059669; font-weight: 600; margin: 0;">
                            <i class="fas fa-lightbulb"></i> Pro Tip: Copy the entire article including title, author, and date for best results
                        </p>
                    </div>
                </div>
                <div class="input-group">
                    <label for="fullArticle"><i class="fas fa-file-alt"></i> Paste Complete Article</label>
                    <textarea id="fullArticle" placeholder="Paste the complete news article here, including:&#10;&#10;• Article title&#10;• Author name and publication&#10;• Publication date&#10;• Full article text&#10;• Any editor's notes or corrections&#10;&#10;This method provides the most accurate analysis with 95%+ reliability." style="min-height: 200px;"></textarea>
                </div>
            </div>
        `;
        
        // Insert after the URL input content
        const urlInput = document.getElementById('urlInput');
        if (urlInput) {
            urlInput.insertAdjacentHTML('afterend', articleInputHTML);
        }
    }
    
    // Enhance the URL input explanation
    const urlExplanation = document.querySelector('#urlInput .tab-explanation');
    if (urlExplanation && !urlExplanation.dataset.enhanced) {
        urlExplanation.dataset.enhanced = 'true';
        urlExplanation.innerHTML = `
            <h3>🔗 URL Verification</h3>
            <p><strong>What it's for:</strong> Online news articles, blog posts, official statements</p>
            <p><strong>What we analyze:</strong></p>
            <ul>
                <li>Source reputation and domain authority</li>
                <li>Article content (if extraction successful)</li>
                <li>Publication patterns and history</li>
            </ul>
            <p><strong>Key benefit:</strong> Quick analysis with source verification</p>
            <div style="background: rgba(245, 158, 11, 0.1); padding: 15px; border-radius: 10px; margin-top: 15px;">
                <p style="color: #d97706; font-weight: 600; margin: 0;">
                    <i class="fas fa-exclamation-triangle"></i> Note: Some websites block content extraction. If analysis seems incomplete, use the "Full Article" tab for best results.
                </p>
            </div>
        `;
    }
}

// Initialize UI enhancements
function initializeNewsUI() {
    // Enhance the UI
    enhanceNewsUI();
    
    // Set up smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add hover effects to stat cards
    document.querySelectorAll('.stat-card, .source-detail-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Add tooltips to score circles
    document.addEventListener('mouseover', function(e) {
        if (e.target.closest('.score-circle')) {
            const circle = e.target.closest('.score-circle');
            if (!circle.dataset.hasTooltip) {
                circle.dataset.hasTooltip = 'true';
                circle.setAttribute('title', 'Based on accuracy, experience & expertise');
            }
        }
    });
}

// Enhanced back to top functionality
function enhanceBackToTop() {
    const backToTop = document.getElementById('backToTop');
    if (!backToTop) return;
    
    let isScrolling = false;
    
    window.addEventListener('scroll', () => {
        if (!isScrolling) {
            window.requestAnimationFrame(() => {
                if (window.pageYOffset > 300) {
                    backToTop.classList.add('visible');
                } else {
                    backToTop.classList.remove('visible');
                }
                isScrolling = false;
            });
            isScrolling = true;
        }
    });
}

// Smooth scroll to top
window.scrollToTop = function() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initializeNewsUI();
        enhanceBackToTop();
    });
} else {
    initializeNewsUI();
    enhanceBackToTop();
}

// Export for use in other modules
window.enhanceNewsUI = enhanceNewsUI;
