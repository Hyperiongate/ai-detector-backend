{% extends "base.html" %}

{% block title %}News Analysis Dashboard{% endblock %}

{% block styles %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/news-main.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/news-components.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/news-specialized.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/new-responsiveness.css') }}">
<style>
/* Additional styles for the updated UI */
.pro-badge {
    background: linear-gradient(45deg, #FFD700, #FFA500);
    color: #000;
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 3px;
    margin-left: 5px;
    font-weight: bold;
}

.reset-button {
    background-color: #6c757d;
    color: white;
    padding: 12px 24px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    margin-left: 10px;
    font-size: 16px;
    font-weight: 600;
}

.reset-button:hover {
    background-color: #5a6268;
}

.free-tier-info {
    margin-top: 20px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
    font-size: 14px;
}

.url-input {
    flex: 1;
    padding: 12px;
    border: 2px solid #ddd;
    border-radius: 5px;
    font-size: 16px;
}

.input-wrapper {
    display: flex;
    gap: 10px;
    margin: 20px 0;
}

.analyze-button {
    background-color: #007bff;
    color: white;
    padding: 12px 24px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 600;
}

.analyze-button:hover {
    background-color: #0056b3;
}

.input-description {
    color: #666;
    margin-bottom: 20px;
}

/* Tab content styling for pro features */
.tab-content:not(#summary-content):not(#pro-content) {
    position: relative;
}

/* Loading spinner */
.loading {
    text-align: center;
    padding: 40px;
}

.spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 0 auto 20px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
</style>
{% endblock %}

{% block content %}
{% include 'includes/header.html' %}

<div class="container">
    <div class="header">
        <h1>News Analysis Dashboard</h1>
        <p>Advanced AI-powered news verification and analysis</p>
    </div>
    
    <!-- Simplified input section - just URL analysis -->
    <div class="analysis-input-section">
        <h2>Analyze News Article</h2>
        <p class="input-description">Enter any news article URL to get instant bias and credibility analysis</p>
        
        <div class="input-wrapper">
            <input type="url" 
                   id="articleUrl" 
                   placeholder="Paste article URL here (e.g., https://www.nytimes.com/...)" 
                   class="url-input">
            <button onclick="analyzeArticle()" class="analyze-button" id="analyzeBtn">
                Analyze Article
            </button>
            <button onclick="resetAnalysis()" class="reset-button" id="resetBtn" style="display: none;">
                Analyze New Article
            </button>
        </div>
        
        <div class="free-tier-info">
            <p>✨ <strong>Free users:</strong> Get comprehensive summary with bias and credibility scores</p>
            <p>🔓 <strong>Pro features:</strong> Deep dive analysis, source verification, author background checks, and more</p>
        </div>
    </div>
    
    <!-- Results section with updated tab labels -->
    <div id="results" class="results-section" style="display: none;">
        <div class="tabs-container">
            <div class="tabs">
                <button class="tab active" onclick="switchTab('summary')">
                    Summary & Analysis
                </button>
                <button class="tab" onclick="switchTab('bias')">
                    Political Bias <span class="pro-badge">Pro</span>
                </button>
                <button class="tab" onclick="switchTab('sources')">
                    Source Diversity <span class="pro-badge">Pro</span>
                </button>
                <button class="tab" onclick="switchTab('credibility')">
                    Credibility Check <span class="pro-badge">Pro</span>
                </button>
                <button class="tab" onclick="switchTab('cross-source')">
                    Cross-Source Verification <span class="pro-badge">Pro</span>
                </button>
                <button class="tab" onclick="switchTab('author')">
                    Author Analysis <span class="pro-badge">Pro</span>
                </button>
                <button class="tab" onclick="switchTab('style')">
                    Writing Style <span class="pro-badge">Pro</span>
                </button>
                <button class="tab" onclick="switchTab('temporal')">
                    Temporal Intelligence <span class="pro-badge">Pro</span>
                </button>
                <button class="tab" onclick="switchTab('pro')">
                    Unlock All Features ✨
                </button>
            </div>
            
            <!-- Tab Contents -->
            <div id="tab-contents">
                <!-- Summary Tab -->
                <div class="tab-content active" id="summary-content">
                    <!-- Content will be dynamically loaded -->
                </div>
                
                <!-- Other tabs -->
                <div class="tab-content" id="bias-content"></div>
                <div class="tab-content" id="sources-content"></div>
                <div class="tab-content" id="credibility-content"></div>
                <div class="tab-content" id="cross-source-content"></div>
                <div class="tab-content" id="author-content"></div>
                <div class="tab-content" id="style-content"></div>
                <div class="tab-content" id="temporal-content"></div>
                <div class="tab-content" id="pro-content"></div>
            </div>
        </div>
    </div>
</div>

<!-- Include modals -->
{% include 'partials/news-modals.html' %}

{% endblock %}

{% block scripts %}
<script src="{{ url_for('static', filename='js/news-helpers.js') }}"></script>
<script src="{{ url_for('static', filename='js/news-ui.js') }}"></script>
<script src="{{ url_for('static', filename='js/news-analysis.js') }}"></script>
<script src="{{ url_for('static', filename='js/news-results.js') }}"></script>
{% endblock %}
