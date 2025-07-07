// News Results Display Functions

// Enhanced Update Summary Tab
function updateSummaryTab(data) {
    const container = document.getElementById('summary-content');
    if (!container || !data) return;
    
    // Calculate visual scores
    const biasScore = data.bias_score || 0;
    const credibilityScore = data.credibility_score || 75;
    const biasPosition = ((biasScore + 100) / 200) * 100;
    
    container.innerHTML = `
        <div class="summary-section">
            <!-- Article Info -->
            <div class="article-info">
                <h3>Article Information</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <strong>Source:</strong> ${data.source || 'Unknown Source'}
                    </div>
                    <div class="info-item">
                        <strong>Author:</strong> ${data.author || 'Not specified'}
                    </div>
                    <div class="info-item">
                        <strong>Date:</strong> ${data.publication_date || 'Not available'}
                    </div>
                </div>
            </div>
            
            <!-- Article Summary -->
            <div class="article-summary">
                <h3>What This Article Is About</h3>
                <p>${data.summary || 'No summary available'}</p>
                
                ${data.key_points && data.key_points.length > 0 ? `
                    <h4>Key Points:</h4>
                    <ul class="key-points">
                        ${data.key_points.slice(0, 3).map(point => `<li>${point}</li>`).join('')}
                    </ul>
                ` : ''}
            </div>
            
            <!-- Analysis Scores -->
            <div class="analysis-scores">
                <h3>Analysis Results</h3>
                
                <!-- Bias Score -->
                <div class="score-section">
                    <h4>Political Bias</h4>
                    <div class="bias-meter">
                        <div class="bias-scale">
                            <div class="bias-indicator" style="left: ${biasPosition}%">
                                <div class="bias-tooltip">${getBiasLabel(biasScore)}</div>
                            </div>
                        </div>
                        <div class="bias-labels">
                            <span>Far Left</span>
                            <span>Left</span>
                            <span>Center</span>
                            <span>Right</span>
                            <span>Far Right</span>
                        </div>
                    </div>
                    <p class="bias-description">${data.bias_summary || 'This article appears to be politically neutral.'}</p>
                </div>
                
                <!-- Credibility Score -->
                <div class="score-section">
                    <h4>Credibility Score</h4>
                    <div class="credibility-meter">
                        <div class="score-circle ${getCredibilityClass(credibilityScore)}">
                            <span class="score-value">${credibilityScore}%</span>
                        </div>
                        <p class="score-label">${getCredibilityLabel(credibilityScore)}</p>
                    </div>
                    <p class="credibility-description">${data.credibility_summary || 'Based on source reputation and content analysis.'}</p>
                </div>
            </div>
            
            <!-- Overall Findings -->
            <div class="overall-findings">
                <h3>Overall Findings</h3>
                <div class="findings-summary">
                    ${data.overall_assessment || `
                        <p>This article has been analyzed for political bias and credibility. 
                        ${getBiasLabel(biasScore) === 'Center' ? 'It appears to be relatively balanced in its political perspective.' : `It shows a ${getBiasLabel(biasScore)} political leaning.`}
                        The credibility score of ${credibilityScore}% indicates ${getCredibilityLabel(credibilityScore).toLowerCase()} reliability.</p>
                    `}
                </div>
            </div>
            
            <!-- Pro Upgrade Prompt -->
            <div class="pro-prompt">
                <h4>Want Deeper Insights?</h4>
                <p>Unlock detailed bias indicators, source verification, author background checks, and more with Pro!</p>
                <button class="upgrade-button-small" onclick="window.location.href='/pricing'">
                    See Pro Features
                </button>
            </div>
        </div>
    `;
}

// Update Bias Tab - Pro Feature
function updateBiasTab(data) {
    const container = document.getElementById('bias-content');
    if (!container) return;
    
    container.innerHTML = `
        <div class="pro-feature-preview">
            <div class="lock-icon">🔒</div>
            <h3>Advanced Political Bias Analysis</h3>
            <p>Unlock detailed insights including:</p>
            <ul class="feature-list">
                <li>Sentence-by-sentence bias detection</li>
                <li>Loaded language identification</li>
                <li>Framing analysis</li>
                <li>Historical bias patterns of the source</li>
                <li>Comparison with similar articles</li>
            </ul>
            <div class="sample-preview">
                <h4>Sample from this article:</h4>
                <p class="sample-text">"${data.sample_biased_text || 'Advanced bias analysis available in Pro version'}"</p>
            </div>
            <button class="upgrade-cta" onclick="window.location.href='/pricing'">
                Unlock Full Bias Analysis
            </button>
            <p class="trial-info">✨ Pro users can analyze unlimited articles. Free trial available!</p>
        </div>
    `;
}

// Update Sources Tab - Pro Feature
function updateSourcesTab(data) {
    const container = document.getElementById('sources-content');
    if (!container) return;
    
    container.innerHTML = `
        <div class="pro-feature-preview">
            <div class="lock-icon">🔒</div>
            <h3>Source Diversity Analysis</h3>
            <p>Pro members get access to:</p>
            <ul class="feature-list">
                <li>Complete source mapping</li>
                <li>Source credibility ratings</li>
                <li>Missing perspective analysis</li>
                <li>Echo chamber detection</li>
                <li>Source relationship networks</li>
            </ul>
            <button class="upgrade-cta" onclick="window.location.href='/pricing'">
                View All Sources
            </button>
        </div>
    `;
}

