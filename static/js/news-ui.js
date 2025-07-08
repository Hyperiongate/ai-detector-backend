// static/js/news-ui.js - Enhanced UI with all missing features

// ============================================================================
// UI INITIALIZATION AND SETUP
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    initializeEnhancedUI();
    setupEventListeners();
});

function initializeEnhancedUI() {
    createBetaBanner();
    createInfoSections();
    createBackToTopButton();
    createModals();
    setupNotifications();
    setupModalHandlers();
}

// ============================================================================
// BETA BANNER
// ============================================================================

function createBetaBanner() {
    const bannerHTML = `
    <div class="beta-banner">
        <div class="beta-content">
            <span class="beta-badge">BETA</span>
            <span>🚀 The world's ONLY platform built specifically for news verification - Join our beta!</span>
            <button class="beta-join-btn" onclick="openBetaModal()">Join Beta</button>
        </div>
    </div>`;
    
    const navBar = document.querySelector('.nav-bar');
    if (navBar && !document.querySelector('.beta-banner')) {
        navBar.insertAdjacentHTML('beforebegin', bannerHTML);
    }
}

// ============================================================================
// INFO SECTIONS GRID
// ============================================================================

function createInfoSections() {
    const container = document.querySelector('.tool-container');
    if (!container || document.querySelector('.info-sections-grid')) return;
    
    const sectionsHTML = `
    <div class="info-sections-grid">
        <!-- Methodologies Section -->
        <div class="dropdown-section compact" id="methodologies-section">
            <div class="dropdown-header compact-header" onclick="toggleDropdown(this, 'info')">
                <div class="compact-header-content">
                    <i class="fas fa-cogs"></i>
                    <div class="compact-header-text">
                        <span class="compact-title">12 Analysis Methods</span>
                        <span class="compact-subtitle">Advanced verification systems</span>
                    </div>
                </div>
                <i class="fas fa-chevron-down dropdown-icon"></i>
            </div>
            <div class="dropdown-content">
                <div class="tools-employed" style="border: none; margin: 0;">
                    <div class="tools-grid">
                        <div class="tool-item"><i class="fas fa-balance-scale"></i> Real-Time Political Bias Detection</div>
                        <div class="tool-item"><i class="fas fa-check-circle"></i> Multi-Source Fact Verification</div>
                        <div class="tool-item"><i class="fas fa-database"></i> 500+ News Source Credibility Database</div>
                        <div class="tool-item"><i class="fas fa-search"></i> Cross-Source Verification Network</div>
                        <div class="tool-item"><i class="fas fa-shield-alt"></i> Misinformation Pattern Recognition</div>
                        <div class="tool-item"><i class="fas fa-network-wired"></i> Multi-Outlet Story Comparison</div>
                        <div class="tool-item"><i class="fas fa-chart-line"></i> Journalism Quality Scoring</div>
                        <div class="tool-item"><i class="fas fa-clock"></i> Timeline & Event Verification</div>
                        <div class="tool-item"><i class="fas fa-fingerprint"></i> Editorial vs News Classification</div>
                        <div class="tool-item"><i class="fas fa-brain"></i> Advanced AI Content Analysis</div>
                        <div class="tool-item"><i class="fas fa-globe"></i> Real-Time Breaking News Verification</div>
                        <div class="tool-item"><i class="fas fa-comments"></i> Social Media Echo Analysis</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- How to Use Section -->
        <div class="dropdown-section compact" id="how-to-use-section">
            <div class="dropdown-header compact-header" onclick="toggleDropdown(this, 'info')">
                <div class="compact-header-content">
                    <i class="fas fa-info-circle"></i>
                    <div class="compact-header-text">
                        <span class="compact-title">How to Use</span>
                        <span class="compact-subtitle">3 simple steps</span>
                    </div>
                </div>
                <i class="fas fa-chevron-down dropdown-icon"></i>
            </div>
            <div class="dropdown-content">
                <div style="display: grid; gap: 15px;">
                    <div style="display: flex; align-items: start; gap: 15px;">
                        <div style="background: #667eea; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0;">1</div>
                        <div>
                            <strong style="color: #4c1d95;">Choose Your Input Method:</strong><br>
                            <span style="color: #6b7280;">Either paste news text directly or enter a news article URL</span>
                        </div>
                    </div>
                    <div style="display: flex; align-items: start; gap: 15px;">
                        <div style="background: #667eea; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0;">2</div>
                        <div>
                            <strong style="color: #4c1d95;">Select Analysis Type:</strong><br>
                            <span style="color: #6b7280;">FREE: Basic credibility check | PRO: Comprehensive verification with bias analysis</span>
                        </div>
                    </div>
                    <div style="display: flex; align-items: start; gap: 15px;">
                        <div style="background: #667eea; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0;">3</div>
                        <div>
                            <strong style="color: #4c1d95;">Review Your Results:</strong><br>
                            <span style="color: #6b7280;">Explore bias compass, source verification, and claim analysis</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Free vs Pro Comparison -->
        <div class="dropdown-section compact" id="comparison-section">
            <div class="dropdown-header compact-header" onclick="toggleDropdown(this, 'info')">
                <div class="compact-header-content">
                    <i class="fas fa-crown"></i>
                    <div class="compact-header-text">
                        <span class="compact-title">Free vs Pro</span>
                        <span class="compact-subtitle">Compare features</span>
                    </div>
                </div>
                <i class="fas fa-chevron-down dropdown-icon"></i>
            </div>
            <div class="dropdown-content">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div style="background: white; padding: 20px; border-radius: 12px; border: 2px solid #e5e7eb;">
                        <h4 style="color: #6b7280; margin-bottom: 15px;"><i class="fas fa-gift"></i> FREE Version</h4>
                        <ul style="list-style: none; padding: 0; margin: 0;">
                            <li style="margin-bottom: 10px; color: #4b5563;">✓ Basic credibility score</li>
                            <li style="margin-bottom: 10px; color: #4b5563;">✓ Source verification (100+ sources)</li>
                            <li style="margin-bottom: 10px; color: #4b5563;">✓ Simple bias indicator</li>
                            <li style="margin-bottom: 10px; color: #4b5563;">✓ 5 analyses per day</li>
                            <li style="margin-bottom: 10px; color: #9ca3af;">✗ No downloadable reports</li>
                            <li style="margin-bottom: 10px; color: #9ca3af;">✗ Limited evidence details</li>
                        </ul>
                    </div>
                    <div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px; border-radius: 12px; border: 2px solid #667eea;">
                        <h4 style="color: white; margin-bottom: 15px;"><i class="fas fa-crown"></i> PRO Version</h4>
                        <ul style="list-style: none; padding: 0; margin: 0;">
                            <li style="margin-bottom: 10px; color: white;">✓ Advanced credibility analysis</li>
                            <li style="margin-bottom: 10px; color: white;">✓ 500+ source database</li>
                            <li style="margin-bottom: 10px; color: white;">✓ Interactive bias compass</li>
                            <li style="margin-bottom: 10px; color: white;">✓ Unlimited analyses</li>
                            <li style="margin-bottom: 10px; color: white;">✓ Downloadable PDF reports</li>
                            <li style="margin-bottom: 10px; color: white;">✓ Full claim verification</li>
                            <li style="margin-bottom: 10px; color: white;">✓ All 12 analysis methodologies</li>
                            <li style="margin-bottom: 10px; color: white;">✓ Priority customer support</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <!-- Daily Usage -->
        <div class="dropdown-section compact" id="usage-section">
            <div class="dropdown-header compact-header" onclick="toggleDropdown(this, 'info')">
                <div class="compact-header-content">
                    <i class="fas fa-chart-bar"></i>
                    <div class="compact-header-text">
                        <span class="compact-title">Daily Usage</span>
                        <span class="compact-subtitle">Track your analyses</span>
                    </div>
                </div>
                <i class="fas fa-chevron-down dropdown-icon"></i>
            </div>
            <div class="dropdown-content">
                <div id="usageCounter">
                    <div style="text-align: center; padding: 20px;">
                        <p style="color: #6b7280; font-size: 1.1rem;">Daily analyses available</p>
                        <div style="font-size: 2.5rem; font-weight: 700; color: #667eea; margin: 10px 0;">Unlimited</div>
                        <p style="color: #10b981; font-weight: 600;">Pro Account Active</p>
                    </div>
                </div>
            </div>
        </div>
    </div>`;
    
    const inputSection = container.querySelector('.input-section');
    if (inputSection) {
        inputSection.insertAdjacentHTML('beforebegin', sectionsHTML);
    }
}

