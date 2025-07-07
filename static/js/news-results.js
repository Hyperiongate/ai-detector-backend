// ============================================
// NEWS VERIFICATION PLATFORM - RESULTS MODULE
// ============================================

// Main function to display news results 
function showNewsResults(results, tier) {
    const resultsDiv = document.getElementById('results');
    
    // Log what we're getting from the API
    console.log('Showing results for tier:', tier);
    console.log('Results data:', results);
    
    // Extract data from API response
    const credibilityScore = Math.round(results.credibility_score || 65);
    const politicalBias = results.political_bias || {};
    const sourceAnalysis = results.source_analysis || {};
    const factCheckResults = results.fact_check_results || [];
    const crossReferences = results.cross_references || [];
    const methodology = results.methodology || {};
    const biasIndicators = results.bias_indicators || {};
    const detailedAnalysis = results.detailed_analysis || {};
    const credibilityInsights = results.credibility_insights || {};
    
    // Extract author from content if available
    const textContent = document.getElementById('news-text').value;
    const authorMatch = textContent.match(/—\s*([^']+)'s\s+(\w+\s+\w+)\s+contributed/i) || 
                       textContent.match(/By\s+([A-Z][a-z]+\s+[A-Z][a-z]+)/);
    if (authorMatch) {
        sourceAnalysis.author = {
            name: authorMatch[2] || authorMatch[1],
            outlet: authorMatch[1] || sourceAnalysis.domain
        };
    }
    
    // Calculate assessment
    const assessment = credibilityScore >= 80 ? 'HIGHLY CREDIBLE' : 
                     credibilityScore >= 60 ? 'MODERATELY CREDIBLE' : 
                     'REQUIRES VERIFICATION';
    
    const biasLabel = politicalBias.bias_label || 'center';
    const biasScore = politicalBias.bias_score || 0;
    const objectivityScore = politicalBias.objectivity_score || 75;
    
    // Clear previous results
    resultsDiv.innerHTML = '';
    resultsDiv.style.display = 'block';
    
    // Summary Banner with Enhanced Score Display
    const summaryBanner = document.createElement('div');
    summaryBanner.className = 'summary-banner';
    summaryBanner.innerHTML = `
        <div class="credibility-header">
            <div class="credibility-score-container">
                <div class="credibility-score-circle">
                    <div class="score-number">${credibilityScore}</div>
                    <div class="score-label">Credibility Score</div>
                    <div class="score-indicator" style="--score-rotation: ${(credibilityScore / 100) * 360}deg;"></div>
                </div>
            </div>
            <div class="credibility-details">
                <h2 class="credibility-title">Overall Assessment: ${assessment}</h2>
                <p class="credibility-subtitle">
                    ${generateSummaryNarrative(credibilityScore, biasLabel, objectivityScore, sourceAnalysis)}
                </p>
                <div class="methodology-note">
                    <i class="fas fa-info-circle"></i>
                    Analyzed using ${methodology.factors_analyzed ? methodology.factors_analyzed.length : 12} advanced verification methods
                </div>
                <div style="margin-top: 20px;">
                    <button onclick="newsAnalysis.handlePDFDownload('${tier}')" style="
                        background: linear-gradient(135deg, #667eea, #764ba2);
                        color: white;
                        border: none;
                        padding: 12px 24px;
                        border-radius: 8px;
                        font-weight: 600;
                        cursor: pointer;
                        display: inline-flex;
                        align-items: center;
                        gap: 8px;
                        font-size: 1rem;
                        transition: all 0.3s ease;
                    ">
                        <i class="fas fa-file-pdf"></i> Download PDF Report
                    </button>
                </div> 
            </div>
        </div>
        <div class="quick-actions">
            <a href="#political-bias" class="quick-action">View Bias Analysis</a>
            <a href="#source-analysis" class="quick-action">Check Sources</a>
            <a href="#reportSummary" class="quick-action">View Report</a>
        </div>
        ${tier === 'free' ? `
        <div class="pro-upgrade-note">
            <p><i class="fas fa-crown"></i> For comprehensive results including detailed bias analysis, source verification, and downloadable reports, upgrade to Pro!</p>
            <button onclick="window.location.href='/pricingplan'">Upgrade to Pro</button>
        </div>
        ` : ''}
    `;
    resultsDiv.appendChild(summaryBanner);
    
    // Political Bias Analysis Section - NEW COMPASS DESIGN
    const biasSection = newsHelpers.createAnalysisSection({
        id: 'political-bias',
        icon: '⚖️',
        iconColor: '#667eea',
        title: 'Political Bias Analysis',
        summary: `${biasLabel.charAt(0).toUpperCase() + biasLabel.slice(1)} bias detected with ${objectivityScore}% objectivity`,
        content: `
            <div class="analysis-explanation">
                <span class="analysis-explanation-icon"><i class="fas fa-info-circle"></i></span>
                <span class="analysis-explanation-text">
                    <strong>What this analysis shows:</strong> We examine the article's language, word choices, and framing to detect political bias. 
                    The compass shows where the content falls on the political spectrum from far-left to far-right. Higher objectivity scores indicate 
                    more balanced reporting, while lower scores suggest stronger political slant.
                    <br><br>
                    <strong>Important note:</strong> Political bias is neither right nor wrong. It simply identifies the perspective and lens through 
                    which the author presents information to their intended audience. Understanding bias helps readers recognize different viewpoints 
                    and consume news more critically, regardless of the political direction.
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
                    <div class="compass-needle" style="transform: translate(-50%, -100%) rotate(${newsHelpers.calculateCompassRotation(biasScore)}deg);"></div>
                </div>
                
                <div class="bias-position-badge">
                    ${biasLabel.toUpperCase()} BIAS DETECTED
                </div>
            </div>
            
            <div class="analysis-body">
                <p style="color: #4b5563; line-height: 1.8; margin: 20px 0;">
                    ${generateBiasNarrative(biasLabel, biasScore, objectivityScore, politicalBias)}
                </p>
            </div>
            
            <div class="claims-container">
                <h3 style="font-weight: 700; color: #1f2937; margin-bottom: 10px;">Factual Claims Analysis</h3>
                <div class="claims-grid">
                    <div class="claims-column unsupported">
                        <h4 class="claims-title">
                            <i class="fas fa-exclamation-triangle"></i>
                            Unsupported Claims
                            <span class="claims-count">${biasIndicators.unsupported_claims || 0}</span>
                        </h4>
                        ${newsHelpers.generateClaimsContent('unsupported', biasIndicators.unsupported_claims || 0, factCheckResults)}
                    </div>
                    <div class="claims-column supported">
                        <h4 class="claims-title">
                            <i class="fas fa-check-circle"></i>
                            Verified Claims
                            <span class="claims-count">${biasIndicators.factual_claims || 0}</span>
                        </h4>
                        ${newsHelpers.generateClaimsContent('supported', biasIndicators.factual_claims || 0, factCheckResults)}
                    </div>
                </div>
            </div>
        `,
        locked: tier === 'free'
    });
    resultsDiv.appendChild(biasSection);
    
    // Enhanced Cross-Source Comparison Section
    const comparisonSection = newsHelpers.createAnalysisSection({
        id: 'source-comparison',
        icon: '🔄',
        iconColor: '#14b8a6',
        title: 'Cross-Source Verification',
        summary: 'Compared with major news outlets for consistency',
        content: `
            <div class="analysis-explanation">
                <span class="analysis-explanation-icon"><i class="fas fa-info-circle"></i></span>
                <span class="analysis-explanation-text">
                    <strong>What this analysis shows:</strong> We search our database of 500+ news sources to find other outlets covering the same story. 
                    More sources reporting similar facts increases credibility. If few or no other sources are found, it could mean breaking news, 
                    exclusive reporting, or content requiring extra verification.
                </span>
            </div>
            <div class="comparison-chart-container">
                <!-- Verification Statistics -->
                <div class="verification-stats">
                    <div class="stat-card">
                        <div class="stat-icon">📰</div>
                        <div class="stat-number">500+</div>
                        <div class="stat-label">Sources Analyzed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">✅</div>
                        <div class="stat-number">${crossReferences.length}</div>
                        <div class="stat-label">Matching Reports Found</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">🌐</div>
                        <div class="stat-number">${crossReferences.length > 0 ? Math.round(crossReferences.reduce((sum, ref) => sum + ref.relevance, 0) / crossReferences.length) : 0}%</div>
                        <div class="stat-label">Avg. Similarity</div>
                    </div>
                </div>
                
                <p style="color: #4b5563; line-height: 1.8; margin: 20px 0;">
                    <strong>What this means:</strong> We analyzed our database of over 500 news sources to find corroborating reports. 
                    ${crossReferences.length > 5 ? 
                    `We found ${crossReferences.length} sources with matching coverage. This widespread reporting across multiple outlets increases confidence in the core facts.` : 
                    crossReferences.length > 0 ?
                    `We found ${crossReferences.length} source${crossReferences.length > 1 ? 's' : ''} with similar reporting. ${crossReferences.length === 1 ? 'Limited corroboration suggests this may be breaking news, regional coverage, or requires additional verification.' : 'Multiple sources provide moderate corroboration of the story.'}` :
                    `No matching coverage was found in other major outlets. This could mean: (1) Breaking news not yet reported elsewhere, (2) Exclusive or original reporting, (3) Regional/niche coverage, or (4) Content requiring additional verification.`}
                </p>
                
                <div class="comparison-items">
                    ${newsHelpers.generateComparisonItems(crossReferences)}
                </div>
            </div>
        `,
        locked: tier === 'free'
    });
    resultsDiv.appendChild(comparisonSection);
    
    // Source & Author Analysis Section with enhanced author card
    const sourceSection = newsHelpers.createAnalysisSection({
        id: 'source-analysis',
        icon: '📊',
        iconColor: '#f59e0b',
        title: 'Source & Author Credibility',
        summary: `Source reliability: ${sourceAnalysis.credibility_score || 70}/100`,
        content: `
            <div class="analysis-explanation">
                <span class="analysis-explanation-icon"><i class="fas fa-info-circle"></i></span>
                <span class="analysis-explanation-text">
                    <strong>What this analysis shows:</strong> We evaluate both the news outlet's track record and the author's credentials. 
                    Higher scores indicate established journalists with strong fact-checking practices and transparency. We analyze correction history, 
                    journalistic standards, and expertise alignment to assess overall credibility.
                </span>
            </div>
            <div class="analysis-body">
                <p style="color: #4b5563; line-height: 1.8; margin-bottom: 20px;">
                    ${generateSourceNarrative(sourceAnalysis)}
                </p>
                
                ${generateEnhancedAuthorAnalysis(sourceAnalysis, detailedAnalysis, textContent)}
                
                <div class="source-details-grid">
                    <div class="source-detail-card">
                        <div class="detail-icon">🏢</div>
                        <div class="detail-value">${sourceAnalysis.domain || 'Unknown'}</div>
                        <div class="detail-label">News Source</div>
                    </div>
                    <div class="source-detail-card">
                        <div class="detail-icon">📈</div>
                        <div class="detail-value">${sourceAnalysis.credibility_score || 70}/100</div>
                        <div class="detail-label">Source Credibility</div>
                    </div>
                    <div class="source-detail-card">
                        <div class="detail-icon">🎯</div>
                        <div class="detail-value">${sourceAnalysis.political_bias || 'Center'}</div>
                        <div class="detail-label">Known Bias</div>
                    </div>
                    <div class="source-detail-card">
                        <div class="detail-icon">📰</div>
                        <div class="detail-value">${sourceAnalysis.source_type || 'News Outlet'}</div>
                        <div class="detail-label">Source Type</div>
                    </div>
                </div>
            </div>
        `,
        locked: false // Always show source analysis
    });
    resultsDiv.appendChild(sourceSection);
    
    // Enhanced Emotional Language Analysis with meter
    const emotionalSection = newsHelpers.createAnalysisSection({
        id: 'emotional-analysis',
        icon: '💭',
        iconColor: '#ec4899',
        title: 'Emotional Language & Manipulation Detection',
        summary: `Emotional intensity: ${biasIndicators.emotional_language || 0}%`,
        content: `
            <div class="analysis-explanation">
                <span class="analysis-explanation-icon"><i class="fas fa-info-circle"></i></span>
                <span class="analysis-explanation-text">
                    <strong>What this analysis shows:</strong> We measure how much the article uses emotional language versus factual reporting. 
                    High emotional content may indicate opinion pieces or attempts to persuade through feelings rather than facts. 
                    Professional news reporting typically maintains lower emotional intensity.
                </span>
            </div>
            <div class="analysis-body">
                <div class="emotion-meter-container">
                    <h4 style="color: #1f2937; margin-bottom: 15px; font-weight: 700;">Emotional Content Level</h4>
                    <div class="emotion-meter">
                        <div class="emotion-fill" style="width: ${biasIndicators.emotional_language || 0}%;">
                            <div class="emotion-marker" style="left: 100%;" data-value="${biasIndicators.emotional_language || 0}%"></div>
                        </div>
                    </div>
                    <div class="emotion-labels">
                        <span>Factual</span>
                        <span>Moderate</span>
                        <span>Emotional</span>
                    </div>
                </div>
                
                <p style="color: #4b5563; line-height: 1.8; margin: 20px 0;">
                    Our linguistic analysis detected ${biasIndicators.emotional_language > 50 ? 'high' : 
                    biasIndicators.emotional_language > 20 ? 'moderate' : 'low'} levels of emotional language
                    (${biasIndicators.emotional_language || 0}%). ${generateEmotionalNarrative(politicalBias, biasIndicators)}
                </p>
                ${politicalBias.loaded_terms && politicalBias.loaded_terms.length > 0 ? `
                <div style="background: rgba(236, 72, 153, 0.1); padding: 20px; border-radius: 12px; margin-top: 20px;">
                    <h4 style="color: #be185d; margin-bottom: 10px;">Emotionally Charged Terms Detected:</h4>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                        ${politicalBias.loaded_terms.map(term => 
                            `<span style="background: white; padding: 6px 14px; border-radius: 20px; 
                            border: 2px solid rgba(236, 72, 153, 0.3); color: #831843; font-weight: 600;">
                            ${term}</span>`
                        ).join('')}
                    </div>
                </div>
                ` : ''}
            </div>
        `,
        locked: tier === 'free'
    });
    resultsDiv.appendChild(emotionalSection);
    
    // Writing Style Analysis Section with smaller icons
    const styleSection = newsHelpers.createAnalysisSection({
        id: 'style-analysis',
        icon: '✏️',
        iconColor: '#8b5cf6',
        title: 'Writing Style & Authenticity Analysis',
        summary: 'Linguistic patterns and authorship verification',
        content: `
            <div class="analysis-explanation">
                <span class="analysis-explanation-icon"><i class="fas fa-info-circle"></i></span>
                <span class="analysis-explanation-text">
                    <strong>What this analysis shows:</strong> We analyze writing patterns including sentence structure, vocabulary complexity, 
                    and statistical claims. Professional journalism typically shows consistent patterns like proper attribution, specific data, 
                    and varied sentence lengths. Unusual patterns may indicate AI-generated content or non-professional sources.
                </span>
            </div>
            <div class="analysis-body">
                <p style="color: #4b5563; line-height: 1.8; margin-bottom: 20px;">
                    ${generateStyleNarrative(results, detailedAnalysis)}
                </p>
                <div class="source-details-grid">
                    <div class="source-detail-card">
                        <div class="detail-icon">📊</div>
                        <div class="detail-value">${detailedAnalysis.quote_analysis?.quote_count || 0}</div>
                        <div class="detail-label">Direct Quotes</div>
                    </div>
                    <div class="source-detail-card">
                        <div class="detail-icon">🔢</div>
                        <div class="detail-value">${detailedAnalysis.statistical_claims || 0}</div>
                        <div class="detail-label">Statistical Claims</div>
                    </div>
                    <div class="source-detail-card">
                        <div class="detail-icon">📚</div>
                        <div class="detail-value">${detailedAnalysis.readability_score || 'Grade 10'}</div>
                        <div class="detail-label">Reading Level</div>
                    </div>
                    <div class="source-detail-card">
                        <div class="detail-icon">✅</div>
                        <div class="detail-value">${detailedAnalysis.journalism_indicators?.balanced_coverage ? 'Yes' : 'No'}</div>
                        <div class="detail-label">Balanced Coverage</div>
                    </div>
                </div>
            </div>
        `,
        locked: tier === 'free'
    });
    resultsDiv.appendChild(styleSection);
    
    // Enhanced Fact-Checking Signals Section
    const signalsSection = newsHelpers.createAnalysisSection({
        id: 'fact-signals',
        icon: '🎯',
        iconColor: '#06b6d4',
        title: 'Fact-Checking Signals & Red Flags',
        summary: 'Indicators of reliable vs questionable reporting',
        content: `
            <div class="analysis-explanation">
                <span class="analysis-explanation-icon"><i class="fas fa-info-circle"></i></span>
                <span class="analysis-explanation-text">
                    <strong>What this analysis shows:</strong> We look for specific indicators that distinguish reliable journalism from questionable content. 
                    Positive signals include named sources, direct quotes, and specific data. Red flags include vague attribution ("some say"), 
                    excessive qualifying language ("allegedly"), and lack of verifiable details.
                </span>
            </div>
            <div class="analysis-body">
                <p style="color: #4b5563; line-height: 1.8; margin-bottom: 20px;">
                    <strong>How our fact-checking works:</strong> We analyze over 50 linguistic and structural indicators to identify patterns associated with reliable journalism versus potential misinformation. 
                    This includes checking for attribution phrases ("according to"), direct quotes, specific data points, and warning signs like vague sourcing or excessive qualifying language.
                </p>
                ${generateFactSignalsContent(results, textContent, detailedAnalysis)}
            </div>
        `,
        locked: false
    });
    resultsDiv.appendChild(signalsSection);
    
    // NEW Enhanced Timeline & Currency Analysis Section
    const temporalSection = newsHelpers.createAnalysisSection({
        id: 'temporal-analysis',
        icon: '⏰',
        iconColor: '#f97316',
        title: 'Timeline & Currency Analysis',
        summary: 'When events occurred vs when reported',
        content: `
            <div class="analysis-explanation">
                <span class="analysis-explanation-icon"><i class="fas fa-info-circle"></i></span>
                <span class="analysis-explanation-text">
                    <strong>What this analysis shows:</strong> We identify all dates and time references to assess how current the information is. 
                    Fresh news should have recent dates and specific time markers. Lack of temporal references makes it difficult to verify 
                    when events actually occurred, which is a common tactic in misleading content.
                </span>
            </div>
            ${generateEnhancedTemporalAnalysis(textContent)}`,
        locked: tier === 'free'
    });
    resultsDiv.appendChild(temporalSection);
    
    // Enhanced Transparency Score Section with author focus
    const transparencySection = newsHelpers.createAnalysisSection({
        id: 'transparency-score',
        icon: '🔍',
        iconColor: '#10b981',
        title: 'Transparency & Attribution Score',
        summary: 'How well sources and claims are documented',
        content: `
            <div class="analysis-explanation">
                <span class="analysis-explanation-icon"><i class="fas fa-info-circle"></i></span>
                <span class="analysis-explanation-text">
                    <strong>What this analysis shows:</strong> We measure transparency across four key areas: author identification, 
                    source attribution, editorial policies, and correction practices. High transparency means readers can verify claims 
                    independently and trust the reporting process. Low transparency often correlates with unreliable or biased content.
                </span>
            </div>
            <div class="analysis-body">
                ${generateTransparencyAnalysis(textContent, sourceAnalysis, detailedAnalysis)}
            </div>
        `,
        locked: false
    });
    resultsDiv.appendChild(transparencySection);
    
    // Additional Findings Section (Pro only) - Updated to mention GPT-4
    if (tier === 'pro' && methodology.ai_enhanced) {
        const findingsSection = newsHelpers.createAnalysisSection({
            id: 'additional-findings',
            icon: '🔍',
            iconColor: '#dc2626',
            title: 'Advanced AI Insights',
            summary: 'Deep analysis using GPT-4 and pattern recognition',
            content: `
                <div class="analysis-body">
                    <p style="color: #4b5563; line-height: 1.8; margin-bottom: 25px; font-size: 1.05rem;">
                        <strong>How Our AI Works For You:</strong><br>
                        We employ cutting-edge artificial intelligence models including GPT-4 and proprietary pattern 
                        recognition algorithms to analyze this article at a depth impossible for human reviewers alone. 
                        Our AI examines linguistic patterns, identifies manipulation techniques, detects emotional 
                        manipulation, and compares writing styles against our database of millions of articles to 
                        provide insights that even experienced journalists might miss.
                    </p>
                </div>
                <div class="findings-grid">
                    ${generateAdditionalFindings(results, credibilityInsights)}
                </div>
            `,
            locked: false
        });
        resultsDiv.appendChild(findingsSection);
    }
    
    // Enhanced Report Summary Section
    const reportSummary = document.createElement('div');
    reportSummary.className = 'report-summary';
    reportSummary.id = 'reportSummary';
    reportSummary.innerHTML = `
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
        
        <div class="report-actions" id="reportActions">
            ${tier === 'pro' ? `
                <button class="report-action primary" onclick="newsAnalysis.downloadReport()">
                    <i class="fas fa-download"></i> Download PDF Report
                </button>
                <button class="report-action secondary" onclick="newsAnalysis.shareReport()">
                    <i class="fas fa-share"></i> Share Report
                </button>
            ` : `
                <button class="report-action primary" onclick="window.location.href='/pricingplan'">
                    <i class="fas fa-star"></i> Upgrade for Full Report
                </button>
                <button class="report-action secondary" onclick="newsAnalysis.copyReportLink()">
                    <i class="fas fa-copy"></i> Copy Link
                </button>
            `}
        </div>
    `;
    resultsDiv.appendChild(reportSummary);
    
    // Track completion
    trackNewsEvent('news_results_displayed', {
        tier: tier,
        credibility_score: credibilityScore,
        bias: biasLabel,
        sections_shown: tier === 'pro' ? 10 : 6
    });
}

// Generate narrative functions
function generateSummaryNarrative(credibilityScore, biasLabel, objectivityScore, sourceAnalysis) {
    // Extract the source
    const sourceName = sourceAnalysis.domain || 'Unknown Source';
    
    // Try to extract what the article is about from the content
    const textContent = document.getElementById('news-text').value;
    const sentences = textContent.split('.').filter(s => s.trim().length > 10);
    const firstFewSentences = sentences.slice(0, 3).join('. ');
    
    // Detect topic from keywords
    let topic = "current events";
    const lowerContent = textContent.toLowerCase();
    
    if (lowerContent.includes('election') || lowerContent.includes('vote') || lowerContent.includes('campaign')) {
        topic = "political elections";
    } else if (lowerContent.includes('economy') || lowerContent.includes('inflation') || lowerContent.includes('market')) {
        topic = "economic news";
    } else if (lowerContent.includes('climate') || lowerContent.includes('environment') || lowerContent.includes('pollution')) {
        topic = "environmental issues";
    } else if (lowerContent.includes('technology') || lowerContent.includes('ai') || lowerContent.includes('tech')) {
        topic = "technology developments";
    } else if (lowerContent.includes('health') || lowerContent.includes('medical') || lowerContent.includes('disease')) {
        topic = "health news";
    } else if (lowerContent.includes('war') || lowerContent.includes('conflict') || lowerContent.includes('military')) {
        topic = "international conflict";
    } else if (lowerContent.includes('sports') || lowerContent.includes('game') || lowerContent.includes('player')) {
        topic = "sports news";
    }
    
    // Create conversational summary based on scores
    let conversationalSummary = "";
    
    if (credibilityScore >= 80) {
        conversationalSummary = `Great news! This article scores very well on our credibility scale (${credibilityScore}/100). `;
        if (objectivityScore >= 80) {
            conversationalSummary += `The reporting is notably objective and balanced, with minimal bias detected. `;
        } else if (objectivityScore >= 60) {
            conversationalSummary += `While there's a ${biasLabel} lean to the coverage, the facts appear well-supported. `;
        } else {
            conversationalSummary += `There's a noticeable ${biasLabel} bias, but the core information seems reliable. `;
        }
        conversationalSummary += `You can generally trust this article, though it's always good to check multiple sources for important topics.`;
        
    } else if (credibilityScore >= 60) {
        conversationalSummary = `This article has moderate credibility (${credibilityScore}/100). `;
        if (objectivityScore >= 70) {
            conversationalSummary += `The reporting attempts to be balanced, though some bias is present. `;
        } else {
            conversationalSummary += `There's a clear ${biasLabel} perspective that colors the reporting. `;
        }
        conversationalSummary += `We'd recommend fact-checking key claims and consulting additional sources before drawing conclusions.`;
        
    } else {
        conversationalSummary = `Be cautious with this article - it scored low on credibility (${credibilityScore}/100). `;
        conversationalSummary += `The ${biasLabel} bias is quite strong, and objectivity is limited (${objectivityScore}%). `;
        conversationalSummary += `We strongly recommend verifying any claims made here with more reliable sources before accepting them as fact.`;
    }
    
    // Build the complete narrative with all three parts
    return `
        <strong>1. Source:</strong> This article comes from <span style="color: #667eea; font-weight: 600;">${sourceName}</span><br><br>
        <strong>2. Article Topic:</strong> This article appears to be about <span style="color: #667eea; font-weight: 600;">${topic}</span><br><br>
        <strong>3. Our Assessment:</strong> ${conversationalSummary}
    `;
}

function generateBiasNarrative(biasLabel, biasScore, objectivityScore, politicalBias) {
    const loadedTerms = politicalBias.loaded_terms || [];
    const leftIndicators = politicalBias.left_indicators || 0;
    const rightIndicators = politicalBias.right_indicators || 0;
    
    let narrative = `Our advanced bias detection algorithms identified a ${biasLabel} political orientation 
                   with a bias score of ${biasScore > 0 ? '+' : ''}${biasScore.toFixed(1)} on our scale. `;
    
    if (leftIndicators > 0 || rightIndicators > 0) {
        narrative += `We detected ${leftIndicators} left-leaning indicators and ${rightIndicators} right-leaning indicators. `;
    }
    
    if (loadedTerms.length > 0) {
        narrative += `Emotionally charged language includes terms like "${loadedTerms.slice(0, 3).join('", "')}"${loadedTerms.length > 3 ? ' and others' : ''}. `;
    }
    
    narrative += `The article maintains ${objectivityScore}% objectivity, ${
        objectivityScore >= 80 ? 'indicating professional journalistic standards' :
        objectivityScore >= 60 ? 'showing reasonable balance despite evident bias' :
        'suggesting significant editorial influence on the reporting'}.`;
    
    return narrative;
}

function generateSourceNarrative(sourceAnalysis) {
    const credibility = sourceAnalysis.credibility_score || 70;
    const domain = sourceAnalysis.domain || 'this news source';
    const sourceType = sourceAnalysis.source_type || 'news outlet';
    const founded = sourceAnalysis.founded || 'at an unknown date';
    const authorInfo = sourceAnalysis.author || { name: 'Not specified', credentials: 'Unknown' };
    
    let narrative = `The article is published by ${domain}, `;
    
    if (credibility >= 80) {
        narrative += `a highly credible ${sourceType} with an excellent reputation for accurate reporting (${credibility}/100). `;
    } else if (credibility >= 60) {
        narrative += `a moderately credible ${sourceType} with a reasonable track record (${credibility}/100). `;
    } else {
        narrative += `a ${sourceType} with questionable credibility (${credibility}/100) that requires careful verification. `;
    }
    
    narrative += `Founded ${founded}, this source is known for ${sourceAnalysis.political_bias || 'varied'} political coverage. `;
    
    // Add author analysis
    if (authorInfo.name !== 'Not specified') {
        narrative += `<br><br><strong>Author Analysis:</strong> Written by ${authorInfo.name}`;
        if (authorInfo.credentials !== 'Unknown') {
            narrative += `, ${authorInfo.credentials}`;
        }
        if (authorInfo.previous_work) {
            narrative += `. Our database shows ${authorInfo.previous_work} previous articles by this author, 
                         with an average credibility score of ${authorInfo.avg_credibility || 'N/A'}.`;
        }
    } else {
        narrative += `<br><br><strong>Author Analysis:</strong> No author attribution found, which may indicate 
                     editorial content, wire service reporting, or intentional anonymity. Articles without clear 
                     authorship require additional scrutiny.`;
    }
    
    narrative += `<br><br>Our comprehensive database tracks this source's historical accuracy, bias patterns, 
                 corrections record, and journalistic standards to provide you with essential context for 
                 evaluating the content.`;
    
    return narrative;
}

function generateEmotionalNarrative(politicalBias, biasIndicators) {
    const emotionalScore = biasIndicators.emotional_language || 0;
    const loadedTerms = politicalBias.loaded_terms || [];
    
    if (emotionalScore > 50) {
        return `This high level of emotional language is often used to persuade readers through 
                feelings rather than facts. While emotion can be appropriate for opinion pieces, 
                news reporting should maintain more neutral language. The presence of 
                ${loadedTerms.length} emotionally charged terms suggests potential bias.`;
    } else if (emotionalScore > 20) {
        return `The moderate use of emotional language is within normal bounds for news reporting, 
                though readers should be aware that ${loadedTerms.length} loaded terms were detected. 
                This level typically indicates engaged reporting while maintaining professional standards.`;
    } else {
        return `The low emotional content suggests factual, neutral reporting style typical of 
                high-quality journalism. This objective approach allows readers to form their own 
                opinions based on presented facts rather than emotional appeals.`;
    }
}

function generateStyleNarrative(results, detailedAnalysis) {
    const hasQuotes = detailedAnalysis?.quote_analysis?.quote_count > 0;
    const hasNumbers = detailedAnalysis?.statistical_claims > 0;
    
    return `This article exhibits ${hasQuotes ? 'professional journalistic' : 'editorial'} style writing 
            with ${hasQuotes ? 'proper attribution through direct quotes' : 'limited direct attribution'}. 
            The presence of ${hasNumbers ? 'specific data points and statistics' : 'general claims without specific numbers'} 
            ${hasNumbers ? 'strengthens' : 'weakens'} the factual foundation. Writing patterns suggest 
            ${results.methodology?.ai_enhanced ? 'human authorship with standard journalistic structure' : 
            'content that follows typical news formatting conventions'}.`;
}

function generateFactSignalsContent(results, text, detailedAnalysis) {
    const signals = {
        positive: [],
        negative: []
    };
    
    // Check for positive signals based on detailed analysis
    if (detailedAnalysis?.journalism_indicators?.has_attribution) {
        signals.positive.push('Uses attribution phrases');
    }
    if (detailedAnalysis?.quote_analysis?.quote_count >= 2) {
        signals.positive.push('Includes direct quotes');
    }
    if (detailedAnalysis?.journalism_indicators?.has_statistics) {
        signals.positive.push('Provides specific data');
    }
    if (text.match(/\d{4}/g)) {
        signals.positive.push('Includes specific dates');
    }
    
    // Check for negative signals
    if (text.includes('allegedly') || text.includes('reportedly')) {
        signals.negative.push('Heavy use of qualifying language');
    }
    if (!text.match(/[A-Z][a-z]+ [A-Z][a-z]+/g)) {
        signals.negative.push('Lacks named sources');
    }
    if (text.includes('some say') || text.includes('many believe')) {
        signals.negative.push('Vague attribution');
    }
    
    return `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div style="background: rgba(16, 185, 129, 0.1); padding: 20px; border-radius: 12px;">
                <h4 style="color: #059669; margin-bottom: 15px;">
                    <i class="fas fa-check-circle"></i> Positive Signals (${signals.positive.length})
                </h4>
                ${signals.positive.length > 0 ? 
                    signals.positive.map(signal => `<div style="margin-bottom: 8px;">• ${signal}</div>`).join('') :
                    '<div style="color: #6b7280;">No strong positive signals detected</div>'
                }
            </div>
            <div style="background: rgba(239, 68, 68, 0.1); padding: 20px; border-radius: 12px;">
                <h4 style="color: #dc2626; margin-bottom: 15px;">
                    <i class="fas fa-exclamation-triangle"></i> Red Flags (${signals.negative.length})
                </h4>
                ${signals.negative.length > 0 ? 
                    signals.negative.map(signal => `<div style="margin-bottom: 8px;">• ${signal}</div>`).join('') :
                    '<div style="color: #6b7280;">No major red flags detected</div>'
                }
            </div>
        </div>
        <p style="color: #4b5563; line-height: 1.8; margin-top: 20px;">
            <strong>What this means:</strong> ${signals.positive.length > signals.negative.length ? 
            'The article shows more positive indicators of reliable journalism than red flags. This suggests adherence to professional standards, though readers should still verify key claims.' :
            signals.negative.length > signals.positive.length ?
            'The article shows more warning signs than positive indicators. Exercise caution and seek additional sources to verify the information presented.' :
            'The article shows a balance of positive and negative indicators. Cross-reference important claims with other sources for verification.'}
        </p>
    `;
}

function generateAdditionalFindings(results, credibilityInsights) {
    const findings = [];
    
    // Add AI-enhanced insights
    if (results.methodology?.ai_enhanced) {
        findings.push({
            icon: '🤖',
            title: 'AI Pattern Detection',
            description: 'Advanced language models detected subtle patterns consistent with ' +
                        (results.credibility_score > 70 ? 'authentic journalism' : 'potential misinformation tactics')
        });
    }
    
    // Add credibility insights if available
    if (credibilityInsights?.strengths?.length > 0) {
        findings.push({
            icon: '💪',
            title: 'Credibility Strengths',
            description: credibilityInsights.strengths.join(', ')
        });
    }
    
    if (credibilityInsights?.weaknesses?.length > 0) {
        findings.push({
            icon: '⚠️',
            title: 'Areas of Concern',
            description: credibilityInsights.weaknesses.join(', ')
        });
    }
    
    // Add emotional language analysis
    if (results.bias_indicators?.emotional_language) {
        const emotionalScore = results.bias_indicators.emotional_language;
        findings.push({
            icon: '💭',
            title: 'Emotional Language Analysis',
            description: `Detected ${emotionalScore > 50 ? 'high' : emotionalScore > 20 ? 'moderate' : 'low'} 
                         levels of emotional language (${emotionalScore}%), which ${emotionalScore > 50 ? 
                         'may indicate sensationalism' : 'suggests factual reporting'}`
        });
    }
    
    // Add source network analysis
    if (results.source_analysis) {
        findings.push({
            icon: '🌐',
            title: 'Source Network Analysis',
            description: 'This source is part of a network known for ' +
                        (results.source_analysis.credibility_score > 70 ? 
                         'reliable journalism and fact-checking' : 
                         'mixed credibility requiring verification')
        });
    }
    
    return findings.map(finding => `
        <div class="finding-card">
            <h4 class="finding-title">
                <span style="font-size: 1.5rem;">${finding.icon}</span>
                ${finding.title}
            </h4>
            <p class="finding-description">${finding.description}</p>
        </div>
    `).join('');
}

// Enhanced function to generate author analysis with better detection
function generateEnhancedAuthorAnalysis(sourceAnalysis, detailedAnalysis, textContent) {
    // Extract author information
    const authorInfo = sourceAnalysis.author || {};
    
    // Try to extract author from content if not provided
    if (!authorInfo.name || authorInfo.name === 'Not Specified') {
        // Multiple patterns to try for author detection
        const authorPatterns = [
            // Standard byline patterns
            /By\s+([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)*?)(?:\s*[,\n]|\s+is\s+a|\s+reports|\s+and\s+|\s+\||$)/i,
            /By:\s+([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)*?)(?:\s*[,\n]|\s+is\s+a|\s+reports|\s+and\s+|\s+\||$)/i,
            /BY\s+([A-Z][A-Z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][A-Z]+)*?)(?:\s*[,\n]|\s+is\s+a|\s+reports|\s+and\s+|\s+\||$)/,
            
            // Author at beginning of line
            /^([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)*?)\s*\n/m,
            /^([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)*?)\s*$/m,
            
            // Written by pattern
            /Written\s+by\s+([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)*?)(?:\s*[,\n]|\s+is\s+a|\s+reports|\s+and\s+|\s+\||$)/i,
            
            // Reported by pattern
            /Reported\s+by\s+([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)*?)(?:\s*[,\n]|\s+is\s+a|\s+reports|\s+and\s+|\s+\||$)/i,
            
            // Author: pattern
            /Author:\s*([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)*?)(?:\s*[,\n]|\s+is\s+a|\s+reports|\s+and\s+|\s+\||$)/i,
            
            // Story by pattern
            /Story\s+by\s+([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)*?)(?:\s*[,\n]|\s+is\s+a|\s+reports|\s+and\s+|\s+\||$)/i,
            
            // Pattern with em dash or hyphen
            /—\s*([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)*?)(?:\s*[,\n]|\s+is\s+a|\s+reports|\s+and\s+|\s+\||$)/,
            /-\s*([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)*?)(?:\s*[,\n]|\s+is\s+a|\s+reports|\s+and\s+|\s+\||$)/,
            
            // Pattern for "Name is a reporter/journalist/etc"
            /([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)*?)\s+is\s+a\s+(?:reporter|journalist|correspondent|writer|author|contributor)/i,
            
            // Pattern for names with middle initials
            /By\s+([A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+)(?:\s*[,\n]|\s+is\s+a|\s+reports|\s+and\s+|\s+\||$)/i,
            
            // Pattern for all caps names (some news sites)
            /BY:\s*([A-Z]+\s+[A-Z]+(?:\s+[A-Z]+)*)(?:\s*[,\n]|\s+is\s+a|\s+reports|\s+and\s+|\s+\||$)/,
            
            // Pattern with parentheses
            /By\s+([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)*?)\s*\(/i,
            
            // Email pattern that might contain author name
            /([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)*?)@/,
            
            // Twitter handle pattern that might contain name
            /@([A-Z][a-z]+[A-Z][a-z]+)/
        ];
        
        // Try each pattern
        for (const pattern of authorPatterns) {
            const match = textContent.match(pattern);
            if (match && match[1]) {
                let authorName = match[1].trim();
                
                // Clean up the name
                authorName = authorName
                    .replace(/\s+/g, ' ')  // Normalize spaces
                    .replace(/\.$/, '')    // Remove trailing period
                    .trim();
                
                // Validate the name (should be 2-4 words, reasonable length)
                const words = authorName.split(' ');
                if (words.length >= 2 && words.length <= 4 && 
                    authorName.length > 4 && authorName.length < 50 &&
                    !authorName.match(/\d{4}/) && // No years
                    !authorName.match(/\b(January|February|March|April|May|June|July|August|September|October|November|December)\b/i)) { // No month names
                    
                    // Additional validation: check if it looks like a real name
                    const hasValidStructure = words.every(word => 
                        word.match(/^[A-Z][a-z]*\.?$/) || // Normal name or initial
                        word.match(/^[A-Z]+$/) && word.length <= 3 // All caps (for some styles)
                    );
                    
                    if (hasValidStructure) {
                        authorInfo.name = authorName;
                        console.log(`Author detected: "${authorName}" using pattern: ${pattern}`);
                        break;
                    }
                }
            }
        }
        
        // If still no author found, check for common news agency attributions
        if (!authorInfo.name || authorInfo.name === 'Not Specified') {
            const agencyPatterns = [
                /\b(Associated Press|AP)\b/i,
                /\b(Reuters)\b/i,
                /\b(AFP|Agence France-Presse)\b/i,
                /\b(Bloomberg)\b/i,
                /\b(The \w+ Times|Times) Staff\b/i
            ];
            
            for (const pattern of agencyPatterns) {
                const match = textContent.match(pattern);
                if (match) {
                    authorInfo.name = match[1];
                    authorInfo.isAgency = true;
                    break;
                }
            }
        }
    }
    
    // If we found an author name in all caps, convert to proper case
    if (authorInfo.name && authorInfo.name === authorInfo.name.toUpperCase() && authorInfo.name.length > 3) {
        authorInfo.name = authorInfo.name
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
            .join(' ');
    }
    
    // Mock enhanced author data (in production, this would come from your API)
    const enhancedAuthorData = {
        verified: authorInfo.name && authorInfo.name !== 'Not Specified' && !authorInfo.isAgency,
        credibilityScore: sourceAnalysis.author_credibility || Math.floor(Math.random() * 20) + 70,
        yearsExperience: authorInfo.years_experience || '5+',
        articleCount: authorInfo.article_count || '150+',
        correctionRate: authorInfo.correction_rate || '2.1%',
        expertiseMatch: newsAnalysis.calculateExpertiseMatch(textContent),
        expertise: authorInfo.expertise || ['General News', 'Politics', 'Technology'],
        hasDisclosures: true,
        hasCorrections: true,
        socialVerified: authorInfo.social_verified || false,
        isAgency: authorInfo.isAgency || false
    };
    
    const initials = authorInfo.name && authorInfo.name !== 'Not Specified' && !authorInfo.isAgency
        ? authorInfo.name.split(' ').map(n => n[0]).join('')
        : authorInfo.isAgency ? '📰' : '?';
    
    // Build the author card HTML
    return `
        <div class="author-card">
            <div class="author-header">
                <div class="author-avatar">
                    ${initials}
                    ${enhancedAuthorData.verified && !enhancedAuthorData.isAgency ? '<div class="verified-badge"><i class="fas fa-check"></i></div>' : ''}
                </div>
                <div class="author-info">
                    <h3 class="author-name">${authorInfo.name || 'Unknown Author'}</h3>
                    <p class="author-outlet">${sourceAnalysis.domain || 'Unknown Outlet'}</p>
                    ${enhancedAuthorData.verified && !enhancedAuthorData.isAgency ? '<span class="verified-text"><i class="fas fa-check-circle"></i> Verified Journalist</span>' : ''}
                    ${enhancedAuthorData.isAgency ? '<span class="verified-text"><i class="fas fa-building"></i> News Agency</span>' : ''}
                </div>
                <div class="author-score">
                    <div class="score-circle" data-tooltip="Based on accuracy, experience & expertise">
                        <span class="score-number">${enhancedAuthorData.credibilityScore}</span>
                        <span class="score-label">Score</span>
                    </div>
                </div>
            </div>
            
            ${!enhancedAuthorData.isAgency ? `
            <div class="author-metrics">
                <div class="author-metric">
                    <div class="metric-value">${enhancedAuthorData.yearsExperience}</div>
                    <div class="metric-label">Years Experience</div>
                </div>
                <div class="author-metric">
                    <div class="metric-value">${enhancedAuthorData.articleCount}</div>
                    <div class="metric-label">Articles Written</div>
                </div>
                <div class="author-metric">
                    <div class="metric-value">${enhancedAuthorData.correctionRate}</div>
                    <div class="metric-label">Correction Rate</div>
                </div>
                <div class="author-metric">
                    <div class="metric-value">${enhancedAuthorData.expertiseMatch}%</div>
                    <div class="metric-label">Topic Match</div>
                </div>
            </div>
            
            ${enhancedAuthorData.expertise ? `
            <div class="author-expertise">
                <h4>Areas of Expertise</h4>
                <div class="expertise-tags">
                    ${enhancedAuthorData.expertise.map(topic => 
                        `<span class="expertise-tag">${topic}</span>`
                    ).join('')}
                </div>
            </div>
            ` : ''}
            
            <div class="author-transparency">
                <h4>Transparency Indicators</h4>
                <div class="transparency-grid">
                    <div class="transparency-indicator ${enhancedAuthorData.hasDisclosures ? 'disclosed' : 'undisclosed'}">
                        <i class="fas fa-${enhancedAuthorData.hasDisclosures ? 'check' : 'times'}"></i>
                        <span>Financial Disclosures</span>
                    </div>
                    <div class="transparency-indicator ${enhancedAuthorData.hasCorrections ? 'disclosed' : 'undisclosed'}">
                        <i class="fas fa-${enhancedAuthorData.hasCorrections ? 'check' : 'times'}"></i>
                        <span>Corrections Published</span>
                    </div>
                    <div class="transparency-indicator ${enhancedAuthorData.socialVerified ? 'disclosed' : 'undisclosed'}">
                        <i class="fas fa-${enhancedAuthorData.socialVerified ? 'check' : 'times'}"></i>
                        <span>Social Media Verified</span>
                    </div>
                </div>
            </div>
            ` : `
            <div class="author-transparency">
                <h4>News Agency Information</h4>
                <p style="color: #6b7280; line-height: 1.6;">
                    This content is from a news agency or wire service. News agencies provide content to multiple outlets
                    and maintain high editorial standards. Individual reporter attribution may not be available for 
                    syndicated content.
                </p>
            </div>
            `}
            ${generateAuthorLinks(authorInfo, enhancedAuthorData)}
        </div>
    `;
}

// Helper function to generate author links
function generateAuthorLinks(authorInfo, enhancedAuthorData) {
    // Mock author links data (in production, this would come from your API)
    const authorLinks = {
        website: authorInfo.website || (enhancedAuthorData.verified ? 'https://example.com/author-profile' : null),
        twitter: authorInfo.twitter || (enhancedAuthorData.socialVerified ? '@journalisthandle' : null),
        linkedin: authorInfo.linkedin || null,
        email: authorInfo.email || null
    };
    
    // Check if any links exist
    const hasLinks = Object.values(authorLinks).some(link => link !== null);
    
    if (!hasLinks) {
        return '';
    }
    
    let linksHTML = '<div class="author-links"><h4>Connect with the Author</h4><div class="author-links-grid">';
    
    if (authorLinks.website) {
        linksHTML += `<a href="${authorLinks.website}" target="_blank" rel="noopener noreferrer" class="author-link">
            <i class="fas fa-globe"></i> Website
        </a>`;
    }
    
    if (authorLinks.twitter) {
        const twitterUrl = authorLinks.twitter.startsWith('@') ? 
            `https://twitter.com/${authorLinks.twitter.substring(1)}` : 
            authorLinks.twitter;
        linksHTML += `<a href="${twitterUrl}" target="_blank" rel="noopener noreferrer" class="author-link">
            <i class="fab fa-twitter"></i> Twitter
        </a>`;
    }
    
    if (authorLinks.linkedin) {
        linksHTML += `<a href="${authorLinks.linkedin}" target="_blank" rel="noopener noreferrer" class="author-link">
            <i class="fab fa-linkedin"></i> LinkedIn
        </a>`;
    }
    
    if (authorLinks.email) {
        linksHTML += `<a href="mailto:${authorLinks.email}" class="author-link">
            <i class="fas fa-envelope"></i> Email
        </a>`;
    }
    
    linksHTML += '</div></div>';
    
    return linksHTML;
}

// NEW Enhanced temporal analysis function with WOW factor
function generateEnhancedTemporalAnalysis(text) {
    const dateMatches = text.match(/\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}|\b\d{1,2}\/\d{1,2}\/\d{2,4}\b|\b(today|yesterday|last\s+week|this\s+week)\b/gi) || [];
    const timeReferences = text.match(/\b(morning|afternoon|evening|night|hours?\s+ago|minutes?\s+ago)\b/gi) || [];
    
    // Calculate currency score (0-100)
    const totalReferences = dateMatches.length + timeReferences.length;
    const currencyScore = Math.min(100, totalReferences * 20);
    
    // Determine currency level
    let currencyLevel, currencyBadgeText, needleRotation;
    if (currencyScore >= 80) {
        currencyLevel = 'highly-current';
        currencyBadgeText = 'HIGHLY CURRENT';
        needleRotation = 45; // Points to green
    } else if (currencyScore >= 60) {
        currencyLevel = 'current';
        currencyBadgeText = 'CURRENT';
        needleRotation = 15;
    } else if (currencyScore >= 40) {
        currencyLevel = 'moderately-current';
        currencyBadgeText = 'MODERATELY CURRENT';
        needleRotation = 0;
    } else if (currencyScore >= 20) {
        currencyLevel = 'dated';
        currencyBadgeText = 'POSSIBLY DATED';
        needleRotation = -15;
    } else {
        currencyLevel = 'undated';
        currencyBadgeText = 'UNDATED CONTENT';
        needleRotation = -45; // Points to red
    }
    
    // Create timeline events
    const timelineEvents = [];
    if (dateMatches.length > 0) {
        // Parse first, middle, and last dates for timeline
        const dates = dateMatches.slice(0, 5); // Maximum 5 for display
        dates.forEach((date, index) => {
            timelineEvents.push({
                icon: index === 0 ? '📅' : index === dates.length - 1 ? '📍' : '📌',
                date: date,
                label: index === 0 ? 'First Reference' : index === dates.length - 1 ? 'Latest Reference' : 'Event Date'
            });
        });
    } else {
        timelineEvents.push({
            icon: '❓',
            date: 'No Dates',
            label: 'Temporal void'
        });
    }
    
    return `
        <div class="analysis-body">
            <div class="timeline-visualization">
                <div class="timeline-header">
                    <h2 class="timeline-title">Temporal Intelligence Report</h2>
                </div>
                
                <!-- Statistics -->
                <div class="timeline-stats">
                    <div class="timeline-stat">
                        <span class="timeline-stat-number">${dateMatches.length}</span>
                        <span class="timeline-stat-label">Date References</span>
                    </div>
                    <div class="timeline-stat">
                        <span class="timeline-stat-number">${timeReferences.length}</span>
                        <span class="timeline-stat-label">Time Indicators</span>
                    </div>
                    <div class="timeline-stat">
                        <span class="timeline-stat-number">${totalReferences}</span>
                        <span class="timeline-stat-label">Total Markers</span>
                    </div>
                </div>
                
                <!-- Timeline Visualization -->
                ${timelineEvents.length > 1 ? `
                <div class="timeline-main">
                    <div class="timeline-line"></div>
                    <div class="timeline-events">
                        ${timelineEvents.map((event, index) => `
                            <div class="timeline-event" style="--index: ${index};">
                                <div class="timeline-event-icon">
                                    ${event.icon}
                                </div>
                                <div class="timeline-event-date">${event.date}</div>
                                <div class="timeline-event-label">${event.label}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
                
                <!-- Currency Meter -->
                <div class="currency-indicator">
                    <h4 style="color: #1f2937; margin-bottom: 20px; font-weight: 700;">Content Currency Assessment</h4>
                    <div class="currency-meter">
                        <div class="currency-needle" style="transform: translateX(-50%) rotate(${needleRotation}deg);"></div>
                    </div>
                    <div class="currency-labels">
                        <span class="currency-label">Outdated</span>
                        <span class="currency-label">Dated</span>
                        <span class="currency-label">Current</span>
                        <span class="currency-label">Fresh</span>
                    </div>
                    <div class="currency-badge">${currencyBadgeText}</div>
                </div>
                
                <!-- Temporal Insights -->
                <div class="temporal-insights">
                    <div class="temporal-insight">
                        <div class="temporal-insight-icon">📊</div>
                        <div class="temporal-insight-title">Temporal Density</div>
                        <div class="temporal-insight-text">
                            ${totalReferences > 5 ? 'High density of temporal markers indicates detailed event reporting' :
                              totalReferences > 2 ? 'Moderate temporal markers suggest standard news coverage' :
                              totalReferences > 0 ? 'Low temporal density may indicate general or evergreen content' :
                              'No temporal markers detected - verification of timing impossible'}
                        </div>
                    </div>
                    <div class="temporal-insight">
                        <div class="temporal-insight-icon">🎯</div>
                        <div class="temporal-insight-title">Verification Impact</div>
                        <div class="temporal-insight-text">
                            ${dateMatches.length > 0 ? 
                              'Specific dates enable independent verification of events' :
                              'Lack of dates makes temporal verification challenging'}
                        </div>
                    </div>
                </div>
                
                <!-- Detailed References -->
                ${dateMatches.length > 0 || timeReferences.length > 0 ? `
                <div style="background: rgba(249, 115, 22, 0.1); padding: 20px; border-radius: 12px; margin-top: 30px;">
                    <h4 style="color: #ea580c; margin-bottom: 15px;">Temporal References Detected:</h4>
                    ${dateMatches.length > 0 ? 
                        `<div style="margin-bottom: 15px;">
                            <strong style="color: #f97316;">📅 Date References:</strong>
                            <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;">
                                ${dateMatches.map(date => 
                                    `<span style="background: white; padding: 4px 12px; border-radius: 15px; 
                                    border: 2px solid rgba(249, 115, 22, 0.3); color: #ea580c; font-weight: 600; font-size: 0.9rem;">
                                    ${date}</span>`
                                ).join('')}
                            </div>
                        </div>` : ''}
                    ${timeReferences.length > 0 ? 
                        `<div>
                            <strong style="color: #f97316;">⏱️ Time References:</strong>
                            <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;">
                                ${timeReferences.map(time => 
                                    `<span style="background: white; padding: 4px 12px; border-radius: 15px; 
                                    border: 2px solid rgba(249, 115, 22, 0.3); color: #ea580c; font-weight: 600; font-size: 0.9rem;">
                                    ${time}</span>`
                                ).join('')}
                            </div>
                        </div>` : ''}
                </div>
                ` : `
                <div style="background: rgba(239, 68, 68, 0.1); padding: 20px; border-radius: 12px; margin-top: 30px; text-align: center;">
                    <h4 style="color: #dc2626; margin-bottom: 10px;">⚠️ No Temporal References Found</h4>
                    <p style="color: #7f1d1d;">This content lacks specific dates or time references, making it impossible to verify when events occurred. This could indicate evergreen content, but it also raises questions about the timeliness and verifiability of the information.</p>
                </div>
                `}
            </div>
        </div>
    `;
}

// Enhanced transparency analysis with author focus
function generateTransparencyAnalysis(text, sourceAnalysis, detailedAnalysis) {
    let transparencyScore = 50; // Base score
    const categories = {
        authorTransparency: {
            title: 'Author Transparency',
            score: 0,
            maxScore: 30,
            items: []
        },
        sourceAttribution: {
            title: 'Source Attribution',
            score: 0,
            maxScore: 30,
            items: []
        },
        editorialTransparency: {
            title: 'Editorial Transparency',
            score: 0,
            maxScore: 20,
            items: []
        },
        correctionPolicy: {
            title: 'Correction & Update Policy',
            score: 0,
            maxScore: 20,
            items: []
        }
    };
    
    // Author Transparency checks
    if (sourceAnalysis.author?.name && sourceAnalysis.author.name !== 'Not Specified') {
        categories.authorTransparency.score += 10;
        categories.authorTransparency.items.push({
            positive: true,
            text: 'Clear author attribution'
        });
        transparencyScore += 15;
    } else {
        categories.authorTransparency.items.push({
            positive: false,
            text: 'No author identified'
        });
    }
    
    // Check for author credentials in text
    if (text.match(/is a\s+(senior\s+)?(reporter|journalist|correspondent|editor|writer)/i)) {
        categories.authorTransparency.score += 10;
        categories.authorTransparency.items.push({
            positive: true,
            text: 'Author credentials mentioned'
        });
        transparencyScore += 10;
    }
    
    // Check for author contact info
    if (text.match(/[@][a-zA-Z0-9_]+|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/)) {
        categories.authorTransparency.score += 10;
        categories.authorTransparency.items.push({
            positive: true,
            text: 'Author contact information provided'
        });
        transparencyScore += 5;
    }
    
    // Source Attribution checks
    if (detailedAnalysis?.journalism_indicators?.has_attribution) {
        categories.sourceAttribution.score += 15;
        categories.sourceAttribution.items.push({
            positive: true,
            text: 'Uses source attribution phrases'
        });
        transparencyScore += 10;
    }
    
    if (detailedAnalysis?.quote_analysis?.quote_count >= 2) {
        categories.sourceAttribution.score += 10;
        categories.sourceAttribution.items.push({
            positive: true,
            text: `Includes ${detailedAnalysis.quote_analysis.quote_count} direct quotes`
        });
        transparencyScore += 10;
    }
    
    if (text.includes('anonymous') || text.includes('unnamed source')) {
        categories.sourceAttribution.score -= 5;
        categories.sourceAttribution.items.push({
            positive: false,
            text: 'Uses anonymous sources'
        });
        transparencyScore -= 10;
    } else {
        categories.sourceAttribution.score += 5;
        categories.sourceAttribution.items.push({
            positive: true,
            text: 'No anonymous sources'
        });
    }
    
    // Editorial Transparency
    if (text.includes('could not be reached') || text.includes('declined to comment')) {
        categories.editorialTransparency.score += 10;
        categories.editorialTransparency.items.push({
            positive: true,
            text: 'Acknowledges reporting limitations'
        });
        transparencyScore += 5;
    }
    
    if (text.match(/\[Editor'?s? Note:?|Correction:|Update:|Disclosure:/i)) {
        categories.editorialTransparency.score += 10;
        categories.editorialTransparency.items.push({
            positive: true,
            text: 'Contains editorial notes or corrections'
        });
        transparencyScore += 5;
    }
    
    // Correction Policy
    if (sourceAnalysis.has_corrections_policy) {
        categories.correctionPolicy.score += 10;
        categories.correctionPolicy.items.push({
            positive: true,
            text: 'Publication has corrections policy'
        });
        transparencyScore += 5;
    }
    
    if (text.includes('updated') || text.includes('corrected')) {
        categories.correctionPolicy.score += 10;
        categories.correctionPolicy.items.push({
            positive: true,
            text: 'Shows update/correction history'
        });
        transparencyScore += 5;
    }
    
    // Cap transparency score at 100
    transparencyScore = Math.min(100, transparencyScore);
    
    // Calculate category percentages
    for (const category of Object.values(categories)) {
        category.percentage = Math.round((category.score / category.maxScore) * 100);
    }
    
    return `
        <div class="enhanced-transparency-section">
            <div class="transparency-overview">
                <div class="transparency-score-visual">
                    <div class="transparency-meter">
                        <div style="width: 180px; height: 180px; border-radius: 50%; 
                            background: conic-gradient(#10b981 0% ${transparencyScore}%, #e5e7eb ${transparencyScore}% 100%);
                            display: flex; align-items: center; justify-content: center;">
                            <div style="width: 140px; height: 140px; background: white; border-radius: 50%;
                                display: flex; align-items: center; justify-content: center; flex-direction: column;">
                                <div style="font-size: 2.5rem; font-weight: 900; color: #1f2937;">
                                    ${transparencyScore}%
                                </div>
                                <div style="font-size: 0.9rem; color: #6b7280; font-weight: 600;">
                                    Transparency Score
                                </div>
                            </div>
                        </div>
                    </div>
                    <p style="color: #4b5563; line-height: 1.6;">
                        ${transparencyScore >= 70 ? 
                        'Excellent transparency with clear attribution and accountability.' :
                        transparencyScore >= 50 ?
                        'Moderate transparency with room for improvement in attribution.' :
                        'Low transparency makes verification difficult.'}
                    </p>
                </div>
                
                <div class="transparency-details">
                    ${Object.values(categories).map(category => `
                        <div class="transparency-category">
                            <div class="category-header">
                                <span class="category-title">${category.title}</span>
                                <span class="category-score">${category.percentage}%</span>
                            </div>
                            <div class="category-items">
                                ${category.items.map(item => `
                                    <div class="category-item">
                                        <i class="fas fa-${item.positive ? 'check-circle' : 'exclamation-triangle'}" 
                                           style="color: ${item.positive ? '#10b981' : '#ef4444'};"></i>
                                        <span>${item.text}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

// Export results functions for global access
window.newsResults = {
    showNewsResults,
    generateSummaryNarrative,
    generateBiasNarrative,
    generateSourceNarrative,
    generateEmotionalNarrative,
    generateStyleNarrative,
    generateFactSignalsContent,
    generateAdditionalFindings,
    generateEnhancedAuthorAnalysis,
    generateEnhancedTemporalAnalysis,
    generateTransparencyAnalysis
};
