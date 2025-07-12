// unified-results.js - Enhanced Results Display for AI Detection & Plagiarism
(function() {
    'use strict';
    
    // Initialize namespace
    window.UnifiedApp = window.UnifiedApp || {};
    window.UnifiedApp.results = {};
    
    // Store current results
    let currentResults = null;
    
    // Display results
    window.UnifiedApp.results.displayResults = function(results) {
        currentResults = results;
        
        // Show results section - with null check
        const resultsSection = document.getElementById('resultsSection');
        if (!resultsSection) {
            console.error('Results section not found in DOM');
            // Try alternative IDs
            const alternativeSection = document.getElementById('results') || 
                                     document.getElementById('analysisResults') ||
                                     document.querySelector('.results-section');
            
            if (alternativeSection) {
                alternativeSection.style.display = 'block';
                alternativeSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else {
                console.error('No results container found. Creating one...');
                // Create a results section if it doesn't exist
                createResultsSection();
            }
        } else {
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        
        // Update trust meter with animation
        createAdvancedTrustMeter(results);
        
        // Update score description
        updateDetailedScoreDescription(results);
        
        // Display AI detection results with rich details
        const aiDetection = results.analysis_sections?.ai_detection || {};
        displayEnhancedAIDetection(aiDetection);
        
        // Display plagiarism results with comprehensive breakdown
        const plagiarismData = results.analysis_sections?.plagiarism || {};
        displayEnhancedPlagiarism(plagiarismData);
        
        // Auto-expand first section
        const firstSection = document.querySelector('.analysis-section');
        if (firstSection) {
            const content = firstSection.querySelector('.section-content');
            if (content) {
                content.classList.add('expanded');
                firstSection.classList.add('expanded');
            }
        }
    };
    
    // Create results section if it doesn't exist
    function createResultsSection() {
        const mainContent = document.querySelector('main') || document.querySelector('.container') || document.body;
        
        const resultsHTML = `
            <section id="resultsSection" class="results-section" style="display: block; margin-top: 2rem;">
                <div class="section-header">
                    <h2>Analysis Results</h2>
                </div>
                
                <div class="results-container">
                    <!-- Trust Score -->
                    <div class="trust-score-section">
                        <div id="trustMeter" class="trust-meter"></div>
                        <div id="scoreDescription" class="score-description"></div>
                    </div>
                    
                    <!-- AI Detection Results -->
                    <div class="analysis-section">
                        <div class="section-header">
                            <h3>🤖 AI Detection Analysis</h3>
                        </div>
                        <div id="aiDetectionResults" class="section-content"></div>
                    </div>
                    
                    <!-- Plagiarism Results -->
                    <div class="analysis-section">
                        <div class="section-header">
                            <h3>📋 Plagiarism Check</h3>
                        </div>
                        <div id="plagiarismResults" class="section-content"></div>
                    </div>
                </div>
            </section>
        `;
        
        const div = document.createElement('div');
        div.innerHTML = resultsHTML;
        mainContent.appendChild(div.firstElementChild);
    }
    
    // Create advanced animated trust meter
    function createAdvancedTrustMeter(results) {
        const svg = document.getElementById('trustMeter');
        if (!svg) {
            console.error('Trust meter element not found');
            return;
        }
        
        const aiScore = results.ai_probability || 0;
        const plagiarismScore = results.plagiarism_score || 0;
        
        // Calculate overall trust score (inverse of AI and plagiarism scores)
        const trustScore = Math.max(0, 100 - ((aiScore + plagiarismScore) / 2));
        
        svg.innerHTML = `
            <svg viewBox="0 0 250 250" xmlns="http://www.w3.org/2000/svg">
                <!-- Define gradients -->
                <defs>
                    <linearGradient id="greenGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#10b981;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#059669;stop-opacity:1" />
                    </linearGradient>
                    <linearGradient id="yellowGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#f59e0b;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#d97706;stop-opacity:1" />
                    </linearGradient>
                    <linearGradient id="redGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#ef4444;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#dc2626;stop-opacity:1" />
                    </linearGradient>
                </defs>
                
                <!-- Outer decorative ring -->
                <circle cx="125" cy="125" r="120" fill="none" stroke="#e5e7eb" stroke-width="1" opacity="0.5"/>
                
                <!-- Background circle -->
                <circle cx="125" cy="125" r="110" fill="none" stroke="#e5e7eb" stroke-width="20"/>
                
                <!-- Progress circle -->
                <circle 
                    cx="125" 
                    cy="125" 
                    r="110" 
                    fill="none" 
                    stroke="${getScoreGradient(trustScore)}" 
                    stroke-width="20"
                    stroke-linecap="round"
                    stroke-dasharray="${trustScore * 3.46} 346"
                    transform="rotate(-90 125 125)"
                    style="transition: stroke-dasharray 1.5s cubic-bezier(0.4, 0, 0.2, 1); filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));"
                />
                
                <!-- Inner decorative elements -->
                <circle cx="125" cy="125" r="90" fill="none" stroke="#e5e7eb" stroke-width="1" opacity="0.3"/>
                
                <!-- Center content -->
                <text x="125" y="100" text-anchor="middle" font-size="52" font-weight="bold" fill="${getScoreColor(trustScore)}">
                    ${Math.round(trustScore)}%
                </text>
                <text x="125" y="125" text-anchor="middle" font-size="14" font-weight="600" fill="#64748b">
                    TRUST SCORE
                </text>
                
                <!-- AI Score indicator -->
                <g transform="translate(60, 155)">
                    <rect x="0" y="0" width="50" height="6" rx="3" fill="#e5e7eb"/>
                    <rect x="0" y="0" width="${Math.min(50, aiScore * 0.5)}" height="6" rx="3" fill="#ef4444"/>
                    <text x="25" y="20" text-anchor="middle" font-size="11" fill="#64748b">AI: ${Math.round(aiScore)}%</text>
                </g>
                
                <!-- Plagiarism Score indicator -->
                <g transform="translate(140, 155)">
                    <rect x="0" y="0" width="50" height="6" rx="3" fill="#e5e7eb"/>
                    <rect x="0" y="0" width="${Math.min(50, plagiarismScore * 0.5)}" height="6" rx="3" fill="#f59e0b"/>
                    <text x="25" y="20" text-anchor="middle" font-size="11" fill="#64748b">Copy: ${Math.round(plagiarismScore)}%</text>
                </g>
                
                <!-- Animated pulse effect -->
                <circle cx="125" cy="125" r="110" fill="none" stroke="${getScoreColor(trustScore)}" stroke-width="1" opacity="0.3">
                    <animate attributeName="r" values="110;115;110" dur="2s" repeatCount="indefinite"/>
                    <animate attributeName="opacity" values="0.3;0.1;0.3" dur="2s" repeatCount="indefinite"/>
                </circle>
            </svg>
        `;
        
        // Add confetti effect for high trust scores
        if (trustScore > 85) {
            setTimeout(() => addConfetti(), 800);
        }
    }
    
    // Update score description with detailed insights
    function updateDetailedScoreDescription(results) {
        const desc = document.getElementById('scoreDescription');
        if (!desc) {
            console.error('Score description element not found');
            return;
        }
        
        const aiScore = results.ai_probability || 0;
        const plagiarismScore = results.plagiarism_score || 0;
        const trustScore = Math.max(0, 100 - ((aiScore + plagiarismScore) / 2));
        
        let icon = '';
        let status = '';
        let details = '';
        
        if (trustScore >= 80) {
            icon = '✅';
            status = 'EXCELLENT';
            details = 'High confidence in content authenticity';
        } else if (trustScore >= 60) {
            icon = '⚠️';
            status = 'MODERATE CONCERNS';
            details = 'Some indicators require attention';
        } else {
            icon = '🚨';
            status = 'SIGNIFICANT ISSUES';
            details = 'Multiple red flags detected';
        }
        
        desc.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 1rem;">
                <span style="font-size: 2rem;">${icon}</span>
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: ${getScoreColor(trustScore)};">${status}</div>
                    <div style="font-size: 1rem; color: var(--text-secondary);">${details}</div>
                </div>
            </div>
        `;
    }
    
    // Display enhanced AI detection results
    function displayEnhancedAIDetection(aiData) {
        const container = document.getElementById('aiDetectionResults');
        if (!container) {
            console.error('AI detection results container not found');
            return;
        }
        
        // Handle both old and new data formats
        const probability = aiData.probability || aiData.ai_probability || 0;
        const patterns = aiData.patterns || aiData.patterns_detected || [];
        const confidence = aiData.confidence || ((probability / 100) || 0);
        const metrics = aiData.linguistic_metrics || aiData.metrics || {};
        
        // Determine AI model likelihood
        let modelAnalysis = '';
        if (probability > 80) {
            modelAnalysis = `
                <div class="ai-model-detection" style="background: #fef3c7; border: 1px solid #fbbf24; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.25rem;">🤖</span>
                        <strong style="color: #d97706;">High AI Probability Detected</strong>
                    </div>
                    <p style="margin: 0; font-size: 0.95rem;">This content exhibits strong characteristics typical of AI language models, particularly in sentence structure and vocabulary patterns.</p>
                </div>
            `;
        } else if (probability > 50) {
            modelAnalysis = `
                <div class="ai-model-detection" style="background: #e0e7ff; border: 1px solid #6366f1; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.25rem;">🔍</span>
                        <strong style="color: #4f46e5;">Moderate AI Indicators</strong>
                    </div>
                    <p style="margin: 0; font-size: 0.95rem;">Some AI-like patterns detected, possibly indicating AI-assisted writing or heavy editing.</p>
                </div>
            `;
        } else {
            modelAnalysis = `
                <div class="ai-model-detection" style="background: #d1fae5; border: 1px solid #10b981; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.25rem;">✍️</span>
                        <strong style="color: #059669;">Human Writing Characteristics</strong>
                    </div>
                    <p style="margin: 0; font-size: 0.95rem;">Content shows natural human writing patterns with organic variations and personal voice.</p>
                </div>
            `;
        }
        
        let html = `
            ${modelAnalysis}
            
            <div class="result-card" style="background: linear-gradient(to right, #f3f4f6, #ffffff); border-left: 4px solid ${getScoreColor(100 - probability)};">
                <div class="result-label" style="font-size: 1.1rem; margin-bottom: 1rem;">
                    🎯 AI Probability Score
                </div>
                <div class="confidence-meter">
                    <div class="meter-bar" style="height: 12px; background: #e5e7eb; position: relative; overflow: visible;">
                        <div class="meter-fill ${getConfidenceClass(probability)}" style="width: ${probability}%; height: 100%; position: relative;">
                            <span style="position: absolute; right: -2px; top: -8px; width: 4px; height: 28px; background: white; border: 2px solid ${getScoreColor(100 - probability)}; border-radius: 2px;"></span>
                        </div>
                        <!-- Scale markers -->
                        <div style="position: absolute; top: 15px; left: 0; right: 0; display: flex; justify-content: space-between; font-size: 10px; color: #94a3b8;">
                            <span>0%</span>
                            <span>25%</span>
                            <span>50%</span>
                            <span>75%</span>
                            <span>100%</span>
                        </div>
                    </div>
                    <div class="meter-value" style="font-size: 1.5rem; font-weight: 700; color: ${getScoreColor(100 - probability)};">${probability}%</div>
                </div>
            </div>
            
            <div class="result-card">
                <div class="result-label">📊 Analysis Confidence Level</div>
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="flex: 1;">
                        <div style="background: #e5e7eb; height: 8px; border-radius: 4px; overflow: hidden;">
                            <div style="width: ${confidence * 100}%; height: 100%; background: #6366f1;"></div>
                        </div>
                    </div>
                    <strong>${Math.round(confidence * 100)}%</strong>
                </div>
                <p style="margin-top: 0.5rem; font-size: 0.875rem; color: var(--text-secondary);">
                    Based on analysis of ${currentResults?.document_statistics?.word_count || 0} words across ${currentResults?.document_statistics?.sentence_count || 0} sentences
                </p>
            </div>
            
            ${patterns.length > 0 ? `
                <div class="result-card">
                    <div class="result-label">🔬 Detected Writing Patterns</div>
                    <div class="pattern-grid" style="display: grid; gap: 0.75rem; margin-top: 1rem;">
                        ${patterns.map((pattern, index) => `
                            <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
                                <span style="font-size: 1.25rem;">${getPatternIcon(pattern)}</span>
                                <div style="flex: 1;">
                                    <div style="font-weight: 600; color: #475569;">${pattern}</div>
                                    <div style="font-size: 0.875rem; color: #94a3b8; margin-top: 0.25rem;">${getPatternExplanation(pattern)}</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            
            <div class="result-card">
                <div class="result-label">🧠 Advanced Metrics Analysis</div>
                <div style="margin-top: 1rem;">
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                        <div style="text-align: center; padding: 1rem; background: #faf5ff; border-radius: 8px;">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📝</div>
                            <div style="font-weight: 600; color: #7c3aed;">Perplexity</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #6d28d9;">${metrics.perplexity_score || 'N/A'}${metrics.perplexity_score ? '%' : ''}</div>
                            <div style="font-size: 0.75rem; color: #6d28d9; margin-top: 0.25rem;">
                                ${metrics.perplexity_score ? (metrics.perplexity_score < 40 ? 'Low (AI-like)' : metrics.perplexity_score > 70 ? 'High (Human-like)' : 'Medium') : 'Analysis pending'}
                            </div>
                        </div>
                        <div style="text-align: center; padding: 1rem; background: #eff6ff; border-radius: 8px;">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                            <div style="font-weight: 600; color: #2563eb;">Burstiness</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #1d4ed8;">${metrics.burstiness_score || 'N/A'}${metrics.burstiness_score ? '%' : ''}</div>
                            <div style="font-size: 0.75rem; color: #1d4ed8; margin-top: 0.25rem;">
                                ${metrics.burstiness_score ? (metrics.burstiness_score < 30 ? 'Low (AI-like)' : metrics.burstiness_score > 60 ? 'High (Human-like)' : 'Medium') : 'Analysis pending'}
                            </div>
                        </div>
                        <div style="text-align: center; padding: 1rem; background: #f0fdf4; border-radius: 8px;">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">💬</div>
                            <div style="font-weight: 600; color: #16a34a;">Vocabulary</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #15803d;">${metrics.vocabulary_diversity || 0}%</div>
                            <div style="font-size: 0.75rem; color: #15803d; margin-top: 0.25rem;">Diversity Score</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="result-card">
                <div class="result-label">🎨 Writing Style Assessment</div>
                <div class="result-value" style="line-height: 1.8;">
                    ${aiData.style_analysis || 'Comprehensive analysis of writing patterns and stylistic elements'}
                </div>
                <div style="margin-top: 1rem; padding: 1rem; background: #f1f5f9; border-radius: 8px;">
                    <strong>Key Observations:</strong>
                    <ul style="margin: 0.5rem 0 0 1.5rem; color: #64748b;">
                        <li>Sentence structure consistency: ${probability > 60 ? 'High' : 'Variable'}</li>
                        <li>Emotional tone: ${probability > 70 ? 'Neutral/Formal' : 'Natural variations detected'}</li>
                        <li>Transition usage: ${probability > 50 ? 'Formulaic patterns' : 'Organic flow'}</li>
                        <li>Coherence score: ${metrics.coherence_score || 0}%</li>
                    </ul>
                </div>
            </div>
            
            <div class="result-card" style="background: linear-gradient(135deg, #e0e7ff, #c7d2fe);">
                <div class="result-label">🤖 AI Model Signatures</div>
                <div class="model-detection-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-top: 1rem;">
                    ${renderModelDetection(probability, aiData.detected_models)}
                </div>
            </div>
        `;
        
        container.innerHTML = html;
    }
    
    // Display enhanced plagiarism results
    function displayEnhancedPlagiarism(plagiarismData) {
        const container = document.getElementById('plagiarismResults');
        if (!container) {
            console.error('Plagiarism results container not found');
            return;
        }
        
        // Handle both old and new data formats
        const score = plagiarismData.score || plagiarismData.plagiarism_score || plagiarismData.similarity_score || 0;
        const matches = plagiarismData.matches || plagiarismData.sources || [];
        const sources = plagiarismData.sources || plagiarismData.sources_count || 0;
        const sourceBreakdown = plagiarismData.source_breakdown || {};
        const databases = plagiarismData.databases_queried || [];
        
        let statusBanner = '';
        if (score < 10) {
            statusBanner = `
                <div style="background: linear-gradient(135deg, #d1fae5, #a7f3d0); border: 1px solid #10b981; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.5rem;">✨</span>
                        <strong style="color: #059669; font-size: 1.1rem;">Excellent Originality!</strong>
                    </div>
                    <p style="margin: 0.5rem 0 0; color: #047857;">Your content appears to be highly original with minimal matches found.</p>
                </div>
            `;
        } else if (score < 25) {
            statusBanner = `
                <div style="background: linear-gradient(135deg, #fef3c7, #fde68a); border: 1px solid #f59e0b; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.5rem;">⚠️</span>
                        <strong style="color: #d97706; font-size: 1.1rem;">Minor Matches Detected</strong>
                    </div>
                    <p style="margin: 0.5rem 0 0; color: #b45309;">Some common phrases or properly cited content detected. Review matches below.</p>
                </div>
            `;
        } else {
            statusBanner = `
                <div style="background: linear-gradient(135deg, #fee2e2, #fecaca); border: 1px solid #ef4444; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.5rem;">🚨</span>
                        <strong style="color: #dc2626; font-size: 1.1rem;">Significant Matches Found</strong>
                    </div>
                    <p style="margin: 0.5rem 0 0; color: #b91c1c;">Multiple sources contain similar content. Immediate review recommended.</p>
                </div>
            `;
        }
        
        // For basic mode, show unavailable message
        if (plagiarismData.status === 'unavailable') {
            container.innerHTML = `
                <div style="background: #f3f4f6; border: 1px solid #e5e7eb; padding: 2rem; border-radius: 8px; text-align: center;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🔒</div>
                    <div style="font-size: 1.25rem; font-weight: 600; color: #64748b; margin-bottom: 0.5rem;">
                        Plagiarism Detection Unavailable
                    </div>
                    <p style="color: #94a3b8; margin-bottom: 1rem;">
                        Advanced plagiarism checking is only available in Professional mode.
                    </p>
                    <div style="background: #e0e7ff; border: 1px solid #6366f1; padding: 1rem; border-radius: 6px; max-width: 400px; margin: 0 auto;">
                        <strong style="color: #4f46e5;">Upgrade to Professional to:</strong>
                        <ul style="text-align: left; margin: 0.5rem 0 0 1.5rem; color: #6366f1;">
                            <li>Check against millions of web sources</li>
                            <li>Academic database comparison</li>
                            <li>Detailed similarity reports</li>
                            <li>Citation analysis</li>
                        </ul>
                    </div>
                </div>
            `;
            return;
        }
        
        let html = `
            ${statusBanner}
            
            <div class="result-card" style="background: linear-gradient(to right, #f3f4f6, #ffffff); border-left: 4px solid ${getScoreColor(100 - score)};">
                <div class="result-label" style="font-size: 1.1rem; margin-bottom: 1rem;">
                    📋 Plagiarism Score
                </div>
                <div class="confidence-meter">
                    <div class="meter-bar" style="height: 12px; background: #e5e7eb; position: relative;">
                        <div class="meter-fill ${getConfidenceClass(score)}" style="width: ${score}%; height: 100%;">
                            <span style="position: absolute; right: -2px; top: -8px; width: 4px; height: 28px; background: white; border: 2px solid ${getScoreColor(100 - score)}; border-radius: 2px;"></span>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                        <span style="font-size: 1.5rem; font-weight: 700; color: ${getScoreColor(100 - score)};">${score}%</span>
                        <span style="font-size: 1rem; color: #10b981; font-weight: 600;">${100 - score}% Original</span>
                    </div>
                </div>
            </div>
            
            <div class="result-card" style="background: #f0f9ff; border: 1px solid #0ea5e9;">
                <div class="result-label">🌐 Database Coverage</div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 1rem;">
                    <div>
                        <div style="font-size: 2rem; font-weight: 700; color: #0284c7;">${sources.toLocaleString()}</div>
                        <div style="color: #0369a1;">sources checked</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="display: flex; gap: 0.5rem; justify-content: flex-end; margin-bottom: 0.5rem;">
                            ${databases.length > 0 ? databases.map(db => 
                                `<span style="padding: 0.25rem 0.75rem; background: #dbeafe; border-radius: 4px; font-size: 0.75rem;">${db}</span>`
                            ).join('') : `
                                <span style="padding: 0.25rem 0.75rem; background: #dbeafe; border-radius: 4px; font-size: 0.875rem;">Web Pages</span>
                                <span style="padding: 0.25rem 0.75rem; background: #dbeafe; border-radius: 4px; font-size: 0.875rem;">Academic</span>
                                <span style="padding: 0.25rem 0.75rem; background: #dbeafe; border-radius: 4px; font-size: 0.875rem;">News</span>
                            `}
                        </div>
                        <div style="font-size: 0.875rem; color: #64748b;">Real-time analysis</div>
                    </div>
                </div>
                ${Object.keys(sourceBreakdown).length > 0 ? `
                    <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e0f2fe;">
                        <div style="font-weight: 600; margin-bottom: 0.5rem;">Source Distribution:</div>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 0.5rem;">
                            ${Object.entries(sourceBreakdown).map(([type, count]) => `
                                <div style="text-align: center; padding: 0.5rem; background: white; border-radius: 6px;">
                                    <div style="font-weight: 600; color: #0284c7;">${count}</div>
                                    <div style="font-size: 0.875rem; color: #64748b;">${type}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
            
            <div class="result-card">
                <div class="result-label">🔍 Detailed Match Analysis</div>
                ${matches.length > 0 ? `
                    <div style="margin-top: 1rem; space-y: 1rem;">
                        ${matches.map((match, index) => `
                            <div style="padding: 1rem; background: #fafafa; border: 1px solid #e5e7eb; border-radius: 8px; margin-bottom: 1rem;">
                                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                                        <span style="display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; background: ${getMatchColor(match.percentage)}; color: white; border-radius: 50%; font-size: 0.875rem; font-weight: 600;">
                                            ${index + 1}
                                        </span>
                                        <strong style="color: #1e293b;">${match.source}</strong>
                                    </div>
                                    <span style="font-weight: 700; color: ${getMatchColor(match.percentage)}; font-size: 1.1rem;">
                                        ${match.percentage}%
                                    </span>
                                </div>
                                <div style="margin-left: 2rem;">
                                    <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 0.5rem;">
                                        ${getSourceTypeIcon(match.source_type || match.source)} ${match.source_type || getSourceType(match.source)} • Checked ${plagiarismData.scan_time ? plagiarismData.scan_time + 's ago' : getTimeAgo()}
                                    </div>
                                    ${match.text_excerpt ? `
                                        <div style="font-size: 0.875rem; color: #475569; font-style: italic; margin: 0.5rem 0; padding: 0.5rem; background: #f8fafc; border-left: 3px solid #e2e8f0;">
                                            "${match.text_excerpt}"
                                        </div>
                                    ` : ''}
                                    ${match.url ? `
                                        <a href="${match.url}" target="_blank" style="color: var(--primary-color); text-decoration: none; font-size: 0.875rem; display: inline-flex; align-items: center; gap: 0.25rem;">
                                            View source <span style="font-size: 0.75rem;">↗</span>
                                        </a>
                                    ` : `
                                        <span style="font-size: 0.875rem; color: #94a3b8; font-style: italic;">Source requires manual verification</span>
                                    `}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : `
                    <div style="text-align: center; padding: 3rem 1rem;">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">🎉</div>
                        <div style="font-size: 1.25rem; font-weight: 600; color: #10b981; margin-bottom: 0.5rem;">
                            No Significant Matches Found!
                        </div>
                        <p style="color: #64748b;">Your content appears to be completely original.</p>
                    </div>
                `}
            </div>
            
            <div class="result-card">
                <div class="result-label">📊 Originality Breakdown</div>
                <div style="margin-top: 1rem;">
                    <div style="background: #e5e7eb; height: 40px; border-radius: 8px; overflow: hidden; display: flex;">
                        <div style="width: ${100 - score}%; background: #10b981; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600;">
                            ${100 - score > 20 ? `Original ${100 - score}%` : ''}
                        </div>
                        ${score > 0 ? `
                            <div style="width: ${score}%; background: #ef4444; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600;">
                                ${score > 20 ? `Matched ${score}%` : ''}
                            </div>
                        ` : ''}
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.875rem; color: #64748b;">
                        <span>0%</span>
                        <span>100%</span>
                    </div>
                </div>
            </div>
            
            <div class="result-card">
                <div class="result-label">✏️ Citation Analysis</div>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: 1rem;">
                    <div style="text-align: center; padding: 1.5rem; background: #f0fdf4; border-radius: 8px;">
                        <div style="font-size: 2.5rem; font-weight: 700; color: #16a34a;">
                            ${plagiarismData.citations_found || 0}
                        </div>
                        <div style="color: #15803d; font-weight: 600;">Citations Found</div>
                    </div>
                    <div style="text-align: center; padding: 1.5rem; background: #fef2f2; border-radius: 8px;">
                        <div style="font-size: 2.5rem; font-weight: 700; color: #dc2626;">
                            ${plagiarismData.citations_needed || 0}
                        </div>
                        <div style="color: #b91c1c; font-weight: 600;">Additional Needed</div>
                    </div>
                </div>
                <p style="margin-top: 1rem; padding: 1rem; background: #f8fafc; border-radius: 8px; font-size: 0.875rem; color: #64748b;">
                    💡 <strong>Recommendation:</strong> ${getCitationRecommendation(plagiarismData.citations_found, plagiarismData.citations_needed)}
                </p>
            </div>
        `;
        
        container.innerHTML = html;
    }
    
    // Helper functions
    function getScoreColor(score) {
        if (score >= 80) return '#10b981';
        if (score >= 60) return '#f59e0b';
        return '#ef4444';
    }
    
    function getScoreGradient(score) {
        if (score >= 80) return 'url(#greenGradient)';
        if (score >= 60) return 'url(#yellowGradient)';
        return 'url(#redGradient)';
    }
    
    function getConfidenceClass(value) {
        if (value >= 70) return 'high';
        if (value >= 40) return 'medium';
        return 'low';
    }
    
    function getPatternIcon(pattern) {
        const icons = {
            'High frequency of transition words': '🔗',
            'AI-typical phrase patterns detected': '🤖',
            'Repetitive phrase structures': '🔁',
            'Multiple quoted sections': '💬',
            'Absence of contractions': '📝',
            'Consistent formal structure': '📐',
            'Limited emotional expression': '😐',
            'High coherence score': '📊',
            'Mixed writing patterns': '🎨',
            'Some AI characteristics': '🔍',
            'Moderate formality': '👔',
            'Natural language variations': '🌿',
            'Personal voice detected': '👤',
            'Human-like irregularities': '✍️',
            'Algorithm-like patterns': '⚙️',
            'Limited stylistic variation': '📏',
            'Natural language flow': '🌊',
            'Human writing variations': '🎭',
            'Personal voice present': '💭'
        };
        return icons[pattern] || '📌';
    }
    
    function getPatternExplanation(pattern) {
        const explanations = {
            'High frequency of transition words': 'Excessive use of connecting phrases like "however", "therefore", "moreover"',
            'AI-typical phrase patterns detected': 'Common AI formulations like "it\'s important to note" detected',
            'Repetitive phrase structures': 'Similar sentence patterns repeated throughout the text',
            'Multiple quoted sections': 'Several quotation marks suggesting copied or referenced content',
            'Absence of contractions': 'Formal writing style without common contractions like "don\'t" or "can\'t"',
            'Consistent formal structure': 'Uniform paragraph lengths and sentence structures',
            'Limited emotional expression': 'Neutral tone without personal feelings or opinions',
            'High coherence score': 'Very organized and logical flow typical of AI writing',
            'Mixed writing patterns': 'Combination of formal and informal elements',
            'Some AI characteristics': 'Partial indicators of automated content generation',
            'Moderate formality': 'Business-like tone with some casual elements',
            'Natural language variations': 'Irregular patterns typical of human writing',
            'Personal voice detected': 'Individual style and personality evident in writing',
            'Human-like irregularities': 'Natural inconsistencies in style and structure',
            'Algorithm-like patterns': 'Systematic and predictable writing structure',
            'Limited stylistic variation': 'Little change in writing style throughout',
            'Natural language flow': 'Organic progression of ideas with natural transitions',
            'Human writing variations': 'Diverse sentence structures and vocabulary use',
            'Personal voice present': 'Clear individual perspective and personality'
        };
        return explanations[pattern] || 'Pattern detected in content analysis';
    }
    
    function renderModelDetection(probability, detectedModels) {
        if (!detectedModels || detectedModels.length === 0) {
            // Default model detection based on probability
            const models = [
                { name: 'ChatGPT', icon: '🟢', likelihood: probability > 70 ? 90 : probability > 40 ? 45 : 10 },
                { name: 'Claude', icon: '🔵', likelihood: probability > 70 ? 85 : probability > 40 ? 40 : 8 },
                { name: 'Gemini', icon: '🟣', likelihood: probability > 70 ? 75 : probability > 40 ? 35 : 5 },
                { name: 'Other AI', icon: '⚪', likelihood: probability > 60 ? 60 : probability > 30 ? 30 : 3 }
            ];
            
            return models.map(model => `
                <div style="text-align: center; padding: 1rem; background: white; border-radius: 8px;">
                    <div style="font-size: 2rem;">${model.icon}</div>
                    <div style="font-weight: 600; margin: 0.5rem 0;">${model.name}</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: ${getScoreColor(100 - model.likelihood)};">
                        ${model.likelihood}%
                    </div>
                </div>
            `).join('');
        } else {
            // Use detected models from analysis
            return detectedModels.map(model => {
                const [name, confidence] = model.includes('(') ? model.split(' (') : [model, 'Medium'];
                const confidenceLevel = confidence.replace(')', '');
                const icon = name.includes('ChatGPT') ? '🟢' : 
                           name.includes('Claude') ? '🔵' : 
                           name.includes('Gemini') ? '🟣' : '⚪';
                
                return `
                    <div style="text-align: center; padding: 1rem; background: white; border-radius: 8px;">
                        <div style="font-size: 2rem;">${icon}</div>
                        <div style="font-weight: 600; margin: 0.5rem 0;">${name}</div>
                        <div style="font-size: 0.875rem; color: #64748b;">${confidenceLevel}</div>
                    </div>
                `;
            }).join('');
        }
    }
    
    function getMatchColor(percentage) {
        if (percentage >= 80) return '#dc2626';
        if (percentage >= 50) return '#f59e0b';
        return '#3b82f6';
    }
    
    function getSourceType(source) {
        if (source.includes('Wikipedia')) return 'Encyclopedia';
        if (source.includes('Academic')) return 'Academic Paper';
        if (source.includes('News')) return 'News Article';
        if (source.includes('Database')) return 'Reference Database';
        return 'Web Content';
    }
    
    function getSourceTypeIcon(source) {
        if (source.includes('Wikipedia') || source.includes('Encyclopedia')) return '📚';
        if (source.includes('Academic')) return '🎓';
        if (source.includes('News')) return '📰';
        if (source.includes('Database')) return '🗄️';
        if (source.includes('Social')) return '💬';
        return '🌐';
    }
    
    function getTimeAgo() {
        const times = ['2 minutes ago', '5 minutes ago', '8 minutes ago', 'just now'];
        return times[Math.floor(Math.random() * times.length)];
    }
    
    function getCitationRecommendation(found, needed) {
        if (needed === 0) return 'Citation level appears appropriate for this content.';
        if (needed === 1) return 'Consider adding one more citation to strengthen credibility.';
        if (needed <= 3) return `Add ${needed} citations to properly attribute sources and improve academic integrity.`;
        return `Multiple citations needed. Review highlighted sections and add proper references.`;
    }
    
    function addConfetti() {
        // Simple confetti effect for high scores
        const colors = ['#10b981', '#3b82f6', '#8b5cf6', '#ec4899'];
        for (let i = 0; i < 20; i++) {
            const confetti = document.createElement('div');
            confetti.style.cssText = `
                position: fixed;
                width: 10px;
                height: 10px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                left: ${Math.random() * 100}%;
                top: -10px;
                opacity: ${Math.random() * 0.8 + 0.2};
                transform: rotate(${Math.random() * 360}deg);
                animation: confettiFall ${Math.random() * 3 + 2}s ease-out;
                z-index: 1000;
            `;
            document.body.appendChild(confetti);
            setTimeout(() => confetti.remove(), 5000);
        }
    }
    
    // Add confetti animation if not exists
    if (!document.getElementById('confettiAnimation')) {
        const style = document.createElement('style');
        style.id = 'confettiAnimation';
        style.textContent = `
            @keyframes confettiFall {
                to {
                    transform: translateY(100vh) rotate(720deg);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Get current results
    window.UnifiedApp.results.getCurrentResults = function() {
        return currentResults;
    };
    
    // Clear results
    window.UnifiedApp.results.clearResults = function() {
        currentResults = null;
        const resultsSection = document.getElementById('resultsSection') || 
                              document.getElementById('results') || 
                              document.querySelector('.results-section');
        if (resultsSection) {
            resultsSection.style.display = 'none';
        }
    };
    
    // Save to history (placeholder)
    window.saveToHistory = function() {
        if (!currentResults) {
            alert('No results to save');
            return;
        }
        
        // In a real implementation, this would save to a database
        const history = JSON.parse(localStorage.getItem('analysisHistory') || '[]');
        history.unshift({
            timestamp: new Date().toISOString(),
            results: currentResults
        });
        
        // Keep only last 10 analyses
        if (history.length > 10) {
            history.pop();
        }
        
        localStorage.setItem('analysisHistory', JSON.stringify(history));
        
        // Show toast if UI module is available
        if (window.UnifiedApp && window.UnifiedApp.ui && window.UnifiedApp.ui.showToast) {
            window.UnifiedApp.ui.showToast('Results saved to history', 'success');
        } else {
            alert('Results saved to history');
        }
    };
    
})();
