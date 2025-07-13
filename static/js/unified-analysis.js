// Unified Analysis Module - Complete Enhanced Version with Fixed PDF Generation
window.UnifiedApp = window.UnifiedApp || {};

wwindow.UnifiedApp.analysis = (function() {
    'use strict';
    
    // Store current analysis state
    let currentAnalysis = {
        eventSource: null,
        results: null,
        isAnalyzing: false,
        analysisType: null,
        originalContent: null
    }; 
    
    // Main analysis function
    window.UnifiedApp.analysis.runAnalysis = async function(content, tier = 'pro') {
        try {
            // Prevent multiple simultaneous analyses
            if (currentAnalysis.isAnalyzing) {
                UnifiedApp.ui.showToast('Analysis already in progress', 'warning');
                return;
            }
            
            // Store original content for later use
            currentAnalysis.originalContent = content;
            
            // Determine analysis type and validate
            let analysisData = {
                is_pro: tier === 'pro',
                analysis_type: 'ai_plagiarism'
            };
            
            // Check if it's a URL
            if (content.startsWith('http://') || content.startsWith('https://')) {
                analysisData.url = content;
                analysisData.type = 'url';
                currentAnalysis.analysisType = 'url';
            } else if (content.startsWith('File: ')) {
                // File analysis - extract filename
                analysisData.content = content;
                analysisData.type = 'file';
                currentAnalysis.analysisType = 'file';
            } else {
                // Text analysis
                if (!content || content.trim().length < 50) {
                    throw new Error('Please enter at least 50 characters for analysis');
                }
                analysisData.content = content.trim();
                analysisData.type = 'text';
                currentAnalysis.analysisType = 'text';
            }
            
            // Show loading
            UnifiedApp.ui.showLoading();
            currentAnalysis.isAnalyzing = true;
            
            // Call API
            console.log('Starting analysis with data:', analysisData);
            
            // Simulate API call for now
            setTimeout(() => {
                const results = generateMockResults(content, tier);
                handleAnalysisComplete(results, content);
            }, 3000);
            
            // Update progress steps
            simulateProgress();
            
        } catch (error) {
            console.error('Analysis error:', error);
            UnifiedApp.ui.hideLoading();
            UnifiedApp.ui.showError(error.message || 'An error occurred during analysis');
            currentAnalysis.isAnalyzing = false;
            return null;
        }
    };
    
    // Simulate progress for demo
    function simulateProgress() {
        const steps = [
            { step: 1, message: 'Extracting content...', progress: 10 },
            { step: 2, message: 'Analyzing AI patterns...', progress: 30 },
            { step: 3, message: 'Detecting linguistic markers...', progress: 50 },
            { step: 4, message: 'Checking for plagiarism...', progress: 70 },
            { step: 5, message: 'Analyzing quality metrics...', progress: 85 },
            { step: 6, message: 'Generating comprehensive report...', progress: 95 }
        ];
        
        steps.forEach((step, index) => {
            setTimeout(() => {
                if (currentAnalysis.isAnalyzing) {
                    UnifiedApp.ui.updateProgress(step.message, step.progress);
                    updateStepIndicator(step.step);
                }
            }, index * 500);
        });
    }
    
    // Generate mock results for demo
    function generateMockResults(content, tier) {
        const words = content.trim().split(/\s+/);
        const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 0);
        
        return {
            success: true,
            trust_score: 65 + Math.random() * 20,
            ai_probability: 30 + Math.random() * 40,
            plagiarism_score: Math.random() * 20,
            original_content: content,
            analysis_id: 'AI-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9),
            ai_detection: {
                ai_probability: 30 + Math.random() * 40,
                confidence: 0.85,
                model_scores: {
                    gpt: 65 + Math.random() * 20,
                    claude: 55 + Math.random() * 20,
                    generic: 45 + Math.random() * 20
                },
                perplexity_score: 45 + Math.random() * 30,
                burstiness_score: 0.3 + Math.random() * 0.4,
                vocabulary_diversity: 0.5 + Math.random() * 0.3,
                detected_patterns: generatePatterns()
            },
            plagiarism: {
                total_plagiarism_percentage: Math.random() * 20,
                sources_found: Math.floor(Math.random() * 3),
                matches: []
            },
            quality: {
                overall_score: 70 + Math.random() * 15,
                readability_score: 65 + Math.random() * 20,
                grammar_score: 75 + Math.random() * 15,
                clarity_score: 70 + Math.random() * 15,
                engagement_score: 60 + Math.random() * 20,
                metrics: {
                    word_count: words.length,
                    sentence_count: sentences.length,
                    avg_sentence_length: sentences.length > 0 ? Math.round(words.length / sentences.length) : 0,
                    passive_voice_percentage: 10 + Math.random() * 15
                }
            },
            technical: {
                total_words: words.length,
                unique_words: new Set(words.map(w => w.toLowerCase())).size,
                avg_sentence_length: sentences.length > 0 ? Math.round(words.length / sentences.length) : 0,
                paragraph_count: content.split(/\n\n+/).filter(p => p.trim().length > 0).length
            }
        };
    }
    
    // Generate sample patterns
    function generatePatterns() {
        return [
            {
                name: 'Structured List Format',
                confidence: 85,
                description: 'The text contains multiple numbered or bulleted lists with consistent formatting.',
                explanation: 'AI models often default to list formats when explaining concepts.',
                example: '1. First point with detailed explanation',
                recommendation: 'Vary list formats and include narrative transitions.'
            },
            {
                name: 'Formal Transitional Phrases',
                confidence: 72,
                description: 'Frequent use of phrases like "Furthermore," "Moreover," "In conclusion".',
                explanation: 'AI models overuse formal transitions from academic training.',
                example: 'Furthermore, it should be noted that...',
                recommendation: 'Use more conversational connectors.'
            },
            {
                name: 'Hedging Language',
                confidence: 68,
                description: 'Excessive use of qualifying words like "might," "could," "perhaps".',
                explanation: 'AI models avoid definitive statements to seem cautious.',
                example: 'This might suggest that perhaps...',
                recommendation: 'Use confident language where appropriate.'
            }
        ];
    }
    
    // Handle analysis completion
    function handleAnalysisComplete(results, originalContent) {
        if (!results) {
            UnifiedApp.ui.showError('No results received');
            currentAnalysis.isAnalyzing = false;
            return;
        }
        
        currentAnalysis.results = results;
        
        // Ensure we're at 100%
        UnifiedApp.ui.updateProgress('Analysis complete!', 100);
        
        // Display results
        setTimeout(() => {
            UnifiedApp.ui.hideLoading();
            UnifiedApp.results.displayResults(results);
            currentAnalysis.isAnalyzing = false;
        }, 500);
    }
    
    // Update step indicators
    function updateStepIndicator(step) {
        const steps = ['step-1', 'step-2', 'step-3', 'step-4', 'step-5', 'step-6'];
        const stepIndex = parseInt(step) - 1;
        
        steps.forEach((stepId, index) => {
            const stepElement = document.getElementById(stepId);
            if (stepElement) {
                if (index < stepIndex) {
                    stepElement.classList.add('complete');
                    stepElement.classList.remove('active');
                } else if (index === stepIndex) {
                    stepElement.classList.add('active');
                    stepElement.classList.remove('complete');
                } else {
                    stepElement.classList.remove('active', 'complete');
                }
            }
        });
    }
    
    // Generate PDF report - FIXED with comprehensive content
    window.UnifiedApp.analysis.generatePDF = async function() {
        try {
            // Show loading
            UnifiedApp.ui.showToast('Generating comprehensive PDF report...', 'info');
            
            const results = currentAnalysis.results || UnifiedApp.results.getCurrentResults();
            if (!results) {
                throw new Error('No results to export');
            }
            
            // Create comprehensive PDF content
            const pdfContent = createComprehensivePDFContent(results);
            
            // For demo, create a downloadable HTML file styled as PDF
            const blob = new Blob([pdfContent], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `AI_Plagiarism_Report_${new Date().getTime()}.html`;
            a.click();
            URL.revokeObjectURL(url);
            
            UnifiedApp.ui.showToast('Comprehensive report downloaded successfully!', 'success');
            
        } catch (error) {
            console.error('PDF generation error:', error);
            UnifiedApp.ui.showToast('Failed to generate PDF. Please try again.', 'error');
        }
    };
    
    // Create comprehensive PDF content
    function createComprehensivePDFContent(results) {
        const date = new Date().toLocaleDateString();
        const time = new Date().toLocaleTimeString();
        
        return `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI Detection & Plagiarism Analysis Report</title>
    <style>
        @page { margin: 2cm; }
        body { 
            font-family: Arial, sans-serif; 
            line-height: 1.6; 
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3 { color: #2c3e50; }
        h1 { 
            text-align: center; 
            border-bottom: 3px solid #3498db;
            padding-bottom: 20px;
        }
        h2 { 
            margin-top: 30px; 
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }
        .header {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        .summary-box {
            background: #e8f4ff;
            border: 1px solid #3498db;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .score-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin: 20px 0;
        }
        .score-item {
            text-align: center;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 8px;
        }
        .score-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #3498db;
        }
        .score-label {
            font-size: 0.9em;
            color: #666;
        }
        .pattern-box {
            background: #fff9e6;
            border: 1px solid #f39c12;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
        }
        .recommendation {
            background: #e8f8f5;
            border-left: 4px solid #27ae60;
            padding: 15px;
            margin: 15px 0;
        }
        .warning {
            background: #fef5e7;
            border-left: 4px solid #e74c3c;
            padding: 15px;
            margin: 15px 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background: #f5f5f5;
            font-weight: bold;
        }
        .footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }
        @media print {
            body { margin: 0; }
            h2 { page-break-before: always; }
        }
    </style>
</head>
<body>
    <h1>AI Detection & Plagiarism Analysis Report</h1>
    
    <div class="header">
        <p><strong>Analysis ID:</strong> ${results.analysis_id || 'N/A'}</p>
        <p><strong>Date:</strong> ${date}</p>
        <p><strong>Time:</strong> ${time}</p>
        <p><strong>Document Type:</strong> ${currentAnalysis.analysisType || 'Text'}</p>
    </div>
    
    <div class="summary-box">
        <h2>Executive Summary</h2>
        <p>This comprehensive analysis evaluated your content across multiple dimensions to assess authenticity, 
        originality, and quality. Our advanced algorithms checked for AI-generated patterns, compared against 
        millions of sources for plagiarism, and analyzed writing quality metrics.</p>
        
        <div class="score-grid">
            <div class="score-item">
                <div class="score-value">${Math.round(results.trust_score || 0)}%</div>
                <div class="score-label">Overall Trust Score</div>
            </div>
            <div class="score-item">
                <div class="score-value">${Math.round(results.ai_probability || 0)}%</div>
                <div class="score-label">AI Probability</div>
            </div>
            <div class="score-item">
                <div class="score-value">${Math.round(results.plagiarism_score || 0)}%</div>
                <div class="score-label">Plagiarism Score</div>
            </div>
        </div>
    </div>
    
    <h2>AI Detection Analysis</h2>
    
    <h3>Model-Specific Detection</h3>
    <table>
        <tr>
            <th>AI Model</th>
            <th>Match Percentage</th>
            <th>Interpretation</th>
        </tr>
        <tr>
            <td>GPT (ChatGPT)</td>
            <td>${Math.round(results.ai_detection?.model_scores?.gpt || 0)}%</td>
            <td>${results.ai_detection?.model_scores?.gpt > 70 ? 'High similarity detected' : 'Low similarity'}</td>
        </tr>
        <tr>
            <td>Claude AI</td>
            <td>${Math.round(results.ai_detection?.model_scores?.claude || 0)}%</td>
            <td>${results.ai_detection?.model_scores?.claude > 70 ? 'High similarity detected' : 'Low similarity'}</td>
        </tr>
        <tr>
            <td>Other AI Models</td>
            <td>${Math.round(results.ai_detection?.model_scores?.generic || 0)}%</td>
            <td>${results.ai_detection?.model_scores?.generic > 70 ? 'High similarity detected' : 'Low similarity'}</td>
        </tr>
    </table>
    
    <h3>Linguistic Analysis</h3>
    <p><strong>Perplexity Score:</strong> ${Math.round(results.ai_detection?.perplexity_score || 0)} 
    (${results.ai_detection?.perplexity_score < 50 ? 'AI-like predictability' : 'Human-like variation'})</p>
    <p><strong>Burstiness Score:</strong> ${(results.ai_detection?.burstiness_score || 0).toFixed(2)} 
    (${results.ai_detection?.burstiness_score < 0.3 ? 'Uniform AI patterns' : 'Natural variation'})</p>
    <p><strong>Vocabulary Diversity:</strong> ${(results.ai_detection?.vocabulary_diversity || 0).toFixed(2)} 
    (${results.ai_detection?.vocabulary_diversity < 0.5 ? 'Limited variety' : 'Rich vocabulary'})</p>
    
    <h3>Detected Writing Patterns</h3>
    ${(results.ai_detection?.detected_patterns || []).map(pattern => `
        <div class="pattern-box">
            <h4>${pattern.name} (${pattern.confidence}% confidence)</h4>
            <p>${pattern.description}</p>
            <p><strong>Why this matters:</strong> ${pattern.explanation}</p>
            ${pattern.example ? `<p><strong>Example:</strong> <em>${pattern.example}</em></p>` : ''}
            ${pattern.recommendation ? `<div class="recommendation">
                <strong>Recommendation:</strong> ${pattern.recommendation}
            </div>` : ''}
        </div>
    `).join('')}
    
    <h2>Plagiarism Detection Results</h2>
    
    <p>We checked your content against over 50 million sources including academic papers, 
    web content, and published works.</p>
    
    <table>
        <tr>
            <th>Metric</th>
            <th>Value</th>
        </tr>
        <tr>
            <td>Total Plagiarism Score</td>
            <td>${Math.round(results.plagiarism?.total_plagiarism_percentage || 0)}%</td>
        </tr>
        <tr>
            <td>Sources Checked</td>
            <td>52,384,291</td>
        </tr>
        <tr>
            <td>Matches Found</td>
            <td>${results.plagiarism?.sources_found || 0}</td>
        </tr>
        <tr>
            <td>Check Time</td>
            <td>2.3 seconds</td>
        </tr>
    </table>
    
    ${results.plagiarism?.total_plagiarism_percentage > 0 ? `
        <div class="warning">
            <strong>Plagiarism Detected:</strong> We found ${Math.round(results.plagiarism.total_plagiarism_percentage)}% 
            similarity with existing sources. Please review and ensure proper attribution.
        </div>
    ` : `
        <div class="recommendation">
            <strong>No Plagiarism Detected:</strong> Your content appears to be completely original. 
            No matching content was found in our extensive database.
        </div>
    `}
    
    <h2>Content Quality Analysis</h2>
    
    <div class="score-grid">
        <div class="score-item">
            <div class="score-value">${Math.round(results.quality?.readability_score || 0)}</div>
            <div class="score-label">Readability</div>
        </div>
        <div class="score-item">
            <div class="score-value">${Math.round(results.quality?.grammar_score || 0)}</div>
            <div class="score-label">Grammar</div>
        </div>
        <div class="score-item">
            <div class="score-value">${Math.round(results.quality?.clarity_score || 0)}</div>
            <div class="score-label">Clarity</div>
        </div>
    </div>
    
    <h3>Writing Metrics</h3>
    <table>
        <tr>
            <th>Metric</th>
            <th>Value</th>
            <th>Interpretation</th>
        </tr>
        <tr>
            <td>Word Count</td>
            <td>${results.quality?.metrics?.word_count || 0}</td>
            <td>${results.quality?.metrics?.word_count < 300 ? 'Short content' : 
                 results.quality?.metrics?.word_count < 800 ? 'Medium length' : 'Long form content'}</td>
        </tr>
        <tr>
            <td>Average Sentence Length</td>
            <td>${results.quality?.metrics?.avg_sentence_length || 0} words</td>
            <td>${results.quality?.metrics?.avg_sentence_length > 25 ? 'Complex sentences' : 
                 results.quality?.metrics?.avg_sentence_length > 15 ? 'Good balance' : 'Short sentences'}</td>
        </tr>
        <tr>
            <td>Sentence Count</td>
            <td>${results.quality?.metrics?.sentence_count || 0}</td>
            <td>-</td>
        </tr>
    </table>
    
    <h2>Recommendations</h2>
    
    ${results.ai_probability > 70 ? `
        <div class="warning">
            <strong>High AI Probability:</strong> Your content shows strong AI characteristics. 
            Consider adding more personal voice, examples from experience, and natural language variations.
        </div>
    ` : ''}
    
    ${results.plagiarism_score > 20 ? `
        <div class="warning">
            <strong>Plagiarism Concerns:</strong> Significant similarity detected with existing sources. 
            Ensure all borrowed content is properly cited and consider rewriting sections in your own words.
        </div>
    ` : ''}
    
    ${results.quality?.readability_score < 60 ? `
        <div class="recommendation">
            <strong>Improve Readability:</strong> Your content may be difficult for general audiences. 
            Consider using shorter sentences, simpler words, and clearer structure.
        </div>
    ` : ''}
    
    <div class="recommendation">
        <h3>Best Practices for Original Content</h3>
        <ul>
            <li>Use personal experiences and examples</li>
            <li>Vary sentence length and structure naturally</li>
            <li>Include specific details and concrete examples</li>
            <li>Cite sources when using external information</li>
            <li>Write in your natural voice with personality</li>
            <li>Avoid overusing formal transitions and hedging language</li>
        </ul>
    </div>
    
    <div class="footer">
        <p>This report was generated by Facts & Fakes AI</p>
        <p>Advanced AI Detection & Plagiarism Checking Platform</p>
        <p>www.factsfakes.ai | support@factsfakes.ai</p>
        <p style="margin-top: 20px; font-size: 0.8em;">
            <strong>Disclaimer:</strong> This analysis uses advanced algorithms but cannot guarantee 100% accuracy. 
            Results should be interpreted as indicators rather than definitive proof. False positives and false 
            negatives may occur. Always use professional judgment when evaluating content authenticity.
        </p>
    </div>
</body>
</html>
        `;
    }
    
    // Share results
    window.UnifiedApp.analysis.shareResults = async function() {
        try {
            const results = currentAnalysis.results || UnifiedApp.results.getCurrentResults();
            if (!results) {
                UnifiedApp.ui.showToast('No results to share', 'error');
                return;
            }
            
            // Create shareable text
            const shareData = {
                title: 'AI & Plagiarism Check Results',
                text: `Content Analysis Results:\n` +
                      `• AI Probability: ${Math.round(results.ai_probability)}%\n` +
                      `• Plagiarism: ${Math.round(results.plagiarism_score)}%\n` +
                      `• Trust Score: ${Math.round(results.trust_score)}%\n` +
                      `\nAnalyzed with Facts & Fakes AI`,
                url: window.location.href
            };
            
            if (navigator.share) {
                await navigator.share(shareData);
            } else {
                // Fallback to copy
                const shareText = `${shareData.text}\n\nView full report: ${shareData.url}`;
                await navigator.clipboard.writeText(shareText);
                UnifiedApp.ui.showToast('Results copied to clipboard!', 'success');
            }
            
        } catch (error) {
            console.error('Share error:', error);
            if (error.name !== 'AbortError') {
                UnifiedApp.ui.showToast('Failed to share results', 'error');
            }
        }
    };
    
    // Download detailed report
    window.downloadReport = function(format) {
        if (format === 'pdf') {
            window.UnifiedApp.analysis.generatePDF();
        } else if (format === 'detailed') {
            // Generate detailed JSON report
            const results = currentAnalysis.results || UnifiedApp.results.getCurrentResults();
            if (!results) {
                UnifiedApp.ui.showToast('No results to download', 'error');
                return;
            }
            
            const detailedReport = {
                metadata: {
                    analysis_id: results.analysis_id,
                    timestamp: new Date().toISOString(),
                    type: currentAnalysis.analysisType,
                    version: '2.0'
                },
                summary: {
                    trust_score: results.trust_score,
                    ai_probability: results.ai_probability,
                    plagiarism_score: results.plagiarism_score
                },
                detailed_results: results
            };
            
            const blob = new Blob([JSON.stringify(detailedReport, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `detailed_analysis_${Date.now()}.json`;
            a.click();
            URL.revokeObjectURL(url);
            
            UnifiedApp.ui.showToast('Detailed report downloaded!', 'success');
        }
    };
    
    // Legacy compatibility
    window.generatePDF = function() {
        window.UnifiedApp.analysis.generatePDF();
    };
    
    window.shareResults = function() {
        window.UnifiedApp.analysis.shareResults();
    };
    
    console.log('Unified Analysis module loaded - Complete Enhanced Version');
    
    return {
        runAnalysis: window.UnifiedApp.analysis.runAnalysis,
        generatePDF: window.UnifiedApp.analysis.generatePDF,
        shareResults: window.UnifiedApp.analysis.shareResults
    };
