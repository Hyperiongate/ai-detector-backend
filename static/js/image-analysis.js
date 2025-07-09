// Image Analysis Module
window.ImageApp = window.ImageApp || {};

window.ImageApp.analysis = (function() {
    'use strict';

    // Analysis configuration
    const ANALYSIS_STAGES = [
        { id: 'upload', text: 'Uploading Image', duration: 1500 },
        { id: 'extract', text: 'Extracting Features', duration: 2000 },
        { id: 'ai', text: 'AI Model Analysis', duration: 3000 },
        { id: 'forensic', text: 'Forensic Examination', duration: 2500 },
        { id: 'metadata', text: 'Metadata Analysis', duration: 2000 },
        { id: 'finalize', text: 'Finalizing Report', duration: 1000 }
    ];

    // Analyze image file
    async function analyzeImage(file, tier = 'pro') {
        console.log('Starting image analysis:', file.name, 'Tier:', tier);

        // Show loading animation
        window.ImageApp.ui.showLoadingAnimation();

        try {
            // Create FormData for file upload
            const formData = new FormData();
            formData.append('image', file);
            formData.append('tier', tier);
            formData.append('analysisType', 'comprehensive');

            // Simulate progress through stages
            await simulateAnalysisProgress();

            // Call API
            const response = await callAnalysisAPI(formData);

            if (response.success) {
                // Display results
                window.ImageApp.results.displayResults(response.results);
                
                // Track analytics
                trackAnalysis('success', file.type);
            } else {
                throw new Error(response.error || 'Analysis failed');
            }

        } catch (error) {
            console.error('Analysis error:', error);
            handleAnalysisError(error);
        } finally {
            window.ImageApp.ui.hideLoadingAnimation();
        }
    }

    // Simulate progress through analysis stages
    async function simulateAnalysisProgress() {
        let progress = 0;
        
        for (let i = 0; i < ANALYSIS_STAGES.length; i++) {
            const stage = ANALYSIS_STAGES[i];
            
            // Update stage UI
            window.ImageApp.ui.updateAnalysisStage(i + 1, stage.text);
            
            // Animate progress
            const stageProgress = ((i + 1) / ANALYSIS_STAGES.length) * 100;
            await animateProgress(progress, stageProgress, stage.duration);
            progress = stageProgress;
            
            // Small delay between stages
            await sleep(200);
        }
    }

    // Animate progress bar
    async function animateProgress(from, to, duration) {
        const startTime = Date.now();
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        return new Promise(resolve => {
            function update() {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const currentProgress = from + (to - from) * easeOutCubic(progress);
                
                if (progressFill) {
                    progressFill.style.width = `${currentProgress}%`;
                }
                
                if (progressText) {
                    progressText.textContent = `${Math.round(currentProgress)}% Complete`;
                }
                
                if (progress < 1) {
                    requestAnimationFrame(update);
                } else {
                    resolve();
                }
            }
            
            update();
        });
    }

    // Easing function for smooth animation
    function easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }

    // Call the analysis API
    async function callAnalysisAPI(formData) {
        try {
            const response = await fetch('/api/analyze-image', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('API call failed:', error);
            
            // Return mock data for development
            if (window.location.hostname === 'localhost') {
                return getMockAnalysisResults();
            }
            
            throw error;
        }
    }

    // Handle analysis errors
    function handleAnalysisError(error) {
        let errorMessage = 'An error occurred during analysis. Please try again.';
        
        if (error.message.includes('size')) {
            errorMessage = 'The image file is too large. Please use an image under 50MB.';
        } else if (error.message.includes('format')) {
            errorMessage = 'Unsupported image format. Please use JPG, PNG, GIF, WebP, or BMP.';
        } else if (error.message.includes('network')) {
            errorMessage = 'Network error. Please check your connection and try again.';
        }
        
        window.ImageApp.ui.showError(errorMessage);
    }

    // Track analysis for analytics
    function trackAnalysis(status, fileType) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'image_analysis', {
                'event_category': 'analysis',
                'event_label': fileType,
                'value': status === 'success' ? 1 : 0
            });
        }
    }

    // Get mock analysis results for development
    function getMockAnalysisResults() {
        return {
            success: true,
            results: {
                trustScore: 15,
                verdict: 'AI Generated',
                confidence: 94,
                aiGenerated: {
                    detected: true,
                    confidence: 94,
                    model: 'Stable Diffusion XL',
                    indicators: [
                        'Characteristic noise patterns in smooth gradients',
                        'Telltale artifacts in high-frequency details',
                        'Latent space signatures match SDXL architecture',
                        'Unnatural color transitions in shadows'
                    ]
                },
                manipulation: {
                    detected: false,
                    confidence: 12,
                    edits: []
                },
                metadata: {
                    hasExif: false,
                    software: 'Unknown',
                    created: 'Not available',
                    modified: 'Not available',
                    suspicious: ['No EXIF data present', 'No camera information']
                },
                forensics: {
                    compression: 'Low quality JPEG compression detected',
                    artifacts: ['Uniform noise distribution', 'Lack of natural image noise'],
                    cloning: false,
                    splicing: false
                },
                visualAnalysis: {
                    lighting: 'Inconsistent lighting angles detected',
                    shadows: 'Shadow directions do not match',
                    perspective: 'Minor perspective anomalies',
                    textures: 'Unnaturally smooth textures in some areas'
                },
                technicalDetails: {
                    resolution: '1024x1024',
                    colorSpace: 'sRGB',
                    bitDepth: '8-bit',
                    fileSize: '2.3 MB',
                    format: 'JPEG'
                }
            }
        };
    }

    // Utility sleep function
    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Export public methods
    return {
        analyzeImage: analyzeImage
    };
})();
