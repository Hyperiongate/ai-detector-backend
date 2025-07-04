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
    window.selectSource = function(source) {
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
        }
        
        // Update active state
        document.querySelectorAll('.source-card').forEach(card => {
            card.classList.remove('active');
        });
        event.currentTarget.classList.add('active');
    };
    
    // Start/stop recording
    window.toggleRecording = function() {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    };
    
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
    window.handleFileUpload = function(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        // For demo purposes, we'll simulate processing
        document.getElementById('status').textContent = 'Processing audio file...';
        
        setTimeout(() => {
            document.getElementById('status').textContent = 'Audio file processed';
            document.getElementById('transcript').value = 'Transcribed content from uploaded audio file would appear here.';
            processTranscript(document.getElementById('transcript').value);
        }, 2000);
    };
    
    // Stream URL handling
    window.processStream = function() {
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
    };
    
    // YouTube processing
    window.processYouTube = function() {
        const youtubeUrl = document.getElementById('youtube-url').value.trim();
        if (!youtubeUrl) {
            alert('Please enter a YouTube URL');
            return;
        }
        
        // Update UI
        document.getElementById('status').textContent = 'Fetching YouTube transcript...';
        document.getElementById('youtube-btn').disabled = true;
        document.getElementById('youtube-btn').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        
        // Clear previous results
        document.getElementById('transcript').value = '';
        factCheckResults = [];
        updateFactCheckDisplay();
        
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
                const infoHtml = `
                    <div class="video-info" style="background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 5px;">
                        <strong>Video:</strong> ${data.metadata.title}<br>
                        <strong>Channel:</strong> ${data.metadata.channel}<br>
                        <strong>Duration:</strong> ${data.metadata.duration}<br>
                        <a href="${data.metadata.url}" target="_blank" style="color: #007bff;">Watch on YouTube</a>
                    </div>
                `;
                document.getElementById('transcript').insertAdjacentHTML('beforebegin', infoHtml);
                
                // Process transcript for fact-checking
                processTranscript(data.transcript);
            } else {
                throw new Error(data.error || 'Failed to fetch transcript');
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
    };
    
    // Demo mode
    function startDemo() {
        const demoTranscript = `Good evening, I'm reporting live from the climate summit where world leaders have gathered to discuss urgent action. 
        
        According to the latest UN report, global temperatures have risen by 1.2 degrees Celsius since pre-industrial times. Scientists say we have less than 10 years to limit warming to 1.5 degrees.
        
        The President announced that the country will reduce emissions by 50% by 2030, which experts say is the most ambitious target ever set. However, critics argue this is still not enough to meet the Paris Agreement goals.
        
        In other news, a new study from Harvard University found that renewable energy is now cheaper than fossil fuels in 85% of the world. The solar industry alone has created over 3 million jobs globally.
        
        Back to you in the studio.`;
        
        document.getElementById('transcript').value = demoTranscript;
        document.getElementById('status').textContent = 'Demo transcript loaded';
        
        // Process the demo transcript
        processTranscript(demoTranscript);
    }
    
    // Process transcript for fact-checking
    function processTranscript(transcript) {
        if (!transcript) return;
        
        document.getElementById('status').textContent = 'Analyzing transcript...';
        
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
            } else {
                throw new Error('Fact check failed');
            }
        })
        .catch(error => {
            console.error('Fact check error:', error);
