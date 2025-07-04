// Speech Fact-Checker JavaScript Module
(function() {
    'use strict';

    // Global variables
    let recognition;
    let isRecording = false;
    let factCheckResults = [];
    let selectedSource = 'microphone';
    
    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        
        recognition.onresult = handleSpeechResult;
        recognition.onerror = handleSpeechError;
        recognition.onend = handleSpeechEnd;
    }
    
    // Source selection
    function selectSource(source) {
        selectedSource = source;
        console.log('Selected source:', source);
        
        // Hide all input sections
        document.querySelectorAll('.source-input').forEach(el => el.style.display = 'none');
        
        // Show relevant input section
        switch(source) {
            case 'microphone':
                document.getElementById('microphone-input').style.display = 'block';
                break;
            case 'upload':
                document.getElementById('file-input').style.display = 'block';
                break;
            case 'stream':
                document.getElementById('stream-input').style.display = 'block';
                break;
            case 'demo':
                startDemo();
                break;
            case 'youtube':
                document.getElementById('youtube-input').style.display = 'block';
                break;
            case 'text':
                // Text mode doesn't need a separate input section
                break;
        }
        
        // Update active state
        document.querySelectorAll('.source-card').forEach(card => {
            card.classList.remove('active');
        });
        
        // Find the clicked card and make it active
        document.querySelector(`[data-mode="${source}"]`).classList.add('active');
        
        // Update UI based on source
        updateUIForSource(source);
    }
    
    // Update UI elements based on selected source
    function updateUIForSource(source) {
        const modeBanner = document.getElementById('modeBanner');
        const modeIcon = document.getElementById('modeIcon');
        const modeText = document.getElementById('modeText');
        const instructionsList = document.getElementById('instructionsList');
        const modeNameInstructions = document.getElementById('modeNameInstructions');
        const recordBtn = document.getElementById('record-btn');
        const transcript = document.getElementById('transcript');
        const hintText = document.getElementById('hintText');
        const status = document.getElementById('status');
        
        // Show status
        status.classList.add('active');
        
        if (source === 'microphone') {
            modeIcon.className = 'fas fa-microphone';
            modeText.textContent = 'Live Recording Mode - Ready to record your speech';
            modeNameInstructions.textContent = 'Live Recording';
            recordBtn.style.display = 'inline-flex';
            transcript.disabled = true;
            transcript.placeholder = 'Your speech will appear here as you speak...';
            hintText.textContent = 'Click "Start Recording" to begin capturing speech';
            modeBanner.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
            
            instructionsList.innerHTML = `
                <div class="instruction-item">
                    <div class="instruction-number">1</div>
                    <div>
                        <strong>Start Recording:</strong> Click the "Start Recording" button below (microphone access required)
                    </div>
                </div>
                <div class="instruction-item">
                    <div class="instruction-number">2</div>
                    <div>
                        <strong>Speak Clearly:</strong> Your words will appear in real-time in the transcript box
                    </div>
                </div>
                <div class="instruction-item">
                    <div class="instruction-number">3</div>
                    <div>
                        <strong>Stop Recording:</strong> Click "Stop Recording" when you're finished speaking
                    </div>
                </div>
                <div class="instruction-item">
                    <div class="instruction-number">4</div>
                    <div>
                        <strong>Check Facts:</strong> Click "Check Facts" to analyze all claims in your speech
                    </div>
                </div>
            `;
        } else if (source === 'text') {
            modeIcon.className = 'fas fa-keyboard';
            modeText.textContent = 'Text Input Mode - Type or paste your text';
            modeNameInstructions.textContent = 'Text Input';
            recordBtn.style.display = 'none';
            transcript.disabled = false;
            transcript.placeholder = 'Type or paste your text here...';
            transcript.focus();
            hintText.textContent = 'Type or paste text, then click "Check Facts" to analyze';
            modeBanner.style.background = 'linear-gradient(135deg, #3b82f6, #2563eb)';
            
            instructionsList.innerHTML = `
                <div class="instruction-item">
                    <div class="instruction-number">1</div>
                    <div>
                        <strong>Enter Text:</strong> Click in the transcript box below
                    </div>
                </div>
                <div class="instruction-item">
                    <div class="instruction-number">2</div>
                    <div>
                        <strong>Type or Paste:</strong> Enter your text manually or paste from clipboard (Ctrl+V)
                    </div>
                </div>
                <div class="instruction-item">
                    <div class="instruction-number">3</div>
                    <div>
                        <strong>Auto-Analysis:</strong> For pasted text, fact-checking starts automatically
                    </div>
                </div>
                <div class="instruction-item">
                    <div class="instruction-number">4</div>
                    <div>
                        <strong>Manual Check:</strong> Or click "Check Facts" when ready to analyze
                    </div>
                </div>
            `;
        } else if (source === 'youtube') {
            modeIcon.className = 'fab fa-youtube';
            modeText.textContent = 'YouTube Mode - Extract and analyze video transcripts';
            modeNameInstructions.textContent = 'YouTube Video';
            recordBtn.style.display = 'none';
            transcript.disabled = true;
            transcript.placeholder = 'YouTube transcript will appear here...';
            hintText.textContent = 'Enter a YouTube URL above and click "Get Transcript"';
            modeBanner.style.background = 'linear-gradient(135deg, #ff0000, #dc2626)';
            
            instructionsList.innerHTML = `
                <div class="instruction-item">
                    <div class="instruction-number">1</div>
                    <div>
                        <strong>Paste URL:</strong> Enter any YouTube video URL in the field above
                    </div>
                </div>
                <div class="instruction-item">
                    <div class="instruction-number">2</div>
                    <div>
                        <strong>Get Transcript:</strong> Click "Get Transcript" to fetch the video's captions
                    </div>
                </div>
                <div class="instruction-item">
                    <div class="instruction-number">3</div>
                    <div>
                        <strong>Review:</strong> The transcript will appear with video information
                    </div>
                </div>
                <div class="instruction-item">
                    <div class="instruction-number">4</div>
                    <div>
                        <strong>Analyze:</strong> Click "Check Facts" to verify claims in the video
                    </div>
                </div>
            `;
        } else if (source === 'demo') {
            modeIcon.className = 'fas fa-play-circle';
            modeText.textContent = 'Demo Mode - Sample speech loaded';
            modeNameInstructions.textContent = 'Demo';
            recordBtn.style.display = 'none';
            transcript.disabled = true;
            hintText.textContent = 'Demo text loaded. Click "Check Facts" to see results';
            modeBanner.style.background = 'linear-gradient(135deg, #10b981, #059669)';
            
            instructionsList.innerHTML = `
                <div class="instruction-item">
                    <div class="instruction-number">✨</div>
                    <div>
                        <strong>Demo Loaded:</strong> Sample speech with factual claims has been loaded
                    </div>
                </div>
                <div class="instruction-item">
                    <div class="instruction-number">👀</div>
                    <div>
                        <strong>Review Text:</strong> See the example speech in the transcript box
                    </div>
                </div>
                <div class="instruction-item">
                    <div class="instruction-number">🚀</div>
                    <div>
                        <strong>Run Analysis:</strong> Click "Check Facts" to see how verification works
                    </div>
                </div>
                <div class="instruction-item">
                    <div class="instruction-number">💡</div>
                    <div>
                        <strong>Try Your Own:</strong> Switch to Recording or Text mode for custom content
                    </div>
                </div>
            `;
        }
        
        status.textContent = `${modeNameInstructions.textContent} mode selected`;
    }
    
    // Start/stop recording
    function toggleRecording() {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    }
    
    function startRecording() {
        if (!recognition) {
            alert('Speech recognition is not supported in your browser.');
            return;
        }
        
        isRecording = true;
        document.getElementById('record-btn').classList.add('recording');
        document.getElementById('record-btn').innerHTML = '<i class="fas fa-stop"></i> Stop Recording';
        document.getElementById('status').textContent = 'Listening...';
        
        // Clear previous results
        document.getElementById('transcript').value = '';
        factCheckResults = [];
        updateFactCheckDisplay();
        
        recognition.start();
    }
    
    function stopRecording() {
        isRecording = false;
        document.getElementById('record-btn').classList.remove('recording');
        document.getElementById('record-btn').innerHTML = '<i class="fas fa-microphone"></i> Start Recording';
        document.getElementById('status').textContent = 'Recording stopped';
        
        if (recognition) {
            recognition.stop();
        }
        
        // Process final transcript
        const transcript = document.getElementById('transcript').value;
        if (transcript) {
            processTranscript(transcript);
        }
    }
    
    function handleSpeechResult(event) {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }
        
        // Update transcript display
        const transcriptElement = document.getElementById('transcript');
        if (finalTranscript) {
            transcriptElement.value += finalTranscript;
            // Real-time fact checking for final segments
            checkFactsInRealTime(finalTranscript);
        }
        
        // Update status with interim results
        if (interimTranscript) {
            document.getElementById('status').textContent = 'Listening: ' + interimTranscript.slice(-50);
        }
        
        updateWordCount();
    }
    
    function handleSpeechError(event) {
        console.error('Speech recognition error:', event.error);
        document.getElementById('status').textContent = 'Error: ' + event.error;
        
        if (event.error === 'no-speech') {
            document.getElementById('status').textContent = 'No speech detected. Please try again.';
        }
    }
    
    function handleSpeechEnd() {
        if (isRecording) {
            // Restart recognition if still recording
            recognition.start();
        }
    }
    
    // File upload handling
    function handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        // For demo purposes, we'll simulate processing
        document.getElementById('status').textContent = 'Processing audio file...';
        
        setTimeout(() => {
            document.getElementById('status').textContent = 'Audio file processed';
            document.getElementById('transcript').value = 'Transcribed content from uploaded audio file would appear here.';
            processTranscript(document.getElementById('transcript').value);
        }, 2000);
    }
    
    // Stream URL handling
    function processStream() {
        const streamUrl = document.getElementById('stream-url').value;
        if (!streamUrl) {
            alert('Please enter a stream URL');
            return;
        }
        
        document.getElementById('status').textContent = 'Connecting to stream...';
        
        // Send to backend
        fetch('/api/stream-transcript', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ stream_url: streamUrl })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('status').textContent = 'Stream connected. Processing...';
                // In a real implementation, this would establish a WebSocket connection
            } else {
                document.getElementById('status').textContent = 'Failed to connect to stream';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('status').textContent = 'Error connecting to stream';
        });
    }
    
    // YouTube processing
    function processYouTube() {
        const youtubeUrl = document.getElementById('youtube-url').value.trim();
        if (!youtubeUrl) {
            alert('Please enter a YouTube URL');
            return;
        }
        
        // Update UI
        document.getElementById('status').textContent = 'Fetching YouTube transcript...';
        document.getElementById('status').classList.add('active');
        document.getElementById('youtube-btn').disabled = true;
        document.getElementById('youtube-btn').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        
        // Clear previous results
        document.getElementById('transcript').value = '';
        factCheckResults = [];
        updateFactCheckDisplay();
        
        // Remove any existing video info
        const existingInfo = document.querySelector('.video-info');
        if (existingInfo) {
            existingInfo.remove();
        }
        
        // Fetch transcript from backend
        fetch('/api/youtube-transcript', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: youtubeUrl })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Display transcript
                document.getElementById('transcript').value = data.transcript;
                document.getElementById('status').textContent = `YouTube transcript loaded - ${data.metadata.title}`;
                
                // Show video info
                const transcriptContainer = document.getElementById('transcript');
                const infoHtml = `
                    <div class="video-info">
                        <strong>Video:</strong> ${data.metadata.title}<br>
                        <strong>Channel:</strong> ${data.metadata.channel}<br>
                        <strong>Duration:</strong> ${data.metadata.duration}<br>
                        <a href="${data.metadata.url}" target="_blank" style="color: #ff0000;">
                            <i class="fab fa-youtube"></i> Watch on YouTube
                        </a>
                    </div>
                `;
                transcriptContainer.insertAdjacentHTML('beforebegin', infoHtml);
                
                // Update word count
                updateWordCount();
                
                // Process transcript for fact-checking
                processTranscript(data.transcript);
            } else {
                throw new Error(data.error || data.details || 'Failed to fetch transcript');
            }
        })
        .catch(error => {
            console.error('YouTube error:', error);
            document.getElementById('status').textContent = `Error: ${error.message}`;
            alert(`Failed to fetch YouTube transcript: ${error.message}`);
        })
        .finally(() => {
            // Reset button
            document.getElementById('youtube-btn').disabled = false;
            document.getElementById('youtube-btn').innerHTML = '<i class="fab fa-youtube"></i> Get Transcript';
        });
    }
    
    // Demo mode
    function startDemo() {
        const demoTranscript = `Good evening, I'm reporting live from the climate summit where world leaders have gathered to discuss urgent action. 
        
        According to the latest UN report, global temperatures have risen by 1.2 degrees Celsius since pre-industrial times. Scientists say we have less than 10 years to limit warming to 1.5 degrees.
        
        The President announced that the country will reduce emissions by 50% by 2030, which experts say is the most ambitious target ever set. However, critics argue this is still not enough to meet the Paris Agreement goals.
        
        In other news, a new study from Harvard University found that renewable energy is now cheaper than fossil fuels in 85% of the world. The solar industry alone has created over 3 million jobs globally.
        
        Back to you in the studio.`;
        
        document.getElementById('transcript').value = demoTranscript;
        document.getElementById('status').textContent = 'Demo transcript loaded';
        updateWordCount();
        
        // Process the demo transcript
        processTranscript(demoTranscript);
    }
    
    // Process transcript for fact-checking
    function processTranscript(transcript) {
        if (!transcript) return;
        
        document.getElementById('status').textContent = 'Analyzing transcript...';
        document.getElementById('status').classList.add('active');
        
        // Extract sentences/claims
        const sentences = transcript.match(/[^.!?]+[.!?]+/g) || [];
        const claims = sentences.filter(sentence => {
            // Simple heuristic for identifying factual claims
            const claimIndicators = [
                /\d+%/,
                /\d+ (?:million|billion|thousand)/,
                /according to/i,
                /study (?:shows|found|reveals)/i,
                /report(?:s|ed)? that/i,
                /data (?:shows|indicates)/i,
                /(?:increased|decreased|rose|fell) by/i
            ];
            
            return claimIndicators.some(pattern => pattern.test(sentence));
        });
        
        // Batch fact-check
        if (claims.length > 0) {
            batchFactCheck(claims);
        } else {
            document.getElementById('status').textContent = 'No factual claims detected in transcript';
        }
        
        // Update statistics
        updateStatistics(transcript);
    }
    
    // Real-time fact checking for live speech
    function checkFactsInRealTime(text) {
        // Extract potential claims from the new text
        const claimPattern = /(?:[\d,]+%|[\d,]+ (?:million|billion|thousand)|according to|study shows|report(?:s|ed)?)/i;
        
        if (claimPattern.test(text)) {
            // Add to pending fact checks
            batchFactCheck([text], 'real-time');
        }
    }
    
    // Batch fact-check claims
    function batchFactCheck(claims, priority = 'balanced') {
        // Show processing overlay
        document.getElementById('processingOverlay').style.display = 'flex';
        
        fetch('/api/batch-factcheck', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                claims: claims,
                priority: priority
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                factCheckResults = factCheckResults.concat(data.results);
                updateFactCheckDisplay();
                document.getElementById('status').textContent = `Fact-checked ${data.processed} claims`;
                
                // Show results section
                document.getElementById('resultsSection').style.display = 'grid';
            } else {
                throw new Error('Fact check failed');
            }
        })
        .catch(error => {
            console.error('Fact check error:', error);
            document.getElementById('status').textContent = 'Error during fact-checking';
        })
        .finally(() => {
            // Hide processing overlay
            setTimeout(() => {
                document.getElementById('processingOverlay').style.display = 'none';
            }, 500);
        });
    }
    
    // Update fact-check results display
    function updateFactCheckDisplay() {
        const resultsContainer = document.getElementById('fact-check-results');
        
        if (factCheckResults.length === 0) {
            resultsContainer.innerHTML = '<p class="text-muted">No fact-checks yet. Start speaking or load content to begin.</p>';
            return;
        }
        
        const resultsHtml = factCheckResults.map((result, index) => {
            const verdictClass = result.verdict === 'true' ? 'success' : 
                               result.verdict === 'false' ? 'danger' : 'warning';
            const verdictIcon = result.verdict === 'true' ? 'check-circle' : 
                              result.verdict === 'false' ? 'times-circle' : 'question-circle';
            
            return `
                <div class="fact-check-item mb-3 p-3 border rounded">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <p class="mb-2"><strong>Claim ${index + 1}:</strong> ${result.claim}</p>
                            <div class="verdict text-${verdictClass}">
                                <i class="fas fa-${verdictIcon}"></i>
                                <strong>${result.verdict.toUpperCase()}</strong>
                                (${Math.round(result.confidence * 100)}% confidence)
                            </div>
                            ${result.sources && result.sources.length > 0 ? `
                                <div class="sources mt-2">
                                    <small class="text-muted">Sources: ${result.sources.map(s => s.source || s).join(', ')}</small>
                                </div>
                            ` : ''}
                        </div>
                        <div class="credibility-score ml-3">
                            <div class="text-center">
                                <div class="score-circle ${getScoreClass(result.credibility_score)}">
                                    ${result.credibility_score}
                                </div>
                                <small>Credibility</small>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        resultsContainer.innerHTML = resultsHtml;
        
        // Update summary
        showSummary();
    }
    
    // Update statistics
    function updateStatistics(transcript) {
        const words = transcript.split(/\s+/).filter(word => word.length > 0);
        const trueCount = factCheckResults.filter(r => r.verdict === 'true').length;
        const falseCount = factCheckResults.filter(r => r.verdict === 'false').length;
        const unverifiedCount = factCheckResults.filter(r => r.verdict === 'unverified').length;
        
        document.getElementById('word-count').textContent = words.length;
        document.getElementById('word-count-stat').textContent = words.length;
        document.getElementById('claims-checked').textContent = factCheckResults.length;
        document.getElementById('true-count').textContent = trueCount;
        document.getElementById('false-count').textContent = falseCount;
        
        const accuracyRate = factCheckResults.length > 0 ? 
            Math.round((trueCount / factCheckResults.length) * 100) : 0;
        
        document.getElementById('accuracy-rate').style.width = accuracyRate + '%';
        document.getElementById('accuracy-percent').textContent = accuracyRate;
        
        // Update chart if available
        if (window.updateChart) {
            window.updateChart(trueCount, falseCount, unverifiedCount);
        }
    }
    
    // Update word count
    function updateWordCount() {
        const text = document.getElementById('transcript').value;
        const words = text.trim().split(/\s+/).filter(w => w.length > 0);
        document.getElementById('word-count').textContent = words.length;
    }
    
    // Show summary
    function showSummary() {
        const summaryCard = document.getElementById('summaryCard');
        if (factCheckResults.length > 0) {
            summaryCard.style.display = 'block';
        }
    }
    
    // Export report
    function exportReport() {
        const transcript = document.getElementById('transcript').value;
        const stats = {
            wordCount: parseInt(document.getElementById('word-count').textContent),
            claimsChecked: parseInt(document.getElementById('claims-checked').textContent),
            trueCount: factCheckResults.filter(r => r.verdict === 'true').length,
            falseCount: factCheckResults.filter(r => r.verdict === 'false').length
        };
        
        fetch('/api/export-speech-report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                transcript: transcript,
                fact_checks: factCheckResults,
                statistics: stats,
                duration: document.getElementById('duration')?.textContent || '00:00'
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Create downloadable report
                const report = data.report;
                const reportText = `
SPEECH FACT-CHECK REPORT
========================
Generated: ${report.generated_at}
Duration: ${report.duration}

STATISTICS
----------
Total Words: ${report.statistics.total_words}
Claims Checked: ${report.statistics.claims_checked}
True Claims: ${report.statistics.true_claims}
False Claims: ${report.statistics.false_claims}
Accuracy Rate: ${report.statistics.accuracy_rate}

TRANSCRIPT
----------
${report.transcript}

FACT-CHECK RESULTS
------------------
${report.fact_checks.map((fc, i) => `
${i + 1}. ${fc.claim}
   Verdict: ${fc.verdict.toUpperCase()}
   Confidence: ${Math.round(fc.confidence * 100)}%
   Sources: ${fc.sources ? fc.sources.join(', ') : 'N/A'}
`).join('\n')}

METHODOLOGY
-----------
${report.methodology.fact_check_sources.join(', ')}
Confidence Threshold: ${report.methodology.confidence_threshold}
Bias Detection: ${report.methodology.bias_detection ? 'Enabled' : 'Disabled'}
`;
                
                // Download the report
                const blob = new Blob([reportText], { type: 'text/plain' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `speech-fact-check-${new Date().toISOString().slice(0, 10)}.txt`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                document.getElementById('status').textContent = 'Report exported successfully!';
            }
        })
        .catch(error => {
            console.error('Export error:', error);
            alert('Failed to export report');
        });
    }
    
    // Utility functions
    function getScoreClass(score) {
        if (score >= 80) return 'score-high';
        if (score >= 60) return 'score-medium';
        return 'score-low';
    }
    
    // Settings modal handlers
    function openSettings() {
        $('#settingsModal').modal('show');
    }
    
    function saveSettings() {
        const checkMode = document.querySelector('input[name="checkMode"]:checked').value;
        const language = document.getElementById('language-select').value;
        
        // Apply settings
        if (recognition) {
            recognition.lang = language;
        }
        
        // Store preferences
        localStorage.setItem('speechCheckMode', checkMode);
        localStorage.setItem('speechLanguage', language);
        
        $('#settingsModal').modal('hide');
    }
    
    // Load saved settings on init
    function loadSettings() {
        const savedMode = localStorage.getItem('speechCheckMode') || 'balanced';
        const savedLanguage = localStorage.getItem('speechLanguage') || 'en-US';
        
        // Settings elements might not exist, so check first
        const modeInput = document.querySelector(`input[name="checkMode"][value="${savedMode}"]`);
        if (modeInput) {
            modeInput.checked = true;
        }
        
        const languageSelect = document.getElementById('language-select');
        if (languageSelect) {
            languageSelect.value = savedLanguage;
        }
        
        if (recognition) {
            recognition.lang = savedLanguage;
        }
    }
    
    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {
        loadSettings();
        
        // Set default source
        selectSource('microphone');
        
        // Initialize chart if available
        if (window.Chart) {
            const ctx = document.getElementById('resultsChart')?.getContext('2d');
            if (ctx) {
                window.factCheckChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['True', 'False', 'Unverified'],
                        datasets: [{
                            data: [0, 0, 0],
                            backgroundColor: ['#28a745', '#dc3545', '#ffc107']
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
                
                window.updateChart = function(trueCount, falseCount, unverifiedCount) {
                    window.factCheckChart.data.datasets[0].data = [trueCount, falseCount, unverifiedCount];
                    window.factCheckChart.update();
                };
            }
        }
        
        // Add event listeners
        const transcript = document.getElementById('transcript');
        if (transcript) {
            transcript.addEventListener('input', updateWordCount);
        }
    });
    
    // Expose functions to global scope
    window.selectSource = selectSource;
    window.toggleRecording = toggleRecording;
    window.handleFileUpload = handleFileUpload;
    window.processStream = processStream;
    window.processYouTube = processYouTube;
    window.exportReport = exportReport;
    window.openSettings = openSettings;
    window.saveSettings = saveSettings;
    window.processTranscript = processTranscript;
    
})();
