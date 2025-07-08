// news-results.js - Complete Results Display Module
(function() {
    'use strict';
    
    // Create namespace
    window.NewsApp = window.NewsApp || {};
    
    NewsApp.results = {
        // Display the complete analysis results
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
            
            // Clear any existing results
            resultsDiv.innerHTML = '';
            
            // Create tabs container
            const tabsContainer = document.createElement('div');
            tabsContainer.className = 'tabs-container';
            
            // Create tab buttons
            const tabButtons = this.createTabButtons();
            tabsContainer.appendChild(tabButtons);
            
            // Create tab content
            const tabContent = document.createElement('div');
            tabContent.className = 'tab-content';
            
            // Add all tab panels
            tabContent.appendChild(this.createOverviewTab(results));
            tabContent.appendChild(this.createCredibilityTab(results));
            tabContent.appendChild(this.createBiasTab(results));
            tabContent.appendChild(this.createAuthorTab(results));
            tabContent.appendChild(this.createSourcesTab(results));
            
            tabsContainer.appendChild(tabContent);
            resultsDiv.appendChild(tabsContainer);
            
            // Add action buttons
            resultsDiv.appendChild(this.createActionButtons());
            
            // Show results section
            resultsDiv.style.display = 'block';
            
            // Activate first tab
            this.activateTab('overview');
            
            // Scroll to results
            resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
        },
        
        createTabButtons: function() {
            const tabButtonsDiv = document.createElement('div');
            tabButtonsDiv.className = 'tab-buttons';
            
            const tabs = [
                { id: 'overview', label: 'Overview', icon: '📊' },
                { id: 'credibility', label: 'Credibility', icon: '✓' },
                { id: 'bias', label: 'Bias Analysis', icon: '⚖️' },
                { id: 'author', label: 'Author', icon: '👤' },
                { id: 'sources', label: 'Sources', icon: '🔗' }
            ];
            
            tabs.forEach((tab, index) => {
                const button = document.createElement('button');
                button.className = 'tab-button' + (index === 0 ? ' active' : '');
                button.setAttribute('data-tab', tab.id);
                button.innerHTML = `<span class="tab-icon">${tab.icon}</span> ${tab.label}`;
                button.onclick = () => this.activateTab(tab.id);
                tabButtonsDiv.appendChild(button);
            });
            
            return tabButtonsDiv;
        },
        
        createOverviewTab: function(results) {
            const panel = document.createElement('div');
            panel.className = 'tab-panel active';
            panel.id = 'overview-panel';
            
            // Calculate overall assessment
            const credScore = results.credibility?.score || 0;
            const overallAssessment = this.getOverallAssessment(credScore);
            
            panel.innerHTML = `
                <div class="overview-content">
                    <div class="assessment-header ${overallAssessment.class}">
                        <div class="assessment-icon">${overallAssessment.icon}</div>
                        <div class="assessment-text">
                            <h3>${overallAssessment.title}</h3>
                            <p>${overallAssessment.description}</p>
                        </div>
                    </div>
                    
                    <div class="quick-stats">
                        <div class="stat-card">
                            <div class="stat-value">${credScore}%</div>
                            <div class="stat-label">Credibility Score</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${results.bias?.direction || 'Unknown'}</div>
                            <div class="stat-label">Bias Direction</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${results.sources?.primary_count || 0}</div>
                            <div class="stat-label">Primary Sources</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${results.style?.tone || 'Unknown'}</div>
                            <div class="stat-label">Article Tone</div>
                        </div>
                    </div>
                    
                    <div class="key-findings">
                        <h4>Key Findings</h4>
                        <ul>
                            ${this.generateKeyFindings(results).map(finding => 
                                `<li>${finding}</li>`
                            ).join('')}
                        </ul>
                    </div>
                </div>
            `;
            
            return panel;
        },
        
        createCredibilityTab: function(results) {
            const panel = document.createElement('div');
            panel.className = 'tab-panel';
            panel.id = 'credibility-panel';
            
            const credibility = results.credibility || {};
            const score = credibility.score || 0;
            
            panel.innerHTML = `
                <div class="credibility-content">
                    <div class="credibility-circle-container">
                        <div class="credibility-circle" style="--score: ${score}">
                            <svg viewBox="0 0 200 200">
                                <circle cx="100" cy="100" r="90" class="circle-bg"/>
                                <circle cx="100" cy="100" r="90" class="circle-progress"
                                        style="stroke-dasharray: ${565.48 * score / 100} 565.48"/>
                            </svg>
                            <div class="credibility-score">
                                <div class="score-number">${score}</div>
                                <div class="score-label">Credibility</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="credibility-details">
                        <h3>Source: ${credibility.source_name || 'Unknown'}</h3>
                        <div class="credibility-factors">
                            ${this.generateCredibilityFactors(credibility).map(factor => `
                                <div class="factor-item">
                                    <span class="factor-icon">${factor.met ? '✓' : '✗'}</span>
                                    <span class="factor-text">${factor.text}</span>
                                </div>
                            `).join('')}
                        </div>
                        
                        <div class="credibility-explanation">
                            <p>${credibility.explanation || this.getCredibilityExplanation(score)}</p>
                        </div>
                    </div>
                </div>
            `;
            
            return panel;
        },
        
        createBiasTab: function(results) {
            const panel = document.createElement('div');
            panel.className = 'tab-panel';
            panel.id = 'bias-panel';
            
            const bias = results.bias || {};
            const biasScore = this.calculateBiasScore(bias.direction);
            
            panel.innerHTML = `
                <div class="bias-content">
                    <div class="bias-compass">
                        <div class="compass-container">
                            <div class="compass-dial" style="--rotation: ${biasScore.rotation}deg">
                                <div class="compass-needle"></div>
                            </div>
                            <div class="compass-labels">
                                <span class="label-left">Far Left</span>
                                <span class="label-center">Center</span>
                                <span class="label-right">Far Right</span>
                            </div>
                        </div>
                        <div class="bias-label">${bias.direction || 'Unknown'}</div>
                    </div>
                    
                    <div class="bias-analysis">
                        <h3>Bias Indicators</h3>
                        <div class="bias-indicators">
                            ${this.generateBiasIndicators(bias).map(indicator => `
                                <div class="indicator-item">
                                    <div class="indicator-label">${indicator.label}</div>
                                    <div class="indicator-bar">
                                        <div class="indicator-fill" style="width: ${indicator.value}%"></div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        
                        <div class="bias-examples">
                            <h4>Examples from Article</h4>
                            <ul>
                                ${(bias.examples || ['No specific examples detected']).map(example => 
                                    `<li>${example}</li>`
                                ).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            `;
            
            return panel;
        },
        
        createAuthorTab: function(results) {
            const panel = document.createElement('div');
            panel.className = 'tab-panel';
            panel.id = 'author-panel';
            
            const author = results.author || {};
            
            panel.innerHTML = `
                <div class="author-content">
                    <div class="author-card">
                        <div class="author-avatar">
                            <div class="avatar-placeholder">${this.getInitials(author.name)}</div>
                        </div>
                        <div class="author-info">
                            <h3>${author.name || 'Unknown Author'}</h3>
                            <p class="author-role">${author.role || 'Journalist'}</p>
                            ${author.organization ? `<p class="author-org">${author.organization}</p>` : ''}
                        </div>
                    </div>
                    
                    <div class="author-stats">
                        <div class="stat-box">
                            <div class="stat-number">${author.article_count || 'N/A'}</div>
                            <div class="stat-desc">Articles Written</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-number">${author.years_experience || 'N/A'}</div>
                            <div class="stat-desc">Years Experience</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-number">${author.expertise_areas?.length || 0}</div>
                            <div class="stat-desc">Expertise Areas</div>
                        </div>
                    </div>
                    
                    ${author.bio ? `
                        <div class="author-bio">
                            <h4>About the Author</h4>
                            <p>${author.bio}</p>
                        </div>
                    ` : ''}
                    
                    ${author.expertise_areas && author.expertise_areas.length > 0 ? `
                        <div class="author-expertise">
                            <h4>Areas of Expertise</h4>
                            <div class="expertise-tags">
                                ${author.expertise_areas.map(area => 
                                    `<span class="tag">${area}</span>`
                                ).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            `;
            
            return panel;
        },
        
        createSourcesTab: function(results) {
            const panel = document.createElement('div');
            panel.className = 'tab-panel';
            panel.id = 'sources-panel';
            
            const sources = results.sources || {};
            
            panel.innerHTML = `
                <div class="sources-content">
                    <div class="sources-overview">
                        <div class="source-metric">
                            <div class="metric-value">${sources.primary_count || 0}</div>
                            <div class="metric-label">Primary Sources</div>
                        </div>
                        <div class="source-metric">
                            <div class="metric-value">${sources.secondary_count || 0}</div>
                            <div class="metric-label">Secondary Sources</div>
                        </div>
                        <div class="source-metric">
                            <div class="metric-value">${sources.expert_count || 0}</div>
                            <div class="metric-label">Expert Sources</div>
                        </div>
                    </div>
                    
                    <div class="source-quality">
                        <h3>Source Quality Assessment</h3>
                        <div class="quality-meter">
                            <div class="meter-fill" style="width: ${sources.quality_score || 0}%"></div>
                        </div>
                        <p class="quality-text">${this.getSourceQualityText(sources.quality_score)}</p>
                    </div>
                    
                    ${sources.list && sources.list.length > 0 ? `
                        <div class="sources-list">
                            <h3>Referenced Sources</h3>
                            <ul>
                                ${sources.list.map(source => `
                                    <li class="source-item">
                                        <span class="source-type">${source.type}</span>
                                        <span class="source-name">${source.name}</span>
                                        ${source.credibility ? 
                                            `<span class="source-cred">${source.credibility}% credible</span>` : 
                                            ''}
                                    </li>
                                `).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    
                    <div class="cross-verification">
                        <h3>Cross-Source Verification</h3>
                        <div class="verification-status ${sources.verified ? 'verified' : 'unverified'}">
                            <span class="status-icon">${sources.verified ? '✓' : '⚠'}</span>
                            <span class="status-text">
                                ${sources.verified ? 
                                    'Claims verified across multiple sources' : 
                                    'Limited cross-source verification available'}
                            </span>
                        </div>
                    </div>
                </div>
            `;
            
            return panel;
        },
        
        createActionButtons: function() {
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'results-actions';
            
            actionsDiv.innerHTML = `
                <button class="action-button primary" onclick="NewsApp.results.generatePDF()">
                    <span class="button-icon">📄</span> Download Report
                </button>
                <button class="action-button secondary" onclick="NewsApp.results.shareResults()">
                    <span class="button-icon">📤</span> Share Analysis
                </button>
                <button class="action-button tertiary" onclick="NewsApp.ui.resetAnalysis()">
                    <span class="button-icon">🔄</span> Analyze Another Article
                </button>
            `;
            
            return actionsDiv;
        },
        
        // Helper functions
        activateTab: function(tabId) {
            // Update button states
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.toggle('active', btn.getAttribute('data-tab') === tabId);
            });
            
            // Update panel visibility
            document.querySelectorAll('.tab-panel').forEach(panel => {
                panel.classList.toggle('active', panel.id === `${tabId}-panel`);
            });
        },
        
        getOverallAssessment: function(credScore) {
            if (credScore >= 80) {
                return {
                    class: 'highly-credible',
                    icon: '✓',
                    title: 'Highly Credible Source',
                    description: 'This article comes from a trusted source with strong journalistic standards.'
                };
            } else if (credScore >= 60) {
                return {
                    class: 'moderately-credible',
                    icon: '!',
                    title: 'Moderately Credible',
                    description: 'This source generally provides reliable information but may have some limitations.'
                };
            } else if (credScore >= 40) {
                return {
                    class: 'questionable',
                    icon: '?',
                    title: 'Questionable Credibility',
                    description: 'This source has mixed reliability. Verify claims with additional sources.'
                };
            } else {
                return {
                    class: 'low-credibility',
                    icon: '✗',
                    title: 'Low Credibility',
                    description: 'This source has significant credibility issues. Exercise caution with this information.'
                };
            }
        },
        
        generateKeyFindings: function(results) {
            const findings = [];
            
            if (results.credibility?.source_name) {
                findings.push(`Source identified as ${results.credibility.source_name}`);
            }
            
            if (results.bias?.direction && results.bias.direction !== 'Unknown') {
                findings.push(`${results.bias.direction} bias detected in content`);
            }
            
            if (results.sources?.primary_count > 0) {
                findings.push(`${results.sources.primary_count} primary sources cited`);
            }
            
            if (results.style?.emotional_language) {
                findings.push('Uses emotional language to convey message');
            }
            
            if (results.sources?.verified) {
                findings.push('Claims cross-verified with multiple sources');
            }
            
            return findings.length > 0 ? findings : ['Analysis complete - see detailed tabs for more information'];
        },
        
        generateCredibilityFactors: function(credibility) {
            return [
                { met: credibility.has_editorial_standards, text: 'Editorial Standards' },
                { met: credibility.fact_checking, text: 'Fact-Checking Process' },
                { met: credibility.corrections_policy, text: 'Corrections Policy' },
                { met: credibility.author_transparency, text: 'Author Transparency' },
                { met: credibility.source_citations, text: 'Source Citations' },
                { met: credibility.ownership_transparency, text: 'Ownership Transparency' }
            ];
        },
        
        getCredibilityExplanation: function(score) {
            if (score >= 80) {
                return 'This source maintains high journalistic standards with rigorous fact-checking, transparent corrections policies, and clear author attribution.';
            } else if (score >= 60) {
                return 'This source generally follows good journalistic practices but may have some gaps in transparency or fact-checking processes.';
            } else if (score >= 40) {
                return 'This source shows mixed adherence to journalistic standards. Some content may be reliable while other content requires additional verification.';
            } else {
                return 'This source has significant issues with journalistic standards, fact-checking, or transparency. Information should be verified with more credible sources.';
            }
        },
        
        calculateBiasScore: function(direction) {
            const biasMap = {
                'Far Left': { rotation: -60, score: -100 },
                'Left': { rotation: -30, score: -50 },
                'Center-Left': { rotation: -15, score: -25 },
                'Center': { rotation: 0, score: 0 },
                'Center-Right': { rotation: 15, score: 25 },
                'Right': { rotation: 30, score: 50 },
                'Far Right': { rotation: 60, score: 100 }
            };
            
            return biasMap[direction] || { rotation: 0, score: 0 };
        },
        
        generateBiasIndicators: function(bias) {
            return [
                { label: 'Language Bias', value: bias.language_bias || 0 },
                { label: 'Source Selection', value: bias.source_selection_bias || 0 },
                { label: 'Headline Bias', value: bias.headline_bias || 0 },
                { label: 'Image Selection', value: bias.image_bias || 0 },
                { label: 'Story Selection', value: bias.story_selection_bias || 0 }
            ];
        },
        
        getInitials: function(name) {
            if (!name || name === 'Unknown Author') return '?';
            return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
        },
        
        getSourceQualityText: function(score) {
            if (!score) return 'Unable to assess source quality';
            if (score >= 80) return 'Excellent - Multiple high-quality sources with strong verification';
            if (score >= 60) return 'Good - Adequate sourcing with some verification';
            if (score >= 40) return 'Fair - Limited sourcing, needs additional verification';
            return 'Poor - Insufficient or low-quality sources';
        },
        
        generatePDF: function() {
            const articleUrl = document.getElementById('articleUrl').value;
            if (!articleUrl) {
                alert('No article URL to generate report for');
                return;
            }
            
            // Make API call to generate PDF
            fetch('/api/generate-pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: articleUrl })
            })
            .then(response => response.blob())
            .then(blob => {
                // Create download link
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = 'news-analysis-report.pdf';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            })
            .catch(error => {
                console.error('Error generating PDF:', error);
                alert('Failed to generate PDF report');
            });
        },
        
        shareResults: function() {
            const articleUrl = document.getElementById('articleUrl').value;
            const shareText = `Check out this news analysis: ${articleUrl}`;
            
            if (navigator.share) {
                navigator.share({
                    title: 'News Analysis Report',
                    text: shareText,
                    url: window.location.href
                }).catch(err => console.log('Error sharing:', err));
            } else {
                // Fallback - copy to clipboard
                navigator.clipboard.writeText(shareText).then(() => {
                    alert('Link copied to clipboard!');
                }).catch(err => {
                    console.error('Failed to copy:', err);
                });
            }
        },
        
        showError: function(message) {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = `
                <div class="error-message">
                    <div class="error-icon">⚠️</div>
                    <div class="error-text">${message}</div>
                    <button class="action-button tertiary" onclick="NewsApp.ui.resetAnalysis()">
                        Try Again
                    </button>
                </div>
            `;
            resultsDiv.style.display = 'block';
        }
    };
    
    // Make sure NewsApp.results is available globally
    window.NewsApp.results = NewsApp.results;
    
})();