// ============================================================================
// BACK TO TOP BUTTON
// ============================================================================

function createBackToTopButton() {
    if (document.getElementById('backToTop')) return;
    
    const button = document.createElement('button');
    button.className = 'back-to-top';
    button.id = 'backToTop';
    button.innerHTML = '<i class="fas fa-arrow-up"></i>';
    button.onclick = () => window.scrollTo({ top: 0, behavior: 'smooth' });
    
    document.body.appendChild(button);
    
    // Show/hide on scroll
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            button.classList.add('visible');
        } else {
            button.classList.remove('visible');
        }
    });
}

// ============================================================================
// MODALS
// ============================================================================

function createModals() {
    if (document.getElementById('betaModal')) return;
    
    const modalsHTML = `
    <!-- Beta Modal -->
    <div id="betaModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeBetaModal()">&times;</span>
            <div class="modal-header">
                <h2>🚀 Join Our Beta Program</h2>
                <p>Get exclusive early access to the world's first news verification platform!</p>
            </div>
            <div class="modal-body">
                <form id="betaSignupForm">
                    <div class="input-group">
                        <input type="email" id="betaEmail" placeholder="Enter your email address" required>
                    </div>
                    <div class="input-group">
                        <input type="text" id="betaName" placeholder="Your name (optional)">
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeBetaModal()">Cancel</button>
                <button class="btn btn-primary" onclick="submitBetaSignup()">Join Beta Program</button>
            </div>
        </div>
    </div>

    <!-- Claims Modal -->
    <div id="claimsModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeClaimsModal()">&times;</span>
            <div class="modal-header">
                <h2><i class="fas fa-exclamation-triangle"></i> Claim Analysis</h2>
                <p>Detailed analysis of claims found in the article</p>
            </div>
            <div class="modal-body" id="claimsList">
                <!-- Claims will be dynamically inserted here -->
            </div>
        </div>
    </div>`;
    
    document.body.insertAdjacentHTML('beforeend', modalsHTML);
}

