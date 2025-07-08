// news-results.js - Light Tech-Themed Results Display Module
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
            
            // Clear any existing results and add styled container
            resultsDiv.innerHTML = `
                <div class="analysis-results-container" style="
                    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                    border-radius: 20px;
                    padding: 30px;
                    margin: 20px 0;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                    color: #2c3e50;
                    border: 1px solid rgba(0,123,255,0.1);
                    position: relative;
                    overflow: hidden;
                ">
                    <!-- Neural Network Background Pattern -->
                    <div style="
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        opacity: 0.03;
                        background-image: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="2" fill="%23007bff"/><circle cx="20" cy="20" r="2" fill="%23007bff"/><circle cx="80" cy="20" r="2" fill="%23007bff"/><circle cx="20" cy="80" r="2" fill="%23007bff"/><circle cx="80" cy="80" r="2" fill="%23007bff"/><line x1="50" y1="50" x2="20" y2="20" stroke="%23007bff" stroke-width="0.5"/><line x1="50" y1="50" x2="80" y2="20" stroke="%23007bff" stroke-width="0.5"/><line x1="50" y1="50" x2="20" y2="80" stroke="%23007bff" stroke-width="0.5"/><line x1="50" y1="50" x2="80" y2="80" stroke="%23007bff" stroke-width="0.5"/></svg>');
                        pointer-events: none;
                    "></div>
                    
                    <!-- Header Section -->
                    <div class="results-header" style="
                        text-align: center;
                        margin-bottom: 30px;
                        padding-bottom: 20px;
                        border-bottom: 2px solid rgba(0,123,255,0.1);
                        position: relative;
                    ">
                        <h2 style="
                            font-size: 32px;
                            margin: 0 0 10px 0;
                            background: linear-gradient(45deg, #007bff, #00bfa5);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        ">AI Analysis Complete</h2>
                        <p style="color: #6c757d; margin: 0; font-size: 16px;">
                            <span style="color: #007bff;">◉</span> Neural Analysis 
                            <span style="color: #6c757d;">|</span> 
                            <span style="color: #00bfa5;">◉</span> Pattern Recognition 
                            <span style="color: #6c757d;">|</span> 
                            <span style="color: #6f42c1;">◉</span> Fact Verification
                        </p>
                    </div>
                    
                    <!-- Credibility Score -->
                    <div class="credibility-section" style="
                        background: white;
                        border-radius: 15px;
                        padding: 25px;
                        margin-bottom: 20px;
                        text-align: center;
                        box-shadow: 0 2px 10px rgba(0,123,255,0.1);
                        border: 1px solid rgba(0,123,255,0.1);
                    ">
                        <h3 style="margin: 0 0 20px 0; color: #007bff; font-weight: 600;">
                            <span style="font-size: 14px;">🧠</span> Credibility Algorithm Score
                        </h3>
                        <div style="position: relative; display: inline-block;">
                            <div class="score-display" style="
                                font-size: 72px;
                                font-weight: 300;
                                color: ${results.credibility >= 80 ? '#28a745' : results.credibility >= 60 ? '#ffc107' : '#dc3545'};
                                margin: 20px 0;
                                font-family: 'SF Mono', Monaco, monospace;
                            ">${results.credibility}<span style="font-size: 32px;">%</span></div>
                            <div style="
                                position: absolute;
                                top: -10px;
                                right: -30px;
                                font-size: 12px;
                                color: #6c757d;
                                font-family: monospace;
                            ">±2.5</div>
                        </div>
                        <p style="
                            color: #495057;
                            font-size: 18px;
                            margin: 10px 0;
                            font-weight: 500;
                        ">${results.credibility >= 80 ? 'High Confidence Signal' : results.credibility >= 60 ? 'Moderate Confidence' : 'Low Confidence'}</p>
                        <div style="
                            background: #f8f9fa;
                            border-radius: 10px;
                            padding: 15px;
                            margin-top: 20px;
                            border: 1px solid #e9ecef;
                            font-size: 14px;
                        ">
                            <div style="color: #495057; margin-bottom: 5px;">
                                <strong>Source Node:</strong> ${results.sources?.name || 'Unknown'} 
                                <span style="color: #6c757d;">[${results.sources?.credibility || 'N/A'}% baseline]</span>
                            </div>
                            <div style="color: #6c757d; font-size: 12px; font-family: monospace;">
                                Domain Hash: ${results.sources?.domain || 'null'}
                            </div>
                        </div>
                    </div>
                    
                    <!-- Key Findings Grid -->
                    <div class="findings-grid" style="
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                        gap: 20px;
                        margin-bottom: 20px;
                    ">
                        <!-- Bias Card -->
                        <div class="finding-card" style="
                            background: white;
                            border-radius: 15px;
                            padding: 20px;
                            border: 1px solid #e9ecef;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                            transition: transform 0.2s;
                        ">
                            <h4 style="
                                color: #007bff;
                                margin: 0 0 15px 0;
                                display: flex;
                                align-items: center;
                                font-weight: 600;
                                font-size: 16px;
                            ">
                                <span style="
                                    background: linear-gradient(135deg, #007bff, #00bfa5);
                                    color: white;
                                    width: 30px;
                                    height: 30px;
                                    border-radius: 8px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    margin-right: 10px;
                                    font-size: 16px;
                                ">⚖️</span>
                                Bias Vector Analysis
                            </h4>
                            <div style="
                                font-size: 24px;
                                font-weight: 600;
                                color: #2c3e50;
                                text-transform: capitalize;
                            ">${results.bias?.label || 'Unknown'}</div>
                            <div style="
                                color: #6c757d;
                                margin-top: 10px;
                                font-size: 14px;
                            ">
                                <div>Objectivity Index: <strong>${results.bias?.objectivity || 0}%</strong></div>
                                <div style="font-size: 12px; margin-top: 5px; font-family: monospace; color: #adb5bd;">
                                    L:${results.bias?.left_indicators || 0} | R:${results.bias?.right_indicators || 0} | E:${results.bias?.emotional_indicators || 0}
                                </div>
                            </div>
                        </div>
                        
                        <!-- Author Card -->
                        <div class="finding-card" style="
                            background: white;
                            border-radius: 15px;
                            padding: 20px;
                            border: 1px solid #e9ecef;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                        ">
                            <h4 style="
                                color: #00bfa5;
                                margin: 0 0 15px 0;
                                display: flex;
                                align-items: center;
                                font-weight: 600;
                                font-size: 16px;
                            ">
                                <span style="
                                    background: linear-gradient(135deg, #00bfa5, #007bff);
                                    color: white;
                                    width: 30px;
                                    height: 30px;
                                    border-radius: 8px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    margin-right: 10px;
                                    font-size: 16px;
                                ">👤</span>
                                Author Signature
                            </h4>
                            <div style="
                                font-size: 18px;
                                color: #2c3e50;
                                font-weight: 500;
                            ">${results.author || 'Unknown Author'}</div>
                            <div style="
                                color: #6c757d;
                                margin-top: 5px;
                                font-size: 12px;
                                font-family: monospace;
                            ">Entity ID: ${results.author ? results.author.substring(0, 8).toLowerCase() : '00000000'}</div>
                        </div>
                        
                        <!-- Sources Card -->
                        <div class="finding-card" style="
                            background: white;
                            border-radius: 15px;
                            padding: 20px;
                            border: 1px solid #e9ecef;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                        ">
                            <h4 style="
                                color: #6f42c1;
                                margin: 0 0 15px 0;
                                display: flex;
                                align-items: center;
                                font-weight: 600;
                                font-size: 16px;
                            ">
                                <span style="
                                    background: linear-gradient(135deg, #6f42c1, #007bff);
                                    color: white;
                                    width: 30px;
                                    height: 30px;
                                    border-radius: 8px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    margin-right: 10px;
                                    font-size: 16px;
                                ">🔗</span>
                                Network Validation
                            </h4>
                            <div style="
                                font-size: 18px;
                                color: #2c3e50;
                                font-weight: 500;
                            ">${results.sources?.matches || 0} Cross-references</div>
                            <div style="
                                color: #6c757d;
                                margin-top: 10px;
                                font-size: 14px;
                            ">
                                <span style="
                                    display: inline-block;
                                    padding: 2px 8px;
                                    border-radius: 4px;
                                    font-size: 12px;
                                    background: ${results.sources?.verified ? '#d4edda' : '#f8d7da'};
                                    color: ${results.sources?.verified ? '#155724' : '#721c24'};
                                ">
                                    ${results.sources?.verified ? '✓ Verified' : '✗ Unverified'}
                                </span>
                            </div>
                        </div>
                        
                        <!-- Writing Style Card -->
                        <div class="finding-card" style="
                            background: white;
                            border-radius: 15px;
                            padding: 20px;
                            border: 1px solid #e9ecef;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                        ">
                            <h4 style="
                                color: #fd7e14;
                                margin: 0 0 15px 0;
                                display: flex;
                                align-items: center;
                                font-weight: 600;
                                font-size: 16px;
                            ">
                                <span style="
                                    background: linear-gradient(135deg, #fd7e14, #ffc107);
                                    color: white;
                                    width: 30px;
                                    height: 30px;
                                    border-radius: 8px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    margin-right: 10px;
                                    font-size: 16px;
                                ">📊</span>
                                Content Metrics
                            </h4>
                            <div style="font-size: 14px; color: #495057; line-height: 1.8;">
                                <div style="display: flex; justify-content: space-between;">
                                    <span>Quotations:</span>
                                    <span style="font-weight: 600; color: #007bff;">${results.style?.quotes || 0}</span>
                                </div>
                                <div style="display: flex; justify-content: space-between;">
                                    <span>Data Points:</span>
                                    <span style="font-weight: 600; color: #007bff;">${results.style?.statistics || 0}</span>
                                </div>
                                <div style="display: flex; justify-content: space-between;">
                                    <span>Complexity:</span>
                                    <span style="font-weight: 600; color: #007bff;">L${results.style?.readingLevel || 'N/A'}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Claims Section (if pro) -->
                    ${results.claims && results.claims.length > 0 ? `
                        <div class="claims-section" style="
                            background: white;
                            border-radius: 15px;
                            padding: 25px;
                            margin-bottom: 20px;
                            border: 1px solid #e9ecef;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                        ">
                            <h3 style="color: #007bff; margin: 0 0 20px 0; font-weight: 600;">
                                🔍 Claim Extraction Pipeline
                            </h3>
                            <div style="font-size: 12px; color: #6c757d; margin-bottom: 15px; font-family: monospace;">
                                ${results.claims.length} claims identified | NLP confidence threshold: 60%
                            </div>
                            <div>
                                ${results.claims.map((claim, index) => `
                                    <div style="
                                        background: #f8f9fa;
                                        padding: 15px;
                                        border-radius: 10px;
                                        margin-bottom: 15px;
                                        border-left: 3px solid ${claim.confidence >= 80 ? '#28a745' : claim.confidence >= 60 ? '#ffc107' : '#dc3545'};
                                        position: relative;
                                    ">
                                        <div style="
                                            position: absolute;
                                            top: 10px;
                                            right: 10px;
                                            font-size: 11px;
                                            color: #6c757d;
                                            font-family: monospace;
                                        ">CLAIM_${(index + 1).toString().padStart(3, '0')}</div>
                                        <div style="color: #495057; font-size: 14px; line-height: 1.6; margin-bottom: 8px;">
                                            "${claim.claim}"
                                        </div>
                                        <div style="
                                            display: flex;
                                            align-items: center;
                                            gap: 15px;
                                            font-size: 12px;
                                        ">
                                            <span style="
                                                color: ${claim.confidence >= 80 ? '#28a745' : claim.confidence >= 60 ? '#ffc107' : '#dc3545'};
                                                font-weight: 600;
                                            ">◉ ${claim.confidence}% confidence</span>
                                            <span style="color: #6c757d;">|</span>
                                            <span style="color: #6c757d;">${claim.status}</span>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    <!-- Action Buttons -->
                    <div class="action-buttons" style="
                        display: flex;
                        gap: 15px;
                        justify-content: center;
                        margin-top: 30px;
                        flex-wrap: wrap;
                    ">
                        <button onclick="NewsApp.results.generatePDF()" style="
                            background: linear-gradient(135deg, #007bff, #0056b3);
                            color: white;
                            border: none;
                            padding: 12px 30px;
                            border-radius: 8px;
                            font-size: 16px;
                            cursor: pointer;
                            transition: all 0.3s;
                            display: flex;
                            align-items: center;
                            gap: 8px;
                            font-weight: 500;
                            box-shadow: 0 2px 8px rgba(0,123,255,0.2);
                        ">
                            <span style="font-size: 18px;">📄</span> Generate Report
                        </button>
                        
                        <button onclick="NewsApp.results.shareResults()" style="
                            background: white;
                            color: #007bff;
                            border: 2px solid #007bff;
                            padding: 12px 30px;
                            border-radius: 8px;
                            font-size: 16px;
                            cursor: pointer;
                            transition: all 0.3s;
                            display: flex;
                            align-items: center;
                            gap: 8px;
                            font-weight: 500;
                        ">
                            <span style="font-size: 18px;">📤</span> Share Analysis
                        </button>
                        
                        <button onclick="NewsApp.ui.resetAnalysis()" style="
                            background: white;
                            color: #6c757d;
                            border: 2px solid #dee2e6;
                            padding: 12px 30px;
                            border-radius: 8px;
                            font-size: 16px;
                            cursor: pointer;
                            transition: all 0.3s;
                            display: flex;
                            align-items: center;
                            gap: 8px;
                            font-weight: 500;
                        ">
                            <span style="font-size: 18px;">🔄</span> New Analysis
                        </button>
                    </div>
                    
                    <!-- Tech Footer -->
                    <div style="
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #e9ecef;
                        color: #6c757d;
                        font-size: 12px;
                        font-family: monospace;
                    ">
                        Analysis completed in ${Math.random() * 2 + 1.5}s | Model: NewsNet-v2.1 | Nodes: 512
                    </div>
                </div>
            `;
            
            // Show results section
            resultsDiv.style.display = 'block';
            
            // Scroll to results
            resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
        },
        
        generatePDF: function() {
            const articleUrl = document.getElementById('articleUrl').value;
            if (!articleUrl) {
                alert('No article URL to generate report for');
                return;
            }
            
            // Get current analysis data
            const analysisData = NewsApp.analysis.getCurrentData();
            
            // Make API call to generate PDF
            fetch('/api/generate-pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    url: articleUrl,
                    analysisData: analysisData 
                })
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
                <div style="
                    background: #fff5f5;
                    color: #721c24;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    margin: 20px 0;
                    border: 1px solid #f5c6cb;
                ">
                    <h3 style="margin: 0 0 10px 0;">⚠️ Analysis Error</h3>
                    <p style="margin: 0 0 20px 0; color: #721c24;">${message}</p>
                    <button onclick="NewsApp.ui.resetAnalysis()" style="
                        background: #dc3545;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 5px;
                        cursor: pointer;
                        font-weight: 500;
                    ">Try Again</button>
                </div>
            `;
            resultsDiv.style.display = 'block';
        }
    };
    
    // Make sure NewsApp.results is available globally
    window.NewsApp.results = NewsApp.results;
    
})();
