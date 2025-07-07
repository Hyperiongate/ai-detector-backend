// Speech Fact-Checker Tool Bundle
// This contains all functionality from the original speech.html in a modular format

window.SpeechFactChecker = (function() {
    'use strict';

    // Module state
    const state = {
        recognition: null,
        isRecording: false,
        isPaused: false,
        factCheckResults: [],
        selectedSource: 'microphone',
        currentLanguage: 'en-US',
        startTime: null,
        duration: 0,
        durationInterval: null,
        claims: [],
        timeline: [],
        liveCheckInterval: null,
        tutorialStep: 0,
        flaggedClaims: new Set(),
        currentFilter: 'all'
    };

    // Initialize the module
    function init() {
        console.log('Initializing Speech Fact-Checker...');
        
        // Load the HTML content
        loadToolContent();
        
        // Initialize after content is loaded
        setTimeout(() => {
            initializeComponents();
            bindEventListeners();
            initSpeechRecognition();
            loadUserPreferences();
        }, 100);
    }

    // Load the tool's HTML content
    function loadToolContent() {
        const container = document.getElementById('speech-tool-content');
        if (!container) return;

        container.innerHTML = `
            <!-- Language Selector -->
            <div class="language-selector">
                <label for="languageSelect">Language:</label>
                <select id="languageSelect" onchange="SpeechFactChecker.changeLanguage()">
                    <option value="en-US">English (US)</option>
                    <option value="en-GB">English (UK)</option>
                    <option value="es-ES">Spanish</option>
                    <option value="fr-FR">French</option>
                    <option value="de-DE">German</option>
                    <option value="it-IT">Italian</option>
                    <option value="pt-BR">Portuguese</option>
                    <option value="zh-CN">Chinese (Simplified)</option>
                    <option value="ja-JP">Japanese</option>
                    <option value="ko-KR">Korean</option>
                </select>
            </div>

            <!-- Mode Selection -->
            <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(124, 58, 237, 0.1)); border: 2px solid #667eea; border-radius: 15px; padding: 20px; margin-bottom: 25px; text-align: center;">
                <h2 style="color: #4f46e5; margin-bottom: 10px; font-size: 1.5rem;">
                    <i class="fas fa-hand-point-down"></i> Step 1: Choose Your Input Method
                </h2>
                <p style="color: #6b7280; margin-bottom: 20px;">Select how you want to provide the speech content</p>
                
                <div style="display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;">
                    <button class="compact-tab active" onclick="SpeechFactChecker.selectSource('microphone')" data-mode="microphone">
                        <i class="fas fa-microphone" style="font-size: 1.5rem; margin-bottom: 5px;"></i>
                        <div style="font-weight: 600;">Live Recording</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">Speak into mic</div>
                    </button>
                    <button class="compact-tab" onclick="SpeechFactChecker.selectSource('text')" data-mode="text">
                        <i class="fas fa-keyboard" style="font-size: 1.5rem; margin-bottom: 5px;"></i>
                        <div style="font-weight: 600;">Text Input</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">Type or paste</div>
                    </button>
                    <button class="compact-tab" onclick="SpeechFactChecker.selectSource('youtube')" data-mode="youtube">
                        <i class="fab fa-youtube" style="font-size: 1.5rem; margin-bottom: 5px;"></i>
                        <div style="font-weight: 600;">YouTube</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">Analyze video</div>
                    </button>
                    <button class="compact-tab" onclick="SpeechFactChecker.selectSource('audio')" data-mode="audio">
                        <i class="fas fa-file-audio" style="font-size: 1.5rem; margin-bottom: 5px;"></i>
                        <div style="font-weight: 600;">Audio File</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">Upload file</div>
                    </button>
                </div>
            </div>

            <!-- Transcript Area -->
            <div class="transcript-container" id="transcriptContainer">
                <div class="transcript-header">
                    <h3 style="color: #4a5568; margin: 0;">
                        <i class="fas fa-file-alt"></i> Transcript
                    </h3>
                    <div class="transcript-info">
                        <div class="transcript-metric">
                            <i class="fas fa-font"></i>
                            <span id="wordCountDisplay">0</span> words
                        </div>
                        <div class="transcript-metric">
                            <i class="fas fa-clock"></i>
                            <span id="durationDisplay">00:00</span>
                        </div>
                        <div class="transcript-metric">
                            <i class="fas fa-chart-line"></i>
                            <span id="claimCountDisplay">0</span> claims
                        </div>
                    </div>
                </div>
                <div id="transcript" 
                     contenteditable="true" 
                     spellcheck="false"
                     data-placeholder="Your speech will appear here as you speak, or paste/type text to analyze..."
                     style="background: rgba(249, 250, 251, 0.8); border: 2px solid #e2e8f0; border-radius: 12px; padding: 20px; min-height: 200px; max-height: 400px; overflow-y: auto; font-size: 1rem; line-height: 1.8;"></div>
                
                <div class="button-group" style="display: flex; gap: 15px; margin-top: 20px; flex-wrap: wrap; justify-content: center;">
                    <button id="startBtn" class="btn btn-primary" onclick="SpeechFactChecker.startRecording()">
                        <i class="fas fa-microphone"></i> Start Recording
                    </button>
                    <button id="stopBtn" class="btn btn-danger" onclick="SpeechFactChecker.stopRecording()" style="display: none;">
                        <i class="fas fa-stop"></i> Stop Recording
                    </button>
                    <button id="checkFactsBtn" class="btn btn-success" onclick="SpeechFactChecker.checkFacts()">
                        <i class="fas fa-search"></i> Check Facts
                    </button>
                    <button class="btn btn-secondary" onclick="SpeechFactChecker.clearAll()">
                        <i class="fas fa-trash"></i> Clear All
                    </button>
                </div>
            </div>

            <!-- Results Section -->
            <div id="resultsSection" style="display: none; margin-top: 30px;">
                <h3>Fact Check Results</h3>
                <div id="factCheckResults"></div>
            </div>
        `;

        // Add necessary styles
        addStyles();
    }

    // Add required styles
    function addStyles() {
        if (document.getElementById('speech-tool-styles')) return;

        const style = document.createElement('style');
        style.id = 'speech-tool-styles';
        style.textContent = `
            .compact-tab {
                padding: 15px 25px;
                background: white;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 5px;
                min-width: 140px;
            }

            .compact-tab:hover {
                transform: translateY(-3px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
                border-color: #667eea;
            }

            .compact-tab.active {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border-color: transparent;
            }

            .btn {
                padding: 15px 30px;
                border: none;
                border-radius: 12px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }

            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }

            .btn-success {
                background: linear-gradient(135deg, #10b981, #059669);
                color: white;
            }

            .btn-danger {
                background: linear-gradient(135deg, #ef4444, #dc2626);
                color: white;
            }

            .btn-secondary {
                background: #6b7280;
                color: white;
            }

            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            }

            #transcript:empty::before {
                content: attr(data-placeholder);
                color: #9ca3af;
                font-style: italic;
            }

            .transcript-container {
                background: white;
                padding: 30px;
                border-radius: 15px;
                border: 2px solid rgba(102, 126, 234, 0.1);
                margin-bottom: 20px;
            }

            .transcript-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }

            .transcript-info {
                display: flex;
                gap: 20px;
                font-size: 0.9rem;
                color: #6b7280;
            }

            .transcript-metric {
                display: flex;
                align-items: center;
                gap: 5px;
            }

            .language-selector {
                position: absolute;
                top: 20px;
                right: 20px;
                display: flex;
                gap: 10px;
                align-items: center;
                background: rgba(255, 255, 255, 0.9);
                padding: 10px 15px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }
        `;
        document.head.appendChild(style);
    }

    // Initialize components
    function initializeComponents() {
        // Initialize any UI components that need setup
        console.log('Components initialized');
    }

    // Bind event listeners
    function bindEventListeners() {
        // Keyboard shortcuts
        document.addEventListener('keydown', handleKeyboardShortcuts);
        
        // Transcript changes
        const transcript = document.getElementById('transcript');
        if (transcript) {
            transcript.addEventListener('input', updateWordCount);
            transcript.addEventListener('paste', handlePaste);
        }
    }

    // Initialize speech recognition
    function initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window) {
            state.recognition = new webkitSpeechRecognition();
            state.recognition.continuous = true;
            state.recognition.interimResults = true;
            state.recognition.lang = state.currentLanguage;
            
            state.recognition.onstart = handleRecognitionStart;
            state.recognition.onend = handleRecognitionEnd;
            state.recognition.onresult = handleRecognitionResult;
            state.recognition.onerror = handleRecognitionError;
        } else {
            console.warn('Speech recognition not supported');
        }
    }

    // Speech recognition handlers
    function handleRecognitionStart() {
        state.isRecording = true;
        updateRecordingUI(true);
    }

    function handleRecognitionEnd() {
        state.isRecording = false;
        updateRecordingUI(false);
    }

    function handleRecognitionResult(event) {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const result = event.results[i];
            if (result.isFinal) {
                finalTranscript += result[0].transcript + ' ';
            } else {
                interimTranscript += result[0].transcript;
            }
        }
        
        const transcript = document.getElementById('transcript');
        if (transcript) {
            transcript.textContent = finalTranscript + interimTranscript;
            updateWordCount();
        }
    }

    function handleRecognitionError(event) {
        console.error('Speech recognition error:', event.error);
        if (event.error === 'not-allowed') {
            alert('Microphone access denied. Please allow microphone access in your browser settings.');
        }
    }

    // Public methods
    function startRecording() {
        if (state.recognition) {
            state.recognition.start();
        }
    }

    function stopRecording() {
        if (state.recognition) {
            state.recognition.stop();
        }
    }

    function selectSource(source) {
        state.selectedSource = source;
        
        // Update UI
        document.querySelectorAll('.compact-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-mode="${source}"]`).classList.add('active');
        
        // Update transcript editability
        const transcript = document.getElementById('transcript');
        if (transcript) {
            transcript.contentEditable = (source === 'text').toString();
        }
        
        // Show/hide start button
        const startBtn = document.getElementById('startBtn');
        if (startBtn) {
            startBtn.style.display = source === 'microphone' ? 'inline-flex' : 'none';
        }
    }

    function changeLanguage() {
        const select = document.getElementById('languageSelect');
        if (select) {
            state.currentLanguage = select.value;
            if (state.recognition) {
                state.recognition.lang = state.currentLanguage;
            }
        }
    }

    function checkFacts() {
        const transcript = document.getElementById('transcript');
        if (!transcript || !transcript.textContent.trim()) {
            alert('Please enter or record some text to fact-check');
            return;
        }
        
        // Show results section
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.style.display = 'block';
            
            // Simulate fact checking
            const results = document.getElementById('factCheckResults');
            if (results) {
                results.innerHTML = '<p>Analyzing claims... (This would connect to your fact-checking API)</p>';
                
                // Here you would make the actual API call
                // fetch('/api/batch-factcheck', { ... })
            }
        }
    }

    function clearAll() {
        if (!confirm('Clear all content?')) return;
        
        const transcript = document.getElementById('transcript');
        if (transcript) {
            transcript.textContent = '';
            updateWordCount();
        }
        
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.style.display = 'none';
        }
    }

    // Utility functions
    function updateWordCount() {
        const transcript = document.getElementById('transcript');
        const display = document.getElementById('wordCountDisplay');
        if (transcript && display) {
            const words = transcript.textContent.trim().split(/\s+/).filter(w => w.length > 0);
            display.textContent = words.length;
        }
    }

    function updateRecordingUI(isRecording) {
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        
        if (isRecording) {
            if (startBtn) startBtn.style.display = 'none';
            if (stopBtn) stopBtn.style.display = 'inline-flex';
        } else {
            if (startBtn) startBtn.style.display = 'inline-flex';
            if (stopBtn) stopBtn.style.display = 'none';
        }
    }

    function handleKeyboardShortcuts(e) {
        if (e.target.matches('input, textarea, [contenteditable="true"]')) return;
        
        switch(e.key.toLowerCase()) {
            case ' ':
                e.preventDefault();
                if (state.isRecording) {
                    stopRecording();
                } else if (state.selectedSource === 'microphone') {
                    startRecording();
                }
                break;
            case 'c':
                checkFacts();
                break;
            case 'r':
                clearAll();
                break;
        }
    }

    function handlePaste(e) {
        if (state.selectedSource === 'text') {
            setTimeout(updateWordCount, 100);
        }
    }

    function loadUserPreferences() {
        // Load any saved preferences
        const savedLanguage = localStorage.getItem('speechLanguage');
        if (savedLanguage) {
            state.currentLanguage = savedLanguage;
            const select = document.getElementById('languageSelect');
            if (select) {
                select.value = savedLanguage;
            }
        }
    }

    // Public API
    return {
        init: init,
        startRecording: startRecording,
        stopRecording: stopRecording,
        selectSource: selectSource,
        changeLanguage: changeLanguage,
        checkFacts: checkFacts,
        clearAll: clearAll
    };
})();