// Update Credibility Tab - Pro Feature
function updateCredibilityTab(data) {
    const container = document.getElementById('credibility-content');
    if (!container) return;
    
    container.innerHTML = `
        <div class="pro-feature-preview">
            <div class="lock-icon">🔒</div>
            <h3>Deep Credibility Check</h3>
            <p>Get comprehensive credibility analysis:</p>
            <ul class="feature-list">
                <li>Source reliability history</li>
                <li>Fact-checking results</li>
                <li>Citation quality analysis</li>
                <li>Transparency scoring</li>
                <li>Domain authority metrics</li>
            </ul>
            <button class="upgrade-cta" onclick="window.location.href='/pricing'">
                Access Full Report
            </button>
        </div>
    `;
}

// Update Cross-Source Tab - Pro Feature
function updateCrossSourceTab(data) {
    const container = document.getElementById('cross-source-content');
    if (!container) return;
    
    container.innerHTML = `
        <div class="pro-feature-preview">
            <div class="lock-icon">🔒</div>
            <h3>Cross-Source Verification</h3>
            <p>Verify claims across multiple sources:</p>
            <ul class="feature-list">
                <li>Automatic fact-checking</li>
                <li>Claim verification across 100+ sources</li>
                <li>Contradiction detection</li>
                <li>Consensus analysis</li>
                <li>Real-time updates</li>
            </ul>
            <button class="upgrade-cta" onclick="window.location.href='/pricing'">
                Unlock Verification Tools
            </button>
        </div>
    `;
}

// Update Author Tab - Pro Feature
function updateAuthorTab(data) {
    const container = document.getElementById('author-content');
    if (!container) return;
    
    container.innerHTML = `
        <div class="pro-feature-preview">
            <div class="lock-icon">🔒</div>
            <h3>Author Background Check</h3>
            <p>Learn about article authors:</p>
            <ul class="feature-list">
                <li>Author credentials and expertise</li>
                <li>Publication history analysis</li>
                <li>Potential conflicts of interest</li>
                <li>Social media presence</li>
                <li>Previous work bias patterns</li>
            </ul>
            <button class="upgrade-cta" onclick="window.location.href='/pricing'">
                View Author Analysis
            </button>
        </div>
    `;
}

// Update Writing Style Tab - Pro Feature
function updateWritingStyleTab(data) {
    const container = document.getElementById('style-content');
    if (!container) return;
    
    container.innerHTML = `
        <div class="pro-feature-preview">
            <div class="lock-icon">🔒</div>
            <h3>Writing Style Analysis</h3>
            <p>Understand how the article influences readers:</p>
            <ul class="feature-list">
                <li>Emotional language detection</li>
                <li>Persuasion technique identification</li>
                <li>Rhetorical device analysis</li>
                <li>Tone and sentiment mapping</li>
                <li>Manipulation tactics detection</li>
            </ul>
            <button class="upgrade-cta" onclick="window.location.href='/pricing'">
                Analyze Writing Style
            </button>
        </div>
    `;
}

// Update Temporal Tab - Pro Feature
function updateTemporalTab(data) {
    const container = document.getElementById('temporal-content');
    if (!container) return;
    
    container.innerHTML = `
        <div class="pro-feature-preview">
            <div class="lock-icon">🔒</div>
            <h3>Temporal Intelligence</h3>
            <p>Track news evolution over time:</p>
            <ul class="feature-list">
                <li>Story development timeline</li>
                <li>Information freshness scoring</li>
                <li>Update frequency analysis</li>
                <li>Historical context mapping</li>
                <li>Predictive trend analysis</li>
            </ul>
            <button class="upgrade-cta" onclick="window.location.href='/pricing'">
                Access Timeline Analysis
            </button>
        </div>
    `;
}

// Update Pro Features Tab
function updateProFeaturesTab() {
    const container = document.getElementById('pro-content');
    if (!container) return;
    
    container.innerHTML = `
        <div class="pro-features">
            <h3>🚀 Unlock Advanced Analysis</h3>
            <p>Take your news analysis to the next level with Pro:</p>
            
            <div class="pro-benefits">
                <div class="benefit-card">
                    <h4>Unlimited Analysis</h4>
                    <p>Analyze as many articles as you want, whenever you want</p>
                </div>
                <div class="benefit-card">
                    <h4>Deep Learning AI</h4>
                    <p>Advanced algorithms for more accurate bias and credibility detection</p>
                </div>
                <div class="benefit-card">
                    <h4>Real-time Verification</h4>
                    <p>Cross-reference claims across hundreds of trusted sources instantly</p>
                </div>
                <div class="benefit-card">
                    <h4>API Access</h4>
                    <p>Integrate our analysis tools into your own applications</p>
                </div>
            </div>
            
            <div class="pricing-info">
                <h4>Special Offer</h4>
                <p class="price">$9.99/month</p>
                <p class="savings">Save 20% with annual billing</p>
            </div>
            
            <button class="upgrade-button-large" onclick="window.location.href='/pricing'">
                Start Free Trial
            </button>
            
            <p class="guarantee">30-day money-back guarantee • Cancel anytime</p>
        </div>
    `;
}

// Helper Functions
function getBiasLabel(score) {
    if (score < -60) return 'Far Left';
    if (score < -20) return 'Left';
    if (score < 20) return 'Center';
    if (score < 60) return 'Right';
    return 'Far Right';
}

function getCredibilityClass(score) {
    if (score >= 80) return 'high';
    if (score >= 60) return 'medium';
    return 'low';
}

function getCredibilityLabel(score) {
    if (score >= 80) return 'High Credibility';
    if (score >= 60) return 'Moderate Credibility';
    if (score >= 40) return 'Low Credibility';
    return 'Very Low Credibility';
}

function getStatusIcon(status) {
    const icons = {
        'Verified': '✓',
        'Unverified': '?',
        'Disputed': '⚠',
        'False': '✗'
    };
    return icons[status] || '?';
}
