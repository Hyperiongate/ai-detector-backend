<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facts & Fakes AI - Premium News Analysis</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0f0f23 100%);
            color: #ffffff;
            min-height: 100vh;
            overflow-x: hidden;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px 0;
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        }

        .header h1 {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(45deg, #ffffff, #e0e7ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
            font-weight: 300;
        }

        .input-section {
            background: rgba(255, 255, 255, 0.05);
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .input-group {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        label {
            font-weight: 600;
            font-size: 1.1rem;
            color: #e0e7ff;
        }

        textarea {
            width: 100%;
            padding: 20px;
            border: 2px solid rgba(102, 126, 234, 0.3);
            border-radius: 15px;
            background: rgba(255, 255, 255, 0.05);
            color: #ffffff;
            font-size: 16px;
            resize: vertical;
            min-height: 120px;
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
        }

        textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
        }

        .analyze-btn {
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 18px 40px;
            border-radius: 50px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .analyze-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
        }

        .analyze-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .progress-container {
            display: none;
            background: rgba(255, 255, 255, 0.05);
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
            backdrop-filter: blur(10px);
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 15px;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 10px;
            transition: width 0.5s ease;
            width: 0%;
        }

        .progress-text {
            text-align: center;
            font-weight: 500;
            color: #e0e7ff;
        }

        .results-container {
            display: none;
            gap: 25px;
        }

        .executive-summary {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            padding: 30px;
            border-radius: 20px;
            border: 1px solid rgba(102, 126, 234, 0.2);
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }

        .credibility-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 15px;
        }

        .credibility-score {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .score-circle {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            font-weight: 800;
            position: relative;
            overflow: hidden;
        }

        .score-circle::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 50%;
            border: 4px solid rgba(255, 255, 255, 0.1);
        }

        .assessment-text {
            font-size: 1.3rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .grade-badge {
            background: rgba(255, 255, 255, 0.1);
            padding: 8px 16px;
            border-radius: 25px;
            font-weight: 700;
            font-size: 1.1rem;
        }

        .summary-text {
            font-size: 1.1rem;
            line-height: 1.6;
            margin-bottom: 20px;
            color: #e0e7ff;
        }

        .key-findings {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }

        .finding-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .analysis-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }

        .analysis-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }

        .analysis-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }

        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .card-title {
            font-size: 1.3rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .card-icon {
            width: 24px;
            height: 24px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
        }

        .expand-btn {
            background: rgba(255, 255, 255, 0.1);
            border: none;
            color: white;
            padding: 8px 12px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.3s ease;
        }

        .expand-btn:hover {
            background: rgba(255, 255, 255, 0.2);
        }

        .bias-visualization {
            margin: 20px 0;
        }

        .bias-meter {
            position: relative;
            height: 40px;
            background: linear-gradient(90deg, #0066cc 0%, #4488cc 25%, #cccccc 50%, #cc8888 75%, #cc0000 100%);
            border-radius: 20px;
            margin: 15px 0;
            overflow: hidden;
        }

        .bias-indicator {
            position: absolute;
            top: -10px;
            width: 20px;
            height: 60px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
            transition: left 0.5s ease;
        }

        .bias-labels {
            display: flex;
            justify-content: space-between;
            margin-top: 10px;
            font-size: 0.9rem;
            opacity: 0.8;
        }

        .metric-bar {
            background: rgba(255, 255, 255, 0.1);
            height: 8px;
            border-radius: 10px;
            margin: 10px 0;
            overflow: hidden;
        }

        .metric-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 10px;
            transition: width 0.8s ease;
        }

        .metric-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 15px 0;
        }

        .metric-label {
            font-weight: 500;
            color: #e0e7ff;
        }

        .metric-value {
            font-weight: 700;
            font-size: 1.1rem;
        }

        .source-list {
            max-height: 300px;
            overflow-y: auto;
            margin-top: 15px;
        }

        .source-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
        }

        .source-title {
            font-weight: 600;
            margin-bottom: 5px;
            color: #ffffff;
        }

        .source-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.9rem;
            color: #b0b7c3;
            margin-bottom: 8px;
        }

        .credibility-badge {
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .expandable-content {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }

        .expandable-content.expanded {
            max-height: 1000px;
        }

        .claim-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            border-left: 4px solid;
        }

        .claim-item.verified { border-left-color: #00cc44; }
        .claim-item.disputed { border-left-color: #ff4444; }
        .claim-item.mixed { border-left-color: #ffaa00; }

        .loading-spinner {
            width: 40px;
            height: 40px;
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-left: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .error-message {
            background: rgba(255, 68, 68, 0.1);
            border: 1px solid rgba(255, 68, 68, 0.3);
            color: #ff9999;
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            text-align: center;
        }

        .recommendation-box {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
            padding: 20px;
            border-radius: 15px;
            margin-top: 20px;
            border: 1px solid rgba(102, 126, 234, 0.3);
        }

        .recommendation-text {
            font-size: 1.1rem;
            font-weight: 500;
            color: #e0e7ff;
        }

        @media (max-width: 768px) {
            .header h1 { font-size: 2rem; }
            .analysis-grid { grid-template-columns: 1fr; }
            .credibility-header { flex-direction: column; }
            .key-findings { grid-template-columns: 1fr; }
            .container { padding: 15px; }
        }

        .pulse {
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }

        .fade-in {
            animation: fadeIn 0.8s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Facts & Fakes AI</h1>
            <p>Premium News Misinformation Analysis</p>
        </div>

        <div class="input-section">
            <div class="input-group">
                <label for="newsText">Enter News Content for Analysis</label>
                <textarea 
                    id="newsText" 
                    placeholder="Paste the news article, headline, or claim you want to analyze for misinformation, bias, and credibility..."
                ></textarea>
                <button class="analyze-btn" onclick="analyzeNews()">
                    🚀 ANALYZE WITH AI
                </button>
            </div>
        </div>

        <div class="progress-container" id="progressContainer">
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <div class="progress-text" id="progressText">Initializing AI Analysis...</div>
            <div class="loading-spinner" style="margin-top: 20px;"></div>
        </div>

        <div class="results-container" id="resultsContainer">
            <!-- Executive Summary -->
            <div class="executive-summary" id="executiveSummary">
                <!-- Dynamic content will be inserted here -->
            </div>

            <!-- Analysis Grid -->
            <div class="analysis-grid" id="analysisGrid">
                <!-- Dynamic analysis cards will be inserted here -->
            </div>
        </div>

        <div class="error-message" id="errorMessage" style="display: none;">
            <!-- Error messages will appear here -->
        </div>
    </div>

    <script>
        let analysisData = null;

        async function analyzeNews() {
            const text = document.getElementById('newsText').value.trim();
            
            if (!text || text.length < 10) {
                showError('Please enter at least 10 characters of news content to analyze.');
                return;
            }

            // Reset UI
            hideError();
            showProgress();
            hideResults();

            const progressStages = [
                { progress: 15, text: '🤖 Starting AI Analysis...' },
                { progress: 30, text: '🎯 Detecting Political Bias...' },
                { progress: 45, text: '📝 Analyzing Author Credibility...' },
                { progress: 60, text: '🔍 Verifying Sources...' },
                { progress: 75, text: '📊 Cross-Platform Analysis...' },
                { progress: 90, text: '✅ Calculating Credibility Scores...' },
                { progress: 100, text: '🎉 Analysis Complete!' }
            ];

            // Animate progress
            let currentStage = 0;
            const progressInterval = setInterval(() => {
                if (currentStage < progressStages.length) {
                    updateProgress(progressStages[currentStage].progress, progressStages[currentStage].text);
                    currentStage++;
                } else {
                    clearInterval(progressInterval);
                }
            }, 600);

            try {
                const response = await fetch('https://ai-detector-backend-g4mj.onrender.com/api/analyze-news', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: text })
                });

                if (!response.ok) {
                    throw new Error(`Analysis failed: ${response.status}`);
                }

                const data = await response.json();
                analysisData = data;

                // Complete progress animation
                clearInterval(progressInterval);
                updateProgress(100, '🎉 Analysis Complete!');

                setTimeout(() => {
                    hideProgress();
                    displayResults(data);
                }, 1000);

            } catch (error) {
                clearInterval(progressInterval);
                hideProgress();
                showError(`Analysis failed: ${error.message}`);
                console.error('Analysis error:', error);
            }
        }

        function updateProgress(percentage, text) {
            document.getElementById('progressFill').style.width = percentage + '%';
            document.getElementById('progressText').textContent = text;
        }

        function showProgress() {
            document.getElementById('progressContainer').style.display = 'block';
            updateProgress(0, 'Initializing AI Analysis...');
        }

        function hideProgress() {
            document.getElementById('progressContainer').style.display = 'none';
        }

        function hideResults() {
            document.getElementById('resultsContainer').style.display = 'none';
        }

        function showError(message) {
            const errorDiv = document.getElementById('errorMessage');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }

        function hideError() {
            document.getElementById('errorMessage').style.display = 'none';
        }

        function displayResults(data) {
            const container = document.getElementById('resultsContainer');
            container.style.display = 'block';
            container.classList.add('fade-in');

            // Display Executive Summary
            displayExecutiveSummary(data);

            // Display Analysis Cards
            displayAnalysisCards(data);
        }

        function displayExecutiveSummary(data) {
            const summaryDiv = document.getElementById('executiveSummary');
            const summary = data.executive_summary || {};
            const scoring = data.scoring || {};

            const credibilityScore = scoring.overall_credibility || 50;
            const grade = scoring.credibility_grade || 'N/A';
            const assessment = summary.main_assessment || 'ANALYSIS COMPLETE';
            const color = summary.assessment_color || 'gray';

            summaryDiv.innerHTML = `
                <div class="credibility-header">
                    <div class="credibility-score">
                        <div class="score-circle" style="background: ${getScoreColor(credibilityScore)};">
                            ${Math.round(credibilityScore)}
                        </div>
                        <div>
                            <div class="assessment-text" style="color: ${getScoreColor(credibilityScore)};">
                                ${assessment}
                            </div>
                            <div style="font-size: 1rem; opacity: 0.8;">Credibility Analysis</div>
                        </div>
                    </div>
                    <div class="grade-badge" style="background: ${getScoreColor(credibilityScore)};">
                        Grade: ${grade}
                    </div>
                </div>
                
                <div class="summary-text">
                    ${summary.summary_text || 'Analysis completed successfully.'}
                </div>
                
                <div class="key-findings">
                    ${(summary.key_findings || []).map(finding => `
                        <div class="finding-item">${finding}</div>
                    `).join('')}
                </div>
                
                ${summary.recommendation ? `
                    <div class="recommendation-box">
                        <strong>🎯 Recommendation:</strong>
                        <div class="recommendation-text">${summary.recommendation}</div>
                    </div>
                ` : ''}
            `;
        }

        function displayAnalysisCards(data) {
            const gridDiv = document.getElementById('analysisGrid');
            
            const cards = [
                createPoliticalBiasCard(data.political_bias || {}),
                createAuthorAnalysisCard(data.author_analysis || {}),
                createSourceVerificationCard(data.source_verification || {}),
                createAIAnalysisCard(data.ai_analysis || {}),
                createFactCheckCard(data.fact_check_results || {}),
                createCrossPlatformCard(data.cross_platform_analysis || {})
            ];

            gridDiv.innerHTML = cards.join('');
        }

        function createPoliticalBiasCard(biasData) {
            const biasScore = biasData.bias_score || 0;
            const biasLabel = biasData.bias_label || 'Unknown';
            const objectivity = biasData.objectivity_score || 50;

            return `
                <div class="analysis-card">
                    <div class="card-header">
                        <div class="card-title">
                            <div class="card-icon">🎯</div>
                            Political Bias Analysis
                        </div>
                        <button class="expand-btn" onclick="toggleExpand(this)">Details</button>
                    </div>
                    
                    <div class="bias-visualization">
                        <div class="metric-item">
                            <span class="metric-label">Bias Rating:</span>
                            <span class="metric-value" style="color: ${getBiasColor(biasScore)};">
                                ${biasLabel} (${biasScore > 0 ? '+' : ''}${biasScore})
                            </span>
                        </div>
                        
                        <div class="bias-meter">
                            <div class="bias-indicator" style="left: ${(biasScore + 100) / 2}%;"></div>
                        </div>
                        
                        <div class="bias-labels">
                            <span>Far Left</span>
                            <span>Center</span>
                            <span>Far Right</span>
                        </div>
                        
                        <div class="metric-item">
                            <span class="metric-label">Objectivity Score:</span>
                            <span class="metric-value">${objectivity}/100</span>
                        </div>
                        <div class="metric-bar">
                            <div class="metric-fill" style="width: ${objectivity}%;"></div>
                        </div>
                    </div>
                    
                    <div class="expandable-content">
                        <div style="margin-top: 15px;">
                            <strong>Political Keywords:</strong>
                            <p>${(biasData.political_keywords || []).join(', ') || 'None identified'}</p>
                            
                            <strong style="margin-top: 10px; display: block;">Explanation:</strong>
                            <p>${biasData.bias_explanation || 'No detailed explanation available.'}</p>
                        </div>
                    </div>
                </div>
            `;
        }

        function createAuthorAnalysisCard(authorData) {
            const writingScore = authorData.writing_style_score || 50;
            const professionalism = authorData.professionalism_score || 50;
            const expertise = authorData.estimated_expertise_level || 'Unknown';

            return `
                <div class="analysis-card">
                    <div class="card-header">
                        <div class="card-title">
                            <div class="card-icon">👤</div>
                            Author & Writing Analysis
                        </div>
                        <button class="expand-btn" onclick="toggleExpand(this)">Details</button>
                    </div>
                    
                    <div class="metric-item">
                        <span class="metric-label">Writing Quality:</span>
                        <span class="metric-value">${writingScore}/100</span>
                    </div>
                    <div class="metric-bar">
                        <div class="metric-fill" style="width: ${writingScore}%;"></div>
                    </div>
                    
                    <div class="metric-item">
                        <span class="metric-label">Professionalism:</span>
                        <span class="metric-value">${professionalism}/100</span>
                    </div>
                    <div class="metric-bar">
                        <div class="metric-fill" style="width: ${professionalism}%;"></div>
                    </div>
                    
                    <div class="metric-item">
                        <span class="metric-label">Expertise Level:</span>
                        <span class="metric-value" style="color: ${getExpertiseColor(expertise)};">
                            ${expertise.charAt(0).toUpperCase() + expertise.slice(1)}
                        </span>
                    </div>
                    
                    <div class="expandable-content">
                        <div style="margin-top: 15px;">
                            <strong>Expertise Indicators:</strong>
                            <ul style="margin-left: 20px; margin-top: 5px;">
                                ${(authorData.expertise_indicators || []).map(indicator => `<li>${indicator}</li>`).join('')}
                            </ul>
                            
                            <strong style="margin-top: 15px; display: block;">Style Analysis:</strong>
                            <p>${authorData.style_analysis || 'No detailed analysis available.'}</p>
                        </div>
                    </div>
                </div>
            `;
        }

        function createSourceVerificationCard(sourceData) {
            const sourcesFound = sourceData.sources_found || 0;
            const avgCredibility = sourceData.average_source_credibility || 0;
            const diversity = sourceData.source_diversity || 0;

            return `
                <div class="analysis-card">
                    <div class="card-header">
                        <div class="card-title">
                            <div class="card-icon">🔍</div>
                            Source Verification
                        </div>
                        <button class="expand-btn" onclick="toggleExpand(this)">Sources</button>
                    </div>
                    
                    <div class="metric-item">
                        <span class="metric-label">Sources Found:</span>
                        <span class="metric-value">${sourcesFound}</span>
                    </div>
                    
                    <div class="metric-item">
                        <span class="metric-label">Average Credibility:</span>
                        <span class="metric-value">${Math.round(avgCredibility)}/100</span>
                    </div>
                    <div class="metric-bar">
                        <div class="metric-fill" style="width: ${avgCredibility}%;"></div>
                    </div>
                    
                    <div class="metric-item">
                        <span class="metric-label">Source Diversity:</span>
                        <span class="metric-value">${diversity} outlets</span>
                    </div>
                    
                    <div class="expandable-content">
                        <div class="source-list">
                            ${(sourceData.articles || []).map(article => `
                                <div class="source-item">
                                    <div class="source-title">${article.title}</div>
                                    <div class="source-meta">
                                        <span>${article.source_name}</span>
                                        <span class="credibility-badge" style="background: ${getCredibilityBadgeColor(article.credibility_score)};">
                                            ${article.credibility_score}/100
                                        </span>
                                    </div>
                                    <div style="font-size: 0.9rem; color: #b0b7c3;">
                                        ${article.description}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
        }

        function createAIAnalysisCard(aiData) {
            const credibility = aiData.credibility_score || 50;
            const confidence = aiData.confidence_level || 50;

            return `
                <div class="analysis-card">
                    <div class="card-header">
                        <div class="card-title">
                            <div class="card-icon">🤖</div>
                            AI Content Analysis
                        </div>
                        <button class="expand-btn" onclick="toggleExpand(this)">Details</button>
                    </div>
                    
                    <div class="metric-item">
                        <span class="metric-label">AI Credibility Score:</span>
                        <span class="metric-value">${credibility}/100</span>
                    </div>
                    <div class="metric-bar">
                        <div class="metric-fill" style="width: ${credibility}%;"></div>
                    </div>
                    
                    <div class="metric-item">
                        <span class="metric-label">Analysis Confidence:</span>
                        <span class="metric-value">${confidence}/100</span>
                    </div>
                    <div class="metric-bar">
                        <div class="metric-fill" style="width: ${confidence}%;"></div>
                    </div>
                    
                    <div class="expandable-content">
                        <div style="margin-top: 15px;">
                            <strong>Key Claims Identified:</strong>
                            <ul style="margin-left: 20px; margin-top: 5px;">
                                ${(aiData.factual_claims || []).map(claim => `<li>${claim}</li>`).join('')}
                            </ul>
                            
                            <strong style="margin-top: 15px; display: block;">Credibility Indicators:</strong>
                            <ul style="margin-left: 20px; margin-top: 5px; color: #88cc88;">
                                ${(aiData.credibility_indicators || []).map(indicator => `<li>✓ ${indicator}</li>`).join('')}
                            </ul>
                            
                            <strong style="margin-top: 15px; display: block;">Red Flags:</strong>
                            <ul style="margin-left: 20px; margin-top: 5px; color: #cc8888;">
                                ${(aiData.red_flags || []).map(flag => `<li>⚠ ${flag}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            `;
        }

        function createFactCheckCard(factData) {
            const factsFound = factData.fact_checks_found || 0;
            const avgRating = factData.average_rating || 0;

            return `
                <div class="analysis-card">
                    <div class="card-header">
                        <div class="card-title">
                            <div class="card-icon">✅</div>
                            Fact Check Results
                        </div>
                        <button class="expand-btn" onclick="toggleExpand(this)">Claims</button>
                    </div>
                    
                    <div class="metric-item">
                        <span class="metric-label">Fact Checks Found:</span>
                        <span class="metric-value">${factsFound}</span>
                    </div>
                    
                    ${avgRating > 0 ? `
                        <div class="metric-item">
                            <span class="metric-label">Average Rating:</span>
                            <span class="metric-value">${Math.round(avgRating)}/100</span>
                        </div>
                        <div class="metric-bar">
                            <div class="metric-fill" style="width: ${avgRating}%;"></div>
                        </div>
                    ` : ''}
                    
                    <div class="expandable-content">
                        ${factsFound > 0 ? `
                            <div style="margin-top: 15px;">
                                ${(factData.claims || []).map(claim => `
                                    <div class="claim-item ${getClaimClass(claim.rating)}">
                                        <strong>${claim.claim_text}</strong><br>
                                        <small>Rating: ${claim.rating} (${claim.reviewer})</small>
                                    </div>
                                `).join('')}
                            </div>
                        ` : `
                            <div style="margin-top: 15px; text-align: center; opacity: 0.7;">
                                No specific fact checks found for this content.
                            </div>
                        `}
                    </div>
                </div>
            `;
        }

        function createCrossPlatformCard(crossData) {
            const platformsAnalyzed = crossData.platforms_analyzed || 0;
            const consistency = crossData.narrative_consistency_score || 0;

            return `
                <div class="analysis-card">
                    <div class="card-header">
                        <div class="card-title">
                            <div class="card-icon">📊</div>
                            Cross-Platform Analysis
                        </div>
                        <button class="expand-btn" onclick="toggleExpand(this)">Platforms</button>
                    </div>
                    
                    <div class="metric-item">
                        <span class="metric-label">Platforms Analyzed:</span>
                        <span class="metric-value">${platformsAnalyzed}</span>
                    </div>
                    
                    <div class="metric-item">
                        <span class="metric-label">Narrative Consistency:</span>
                        <span class="metric-value">${Math.round(consistency)}/100</span>
                    </div>
                    <div class="metric-bar">
                        <div class="metric-fill" style="width: ${consistency}%;"></div>
                    </div>
                    
                    <div class="expandable-content">
                        <div style="margin-top: 15px;">
                            ${(crossData.coverage_analysis || []).map(platform => `
                                <div class="source-item">
                                    <div class="source-title">${platform.platform_type}</div>
                                    <div class="source-meta">
                                        <span>Bias: ${platform.bias_lean}</span>
                                        <span>Tone: ${platform.coverage_tone}</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
        }

        function toggleExpand(button) {
            const content = button.closest('.analysis-card').querySelector('.expandable-content');
            content.classList.toggle('expanded');
            button.textContent = content.classList.contains('expanded') ? 'Less' : 'Details';
        }

        // Helper functions for colors and styling
        function getScoreColor(score) {
            if (score >= 80) return '#00cc44';
            if (score >= 60) return '#88cc00';
            if (score >= 40) return '#ffaa00';
            return '#ff4444';
        }

        function getBiasColor(biasScore) {
            if (Math.abs(biasScore) <= 20) return '#cccccc';
            if (biasScore < 0) return '#4488cc';
            return '#cc8888';
        }

        function getExpertiseColor(expertise) {
            switch(expertise.toLowerCase()) {
                case 'expert': return '#00cc44';
                case 'professional': return '#88cc00';
                case 'amateur': return '#ffaa00';
                default: return '#cc8888';
            }
        }

        function getCredibilityBadgeColor(score) {
            if (score >= 80) return 'rgba(0, 204, 68, 0.3)';
            if (score >= 60) return 'rgba(136, 204, 0, 0.3)';
            if (score >= 40) return 'rgba(255, 170, 0, 0.3)';
            return 'rgba(255, 68, 68, 0.3)';
        }

        function getClaimClass(rating) {
            const ratingLower = rating.toLowerCase();
            if (ratingLower.includes('true') || ratingLower.includes('accurate')) return 'verified';
            if (ratingLower.includes('false') || ratingLower.includes('inaccurate')) return 'disputed';
            return 'mixed';
        }

        // Auto-resize textarea
        document.getElementById('newsText').addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });

        // Add keyboard shortcut for analysis
        document.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                analyzeNews();
            }
        });
    </script>
</body>
</html>
