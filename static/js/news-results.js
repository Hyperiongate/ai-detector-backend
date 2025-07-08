// static/js/news-results.js - Enhanced with all visual components

// Global variable to store current analysis data
let currentAnalysisData = null;

// ============================================================================
// MAIN DISPLAY FUNCTION
// ============================================================================

function displayResults(data, tier = 'pro') {
    console.log('Displaying results with data:', data);
    currentAnalysisData = data;
    
    const resultsDiv = document.getElementById('results');
    
    // Make sure results div exists
    if (!resultsDiv) {
        console.error('Results div not found!');
        return;
    }
    
    // Show results section
    resultsDiv.style.display = 'block';
    
    // Find or create tab-contents div
    let tabContents = document.getElementById('tab-contents');
    if (!tabContents) {
        // If tab-contents doesn't exist, look for the tabs container
        const tabsContainer = resultsDiv.querySelector('.tabs-container');
        if (tabsContainer) {
            tabContents = tabsContainer.querySelector('#tab-contents');
            if (!tabContents) {
                // Create tab-contents if it doesn't exist
                tabContents = document.createElement('div');
                tabContents.id = 'tab-contents';
                tabsContainer.appendChild(tabContents);
            }
        }
    }
    
    // Clear previous content
    if (tabContents) {
        tabContents.innerHTML = '';
    } else {
        // Fallback: just put content directly in results
        resultsDiv.innerHTML = `<div id="tab-contents"></div>`;
        tabContents = document.getElementById('tab-contents');
    }
    
    // Create tab contents
    createSummaryTab(data, tier);
    createBiasTab(data, tier);
    createSourcesTab(data, tier);
    createCredibilityTab(data, tier);
    createCrossSourceTab(data, tier);
    createAuthorTab(data, tier);
    createStyleTab(data, tier);
    createTemporalTab(data, tier);
    createProTab(data, tier);
    
    // Activate first tab
    switchTab('summary');
}

// ============================================================================
// TAB SWITCHING
// ============================================================================

window.switchTab = function(tabName) {
    // Update active tab button
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Find and activate the correct tab
    const tabs = document.querySelectorAll('.tab');
    const tabIndex = getTabIndex(tabName) - 1;
    if (tabs[tabIndex]) {
        tabs[tabIndex].classList.add('active');
    }
    
    // Update active tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
        content.style.display = 'none';
    });
    
    const targetContent = document.getElementById(`${tabName}-content`);
    if (targetContent) {
        targetContent.classList.add('active');
        targetContent.style.display = 'block';
    }
};

function getTabIndex(tabName) {
    const tabMap = {
        'summary': 1, 'bias': 2, 'sources': 3, 'credibility': 4,
        'cross-source': 5, 'author': 6, 'style': 7, 'temporal': 8, 'pro': 9
    };
    return tabMap[tabName] || 1;
}

// ============================================================================
// SUMMARY TAB - With Credibility Circle
// ============================================================================

