// Image Results Display Module
window.ImageApp = window.ImageApp || {};

window.ImageApp.results = (function() {
    'use strict';

    // Display analysis results
    function displayResults(results) {
        console.log('Displaying image analysis results:', results);

        const resultsSection = document.getElementById('resultsSection');
        if (!resultsSection) return;

        // Clear previous results
        resultsSection.innerHTML = '';

        // Create results container
        const resultsContainer = createResultsContainer(results);
        resultsSection.appendChild(resultsContainer);

        // Show results section
        window.ImageApp.ui.showResults();

        // Animate trust meter
        setTimeout(() => {
            animateTrustMeter(results.trustScore);
        }, 100);

        // Initialize result interactions
        initializeResultInteractions();
    }

    // Create main results container
    function createResultsContainer(results) {
        const container = document.createElement('div');
        container.className = 'results-container';
        container.innerHTML = `
            <div class="results-header">
                <h2>Image Analysis Complete</h2>
                <div class="results-actions">
                    <button onclick="window.shareImageResults()" class="action-btn">
                        <i class="fas fa-share-alt"></i> Share
                    </button>
                    <button onclick="window.downloadImagePDF()" class="action-btn">
                        <i class="fas fa-file-pdf"></i> Download PDF
                    </button>
                    <button onclick="window.resetImageAnalysis()" class="action-btn secondary">
                        <i class="fas fa-redo"></i> New Analysis
                    </button>
                </div>
            </div>

            <div class="trust-score-section">
                ${createTrustMeter(results)}
                ${createVerdictBadge(results)}
            </div>

            <div class="analysis-sections">
                ${createAIDetectionSection(results.aiGenerated)}
                ${createManipulationSection(results.manipulation)}
                ${createMetadataSection(results.metadata)}
                ${createForensicsSection(results.forensics)}
                ${createVisualAnalysisSection(results.visualAnalysis)}
                ${createTechnicalDetailsSection(results.technicalDetails)}
                ${createKeyFindingsSection(results)}
                ${createRecommendationsSection(results)}
                ${createMethodologySection()}
                ${createConfidenceSection(results)}
            </div>
        `;
        return container;
    }

    // Create trust meter visualization
    function createTrustMeter(results) {
        const trustClass = results.trustScore >= 80 ? 'high' : 
                          results.trustScore >= 60 ? 'medium' : 
                          results.trustScore >= 40 ? 'low' : 'very-low';

        return `
            <div class="trust-meter-container">
                <svg class="trust-meter" width="250" height="250" viewBox="0 0 250 250">
                    <defs>
                        <linearGradient id="trustGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#667eea" />
                            <stop offset="100%" style="stop-color:#764ba2" />
                        </linearGradient>
                    </defs>
                    
                    <!-- Background circle -->
                    <circle cx="125" cy="125" r="110" fill="none" stroke="#e2e8f0" stroke-width="20" />
                    
                    <!-- Progress circle -->
                    <circle class="trust-progress" cx="125" cy="125" r="110" fill="none" 
                            stroke="url(#trustGradient)" stroke-width="20"
                            stroke-linecap="round" transform="rotate(-90 125 125)"
                            stroke-dasharray="691.15" stroke-dashoffset="691.15" />
                    
                    <!-- Center content -->
                    <text x="125" y="115" text-anchor="middle" class="trust-score-text">
                        <tspan class="score-number">${results.trustScore}</tspan>
                        <tspan class="score-percent" dx="5">%</tspan>
                    </text>
                    <text x="125" y="145" text-anchor="middle" class="trust-label">
                        Authenticity Score
                    </text>
                </svg>
                
                <div class="trust-description ${trustClass}">
                    <i class="fas ${getVerdictIcon(results.verdict)}"></i>
                    <span>${getTrustDescription(results.trustScore)}</span>
                </div>
            </div>
        `;
    }

    // Create verdict badge
    function createVerdictBadge(results) {
        const verdictClass = results.verdict.toLowerCase().replace(' ', '-');
        return `
            <div class="verdict-badge ${verdictClass}">
                <i class="fas ${getVerdictIcon(results.verdict)}"></i>
                <div class="verdict-content">
                    <h3>${results.verdict}</h3>
                    <p>Confidence: ${results.confidence}%</p>
                </div>
            </div>
        `;
    }

    // Create AI detection section
    function createAIDetectionSection(aiData) {
        const statusClass = aiData.detected ? 'detected' : 'not-detected';
        const borderColor = aiData.detected ? '#ef4444' : '#10b981';

        return createSection(
            'AI Generation Analysis',
            'fa-robot',
            `
                <div class="detection-status ${statusClass}">
                    <i class="fas ${aiData.detected ? 'fa-exclamation-triangle' : 'fa-check-circle'}"></i>
                    <span>${aiData.detected ? 'AI Generation Detected' : 'No AI Generation Detected'}</span>
                </div>
                ${aiData.detected ? `
                    <div class="detection-details">
                        <div class="detail-item">
                            <strong>Suspected Model:</strong> ${aiData.model || 'Unknown'}
                        </div>
                        <div class="detail-item">
                            <strong>Confidence:</strong> ${aiData.confidence}%
                        </div>
                        <div class="indicators">
                            <h4>Key Indicators:</h4>
                            <ul>
                                ${aiData.indicators.map(indicator => `<li>${indicator}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                ` : '<p>This image appears to be captured by a real camera or created through traditional means.</p>'}
            `,
            borderColor
        );
    }

    // Create manipulation section
    function createManipulationSection(manipData) {
        const statusClass = manipData.detected ? 'detected' : 'not-detected';
        const borderColor = manipData.detected ? '#f59e0b' : '#10b981';

        return createSection(
            'Digital Manipulation Check',
            'fa-cut',
            `
                <div class="detection-status ${statusClass}">
                    <i class="fas ${manipData.detected ? 'fa-exclamation-circle' : 'fa-check-circle'}"></i>
                    <span>${manipData.detected ? 'Manipulation Detected' : 'No Manipulation Detected'}</span>
                </div>
                ${manipData.detected && manipData.edits.length > 0 ? `
                    <div class="edit-list">
                        <h4>Detected Edits:</h4>
                        <ul>
                            ${manipData.edits.map(edit => `<li>${edit}</li>`).join('')}
                        </ul>
                    </div>
                ` : '<p>No signs of digital editing, cropping, or manipulation found in this image.</p>'}
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${100 - manipData.confidence}%"></div>
                    <span class="confidence-label">Authenticity: ${100 - manipData.confidence}%</span>
                </div>
            `,
            borderColor
        );
    }

    // Create metadata section
    function createMetadataSection(metadata) {
        const borderColor = metadata.suspicious.length > 0 ? '#f59e0b' : '#3b82f6';

        return createSection(
            'Metadata Analysis',
            'fa-database',
            `
                <div class="metadata-grid">
                    <div class="metadata-item">
                        <i class="fas fa-camera"></i>
                        <div>
                            <strong>Camera Info:</strong>
                            <span>${metadata.hasExif ? 'Available' : 'Not Available'}</span>
                        </div>
                    </div>
                    <div class="metadata-item">
                        <i class="fas fa-desktop"></i>
                        <div>
                            <strong>Software:</strong>
                            <span>${metadata.software || 'Unknown'}</span>
                        </div>
                    </div>
                    <div class="metadata-item">
                        <i class="fas fa-calendar"></i>
                        <div>
                            <strong>Created:</strong>
                            <span>${metadata.created || 'Unknown'}</span>
                        </div>
                    </div>
                    <div class="metadata-item">
                        <i class="fas fa-edit"></i>
                        <div>
                            <strong>Modified:</strong>
                            <span>${metadata.modified || 'Unknown'}</span>
                        </div>
                    </div>
                </div>
                ${metadata.suspicious.length > 0 ? `
                    <div class="suspicious-items">
                        <h4><i class="fas fa-exclamation-triangle"></i> Suspicious Findings:</h4>
                        <ul>
                            ${metadata.suspicious.map(item => `<li>${item}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            `,
            borderColor
        );
    }

    // Create forensics section
    function createForensicsSection(forensics) {
        return createSection(
            'Forensic Examination',
            'fa-microscope',
            `
                <div class="forensics-grid">
                    <div class="forensic-item">
                        <h4>Compression Analysis</h4>
                        <p>${forensics.compression}</p>
                    </div>
                    <div class="forensic-item">
                        <h4>Clone Detection</h4>
                        <p>${forensics.cloning ? 'Cloning detected' : 'No cloning detected'}</p>
                    </div>
                    <div class="forensic-item">
                        <h4>Splicing Check</h4>
                        <p>${forensics.splicing ? 'Splicing detected' : 'No splicing detected'}</p>
                    </div>
                </div>
                ${forensics.artifacts.length > 0 ? `
                    <div class="artifacts-list">
                        <h4>Detected Artifacts:</h4>
                        <ul>
                            ${forensics.artifacts.map(artifact => `<li>${artifact}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            `,
            '#8b5cf6'
        );
    }

    // Create visual analysis section
    function createVisualAnalysisSection(visual) {
        return createSection(
            'Visual Consistency Analysis',
            'fa-eye',
            `
                <div class="visual-grid">
                    <div class="visual-check">
                        <i class="fas fa-sun"></i>
                        <div>
                            <strong>Lighting:</strong>
                            <p>${visual.lighting}</p>
                        </div>
                    </div>
                    <div class="visual-check">
                        <i class="fas fa-moon"></i>
                        <div>
                            <strong>Shadows:</strong>
                            <p>${visual.shadows}</p>
                        </div>
                    </div>
                    <div class="visual-check">
                        <i class="fas fa-cube"></i>
                        <div>
                            <strong>Perspective:</strong>
                            <p>${visual.perspective}</p>
                        </div>
                    </div>
                    <div class="visual-check">
                        <i class="fas fa-th"></i>
                        <div>
                            <strong>Textures:</strong>
                            <p>${visual.textures}</p>
                        </div>
                    </div>
                </div>
            `,
            '#06b6d4'
        );
    }

    // Create technical details section
    function createTechnicalDetailsSection(technical) {
        return createSection(
            'Technical Information',
            'fa-info-circle',
            `
                <div class="tech-details-grid">
                    <div class="tech-detail">
                        <span class="label">Resolution:</span>
                        <span class="value">${technical.resolution}</span>
                    </div>
                    <div class="tech-detail">
                        <span class="label">Color Space:</span>
                        <span class="value">${technical.colorSpace}</span>
                    </div>
                    <div class="tech-detail">
                        <span class="label">Bit Depth:</span>
                        <span class="value">${technical.bitDepth}</span>
                    </div>
                    <div class="tech-detail">
                        <span class="label">File Size:</span>
                        <span class="value">${technical.fileSize}</span>
                    </div>
                    <div class="tech-detail">
                        <span class="label">Format:</span>
                        <span class="value">${technical.format}</span>
                    </div>
                </div>
            `,
            '#6b7280'
        );
    }

    // Create key findings section
    function createKeyFindingsSection(results) {
        const findings = generateKeyFindings(results);
        
        return createSection(
            'Key Findings Summary',
            'fa-clipboard-check',
            `
                <div class="key-findings">
                    ${findings.map(finding => `
                        <div class="finding-item ${finding.type}">
                            <i class="fas ${finding.icon}"></i>
                            <span>${finding.text}</span>
                        </div>
                    `).join('')}
                </div>
            `,
            '#f59e0b',
            true // highlight section
        );
    }

    // Create recommendations section
    function createRecommendationsSection(results) {
        const recommendations = generateRecommendations(results);
        
        return createSection(
            'Recommendations',
            'fa-lightbulb',
            `
                <div class="recommendations-list">
                    ${recommendations.map(rec => `
                        <div class="recommendation">
                            <i class="fas fa-chevron-right"></i>
                            <span>${rec}</span>
                        </div>
                    `).join('')}
                </div>
            `,
            '#10b981'
        );
    }

    // Create methodology section
    function createMethodologySection() {
        return createSection(
            'Analysis Methodology',
            'fa-flask',
            `
                <div class="methodology-content">
                    <p>This analysis used multiple AI models and forensic techniques:</p>
                    <div class="method-grid">
                        <div class="method-item">
                            <i class="fas fa-brain"></i>
                            <span>Deep Learning Models</span>
                        </div>
                        <div class="method-item">
                            <i class="fas fa-search-plus"></i>
                            <span>Pixel-level Analysis</span>
                        </div>
                        <div class="method-item">
                            <i class="fas fa-fingerprint"></i>
                            <span>Digital Fingerprinting</span>
                        </div>
                        <div class="method-item">
                            <i class="fas fa-chart-line"></i>
                            <span>Statistical Analysis</span>
                        </div>
                    </div>
                </div>
            `,
            '#7c3aed',
            false,
            'methodology'
        );
    }

    // Create confidence section
    function createConfidenceSection(results) {
        return createSection(
            'Confidence & Limitations',
            'fa-chart-bar',
            `
                <div class="confidence-overview">
                    <div class="overall-confidence">
                        <h4>Overall Analysis Confidence</h4>
                        <div class="confidence-meter">
                            <div class="confidence-bar-fill" style="width: ${results.confidence}%"></div>
                            <span class="confidence-value">${results.confidence}%</span>
                        </div>
                    </div>
                    <div class="limitations">
                        <h4>Important Limitations</h4>
                        <ul>
                            <li>AI detection is probabilistic, not absolute</li>
                            <li>New generation techniques may evade detection</li>
                            <li>Some edits may be too subtle to detect</li>
                            <li>Results should be considered alongside other evidence</li>
                        </ul>
                    </div>
                </div>
            `,
            '#9333ea'
        );
    }

    // Helper function to create sections
    function createSection(title, icon, content, borderColor = '#667eea', highlight = false, className = '') {
        return `
            <div class="analysis-section ${highlight ? 'highlight' : ''} ${className}" 
                 style="border-left-color: ${borderColor}">
                <div class="section-header" onclick="window.ImageApp.results.toggleSection(this)">
                    <div class="section-title">
                        <i class="fas ${icon}"></i>
                        <h3>${title}</h3>
                    </div>
                    <i class="fas fa-chevron-down toggle-icon"></i>
                </div>
                <div class="section-content">
                    ${content}
                </div>
            </div>
        `;
    }

    // Generate key findings based on results
    function generateKeyFindings(results) {
        const findings = [];

        if (results.aiGenerated.detected) {
            findings.push({
                type: 'warning',
                icon: 'fa-exclamation-triangle',
                text: `High probability (${results.aiGenerated.confidence}%) this is an AI-generated image`
            });
        }

        if (results.manipulation.detected) {
            findings.push({
                type: 'warning',
                icon: 'fa-cut',
                text: 'Digital manipulation or editing detected'
            });
        }

        if (!results.metadata.hasExif) {
            findings.push({
                type: 'info',
                icon: 'fa-info-circle',
                text: 'No camera metadata found (common for screenshots or AI images)'
            });
        }

        if (results.trustScore < 20) {
            findings.push({
                type: 'danger',
                icon: 'fa-times-circle',
                text: 'Very low authenticity score - treat with extreme caution'
            });
        } else if (results.trustScore > 80) {
            findings.push({
                type: 'success',
                icon: 'fa-check-circle',
                text: 'High authenticity score - likely genuine'
            });
        }

        return findings;
    }

    // Generate recommendations based on results
    function generateRecommendations(results) {
        const recommendations = [];

        if (results.aiGenerated.detected) {
            recommendations.push('Verify the source before using this image');
            recommendations.push('Check if AI-generated content is disclosed');
            recommendations.push('Consider the context where this image appeared');
        }

        if (results.manipulation.detected) {
            recommendations.push('Look for the original, unedited version');
            recommendations.push('Be cautious about drawing conclusions from this image');
        }

        if (results.trustScore < 50) {
            recommendations.push('Seek additional verification before sharing');
            recommendations.push('Cross-reference with trusted sources');
        }

        if (recommendations.length === 0) {
            recommendations.push('This image appears authentic based on our analysis');
            recommendations.push('Always consider context when evaluating images');
        }

        return recommendations;
    }

    // Get verdict icon
    function getVerdictIcon(verdict) {
        const iconMap = {
            'AI Generated': 'fa-robot',
            'Likely Authentic': 'fa-check-circle',
            'Possibly Manipulated': 'fa-exclamation-triangle',
            'Heavily Edited': 'fa-cut',
            'Inconclusive': 'fa-question-circle'
        };
        return iconMap[verdict] || 'fa-question-circle';
    }

    // Get trust description
    function getTrustDescription(score) {
        if (score >= 80) return 'This image appears to be authentic';
        if (score >= 60) return 'Mostly authentic with minor concerns';
        if (score >= 40) return 'Significant authenticity concerns detected';
        if (score >= 20) return 'Strong indicators of AI generation or manipulation';
        return 'Very likely AI-generated or heavily manipulated';
    }

    // Animate trust meter
    function animateTrustMeter(score) {
        const circle = document.querySelector('.trust-progress');
        if (!circle) return;

        const circumference = 2 * Math.PI * 110;
        const offset = circumference - (score / 100) * circumference;

        setTimeout(() => {
            circle.style.strokeDashoffset = offset;
            circle.style.transition = 'stroke-dashoffset 2s ease-out';
        }, 100);
    }

    // Toggle section expansion
    window.ImageApp.results.toggleSection = function(header) {
        const section = header.parentElement;
        const isExpanded = section.classList.contains('expanded');
        
        // Toggle expanded state
        if (isExpanded) {
            section.classList.remove('expanded');
        } else {
            section.classList.add('expanded');
        }
    };

    // Initialize result interactions
    function initializeResultInteractions() {
        // Auto-expand first few sections
        const sections = document.querySelectorAll('.analysis-section');
        sections.forEach((section, index) => {
            if (index < 3) {
                section.classList.add('expanded');
            }
        });

        // Add hover effects
        const findings = document.querySelectorAll('.finding-item');
        findings.forEach(finding => {
            finding.addEventListener('mouseenter', function() {
                this.style.transform = 'translateX(5px)';
            });
            finding.addEventListener('mouseleave', function() {
                this.style.transform = 'translateX(0)';
            });
        });
    }

    // Export public methods
    return {
        displayResults: displayResults
    };
})();

// Add required styles
const resultsStyle = document.createElement('style');
resultsStyle.textContent = `
    /* Results Container */
    .results-container {
        max-width: 1000px;
        margin: 0 auto;
        padding: 40px 20px;
    }

    .results-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 40px;
        flex-wrap: wrap;
        gap: 20px;
    }

    .results-header h2 {
        font-size: 32px;
        color: #1a202c;
        margin: 0;
    }

    .results-actions {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
    }

    .action-btn {
        padding: 10px 20px;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 8px;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    .action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    .action-btn.secondary {
        background: #718096;
    }

    .action-btn.secondary:hover {
        background: #4a5568;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    /* Trust Score Section */
    .trust-score-section {
        display: flex;
        justify-content: space-around;
        align-items: center;
        margin-bottom: 60px;
        flex-wrap: wrap;
        gap: 40px;
    }

    .trust-meter-container {
        text-align: center;
    }

    .trust-meter .trust-score-text {
        fill: #1a202c;
    }

    .trust-meter .score-number {
        font-size: 48px;
        font-weight: bold;
    }

    .trust-meter .score-percent {
        font-size: 24px;
    }

    .trust-meter .trust-label {
        fill: #718096;
        font-size: 16px;
    }

    .trust-description {
        margin-top: 20px;
        padding: 12px 24px;
        border-radius: 25px;
        display: inline-flex;
        align-items: center;
        gap: 10px;
        font-weight: 500;
    }

    .trust-description.high {
        background: #d1fae5;
        color: #065f46;
    }

    .trust-description.medium {
        background: #fed7aa;
        color: #9a3412;
    }

    .trust-description.low {
        background: #fee2e2;
        color: #991b1b;
    }

    .trust-description.very-low {
        background: #fce7f3;
        color: #9f1239;
    }

    /* Verdict Badge */
    .verdict-badge {
        padding: 30px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        gap: 20px;
    }

    .verdict-badge i {
        font-size: 48px;
    }

    .verdict-badge.ai-generated {
        border-left: 5px solid #ef4444;
    }

    .verdict-badge.ai-generated i {
        color: #ef4444;
    }

    .verdict-badge.likely-authentic {
        border-left: 5px solid #10b981;
    }

    .verdict-badge.likely-authentic i {
        color: #10b981;
    }

    .verdict-content h3 {
        margin: 0 0 8px 0;
        font-size: 24px;
        color: #1a202c;
    }

    .verdict-content p {
        margin: 0;
        color: #718096;
    }

    /* Analysis Sections */
    .analysis-sections {
        display: flex;
        flex-direction: column;
        gap: 20px;
    }

    .analysis-section {
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #667eea;
        overflow: hidden;
        transition: all 0.3s ease;
    }

    .analysis-section:hover {
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }

    .analysis-section.highlight {
        background: #fffbeb;
    }

    .section-header {
        padding: 20px 25px;
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: background 0.3s ease;
    }

    .section-header:hover {
        background: #f8fafc;
    }

    .section-title {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .section-title i {
        font-size: 24px;
        color: #667eea;
    }

    .section-title h3 {
        margin: 0;
        font-size: 20px;
        color: #1a202c;
    }

    .toggle-icon {
        color: #718096;
        transition: transform 0.3s ease;
    }

    .analysis-section.expanded .toggle-icon {
        transform: rotate(180deg);
    }

    .section-content {
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.3s ease;
    }

    .analysis-section.expanded .section-content {
        max-height: 2000px;
        padding: 0 25px 25px;
    }

    /* Detection Status */
    .detection-status {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        font-weight: 500;
    }

    .detection-status.detected {
        background: #fee2e2;
        color: #991b1b;
    }

    .detection-status.not-detected {
        background: #d1fae5;
        color: #065f46;
    }

    .detection-status i {
        font-size: 20px;
    }

    /* Various Grid Layouts */
    .metadata-grid,
    .forensics-grid,
    .visual-grid,
    .tech-details-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin-top: 20px;
    }

    .metadata-item,
    .forensic-item,
    .visual-check {
        display: flex;
        align-items: flex-start;
        gap: 15px;
        padding: 15px;
        background: #f8fafc;
        border-radius: 8px;
    }

    .metadata-item i,
    .visual-check i {
        font-size: 24px;
        color: #667eea;
        margin-top: 3px;
    }

    /* Confidence Bar */
    .confidence-bar {
        margin-top: 20px;
        height: 30px;
        background: #e2e8f0;
        border-radius: 15px;
        overflow: hidden;
        position: relative;
    }

    .confidence-fill {
        height: 100%;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        transition: width 1s ease;
    }

    .confidence-label {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-weight: 500;
        color: #1a202c;
    }

    /* Key Findings */
    .key-findings {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }

    .finding-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        border-radius: 8px;
        transition: transform 0.3s ease;
    }

    .finding-item.warning {
        background: #fed7aa;
        color: #9a3412;
    }

    .finding-item.danger {
        background: #fee2e2;
        color: #991b1b;
    }

    .finding-item.success {
        background: #d1fae5;
        color: #065f46;
    }

    .finding-item.info {
        background: #dbeafe;
        color: #1e3a8a;
    }

    /* Recommendations */
    .recommendations-list {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    .recommendation {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        padding: 10px;
        background: #f0fdf4;
        border-radius: 6px;
        line-height: 1.6;
    }

    .recommendation i {
        color: #10b981;
        margin-top: 3px;
    }

    /* Methodology */
    .method-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin-top: 20px;
    }

    .method-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px;
        background: #ede9fe;
        border-radius: 8px;
        color: #5b21b6;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .results-header {
            flex-direction: column;
            align-items: flex-start;
        }

        .trust-score-section {
            flex-direction: column;
        }

        .verdict-badge {
            width: 100%;
        }
    }
`;
document.head.appendChild(resultsStyle);
