// News Results Display Functions

// Update Summary Tab
function updateSummaryTab(data) {
    const container = document.getElementById('summary-content');
    if (!container || !data) return;
    
    container.innerHTML = `
        <div class="summary-section">
            <h3>Article Summary</h3>
            <p>${data.summary || 'No summary available'}</p>
            
            ${data.key_points ? `
                <h4>Key Points</h4>
                <ul>
                    ${data.key_points.map(point => `<li>${point}</li>`).join('')}
                </ul>
            ` : ''}
            
            ${data.main_claims ? `
                <h4>Main Claims</h4>
                <ul>
                    ${data.main_claims.map(claim => `<li>${claim}</li>`).join('')}
                </ul>
            ` : ''}
        </div>
    `;
}

// Update Bias Tab
function updateBiasTab(data) {
    const container = document.getElementById('bias-content');
    if (!container || !data) return;
    
    container.innerHTML = `
        <div class="bias-analysis">
            <h3>Political Bias Analysis</h3>
            
            <div class="bias-meter">
                <div class="bias-scale">
                    <div class="bias-indicator" style="left: ${getBiasPosition(data.bias_score)}%"></div>
                </div>
                <div class="bias-labels">
                    <span>Far Left</span>
                    <span>Left</span>
                    <span>Center</span>
                    <span>Right</span>
                    <span>Far Right</span>
                </div>
            </div>
            
            <div class="bias-details">
                <p><strong>Detected Bias:</strong> ${data.bias_rating || 'Neutral'}</p>
                <p><strong>Confidence:</strong> ${data.confidence || 'Medium'}</p>
                
                ${data.bias_indicators ? `
                    <h4>Bias Indicators</h4>
                    <ul>
                        ${data.bias_indicators.map(indicator => `<li>${indicator}</li>`).join('')}
                    </ul>
                ` : ''}
                
                ${data.loaded_language ? `
                    <h4>Loaded Language Examples</h4>
                    <ul>
                        ${data.loaded_language.map(example => `<li>"${example}"</li>`).join('')}
                    </ul>
                ` : ''}
            </div>
        </div>
    `;
}

// Update Sources Tab
function updateSourcesTab(data) {
    const container = document.getElementById('sources-content');
    if (!container || !data) return;
    
    container.innerHTML = `
        <div class="sources-analysis">
            <h3>Source Diversity Analysis</h3>
            
            <div class="source-stats">
                <div class="stat-item">
                    <span class="stat-value">${data.total_sources || 0}</span>
                    <span class="stat-label">Total Sources</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${data.unique_sources || 0}</span>
                    <span class="stat-label">Unique Sources</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${data.source_types || 'N/A'}</span>
                    <span class="stat-label">Source Types</span>
                </div>
            </div>
            
            ${data.source_list ? `
                <h4>Sources Referenced</h4>
                <ul class="source-list">
                    ${data.source_list.map(source => `
                        <li>
                            <strong>${source.name}</strong>
                            <span class="source-type">${source.type}</span>
                            ${source.bias ? `<span class="source-bias">${source.bias}</span>` : ''}
                        </li>
                    `).join('')}
                </ul>
            ` : ''}
            
            ${data.missing_perspectives ? `
                <h4>Potentially Missing Perspectives</h4>
                <ul>
                    ${data.missing_perspectives.map(perspective => `<li>${perspective}</li>`).join('')}
                </ul>
            ` : ''}
        </div>
    `;
}