function createSummaryTab(data, tier) {
    const credibilityScore = Math.round(data.credibility_score || 65);
    const assessment = credibilityScore >= 80 ? 'HIGHLY CREDIBLE' : 
                      credibilityScore >= 60 ? 'MODERATELY CREDIBLE' : 
                      'REQUIRES VERIFICATION';
    
    const summaryHTML = `
    <div class="tab-content active" id="summary-content" style="display: block;">
        <div class="summary-banner" style="background: rgba(0,0,0,0.8); border: 2px solid rgba(0,255,255,0.3); border-radius: 20px; padding: 40px; margin-bottom: 30px;">
            <div class="credibility-header" style="display: flex; align-items: center; gap: 40px; margin-bottom: 30px; flex-wrap: wrap;">
                ${createCredibilityCircle(credibilityScore)}
                <div class="credibility-details" style="flex: 1; min-width: 300px;">
                    <h2 class="credibility-title" style="font-size: 2.5rem; font-weight: 800; color: #00ffff; margin-bottom: 15px;">
                        Overall Assessment: ${assessment}
                    </h2>
                    <p class="credibility-subtitle" style="font-size: 1.2rem; color: #fff; line-height: 1.8; opacity: 0.9;">
                        ${generateSummaryNarrative(data)}
                    </p>
                    <div class="methodology-note" style="margin-top: 20px; display: inline-flex; align-items: center; gap: 10px; background: rgba(0,255,255,0.1); padding: 10px 20px; border-radius: 25px; color: #00ffff;">
                        <i class="fas fa-info-circle"></i>
                        Analyzed using 12 advanced verification methods
                    </div>
                </div>
            </div>
            
            <!-- Quick Stats Grid -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 30px;">
                <div style="background: rgba(0,255,255,0.1); border: 1px solid rgba(0,255,255,0.3); border-radius: 15px; padding: 20px; text-align: center;">
                    <div style="font-size: 2rem; font-weight: 800; color: #00ffff;">${credibilityScore}%</div>
                    <div style="color: #fff; opacity: 0.8;">Credibility</div>
                </div>
                <div style="background: rgba(255,0,255,0.1); border: 1px solid rgba(255,0,255,0.3); border-radius: 15px; padding: 20px; text-align: center;">
                    <div style="font-size: 2rem; font-weight: 800; color: #ff00ff;">${(data.political_bias?.bias_label || 'Center').toUpperCase()}</div>
                    <div style="color: #fff; opacity: 0.8;">Political Bias</div>
                </div>
                <div style="background: rgba(0,255,136,0.1); border: 1px solid rgba(0,255,136,0.3); border-radius: 15px; padding: 20px; text-align: center;">
                    <div style="font-size: 2rem; font-weight: 800; color: #00ff88;">${data.political_bias?.objectivity_score || 75}%</div>
                    <div style="color: #fff; opacity: 0.8;">Objectivity</div>
                </div>
                <div style="background: rgba(255,255,0,0.1); border: 1px solid rgba(255,255,0,0.3); border-radius: 15px; padding: 20px; text-align: center;">
                    <div style="font-size: 2rem; font-weight: 800; color: #ffff00;">${data.cross_references?.length || 0}</div>
                    <div style="color: #fff; opacity: 0.8;">Sources Found</div>
                </div>
            </div>
        </div>
        
        <!-- Key Findings -->
        <div style="background: rgba(0,0,0,0.6); border: 1px solid rgba(0,255,255,0.3); border-radius: 20px; padding: 30px;">
            <h3 style="color: #00ffff; font-size: 1.8rem; margin-bottom: 20px;">🔍 Key Findings</h3>
            ${generateKeyFindings(data)}
        </div>
    </div>`;
    
    const tabContents = document.getElementById('tab-contents');
    if (tabContents) {
        tabContents.insertAdjacentHTML('beforeend', summaryHTML);
    }
}

// ============================================================================
// BIAS TAB - With Compass Visualization
// ============================================================================

function createBiasTab(data, tier) {
    const biasData = data.political_bias || {};
    const biasScore = biasData.bias_score || 0;
    const biasLabel = biasData.bias_label || 'center';
    
    const biasHTML = `
    <div class="tab-content" id="bias-content" style="display: none;">
        <div style="background: rgba(0,0,0,0.8); border: 2px solid rgba(255,0,255,0.3); border-radius: 20px; padding: 40px;">
            <h2 style="color: #ff00ff; font-size: 2rem; margin-bottom: 30px; text-align: center;">⚖️ Political Bias Analysis</h2>
            
            ${createBiasCompass(biasScore, biasLabel)}
            
            <div style="margin-top: 40px; background: rgba(255,0,255,0.1); border-radius: 15px; padding: 25px;">
                <h3 style="color: #ff00ff; margin-bottom: 15px;">Bias Indicators Detected:</h3>
                <p style="color: #fff; line-height: 1.8; opacity: 0.9;">
                    ${generateBiasNarrative(biasData)}
                </p>
                
                <!-- Loaded Terms -->
                ${biasData.loaded_terms && biasData.loaded_terms.length > 0 ? `
                <div style="margin-top: 20px;">
                    <h4 style="color: #ff00ff;">Emotionally Charged Language:</h4>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;">
                        ${biasData.loaded_terms.map(term => 
                            `<span style="background: rgba(255,0,255,0.2); padding: 6px 14px; border-radius: 20px; 
                            border: 1px solid rgba(255,0,255,0.4); color: #fff;">
                            ${term}</span>`
                        ).join('')}
                    </div>
                </div>` : ''}
            </div>
            
            ${createClaimsGrid(data)}
        </div>
    </div>`;
    
    const tabContents = document.getElementById('tab-contents');
    if (tabContents) {
        tabContents.insertAdjacentHTML('beforeend', biasHTML);
    }
}

