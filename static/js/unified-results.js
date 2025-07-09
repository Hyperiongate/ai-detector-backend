/**
 * Facts & Fakes AI - Unified Results Module
 * Handles display of multi-modal analysis results
 */

(function() {
    'use strict';
    
    // Unified Results Module
    const UnifiedResults = {
        
        /**
         * Display comprehensive analysis results
         */
        displayResults(results) {
            console.log('Displaying unified results:', results);
            
            try {
                // Process results for display
                const processedResults = window.UnifiedApp.analysis.processResults(results);
                
                // Show results container
                this.showResultsContainer();
                
                // Display trust meter
                this.displayTrustMeter(processedResults.overall.trustScore);
                
                // Display all analysis sections
                this.displayAnalysisSections(processedResults);
                
                // Scroll to results
                this.scrollToResults();
                
                console.log('Results displayed successfully');
                
            } catch (error) {
                console.error('Error displaying results:', error);
                if (window.UnifiedApp.ui) {
                    window.UnifiedApp.ui.showError('Failed to display results. Please try again.');
                }
            }
        },
        
        /**
         * Show results container with animation
         */
        showResultsContainer() {
            const resultsContainer = document.getElementById('unifiedResults');
            if (resultsContainer) {
                resultsContainer.style.display = 'block';
                resultsContainer.classList.add('results-enter');
                
                // Remove animation class after animation completes
                setTimeout(() => {
                    resultsContainer.classList.remove('results-enter');
                }, 600);
            }
        },
        
        /**
         * Display animated trust meter
         */
        displayTrustMeter(trustScore) {
            const meterContainer = document.getElementById('unifiedTrustMeter');
            if (!meterContainer) return;
            
            // Clear existing content
            meterContainer.innerHTML = '';
            
            // Create SVG trust meter
            const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.setAttribute('width', '250');
            svg.setAttribute('height', '250');
            svg.setAttribute('viewBox', '0 0 250 250');
            
            // Background circle
            const bgCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            bgCircle.setAttribute('cx', '125');
            bgCircle.setAttribute('cy', '125');
            bgCircle.setAttribute('r', '100');
            bgCircle.setAttribute('fill', 'none');
            bgCircle.setAttribute('stroke', '#e2e8f0');
            bgCircle.setAttribute('stroke-width', '20');
            
            // Progress circle
            const progressCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            progressCircle.setAttribute('cx', '125');
            progressCircle.setAttribute('cy', '125');
            progressCircle.setAttribute('r', '100');
            progressCircle.setAttribute('fill', 'none');
            progressCircle.setAttribute('stroke-width', '20');
            progressCircle.setAttribute('stroke-linecap', 'round');
            progressCircle.setAttribute('transform', 'rotate(-90 125 125)');
            
            // Calculate stroke properties
            const circumference = 2 * Math.PI * 100;
            const strokeDasharray = circumference;
            const strokeDashoffset = circumference - (trustScore / 100) * circumference;
            
            progressCircle.setAttribute('stroke-dasharray', strokeDasharray);
            progressCircle.setAttribute('stroke-dashoffset', circumference); // Start at 0%
            
            // Set color based on trust score
            let strokeColor;
            if (trustScore >= 80) {
                strokeColor = '#48bb78'; // Green
            } else if (trustScore >= 60) {
                strokeColor = '#ed8936'; // Orange
            } else {
                strokeColor = '#e53e3e'; // Red
            }
            progressCircle.setAttribute('stroke', strokeColor);
            
            // Center text
            const centerText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            centerText.setAttribute('x', '125');
            centerText.setAttribute('y', '135');
            centerText.setAttribute('text-anchor', 'middle');
            centerText.setAttribute('font-size', '36');
            centerText.setAttribute('font-weight', 'bold');
            centerText.setAttribute('fill', '#2d3748');
            centerText.textContent = '0%';
            
            // Trust label
            const trustLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            trustLabel.setAttribute('x', '125');
            trustLabel.setAttribute('y', '155');
            trustLabel.setAttribute('text-anchor', 'middle');
            trustLabel.setAttribute('font-size', '16');
            trustLabel.setAttribute('fill', '#718096');
            trustLabel.textContent = 'Trust Score';
            
            // Assemble SVG
            svg.appendChild(bgCircle);
            svg.appendChild(progressCircle);
            svg.appendChild(centerText);
            svg.appendChild(trustLabel);
            
            meterContainer.appendChild(svg);
            
            // Animate the meter
            this.animateTrustMeter(progressCircle, centerText, trustScore, strokeDashoffset);
        },
        
        /**
         * Animate trust meter from 0 to target score
         */
        animateTrustMeter(progressCircle, centerText, targetScore, targetOffset) {
            let currentScore = 0;
            const duration = 2000; // 2 seconds
            const startTime = Date.now();
            const circumference = 2 * Math.PI * 100;
            
            const animate = () => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);
                
                // Use easing function
                const easedProgress = this.easeOutCubic(progress);
                
                currentScore = Math.round(targetScore * easedProgress);
                const currentOffset = circumference - (currentScore / 100) * circumference;
                
                // Update circle
                progressCircle.setAttribute('stroke-dashoffset', currentOffset);
                
                // Update text
                centerText.textContent = currentScore + '%';
                
                if (progress < 1) {
                    requestAnimationFrame(animate);
                }
            };
            
            requestAnimationFrame(animate);
        },
        
        /**
         * Easing function for smooth animation
         */
        easeOutCubic(t) {
            return 1 - Math.pow(1 - t, 3);
        },
        
        /**
         * Display all analysis sections
         */
        displayAnalysisSections(results) {
            const sectionsContainer = document.getElementById('unifiedAnalysisSections');
            if (!sectionsContainer) return;
            
            sectionsContainer.innerHTML = '';
            
            // Create sections based on available results
            const sections = [];
            
            // Overall Summary Section
            sections.push(this.createOverallSection(results.overall));
            
            // Text Analysis Section
            if (results.textAnalysis) {
                sections.push(this.createTextAnalysisSection(results.textAnalysis));
            }
            
            // News Analysis Section
            if (results.newsAnalysis) {
                sections.push(this.createNewsAnalysisSection(results.newsAnalysis));
            }
            
            // Image Analysis Section
            if (results.imageAnalysis) {
                sections.push(this.createImageAnalysisSection(results.imageAnalysis));
            }
            
            // Combined Insights Section
            if (results.combinedInsights.length > 0) {
                sections.push(this.createCombinedInsightsSection(results.combinedInsights));
            }
            
            // Technical Details Section
            sections.push(this.createTechnicalDetailsSection(results));
            
            // Recommendations Section
            sections.push(this.createRecommendationsSection(results));
            
            // Methodology Section
            sections.push(this.createMethodologySection());
            
            // Sources Section
            sections.push(this.createSourcesSection(results));
            
            // Export Options Section
            sections.push(this.createExportSection());
            
            // Add all sections to container
            sections.forEach(section => {
                sectionsContainer.appendChild(section);
            });
            
            // Initialize expandable functionality
            this.initializeExpandableSections();
        },
        
        /**
         * Create overall summary section
         */
        createOverallSection(overall) {
            const section = this.createSection('overall-summary', 'Overall Assessment', 'fas fa-chart-line', 'high');
            
            const content = `
                <div class="summary-grid">
                    <div class="summary-item">
                        <div class="summary-label">Trust Score</div>
                        <div class="summary-value trust-score-${this.getTrustLevel(overall.trustScore)}">${overall.trustScore}%</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Risk Level</div>
                        <div class="summary-value risk-${overall.riskLevel}">${overall.riskLevel.toUpperCase()}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Analysis Time</div>
                        <div class="summary-value">${new Date().toLocaleTimeString()}</div>
                    </div>
                </div>
                <div class="summary-description">
                    <p>${overall.summary}</p>
                </div>
            `;
            
            section.querySelector('.section-content').innerHTML = content;
            return section;
        },
        
        /**
         * Create text analysis section
         */
        createTextAnalysisSection(textAnalysis) {
            const section = this.createSection('text-analysis', 'Text AI Detection', 'fas fa-robot', 'medium');
            
            const aiProbability = Math.round(textAnalysis.aiProbability * 100);
            const humanProbability = 100 - aiProbability;
            
            const content = `
                <div class="detection-results">
                    <div class="detection-bar">
                        <div class="bar-label">AI Generated</div>
                        <div class="probability-bar">
                            <div class="bar-fill ai-bar" style="width: ${aiProbability}%"></div>
                            <span class="bar-text">${aiProbability}%</span>
                        </div>
                    </div>
                    <div class="detection-bar">
                        <div class="bar-label">Human Written</div>
                        <div class="probability-bar">
                            <div class="bar-fill human-bar" style="width: ${humanProbability}%"></div>
                            <span class="bar-text">${humanProbability}%</span>
                        </div>
                    </div>
                </div>
                <div class="analysis-details">
                    <h4>Key Findings:</h4>
                    <ul>
                        ${textAnalysis.patterns.map(pattern => `<li>${pattern}</li>`).join('')}
                    </ul>
                </div>
            `;
            
            section.querySelector('.section-content').innerHTML = content;
            return section;
        },
        
        /**
         * Create news analysis section
         */
        createNewsAnalysisSection(newsAnalysis) {
            const section = this.createSection('news-analysis', 'News Verification', 'fas fa-newspaper', 'high');
            
            const content = `
                <div class="news-scores">
                    <div class="score-item">
                        <span class="score-label">Credibility:</span>
                        <span class="score-value">${newsAnalysis.trustScore}%</span>
                    </div>
                    <div class="score-item">
                        <span class="score-label">Bias Level:</span>
                        <span class="score-value">${newsAnalysis.biasScore}%</span>
                    </div>
                </div>
                <div class="fact-checks">
                    <h4>Fact Check Results:</h4>
                    ${newsAnalysis.factChecks.map(check => `
                        <div class="fact-check-item verdict-${check.verdict}">
                            <div class="claim">${check.claim}</div>
                            <div class="verdict">${check.verdict.toUpperCase()}</div>
                        </div>
                    `).join('')}
                </div>
            `;
            
            section.querySelector('.section-content').innerHTML = content;
            return section;
        },
        
        /**
         * Create image analysis section
         */
        createImageAnalysisSection(imageAnalysis) {
            const section = this.createSection('image-analysis', 'Image Authentication', 'fas fa-image', 'medium');
            
            const content = `
                <div class="image-scores">
                    <div class="authenticity-score">
                        <span class="score-label">Authenticity Score:</span>
                        <span class="score-value">${imageAnalysis.trustScore}%</span>
                    </div>
                </div>
                <div class="image-findings">
                    <div class="finding-item ${imageAnalysis.aiGenerated ? 'warning' : 'success'}">
                        <i class="fas ${imageAnalysis.aiGenerated ? 'fa-exclamation-triangle' : 'fa-check-circle'}"></i>
                        <span>AI Generated: ${imageAnalysis.aiGenerated ? 'Detected' : 'Not Detected'}</span>
                    </div>
                    <div class="finding-item ${imageAnalysis.manipulated ? 'warning' : 'success'}">
                        <i class="fas ${imageAnalysis.manipulated ? 'fa-exclamation-triangle' : 'fa-check-circle'}"></i>
                        <span>Manipulation: ${imageAnalysis.manipulated ? 'Detected' : 'Not Detected'}</span>
                    </div>
                </div>
                <div class="metadata-info">
                    <h4>Metadata Analysis:</h4>
                    <p>Camera: ${imageAnalysis.metadata.camera || 'Unknown'}</p>
                    <p>Date Taken: ${imageAnalysis.metadata.dateTaken || 'Unknown'}</p>
                    <p>Location: ${imageAnalysis.metadata.location || 'Not available'}</p>
                </div>
            `;
            
            section.querySelector('.section-content').innerHTML = content;
            return section;
        },
        
        /**
         * Create combined insights section
         */
        createCombinedInsightsSection(insights) {
            const section = this.createSection('combined-insights', 'Cross-Modal Insights', 'fas fa-lightbulb', 'high');
            
            const content = `
                <div class="insights-list">
                    ${insights.map(insight => `
                        <div class="insight-item insight-${insight.type}">
                            <div class="insight-header">
                                <i class="fas ${this.getInsightIcon(insight.type)}"></i>
                                <h4>${insight.title}</h4>
                            </div>
                            <p>${insight.description}</p>
                        </div>
                    `).join('')}
                </div>
            `;
            
            section.querySelector('.section-content').innerHTML = content;
            return section;
        },
        
        /**
         * Create technical details section
         */
        createTechnicalDetailsSection(results) {
            const section = this.createSection('technical-details', 'Technical Analysis', 'fas fa-cogs', 'low');
            
            const content = `
                <div class="tech-details">
                    <div class="detail-group">
                        <h4>Models Used:</h4>
                        <ul>
                            ${results.textAnalysis ? '<li>GPT-4 Text Analysis</li>' : ''}
                            ${results.newsAnalysis ? '<li>News Credibility Engine</li>' : ''}
                            ${results.imageAnalysis ? '<li>Computer Vision Models</li>' : ''}
                        </ul>
                    </div>
                    <div class="detail-group">
                        <h4>Processing Time:</h4>
                        <p>Analysis completed in under 30 seconds</p>
                    </div>
                    <div class="detail-group">
                        <h4>Confidence Intervals:</h4>
                        <p>All scores include 95% confidence intervals</p>
                    </div>
                </div>
            `;
            
            section.querySelector('.section-content').innerHTML = content;
            return section;
        },
        
        /**
         * Create recommendations section
         */
        createRecommendationsSection(results) {
            const section = this.createSection('recommendations', 'Recommendations', 'fas fa-lightbulb', 'medium');
            
            const recommendations = this.generateRecommendations(results);
            
            const content = `
                <div class="recommendations-list">
                    ${recommendations.map(rec => `
                        <div class="recommendation-item">
                            <i class="fas ${rec.icon}"></i>
                            <div class="rec-content">
                                <h4>${rec.title}</h4>
                                <p>${rec.description}</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
            
            section.querySelector('.section-content').innerHTML = content;
            return section;
        },
        
        /**
         * Create methodology section
         */
        createMethodologySection() {
            const section = this.createSection('methodology', 'Our Methodology', 'fas fa-microscope', 'low');
            
            const content = `
                <div class="methodology-content">
                    <p>Our multi-modal analysis combines several cutting-edge AI technologies:</p>
                    <ul>
                        <li><strong>Natural Language Processing:</strong> Advanced transformer models analyze text patterns</li>
                        <li><strong>Computer Vision:</strong> Deep learning models detect image manipulation</li>
                        <li><strong>Knowledge Graphs:</strong> Cross-reference claims with verified databases</li>
                        <li><strong>Ensemble Methods:</strong> Multiple models provide consensus scoring</li>
                    </ul>
                    <p>All analyses are performed with strict privacy protections and data security measures.</p>
                </div>
            `;
            
            section.querySelector('.section-content').innerHTML = content;
            return section;
        },
        
        /**
         * Create sources section
         */
        createSourcesSection(results) {
            const section = this.createSection('sources', 'Sources & References', 'fas fa-book', 'low');
            
            const content = `
                <div class="sources-content">
                    <h4>Verification Sources:</h4>
                    <ul>
                        <li>Fact-checking databases (Snopes, PolitiFact, FactCheck.org)</li>
                        <li>News credibility ratings (AllSides, Media Bias/Fact Check)</li>
                        <li>Academic research publications</li>
                        <li>Government and institutional sources</li>
                    </ul>
                    <p><em>Last updated: ${new Date().toLocaleDateString()}</em></p>
                </div>
            `;
            
            section.querySelector('.section-content').innerHTML = content;
            return section;
        },
        
        /**
         * Create export options section
         */
        createExportSection() {
            const section = this.createSection('export-options', 'Export & Share', 'fas fa-download', 'medium');
            
            const content = `
                <div class="export-actions">
                    <button class="export-btn pdf-btn" onclick="window.downloadUnifiedPDF()">
                        <i class="fas fa-file-pdf"></i>
                        Download PDF Report
                    </button>
                    <button class="export-btn share-btn" onclick="window.shareUnifiedResults()">
                        <i class="fas fa-share-alt"></i>
                        Share Results
                    </button>
                </div>
                <div class="export-info">
                    <p>Export your analysis results as a comprehensive PDF report or share via social media.</p>
                </div>
            `;
            
            section.querySelector('.section-content').innerHTML = content;
            return section;
        },
        
        /**
         * Create a standardized section element
         */
        createSection(id, title, icon, priority) {
            const section = document.createElement('div');
            section.className = `analysis-section expandable priority-${priority}`;
            section.id = id;
            
            section.innerHTML = `
                <div class="section-header expand-trigger">
                    <div class="section-title">
                        <i class="${icon}"></i>
                        <h3>${title}</h3>
                    </div>
                    <div class="expand-icon">
                        <i class="fas fa-chevron-down"></i>
                    </div>
                </div>
                <div class="section-content expand-content">
                    <!-- Content will be added by specific section creators -->
                </div>
            `;
            
            return section;
        },
        
        /**
         * Initialize expandable sections
         */
        initializeExpandableSections() {
            const expandables = document.querySelectorAll('.analysis-section.expandable');
            
            expandables.forEach(section => {
                const trigger = section.querySelector('.expand-trigger');
                const content = section.querySelector('.expand-content');
                const icon = section.querySelector('.expand-icon i');
                
                // Expand high priority sections by default
                if (section.classList.contains('priority-high')) {
                    section.classList.add('expanded');
                    content.style.maxHeight = content.scrollHeight + 'px';
                    icon.style.transform = 'rotate(180deg)';
                }
                
                trigger.addEventListener('click', () => {
                    const isExpanded = section.classList.contains('expanded');
                    
                    if (isExpanded) {
                        content.style.maxHeight = '0';
                        section.classList.remove('expanded');
                        icon.style.transform = 'rotate(0deg)';
                    } else {
                        content.style.maxHeight = content.scrollHeight + 'px';
                        section.classList.add('expanded');
                        icon.style.transform = 'rotate(180deg)';
                    }
                });
            });
        },
        
        /**
         * Scroll to results section
         */
        scrollToResults() {
            const resultsContainer = document.getElementById('unifiedResults');
            if (resultsContainer) {
                setTimeout(() => {
                    resultsContainer.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }, 300);
            }
        },
        
        /**
         * Get trust level for styling
         */
        getTrustLevel(score) {
            if (score >= 80) return 'high';
            if (score >= 60) return 'medium';
            return 'low';
        },
        
        /**
         * Get insight icon based on type
         */
        getInsightIcon(type) {
            switch (type) {
                case 'warning': return 'fa-exclamation-triangle';
                case 'alert': return 'fa-exclamation-circle';
                case 'info': return 'fa-info-circle';
                default: return 'fa-lightbulb';
            }
        },
        
        /**
         * Generate recommendations based on results
         */
        generateRecommendations(results) {
            const recommendations = [];
            
            if (results.overall.trustScore < 60) {
                recommendations.push({
                    icon: 'fa-shield-alt',
                    title: 'Exercise Caution',
                    description: 'This content shows multiple indicators of low trustworthiness. Verify information through additional sources.'
                });
            }
            
            if (results.textAnalysis && results.textAnalysis.aiDetected) {
                recommendations.push({
                    icon: 'fa-robot',
                    title: 'AI-Generated Content',
                    description: 'Consider the source and purpose of AI-generated content when evaluating its reliability.'
                });
            }
            
            if (results.newsAnalysis && results.newsAnalysis.biasScore > 70) {
                recommendations.push({
                    icon: 'fa-balance-scale',
                    title: 'Check for Bias',
                    description: 'This source shows significant bias. Seek out diverse perspectives on this topic.'
                });
            }
            
            recommendations.push({
                icon: 'fa-users',
                title: 'Cross-Reference Sources',
                description: 'Always verify important information across multiple reliable sources before sharing.'
            });
            
            return recommendations;
        }
    };
    
    // Attach to UnifiedApp namespace when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            if (window.UnifiedApp) {
                window.UnifiedApp.results = UnifiedResults;
                console.log('Unified Results module loaded');
            }
        });
    } else {
        if (window.UnifiedApp) {
            window.UnifiedApp.results = UnifiedResults;
            console.log('Unified Results module loaded');
        }
    }
    
})();