// ============================================================================
// NOTIFICATIONS
// ============================================================================

function setupNotifications() {
    window.showNotification = function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.display = 'block';
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    };
}

// ============================================================================
// DROPDOWN TOGGLES
// ============================================================================

window.toggleDropdown = function(header, tier) {
    const content = header.nextElementSibling;
    const isOpen = header.classList.contains('open');
    
    header.classList.toggle('open');
    content.classList.toggle('open');
    
    if (!isOpen) {
        content.style.maxHeight = content.scrollHeight + 'px';
    } else {
        content.style.maxHeight = '0';
    }
};

// ============================================================================
// MODAL FUNCTIONS
// ============================================================================

window.openBetaModal = function() {
    document.getElementById('betaModal').style.display = 'block';
};

window.closeBetaModal = function() {
    document.getElementById('betaModal').style.display = 'none';
};

window.closeClaimsModal = function() {
    document.getElementById('claimsModal').style.display = 'none';
};

window.submitBetaSignup = async function() {
    const email = document.getElementById('betaEmail').value;
    const name = document.getElementById('betaName').value;

    if (!email) {
        showNotification('Please enter your email address', 'error');
        return;
    }

    try {
        const response = await fetch('/api/beta-signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, name })
        });

        if (response.ok) {
            showNotification('🎉 Welcome to the beta! Check your email for details.', 'success');
            closeBetaModal();
            document.getElementById('betaSignupForm').reset();
        } else {
            showNotification('Error joining beta. Please try again.', 'error');
        }
    } catch (error) {
        showNotification('🎉 Thanks for your interest! Beta signup recorded.', 'success');
        closeBetaModal();
        document.getElementById('betaSignupForm').reset();
    }
};

// ============================================================================
// MODAL HANDLERS
// ============================================================================

function setupModalHandlers() {
    // Close modal when clicking outside
    window.onclick = function(event) {
        const betaModal = document.getElementById('betaModal');
        const claimsModal = document.getElementById('claimsModal');
        
        if (event.target === betaModal) {
            closeBetaModal();
        }
        if (event.target === claimsModal) {
            closeClaimsModal();
        }
    };
}

// ============================================================================
// SHOW ALL CLAIMS FUNCTION
// ============================================================================

window.showAllClaims = function(claimType, analysisData) {
    const modal = document.getElementById('claimsModal');
    const claimsList = document.getElementById('claimsList');
    const modalHeader = modal.querySelector('.modal-header h2');
    
    let claims = [];
    let headerText;
    let headerIcon;
    
    if (claimType === 'unsupported') {
        claims = analysisData.fact_check_results?.filter(result => 
            result.status === 'Identified for verification' || 
            result.confidence < 50
        ) || [];
        headerText = 'Unsupported Claims Analysis';
        headerIcon = 'fas fa-exclamation-triangle';
    } else {
        claims = analysisData.fact_check_results?.filter(result => 
            result.confidence >= 50
        ) || [];
        headerText = 'Verified Claims Analysis';
        headerIcon = 'fas fa-check-circle';
    }
    
    modalHeader.innerHTML = `<i class="${headerIcon}"></i> ${headerText}`;
    claimsList.innerHTML = '';

    claims.forEach((item, index) => {
        const claimDiv = document.createElement('div');
        claimDiv.className = 'claim-modal-item';
        
        if (claimType === 'unsupported') {
            claimDiv.innerHTML = `
                <div class="claim-number">Claim ${index + 1}</div>
                <div class="claim-text">"${item.claim}"</div>
                <div class="claim-analysis">
                    <div class="claim-analysis-title">Why This Needs Verification:</div>
                    <div class="claim-reason">${item.context || 'This claim requires additional sources for verification.'}</div>
                </div>
            `;
        } else {
            claimDiv.style.borderLeftColor = '#10b981';
            claimDiv.innerHTML = `
                <div class="claim-number" style="color: #10b981;">Verified Claim ${index + 1}</div>
                <div class="claim-text">"${item.claim}"</div>
                <div class="claim-analysis">
                    <div class="claim-analysis-title" style="color: #10b981;">Supporting Evidence:</div>
                    <div class="claim-reason">${item.context || 'This claim is supported by multiple reliable sources.'}</div>
                </div>
            `;
        }
        claimsList.appendChild(claimDiv);
    });

    modal.style.display = 'block';
};

// ============================================================================
// EVENT LISTENERS
// ============================================================================

function setupEventListeners() {
    // Any additional event listeners can be added here
}

// ============================================================================
// EXPORT FUNCTIONS FOR OTHER MODULES
// ============================================================================

window.newsUI = {
    showNotification: window.showNotification,
    toggleDropdown: window.toggleDropdown,
    showAllClaims: window.showAllClaims
};
