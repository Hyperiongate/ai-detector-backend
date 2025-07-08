// enhanced-news-results.js - Enhanced UI with REAL data connections
// This file creates beautiful visualizations using only real data from your backend 

(function() {
    'use strict';
    
    window.NewsApp = window.NewsApp || {};
    
    NewsApp.enhancedResults = {
        // Display results with enhanced UI but REAL data
        displayResults: function(data) {
            console.log('Displaying enhanced results with real data:', data);
            
            if (!data || !data.results) {
                this.showError('Invalid analysis data received');
                return;
            }
            
            const results = data.results;
            const resultsDiv = document.getElementById('results');
            
            if (!resultsDiv) {
                console.error('Results div not found');
                return;
            }
            
            // Extract REAL data from backend
            const trustScore = results.credibility || 0;
            const biasData = results.bias || {};
            const sourceInfo = results.sources || {};
            const authorName = results.author || 'Not Specified';
            const styleData = results.style || {};
            const claims = results.claims || [];
            const crossRefs = results.cross_references || [];
            
            // Build enhanced UI with REAL data
            resultsDiv.innerHTML = `
                <div class="enhanced-results-container" style="
                    background: linear-gradient(135deg, rgba(10,14,39,0.95), rgba(0,0,0,0.95));
                    border: 2px solid rgba(0,255,255,0.3);
                    border-radius: 20px;
                    padding: 40px;
                    margin: 20px 0;
                    color: #fff;
                    position: relative;
                    overflow: hidden;
                    box-shadow: 0 0 40px rgba(0,255,255,0.3);
                ">
                    <!-- Animated background pattern -->
                    <div style="
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        opacity: 0.05;
                        background-image: repeating-linear-gradient(
                            45deg,
                            transparent,
                            transparent 10px,
                            rgba(0,255,255,0.1) 10px,
                            rgba(0,255,255,0.1) 20px
                        );
                        pointer-events: none;
                    "></div>
                    
                    <!-- Header -->
                    <div class="results-header" style="text-align: center; margin-bottom: 40px; position: relative;">
                        <h2 style="
                            font-size: 2.5em;
                            background: linear-gradient(45deg, #00ffff, #ff00ff, #00ff88);
                            background-size: 200% 200%;
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                            animation: gradientShift 4s ease infinite;
                            margin-bottom: 10px;
                        ">Analysis Complete</h2>
                        <p style="color: #00ffff; opacity: 0.8;">
                            Powered by keyword analysis and source verification
                        </p>
                    </div>
                    
                    <!-- Main Metrics Row -->
                    <div style="
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 30px;
                        margin-bottom: 40px;
                    ">
                        <!-- Trust Score Circle (REAL DATA) -->
                        <div style="text-align: center;">
                            <h3 style="color: #00ffff; margin-bottom: 20px; font-size: 1.5em;">Trust Score</h3>
                            ${this.createTrustCircle(trustScore)}
                            <p style="color: #aaa; margin-top: 10px; font-size: 14px;">
                                Based on source credibility and content analysis
                            </p>
                        </div>
                        
                        <!-- Bias Gauge (REAL DATA) -->
                        <div style="text-align: center;">
                            <h3 style="color: #ff00ff; margin-bottom: 20px; font-size: 1.5em;">Political Bias</h3>
                            ${this.createBiasGauge(biasData)}
                            <p style="color: #aaa; margin-top: 10px; font-size: 14px;">
                                Objectivity: ${biasData.objectivity || 0}%
                            </p>
                        </div>
                    </div>
                    
                    <!-- Analysis Cards (REAL DATA) -->
                    <div class="analysis-cards" style="margin-bottom: 30px;">
                        <h3 style="color: #00ffff; text-align: center; margin-bottom: 30px; font-size: 1.8em;">
                            Detailed Analysis
                        </h3>
                        
                        <div style="
                            display: grid;
                            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                            gap: 20px;
                        ">
                            <!-- Source Verification Card -->
                            ${this.createAnalysisCard(
                                '🔍',
                                'Source Verification',
                                this.getSourceVerificationContent(sourceInfo),
                                '#00ffff'
                            )}
                            
                            <!-- Author Information Card -->
                            ${this.createAnalysisCard(
                                '👤',
                                'Author Information',
                                this.getAuthorContent(authorName),
                                '#ff00ff'
                            )}
                            
                            <!-- Content Analysis Card -->
                            ${this.createAnalysisCard(
                                '📊',
                                'Content Analysis',
                                this.getContentAnalysisContent(styleData),
                                '#00ff88'
                            )}
                            
                            <!-- Bias Indicators Card -->
                            ${this.createAnalysisCard(
                                '⚖️',
                                'Bias Indicators',
                                this.getBiasIndicatorsContent(biasData),
                                '#ffff00'
                            )}
                            
                            <!-- Fact Checking Card (Conditional) -->
                            ${claims.length > 0 ? this.createAnalysisCard(
                                '✓',
                                'Fact Checking',
                                this.getFactCheckingContent(claims),
                                '#ff8800'
                            ) : ''}
                            
                            <!-- Cross References Card (Conditional) -->
                            ${crossRefs.length > 0 ? this.createAnalysisCard(
                                '🔗',
                                'Cross References',
                                this.getCrossReferencesContent(crossRefs),
                                '#ff0088'
                            ) : ''}
                        </div>
                    </div>
                    
                    <!-- Action Buttons -->
                    <div style="
                        display: flex;
                        gap: 15px;
                        justify-content: center;
                        margin-top: 40px;
                        flex-wrap: wrap;
                    ">
                        <button onclick="NewsApp.ui.resetAnalysis()" style="
                            background: linear-gradient(45deg, #00ffff, #0099cc);
                            color: #0a0e27;
                            border: none;
                            padding: 15px 30px;
                            border-radius: 10px;
                            font-size: 16px;
                            font-weight: bold;
                            cursor: pointer;
                            transition: all 0.3s;
                            box-shadow: 0 4px 15px rgba(0,255,255,0.4);
                        ">
                            🔄 New Analysis
                        </button>
                    </div>
                    
                    <!-- Methodology Note -->
                    <div style="
                        text-align: center;
                        padding: 20px;
                        background: rgba(255,255,255,0.05);
                        border-radius: 10px;
                        margin-top: 30px;
                    ">
                        <p style="color: #aaa; font-size: 14px; margin: 0;">
                            <strong>Analysis Method:</strong> 
                            ${results.methodology?.analysis_type || 'Keyword-based analysis'} | 
                            Processing time: ${results.methodology?.processing_time || 'N/A'} | 
                            Source database: ${Object.keys(sourceInfo).length > 0 ? 'Verified' : 'Not in database'}
                        </p>
                    </div>
                </div>
            `;
            
            resultsDiv.style.display = 'block';
            resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
            
            // Add gradient animation
            const style = document.createElement('style');
            style.textContent = `
                @keyframes gradientShift {
                    0% { background-position: 0% 50%; }
                    50% { background-position: 100% 50%; }
                    100% { background-position: 0% 50%; }
                }
            `;
            document.head.appendChild(style);
        },
        
        // Create animated trust circle with REAL score
        createTrustCircle: function(score) {
            const radius = 80;
            const circumference = 2 * Math.PI * radius;
            const offset = circumference - (score / 100) * circumference;
            
            const color = score >= 80 ? '#00ff88' : score >= 60 ? '#ffff00' : '#ff4444';
            const label = score >= 80 ? 'High' : score >= 60 ? 'Moderate' : 'Low';
            
            return `
                <div style="position: relative; display: inline-block;">
                    <svg width="200" height="200" style="transform: rotate(-90deg);">
                        <!-- Background circle -->
                        <circle
                            cx="100"
                            cy="100"
                            r="${radius}"
                            stroke="rgba(255,255,255,0.1)"
                            stroke-width="15"
                            fill="none"
                        />
                        <!-- Progress circle -->
                        <circle
                            cx="100"
                            cy="100"
                            r="${radius}"
                            stroke="${color}"
                            stroke-width="15"
                            fill="none"
                            stroke-dasharray="${circumference}"
                            stroke-dashoffset="${offset}"
                            style="
                                transition: stroke-dashoffset 1s ease-in-out;
                                filter: drop-shadow(0 0 10px ${color});
                            "
                        />
                    </svg>
                    <div style="
                        position: absolute;
                        top: 50%;
                        left: 50%;
                        transform: translate(-50%, -50%);
                        text-align: center;
                    ">
                        <div style="font-size: 48px; font-weight: bold; color: ${color};">
                            ${score}%
                        </div>
                        <div style="font-size: 18px; color: #aaa; margin-top: 5px;">
                            ${label} Trust
                        </div>
                    </div>
                </div>
            `;
        },
        
        // Create bias gauge with REAL data
        createBiasGauge: function(biasData) {
            const score = biasData.score || 0; // -10 to +10
            const label = biasData.label || 'Unknown';
            const position = ((score + 10) / 20) * 100; // Convert to 0-100%
            
            return `
                <div style="position: relative; width: 200px; margin: 0 auto;">
                    <!-- Gauge background -->
                    <div style="
                        height: 100px;
                        background: linear-gradient(to right, #0066cc, #888, #cc0000);
                        border-radius: 100px 100px 0 0;
                        position: relative;
                        overflow: hidden;
                        box-shadow: inset 0 0 20px rgba(0,0,0,0.3);
                    ">
                        <!-- Gauge needle -->
                        <div style="
                            position: absolute;
                            bottom: 0;
                            left: ${position}%;
                            width: 2px;
                            height: 100px;
                            background: #fff;
                            transform-origin: bottom;
                            transition: left 1s ease-in-out;
                            box-shadow: 0 0 10px rgba(255,255,255,0.8);
                        "></div>
                        <!-- Center dot -->
                        <div style="
                            position: absolute;
                            bottom: -5px;
                            left: ${position}%;
                            width: 10px;
                            height: 10px;
                            background: #fff;
                            border-radius: 50%;
                            transform: translateX(-50%);
                            box-shadow: 0 0 10px rgba(255,255,255,0.8);
                        "></div>
                    </div>
                    <!-- Labels -->
                    <div style="
                        display: flex;
                        justify-content: space-between;
                        margin-top: 10px;
                        font-size: 12px;
                        color: #aaa;
                    ">
                        <span>Left</span>
                        <span>Center</span>
                        <span>Right</span>
                    </div>
                    <!-- Current bias label -->
                    <div style="
                        text-align: center;
                        margin-top: 10px;
                        font-size: 18px;
                        font-weight: bold;
                        text-transform: capitalize;
                        color: ${label.includes('left') ? '#0066cc' : label.includes('right') ? '#cc0000' : '#888'};
                    ">
                        ${label}
                    </div>
                </div>
            `;
        },
        
        // Create expandable analysis card
        createAnalysisCard: function(icon, title, content, color) {
            const cardId = title.toLowerCase().replace(/\s+/g, '-');
            return `
                <div class="analysis-card" style="
                    background: rgba(255,255,255,0.05);
                    border: 1px solid ${color}33;
                    border-radius: 15px;
                    padding: 20px;
                    cursor: pointer;
                    transition: all 0.3s;
                    position: relative;
                    overflow: hidden;
                " 
                onmouseover="this.style.borderColor='${color}66'; this.style.background='rgba(255,255,255,0.08)'; this.style.transform='translateY(-2px)'; this.style.boxShadow='0 5px 20px rgba(0,0,0,0.3)'"
                onmouseout="this.style.borderColor='${color}33'; this.style.background='rgba(255,255,255,0.05)'; this.style.transform='translateY(0)'; this.style.boxShadow='none'"
                onclick="NewsApp.enhancedResults.toggleCard('${cardId}')">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center;">
                            <span style="font-size: 24px; margin-right: 10px;">${icon}</span>
                            <h4 style="color: ${color}; margin: 0; font-size: 16px;">${title}</h4>
                        </div>
                        <span id="${cardId}-arrow" style="color: ${color}; transition: transform 0.3s;">▼</span>
                    </div>
                    <div id="${cardId}-content" style="
                        max-height: 0;
                        overflow: hidden;
                        transition: max-height 0.3s ease-out;
                        margin-top: 0;
                    ">
                        <div style="padding-top: 15px; color: #ddd;">
                            ${content}
                        </div>
                    </div>
                </div>
            `;
        },
        
        // Get REAL source verification content
        getSourceVerificationContent: function(sourceInfo) {
            if (!sourceInfo.domain || sourceInfo.domain === 'Unknown Source' || sourceInfo.domain === 'Direct Input') {
                return `
                    <p style="color: #ff4444;">⚠️ Source not in our database</p>
                    <p style="color: #aaa; font-size: 14px; margin-top: 10px;">
                        This source has not been verified. We check against 14 major news sources.
                        Consider verifying information with multiple sources.
                    </p>
                `;
            }
            
            return `
                <p><strong>Source:</strong> ${sourceInfo.name || sourceInfo.domain}</p>
                <p><strong>Credibility:</strong> ${sourceInfo.credibility || 'Unknown'}%</p>
                <p><strong>Political Bias:</strong> ${sourceInfo.bias || 'Unknown'}</p>
                <p style="color: #aaa; font-size: 14px; margin-top: 10px;">
                    ✓ Verified against our database of 14 major news sources
                </p>
            `;
        },
        
        // Get REAL author content
        getAuthorContent: function(authorName) {
            if (authorName === 'Not Specified' || authorName === 'Unknown Author') {
                return `
                    <p style="color: #ff4444;">⚠️ No author information found</p>
                    <p style="color: #aaa; font-size: 14px; margin-top: 10px;">
                        Articles without clear authorship may be less reliable.
                        Always verify information from unattributed sources.
                    </p>
                `;
            }
            
            return `
                <p><strong>Author:</strong> ${authorName}</p>
                <p style="color: #aaa; font-size: 14px; margin-top: 10px;">
                    ✓ Author detected from article content
                    <br><br>
                    Note: We do not track author history or credentials.
                    This is simply the byline extracted from the article.
                </p>
            `;
        },
        
        // Get REAL content analysis
        getContentAnalysisContent: function(styleData) {
            const quotes = styleData.quotes || 0;
            const stats = styleData.statistics || 0;
            const quality = quotes >= 2 && stats >= 2 ? 'Good' : quotes >= 1 || stats >= 1 ? 'Fair' : 'Limited';
            
            return `
                <p><strong>Quotations Found:</strong> ${quotes}</p>
                <p><strong>Statistical Claims:</strong> ${stats}</p>
                <p><strong>Reading Level:</strong> Grade ${styleData.readingLevel || 'N/A'}</p>
                <p><strong>Content Quality:</strong> ${quality}</p>
                <p style="color: #aaa; font-size: 14px; margin-top: 10px;">
                    Based on text structure analysis. Articles with more quotes
                    and statistics tend to be more credible.
                </p>
            `;
        },
        
        // Get REAL bias indicators content
        getBiasIndicatorsContent: function(biasData) {
            const total = (biasData.left_indicators || 0) + (biasData.right_indicators || 0);
            
            return `
                <p><strong>Political Bias:</strong> ${biasData.label || 'Unknown'}</p>
                <p><strong>Bias Score:</strong> ${biasData.score || 0} <span style="color: #aaa; font-size: 12px;">(scale: -10 to +10)</span></p>
                <p><strong>Left Keywords:</strong> ${biasData.left_indicators || 0}</p>
                <p><strong>Right Keywords:</strong> ${biasData.right_indicators || 0}</p>
                <p><strong>Emotional Language:</strong> ${biasData.emotional_indicators || 0} words</p>
                <p style="color: #aaa; font-size: 14px; margin-top: 10px;">
                    Detected using keyword frequency analysis.
                    ${total > 0 ? `Found ${total} political indicator words.` : 'No strong political indicators found.'}
                </p>
            `;
        },
        
        // Get REAL fact checking content (only if available)
        getFactCheckingContent: function(claims) {
            if (claims.length === 0) {
                return `<p style="color: #aaa;">No claims extracted for verification</p>`;
            }
            
            return `
                <p><strong>Claims Identified:</strong> ${claims.length}</p>
                ${claims.slice(0, 3).map((claim, index) => `
                    <div style="
                        background: rgba(255,255,255,0.05);
                        padding: 10px;
                        border-radius: 5px;
                        margin-top: 10px;
                        border-left: 3px solid ${claim.confidence >= 80 ? '#00ff88' : claim.confidence >= 60 ? '#ffff00' : '#ff4444'};
                    ">
                        <p style="font-size: 14px; color: #ddd; margin: 0 0 5px 0;">
                            "${claim.claim.substring(0, 100)}${claim.claim.length > 100 ? '...' : ''}"
                        </p>
                        <p style="font-size: 12px; color: #aaa; margin: 0;">
                            Status: ${claim.status} | Confidence: ${claim.confidence}%
                        </p>
                    </div>
                `).join('')}
                <p style="color: #aaa; font-size: 14px; margin-top: 10px;">
                    AI-powered fact checking (requires Pro subscription with OpenAI integration)
                </p>
            `;
        },
        
        // Get REAL cross references content (only if available)
        getCrossReferencesContent: function(crossRefs) {
            if (crossRefs.length === 0) {
                return `
                    <p style="color: #aaa;">No cross-references available</p>
                    <p style="color: #aaa; font-size: 14px; margin-top: 10px;">
                        Cross-reference data requires Pro subscription
                    </p>
                `;
            }
            
            return `
                <p><strong>Related Coverage Found:</strong></p>
                ${crossRefs.map(ref => `
                    <div style="
                        background: rgba(255,255,255,0.05);
                        padding: 10px;
                        border-radius: 5px;
                        margin-top: 10px;
                    ">
                        <p style="font-size: 14px; color: #ddd; margin: 0 0 5px 0;">
                            ${ref.source}: ${ref.title}
                        </p>
                        <p style="font-size: 12px; color: #aaa; margin: 0;">
                            Relevance: ${ref.relevance}%
                        </p>
                    </div>
                `).join('')}
            `;
        },
        
        // Toggle card expansion
        toggleCard: function(cardId) {
            const content = document.getElementById(cardId + '-content');
            const arrow = document.getElementById(cardId + '-arrow');
            
            if (content.style.maxHeight && content.style.maxHeight !== '0px') {
                content.style.maxHeight = '0';
                arrow.style.transform = 'rotate(0deg)';
            } else {
                content.style.maxHeight = content.scrollHeight + 'px';
                arrow.style.transform = 'rotate(180deg)';
            }
        },
        
        // Show error message
        showError: function(message) {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = `
                <div style="
                    background: rgba(255,0,0,0.1);
                    border: 2px solid #ff4444;
                    color: #ff4444;
                    padding: 30px;
                    border-radius: 15px;
                    text-align: center;
                    margin: 20px 0;
                ">
                    <h3 style="margin: 0 0 10px 0;">⚠️ Analysis Error</h3>
                    <p style="margin: 0 0 20px 0;">${message}</p>
                    <button onclick="NewsApp.ui.resetAnalysis()" style="
                        background: #ff4444;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 5px;
                        cursor: pointer;
                        font-weight: bold;
                    ">Try Again</button>
                </div>
            `;
            resultsDiv.style.display = 'block';
        }
    };
    
    // Make available globally
    window.NewsApp.enhancedResults = NewsApp.enhancedResults;
    
})();
