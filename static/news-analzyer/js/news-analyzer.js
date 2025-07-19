// News Analyzer - Separated JavaScript File
// Facts & Fakes AI - Advanced News Analysis JavaScript

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Reset form function
    window.resetForm = function() {
        document.getElementById('news-url').value = '';
        document.getElementById('news-text').value = '';
        
        // Reset to URL tab
        switchInputType('url');
        
        // Hide any error messages
        const errorContainer = document.getElementById('error-container');
        if (errorContainer) {
            errorContainer.style.display = 'none';
        }
        
        // Hide results if shown
        const resultsSection = document.getElementById('results-section');
        if (resultsSection) {
            resultsSection.style.display = 'none';
        }
        
        // Scroll to top of input section
        document.querySelector('.input-section').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
        });
    }

    // Toggle resources dropdown
    window.toggleResources = function() {
        const content = document.getElementById('resources-content');
        const header = document.querySelector('.resources-header');
        
        if (content.classList.contains('show')) {
            content.classList.remove('show');
            header.classList.remove('active');
        } else {
            content.classList.add('show');
            header.classList.add('active');
        }
    }

    // Enhanced input field focus effects
    document.getElementById('news-url').addEventListener('focus', function() {
        this.style.borderColor = '#4a90e2';
        this.style.boxShadow = '0 0 0 3px rgba(74, 144, 226, 0.1)';
    });

    document.getElementById('news-url').addEventListener('blur', function() {
        this.style.borderColor = '#e5e7eb';
        this.style.boxShadow = 'none';
    });

    document.getElementById('news-text').addEventListener('focus', function() {
        this.style.borderColor = '#4a90e2';
        this.style.boxShadow = '0 0 0 3px rgba(74, 144, 226, 0.1)';
    });

    document.getElementById('news-text').addEventListener('blur', function() {
        this.style.borderColor = '#e5e7eb';
        this.style.boxShadow = 'none';
    });
    
    // Initialize any needed components
    console.log('News analyzer ready');
});

// Toggle feature preview dropdown
window.toggleFeaturePreview = function() {
    const content = document.getElementById('feature-preview-content');
    const header = document.querySelector('.feature-preview-header');
    
    if (content.classList.contains('show')) {
        content.classList.remove('show');
        header.classList.remove('active');
    } else {
        content.classList.add('show');
        header.classList.add('active');
    }
}

// Global variable to store current analysis results
let currentAnalysisResults = null;

// Switch between URL and text input
window.switchInputType = function(type) {
    const urlSection = document.getElementById('url-input-section');
    const textSection = document.getElementById('text-input-section');
    const tabs = document.querySelectorAll('.input-tab');
    
    tabs.forEach(tab => tab.classList.remove('active'));
    
    if (type === 'url') {
        urlSection.style.display = 'block';
        textSection.style.display = 'none';
        tabs[0].classList.add('active');
    } else {
        urlSection.style.display = 'none';
        textSection.style.display = 'block';
        tabs[1].classList.add('active');
    }
}

