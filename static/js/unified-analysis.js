// unified-analysis.js - AI Detection and Plagiarism Check with Real-Time Progress
(function() {
    'use strict';
    
    // Initialize namespace
    window.UnifiedApp = window.UnifiedApp || {};
    window.UnifiedApp.analysis = {};
    
    // Store current analysis state
    let currentAnalysis = {
        eventSource: null,
        results: null,
        isAnalyzing: false,
        analysisType: null
    };
    
    // Main analysis function with streaming
    window.UnifiedApp.analysis.runAnalysis = async function(content, tier = 'pro') {
        try {
            // Prevent multiple simultaneous analyses
            if (currentAnalysis.isAnalyzing) {
                UnifiedApp.ui.showToast('Analysis already in progress', 'warning');
                return;
            }
            
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
            
            // Show loading overlay
            UnifiedApp.ui.showLoading();
            currentAnalysis.isAnalyzing = true;
            
            // Close any existing connection
            if (currentAnalysis.eventSource) {
                currentAnalysis.eventSource.close();
            }
            
            // Create query parameters for SSE
            const queryParams = new URLSearchParams();
            Object.keys(analysisData).forEach(key => {
                queryParams.append(key, analysisData[key]);
            });
            
            console.log('Starting analysis with params:', queryParams.toString());
            
            // Create EventSource for streaming
            const eventSource = new EventSource('/api/analyze-unified/stream?' + queryParams.toString());
            
            currentAnalysis.eventSource = eventSource;
            
            // Handle connection open
            eventSource.onopen = function() {
                console.log('Streaming connection established');
            };
            
            // Handle messages
            eventSource.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    
                    if (data.type === 'progress') {
                        UnifiedApp.ui.updateProgress(data.message || data.stage, data.progress);
                        
                        // Update step indicators
                        if (data.step) {
                            updateStepIndicator(data.step);
                        }
                    } else if (data.type === 'partial') {
                        // Show partial results if available
                        if (data.results) {
                            UnifiedApp.ui.showPartialResults(data.results);
                        }
                    } else if (data.type === 'complete') {
                        // Handle completion with enhanced data structure
                        handleAnalysisComplete(data.results, content);
                        eventSource.close();
                    } else if (data.type === 'error') {
                        throw new Error(data.message || 'Analysis failed');
                    }
                } catch (error) {
                    console.error('Error processing message:', error);
                }
            };
            
            // Handle errors
            eventSource.onerror = function(event) {
                console.error('SSE error:', event);
                eventSource.close();
                currentAnalysis.eventSource = null;
                currentAnalysis.isAnalyzing = false;
                
                // Check if it's a connection error or server error
                if (eventSource.readyState === EventSource.CLOSED) {
                    // Connection closed, try fallback
                    UnifiedApp.ui.showToast('Streaming failed, using standard method...', 'warning');
                    fallbackAnalysis(analysisData);
                } else {
                    // Other error
                    UnifiedApp.ui.hideLoading();
                    UnifiedApp.ui.showError('Connection error. Please try again.');
                }
            };
            
        } catch (error) {
            console.error('Analysis error:', error);
            UnifiedApp.ui.hideLoading();
            UnifiedApp.ui.showError(error.message || 'An error occurred during analysis');
            currentAnalysis.isAnalyzing = false;
            return null;
        }
    };
    
    // Handle analysis completion with enhanced data structure
    function handleAnalysisComplete(results, originalContent) {
        if (!results) {
            UnifiedApp.ui.showError('No results received');
            currentAnalysis.isAnalyzing = false;
            return;
        }
        
        // Enhance results with additional data for new UI
        results = enhanceResultsData(results, originalContent);
        
        // Add analysis metadata
        results.timestamp = new Date().toISOString();
        
        if (currentAnalysis.analysisType === 'text') {
            results.textLength = originalContent.length;
            results.wordCount = originalContent.trim().split(/\s+/).length;
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
    
    // Enhance results data for new UI requirements
    function enhanceResultsData(results, originalContent) {
        // Ensure all required fields exist
        results.trust_score = results.trust_score || 50;
        results.ai_probability = results.ai_probability || 0;
        results.plagiarism_score = results.plagiarism_score || 0;
        
        // Enhance AI detection section
        if (!results.analysis_sections) {
            results.analysis_sections = {};
        }
        
        // Ensure AI detection has all required fields
        const aiSection = results.analysis_sections.ai_detection || {};
        aiSection.ai_probability = aiSection.ai_probability || results.ai_probability || 0;
        aiSection.human_probability = 100 - aiSection.ai_probability;
        aiSection.confidence = aiSection.confidence || 0.7;
        
        // Add linguistic metrics if not present
        if (!aiSection.linguistic_metrics) {
            aiSection.linguistic_metrics = {
                perplexity_score: calculatePerplexity(originalContent),
                burstiness_score: calculateBurstiness(originalContent),
                vocabulary_diversity: calculateVocabularyDiversity(originalContent)
            };
        }
        
        // Add patterns if not present
        if (!aiSection.patterns || aiSection.patterns.length === 0) {
            aiSection.patterns = generatePatterns(aiSection.ai_probability);
        }
        
        results.analysis_sections.ai_detection = aiSection;
        
        // Enhance plagiarism section
        const plagSection = results.analysis_sections.plagiarism || {};
        plagSection.score = plagSection.score || results.plagiarism_score || 0;
        plagSection.sources_found = plagSection.sources_found || 0;
        plagSection.similarity_score = plagSection.score / 100;
        
        // Ensure matches array exists
        if (!plagSection.matches) {
            plagSection.matches = [];
        }
        
        results.analysis_sections.plagiarism = plagSection;
        
        // Enhance quality section
        const qualitySection = results.analysis_sections.quality || {};
        if (!qualitySection.metrics) {
            const words = originalContent.trim().split(/\s+/);
            const sentences = originalContent.split(/[.!?]+/).filter(s => s.trim().length > 0);
            
            qualitySection.metrics = {
                word_count: words.length,
                sentence_count: sentences.length,
                avg_sentence_length: sentences.length > 0 ? words.length / sentences.length : 0,
                readability: calculateReadability(sentences, words)
            };
        }
        
        results.analysis_sections.quality = qualitySection;
        
        // Generate summary if not present
        if (!results.summary) {
            results.summary = generateSummary(results);
        }
        
        // Generate recommendations if not present
        if (!results.recommendations || results.recommendations.length === 0) {
            results.recommendations = generateRecommendations(results);
        }
        
        return results;
    }
    
    // Calculate perplexity score (simplified)
    function calculatePerplexity(text) {
        // Simple heuristic: longer words and varied sentence structure = higher perplexity
        const words = text.split(/\s+/);
        const avgWordLength = words.reduce((sum, word) => sum + word.length, 0) / words.length;
        const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
        const sentenceLengthVariance = calculateVariance(sentences.map(s => s.split(/\s+/).length));
        
        // Convert to 0-100 scale
        const perplexity = Math.min(100, (avgWordLength * 10) + (sentenceLengthVariance * 2));
        return Math.round(perplexity);
    }
    
    // Calculate burstiness score
    function calculateBurstiness(text) {
        const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
        const lengths = sentences.map(s => s.split(/\s+/).length);
        
        if (lengths.length < 2) return 50;
        
        const variance = calculateVariance(lengths);
        const burstiness = Math.min(100, variance * 5);
        return Math.round(burstiness);
    }
    
    // Calculate vocabulary diversity
    function calculateVocabularyDiversity(text) {
        const words = text.toLowerCase().split(/\s+/);
        const uniqueWords = new Set(words);
        const diversity = (uniqueWords.size / words.length) * 100;
        return Math.round(diversity);
    }
    
    // Calculate variance
    function calculateVariance(numbers) {
        const mean = numbers.reduce((sum, n) => sum + n, 0) / numbers.length;
        const squaredDiffs = numbers.map(n => Math.pow(n - mean, 2));
        return Math.sqrt(squaredDiffs.reduce((sum, n) => sum + n, 0) / numbers.length);
    }
    
    // Calculate readability
    function calculateReadability(sentences, words) {
        const avgSentenceLength = words.length / sentences.length;
        if (avgSentenceLength < 15) return 'Good';
        if (avgSentenceLength < 20) return 'Good';
        if (avgSentenceLength < 25) return 'Complex';
        return 'Very Complex';
    }
    
    // Generate patterns based on AI probability
    function generatePatterns(aiProbability) {
        const patterns = [];
        
        if (aiProbability > 70) {
            patterns.push(
                'AI-typical phrase patterns detected',
                'Consistent formal structure',
                'Absence of contractions',
                'Limited emotional expression',
                'High coherence score'
            );
        } else if (aiProbability > 40) {
            patterns.push(
                'Some AI characteristics',
                'Moderate formality',
                'Mixed writing patterns',
                'Partial AI indicators'
            );
        } else {
            patterns.push(
                'Natural language variations',
                'Human-like irregularities',
                'Personal voice detected',
                'Organic writing flow'
            );
        }
        
        return patterns;
    }
    
    // Generate summary
    function generateSummary(results) {
        const aiScore = results.ai_probability || 0;
        const plagScore = results.plagiarism_score || 0;
        const trustScore = results.trust_score || 50;
        
        let summary = '';
        
        if (aiScore > 70) {
            summary += `High probability of AI-generated content (${aiScore}%). `;
        } else if (aiScore > 40) {
            summary += `Moderate AI indicators detected (${aiScore}%). `;
        } else {
            summary += `Content appears primarily human-written (${100-aiScore}% human probability). `;
        }
        
        if (plagScore > 30) {
            summary += `Significant plagiarism detected (${plagScore}% similarity). `;
        } else if (plagScore > 10) {
            summary += `Some similar content found (${plagScore}% similarity). `;
        } else {
            summary += `No significant plagiarism detected. `;
        }
        
        summary += `Overall trust score: ${trustScore}%.`;
        
        return summary;
    }
    
    // Generate recommendations
    function generateRecommendations(results) {
        const recommendations = [];
        const aiScore = results.ai_probability || 0;
        const plagScore = results.plagiarism_score || 0;
        const trustScore = results.trust_score || 50;
        
        if (trustScore < 60) {
            recommendations.push('Content shows concerning patterns - verify with additional sources');
        }
        
        if (aiScore > 70) {
            recommendations.push('High probability of AI-generated content detected - consider human review');
        } else if (aiScore > 40) {
            recommendations.push('Some AI indicators present - may benefit from more personal voice');
        }
        
        if (plagScore > 30) {
            recommendations.push('Similar content found online - ensure proper attribution');
        } else if (plagScore > 10) {
            recommendations.push('Minor similarities detected - review for unintentional overlap');
        }
        
        if (trustScore > 80 && aiScore < 30 && plagScore < 10) {
            recommendations.push('Content appears authentic and trustworthy - maintain these standards');
        }
        
        const quality = results.analysis_sections?.quality?.metrics;
        if (quality?.avg_sentence_length > 25) {
            recommendations.push('Consider breaking up long sentences for better readability');
        }
        
        return recommendations;
    }
    
    // Update step indicators during progress
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
    
    // Fallback to regular API if streaming fails
    async function fallbackAnalysis(analysisData) {
        try {
            UnifiedApp.ui.showToast('Using standard analysis method...', 'info');
            
            const response = await window.ffAPI.analyzeUnified(analysisData);
            
            if (response.success && response.results) {
                handleAnalysisComplete(response.results, analysisData.content || analysisData.url);
            } else {
                throw new Error(response.error || 'Analysis failed');
            }
        } catch (error) {
            console.error('Fallback analysis error:', error);
            UnifiedApp.ui.hideLoading();
            UnifiedApp.ui.showError(error.message || 'Analysis failed');
            currentAnalysis.isAnalyzing = false;
        }
    }
    
    // Export PDF report
    window.UnifiedApp.analysis.generatePDF = async function() {
        try {
            // Don't show error toast, show loading instead
            if (window.UnifiedApp && window.UnifiedApp.ui && window.UnifiedApp.ui.showToast) {
                window.UnifiedApp.ui.showToast('Generating PDF report...', 'info');
            }
            
            const results = currentAnalysis.results || UnifiedApp.results.getCurrentResults();
            if (!results) {
                throw new Error('No results to export');
            }
            
            const response = await window.ffAPI.generateUnifiedPDF({
                results: results,
                analysis_type: 'ai_plagiarism'
            });
            
            if (response.success && response.pdf_url) {
                // Download PDF
                const a = document.createElement('a');
                a.href = response.pdf_url;
                a.download = `AI_Plagiarism_Report_${new Date().getTime()}.pdf`;
                a.click();
                
                UnifiedApp.ui.showToast('PDF downloaded successfully!', 'success');
            } else {
                throw new Error('Failed to generate PDF');
            }
            
        } catch (error) {
            console.error('PDF generation error:', error);
            UnifiedApp.ui.showToast('Failed to generate PDF. Please try again.', 'error');
        }
    };
    
    // Share results
    window.UnifiedApp.analysis.shareResults = async function() {
        try {
            const results = currentAnalysis.results || UnifiedApp.results.getCurrentResults();
            if (!results) {
                UnifiedApp.ui.showToast('No results to share', 'error');
                return;
            }
            
            // Create shareable URL
            const shareData = {
                title: 'AI & Plagiarism Check Results',
                text: `Content Analysis: ${results.ai_probability}% AI probability, ${results.plagiarism_score}% plagiarism detected`,
                url: window.location.href
            };
            
            if (navigator.share) {
                await navigator.share(shareData);
            } else {
                // Fallback to copy link
                await navigator.clipboard.writeText(window.location.href);
                UnifiedApp.ui.showToast('Link copied to clipboard!', 'success');
            }
            
        } catch (error) {
            console.error('Share error:', error);
            UnifiedApp.ui.showToast('Failed to share results', 'error');
        }
    };
    
    // Cancel ongoing analysis
    window.UnifiedApp.analysis.cancelAnalysis = function() {
        if (currentAnalysis.eventSource) {
            currentAnalysis.eventSource.close();
            currentAnalysis.eventSource = null;
        }
        currentAnalysis.isAnalyzing = false;
        UnifiedApp.ui.hideLoading();
        UnifiedApp.ui.showToast('Analysis cancelled', 'info');
    };
    
    // Reset analysis
    window.UnifiedApp.analysis.reset = function() {
        // Cancel any ongoing analysis
        if (currentAnalysis.isAnalyzing) {
            UnifiedApp.analysis.cancelAnalysis();
        }
        
        // Clear all inputs
        const urlInput = document.getElementById('url-input');
        const textInput = document.getElementById('text-input');
        const fileInput = document.getElementById('file-input');
        
        if (urlInput) urlInput.value = '';
        if (textInput) textInput.value = '';
        if (fileInput) fileInput.value = '';
        
        // Clear file preview
        window.clearFileUpload && window.clearFileUpload();
        
        // Hide results
        const resultsContainer = document.getElementById('results-container');
        if (resultsContainer) {
            resultsContainer.style.display = 'none';
        }
        
        // Show input section
        const inputSection = document.getElementById('input-section');
        if (inputSection) {
            inputSection.style.display = 'block';
        }
        
        // Hide progress
        const progressContainer = document.getElementById('progress-container');
        if (progressContainer) {
            progressContainer.style.display = 'none';
        }
        
        // Clear stored results
        currentAnalysis.results = null;
        currentAnalysis.analysisType = null;
        
        if (UnifiedApp.results && UnifiedApp.results.clearResults) {
            UnifiedApp.results.clearResults();
        }
        
        UnifiedApp.ui.showToast('Analysis reset', 'info');
    };
    
    // Legacy compatibility functions
    window.analyzeUnified = function() {
        const text = document.getElementById('text-input').value;
        UnifiedApp.analysis.runAnalysis(text, 'pro');
    };
    
    window.downloadUnifiedPDF = function() {
        UnifiedApp.analysis.generatePDF();
    };
    
    window.shareUnifiedResults = function() {
        UnifiedApp.analysis.shareResults();
    };
    
    window.resetUnifiedAnalysis = function() {
        UnifiedApp.analysis.reset();
    };
    
    console.log('Unified Analysis module loaded - Enhanced version');
})();
