// API Client for Facts & Fakes AI
// Centralized API communication for all tools

class APIClient {
    constructor() {
        this.baseURL = '/api';
        this.headers = {
            'Content-Type': 'application/json'
        };
    }

    // Handle API responses
    async handleResponse(response) {
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.message || error.error || `HTTP error! status: ${response.status}`);
        }
        return response.json();
    }

    // Speech Fact-Checker APIs
    async factCheckClaims(claims) {
        const response = await fetch(`${this.baseURL}/batch-factcheck`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ claims })
        });
        return this.handleResponse(response);
    }

    async transcribeAudio(audioFile) {
        const formData = new FormData();
        formData.append('audio', audioFile);
        
        const response = await fetch(`${this.baseURL}/transcribe`, {
            method: 'POST',
            body: formData
        });
        return this.handleResponse(response);
    }

    async extractYouTubeTranscript(url) {
        const response = await fetch(`${this.baseURL}/youtube-transcript`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ url })
        });
        return this.handleResponse(response);
    }

    // News Verification APIs
    async verifyNews(data) {
        const response = await fetch(`${this.baseURL}/verify-news`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        return this.handleResponse(response);
    }

    // Image Analysis APIs
    async analyzeImage(imageFile) {
        const formData = new FormData();
        formData.append('image', imageFile);
        
        const response = await fetch(`${this.baseURL}/analyze-image`, {
            method: 'POST',
            body: formData
        });
        return this.handleResponse(response);
    }

    // Unified Content Check APIs
    async checkContent(content, type) {
        const response = await fetch(`${this.baseURL}/check-content`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ content, type })
        });
        return this.handleResponse(response);
    }

    // Unified Analysis API (AI Detection & Plagiarism) - NEW
    async analyzeUnified(data) {
        const response = await fetch(`${this.baseURL}/analyze-unified`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        return this.handleResponse(response);
    }

    // Analyze File API - NEW
    async analyzeFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${this.baseURL}/analyze-file`, {
            method: 'POST',
            body: formData
        });
        return this.handleResponse(response);
    }

    // Analyze URL API - NEW
    async analyzeURL(url) {
        const response = await fetch(`${this.baseURL}/analyze-url`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ url })
        });
        return this.handleResponse(response);
    }

    // Generate Unified PDF Report - NEW
    async generateUnifiedPDF(data) {
        const response = await fetch(`${this.baseURL}/generate-unified-pdf`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        
        // Handle PDF blob response
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `ai-plagiarism-report-${Date.now()}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            return { success: true };
        } else {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.error || 'Failed to generate PDF');
        }
    }

    // User Authentication APIs
    async getUserStatus() {
        const response = await fetch(`${this.baseURL}/user/status`);
        return this.handleResponse(response);
    }

    async login(email, password) {
        const response = await fetch(`${this.baseURL}/login`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ email, password })
        });
        return this.handleResponse(response);
    }

    async logout() {
        const response = await fetch(`${this.baseURL}/logout`, {
            method: 'POST',
            headers: this.headers
        });
        return this.handleResponse(response);
    }

    // Usage tracking
    async trackUsage(toolType, action) {
        const response = await fetch(`${this.baseURL}/track-usage`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ tool: toolType, action })
        });
        return this.handleResponse(response);
    }

    // Export/Download APIs
    async generateReport(data, format) {
        const response = await fetch(`${this.baseURL}/generate-report`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ data, format })
        });
        
        if (format === 'pdf' || format === 'csv') {
            // Handle binary responses
            return response.blob();
        }
        return this.handleResponse(response);
    }

    // News Analysis API
    async analyzeNews(data) {
        const response = await fetch(`${this.baseURL}/analyze-news`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        return this.handleResponse(response);
    }

    // Text Analysis API
    async analyzeText(text) {
        const response = await fetch(`${this.baseURL}/analyze-text`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ text })
        });
        return this.handleResponse(response);
    }

    // Contact Form API
    async submitContact(contactData) {
        const response = await fetch(`${this.baseURL}/contact`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(contactData)
        });
        return this.handleResponse(response);
    }

    // Beta Signup API
    async betaSignup(email) {
        const response = await fetch(`${this.baseURL}/beta-signup`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ email })
        });
        return this.handleResponse(response);
    }
}

// Create global instance
window.ffAPI = new APIClient();

// Export for module systems if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APIClient;
}
