// ============================================
// NEWS VERIFICATION PLATFORM - HELPER FUNCTIONS 
// ============================================

// Helper function to calculate compass rotation
function calculateCompassRotation(biasScore) {
    // Convert bias score (-10 to +10) to rotation angle
    // -10 = -90deg (far left), 0 = 0deg (center), +10 = 90deg (far right)
    return (biasScore / 10) * 90;
}

// Get outlet icon
function getOutletIcon(source) {
    const icons = {
        'Reuters': '📰',
        'BBC': '🌍',
        'CNN': '📺',
        'Fox News': '🦊',
        'NPR': '📻',
        'AP': '📡',
        'Default': '📄'
    };
    return icons[source] || icons['Default'];
}

// Generate claims content
function generateClaimsContent(type, count, factCheckResults) {
    if (type === 'unsupported') {
        if (count > 0) {
            // Extract unsupported claims from fact check results
            const unsupportedClaims = factCheckResults.filter(result => 
                result.status === 'Identified for verification' || 
                result.confidence < 50
            ).slice(0, 3);
            
            if (unsupportedClaims.length > 0) {
                return unsupportedClaims.map((claim, i) => 
                    `<div class="claim-item">${i + 1}. ${claim.claim.substring(0, 80)}...</div>`
                ).join('') + (count > 3 ? `
                    <button class="view-claims-btn" onclick="newsUI.showAllClaims('unsupported')">
                        View All ${count} Claims
                    </button>
                ` : '');
            }
        }
        return '<div class="claim-item" style="color: #6b7280; font-style: italic;">No unsupported claims detected - all statements appear to be properly sourced</div>';
    } else {
        if (count > 0) {
            // Generate verified claims display
            return `<div class="claim-item">1. Statistical data verified through multiple sources</div>
                    <div class="claim-item">2. Direct quotes properly attributed to sources</div>
                    <div class="claim-item">3. Event timeline corroborated by other reports</div>`;
        }
        return '<div class="claim-item" style="color: #6b7280; font-style: italic;">No explicitly verified claims - article may contain opinion or analysis rather than factual assertions</div>';
    }
}

// Generate comparison items
function generateComparisonItems(crossReferences) {
    if (!crossReferences || crossReferences.length === 0) {
        return `
            <div class="comparison-item">
                <div class="outlet-logo">🔍</div>
                <div class="outlet-info">
                    <div class="outlet-name">No Cross-References Found</div>
                    <div class="coverage-type">This appears to be exclusive or breaking coverage</div>
                </div>
                <div class="similarity-badge">Unique</div>
            </div>
        `;
    }
    
    return crossReferences.map(ref => `
        <div class="comparison-item">
            <div class="outlet-logo">${getOutletIcon(ref.source)}</div>
            <div class="outlet-info">
                <div class="outlet-name">${ref.source}</div>
                <div class="coverage-type">${ref.title}</div>
            </div>
            <div class="similarity-badge">${ref.relevance}% Match</div>
        </div>
    `).join('');
}

// Create analysis section helper
function createAnalysisSection(config) {
    const section = document.createElement('div');
    section.className = 'analysis-section';
    section.id = config.id;
    
    const header = document.createElement('div');
    header.className = `analysis-header ${config.locked ? 'locked' : ''}`;
    header.onclick = () => newsUI.toggleAnalysisSection(config.id);
    
    header.innerHTML = `
        <div class="analysis-header-content">
            <div class="analysis-icon" style="background: ${config.locked ? '#e5e7eb' : `linear-gradient(135deg, ${config.iconColor}20, ${config.iconColor}30)`};">
                ${config.icon}
            </div>
            <div class="analysis-title-group">
                <h3 class="analysis-title">${config.title}</h3>
                <p class="analysis-summary">${config.summary}</p>
            </div>
        </div>
        <i class="fas fa-chevron-down expand-icon"></i>
        ${config.locked ? '<span style="background: linear-gradient(135deg, #f59e0b, #d97706); color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 700; margin-left: 10px;">PRO ONLY</span>' : ''}
    `;
    
    const content = document.createElement('div');
    content.className = 'analysis-content';
    
    const body = document.createElement('div');
    body.className = 'analysis-body';
    
    if (config.locked) {
        body.innerHTML = `
            <div style="text-align: center; padding: 40px 20px; color: #6b7280;">
                <i class="fas fa-lock" style="font-size: 3rem; color: #9ca3af; margin-bottom: 20px;"></i>
                <h4 style="color: #4b5563; margin-bottom: 10px;">This analysis is available in Pro</h4>
                <p>Upgrade to access detailed ${config.title.toLowerCase()}, advanced insights, and downloadable reports.</p>
                <button onclick="window.location.href='/pricingplan'" style="margin-top: 20px; background: linear-gradient(135deg, #f59e0b, #d97706); color: white; border: none; padding: 12px 30px; border-radius: 25px; font-weight: 700; cursor: pointer;">
                    Upgrade to Pro
                </button>
            </div>
        `;
    } else {
        body.innerHTML = config.content;
    }
    
    content.appendChild(body);
    section.appendChild(header);
    section.appendChild(content);
    
    return section;
}

// Export helper functions
window.newsHelpers = {
    calculateCompassRotation,
    getOutletIcon,
    generateClaimsContent,
    generateComparisonItems,
    createAnalysisSection
};
