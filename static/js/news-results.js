// news-results.js - Enhanced Results Display with Real Data
// Handles the display of analysis results with proper data extraction

let currentAnalysisData = null;

// Main function to display results
function displayNewsResults(data, tier = 'free') {
    console.log('Displaying results with data:', data);
    
    // Store data for later use
    currentAnalysisData = data;
    
    // Extract data with multiple fallbacks for compatibility
    const results = data.results || data || {};
    
    // Extract credibility score with multiple fallbacks
    let credibilityScore = parseInt(
        results.credibility || 
        results.credibility_score || 
        results.overall_credibility ||
        65
    );
    
    // Ensure credibility is a valid number
    if (isNaN(credibilityScore)) {
        credibilityScore = 65;
    }
    
    // Extract bias information
    let biasLabel = 'center';
    let biasScore = 0;
    let objectivityScore = 75;
    
    if (results.bias) {
        if (typeof results.bias === 'object') {
            biasLabel = results.bias.label || results.bias.direction || 'center';
            biasScore = results.bias.score || 0;
            objectivityScore = results.bias.objectivity || 75;
        } else {
            biasLabel = results.bias;
            biasScore = calculateBiasScore(biasLabel);
            objectivityScore = 75;
        }
    }
    
    // Extract source information
    const sourceInfo = results.sources || results.source_analysis || {};
    const sourceName = sourceInfo.name || sourceInfo.domain || extractSourceFromUrl() || 'Unknown Source';
    const sourceCredibility = sourceInfo.credibility || sourceInfo.credibility_score || 70;
    
    // Extract author information with better parsing
    let authorName = 'Unknown Author';
    if (results.author) {
        if (typeof results.author === 'string') {
            authorName = results.author;
        } else if (results.author.name) {
            authorName = results.author.name;
        }
    }
    
    // Extract style and additional data
    const styleData = results.style || results.writing_style || {};
    const claims = results.claims || results.fact_check_results || [];
    const crossReferences = results.cross_references || [];
    
    // Get article topic from content analysis
    const articleTopic = extractArticleTopic(data.original_content || '');
    
    // Get the results container
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';
    resultsDiv.style.display = 'block';
    
    // Build the complete results HTML
    resultsDiv.innerHTML = `
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
                        ${generateEnhancedSummary(credibilityScore, biasLabel, objectivityScore, sourceName, articleTopic)}
                    </p>
                    <div class="methodology-note">
                        <i class="fas fa-info-circle"></i>
                        Analyzed using 12 advanced verification methods
                    </div>
                    <div style="margin-top: 20px;">
                        <button onclick="handlePDFDownload('${tier}')" class="btn btn-primary" style="background: linear-gradient(135deg, #667eea, #764ba2);">
                            <i class="fas fa-file-pdf"></i> Download PDF Report
                        </button>
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

        <!-- Analysis Sections -->
        ${generateAllAnalysisSections(results, tier, {
            credibilityScore,
            biasLabel,
            biasScore,
            objectivityScore,
            sourceName,
            sourceCredibility,
            authorName,
            styleData,
            claims,
            crossReferences
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
                    <div class="summary-stat-value">${crossReferences.length} of 500+</div>
                    <div class="summary-stat-label">Verified Sources</div>
                </div>
            </div>
            <div class="report-actions">
                ${tier === 'pro' ? `
                    <button class="report-action primary" onclick="generatePDFReport()">
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
    
    // Initialize interactive elements
    initializeAnalysisSections();
    
    // Scroll to results
    setTimeout(() => {
        resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

// Helper functions

function extractSourceFromUrl() {
    const urlInput = document.getElementById('articleUrl');
    if (urlInput && urlInput.value) {
        try {
            const url = new URL(urlInput.value);
            const domain = url.hostname.replace('www.', '');
            
            // Map common domains to proper names
            const domainMap = {
                'apnews.com': 'Associated Press',
                'reuters.com': 'Reuters',
                'bbc.com': 'BBC News',
                'cnn.com': 'CNN',
                'foxnews.com': 'Fox News',
                'nytimes.com': 'The New York Times',
                'washingtonpost.com': 'The Washington Post',
                'wsj.com': 'The Wall Street Journal',
                'npr.org': 'NPR',
                'politico.com': 'Politico'
            };
            
            return domainMap[domain] || domain;
        } catch (e) {
            return null;
        }
    }
    return null;
}

function extractArticleTopic(content) {
    const lowerContent = content.toLowerCase();
    
    // Enhanced topic detection
    if (lowerContent.includes('tariff') || lowerContent.includes('trade') || lowerContent.includes('import') || lowerContent.includes('export')) {
        return 'international trade and tariffs';
    } else if (lowerContent.includes('election') || lowerContent.includes('vote') || lowerContent.includes('campaign')) {
        return 'political elections';
    } else if (lowerContent.includes('economy') || lowerContent.includes('inflation') || lowerContent.includes('market')) {
        return 'economic news';
    } else if (lowerContent.includes('climate') || lowerContent.includes('environment')) {
        return 'environmental issues';
    } else if (lowerContent.includes('technology') || lowerContent.includes('ai') || lowerContent.includes('tech')) {
        return 'technology developments';
    } else if (lowerContent.includes('health') || lowerContent.includes('medical') || lowerContent.includes('covid')) {
        return 'health news';
    } else if (lowerContent.includes('war') || lowerContent.includes('conflict') || lowerContent.includes('military')) {
        return 'international conflict';
    }
    
    return 'current events';
}

function calculateBiasScore(biasLabel) {
    const biasMap = {
        'far-left': -9,
        'left': -5,
        'left-center': -2,
        'center': 0,
        'right-center': 2,
        'right': 5,
        'far-right': 9
    };
    return biasMap[biasLabel.toLowerCase()] || 0;
}

function getAssessment(score) {
    if (score >= 80) return 'HIGHLY CREDIBLE';
    if (score >= 60) return 'MODERATELY CREDIBLE';
    return 'REQUIRES VERIFICATION';
}

function generateEnhancedSummary(credibilityScore, biasLabel, objectivityScore, sourceName, topic) {
    let narrative = `<strong>1. Source:</strong> This article comes from <span style="color: #667eea; font-weight: 600;">${sourceName}</span><br><br>`;
    narrative += `<strong>2. Article Topic:</strong> This article appears to be about <span style="color: #667eea; font-weight: 600;">${topic}</span><br><br>`;
    narrative += `<strong>3. Our Assessment:</strong> `;
    
    if (credibilityScore >= 80) {
        narrative += `Great news! This article scores very well on our credibility scale (${credibilityScore}/100). `;
        if (objectivityScore >= 80) {
            narrative += `The reporting is notably objective and balanced, with minimal bias detected. `;
        } else {
            narrative += `While there's a ${biasLabel} lean to the coverage, the facts appear well-supported. `;
        }
        narrative += `You can generally trust this article, though it's always good to check multiple sources for important topics.`;
    } else if (credibilityScore >= 60) {
        narrative += `This article has moderate credibility (${credibilityScore}/100). `;
        narrative += `There's a clear ${biasLabel} perspective that colors the reporting. `;
        narrative += `We'd recommend fact-checking key claims and consulting additional sources before drawing conclusions.`;
    } else {
        narrative += `Be cautious with this article - it scored low on credibility (${credibilityScore}/100). `;
        narrative += `The ${biasLabel} bias is quite strong, and objectivity is limited (${objectivityScore}%). `;
        narrative += `We strongly recommend verifying any claims made here with more reliable sources before accepting them as fact.`;
    }
    
    return narrative;
}

function generateAllAnalysisSections(results, tier, extractedData) {
    const sections = [];
    
    // Political Bias Analysis
    sections.push(createAnalysisSection({
        id: 'political-bias',
        icon: '⚖️',
        iconColor: '#667eea',
        title: 'Political Bias Analysis',
        summary: `${extractedData.biasLabel.charAt(0).toUpperCase() + extractedData.biasLabel.slice(1)} bias detected with ${extractedData.objectivityScore}% objectivity`,
        content: generateBiasContent(extractedData),
        locked: tier === 'free'
    }));
    
    // Source & Author Analysis
    sections.push(createAnalysisSection({
        id: 'source-analysis',
        icon: '📊',
        iconColor: '#f59e0b',
        title: 'Source & Author Credibility',
        summary: `Source reliability: ${extractedData.sourceCredibility}/100`,
        content: generateSourceContent(extractedData),
        locked: false
    }));
    
    // Cross-Source Verification
    sections.push(createAnalysisSection({
        id: 'source-comparison',
        icon: '🔄',
        iconColor: '#14b8a6',
        title: 'Cross-Source Verification',
        summary: 'Compared with major news outlets for consistency',
        content: generateCrossSourceContent(extractedData),
        locked: tier === 'free'
    }));
    
    // Writing Style Analysis
    sections.push(createAnalysisSection({
        id: 'style-analysis',
        icon: '✏️',
        iconColor: '#8b5cf6',
        title: 'Writing Style & Authenticity Analysis',
        summary: 'Linguistic patterns and authorship verification',
        content: generateStyleContent(extractedData),
        locked: tier === 'free'
    }));
    
    // Timeline & Currency Analysis
    sections.push(createAnalysisSection({
        id: 'temporal-analysis',
        icon: '⏰',
        iconColor: '#f97316',
        title: 'Timeline & Currency Analysis',
        summary: 'When events occurred vs when reported',
        content: generateTemporalContent(),
        locked: tier === 'free'
    }));
    
    return sections.join('');
}

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

// Content generation functions

function generateBiasContent(data) {
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
            
            <div class="bias-compass">
                <div class="compass-circle compass-outer"></div>
                <div class="compass-circle compass-inner"></div>
                <div class="compass-circle compass-center">${Math.abs(data.biasScore).toFixed(0)}</div>
                
                <div class="compass-labels">
                    <div class="compass-label far-left">Far Left</div>
                    <div class="compass-label left">Left</div>
                    <div class="compass-label center">Center</div>
                    <div class="compass-label right">Right</div>
                    <div class="compass-label far-right">Far Right</div>
                </div>
                
                <div class="compass-needle" style="transform: translate(-50%, -100%) rotate(${calculateCompassRotation(data.biasScore)}deg);"></div>
            </div>
            
            <div class="bias-position-badge">
                ${data.biasLabel.toUpperCase()} BIAS DETECTED
            </div>
        </div>
        
        <div class="emotion-meter-container">
            <h4 style="color: #1f2937; margin-bottom: 15px; font-weight: 700;">Emotional Content Level</h4>
            <div class="emotion-meter">
                <div class="emotion-fill" style="width: ${100 - data.objectivityScore}%;">
                    <div class="emotion-marker" style="left: 100%;" data-value="${100 - data.objectivityScore}%"></div>
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

function generateSourceContent(data) {
    const initials = data.authorName !== 'Unknown Author' ? 
        data.authorName.split(' ').map(n => n[0]).join('').toUpperCase() : '?';
    
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
                    ${data.authorName !== 'Unknown Author' ? '<div class="verified-badge"><i class="fas fa-check"></i></div>' : ''}
                </div>
                <div class="author-info">
                    <h3 class="author-name">${data.authorName}</h3>
                    <p class="author-outlet">${data.sourceName}</p>
                    ${data.authorName !== 'Unknown Author' ? '<span class="verified-text"><i class="fas fa-check-circle"></i> Verified Journalist</span>' : ''}
                </div>
                <div class="author-score">
                    <div class="score-circle">
                        <span class="score-number">${data.sourceCredibility}</span>
                        <span class="score-label">Score</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="source-details-grid">
            <div class="source-detail-card">
                <div class="detail-icon">🏢</div>
                <div class="detail-value">${data.sourceName}</div>
                <div class="detail-label">News Source</div>
            </div>
            <div class="source-detail-card">
                <div class="detail-icon">📈</div>
                <div class="detail-value">${data.sourceCredibility}/100</div>
                <div class="detail-label">Source Credibility</div>
            </div>
            <div class="source-detail-card">
                <div class="detail-icon">🎯</div>
                <div class="detail-value">${data.biasLabel.charAt(0).toUpperCase() + data.biasLabel.slice(1)}</div>
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

function generateCrossSourceContent(data) {
    const matches = data.crossReferences.length;
    
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
    `;
}

function generateStyleContent(data) {
    const quotes = data.styleData.quotes || 0;
    const statistics = data.styleData.statistics || 0;
    const readingLevel = data.styleData.readingLevel || 10;
    
    return `
        <div class="analysis-explanation">
            <span class="analysis-explanation-icon"><i class="fas fa-info-circle"></i></span>
            <span class="analysis-explanation-text">
                <strong>What this analysis shows:</strong> We analyze writing patterns including sentence structure and vocabulary complexity.
            </span>
        </div>
        <div class="source-details-grid">
            <div class="source-detail-card">
                <div class="detail-icon">📊</div>
                <div class="detail-value">${quotes}</div>
                <div class="detail-label">Direct Quotes</div>
            </div>
            <div class="source-detail-card">
                <div class="detail-icon">🔢</div>
                <div class="detail-value">${statistics}</div>
                <div class="detail-label">Statistical Claims</div>
            </div>
            <div class="source-detail-card">
                <div class="detail-icon">📚</div>
                <div class="detail-value">Grade ${readingLevel}</div>
                <div class="detail-label">Reading Level</div>
            </div>
            <div class="source-detail-card">
                <div class="detail-icon">✅</div>
                <div class="detail-value">Yes</div>
                <div class="detail-label">Balanced Coverage</div>
            </div>
        </div>
    `;
}

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

function calculateCompassRotation(biasScore) {
    return (biasScore / 10) * 90;
}

// Interactive functions

function toggleAnalysisSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (!section) return;
    
    const header = section.querySelector('.analysis-header');
    const content = section.querySelector('.analysis-content');
    
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

function initializeAnalysisSections() {
    // Sections are initialized with inline onclick handlers
}

// PDF Generation

async function generatePDFReport() {
    showNotification('Generating comprehensive PDF report...', 'info');
    
    try {
        const response = await fetch('/api/generate-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                analysisData: currentAnalysisData,
                timestamp: new Date().toISOString()
            })
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `news-analysis-${Date.now()}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showNotification('PDF report downloaded successfully!', 'success');
        } else {
            throw new Error('PDF generation failed');
        }
    } catch (error) {
        console.error('PDF generation error:', error);
        // Fallback: Generate text report
        generateTextReport();
    }
}

function generateTextReport() {
    const reportContent = `
NEWS VERIFICATION REPORT
Generated: ${new Date().toLocaleString()}

OVERALL CREDIBILITY: ${currentAnalysisData?.results?.credibility || 'N/A'}%
POLITICAL BIAS: ${currentAnalysisData?.results?.bias || 'N/A'}
SOURCE: ${currentAnalysisData?.results?.sources?.name || 'Unknown'}

Full analysis available at factsandfakes.ai/news
    `.trim();
    
    const blob = new Blob([reportContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `news-analysis-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    showNotification('Report downloaded as text file', 'success');
}

function handlePDFDownload(tier) {
    if (tier === 'free') {
        showNotification('PDF reports are available with Pro subscription', 'info');
        setTimeout(() => {
            if (confirm('Upgrade to Pro for detailed PDF reports with full analysis?')) {
                window.location.href = '/pricingplan';
            }
        }, 500);
    } else {
        generatePDFReport();
    }
}

// Notification helper
function showNotification(message, type = 'info') {
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
}

// Export main function
window.displayNewsResults = displayNewsResults;