// ============================================================================
// SOURCES TAB
// ============================================================================

function createSourcesTab(data, tier) {
    const sourceData = data.source_analysis || {};
    
    const sourcesHTML = `
    <div class="tab-content" id="sources-content" style="display: none;">
        <div style="background: rgba(0,0,0,0.8); border: 2px solid rgba(0,255,136,0.3); border-radius: 20px; padding: 40px;">
            <h2 style="color: #00ff88; font-size: 2rem; margin-bottom: 30px; text-align: center;">🌐 Source Diversity Analysis</h2>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px;">
                <div style="background: rgba(0,255,136,0.1); border-radius: 15px; padding: 25px;">
                    <h3 style="color: #00ff88; margin-bottom: 15px;">Primary Source</h3>
                    <p style="color: #fff; font-size: 1.3rem; margin-bottom: 10px;">${sourceData.domain || 'Unknown Source'}</p>
                    <p style="color: #fff; opacity: 0.8;">Type: ${sourceData.source_type || 'News Outlet'}</p>
                    <p style="color: #fff; opacity: 0.8;">Credibility: ${sourceData.credibility_score || 70}/100</p>
                    <p style="color: #fff; opacity: 0.8;">Known Bias: ${sourceData.political_bias || 'Center'}</p>
                </div>
                
                <div style="background: rgba(0,255,136,0.1); border-radius: 15px; padding: 25px;">
                    <h3 style="color: #00ff88; margin-bottom: 15px;">Source Metrics</h3>
                    <div style="display: grid; gap: 10px;">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: #fff; opacity: 0.8;">Factual Reporting:</span>
                            <span style="color: #00ff88; font-weight: 600;">${sourceData.factual_reporting || 'High'}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: #fff; opacity: 0.8;">Media Type:</span>
                            <span style="color: #00ff88; font-weight: 600;">${sourceData.media_type || 'Digital'}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: #fff; opacity: 0.8;">Traffic Rank:</span>
                            <span style="color: #00ff88; font-weight: 600;">${sourceData.traffic_rank || 'Top 1000'}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 30px; background: rgba(0,255,136,0.1); border-radius: 15px; padding: 25px;">
                <h3 style="color: #00ff88; margin-bottom: 15px;">Source Analysis</h3>
                <p style="color: #fff; line-height: 1.8; opacity: 0.9;">
                    ${generateSourceNarrative(sourceData)}
                </p>
            </div>
        </div>
    </div>`;
    
    const tabContents = document.getElementById('tab-contents');
    if (tabContents) {
        tabContents.insertAdjacentHTML('beforeend', sourcesHTML);
    }
}

// ============================================================================
// VISUAL COMPONENTS
// ============================================================================

function createCredibilityCircle(score) {
    return `
    <div class="credibility-score-container" style="position: relative; flex-shrink: 0;">
        <div class="credibility-score-circle" style="width: 200px; height: 200px; position: relative;">
            <svg width="200" height="200" style="transform: rotate(-90deg);">
                <circle cx="100" cy="100" r="90" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="20"/>
                <circle cx="100" cy="100" r="90" fill="none" 
                    stroke="url(#gradient)" 
                    stroke-width="20"
                    stroke-dasharray="${2 * Math.PI * 90 * score / 100} ${2 * Math.PI * 90}"
                    stroke-linecap="round"/>
                <defs>
                    <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#00ffff;stop-opacity:1" />
                        <stop offset="50%" style="stop-color:#00ff88;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#ffff00;stop-opacity:1" />
                    </linearGradient>
                </defs>
            </svg>
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                <div style="font-size: 3.5rem; font-weight: 900; color: #00ffff;">${score}</div>
                <div style="color: #fff; opacity: 0.8;">Credibility Score</div>
            </div>
        </div>
    </div>`;
}