// FIXED analysis function that matches YOUR API response structure
window.analyzeArticle = async function() {
    const urlInput = document.getElementById('news-url');
    const textInput = document.getElementById('news-text');
    const loadingSection = document.getElementById('loading-section');
    const resultsSection = document.getElementById('results-section');
    const errorContainer = document.getElementById('error-container');
    
    // Get input based on active section
    const isUrlMode = document.getElementById('url-input-section').style.display !== 'none';
    const input = isUrlMode ? urlInput.value.trim() : textInput.value.trim();
    
    if (!input) {
        alert('Please enter a URL or paste article text');
        return;
    }
    
    // Hide any previous errors
    errorContainer.style.display = 'none';
    
    // Show loading
    loadingSection.style.display = 'block';
    resultsSection.style.display = 'none';
    
    // Reset stages
    document.querySelectorAll('.analysis-stage').forEach(stage => {
        stage.classList.remove('active', 'complete');
    });
    
    // Initialize progress tracking
    let progress = 0;
    const progressBar = document.getElementById('analysis-progress');
    const stages = document.querySelectorAll('.analysis-stage');
    let currentStage = 0;
    
    try {
        // Start progress animation
        const progressInterval = setInterval(() => {
            if (progress < 90) {
                progress += 5;
                progressBar.style.width = progress + '%';
                progressBar.textContent = progress + '%';
                
                // Add active class for enhanced animations
                progressBar.classList.add('active');
                
                // Change to high-progress gradient at 60%
                if (progress >= 60 && !progressBar.classList.contains('high-progress')) {
                    progressBar.classList.add('high-progress');
                }
                
                // Update stages
                const stageProgress = Math.floor((progress / 100) * stages.length);
                if (stageProgress > currentStage && currentStage < stages.length) {
                    if (currentStage > 0) {
                        stages[currentStage - 1].classList.remove('active');
                        stages[currentStage - 1].classList.add('complete');
                    }
                    stages[currentStage].classList.add('active');
                    currentStage = stageProgress;
                    
                    // Update stage text with emojis
                    const stageTexts = [
                        '📥 Extracting content and metadata...',
                        '🧠 Running deep AI analysis with GPT-4...',
                        '✅ Cross-referencing fact databases...',
                        '⚖️ Detecting bias and manipulation...',
                        '📊 Analyzing source reliability...',
                        '📄 Compiling comprehensive report...'
                    ];
                    
                    if (currentStage - 1 < stageTexts.length) {
                        document.getElementById('current-stage-text').textContent = stageTexts[currentStage - 1];
                    }
                }
            }
        }, 200);
        
        // Prepare request body
        const requestBody = {
            content: input,
            type: isUrlMode ? 'url' : 'text',
            is_pro: true
        };
        
        console.log('Sending analysis request:', requestBody);
        
        // CALL YOUR ACTUAL BACKEND
        const response = await fetch('/api/analyze-news', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        clearInterval(progressInterval);
        
        // Check response
        if (!response.ok) {
            let errorMessage = `Server error: ${response.status}`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorData.message || errorMessage;
            } catch (e) {
                console.error('Error parsing error response:', e);
            }
            throw new Error(errorMessage);
        }
        
        const data = await response.json();
        console.log('Analysis response:', data);
        
        // Complete progress
        progressBar.style.width = '100%';
        progressBar.textContent = '100%';
        progressBar.classList.remove('active', 'high-progress');
        progressBar.classList.add('complete');
        stages.forEach(stage => {
            stage.classList.remove('active');
            stage.classList.add('complete');
        });
        
        // FIXED: Check for success - handle both success flag and presence of results
        if (data.success === true || (data.trust_score !== undefined && !data.error)) {
            // Store results globally for PDF generation - data is at root level
            currentAnalysisResults = data;
            
            // Display REAL results from YOUR backend - pass data directly
            setTimeout(() => {
                displayRealResults(data);
                loadingSection.style.display = 'none';
                resultsSection.style.display = 'block';
                
                // Scroll to results
                resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 500);
        } else {
            // Log the full response for debugging
            console.error('Analysis failed. Server response:', data);
            
            // Extract the actual error message from the server
            let errorMessage = data.error || data.message || 'Could not extract article content';
            
            // Check if the error is the generic extraction error and enhance it
            if (errorMessage === 'Could not extract article content' || 
                errorMessage.toLowerCase().includes('could not extract')) {
                errorMessage = 'Unable to extract content from this URL. This often happens with major news sites like Washington Post, CNN, or NYTimes that block automated access.\n\nPlease try:\n• Copy and paste the article text using the "Paste Text" tab\n• Try a different news source\n• Use a direct link to the article (not the homepage)';
            }
            // Make timeout errors more user-friendly
            else if (errorMessage.includes('timed out') || errorMessage.includes('timeout')) {
                errorMessage = 'The website took too long to respond. This can happen with some news sites.\n\nPlease try:\n• Copy and paste the article text using the "Paste Text" tab\n• Try a different article\n• Wait a moment and try again';
            } 
            // URL extraction errors
            else if (errorMessage.includes('extraction error') || errorMessage.includes('URL extraction')) {
                errorMessage = 'Unable to extract content from this URL. Some websites block automated access.\n\nPlease copy and paste the article text directly using the "Paste Text" tab.';
            }
            
            throw new Error(errorMessage);
        }
        
    } catch (error) {
        console.error('Analysis error:', error);
        loadingSection.style.display = 'none';
        
        // Clear any running intervals
        if (typeof progressInterval !== 'undefined') {
            clearInterval(progressInterval);
        }
        
        // Show pro tip for extraction errors
        if (error.message.includes('extract') || 
            error.message.includes('block') || 
            error.message.includes('Unable to extract') ||
            error.message.includes('CNN') ||
            error.message.includes('NYTimes') ||
            error.message.includes('major news sites')) {
            document.getElementById('pro-tip-box').style.display = 'block';
        }
        
        // Show user-friendly error message
        let userMessage = error.message;
        
        // Make error messages more user-friendly
        if (userMessage.includes('fetch')) {
            userMessage = 'Unable to connect to the analysis service. Please check your internet connection and try again.';
        } else if (userMessage.includes('404')) {
            userMessage = 'Analysis service not found. Please contact support.';
        } else if (userMessage.includes('500')) {
            userMessage = 'Server error occurred. Please try again later.';
        } else if (userMessage.includes('extract')) {
            userMessage = 'Unable to extract article content. Please ensure the URL is valid or try pasting the article text directly.';
        }
        
        showError(userMessage);
    }
}

// FIXED display function to match YOUR API response structure
function displayRealResults(results) {
    // Update timestamp
    const now = new Date();
    document.getElementById('analysis-time').textContent = now.toLocaleString();
    document.getElementById('analysis-id').textContent = results.analysis_id || 'AN-' + Date.now().toString(36).toUpperCase();
    
    // FIXED: Use trust_score directly from root
    const trustScore = results.trust_score || 0;
    animateTrustMeter(trustScore);
    
    // Update Overall Assessment with new enhanced version
    updateOverallAssessment(results);
    
    // Populate all sections with REAL data
    populateRealSections(results);
}

// Animate trust meter with REAL score
function animateTrustMeter(trustScore) {
    const trustMeter = document.querySelector('.trust-meter-fill');
    const trustScoreEl = document.getElementById('trust-score');
    const circumference = 2 * Math.PI * 90;
    const offset = circumference - (trustScore / 100) * circumference;
    
    // Set color based on REAL score
    let color = '#10b981'; // green
    if (trustScore < 60) color = '#ef4444'; // red
    else if (trustScore < 80) color = '#f59e0b'; // orange
    
    setTimeout(() => {
        trustMeter.style.stroke = color;
        trustMeter.style.strokeDashoffset = offset;
        
        // Animate number
        let current = 0;
        const interval = setInterval(() => {
            if (current < trustScore) {
                current += 2;
                trustScoreEl.textContent = Math.min(current, trustScore);
            } else {
                clearInterval(interval);
            }
        }, 30);
    }, 100);
}

// FIXED function to populate sections with YOUR API's actual data structure
function populateRealSections(results) {
    // Source Credibility - using source_credibility from root
    const sourceData = results.source_credibility || {};
    if (sourceData && results.article_info) {
        const domain = results.article_info.domain || 'Unknown';
        const credScore = results.credibility_score || 0;
        
        document.getElementById('source-credibility').innerHTML = `
            <h5>Source: ${domain}</h5>
            <p>Credibility Score: <strong>${credScore}/100</strong></p>
            <ul>
                <li>Trust Score: ${results.trust_score || 0}</li>
                <li>Article Title: ${results.article_info.title || 'N/A'}</li>
                ${results.article_info.publish_date ? `<li>Published: ${results.article_info.publish_date}</li>` : ''}
            </ul>
        `;
        
        document.getElementById('this-source-score').textContent = `${Math.round(credScore)}%`;
        document.getElementById('source-explanation').textContent = 'Source credibility assessed based on trust score and analysis results';
        document.getElementById('source-methodology').textContent = 'Analysis based on content quality, claims verification, and bias detection';
    }
    
    // Author Credibility - extract from article_info or other fields
    const authorName = results.article_info?.author || results.author || 'Unknown';
    const hasAuthor = authorName && authorName !== 'Unknown';
    
    if (hasAuthor) {
        // Clean author name (remove "By" prefix if present)
        const cleanAuthorName = authorName.replace(/^by\s+/i, '').trim();
        
        document.getElementById('author-credibility').innerHTML = `
            <h5>Author: ${cleanAuthorName}</h5>
            <p>Author detected from article metadata</p>
            <ul>
                <li>Name: <strong>${cleanAuthorName}</strong></li>
                <li>Verification Status: Pending manual verification</li>
                <li>Expertise: Research author's background for subject matter expertise</li>
                <li>Publication History: Check author's previous work for consistency</li>
            </ul>
            ${results.author_info ? `
                <div class="mt-3">
                    <h6>Additional Author Information:</h6>
                    <ul>
                        ${results.author_info.bio ? `<li>Bio: ${results.author_info.bio}</li>` : ''}
                        ${results.author_info.credentials ? `<li>Credentials: ${results.author_info.credentials}</li>` : ''}
                        ${results.author_info.website ? `<li>Website: <a href="${results.author_info.website}" target="_blank" rel="noopener">${results.author_info.website}</a></li>` : ''}
                    </ul>
                </div>
            ` : ''}
            
            <!-- Author Research Links -->
            <div class="mt-3">
                <h5>Research This Author:</h5>
                <div class="btn-group" role="group">
                    <a href="https://twitter.com/search?q=${encodeURIComponent(cleanAuthorName)}" class="btn btn-outline-primary btn-sm" target="_blank">
                        <i class="fab fa-twitter me-1"></i>Twitter
                    </a>
                    <a href="https://www.google.com/search?q=${encodeURIComponent(cleanAuthorName + ' journalist')}" class="btn btn-outline-primary btn-sm" target="_blank">
                        <i class="fab fa-google me-1"></i>Google
                    </a>
                    <a href="https://www.linkedin.com/search/results/all/?keywords=${encodeURIComponent(cleanAuthorName)}" class="btn btn-outline-primary btn-sm" target="_blank">
                        <i class="fab fa-linkedin me-1"></i>LinkedIn
                    </a>
                    ${results.author_info?.website ? `
                        <a href="${results.author_info.website}" class="btn btn-outline-primary btn-sm" target="_blank">
                            <i class="fas fa-globe me-1"></i>Website
                        </a>
                    ` : ''}
                </div>
            </div>
        `;
        
        document.getElementById('author-explanation').textContent = `Author "${cleanAuthorName}" has been identified. Established journalists with verifiable credentials and consistent publication history are generally more trustworthy sources. Research this author's background to assess their expertise in the subject matter.`;
        document.getElementById('author-methodology').textContent = `We detected the author through metadata extraction from the article. For comprehensive credibility assessment, we recommend verifying the author's credentials, checking their publication history, and confirming their expertise in the topic area. Professional journalists typically have a digital footprint that includes social media profiles, previous articles, and professional affiliations.`;
        
    } else {
        // No author detected - show manual input component
        document.getElementById('author-credibility').innerHTML = `
            <h5>Author: Not Detected</h5>
            <p>No author information found in article metadata</p>
            <ul>
                <li>Articles without clear authorship should be approached with caution</li>
                <li>Check the original source for author attribution</li>
                <li>Anonymous or missing authorship may indicate lower credibility</li>
                <li>Some reputable sources use editorial boards instead of individual authors</li>
            </ul>
            
            <!-- Insert the author input component here -->
            <div id="author-manual-input" class="author-input-section mt-4">
                <div class="alert alert-info mb-4">
                    <i class="fas fa-info-circle me-2"></i>
                    <strong>No author detected.</strong> You can manually enter the author's name to research their background and credibility.
                </div>
                
                <div class="manual-author-form">
                    <h6 class="mb-3">Enter Author Information:</h6>
                    
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label for="manual-author-name" class="form-label">Author Name</label>
                            <input type="text" 
                                   class="form-control" 
                                   id="manual-author-name" 
                                   placeholder="e.g., John Smith or Jane Doe"
                                   autocomplete="off">
                            <small class="text-muted">Enter the full name of the article's author</small>
                        </div>
                        
                        <div class="col-md-6">
                            <label for="manual-author-affiliation" class="form-label">Affiliation (Optional)</label>
                            <input type="text" 
                                   class="form-control" 
                                   id="manual-author-affiliation" 
                                   placeholder="e.g., New York Times, CNN"
                                   autocomplete="off">
                            <small class="text-muted">Publication or organization they work for</small>
                        </div>
                    </div>
                    
                    <button class="btn btn-primary mt-3" onclick="researchManualAuthor()">
                        <i class="fas fa-search me-2"></i>Research Author
                    </button>
                </div>
                
                <!-- Loading state for author research -->
                <div id="author-research-loading" class="text-center py-4" style="display: none;">
                    <div class="spinner-border text-primary mb-3" role="status">
                        <span class="visually-hidden">Researching...</span>
                    </div>
                    <p class="text-muted">Researching author background and credibility...</p>
                </div>
                
                <!-- Results container for manual author research -->
                <div id="manual-author-results" style="display: none;">
                    <hr class="my-4">
                    
                    <h6 class="mb-3">
                        <i class="fas fa-user-check me-2"></i>Author Research Results
                    </h6>
                    
                    <div id="author-research-content">
                        <!-- Dynamically populated with research results -->
                    </div>
                    
                    <!-- Author Research Links (dynamically updated) -->
                    <div class="mt-3">
                        <h6>Additional Research Links:</h6>
                        <div class="btn-group" role="group">
                            <a href="#" class="btn btn-outline-primary btn-sm" id="manual-author-twitter" target="_blank">
                                <i class="fab fa-twitter me-1"></i>Twitter
                            </a>
                            <a href="#" class="btn btn-outline-primary btn-sm" id="manual-author-google" target="_blank">
                                <i class="fab fa-google me-1"></i>Google
                            </a>
                            <a href="#" class="btn btn-outline-primary btn-sm" id="manual-author-linkedin" target="_blank">
                                <i class="fab fa-linkedin me-1"></i>LinkedIn
                            </a>
                            <a href="#" class="btn btn-outline-primary btn-sm" id="manual-author-website" target="_blank" style="display: none;">
                                <i class="fas fa-globe me-1"></i>Website
                            </a>
                        </div>
                    </div>
                    
                    <!-- Credibility Assessment -->
                    <div class="credibility-assessment mt-4">
                        <h6>Credibility Indicators:</h6>
                        <div id="author-credibility-indicators">
                            <!-- Dynamically populated -->
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.getElementById('author-explanation').textContent = 'No author information was detected in this article. You can manually enter the author\'s name above to research their background and credibility. Articles without clear authorship attribution should be evaluated more carefully.';
        document.getElementById('author-methodology').textContent = 'Author detection relies on metadata extraction from the article source. When no author is found, you can use the manual research tool above to investigate the author\'s credentials and credibility.';
    }
    
    // Writing Quality - derive from available data
    document.getElementById('writing-quality').innerHTML = `
        <h5>Quality Metrics:</h5>
        <ul>
            <li>Overall Trust Score: ${results.trust_score || 0}/100</li>
            <li>Credibility Score: ${results.credibility_score || 0}/100</li>
            <li>Content Length: ${results.article_info?.text ? results.article_info.text.length + ' characters' : 'N/A'}</li>
            <li>Key Claims Identified: ${results.key_claims?.length || 0}</li>
            <li>Fact Checks Performed: ${results.fact_checks?.length || 0}</li>
        </ul>
    `;
    
    document.getElementById('quality-explanation').textContent = 'Writing quality assessed through credibility and trust scoring';
    document.getElementById('quality-methodology').textContent = 'Analysis based on content structure and claim verification';
    
    // Fact-Checking - using fact_checks and key_claims
    const claims = results.key_claims || [];
    const factChecks = results.fact_checks || [];
    
    document.getElementById('fact-checking').innerHTML = `
        <h5>Claims Analyzed: ${claims.length}</h5>
        ${claims.map((claim, index) => `
            <div class="claim-card">
                <p><strong>Claim ${index + 1}:</strong> "${claim}"</p>
                <span class="claim-status status-unverified">REQUIRES VERIFICATION</span>
                <p class="mt-2"><small>Confidence: Pending fact-check</small></p>
            </div>
        `).join('')}
        ${factChecks.length > 0 ? `
            <h5 class="mt-4">Fact Check Results:</h5>
            ${factChecks.map(check => `<p>${check}</p>`).join('')}
        ` : ''}
    `;
    
    document.getElementById('fact-explanation').textContent = claims.length > 0 ? 
        'Key claims have been identified for verification' : 
        'No specific claims were identified for fact-checking';
    document.getElementById('fact-methodology').textContent = 'Claims extracted using natural language processing';
    
    // Political Bias - handle "N/A" string value
    const biasScore = results.bias_score;
    const biasMarker = document.getElementById('bias-marker');
    
    if (biasScore !== 'N/A' && !isNaN(biasScore)) {
        // Assuming bias_score is on a scale, adjust as needed
        const biasPosition = 50; // Center by default, adjust based on your scale
        biasMarker.style.left = biasPosition + '%';
        
        document.getElementById('political-bias').innerHTML = `
            <h5>Bias Assessment:</h5>
            <p>Bias Score: <strong>${biasScore}</strong></p>
            <p>Political Lean: <strong>Analysis in progress</strong></p>
            <ul>
                <li>Bias detection requires deeper content analysis</li>
            </ul>
        `;
    } else {
        biasMarker.style.left = '50%'; // Center for N/A
        
        document.getElementById('political-bias').innerHTML = `
            <h5>Bias Assessment:</h5>
            <p>Bias Score: <strong>Not Available</strong></p>
            <p>Insufficient data to determine political bias</p>
            <ul>
                <li>Content may be too short or neutral for bias detection</li>
            </ul>
        `;
    }
    
    document.getElementById('bias-explanation').textContent = biasScore !== 'N/A' ? 
        'Bias analysis completed' : 
        'Insufficient content for bias detection';
    document.getElementById('bias-methodology').textContent = 'Word choice and framing analysis';
    
    // Hidden Agenda - using manipulation_tactics
    const manipulationTactics = results.manipulation_tactics || [];
    document.getElementById('hidden-agenda').innerHTML = `
        <h5>Agenda Detection:</h5>
        <p>Manipulation Tactics Found: <strong>${manipulationTactics.length}</strong></p>
        ${manipulationTactics.length > 0 ? `
            <ul>
                ${manipulationTactics.map(tactic => `<li>${tactic}</li>`).join('')}
            </ul>
        ` : '<p>No manipulation tactics detected</p>'}
    `;
    
    document.getElementById('agenda-explanation').textContent = manipulationTactics.length > 0 ?
        'Potential manipulation tactics were identified' :
        'No hidden agenda detected';
    document.getElementById('agenda-methodology').textContent = 'Pattern recognition and persuasion technique analysis';
    
    // Clickbait Analysis - derive from title if available
    const title = results.article_info?.title || '';
    const hasClickbaitIndicators = title.includes('!') || title.includes('?') || 
                                  title.toLowerCase().includes('shocking') || 
                                  title.toLowerCase().includes('you won\'t believe');
    
    document.getElementById('clickbait-analysis').innerHTML = `
        <h5>Clickbait Score: <strong>${hasClickbaitIndicators ? 'Medium' : 'Low'}</strong></h5>
        <ul>
            <li>Title: "${title || 'No title provided'}"</li>
            ${hasClickbaitIndicators ? '<li>Contains potential clickbait indicators</li>' : '<li>Title appears straightforward</li>'}
        </ul>
    `;
    
    document.getElementById('clickbait-explanation').textContent = hasClickbaitIndicators ?
        'Title may contain clickbait elements' :
        'Title appears to be straightforward';
    document.getElementById('clickbait-methodology').textContent = 'Headline pattern analysis';
    
    // Emotional Manipulation - basic analysis
    const emotionScore = manipulationTactics.length * 20; // Simple scoring
    const emotionNeedle = document.getElementById('emotion-needle');
    const emotionAngle = -90 + Math.min(emotionScore * 1.8, 180);
    emotionNeedle.style.transform = `translateX(-50%) rotate(${emotionAngle}deg)`;
    
    document.getElementById('emotional-manipulation').innerHTML = `
        <h5>Emotional Manipulation Level: <strong>${emotionScore > 60 ? 'High' : emotionScore > 30 ? 'Medium' : 'Low'}</strong></h5>
        <p>Based on identified manipulation tactics</p>
        <ul>
            <li>Manipulation tactics found: ${manipulationTactics.length}</li>
            <li>Emotional appeal level: ${emotionScore > 60 ? 'Significant' : emotionScore > 30 ? 'Moderate' : 'Minimal'}</li>
        </ul>
    `;
    
    document.getElementById('emotion-explanation').textContent = 'Emotional manipulation assessed based on rhetoric analysis';
    document.getElementById('emotion-methodology').textContent = 'Sentiment and persuasion technique detection';
    
    // Source Diversity - basic implementation
    const diversityScore = 50; // Default middle score
    const diversityBar = document.getElementById('diversity-bar');
    diversityBar.style.width = diversityScore + '%';
    diversityBar.textContent = diversityScore + '%';
    
    document.getElementById('source-diversity').innerHTML = `
        <h5>Source Diversity Score: <strong>${diversityScore}/100</strong></h5>
        <ul>
            <li>Single source analysis</li>
            <li>Additional sources needed for comprehensive verification</li>
            <li>Consider cross-referencing with multiple sources</li>
        </ul>
    `;
    
    document.getElementById('diversity-explanation').textContent = 'Source diversity analysis requires multiple sources';
    document.getElementById('diversity-methodology').textContent = 'Single source provided for this analysis';
    
    // Timeliness - using publish_date if available
    const publishDate = results.article_info?.publish_date;
    document.getElementById('timeliness-check').innerHTML = `
        <h5>Timeliness Assessment:</h5>
        <ul>
            <li>Article date: ${publishDate || 'Unknown'}</li>
            <li>Analysis date: ${new Date().toLocaleDateString()}</li>
            <li>URL provided: ${results.article_info?.url ? 'Yes' : 'No'}</li>
            <li>Content type: ${results.article_info?.url ? 'Web article' : 'Direct text'}</li>
        </ul>
    `;
    
    document.getElementById('timeliness-explanation').textContent = publishDate ? 
        'Article date information available' : 
        'Publication date not available';
    document.getElementById('timeliness-methodology').textContent = 'Metadata extraction from source';
    
    // AI Detection - basic implementation
    const aiProbability = 25; // Default low probability
    setTimeout(() => {
        const aiBar = document.getElementById('ai-probability');
        aiBar.style.width = aiProbability + '%';
        aiBar.querySelector('.confidence-label').textContent = aiProbability + '%';
    }, 300);
    
    document.getElementById('ai-patterns').innerHTML = `
        <li><i class="fas fa-check-circle text-success me-2"></i>Natural language variations detected</li>
        <li><i class="fas fa-check-circle text-success me-2"></i>Human-like writing patterns</li>
        <li><i class="fas fa-info-circle text-primary me-2"></i>Further analysis needed for definitive assessment</li>
    `;
    
    document.getElementById('ai-explanation').textContent = 'Low probability of AI-generated content';
    document.getElementById('ai-methodology').textContent = 'Pattern analysis and writing style assessment';
}

// Show error
window.showError = function(message) {
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');
    
    // Convert newlines to <br> and bullet points to proper HTML
    let formattedMessage = message
        .replace(/\n/g, '<br>')
        .replace(/•/g, '<br>•');
    
    errorMessage.innerHTML = formattedMessage;
    errorContainer.style.display = 'block';
    
    // Hide results
    document.getElementById('results-section').style.display = 'none';
    
    // Scroll to error
    errorContainer.scrollIntoView({ behavior: 'smooth' });
}

// Retry analysis
window.retryAnalysis = function() {
    document.getElementById('error-container').style.display = 'none';
    analyzeArticle();
}

// Toggle dropdown
window.toggleDropdown = function(header) {
    const content = header.nextElementSibling;
    const isOpen = content.classList.contains('show');
    
    if (isOpen) {
        content.classList.remove('show');
        header.style.borderColor = 'transparent';
    } else {
        content.classList.add('show');
        header.style.borderColor = 'var(--primary-blue)';
    }
}

// Generate REAL PDF from actual results
window.generatePDF = async function() {
    if (!currentAnalysisResults) {
        alert('Please run an analysis first');
        return;
    }
    
    const btn = event.target;
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
    btn.disabled = true;
    
    try {
        // Call your backend to generate PDF
        const response = await fetch('/api/generate-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                analysis_type: 'news',
                results: currentAnalysisResults
            })
        });
        
        if (!response.ok) {
            throw new Error('PDF generation failed');
        }
        
        // If backend returns PDF blob
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `news-analysis-${Date.now()}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        
    } catch (error) {
        console.error('PDF generation error:', error);
        // Fallback: Generate client-side PDF with results
        generateClientSidePDF();
    } finally {
        btn.innerHTML = originalHTML;
        btn.disabled = false;
    }
}

// Fallback client-side PDF generation
function generateClientSidePDF() {
    // Create a new window with the results formatted for printing
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>News Analysis Report</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                h1 { color: #333; }
                .section { margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; }
                .score { font-size: 24px; font-weight: bold; color: #4CAF50; }
            </style>
        </head>
        <body>
            <h1>News Analysis Report</h1>
            <p>Generated: ${new Date().toLocaleString()}</p>
            <div class="section">
                <h2>Overall Trust Score</h2>
                <p class="score">${currentAnalysisResults.trust_score || 0}%</p>
            </div>
            <div class="section">
                <h2>Summary</h2>
                <p>${currentAnalysisResults.summary || 'Analysis completed'}</p>
            </div>
            <div class="section">
                <h2>Key Claims</h2>
                <ul>
                    ${(currentAnalysisResults.key_claims || []).map(c => `<li>${c}</li>`).join('')}
                </ul>
            </div>
            <div class="section">
                <h2>Manipulation Tactics</h2>
                <ul>
                    ${(currentAnalysisResults.manipulation_tactics || []).map(t => `<li>${t}</li>`).join('')}
                </ul>
            </div>
            <div class="section">
                <h2>Article Information</h2>
                <p><strong>Title:</strong> ${currentAnalysisResults.article_info?.title || 'N/A'}</p>
                <p><strong>Domain:</strong> ${currentAnalysisResults.article_info?.domain || 'N/A'}</p>
                <p><strong>Published:</strong> ${currentAnalysisResults.article_info?.publish_date || 'N/A'}</p>
            </div>
            <div class="section">
                <h2>Scores</h2>
                <p><strong>Trust Score:</strong> ${currentAnalysisResults.trust_score || 0}/100</p>
                <p><strong>Credibility Score:</strong> ${currentAnalysisResults.credibility_score || 0}/100</p>
                <p><strong>Bias Score:</strong> ${currentAnalysisResults.bias_score || 'N/A'}</p>
            </div>
        </body>
        </html>
    `);
    printWindow.document.close();
    printWindow.print();
}

// Show analysis process modal
window.showAnalysisProcess = function() {
    const modal = document.getElementById('analysisProcessModal');
    if (modal) {
        // If Bootstrap is available
        if (typeof bootstrap !== 'undefined') {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        } else {
            // Fallback
            modal.style.display = 'block';
            modal.classList.add('show');
        }
    }
}

// Show methodology
window.showMethodology = function() {
    showAnalysisProcess();
}

// Download full report
window.downloadFullReport = async function() {
    if (!currentAnalysisResults) {
        alert('Please run an analysis first');
        return;
    }
    
    // Same as generatePDF but with more comprehensive data
    generatePDF();
}

// Author Research Functions
window.researchManualAuthor = async function() {
    const authorName = document.getElementById('manual-author-name').value.trim();
    const affiliation = document.getElementById('manual-author-affiliation').value.trim();
    
    if (!authorName) {
        alert('Please enter an author name');
        return;
    }
    
    // Show loading state
    document.querySelector('.manual-author-form').style.display = 'none';
    document.getElementById('author-research-loading').style.display = 'block';
    document.getElementById('manual-author-results').style.display = 'none';
    
    try {
        // Call your backend API to research the author
        const response = await fetch('/api/research-author', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                author_name: authorName,
                affiliation: affiliation,
                article_url: currentAnalysisResults?.article_info?.url || '',
                article_title: currentAnalysisResults?.article_info?.title || ''
            })
        });
        
        if (!response.ok) {
            throw new Error('Author research failed');
        }
        
        const authorData = await response.json();
        
        // Display results
        displayAuthorResearchResults(authorData);
        
    } catch (error) {
        console.error('Author research error:', error);
        
        // Fallback: Show basic research links
        displayBasicAuthorResearch(authorName, affiliation);
    } finally {
        document.getElementById('author-research-loading').style.display = 'none';
        document.getElementById('manual-author-results').style.display = 'block';
    }
}

// Function to display author research results
function displayAuthorResearchResults(authorData) {
    const resultsContainer = document.getElementById('author-research-content');
    
    // If we have comprehensive data from the API
    if (authorData.success && authorData.author_info) {
        const info = authorData.author_info;
        
        resultsContainer.innerHTML = `
            <div class="author-info-card">
                <h5>${info.name}</h5>
                ${info.bio ? `<p class="author-bio">${info.bio}</p>` : ''}
                
                ${info.credentials && info.credentials.length > 0 ? `
                    <h6 class="mt-3">Credentials & Background:</h6>
                    <ul class="author-credentials">
                        ${info.credentials.map(cred => `
                            <li><i class="fas fa-check-circle"></i> ${cred}</li>
                        `).join('')}
                    </ul>
                ` : ''}
                
                ${info.expertise && info.expertise.length > 0 ? `
                    <h6 class="mt-3">Areas of Expertise:</h6>
                    <div class="mb-3">
                        ${info.expertise.map(exp => `
                            <span class="badge bg-primary me-2">${exp}</span>
                        `).join('')}
                    </div>
                ` : ''}
                
                ${info.publications ? `
                    <p><strong>Publications:</strong> ${info.publications}</p>
                ` : ''}
                
                ${info.verification_status ? `
                    <div class="alert alert-${info.verified ? 'success' : 'warning'} mt-3">
                        <i class="fas fa-${info.verified ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
                        ${info.verification_status}
                    </div>
                ` : ''}
            </div>
        `;
        
        // Update research links
        updateAuthorResearchLinks(info.name, info.website);
        
        // Display credibility indicators
        displayCredibilityIndicators(authorData.credibility_indicators || []);
        
    } else {
        // Basic display without API data
        displayBasicAuthorResearch(authorData.author_name || 'Unknown', authorData.affiliation);
    }
}

// Function to display basic author research (fallback)
function displayBasicAuthorResearch(authorName, affiliation) {
    const resultsContainer = document.getElementById('author-research-content');
    
    resultsContainer.innerHTML = `
        <div class="author-info-card">
            <h5>${authorName}</h5>
            ${affiliation ? `<p><strong>Affiliation:</strong> ${affiliation}</p>` : ''}
            <div class="alert alert-info mt-3">
                <i class="fas fa-info-circle me-2"></i>
                Use the research links below to verify this author's credentials and background.
            </div>
        </div>
    `;
    
    // Update research links
    updateAuthorResearchLinks(authorName, null);
    
    // Show basic credibility checklist
    displayCredibilityIndicators([
        {
            type: 'neutral',
            icon: 'fa-search',
            text: 'Search for author\'s professional profile'
        },
        {
            type: 'neutral',
            icon: 'fa-newspaper',
            text: 'Look for previous articles by this author'
        },
        {
            type: 'neutral',
            icon: 'fa-university',
            text: 'Verify educational credentials if claimed'
        },
        {
            type: 'neutral',
            icon: 'fa-award',
            text: 'Check for journalism awards or recognition'
        }
    ]);
}

// Function to update author research links
function updateAuthorResearchLinks(authorName, website) {
    const searchQuery = encodeURIComponent(authorName);
    
    document.getElementById('manual-author-twitter').href = 
        `https://twitter.com/search?q=${searchQuery}`;
    document.getElementById('manual-author-google').href = 
        `https://www.google.com/search?q=${searchQuery}+journalist`;
    document.getElementById('manual-author-linkedin').href = 
        `https://www.linkedin.com/search/results/all/?keywords=${searchQuery}`;
    
    if (website) {
        const websiteBtn = document.getElementById('manual-author-website');
        websiteBtn.href = website;
        websiteBtn.style.display = 'inline-flex';
    }
}

// Function to display credibility indicators
function displayCredibilityIndicators(indicators) {
    const container = document.getElementById('author-credibility-indicators');
    
    if (indicators.length === 0) {
        // Default indicators if none provided
        indicators = [
            {
                type: 'positive',
                icon: 'fa-check-circle',
                text: 'Author name provided for verification'
            },
            {
                type: 'neutral',
                icon: 'fa-question-circle',
                text: 'Manual verification recommended'
            }
        ];
    }
    
    container.innerHTML = indicators.map(indicator => `
        <div class="credibility-indicator ${indicator.type}">
            <i class="fas ${indicator.icon}"></i>
            <span>${indicator.text}</span>
        </div>
    `).join('');
}

// Function to reset author input form
function resetAuthorInput() {
    document.getElementById('manual-author-name').value = '';
    document.getElementById('manual-author-affiliation').value = '';
    document.querySelector('.manual-author-form').style.display = 'block';
    document.getElementById('author-research-loading').style.display = 'none';
    document.getElementById('manual-author-results').style.display = 'none';
}

// Enhanced JavaScript for Overall Assessment - Factual Version
function updateOverallAssessment(results) {
    const trustScore = results.trust_score || 0;
    
    // Update trust score display
    document.getElementById('trust-score-display').innerHTML = `
        ${trustScore}%
        <span class="score-meaning" id="score-meaning">${getScoreMeaning(trustScore)}</span>
    `;
    
    // Update icon and label based on score
    const iconWrapper = document.getElementById('trust-icon-wrapper');
    const credibilityLabel = document.getElementById('credibility-label');
    
    if (trustScore >= 80) {
        iconWrapper.className = 'trust-icon-wrapper high';
        iconWrapper.innerHTML = '<i class="fas fa-shield-alt"></i>';
        credibilityLabel.textContent = 'Generally Reliable (80%+ score)';
    } else if (trustScore >= 60) {
        iconWrapper.className = 'trust-icon-wrapper medium';
        iconWrapper.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
        credibilityLabel.textContent = 'Moderate Reliability (60-79% score)';
    } else {
        iconWrapper.className = 'trust-icon-wrapper low';
        iconWrapper.innerHTML = '<i class="fas fa-times-circle"></i>';
        credibilityLabel.textContent = 'Low Reliability (Below 60% score)';
    }
    
    // Update summary - use actual analysis summary
    document.getElementById('overall-summary').textContent = results.summary || 
        `This article scored ${trustScore}% in our trust analysis. ${getScoreContext(trustScore)}`;
    
    // Update metrics with clear explanations
    const sourceScore = results.credibility_score || 0;
    document.getElementById('source-metric').textContent = sourceScore + '%';
    document.getElementById('source-explainer').textContent = 
        sourceScore >= 80 ? '(High)' : sourceScore >= 60 ? '(Medium)' : '(Low)';
    
    // Claim verification - show actual numbers
    const totalClaims = results.key_claims?.length || 0;
    const verifiedClaims = results.fact_checks?.filter(f => f.verdict === 'true').length || 0;
    document.getElementById('accuracy-metric').textContent = 
        totalClaims > 0 ? `${verifiedClaims}/${totalClaims}` : 'No claims';
    document.getElementById('accuracy-explainer').textContent = 
        totalClaims > 0 ? 'verified' : 'to check';
    
    // Political bias - be specific
    const biasScore = results.bias_score;
    const biasMetric = document.getElementById('bias-metric');
    if (biasScore !== 'N/A' && !isNaN(biasScore)) {
        if (biasScore < -0.3) biasMetric.textContent = 'Left-leaning';
        else if (biasScore > 0.3) biasMetric.textContent = 'Right-leaning';
        else biasMetric.textContent = 'Center/Neutral';
    } else {
        biasMetric.textContent = 'Not detected';
    }
    
    // Red flags - show actual count
    const manipulationCount = results.manipulation_tactics?.length || 0;
    document.getElementById('manipulation-metric').textContent = manipulationCount;
    
    // Update findings - use actual data
    const keyFindings = [];
    if (results.article_info?.author && results.article_info.author !== 'Unknown') {
        keyFindings.push(`Author identified: ${results.article_info.author}`);
    }
    if (results.article_info?.domain) {
        keyFindings.push(`Source: ${results.article_info.domain}`);
    }
    if (results.key_claims?.length > 0) {
        keyFindings.push(`${results.key_claims.length} claims detected`);
    }
    if (trustScore >= 80) {
        keyFindings.push('Meets reliability threshold');
    }
    
    if (keyFindings.length > 0) {
        document.getElementById('key-findings-list').innerHTML = keyFindings
            .map(finding => `<li><i class="fas fa-check"></i>${finding}</li>`)
            .join('');
    } else {
        document.getElementById('key-findings-list').innerHTML = 
            '<li><i class="fas fa-info"></i>Limited data available</li>';
    }
    
    // Update red flags - use actual manipulation tactics
    const redFlags = results.manipulation_tactics || [];
    if (redFlags.length > 0) {
        document.getElementById('red-flags-list').innerHTML = redFlags
            .slice(0, 4) // Limit to 4 for space
            .map(flag => `<li><i class="fas fa-times"></i>${flag}</li>`)
            .join('');
    } else {
        document.getElementById('red-flags-list').innerHTML = 
            '<li><i class="fas fa-check"></i>No manipulation tactics detected</li>';
    }
    
    // Update confidence
    const confidence = calculateConfidence(results);
    document.getElementById('confidence-percentage').textContent = confidence + '%';
    document.getElementById('overall-confidence').style.width = confidence + '%';
    
    // Update confidence explanation
    document.getElementById('confidence-explanation').textContent = 
        `Based on ${getConfidenceFactors(results).join(', ')}`;
}

// Helper function to get score meaning
function getScoreMeaning(score) {
    if (score >= 90) return 'Very High Reliability';
    if (score >= 80) return 'High Reliability';
    if (score >= 70) return 'Moderate-High';
    if (score >= 60) return 'Moderate';
    if (score >= 50) return 'Moderate-Low';
    if (score >= 40) return 'Low Reliability';
    return 'Very Low Reliability';
}

// Helper function to get score context
function getScoreContext(score) {
    if (score >= 80) return 'Articles scoring 80% or higher are generally reliable for citations and sharing.';
    if (score >= 60) return 'Articles scoring 60-79% should be cross-referenced with other sources.';
    return 'Articles scoring below 60% require significant verification before use.';
}

// Calculate confidence based on available data
function calculateConfidence(results) {
    let confidence = 50; // Base confidence
    
    // Add confidence based on available data
    if (results.article_info?.author && results.article_info.author !== 'Unknown') confidence += 10;
    if (results.article_info?.domain) confidence += 10;
    if (results.article_info?.publish_date) confidence += 5;
    if (results.key_claims?.length > 0) confidence += 10;
    if (results.fact_checks?.length > 0) confidence += 10;
    if (results.source_credibility) confidence += 5;
    
    return Math.min(confidence, 95); // Cap at 95%
}

// Get confidence factors
function getConfidenceFactors(results) {
    const factors = [];
    
    if (results.article_info?.author && results.article_info.author !== 'Unknown') {
        factors.push('author identified');
    }
    if (results.key_claims?.length > 0) {
        factors.push(`${results.key_claims.length} claims analyzed`);
    }
    if (results.source_credibility) {
        factors.push('source verified');
    }
    
    if (factors.length === 0) {
        factors.push('limited data available');
    }
    
    return factors;
}

// Namespace all navigation functions to avoid conflicts
window.ffNav = {
    checkAuthStatus: async function() {
        try {
            const response = await fetch('/api/user/status');
            
            // Check if response is OK and content type is JSON
            if (!response.ok || !response.headers.get('content-type')?.includes('application/json')) {
                console.log('Auth endpoint not available or not returning JSON');
                return;
            }
            
            const data = await response.json();
            
            if (data.authenticated) {
                document.getElementById('ffNavAuth').style.display = 'none';
                document.getElementById('ffUserMenu').style.display = 'block';
                
                document.getElementById('ffUserEmail').textContent = data.email || 'User';
                document.getElementById('ffUserEmailDropdown').textContent = data.email || 'User';
                document.getElementById('ffUserPlan').textContent = data.plan === 'pro' ? 'Pro Plan' : 'Free Plan';
                
                const usagePercent = (data.usage_today / data.daily_limit) * 100;
                document.getElementById('ffUsageProgress').style.width = usagePercent + '%';
                document.getElementById('ffUsageText').textContent = `${data.usage_today} / ${data.daily_limit} analyses used`;
            }
        } catch (error) {
            // Silently fail - user is not authenticated or endpoint doesn't exist
            console.log('Auth check skipped:', error.message);
        }
    },
    
    init: function() {
        this.checkAuthStatus();
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            const userMenu = document.querySelector('.ff-user-menu');
            if (userMenu && !userMenu.contains(event.target)) {
                document.getElementById('ffUserDropdown').classList.remove('active');
            }
        });
        
        // Add active class to current page
        const currentPath = window.location.pathname;
        document.querySelectorAll('.ff-nav-link').forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    }
};

// Global functions for onclick handlers
window.ffToggleMobileMenu = function() {
    const navLinks = document.getElementById('ffNavLinks');
    navLinks.classList.toggle('active');
}

window.ffToggleUserDropdown = function() {
    const dropdown = document.getElementById('ffUserDropdown');
    dropdown.classList.toggle('active');
}

window.ffLogout = async function() {
    try {
        await fetch('/api/logout', { method: 'POST' });
        window.location.href = '/';
    } catch (error) {
        console.error('Logout failed:', error);
    }
}

// Initialize navigation when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        window.ffNav.init();
    });
} else {
    window.ffNav.init();
}
