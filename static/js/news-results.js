// news-results.js - Fixed Results Display with Conversational Format
(function() {
    'use strict';
    
    // Create namespace
    window.NewsApp = window.NewsApp || {};
    
    NewsApp.results = {
        // Display the complete analysis results with conversational format
        displayResults: function(data) {
            console.log('Displaying results:', data);
            
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
            
            // Extract data from backend
            const trustScore = results.credibility || 0;
            const biasData = results.bias || {};
            const sourceInfo = results.sources || {};
            const authorName = results.author || 'Not Specified';
            const styleData = results.style || {};
            const originalContent = data.original_content || '';
            
            // Determine trust level and color
            const trustLevel = trustScore >= 80 ? 'High' : trustScore >= 60 ? 'Moderate' : 'Low';
            const trustColor = trustScore >= 80 ? '#00ff88' : trustScore >= 60 ? '#ffff00' : '#ff4444';
            
            // Get article summary (first 150 chars of content)
            const articleSummary = originalContent.length > 150 ? 
                originalContent.substring(0, 150) + '...' : 
                originalContent || 'No content summary available';
            
            // Build conversational UI
            resultsDiv.innerHTML = `
                <div class="analysis-results" style="
                    background: linear-gradient(135deg, rgba(10,14,39,0.95), rgba(0,0,0,0.95));
                    border: 2px solid rgba(0,255,255,0.3);
                    border-radius: 20px;
                    padding: 40px;
                    margin: 20px 0;
                    color: #fff;
                    box-shadow: 0 0 40px rgba(0,255,255,0.3);
                ">
                    <!-- Header with Trust Score -->
                    <div style="text-align: center; margin-bottom: 40px;">
                        <h2 style="
                            font-size: 2.5em;
                            background: linear-gradient(45deg, #00ffff, #ff00ff);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                            margin-bottom: 20px;
                        ">Analysis Complete</h2>
                        
                        <!-- Trust Score Display -->
                        <div style="
                            display: inline-block;
                            background: rgba(255,255,255,0.05);
                            border: 2px solid ${trustColor};
                            border-radius: 100px;
                            padding: 20px 40px;
                            margin-bottom: 30px;
                        ">
                            <div style="font-size: 48px; font-weight: bold; color: ${trustColor};">
                                ${trustScore}%
                            </div>
                            <div style="font-size: 20px; color: #aaa; margin-top: 5px;">
                                ${trustLevel} Trust Score
                            </div>
                        </div>
                    </div>
                    
                    <!-- Main Conversational Section -->
                    <div style="
                        background: rgba(255,255,255,0.03);
                        border-radius: 15px;
                        padding: 30px;
                        margin-bottom: 30px;
                    ">
                        <!-- 1. Source & Author -->
                        <div style="margin-bottom: 30px;">
                            <h3 style="color: #00ffff; font-size: 1.5em; margin-bottom: 15px;">
                                📰 Source & Author
                            </h3>
                            <div style="font-size: 18px; line-height: 1.8; color: #ddd;">
                                ${this.getSourceDescription(sourceInfo, authorName)}
                            </div>
                        </div>
                        
                        <!-- 2. What is this article about? -->
                        <div style="margin-bottom: 30px;">
                            <h3 style="color: #ff00ff; font-size: 1.5em; margin-bottom: 15px;">
                                📋 What is this article about?
                            </h3>
                            <div style="
                                background: rgba(255,0,255,0.1);
                                padding: 20px;
                                border-radius: 10px;
                                font-size: 16px;
                                line-height: 1.6;
                                color: #ddd;
                            ">
                                ${articleSummary}
                            </div>
                        </div>
                        
                        <!-- 3. What did we find? -->
                        <div style="margin-bottom: 30px;">
                            <h3 style="color: #00ff88; font-size: 1.5em; margin-bottom: 15px;">
                                🔍 What did we find?
                            </h3>
                            <div style="font-size: 16px; line-height: 1.8; color: #ddd;">
                                ${this.getConversationalFindings(trustScore, biasData, styleData)}
                            </div>
                        </div>
                    </div>
                    
                    <!-- Expandable Educational Cards -->
                    <div style="margin-bottom: 30px;">
                        <h3 style="color: #00ffff; text-align: center; margin-bottom: 30px; font-size: 1.8em;">
                            📚 Understanding Our Analysis - Click to Learn More
                        </h3>
                        
                        <div style="
                            display: grid;
                            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                            gap: 20px;
                        ">
                            ${this.createEducationalCard(
                                '🎯',
                                'How We Calculate Trust Score',
                                this.getTrustEducation(trustScore, sourceInfo, styleData),
                                '#00ffff',
                                'trust-edu'
                            )}
                            
                            ${this.createEducationalCard(
                                '⚖️',
                                'How We Detect Bias',
                                this.getBiasEducation(biasData),
                                '#ff00ff',
                                'bias-edu'
                            )}
                            
                            ${this.createEducationalCard(
                                '✍️',
                                'What Makes Quality Journalism',
                                this.getQualityEducation(styleData),
                                '#00ff88',
                                'quality-edu'
                            )}
                            
                            ${this.createEducationalCard(
                                '⚠️',
                                'Our Limitations',
                                this.getLimitationsEducation(),
                                '#ff8800',
                                'limits-edu'
                            )}
                        </div>
                    </div>
                    
                    <!-- Action Buttons -->
                    <div style="
                        display: flex;
                        gap: 15px;
                        justify-content: center;
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
                        ">
                            📄 Download Report
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
                        ">
                            📤 Share Analysis
                        </button>
                        
                        <button onclick="NewsApp.results.resetAnalysis()" style="
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
                        ">
                            🔄 New Analysis
                        </button>
                    </div>
                </div>
            `;
            
            // Show results section
            resultsDiv.style.display = 'block';
            
            // Scroll to results
            resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
        },
        
        // Get conversational source description
        getSourceDescription: function(sourceInfo, authorName) {
            let description = '';
            
            // Handle source
            if (sourceInfo.domain && sourceInfo.domain !== 'Direct Input' && sourceInfo.domain !== 'Unknown Source') {
                description += `This article comes from <strong style="color: #00ffff;">${sourceInfo.name || sourceInfo.domain}</strong>`;
                
                if (sourceInfo.credibility) {
                    description += `, a ${sourceInfo.bias || 'politically neutral'} news source with a ${sourceInfo.credibility}% credibility rating in our database`;
                }
            } else {
                description += `This content was <strong style="color: #ff8800;">directly pasted</strong> or comes from an <strong style="color: #ff8800;">unverified source</strong>`;
            }
            
            // Handle author
            if (authorName && authorName !== 'Not Specified' && authorName !== 'Unknown Author') {
                description += `. It was written by <strong style="color: #00ffff;">${authorName}</strong>`;
            } else {
                description += `. <strong style="color: #ff8800;">No author</strong> was identified, which may affect credibility`;
            }
            
            description += '.';
            
            return description;
        },
        
        // Get conversational findings
        getConversationalFindings: function(trustScore, biasData, styleData) {
            let findings = '';
            
            // Trust finding
            if (trustScore >= 80) {
                findings += `✅ <strong style="color: #00ff88;">Good news!</strong> This article scores high on our trust metrics. `;
            } else if (trustScore >= 60) {
                findings += `⚠️ <strong style="color: #ffff00;">Mixed signals:</strong> This article has moderate credibility. `;
            } else {
                findings += `❌ <strong style="color: #ff4444;">Be cautious:</strong> This article scores low on our trust metrics. `;
            }
            
            // Bias finding
            const biasLabel = biasData.label || 'unknown';
            if (biasLabel === 'center' || biasLabel === 'unknown') {
                findings += `The content appears <strong>politically balanced</strong> `;
            } else {
                findings += `We detected a <strong style="color: #ff00ff;">${biasLabel}</strong> political lean `;
            }
            
            findings += `with ${biasData.objectivity || 0}% objectivity. `;
            
            // Quality finding
            const quotes = styleData.quotes || 0;
            const stats = styleData.statistics || 0;
            
            if (quotes >= 2 && stats >= 2) {
                findings += `<br><br>📊 <strong style="color: #00ff88;">Strong journalism indicators:</strong> The article includes ${quotes} direct quotes and ${stats} statistical references, suggesting thorough reporting.`;
            } else if (quotes > 0 || stats > 0) {
                findings += `<br><br>📊 <strong style="color: #ffff00;">Some evidence present:</strong> We found ${quotes} quotes and ${stats} statistics. More sources would strengthen credibility.`;
            } else {
                findings += `<br><br>📊 <strong style="color: #ff8800;">Limited evidence:</strong> The article lacks direct quotes or statistics, which are hallmarks of quality journalism.`;
            }
            
            // Emotional language
            if (biasData.emotional_indicators > 3) {
                findings += `<br><br>⚡ <strong style="color: #ff8800;">Note:</strong> We detected ${biasData.emotional_indicators} emotionally charged words, which may indicate sensationalized reporting.`;
            }
            
            return findings;
        },
        
        // Create educational card
        createEducationalCard: function(icon, title, content, color, id) {
            return `
                <div class="edu-card" style="
                    background: rgba(255,255,255,0.05);
                    border: 1px solid ${color}33;
                    border-radius: 15px;
                    padding: 20px;
                    cursor: pointer;
                    transition: all 0.3s;
                " 
                onclick="NewsApp.results.toggleCard('${id}')"
                onmouseover="this.style.borderColor='${color}66'; this.style.background='rgba(255,255,255,0.08)'"
                onmouseout="this.style.borderColor='${color}33'; this.style.background='rgba(255,255,255,0.05)'">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center;">
                            <span style="font-size: 28px; margin-right: 12px;">${icon}</span>
                            <h4 style="color: ${color}; margin: 0; font-size: 18px;">${title}</h4>
                        </div>
                        <span id="${id}-arrow" style="color: ${color}; transition: transform 0.3s;">▼</span>
                    </div>
                    <div id="${id}-content" style="
                        max-height: 0;
                        overflow: hidden;
                        transition: max-height 0.3s ease-out;
                    ">
                        <div style="padding-top: 20px; color: #ddd; line-height: 1.6;">
                            ${content}
                        </div>
                    </div>
                </div>
            `;
        },
        
        // Educational content generators
        getTrustEducation: function(score, sourceInfo, styleData) {
            return `
                <h5 style="color: #00ffff; margin: 0 0 15px 0;">Your article scored ${score}% - here's why:</h5>
                
                <div style="background: rgba(0,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <strong>How we calculate trust scores:</strong>
                    <ul style="margin: 10px 0 0 20px;">
                        <li>Base score from source reputation (${sourceInfo.credibility || 50}%)</li>
                        <li>+5% if author is clearly identified</li>
                        <li>+5% if publication date is present</li>
                        <li>+10% if article includes direct quotes</li>
                        <li>+5% if statistics are properly cited</li>
                        <li>-5% for excessive emotional language</li>
                    </ul>
                </div>
                
                <p><strong>What this means:</strong> ${
                    score >= 80 ? 
                    "This is a highly credible article from a reputable source with good journalistic practices." :
                    score >= 60 ?
                    "This article has decent credibility but may lack some important journalistic elements." :
                    "This article has low credibility - verify information with additional sources."
                }</p>
                
                <p style="color: #aaa; font-size: 14px; margin-top: 15px;">
                    <strong>Remember:</strong> Even high-scoring articles can contain errors. Always think critically about what you read.
                </p>
            `;
        },
        
        getBiasEducation: function(biasData) {
            return `
                <h5 style="color: #ff00ff; margin: 0 0 15px 0;">We detected: ${biasData.label || 'Unknown bias'}</h5>
                
                <div style="background: rgba(255,0,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <strong>Our bias detection method:</strong>
                    <ul style="margin: 10px 0 0 20px;">
                        <li>We scan for politically-charged keywords</li>
                        <li>Left indicators found: ${biasData.left_indicators || 0}</li>
                        <li>Right indicators found: ${biasData.right_indicators || 0}</li>
                        <li>Emotional words detected: ${biasData.emotional_indicators || 0}</li>
                        <li>Objectivity score: ${biasData.objectivity || 0}%</li>
                    </ul>
                </div>
                
                <p><strong>Important limitations:</strong></p>
                <ul style="margin: 10px 0 0 20px;">
                    <li>Keyword detection can miss context and nuance</li>
                    <li>Some topics naturally use "biased" words</li>
                    <li>We can't detect subtle framing or omission bias</li>
                    <li>Opinion pieces will always show bias (that's okay!)</li>
                </ul>
                
                <p style="color: #aaa; font-size: 14px; margin-top: 15px;">
                    <strong>Pro tip:</strong> Read sources from across the political spectrum to get a complete picture.
                </p>
            `;
        },
        
        getQualityEducation: function(styleData) {
            const quotes = styleData.quotes || 0;
            const stats = styleData.statistics || 0;
            const readingLevel = styleData.readingLevel || 'N/A';
            
            return `
                <h5 style="color: #00ff88; margin: 0 0 15px 0;">Quality Journalism Checklist:</h5>
                
                <div style="background: rgba(0,255,136,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <strong>This article has:</strong>
                    <ul style="margin: 10px 0 0 20px;">
                        <li>${quotes >= 2 ? '✅' : '❌'} Multiple sources quoted (${quotes} found)</li>
                        <li>${stats >= 2 ? '✅' : '❌'} Statistical evidence (${stats} found)</li>
                        <li>${readingLevel >= 10 ? '✅' : '⚠️'} Appropriate complexity (Grade ${readingLevel})</li>
                        <li>${styleData.balanced ? '✅' : '❌'} Balanced presentation</li>
                    </ul>
                </div>
                
                <p><strong>Why this matters:</strong></p>
                <ul style="margin: 10px 0 0 20px;">
                    <li><strong>Quotes</strong> show the journalist talked to real sources</li>
                    <li><strong>Statistics</strong> provide concrete evidence for claims</li>
                    <li><strong>Complexity</strong> indicates depth of coverage</li>
                    <li><strong>Balance</strong> suggests multiple perspectives considered</li>
                </ul>
                
                <p style="color: #aaa; font-size: 14px; margin-top: 15px;">
                    <strong>Remember:</strong> Even well-written articles can be wrong. Quality indicators suggest good process, not guaranteed truth.
                </p>
            `;
        },
        
        getLimitationsEducation: function() {
            return `
                <h5 style="color: #ff8800; margin: 0 0 15px 0;">What our analysis CAN and CAN'T do:</h5>
                
                <div style="background: rgba(255,136,0,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <strong>✅ What we CAN do:</strong>
                    <ul style="margin: 10px 0 0 20px;">
                        <li>Check if source is in our database of 14 major outlets</li>
                        <li>Detect obvious political keywords</li>
                        <li>Count quotes and statistics</li>
                        <li>Extract author names and dates</li>
                        <li>Assess basic writing quality</li>
                    </ul>
                </div>
                
                <div style="background: rgba(255,100,100,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <strong>❌ What we CAN'T do:</strong>
                    <ul style="margin: 10px 0 0 20px;">
                        <li>Verify if facts are actually true</li>
                        <li>Check quotes against original sources</li>
                        <li>Detect sophisticated propaganda</li>
                        <li>Understand context or sarcasm</li>
                        <li>Verify images or videos</li>
                        <li>Check author credentials</li>
                    </ul>
                </div>
                
                <p style="color: #ffaa00; font-weight: bold;">
                    ⚠️ This is a HELPER TOOL, not a truth detector. Always verify important information through multiple sources.
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
        
        // Reset analysis - FIXED
        resetAnalysis: function() {
            // Hide results
            const resultsDiv = document.getElementById('results');
            if (resultsDiv) {
                resultsDiv.style.display = 'none';
                resultsDiv.innerHTML = '';
            }
            
            // Clear all input fields
            const urlInput = document.getElementById('articleUrl');
            const textArea = document.getElementById('news-text');
            const fullArticle = document.getElementById('fullArticle');
            
            if (urlInput) urlInput.value = '';
            if (textArea) textArea.value = '';
            if (fullArticle) fullArticle.value = '';
            
            // Show input section
            const inputSection = document.querySelector('.input-section');
            if (inputSection) {
                inputSection.style.display = 'block';
            }
            
            // Reset tabs to URL tab
            const urlTab = document.querySelector('[onclick*="showUrlInput"]');
            const textTab = document.querySelector('[onclick*="showTextInput"]');
            if (urlTab && textTab) {
                urlTab.classList.add('active');
                textTab.classList.remove('active');
            }
            
            // Show URL input, hide text input
            const urlInputDiv = document.getElementById('url-input');
            const textInputDiv = document.getElementById('text-input');
            if (urlInputDiv) urlInputDiv.style.display = 'block';
            if (textInputDiv) textInputDiv.style.display = 'none';
            
            // Clear any stored data
            if (window.NewsApp && window.NewsApp.analysis) {
                window.NewsApp.analysis.currentData = null;
            }
            
            // Scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });
        },
        
        // Generate PDF report - FIXED
        generatePDF: function() {
            const currentData = window.NewsApp?.analysis?.currentData || window.NewsApp?.analysis?.getCurrentData?.();
            
            if (!currentData) {
                this.showNotification('No analysis data available to generate report', 'error');
                return;
            }
            
            // Show loading
            this.showNotification('Generating PDF report...', 'info');
            
            // Prepare data for PDF
            const pdfData = {
                results: currentData.results || {},
                original_content: currentData.original_content || '',
                analyzed_url: document.getElementById('articleUrl')?.value || '',
                analyzed_text: document.getElementById('news-text')?.value || document.getElementById('fullArticle')?.value || '',
                analysis_date: new Date().toISOString()
            };
            
            // Make API call to generate PDF
            fetch('/api/news/generate-pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(pdfData)
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
                a.download = `news-analysis-${new Date().toISOString().split('T')[0]}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showNotification('PDF report downloaded successfully!', 'success');
            })
            .catch(error => {
                console.error('Error generating PDF:', error);
                this.showNotification('Failed to generate PDF. Please try again.', 'error');
            });
        },
        
        // Share results - FIXED
        shareResults: function() {
            const currentData = window.NewsApp?.analysis?.currentData || window.NewsApp?.analysis?.getCurrentData?.();
            
            if (!currentData) {
                this.showNotification('No analysis data to share', 'error');
                return;
            }
            
            const results = currentData.results || {};
            const trustScore = results.credibility || 0;
            const bias = results.bias?.label || 'Unknown';
            const source = results.sources?.name || 'Unknown source';
            
            const shareText = `I analyzed an article from ${source} using Facts & Fakes AI:\n\n` +
                            `📊 Trust Score: ${trustScore}%\n` +
                            `⚖️ Political Bias: ${bias}\n` +
                            `✍️ Quality: ${results.style?.quotes || 0} quotes, ${results.style?.statistics || 0} statistics\n\n` +
                            `Try it yourself at: ${window.location.origin}`;
            
            if (navigator.share) {
                navigator.share({
                    title: 'News Analysis - Facts & Fakes AI',
                    text: shareText,
                    url: window.location.href
                }).catch(err => {
                    // Fallback to clipboard
                    this.copyToClipboard(shareText);
                });
            } else {
                // Fallback - copy to clipboard
                this.copyToClipboard(shareText);
            }
        },
        
        // Copy to clipboard helper
        copyToClipboard: function(text) {
            navigator.clipboard.writeText(text).then(() => {
                this.showNotification('Analysis results copied to clipboard!', 'success');
            }).catch(err => {
                console.error('Failed to copy:', err);
                // Final fallback
                const textArea = document.createElement('textarea');
                textArea.value = text;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                document.body.appendChild(textArea);
                textArea.select();
                try {
                    document.execCommand('copy');
                    this.showNotification('Analysis results copied to clipboard!', 'success');
                } catch (err) {
                    this.showNotification('Failed to copy to clipboard', 'error');
                }
                document.body.removeChild(textArea);
            });
        },
        
        // Show notification - IMPROVED
        showNotification: function(message, type = 'info') {
            // Remove any existing notifications
            const existing = document.querySelector('.notification');
            if (existing) existing.remove();
            
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
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                animation: slideIn 0.3s ease;
                background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
                color: white;
                font-weight: 500;
            `;
            notification.textContent = message;
            
            // Add animation
            const style = document.createElement('style');
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.style.animation = 'slideOut 0.3s ease';
                notification.style.animationFillMode = 'forwards';
                setTimeout(() => notification.remove(), 300);
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
                    <button onclick="NewsApp.results.resetAnalysis()" style="
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
    
    // Make resetAnalysis available globally for the button
    window.NewsApp.ui = window.NewsApp.ui || {};
    window.NewsApp.ui.resetAnalysis = NewsApp.results.resetAnalysis;
    
    // Make available globally
    window.NewsApp.results = NewsApp.results;
    
})();