function createBiasCompass(biasScore, biasLabel) {
    const rotation = (biasScore / 10) * 90;
    
    return `
    <div class="bias-compass-container" style="text-align: center; margin: 30px 0;">
        <div class="bias-compass" style="position: relative; width: 300px; height: 300px; margin: 0 auto;">
            <!-- Background circles -->
            <div style="position: absolute; width: 300px; height: 300px; border-radius: 50%; 
                background: linear-gradient(45deg, #3b82f6 0%, #10b981 25%, #fbbf24 50%, #f59e0b 75%, #ef4444 100%);
                top: 50%; left: 50%; transform: translate(-50%, -50%);"></div>
            <div style="position: absolute; width: 200px; height: 200px; border-radius: 50%; 
                background: rgba(0,0,0,0.8); top: 50%; left: 50%; transform: translate(-50%, -50%);"></div>
            <div style="position: absolute; width: 80px; height: 80px; border-radius: 50%; 
                background: rgba(0,0,0,0.9); top: 50%; left: 50%; transform: translate(-50%, -50%);
                display: flex; align-items: center; justify-content: center; font-size: 1.8rem; font-weight: 900; color: #fff;">
                ${Math.abs(biasScore).toFixed(0)}
            </div>
            
            <!-- Needle -->
            <div style="position: absolute; width: 4px; height: 120px; background: #fff;
                top: 50%; left: 50%; transform-origin: center bottom;
                transform: translate(-50%, -100%) rotate(${rotation}deg);
                transition: transform 1s ease;">
                <div style="position: absolute; top: -20px; left: 50%; transform: translateX(-50%);
                    width: 0; height: 0; border-left: 15px solid transparent;
                    border-right: 15px solid transparent; border-bottom: 30px solid #fff;"></div>
            </div>
            
            <!-- Labels -->
            <div style="position: absolute; top: 50%; left: -20px; transform: translateY(-50%); 
                background: rgba(0,0,0,0.8); padding: 5px 15px; border-radius: 20px; color: #3b82f6; font-weight: 700;">
                Far Left
            </div>
            <div style="position: absolute; top: 50%; right: -20px; transform: translateY(-50%); 
                background: rgba(0,0,0,0.8); padding: 5px 15px; border-radius: 20px; color: #ef4444; font-weight: 700;">
                Far Right
            </div>
            <div style="position: absolute; bottom: -40px; left: 50%; transform: translateX(-50%); 
                background: rgba(0,0,0,0.8); padding: 5px 15px; border-radius: 20px; color: #10b981; font-weight: 700;">
                Center
            </div>
        </div>
        
        <div style="background: linear-gradient(135deg, #ff00ff, #ff0080); color: #fff; 
            padding: 12px 25px; border-radius: 30px; font-weight: 700; font-size: 1.2rem; 
            margin-top: 30px; display: inline-block;">
            ${biasLabel.toUpperCase()} BIAS DETECTED
        </div>
    </div>`;
}

function createClaimsGrid(data) {
    const unsupportedCount = data.bias_indicators?.unsupported_claims || 0;
    const supportedCount = data.bias_indicators?.factual_claims || 0;
    
    return `
    <div style="margin-top: 30px;">
        <h3 style="color: #ff00ff; margin-bottom: 20px;">Factual Claims Analysis</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
            <div style="background: rgba(255,0,0,0.1); border: 1px solid rgba(255,0,0,0.3); border-radius: 15px; padding: 20px;">
                <h4 style="color: #ff6666; margin-bottom: 10px;">
                    <i class="fas fa-exclamation-triangle"></i> Unsupported Claims
                    <span style="background: rgba(255,0,0,0.3); padding: 2px 8px; border-radius: 10px; margin-left: 10px;">${unsupportedCount}</span>
                </h4>
                ${unsupportedCount > 0 ? 
                    '<p style="color: #fff; opacity: 0.8;">Claims requiring additional verification were detected.</p>' : 
                    '<p style="color: #fff; opacity: 0.8;">No unsupported claims detected.</p>'}
            </div>
            <div style="background: rgba(0,255,0,0.1); border: 1px solid rgba(0,255,0,0.3); border-radius: 15px; padding: 20px;">
                <h4 style="color: #66ff66; margin-bottom: 10px;">
                    <i class="fas fa-check-circle"></i> Verified Claims
                    <span style="background: rgba(0,255,0,0.3); padding: 2px 8px; border-radius: 10px; margin-left: 10px;">${supportedCount}</span>
                </h4>
                ${supportedCount > 0 ? 
                    '<p style="color: #fff; opacity: 0.8;">Claims with proper attribution and verification.</p>' : 
                    '<p style="color: #fff; opacity: 0.8;">No explicitly verifiable claims found.</p>'}
            </div>
        </div>
    </div>`;
}

