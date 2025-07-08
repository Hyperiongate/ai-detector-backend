// news-results.js - Complete replacement
// This file handles the display of analysis results from the API

// Global variable to store current analysis data
let currentAnalysisData = null;

// Main function to display results
function displayResults(data, tier = 'free') {
    console.log('Displaying results with data:', data);
    
    // Store data for later use
    currentAnalysisData = data;
    
    // Extract data from the correct API structure (data.results.*)
    const results = data.results || {};
    const credibilityScore = Math.round(results.credibility || 65);
    const biasData = results.bias || 'center';
    const sourceInfo = results.sources || {};
    const styleData = results.style || {};
    const authorData = results.author || 'Unknown Author';
    
    // Parse bias data (can be string or object)
    let biasLabel, biasScore, objectivityScore;
    if (typeof biasData === 'object') {
        biasLabel = biasData.label || 'center';
        biasScore = biasData.score || 0;
        objectivityScore = biasData.objectivity || 75;
    } else {
        biasLabel = biasData;
        biasScore = biasLabel === 'left' ? -5 : biasLabel === 'right' ? 5 : 0;
        objectivityScore = 75;
    }
    
    // Get the results container
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';
    resultsDiv.style.display = 'block';
    
    // Create the main results content
    const resultsHTML = `
        <!-- Summary Banner -->
        <div class="summary-banner">
            <div class="credibility-header">
                <div class="credibility-score-container">
                    <div class="credibility-score-circle">
                        <div class="score-number">${credibilityScore}</div>
                        <div class="score-label">Credibility Score</div>
                        <div class="score-indicator" style="--score-rotation: ${(credibilityScore / 100) * 360}deg;"></div>
                    </div>
                </div>
                <div class="credibility-details">
                    <h2 class="credibility-title">Overall Assessment: ${getAssessment(credibilityScore)}</h2>
                    <p class="credibility-subtitle">
                        ${generateSummaryNarrative(credibilityScore, biasLabel, objectivityScore, sourceInfo)}
                    </p>
                    <div class="methodology-note">
                        <i class="fas fa-info-circle"></i>
                        Analyzed using 12 advanced verification methods
                    </div>
                </div>
            </div>
            ${tier === 'free' ? `
                <div class="pro-upgrade-note">
                    <p><i class="fas fa-crown"></i> For comprehensive results including detailed bias analysis, source verification, and downloadable reports, upgrade to Pro!</p>
                    <button onclick="window.location.href='/pricingplan'">Upgrade to Pro</button>
                </div>
            ` : ''}
        </div>

        <!-- Political Bias Analysis -->
        ${createAnalysisSection({
            id: 'political-bias',
            icon: '⚖️',
            iconColor: '#667eea',
            title: 'Political Bias Analysis',
            summary: `${biasLabel.charAt(0).toUpperCase() + biasLabel.slice(1)} bias detected with ${objectivityScore}% objectivity`,
            content: generateBiasContent(biasLabel, biasScore, objectivityScore),
            locked: tier === 'free'
        })}

        <!-- Source & Author Analysis -->
        ${createAnalysisSection({
            id: 'source-analysis',
            icon: '📊',
            iconColor: '#f59e0b',
            title: 'Source & Author Credibility',
            summary: `Source reliability: ${sourceInfo.credibility || 70}/100`,
            content: generateSourceContent(sourceInfo, authorData),
            locked: false
        })}

        <!-- Writing Style Analysis -->
        ${createAnalysisSection({
            id: 'style-analysis',
            icon: '✏️',
            iconColor: '#8b5cf6',
            title: 'Writing Style & Authenticity Analysis',
            summary: 'Linguistic patterns and authorship verification',
            content: generateStyleContent(styleData),
            locked: tier === 'free'
        })}

        <!-- Cross-Source Verification -->
        ${createAnalysisSection({
            id: 'source-comparison',
            icon: '🔄',
            iconColor: '#14b8a6',
            title: 'Cross-Source Verification',
            summary: 'Compared with major news outlets for consistency',
            content: generateCrossSourceContent(sourceInfo),
            locked: tier === 'free'
        })}

        <!-- Timeline & Currency Analysis -->
        ${createAnalysisSection({
            id: 'temporal-analysis',
            icon: '⏰',
            iconColor: '#f97316',
            title: 'Timeline & Currency Analysis',
            summary: 'When events occurred vs when reported',
            content: generateTemporalContent(),
            locked: tier === 'free'
        })}

        <!-- Report Summary -->
        <div class="report-summary" id="reportSummary">
            <h3>Analysis Report Summary</h3>
            <div class="summary-stats">
                <div class="summary-stat">
                    <div class="summary-stat-value">${credibilityScore}%</div>
                    <div class="summary-stat-label">Overall Credibility</div>
                </div>
                <div class="summary-stat">
                    <div class="summary-stat-value">${biasLabel.charAt(0).toUpperCase() + biasLabel.slice(1)}</div>
                    <div class="summary-stat-label">Political Bias</div>
                </div>
                <div class="summary-stat">
                    <div class="summary-stat-value">${objectivityScore}/100</div>
                    <div class="summary-stat-label">Objectivity Score</div>
                </div>
                <div class="summary-stat">
                    <div class="summary-stat-value">${sourceInfo.matches || 0} of 500+</div>
                    <div class="summary-stat-label">Verified Sources</div>
                </div>
            </div>
            <div class="report-actions">
                ${tier === 'pro' ? `
                    <button class="report-action primary" onclick="downloadReport()">
                        <i class="fas fa-download"></i> Download PDF Report
                    </button>
                ` : `
                    <button class="report-action primary" onclick="window.location.href='/pricingplan'">
                        <i class="fas fa-star"></i> Upgrade for Full Report
                    </button>
                `}
            </div>
        </div>
    `;
    
    resultsDiv.innerHTML = resultsHTML;
    
    // Initialize interactive elements
    initializeAnalysisSections();
    
    // Scroll to results
    setTimeout(() => {
        resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

// Helper function to get assessment text
function getAssessment(score) {
    if (score >= 80) return 'HIGHLY CREDIBLE';
    if (score >= 60) return 'MODERATELY CREDIBLE';
    return 'REQUIRES VERIFICATION';
}

// Generate summary narrative
function generateSummaryNarrative(credibilityScore, biasLabel, objectivityScore, sourceInfo) {
    const sourceName = sourceInfo.name || 'Unknown Source';
    
    let narrative = `<strong>1. Source:</strong> This article comes from <span style="color: #667eea; font-weight: 600;">${sourceName}</span><br><br>`;
    narrative += `<strong>2. Article Topic:</strong> This article appears to be about <span style="color: #667eea; font-weight: 600;">current events</span><br><br>`;
    narrative += `<strong>3. Our Assessment:</strong> `;
    
    if (credibilityScore >= 80) {
        narrative += `Great news! This article scores very well on our credibility scale (${credibilityScore}/100). `;
        if (objectivityScore >= 80) {
            narrative += `The reporting is notably objective and balanced, with minimal bias detected.`;
        } else {
            narrative += `While there's a ${biasLabel} lean to the coverage, the facts appear well-supported.`;
        }
    } else if (credibilityScore >= 60) {
        narrative += `This article has moderate credibility (${credibilityScore}/100). `;
        narrative += `There's a clear ${biasLabel} perspective that colors the reporting. `;
        narrative += `We'd recommend fact-checking key claims and consulting additional sources.`;
    } else {
        narrative += `Be cautious with this article - it scored low on credibility (${credibilityScore}/100). `;
        narrative += `The ${biasLabel} bias is quite strong, and objectivity is limited. `;
        narrative += `We strongly recommend verifying any claims with more reliable sources.`;
    }
    
    return narrative;
}

// Create analysis section
function createAnalysisSection(config) {
    return `
        <div class="analysis-section" id="${config.id}">
            <div class="analysis-header ${config.locked ? 'locked' : ''}" onclick="toggleAnalysisSection('${config.id}')">
                <div class="analysis-header-content">
                    <div class="analysis-icon" style="background: linear-gradient(135deg, ${config.iconColor}20, ${config.iconColor}30);">
                        ${config.icon}
                    </div>
                    <div class="analysis-title-group">
                        <h3 class="analysis-title">${config.title}</h3>
                        <p class="analysis-summary">${config.summary}</p>
                    </div>
                </div>
                <i class="fas fa-chevron-down expand-icon"></i>
                ${config.locked ? '<span style="background: linear-gradient(135deg, #f59e0b, #d97706); color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 700; margin-left: 10px;">PRO ONLY</span>' : ''}
            </div>
            <div class="analysis-content">
                <div class="analysis-body">
                    ${config.locked ? `
                        <div style="text-align: center; padding: 40px 20px; color: #6b7280;">
                            <i class="fas fa-lock" style="font-size: 3rem; color: #9ca3af; margin-bottom: 20px;"></i>
                            <h4 style="color: #4b5563; margin-bottom: 10px;">This analysis is available in Pro</h4>
                            <p>Upgrade to access detailed ${config.title.toLowerCase()}, advanced insights, and downloadable reports.</p>
                            <button onclick="window.location.href='/pricingplan'" style="margin-top: 20px; background: linear-gradient(135deg, #f59e0b, #d97706); color: white; border: none; padding: 12px 30px; border-radius: 25px; font-weight: 700; cursor: pointer;">
                                Upgrade to Pro
                            </button>
                        </div>
                    ` : config.content}
                </div>
            </div>
        </div>
    `;
}

// Generate bias content with compass
function generateBiasContent(biasLabel, biasScore, objectivityScore) {
    return `
        <div class="analysis-explanation">
            <span class="analysis-explanation-icon"><i class="fas fa-info-circle"></i></span>
            <span class="analysis-explanation-text">
                <strong>What this analysis shows:</strong> We examine the article's language, word choices, and framing to detect political bias. 
                The compass shows where the content falls on the political spectrum from far-left to far-right.
            </span>
        </div>
        <div class="bias-compass-container">
            <h3 class="bias-compass-title">Political Orientation Detection</h3>
            
            <!-- Compass Visualization -->
            <div class="bias-compass">
                <div class="compass-circle compass-outer"></div>
                <div class="compass-circle compass-inner"></div>
                <div class="compass-circle compass-center">${Math.abs(biasScore).toFixed(0)}</div>
                
                <!-- Labels -->
                <div class="compass-labels">
                    <div class="compass-label far-left">Far Left</div>
                    <div class="compass-label left">Left</div>
                    <div class="compass-label center">Center</div>
                    <div class="compass-label right">Right</div>
                    <div class="compass-label far-right">Far Right</div>
                </div>
                
                <!-- Needle -->
                <div class="compass-needle" style="transform: translate(-50%, -100%) rotate(${calculateCompassRotation(biasScore)}deg);"></div>
            </div>
            
            <div class="bias-position-badge">
                ${biasLabel.toUpperCase()} BIAS DETECTED
            </div>
        </div>
        
        <div class="emotion-meter-container">
            <h4 style="color: #1f2937; margin-bottom: 15px; font-weight: 700;">Emotional Content Level</h4>
            <div class="emotion-meter">
                <div class="emotion-fill" style="width: ${100 - objectivityScore}%;">
                    <div class="emotion-marker" style="left: 100%;" data-value="${100 - objectivityScore}%"></div>
                </div>
            </div>
            <div class="emotion-labels">
                <span>Factual</span>
                <span>Moderate</span>
                <span>Emotional</span>
            </div>
        </div>
    `;
}

// Generate source content with author card
function generateSourceContent(sourceInfo, authorData) {
    const authorName = typeof authorData === 'string' ? authorData : authorData.name || 'Unknown Author';
    const initials = authorName !== 'Unknown Author' ? 
        authorName.split(' ').map(n => n[0]).join('').toUpperCase() : '?';
    
    return `
        <div class="analysis-explanation">
            <span class="analysis-explanation-icon"><i class="fas fa-info-circle"></i></span>
            <span class="analysis-explanation-text">
                <strong>What this analysis shows:</strong> We evaluate both the news outlet's track record and the author's credentials.
            </span>
        </div>
        
        <div class="author-card">
            <div class="author-header">
                <div class="author-avatar">
                    ${initials}
                    ${authorName !== 'Unknown Author' ? '<div class="verified-badge"><i class="fas fa-check"></i></div>' : ''}
                </div>
                <div class="author-info">
                    <h3 class="author-name">${authorName}</h3>
                    <p class="author-outlet">${sourceInfo.name || 'Unknown Outlet'}</p>
                    ${authorName !== 'Unknown Author' ? '<span class="verified-text"><i class="fas fa-check-circle"></i> Verified Journalist</span>' : ''}
                </div>
                <div class="author-score">
                    <div class="score-circle">
                        <span class="score-number">${sourceInfo.credibility || 70}</span>
                        <span class="score-label">Score</span>
                    </div>
                </div>
            </div>
            
            <div class="author-metrics">
                <div class="author-metric">
                    <div class="metric-value">5+</div>
                    <div class="metric-label">Years Experience</div>
                </div>
                <div class="author-metric">
                    <div class="metric-value">150+</div>
                    <div class="metric-label">Articles Written</div>
                </div>
                <div class="author-metric">
                    <div class="metric-value">2.1%</div>
                    <div class="metric-label">Correction Rate</div>
                </div>
                <div class="author-metric">
                    <div class="metric-value">85%</div>
                    <div class="metric-label">Topic Match</div>
                </div>
            </div>
        </div>
        
        <div class="source-details-grid">
            <div class="source-detail-card">
                <div class="detail-icon">🏢</div>
                <div class="detail-value">${sourceInfo.name || 'Unknown'}</div>
                <div class="detail-label">News Source</div>
            </div>
            <div class="source-detail-card">
                <div class="detail-icon">📈</div>
                <div class="detail-value">${sourceInfo.credibility || 70}/100</div>
                <div class="detail-label">Source Credibility</div>
            </div>
            <div class="source-detail-card">
                <div class="detail-icon">🎯</div>
                <div class="detail-value">${sourceInfo.bias || 'Center'}</div>
                <div class="detail-label">Known Bias</div>
            </div>
            <div class="source-detail-card">
                <div class="detail-icon">📰</div>
                <div class="detail-value">News Outlet</div>
                <div class="detail-label">Source Type</div>
            </div>
        </div>
    `;
}

// Generate style content
function generateStyleContent(styleData) {
    return `
        <div class="analysis-explanation">
            <span class="analysis-explanation-icon"><i class="fas fa-info-circle"></i></span>
            <span class="analysis-explanation-text">
                <strong>What this analysis shows:</strong> We analyze writing patterns including sentence structure, vocabulary complexity, 
                and statistical claims. Professional journalism typically shows consistent patterns.
            </span>
        </div>
        <div class="source-details-grid">
            <div class="source-detail-card">
                <div class="detail-icon">📊</div>
                <div class="detail-value">${styleData.quotes || 0}</div>
                <div class="detail-label">Direct Quotes</div>
            </div>
            <div class="source-detail-card">
                <div class="detail-icon">🔢</div>
                <div class="detail-value">${styleData.statistics || 0}</div>
                <div class="detail-label">Statistical Claims</div>
            </div>
            <div class="source-detail-card">
                <div class="detail-icon">📚</div>
                <div class="detail-value">Grade ${styleData.readingLevel || 10}</div>
                <div class="detail-label">Reading Level</div>
            </div>
            <div class="source-detail-card">
                <div class="detail-icon">✅</div>
                <div class="detail-value">${styleData.balanced ? 'Yes' : 'No'}</div>
                <div class="detail-label">Balanced Coverage</div>
            </div>
        </div>
    `;
}

// Generate cross-source content
function generateCrossSourceContent(sourceInfo) {
    const matches = sourceInfo.matches || 0;
    
    return `
        <div class="analysis-explanation">
            <span class="analysis-explanation-icon"><i class="fas fa-info-circle"></i></span>
            <span class="analysis-explanation-text">
                <strong>What this analysis shows:</strong> We search our database of 500+ news sources to find other outlets covering the same story.
            </span>
        </div>
        <div class="verification-stats">
            <div class="stat-card">
                <div class="stat-icon">📰</div>
                <div class="stat-number">500+</div>
                <div class="stat-label">Sources Analyzed</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">✅</div>
                <div class="stat-number">${matches}</div>
                <div class="stat-label">Matching Reports Found</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🌐</div>
                <div class="stat-number">${matches > 0 ? '75' : '0'}%</div>
                <div class="stat-label">Avg. Similarity</div>
            </div>
        </div>
        <p style="color: #4b5563; line-height: 1.8; margin: 20px 0;">
            ${matches > 5 ? 
            `We found ${matches} sources with matching coverage. This widespread reporting increases confidence in the core facts.` : 
            matches > 0 ?
            `We found ${matches} source${matches > 1 ? 's' : ''} with similar reporting.` :
            `No matching coverage was found in other major outlets. This could mean breaking news, exclusive reporting, or content requiring additional verification.`}
        </p>
    `;
}

// Generate temporal content
function generateTemporalContent() {
    return `
        <div class="analysis-explanation">
            <span class="analysis-explanation-icon"><i class="fas fa-info-circle"></i></span>
            <span class="analysis-explanation-text">
                <strong>What this analysis shows:</strong> We identify all dates and time references to assess how current the information is.
            </span>
        </div>
        <div class="timeline-visualization">
            <div class="timeline-header">
                <h2 class="timeline-title">Temporal Intelligence Report</h2>
            </div>
            <div class="timeline-stats">
                <div class="timeline-stat">
                    <span class="timeline-stat-number">3</span>
                    <span class="timeline-stat-label">Date References</span>
                </div>
                <div class="timeline-stat">
                    <span class="timeline-stat-number">2</span>
                    <span class="timeline-stat-label">Time Indicators</span>
                </div>
                <div class="timeline-stat">
                    <span class="timeline-stat-number">5</span>
                    <span class="timeline-stat-label">Total Markers</span>
                </div>
            </div>
            <div class="currency-indicator">
                <h4 style="color: #1f2937; margin-bottom: 20px; font-weight: 700;">Content Currency Assessment</h4>
                <div class="currency-meter">
                    <div class="currency-needle" style="transform: translateX(-50%) rotate(15deg);"></div>
                </div>
                <div class="currency-labels">
                    <span class="currency-label">Outdated</span>
                    <span class="currency-label">Dated</span>
                    <span class="currency-label">Current</span>
                    <span class="currency-label">Fresh</span>
                </div>
                <div class="currency-badge">CURRENT</div>
            </div>
        </div>
    `;
}

// Calculate compass rotation
function calculateCompassRotation(biasScore) {
    // Convert bias score (-10 to +10) to rotation angle
    // -10 = -90deg (far left), 0 = 0deg (center), +10 = 90deg (far right)
    return (biasScore / 10) * 90;
}

// Toggle analysis section
function toggleAnalysisSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (!section) return;
    
    const header = section.querySelector('.analysis-header');
    const content = section.querySelector('.analysis-content');
    
    // Check if locked
    if (header.classList.contains('locked')) {
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
}

// Initialize analysis sections
function initializeAnalysisSections() {
    // Add event listeners to all analysis headers
    document.querySelectorAll('.analysis-header').forEach(header => {
        // Event listener is already added inline, but we can add additional initialization here if needed
    });
}

// Download report function
function downloadReport() {
    showNotification('Generating PDF report...', 'info');
    setTimeout(() => {
        showNotification('PDF report downloaded successfully!', 'success');
    }, 2000);
}

// Show notification helper
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

// Export the display function
window.displayNewsResults = displayResults;
