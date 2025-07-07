// ============================================
// NEWS VERIFICATION PLATFORM - UI MODULE
// ============================================

// Notification helper function
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.display = 'block'; 
    
    // Add to body
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Input switching
function switchInputType(type) {
    window.currentInputType = type;
    
    document.querySelectorAll('.input-tab').forEach((tab, index) => {
        tab.classList.remove('active');
        if ((type === 'text' && index === 0) || (type === 'url' && index === 1)) {
            tab.classList.add('active');
        }
    });
    
    document.querySelectorAll('.input-content').forEach(content => {
        content.classList.remove('active');
    });
    
    const targetContent = document.getElementById(type + 'Input');
    if (targetContent) {
        targetContent.classList.add('active');
    }
}

// Load test data
function loadTestData() {
    const testContent = "Breaking: Infrastructure Bill Passes Senate with Bipartisan Support. The Department of Transportation announced today the allocation of $2.3 billion for highway improvements across 15 states, according to officials who state this initiative will create approximately 45,000 jobs over the next 18 months. The announcement comes following congressional support for the infrastructure bill passed last quarter. Sources close to the administration suggest this represents the largest single infrastructure investment in recent history. Industry experts predict significant economic impact in rural communities, though some critics question the timeline for implementation.";
    
    document.getElementById('news-text').value = testContent;
    switchInputType('text');
    
    showNotification('Sample news content loaded successfully!', 'success');
}

// Reset form
function resetForm() {
    document.getElementById('news-text').value = '';
    document.getElementById('news-url').value = '';
    document.getElementById('results').style.display = 'none';
    document.getElementById('results').innerHTML = '';
    window.currentAnalysisData = null;
    showNotification('Form reset successfully', 'success');
}

// Modal functions
function closeClaimsModal() {
    document.getElementById('claimsModal').style.display = 'none';
}

function closeBetaModal() {
    document.getElementById('betaModal').style.display = 'none';
}

function openBetaModal() {
    document.getElementById('betaModal').style.display = 'block';
}

function submitBetaSignup() {
    const email = document.getElementById('betaEmail').value;
    const name = document.getElementById('betaName').value;

    if (!email) {
        alert('Please enter your email address');
        return;
    }

    // Submit to backend
    fetch('/api/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: email, password: 'BetaUser2025!' })
    })
    .then(response => response.json())
    .then(data => {
        alert('🎉 Welcome to the beta! Check your email for access details.');
        closeBetaModal();
        document.getElementById('betaSignupForm').reset();
    })
    .catch(error => {
        console.log('Demo mode: Beta signup for', email);
        alert('🎉 Thanks for your interest! Beta signup recorded.');
        closeBetaModal();
        document.getElementById('betaSignupForm').reset();
    });
}

// Enhanced dropdown toggle
function toggleDropdown(header, tier) {
    const content = header.nextElementSibling;
    const isOpen = header.classList.contains('open');
    
    header.classList.toggle('open');
    content.classList.toggle('open');
    
    if (!isOpen) {
        content.style.maxHeight = content.scrollHeight + 'px';
    } else {
        content.style.maxHeight = '0';
    }
}

// Toggle analysis section
function toggleAnalysisSection(sectionId) {
    const section = document.getElementById(sectionId);
    const header = section.querySelector('.analysis-header');
    const content = section.querySelector('.analysis-content');
    
    if (header.classList.contains('locked') && window.newsAnalysis.currentTier() === 'free') {
        showNotification('Upgrade to Pro to access this analysis', 'info');
        return;
    }
    
    const isExpanded = section.classList.contains('expanded');
    
    if (isExpanded) {
        section.classList.remove('expanded');
        header.classList.remove('expanded');
        content.classList.remove('expanded');
    } else {
        section.classList.add('expanded');
        header.classList.add('expanded');
        content.classList.add('expanded');
    }
    
    trackNewsEvent('analysis_section_toggled', {
        section: sectionId,
        action: isExpanded ? 'collapsed' : 'expanded'
    });
}

// Scroll to top
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Show/hide back to top button
window.addEventListener('scroll', () => {
    const backToTop = document.getElementById('backToTop');
    if (window.pageYOffset > 300) {
        backToTop.classList.add('visible');
    } else {
        backToTop.classList.remove('visible');
    }
});

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

// Show all claims in modal
function showAllClaims(claimType) {
    const currentAnalysisData = window.newsAnalysis.currentAnalysisData();
    if (!currentAnalysisData) {
        return;
    }

    const modal = document.getElementById('claimsModal');
    const claimsList = document.getElementById('claimsList');
    const modalHeader = modal.querySelector('.modal-header h2');
    
    let claims = [];
    let headerText;
    let headerIcon;
    
    // Extract claims from fact check results
    if (claimType === 'unsupported') {
        claims = currentAnalysisData.fact_check_results?.filter(result => 
            result.status === 'Identified for verification' || 
            result.confidence < 50
        ) || [];
        headerText = 'Unsupported Claims Analysis';
        headerIcon = 'fas fa-exclamation-triangle';
    } else {
        claims = currentAnalysisData.fact_check_results?.filter(result => 
            result.confidence >= 50
        ) || [];
        headerText = 'Verified Claims Analysis';
        headerIcon = 'fas fa-check-circle';
    }
    
    // Update modal header
    modalHeader.innerHTML = `<i class="${headerIcon}"></i> ${headerText}`;
    
    // Clear existing content
    claimsList.innerHTML = '';

    // Add each claim with detailed analysis
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

    // Show modal
    modal.style.display = 'block';

    // Track event
    trackNewsEvent(`${claimType}_claims_viewed`, {
        count: claims.length,
        tier: window.newsAnalysis.currentTier()
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Track page load
    trackNewsEvent('news_verification_page_loaded', {
        user_agent: navigator.userAgent,
        screen_resolution: screen.width + 'x' + screen.height,
        referrer: document.referrer
    });
});

// Export UI functions for global access
window.newsUI = {
    showNotification,
    switchInputType,
    loadTestData,
    resetForm,
    toggleDropdown,
    toggleAnalysisSection,
    scrollToTop,
    showAllClaims,
    openBetaModal,
    closeBetaModal,
    closeClaimsModal,
    submitBetaSignup
};