// Update Credibility Tab
function updateCredibilityTab(data) {
    const container = document.getElementById('credibility-content');
    if (!container || !data) return;
    
    container.innerHTML = `
        <div class="credibility-analysis">
            <h3>Credibility Assessment</h3>
            
            <div class="credibility-score">
                <div class="score-circle">
                    <span class="score-value">${data.credibility_score || 'N/A'}</span>
                    <span class="score-label">Credibility Score</span>
                </div>
            </div>
            
            <div class="credibility-factors">
                ${data.source_reliability ? `
                    <div class="factor-item">
                        <h4>Source Reliability</h4>
                        <p>${data.source_reliability}</p>
                    </div>
                ` : ''}
                
                ${data.fact_checking ? `
                    <div class="factor-item">
                        <h4>Fact Checking Results</h4>
                        <ul>
                            ${data.fact_checking.map(fact => `<li>${fact}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${data.transparency_issues ? `
                    <div class="factor-item">
                        <h4>Transparency Issues</h4>
                        <ul>
                            ${data.transparency_issues.map(issue => `<li>${issue}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

// Update Cross-Source Tab (renamed from updateVerificationTab)
function updateCrossSourceTab(data) {
    const container = document.getElementById('cross-source-content');
    if (!container || !data) return;
    
    container.innerHTML = `
        <div class="cross-source-analysis">
            <h3>Cross-Source Verification</h3>
            
            ${data.verification_status ? `
                <div class="verification-status ${data.verification_status.toLowerCase()}">
                    <span class="status-icon">${getStatusIcon(data.verification_status)}</span>
                    <span class="status-text">${data.verification_status}</span>
                </div>
            ` : ''}
            
            ${data.corroborating_sources ? `
                <h4>Corroborating Sources</h4>
                <ul>
                    ${data.corroborating_sources.map(source => `<li>${source}</li>`).join('')}
                </ul>
            ` : ''}
            
            ${data.conflicting_reports ? `
                <h4>Conflicting Reports</h4>
                <ul>
                    ${data.conflicting_reports.map(report => `<li>${report}</li>`).join('')}
                </ul>
            ` : ''}
            
            ${data.fact_check_results ? `
                <h4>Fact Check Results</h4>
                <div class="fact-check-results">
                    ${data.fact_check_results.map(result => `
                        <div class="fact-check-item">
                            <strong>${result.claim}</strong>
                            <span class="fact-status ${result.status.toLowerCase()}">${result.status}</span>
                            <p>${result.explanation}</p>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        </div>
    `;
}

// Update Author Tab
function updateAuthorTab(data) {
    const container = document.getElementById('author-content');
    if (!container || !data) return;
    
    container.innerHTML = `
        <div class="author-analysis">
            <h3>Author Information</h3>
            
            ${data.author_name ? `
                <div class="author-profile">
                    <h4>${data.author_name}</h4>
                    ${data.author_bio ? `<p>${data.author_bio}</p>` : ''}
                    ${data.author_credentials ? `<p><strong>Credentials:</strong> ${data.author_credentials}</p>` : ''}
                </div>
            ` : '<p>Author information not available</p>'}
            
            ${data.author_history ? `
                <h4>Publication History</h4>
                <ul>
                    ${data.author_history.map(item => `<li>${item}</li>`).join('')}
                </ul>
            ` : ''}
            
            ${data.expertise_alignment ? `
                <h4>Expertise Alignment</h4>
                <p>${data.expertise_alignment}</p>
            ` : ''}
            
            ${data.potential_conflicts ? `
                <h4>Potential Conflicts of Interest</h4>
                <ul>
                    ${data.potential_conflicts.map(conflict => `<li>${conflict}</li>`).join('')}
                </ul>
            ` : ''}
        </div>
    `;
}

// Update Writing Style Tab (renamed from updateStyleTab)
function updateWritingStyleTab(data) {
    const container = document.getElementById('style-content');
    if (!container || !data) return;
    
    container.innerHTML = `
        <div class="style-analysis">
            <h3>Writing Style Analysis</h3>
            
            <div class="style-metrics">
                ${data.tone ? `
                    <div class="metric-item">
                        <h4>Tone</h4>
                        <p>${data.tone}</p>
                    </div>
                ` : ''}
                
                ${data.complexity ? `
                    <div class="metric-item">
                        <h4>Complexity Level</h4>
                        <p>${data.complexity}</p>
                    </div>
                ` : ''}
                
                ${data.emotional_language ? `
                    <div class="metric-item">
                        <h4>Emotional Language Score</h4>
                        <p>${data.emotional_language}</p>
                    </div>
                ` : ''}
            </div>
            
            ${data.persuasion_techniques ? `
                <h4>Detected Persuasion Techniques</h4>
                <ul>
                    ${data.persuasion_techniques.map(technique => `<li>${technique}</li>`).join('')}
                </ul>
            ` : ''}
            
            ${data.rhetorical_devices ? `
                <h4>Rhetorical Devices Used</h4>
                <ul>
                    ${data.rhetorical_devices.map(device => `<li>${device}</li>`).join('')}
                </ul>
            ` : ''}
        </div>
    `;
}

// Update Temporal Tab
function updateTemporalTab(data) {
    const container = document.getElementById('temporal-content');
    if (!container || !data) return;
    
    container.innerHTML = `
        <div class="temporal-analysis">
            <h3>Temporal Intelligence</h3>
            
            ${data.publication_date ? `
                <p><strong>Publication Date:</strong> ${data.publication_date}</p>
            ` : ''}
            
            ${data.last_updated ? `
                <p><strong>Last Updated:</strong> ${data.last_updated}</p>
            ` : ''}
            
            ${data.timeliness_score ? `
                <div class="timeliness-score">
                    <h4>Timeliness Score</h4>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${data.timeliness_score}%"></div>
                    </div>
                    <p>${data.timeliness_score}% current</p>
                </div>
            ` : ''}
            
            ${data.temporal_context ? `
                <h4>Temporal Context</h4>
                <p>${data.temporal_context}</p>
            ` : ''}
            
            ${data.related_timeline ? `
                <h4>Related Events Timeline</h4>
                <ul class="timeline">
                    ${data.related_timeline.map(event => `
                        <li>
                            <strong>${event.date}</strong>: ${event.description}
                        </li>
                    `).join('')}
                </ul>
            ` : ''}
        </div>
    `;
}

// Update Pro Features Tab (renamed from updateProTab)
function updateProFeaturesTab() {
    const container = document.getElementById('pro-content');
    if (!container) return;
    
    container.innerHTML = `
        <div class="pro-features">
            <h3>Unlock Advanced Analysis</h3>
            <p>Upgrade to Pro for access to:</p>
            <ul>
                <li>Deep learning sentiment analysis</li>
                <li>Network analysis of information spread</li>
                <li>Predictive bias modeling</li>
                <li>Custom analysis parameters</li>
                <li>API access for automation</li>
                <li>Bulk article processing</li>
                <li>Advanced visualizations</li>
                <li>Export detailed reports</li>
            </ul>
            <button class="upgrade-button" onclick="window.location.href='/pricing'">Upgrade to Pro</button>
        </div>
    `;
}

// Helper Functions
function getBiasPosition(score) {
    // Convert bias score (-100 to 100) to position (0 to 100)
    if (!score) return 50;
    return ((score + 100) / 200) * 100;
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