// ============================================================================
// REMAINING TABS
// ============================================================================

function createCredibilityTab(data, tier) {
    const html = `
    <div class="tab-content" id="credibility-content" style="display: none;">
        <div style="background: rgba(0,0,0,0.8); border: 2px solid rgba(255,255,0,0.3); border-radius: 20px; padding: 40px;">
            <h2 style="color: #ffff00; font-size: 2rem; margin-bottom: 30px; text-align: center;">✓ Credibility Check</h2>
            <p style="color: #fff; text-align: center; font-size: 1.2rem;">Detailed credibility analysis coming soon...</p>
        </div>
    </div>`;
    
    const tabContents = document.getElementById('tab-contents');
    if (tabContents) {
        tabContents.insertAdjacentHTML('beforeend', html);
    }
}

function createCrossSourceTab(data, tier) {
    const crossRefs = data.cross_references || [];
    const html = `
    <div class="tab-content" id="cross-source-content" style="display: none;">
        <div style="background: rgba(0,0,0,0.8); border: 2px solid rgba(0,255,255,0.3); border-radius: 20px; padding: 40px;">
            <h2 style="color: #00ffff; font-size: 2rem; margin-bottom: 30px; text-align: center;">🔍 Cross-Source Verification</h2>
            <p style="color: #fff; text-align: center; font-size: 1.2rem;">Found ${crossRefs.length} matching sources in our database of 500+ outlets.</p>
        </div>
    </div>`;
    
    const tabContents = document.getElementById('tab-contents');
    if (tabContents) {
        tabContents.insertAdjacentHTML('beforeend', html);
    }
}

function createAuthorTab(data, tier) {
    const html = `
    <div class="tab-content" id="author-content" style="display: none;">
        <div style="background: rgba(0,0,0,0.8); border: 2px solid rgba(255,0,255,0.3); border-radius: 20px; padding: 40px;">
            <h2 style="color: #ff00ff; font-size: 2rem; margin-bottom: 30px; text-align: center;">👤 Author Analysis</h2>
            <p style="color: #fff; text-align: center; font-size: 1.2rem;">Author credibility and expertise analysis coming soon...</p>
        </div>
    </div>`;
    
    const tabContents = document.getElementById('tab-contents');
    if (tabContents) {
        tabContents.insertAdjacentHTML('beforeend', html);
    }
}

function createStyleTab(data, tier) {
    const html = `
    <div class="tab-content" id="style-content" style="display: none;">
        <div style="background: rgba(0,0,0,0.8); border: 2px solid rgba(0,255,136,0.3); border-radius: 20px; padding: 40px;">
            <h2 style="color: #00ff88; font-size: 2rem; margin-bottom: 30px; text-align: center;">✍️ Writing Style Analysis</h2>
            <p style="color: #fff; text-align: center; font-size: 1.2rem;">Linguistic patterns and authenticity analysis coming soon...</p>
        </div>
    </div>`;
    
    const tabContents = document.getElementById('tab-contents');
    if (tabContents) {
        tabContents.insertAdjacentHTML('beforeend', html);
    }
}

function createTemporalTab(data, tier) {
    const html = `
    <div class="tab-content" id="temporal-content" style="display: none;">
        <div style="background: rgba(0,0,0,0.8); border: 2px solid rgba(255,255,0,0.3); border-radius: 20px; padding: 40px;">
            <h2 style="color: #ffff00; font-size: 2rem; margin-bottom: 30px; text-align: center;">⏱️ Temporal Intelligence</h2>
            <p style="color: #fff; text-align: center; font-size: 1.2rem;">Timeline and currency analysis coming soon...</p>
        </div>
    </div>`;
    
    const tabContents = document.getElementById('tab-contents');
    if (tabContents) {
        tabContents.insertAdjacentHTML('beforeend', html);
    }
}

