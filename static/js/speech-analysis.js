/**
 * Speech Analysis Module
 * Handles the core analysis logic for speech fact-checking
 */

window.SpeechApp = window.SpeechApp || {};

window.SpeechApp.analysis = (function() {
    'use strict';
    
    // Private variables
    let currentAnalysis = null;
    let analysisInProgress = false;
    
    // Analysis stages for progress tracking
    const ANALYSIS_STAGES = [
        { id: 'transcribing', label: 'Transcribing Audio', duration: 3000 },
        { id: 'extracting', label: 'Extracting Claims', duration: 2500 },
        { id: 'factchecking', label: 'Fact-Checking Claims', duration: 4000 },
        { id: 'speaker', label: 'Analyzing Speaker', duration: 2000 },
        { id: 'emotional', label: 'Detecting Manipulation', duration: 2500 },
        { id: 'finalizing', label: 'Finalizing Report', duration: 1000 }
    ];
    
    /**
     * Initialize the analysis module
     */
    function initialize() {
        console.log('Speech analysis module initialized');
        setupEventListeners();
    }
    
    /**
     * Set up event listeners
     */
    function setupEventListeners() {
        // File input change listener
        const fileInput = document.getElementById('speechFile');
        if (fileInput) {
            fileInput.addEventListener('change', handleFileSelect);
        }
        
        // YouTube URL input listener
        const youtubeInput = document.getElementById('youtubeUrl');
        if (youtubeInput) {
            youtubeInput.addEventListener('paste', handleYouTubePaste);
        }
    }
    
    /**
     * Handle file selection
     */
    function handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            // Update file name display
            const fileName = document.querySelector('.file-name');
            if (fileName) {
                fileName.textContent = file.name;
            }
            
            // Show file info
            const fileSize = (file.size / (1024 * 1024)).toFixed(2);
            window.SpeechApp.ui.showInfo(`Selected: ${file.name} (${fileSize} MB)`);
        }
    }
    
    /**
     * Handle YouTube URL paste
     */
    function handleYouTubePaste(event) {
        setTimeout(() => {
            const url = event.target.value;
            if (window.SpeechApp.helpers.isValidYouTubeUrl(url)) {
                // Extract video ID and show preview
                const videoId = window.SpeechApp.helpers.extractYouTubeId(url);
                if (videoId) {
                    showYouTubePreview(videoId);
                }
            }
        }, 100);
    }
    
    /**
     * Show YouTube video preview
     */
    function showYouTubePreview(videoId) {
        const previewContainer = document.getElementById('youtubePreview');
        if (previewContainer) {
            previewContainer.innerHTML = `
                <div class="youtube-preview">
                    <img src="https://img.youtube.com/vi/${videoId}/hqdefault.jpg" alt="Video thumbnail">
                    <div class="preview-play">
                        <i class="fas fa-play-circle"></i>
                    </div>
                </div>
            `;
            previewContainer.style.display = 'block';
        }
    }
    
    /**
     * Analyze a file
     */
    function analyzeFile(file, tier) {
        if (analysisInProgress) {
            window.SpeechApp.ui.showError('Analysis already in progress');
            return;
        }
        
        analysisInProgress = true;
        currentAnalysis = {
            type: 'file',
            file: file,
            tier: tier,
            startTime: Date.now()
        };
        
        // Show loading state
        window.SpeechApp.ui.showAnalysisProgress();
        
        // Start progress animation
        animateProgress(0);
        
        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        formData.append('tier', tier);
        
        // Call API
        fetch('/api/analyze-speech', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(handleAnalysisResponse)
        .catch(handleAnalysisError);
    }
    
    /**
     * Analyze a YouTube video
     */
    function analyzeYouTube(url, tier) {
        if (analysisInProgress) {
            window.SpeechApp.ui.showError('Analysis already in progress');
            return;
        }
        
        analysisInProgress = true;
        currentAnalysis = {
            type: 'youtube',
            url: url,
            tier: tier,
            startTime: Date.now()
        };
        
        // Show loading state
        window.SpeechApp.ui.showAnalysisProgress();
        
        // Start progress animation
        animateProgress(0);
        
        // Call API
        fetch('/api/analyze-youtube-speech', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: url,
                tier: tier
            })
        })
        .then(response => response.json())
        .then(handleAnalysisResponse)
        .catch(handleAnalysisError);
    }
    
    /**
     * Animate progress through stages
     */
    function animateProgress(stageIndex) {
        if (stageIndex >= ANALYSIS_STAGES.length) {
            return;
        }
        
        const stage = ANALYSIS_STAGES[stageIndex];
        const progress = ((stageIndex + 1) / ANALYSIS_STAGES.length) * 100;
        
        // Update progress bar
        window.SpeechApp.ui.updateProgress(progress, stage.label);
        
        // Continue to next stage
        setTimeout(() => {
            if (analysisInProgress) {
                animateProgress(stageIndex + 1);
            }
        }, stage.duration);
    }
    
    /**
     * Handle successful analysis response
     */
    function handleAnalysisResponse(data) {
        analysisInProgress = false;
        
        if (data.success && data.results) {
            // Add analysis metadata
            data.results.analysisId = data.analysisId || 'SPEECH-' + Date.now();
            data.results.timestamp = new Date().toISOString();
            data.results.duration = Date.now() - currentAnalysis.startTime;
            
            // Store current results
            window.SpeechApp.results.setCurrentResults(data.results);
            
            // Hide loading and show results
            window.SpeechApp.ui.hideAnalysisProgress();
            window.SpeechApp.results.displayResults(data.results);
            
            // Scroll to results
            setTimeout(() => {
                const resultsSection = document.getElementById('speechResults');
                if (resultsSection) {
                    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }, 300);
            
        } else {
            throw new Error(data.error || 'Analysis failed');
        }
    }
    
    /**
     * Handle analysis error
     */
    function handleAnalysisError(error) {
        console.error('Analysis error:', error);
        analysisInProgress = false;
        
        window.SpeechApp.ui.hideAnalysisProgress();
        
        let errorMessage = 'An error occurred during analysis. ';
        
        if (error.message.includes('fetch')) {
            errorMessage += 'Please check your internet connection.';
        } else if (error.message.includes('size')) {
            errorMessage += 'The file is too large. Please try a smaller file.';
        } else if (error.message.includes('format')) {
            errorMessage += 'The file format is not supported.';
        } else {
            errorMessage += 'Please try again or contact support.';
        }
        
        window.SpeechApp.ui.showError(errorMessage);
        
        // Reset form
        window.resetSpeechAnalysis();
    }
    
    /**
     * Get sample analysis for demo
     */
    function getSampleAnalysis() {
        return {
            truthScore: 72,
            transcript: "This is a sample transcript of the analyzed speech...",
            duration: "5:23",
            speaker: {
                name: "John Doe",
                credibility: 78,
                expertise: "Political Science",
                historicalAccuracy: 75
            },
            claims: [
                {
                    text: "The unemployment rate dropped to 3.5% last quarter",
                    verdict: "True",
                    confidence: 95,
                    sources: ["Bureau of Labor Statistics", "Federal Reserve"]
                },
                {
                    text: "Crime rates have increased by 50% in major cities",
                    verdict: "Mostly False",
                    confidence: 88,
                    sources: ["FBI Crime Statistics", "Local Police Reports"]
                },
                {
                    text: "The new policy will save taxpayers $2 billion",
                    verdict: "Unverified",
                    confidence: 65,
                    sources: ["No reliable sources found"]
                }
            ],
            emotionalAnalysis: {
                score: 6.5,
                techniques: ["Appeal to fear", "Urgency creation", "Us vs Them rhetoric"],
                tone: "Alarmist with authoritative undertones"
            },
            fallacies: [
                {
                    type: "Strawman Argument",
                    example: "They want to destroy our way of life...",
                    severity: "Medium"
                },
                {
                    type: "False Dichotomy",
                    example: "Either we act now or face disaster...",
                    severity: "High"
                }
            ],
            contextAnalysis: {
                missingContext: ["Economic factors not mentioned", "Historical precedent ignored"],
                cherryPicking: true,
                fullPicture: false
            },
            overallAssessment: "The speech contains a mix of accurate and misleading claims. While some statistics are correctly cited, others lack context or are exaggerated. The speaker uses emotional manipulation techniques to strengthen their argument."
        };
    }
    
    /**
     * Run demo analysis
     */
    function runDemoAnalysis() {
        if (analysisInProgress) {
            window.SpeechApp.ui.showError('Analysis already in progress');
            return;
        }
        
        analysisInProgress = true;
        currentAnalysis = {
            type: 'demo',
            startTime: Date.now()
        };
        
        // Show loading state
        window.SpeechApp.ui.showAnalysisProgress();
        
        // Animate through stages
        animateProgress(0);
        
        // Simulate API delay
        setTimeout(() => {
            const demoResults = getSampleAnalysis();
            handleAnalysisResponse({
                success: true,
                results: demoResults
            });
        }, ANALYSIS_STAGES.reduce((total, stage) => total + stage.duration, 0));
    }
    
    // Public API
    return {
        initialize: initialize,
        analyzeFile: analyzeFile,
        analyzeYouTube: analyzeYouTube,
        runDemoAnalysis: runDemoAnalysis,
        isAnalyzing: () => analysisInProgress
    };
})();

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        window.SpeechApp.analysis.initialize();
    });
} else {
    window.SpeechApp.analysis.initialize();
}

console.log('Speech Analysis Module Loaded');
