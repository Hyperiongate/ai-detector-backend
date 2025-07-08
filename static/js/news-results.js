// news-results.js - Styled Results Display Module
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
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    border-radius: 20px;
                    padding: 30px;
                    margin: 20px 0;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                    color: white;
                ">
                    <!-- Header Section -->
                    <div class="results-header" style="
                        text-align: center;
                        margin-bottom: 30px;
                        padding-bottom: 20px;
                        border-bottom: 2px solid rgba(255,255,255,0.1);
                    ">
                        <h2 style="
                            font-size: 32px;
                            margin: 0 0 10px 0;
                            background: linear-gradient(45deg, #00d4ff, #0099ff);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                        ">Analysis Complete</h2>
                        <p style="color: #b0b0b0; margin: 0;">Comprehensive fact-check and bias analysis</p>
                    </div>
                    
                    <!-- Credibility Score -->
                    <div class="credibility-section" style="
                        background: rgba(255,255,255,0.05);
                        border-radius: 15px;
                        padding: 25px;
                        margin-bottom: 20px;
                        text-align: center;
                    ">
                        <h3 style="margin: 0 0 20px 0; color: #00d4ff;">Credibility Score</h3>
                        <div class="score-display" style="
                            font-size: 72px;
                            font-weight: bold;
                            color: ${results.credibility >= 80 ? '#4CAF50' : results.credibility >= 60 ? '#FFC107' : '#FF5252'};
                            margin: 20px 0;
                        ">${results.credibility}%</div>
                        <p style="
                            color: #e0e0e0;
                            font-size: 18px;
                            margin: 10px 0;
                        ">${results.credibility >= 80 ? 'Highly Credible Source' : results.credibility >= 60 ? 'Moderately Credible' : 'Low Credibility'}</p>
                        <div style="
                            background: rgba(255,255,255,0.1);
                            border-radius: 10px;
                            padding: 15px;
                            margin-top: 20px;
                        ">
                            <strong>Source:</strong> ${results.sources?.name || 'Unknown'}<br>
                            <strong>Domain Credibility:</strong> ${results.sources?.credibility || 'N/A'}%
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
                            background: rgba(255,255,255,0.05);
                            border-radius: 15px;
                            padding: 20px;
                            border: 1px solid rgba(255,255,255,0.1);
                        ">
                            <h4 style="
                                color: #00d4ff;
                                margin: 0 0 15px 0;
                                display: flex;
                                align-items: center;
                            ">⚖️ Political Bias</h4>
                            <div style="
                                font-size: 24px;
                                font-weight: bold;
                                color: #fff;
                                text-transform: capitalize;
                            ">${results.bias?.label || 'Unknown'}</div>
                            <div style="
                                color: #b0b0b0;
                                margin-top: 10px;
                                font-size: 14px;
                            ">Objectivity: ${results.bias?.objectivity || 0}%</div>
                        </div>
                        
                        <!-- Author Card -->
                        <div class="finding-card" style="
                            background: rgba(255,255,255,0.05);
                            border-radius: 15px;
                            padding: 20px;
                            border: 1px solid rgba(255,255,255,0.1);
                        ">
                            <h4 style="
                                color: #00d4ff;
                                margin: 0 0 15px 0;
                                display: flex;
                                align-items: center;
                            ">👤 Author</h4>
                            <div style="
                                font-size: 18px;
                                color: #fff;
                            ">${results.author || 'Unknown Author'}</div>
                        </div>
                        
                        <!-- Sources Card -->
                        <div class="finding-card" style="
                            background: rgba(255,255,255,0.05);
                            border-radius: 15px;
                            padding: 20px;
                            border: 1px solid rgba(255,255,255,0.1);
                        ">
                            <h4 style="
                                color: #00d4ff;
                                margin: 0 0 15px 0;
                                display: flex;
                                align-items: center;
                            ">🔗 Source Quality</h4>
                            <div style="
                                font-size: 18px;
                                color: #fff;
                            ">${results.sources?.matches || 0} Cross-references</div>
                            <div style="
                                color: #b0b0b0;
                                margin-top: 10px;
                                font-size: 14px;
                            ">Verified: ${results.sources?.verified ? 'Yes' : 'No'}</div>
                        </div>
                        
                        <!-- Writing Style Card -->
                        <div class="finding-card" style="
                            background: rgba(255,255,255,0.05);
                            border-radius: 15px;
                            padding: 20px;
                            border: 1px solid rgba(255,255,255,0.1);
                        ">
                            <h4 style="
                                color: #00d4ff;
                                margin: 0 0 15px 0;
                                display: flex;
                                align-items: center;
                            ">📝 Writing Analysis</h4>
                            <div style="font-size: 14px; color: #e0e0e0;">
                                <div>Quotes: ${results.style?.quotes || 0}</div>
                                <div>Statistics: ${results.style?.statistics || 0}</div>
                                <div>Reading Level: ${results.style?.readingLevel || 'N/A'}</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Claims Section (if pro) -->
                    ${results.claims && results.claims.length > 0 ? `
                        <div class="claims-section" style="
                            background: rgba(255,255,255,0.05);
                            border-radius: 15px;
                            padding: 25px;
                            margin-bottom: 20px;
                        ">
                            <h3 style="color: #00d4ff; margin: 0 0 20px 0;">🔍 Key Claims Identified</h3>
                            <div style="space-y: 15px;">
                                ${results.claims.map((claim, index) => `
                                    <div style="
                                        background: rgba(255,255,255,0.05);
                                        padding: 15px;
                                        border-radius: 10px;
                                        margin-bottom: 10px;
                                        border-left: 3px solid #00d4ff;
                                    ">
                                        <div style="color: #e0e0e0; font-size: 14px; line-height: 1.6;">
                                            "${claim.claim}"
                                        </div>
                                        <div style="
                                            color: #00d4ff;
                                            font-size: 12px;
                                            margin-top: 8px;
                                        ">Confidence: ${claim.confidence}% • ${claim.status}</div>
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
                            background: linear-gradient(45deg, #00d4ff, #0099ff);
                            color: white;
                            border: none;
                            padding: 12px 30px;
                            border-radius: 25px;
                            font-size: 16px;
                            cursor: pointer;
                            transition: all 0.3s;
                            display: flex;
                            align-items: center;
                            gap: 8px;
                        ">📄 Download Report</button>
                        
                        <button onclick="NewsApp.results.shareResults()" style="
                            background: transparent;
                            color: #00d4ff;
                            border: 2px solid #00d4ff;
                            padding: 12px 30px;
                            border-radius: 25px;
                            font-size: 16px;
                            cursor: pointer;
                            transition: all 0.3s;
                            display: flex;
                            align-items: center;
                            gap: 8px;
                        ">📤 Share Analysis</button>
                        
                        <button onclick="NewsApp.ui.resetAnalysis()" style="
                            background: transparent;
                            color: #b0b0b0;
                            border: 2px solid #b0b0b0;
                            padding: 12px 30px;
                            border-radius: 25px;
                            font-size: 16px;
                            cursor: pointer;
                            transition: all 0.3s;
                            display: flex;
                            align-items: center;
                            gap: 8px;
                        ">🔄 Analyze Another</button>
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
                    background: #ff4444;
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    margin: 20px 0;
                ">
                    <h3 style="margin: 0 0 10px 0;">⚠️ Analysis Failed</h3>
                    <p style="margin: 0 0 20px 0;">${message}</p>
                    <button onclick="NewsApp.ui.resetAnalysis()" style="
                        background: white;
                        color: #ff4444;
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
    
    // Make sure NewsApp.results is available globally
    window.NewsApp.results = NewsApp.results;
    
})();