function createProTab(data, tier) {
    const html = `
    <div class="tab-content" id="pro-content" style="display: none;">
        <div style="background: linear-gradient(135deg, rgba(255,215,0,0.2), rgba(255,165,0,0.2)); border: 2px solid #FFD700; border-radius: 20px; padding: 40px;">
            <h2 style="color: #FFD700; font-size: 2rem; margin-bottom: 30px; text-align: center;">💎 Pro Features Unlocked</h2>
            <p style="color: #fff; text-align: center; font-size: 1.2rem;">All advanced analysis features are currently available for development.</p>
        </div>
    </div>`;
    
    const tabContents = document.getElementById('tab-contents');
    if (tabContents) {
        tabContents.insertAdjacentHTML('beforeend', html);
    }
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function generateSummaryNarrative(data) {
    const credibilityScore = data.credibility_score || 65;
    const sourceName = data.source_analysis?.domain || 'Unknown Source';
    const biasLabel = data.political_bias?.bias_label || 'unknown';
    
    return `This article from <strong style="color: #00ffff;">${sourceName}</strong> scores ${credibilityScore}/100 on our credibility scale. 
            ${credibilityScore >= 80 ? 'The reporting appears highly reliable with excellent sourcing and fact-checking.' : 
             credibilityScore >= 60 ? 'The content shows moderate credibility with some areas requiring additional verification.' :
             'Significant credibility concerns detected - we recommend verifying key claims through additional sources.'}
            Our bias analysis detected a <strong style="color: #ff00ff;">${biasLabel}</strong> political perspective.`;
}

function generateBiasNarrative(biasData) {
    const biasLabel = biasData.bias_label || 'center';
    const biasScore = biasData.bias_score || 0;
    const objectivityScore = biasData.objectivity_score || 75;
    
    return `Our AI detected a ${biasLabel} political orientation with a bias score of ${biasScore > 0 ? '+' : ''}${biasScore.toFixed(1)}. 
            The article maintains ${objectivityScore}% objectivity, ${
            objectivityScore >= 80 ? 'indicating professional journalistic standards with minimal bias' :
            objectivityScore >= 60 ? 'showing reasonable balance despite some evident political perspective' :
            'suggesting significant editorial influence that may affect the presentation of facts'}.`;
}

function generateSourceNarrative(sourceData) {
    const credibility = sourceData.credibility_score || 70;
    const domain = sourceData.domain || 'this source';
    
    return `${domain} has a credibility rating of ${credibility}/100 in our database. 
            ${credibility >= 80 ? 'This is a highly trusted source with an excellent track record for accurate reporting.' : 
             credibility >= 60 ? 'This source generally provides reliable information but may have occasional accuracy issues.' :
             'This source has credibility concerns - we recommend cross-referencing important claims.'}`;
}

function generateKeyFindings(data) {
    const findings = [];
    
    if (data.credibility_score >= 80) {
        findings.push('✅ High credibility score indicates reliable reporting');
    } else if (data.credibility_score >= 60) {
        findings.push('⚠️ Moderate credibility - verify key claims');
    } else {
        findings.push('❌ Low credibility score - significant concerns detected');
    }
    
    if (data.political_bias?.bias_label && data.political_bias.bias_label !== 'center') {
        findings.push(`🎯 ${data.political_bias.bias_label} political bias detected`);
    }
    
    if (data.cross_references && data.cross_references.length > 0) {
        findings.push(`📰 Story corroborated by ${data.cross_references.length} other sources`);
    }
    
    if (data.bias_indicators?.emotional_language > 50) {
        findings.push('💭 High emotional language detected');
    }
    
    return findings.map(finding => 
        `<div style="background: rgba(0,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 10px; 
         border-left: 4px solid #00ffff; color: #fff;">
         ${finding}
         </div>`
    ).join('');
}

// Make displayResults globally available
window.displayResults = displayResults;
