// news-results.js - Enhanced Results Display with Expandable Cards and Real Data
(function() {
    'use strict';
    
    // Create namespace
    window.NewsApp = window.NewsApp || {};
    
    NewsApp.results = {
        // Display the complete analysis results with enhanced UI
        displayResults: function(data) {
            console.log('Displaying enhanced results with expandable cards:', data);
            
            if (!data || !data.results) {
                console.error('Invalid data structure:', data);
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
            const temporalData = results.temporal_analysis || {};
            const contentStats = results.content_stats || {};
            
            // Build enhanced UI with expandable cards
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
                        <!-- Trust Score Circle -->
                        <div style="text-align: center;">
                            <h3 style="color: #00ffff; margin-bottom: 20px; font-size: 1.5em;">Trust Score</h3>
                            ${this.createTrustCircle(trustScore)}
                            <p style="color: #aaa; margin-top: 10px; font-size: 14px;">
                                Based on source credibility and content analysis
                            </p>
                        </div>
                        
                        <!-- Bias Gauge -->
                        <div style="text-align: center;">
                            <h3 style="color: #ff00ff; margin-bottom: 20px; font-size: 1.5em;">Political Bias</h3>
                            ${this.createBiasGauge(biasData)}
                            <p style="color: #aaa; margin-top: 10px; font-size: 14px;">
                                Objectivity: ${biasData.objectivity || 0}%
                            </p>
                        </div>
                    </div>
                    
                    <!-- 8 Expandable Analysis Cards -->
                    <div class="analysis-cards" style="margin-bottom: 30px;">
                        <h3 style="color: #00ffff; text-align: center; margin-bottom: 30px; font-size: 1.8em;">
                            Detailed Analysis - Click Cards to Expand
                        </h3>
                        
                        <div style="
                            display: grid;
                            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                            gap: 20px;
                        ">
                            <!-- 1. Credibility Analysis Card -->
                            ${this.createExpandableCard(
                                '🎯',
                                'Credibility Analysis',
                                this.getCredibilityContent(trustScore, sourceInfo),
                                '#00ffff',
                                'credibility'
                            )}
                            
                            <!-- 2. Bias Detection Card -->
                            ${this.createExpandableCard(
                                '⚖️',
                                'Bias Detection',
                                this.getBiasContent(biasData),
                                '#ff00ff',
                                'bias'
                            )}
                            
                            <!-- 3. Source Verification Card -->
                            ${this.createExpandableCard(
                                '🔍',
                                'Source Verification',
                                this.getSourceContent(sourceInfo),
                                '#00ff88',
                                'source'
                            )}
                            
                            <!-- 4. Author Information Card -->
                            ${this.createExpandableCard(
                                '👤',
                                'Author Information',
                                this.getAuthorContent(authorName, sourceInfo),
                                '#ffff00',
                                'author'
                            )}
                            
                            <!-- 5. Writing Style Card -->
                            ${this.createExpandableCard(
                                '✍️',
                                'Writing Style Analysis',
                                this.getStyleContent(styleData),
                                '#ff8800',
                                'style'
                            )}
                            
                            <!-- 6. Fact Checking Card -->
                            ${this.createExpandableCard(
                                '✓',
                                'Fact Checking',
                                this.getFactCheckContent(claims),
                                '#ff0088',
                                'facts'
                            )}
                            
                            <!-- 7. Cross References Card -->
                            ${this.createExpandableCard(
                                '🔗',
                                'Cross References',
                                this.getCrossRefContent(crossRefs),
                                '#8800ff',
                                'crossref'
                            )}
                            
                            <!-- 8. Temporal Analysis Card -->
                            ${this.createExpandableCard(
                                '📅',
                                'Temporal Analysis',
                                this.getTemporalContent(temporalData, contentStats),
                                '#00ffcc',
                                'temporal'
                            )}
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
                        <button onclick="NewsApp.results.generatePDF()" style="
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
                            display: flex;
                            align-items: center;
                            gap: 8px;
                        " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(0,255,255,0.6)'"
                           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(0,255,255,0.4)'">
                            📄 Download PDF Report
                        </button>
                        
                        <button onclick="NewsApp.results.shareResults()" style="
                            background: linear-gradient(45deg, #ff00ff, #cc00cc);
                            color: #fff;
                            border: none;
                            padding: 15px 30px;
                            border-radius: 10px;
                            font-size: 16px;
                            font-weight: bold;
                            cursor: pointer;
                            transition: all 0.3s;
                            box-shadow: 0 4px 15px rgba(255,0,255,0.4);
                            display: flex;
                            align-items: center;
                            gap: 8px;
                        " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(255,0,255,0.6)'"
                           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(255,0,255,0.4)'">
                            📤 Share Analysis
                        </button>
                        
                        <button onclick="NewsApp.ui.resetAnalysis()" style="
                            background: linear-gradient(45deg, #00ff88, #00cc66);
                            color: #0a0e27;
                            border: none;
                            padding: 15px 30px;
                            border-radius: 10px;
                            font-size: 16px;
                            font-weight: bold;
                            cursor: pointer;
                            transition: all 0.3s;
                            box-shadow: 0 4px 15px rgba(0,255,136,0.4);
                            display: flex;
                            align-items: center;
                            gap: 8px;
                        " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(0,255,136,0.6)'"
                           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(0,255,136,0.4)'">
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
            
            // Show results section
            resultsDiv.style.display = 'block';
            
            // Scroll to results
            resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
            
            // Add gradient animation style if not already added
            if (!document.getElementById('gradient-animation-style')) {
                const style = document.createElement('style');
                style.id = 'gradient-animation-style';
                style.textContent = `
                    @keyframes gradientShift {
                        0% { background-position: 0% 50%; }
                        50% { background-position: 100% 50%; }
                        100% { background-position: 0% 50%; }
                    }
                `;
                document.head.appendChild(style);
            }
        },
        
        // Create animated trust circle
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
        
        // Create bias gauge
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
        
        // Create expandable card with animation
        createExpandableCard: function(icon, title, content, color, id) {
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
                onclick="NewsApp.results.toggleCard('${id}')">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center;">
                            <span style="font-size: 28px; margin-right: 12px;">${icon}</span>
                            <h4 style="color: ${color}; margin: 0; font-size: 18px; font-weight: 600;">${title}</h4>
                        </div>
                        <span id="${id}-arrow" style="color: ${color}; transition: transform 0.3s; font-size: 20px;">▼</span>
                    </div>
                    <div id="${id}-content" style="
                        max-height: 0;
                        overflow: hidden;
                        transition: max-height 0.3s ease-out;
                        margin-top: 0;
                    ">
                        <div style="padding-top: 20px; color: #ddd; line-height: 1.6;">
                            ${content}
                        </div>
                    </div>
                </div>
            `;
        },
        
        // Card content generators with REAL data
        getCredibilityContent: function(score, sourceInfo) {
            return `
                <div style="background: rgba(0,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <h5 style="color: #00ffff; margin: 0 0 10px 0;">Overall Credibility Score</h5>
                    <div style="font-size: 36px; font-weight: bold; color: ${score >= 80 ? '#00ff88' : score >= 60 ? '#ffff00' : '#ff4444'};">
                        ${score}%
                    </div>
                </div>
                
                <h5 style="color: #00ffff; margin: 20px 0 10px 0;">Credibility Factors:</h5>
                <ul style="list-style: none; padding: 0; margin: 0;">
                    <li style="margin-bottom: 8px;">✓ Source verification: ${sourceInfo.domain ? 'Verified' : 'Not in database'}</li>
                    <li style="margin-bottom: 8px;">✓ Author attribution: ${sourceInfo.author ? 'Present' : 'Missing'}</li>
                    <li style="margin-bottom: 8px;">✓ Content structure: Analyzed</li>
                    <li style="margin-bottom: 8px;">✓ Citation quality: Assessed</li>
                </ul>
                
                <p style="color: #aaa; font-size: 14px; margin-top: 15px;">
                    Credibility score is calculated based on source reputation, author credentials, 
                    citation quality, and content structure analysis.
                </p>
            `;
        },
        
        getBiasContent: function(biasData) {
            return `
                <div style="background: rgba(255,0,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <h5 style="color: #ff00ff; margin: 0 0 10px 0;">Political Bias Analysis</h5>
                    <div style="font-size: 24px; font-weight: bold; color: #ff00ff; text-transform: capitalize;">
                        ${biasData.label || 'Unknown'}
                    </div>
                    <div style="font-size: 14px; color: #aaa; margin-top: 5px;">
                        Bias Score: ${biasData.score || 0} (scale: -10 to +10)
                    </div>
                </div>
                
                <h5 style="color: #ff00ff; margin: 20px 0 10px 0;">Bias Indicators Found:</h5>
                <ul style="list-style: none; padding: 0; margin: 0;">
                    <li style="margin-bottom: 8px;">📊 Left-leaning keywords: ${biasData.left_indicators || 0}</li>
                    <li style="margin-bottom: 8px;">📊 Right-leaning keywords: ${biasData.right_indicators || 0}</li>
                    <li style="margin-bottom: 8px;">📊 Emotional language: ${biasData.emotional_indicators || 0} words</li>
                    <li style="margin-bottom: 8px;">📊 Objectivity score: ${biasData.objectivity || 0}%</li>
                </ul>
                
                <p style="color: #aaa; font-size: 14px; margin-top: 15px;">
                    Bias detection uses keyword frequency analysis to identify political leaning 
                    and emotional language patterns.
                </p>
            `;
        },
        
        getSourceContent: function(sourceInfo) {
            if (!sourceInfo.domain || sourceInfo.domain === 'Unknown Source' || sourceInfo.domain === 'Direct Input') {
                return `
                    <div style="background: rgba(255,100,100,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                        <h5 style="color: #ff4444; margin: 0 0 10px 0;">⚠️ Source Not Verified</h5>
                        <p style="color: #ddd; margin: 0;">
                            This source is not in our database of verified news outlets.
                        </p>
                    </div>
                    
                    <p style="color: #aaa; font-size: 14px; margin-top: 15px;">
                        We verify sources against 14 major news outlets including Reuters, BBC, CNN, Fox News, 
                        and others. Consider cross-checking information from unverified sources.
                    </p>
                `;
            }
            
            return `
                <div style="background: rgba(0,255,136,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <h5 style="color: #00ff88; margin: 0 0 10px 0;">✓ Verified Source</h5>
                    <div style="font-size: 20px; font-weight: bold; color: #00ff88;">
                        ${sourceInfo.name || sourceInfo.domain}
                    </div>
                </div>
                
                <h5 style="color: #00ff88; margin: 20px 0 10px 0;">Source Details:</h5>
                <ul style="list-style: none; padding: 0; margin: 0;">
                    <li style="margin-bottom: 8px;">🌐 Domain: ${sourceInfo.domain}</li>
                    <li style="margin-bottom: 8px;">📊 Credibility: ${sourceInfo.credibility}%</li>
                    <li style="margin-bottom: 8px;">⚖️ Known bias: ${sourceInfo.bias || 'Unknown'}</li>
                    <li style="margin-bottom: 8px;">✓ In database: Yes</li>
                </ul>
                
                <p style="color: #aaa; font-size: 14px; margin-top: 15px;">
                    Source verification checks against our database of major news outlets
                    with known credibility ratings and bias assessments.
                </p>
            `;
        },
        
        getAuthorContent: function(authorName, sourceInfo) {
            if (authorName === 'Not Specified' || authorName === 'Unknown Author') {
                return `
                    <div style="background: rgba(255,100,100,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                        <h5 style="color: #ff4444; margin: 0 0 10px 0;">⚠️ No Author Information</h5>
                        <p style="color: #ddd; margin: 0;">
                            No author byline was detected in this article.
                        </p>
                    </div>
                    
                    <p style="color: #aaa; font-size: 14px; margin-top: 15px;">
                        Articles without clear authorship may be less reliable. Anonymous or unattributed 
                        content should be verified with additional sources.
                    </p>
                `;
            }
            
            return `
                <div style="background: rgba(255,255,0,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <h5 style="color: #ffff00; margin: 0 0 10px 0;">Author Detected</h5>
                    <div style="font-size: 20px; font-weight: bold; color: #ffff00;">
                        ${authorName}
                    </div>
                </div>
                
                <p style="color: #aaa; font-size: 14px; margin-top: 15px;">
                    Author name extracted from article byline. We do not currently track author history, 
                    credentials, or previous work. This is simply the name as it appears in the article.
                </p>
            `;
        },
        
        getStyleContent: function(styleData) {
            const quotes = styleData.quotes || 0;
            const stats = styleData.statistics || 0;
            const readingLevel = styleData.readingLevel || 'N/A';
            const quality = quotes >= 2 && stats >= 2 ? 'High' : quotes >= 1 || stats >= 1 ? 'Medium' : 'Low';
            
            return `
                <div style="background: rgba(255,136,0,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <h5 style="color: #ff8800; margin: 0 0 10px 0;">Writing Quality Analysis</h5>
                    <div style="font-size: 24px; font-weight: bold; color: #ff8800;">
                        ${quality} Quality
                    </div>
                </div>
                
                <h5 style="color: #ff8800; margin: 20px 0 10px 0;">Content Metrics:</h5>
                <ul style="list-style: none; padding: 0; margin: 0;">
                    <li style="margin-bottom: 8px;">💬 Direct quotes found: ${quotes}</li>
                    <li style="margin-bottom: 8px;">📊 Statistical claims: ${stats}</li>
                    <li style="margin-bottom: 8px;">📚 Reading level: Grade ${readingLevel}</li>
                    <li style="margin-bottom: 8px;">✍️ Style: ${styleData.balanced ? 'Balanced' : 'Needs improvement'}</li>
                </ul>
                
                <p style="color: #aaa; font-size: 14px; margin-top: 15px;">
                    Quality journalism typically includes multiple direct quotes and statistical 
                    evidence to support claims. Higher quality scores indicate better sourcing.
                </p>
            `;
        },
        
        getFactCheckContent: function(claims) {
            if (!claims || claims.length === 0) {
                return `
                    <div style="background: rgba(150,150,150,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                        <h5 style="color: #999; margin: 0 0 10px 0;">No Claims Extracted</h5>
                        <p style="color: #ddd; margin: 0;">
                            No specific claims were identified for fact-checking in this article.
                        </p>
                    </div>
                    
                    <p style="color: #aaa; font-size: 14px; margin-top: 15px;">
                        Advanced fact-checking requires Pro subscription with AI integration. 
                        The system extracts and verifies specific factual claims when available.
                    </p>
                `;
            }
            
            return `
                <div style="background: rgba(255,0,136,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <h5 style="color: #ff0088; margin: 0 0 10px 0;">Claims Identified</h5>
                    <div style="font-size: 20px; font-weight: bold; color: #ff0088;">
                        ${claims.length} Claims Found
                    </div>
                </div>
                
                <h5 style="color: #ff0088; margin: 20px 0 10px 0;">Claims for Verification:</h5>
                ${claims.slice(0, 3).map((claim, index) => `
                    <div style="
                        background: rgba(255,255,255,0.05);
                        padding: 12px;
                        border-radius: 8px;
                        margin-bottom: 10px;
                        border-left: 3px solid ${claim.confidence >= 80 ? '#00ff88' : claim.confidence >= 60 ? '#ffff00' : '#ff4444'};
                    ">
                        <p style="color: #ddd; margin: 0 0 5px 0; font-size: 14px;">
                            ${index + 1}. "${claim.claim.substring(0, 100)}${claim.claim.length > 100 ? '...' : ''}"
                        </p>
                        <p style="color: #aaa; margin: 0; font-size: 12px;">
                            Status: ${claim.status} | Confidence: ${claim.confidence}%
                        </p>
                    </div>
                `).join('')}
                
                <p style="color: #aaa; font-size: 14px; margin-top: 15px;">
                    AI-powered fact checking extracts and identifies claims for verification.
                    Full verification requires cross-referencing with fact-checking databases.
                </p>
            `;
        },
        
        getCrossRefContent: function(crossRefs) {
            if (!crossRefs || crossRefs.length === 0) {
                return `
                    <div style="background: rgba(150,150,150,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                        <h5 style="color: #999; margin: 0 0 10px 0;">No Cross-References Available</h5>
                        <p style="color: #ddd; margin: 0;">
                            No related coverage found in our reference database.
                        </p>
                    </div>
                    
                    <p style="color: #aaa; font-size: 14px; margin-top: 15px;">
                        Cross-reference data requires Pro subscription. When available, we show 
                        related coverage from other verified news sources.
                    </p>
                `;
            }
            
            return `
                <div style="background: rgba(136,0,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <h5 style="color: #8800ff; margin: 0 0 10px 0;">Related Coverage Found</h5>
                    <div style="font-size: 20px; font-weight: bold; color: #8800ff;">
                        ${crossRefs.length} References
                    </div>
                </div>
                
                <h5 style="color: #8800ff; margin: 20px 0 10px 0;">Related Articles:</h5>
                ${crossRefs.map(ref => `
                    <div style="
                        background: rgba(255,255,255,0.05);
                        padding: 12px;
                        border-radius: 8px;
                        margin-bottom: 10px;
                    ">
                        <p style="color: #ddd; margin: 0 0 5px 0; font-weight: 500;">
                            ${ref.source}: ${ref.title}
                        </p>
                        <p style="color: #aaa; margin: 0; font-size: 12px;">
                            Relevance: ${ref.relevance}%
                        </p>
                    </div>
                `).join('')}
            `;
        },
        
        getTemporalContent: function(temporalData, contentStats) {
            const datesFound = temporalData.dates_found || [];
            const wordCount = contentStats.word_count || 0;
            const sentenceCount = contentStats.sentence_count || 0;
            
            return `
                <div style="background: rgba(0,255,204,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <h5 style="color: #00ffcc; margin: 0 0 10px 0;">Temporal & Content Analysis</h5>
                    <div style="font-size: 20px; font-weight: bold; color: #00ffcc;">
                        ${datesFound.length > 0 ? 'Dated Content' : 'No Dates Found'}
                    </div>
                </div>
                
                <h5 style="color: #00ffcc; margin: 20px 0 10px 0;">Content Statistics:</h5>
                <ul style="list-style: none; padding: 0; margin: 0;">
                    <li style="margin-bottom: 8px;">📅 Dates found: ${datesFound.length}</li>
                    ${datesFound.length > 0 ? `<li style="margin-bottom: 8px;">📅 Dates: ${datesFound.slice(0, 3).join(', ')}</li>` : ''}
                    <li style="margin-bottom: 8px;">📝 Word count: ${wordCount}</li>
                    <li style="margin-bottom: 8px;">📄 Sentences: ${sentenceCount}</li>
                    <li style="margin-bottom: 8px;">📊 Avg sentence length: ${sentenceCount > 0 ? Math.round(wordCount / sentenceCount) : 0} words</li>
                </ul>
                
                <p style="color: #aaa; font-size: 14px; margin-top: 15px;">
                    Temporal analysis identifies dates and time references in the content. 
                    This helps assess the timeliness and relevance of the information.
                </p>
            `;
        },
        
        // Toggle card expansion
        toggleCard: function(cardId) {
            const content = document.getElementById(cardId + '-content');
            const arrow = document.getElementById(cardId + '-arrow');
            
            if (content && arrow) {
                if (content.style.maxHeight && content.style.maxHeight !== '0px') {
                    content.style.maxHeight = '0';
                    arrow.style.transform = 'rotate(0deg)';
                } else {
                    content.style.maxHeight = content.scrollHeight + 'px';
                    arrow.style.transform = 'rotate(180deg)';
                }
            }
        },
        
        // Generate PDF report
        generatePDF: function() {
            const currentData = NewsApp.analysis.getCurrentData();
            if (!currentData) {
                alert('No analysis data available to generate report');
                return;
            }
            
            // Get the article URL or text that was analyzed
            const articleUrl = document.getElementById('articleUrl')?.value || 
                             document.getElementById('news-text')?.value || 
                             document.getElementById('fullArticle')?.value || 
                             'No content';
            
            // Make API call to generate PDF
            fetch('/api/generate-pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    url: articleUrl,
                    analysisData: currentData 
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('PDF generation failed');
                }
                return response.blob();
            })
            .then(blob => {
                // Create download link
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `news-analysis-report-${new Date().toISOString().split('T')[0]}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                // Show success notification
                this.showNotification('PDF report downloaded successfully!', 'success');
            })
            .catch(error => {
                console.error('Error generating PDF:', error);
                alert('Failed to generate PDF report. Please try again.');
            });
        },
        
        // Share results
        shareResults: function() {
            const currentData = NewsApp.analysis.getCurrentData();
            if (!currentData) {
                alert('No analysis data to share');
                return;
            }
            
            const articleUrl = document.getElementById('articleUrl')?.value || window.location.href;
            const results = currentData.results || {};
            const shareText = `News Analysis Results:\n` +
                            `Trust Score: ${results.credibility || 0}%\n` +
                            `Bias: ${results.bias?.label || 'Unknown'}\n` +
                            `Check it out: ${articleUrl}`;
            
            if (navigator.share) {
                navigator.share({
                    title: 'News Analysis Report',
                    text: shareText,
                    url: window.location.href
                }).catch(err => console.log('Error sharing:', err));
            } else {
                // Fallback - copy to clipboard
                navigator.clipboard.writeText(shareText).then(() => {
                    this.showNotification('Analysis results copied to clipboard!', 'success');
                }).catch(err => {
                    console.error('Failed to copy:', err);
                    alert('Failed to copy to clipboard');
                });
            }
        },
        
        // Show notification
        showNotification: function(message, type = 'info') {
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 25px;
                border-radius: 8px;
                z-index: 10000;
                max-width: 400px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                animation: slideIn 0.3s ease;
                background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#667eea'};
                color: white;
            `;
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 3000);
        },
        
        // Show error
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
    window.NewsApp.results = NewsApp.results;
    
})();
