// Authentication and Analysis Utilities for Facts & Fakes AI
window.authAnalysis = {
    // Check if user is authenticated
    checkAuth: function() {
        const authToken = localStorage.getItem('authToken');
        const userEmail = localStorage.getItem('userEmail');
        return !!(authToken && userEmail);
    },
    
    // Show authentication message
    showAuthMessage: function() {
        const messageArea = document.getElementById('authMessageArea');
        if (messageArea) {
            messageArea.innerHTML = `
                <div style="background: linear-gradient(135deg, #f59e0b, #d97706); color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: center;">
                    <h3 style="margin-bottom: 10px;"><i class="fas fa-lock"></i> Pro Feature - Authentication Required</h3>
                    <p style="margin-bottom: 15px;">Please sign up or log in to access Pro analysis features.</p>
                    <div style="display: flex; gap: 10px; justify-content: center;">
                        <a href="/login" style="background: rgba(255,255,255,0.2); color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; transition: all 0.3s ease;">
                            <i class="fas fa-sign-in-alt"></i> Login
                        </a>
                        <a href="/pricingplan" style="background: rgba(255,255,255,0.3); color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; transition: all 0.3s ease;">
                            <i class="fas fa-crown"></i> Sign Up for Pro
                        </a>
                    </div>
                </div>
            `;
        }
    },
    
    // Initialize authentication features
    init: function() {
        // Check auth status on page load
        this.checkAuthStatus();
        
        // Update usage counter if authenticated
        if (this.checkAuth()) {
            this.updateUsage();
        }
    },
    
    // Check authentication status from backend
    checkAuthStatus: async function() {
        try {
            const response = await fetch('/api/user/status');
            const data = await response.json();
            
            if (data.authenticated) {
                localStorage.setItem('authToken', data.token || 'authenticated');
                localStorage.setItem('userEmail', data.email || 'user@example.com');
                localStorage.setItem('userPlan', data.plan || 'free');
                this.updateUIForAuth(data);
            } else {
                localStorage.removeItem('authToken');
                localStorage.removeItem('userEmail');
                localStorage.removeItem('userPlan');
            }
        } catch (error) {
            console.log('Auth check failed:', error);
        }
    },
    
    // Update UI for authenticated users
    updateUIForAuth: function(userData) {
        const usageCounter = document.getElementById('usageCounter');
        if (usageCounter) {
            const limit = userData.plan === 'pro' ? 10 : 5;
            const used = userData.usage_today || 0;
            const percentage = (used / limit) * 100;
            
            usageCounter.innerHTML = `
                <div style="background: rgba(102, 126, 234, 0.1); border: 2px solid rgba(102, 126, 234, 0.2); border-radius: 12px; padding: 15px; margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span style="font-weight: 600; color: #4a5568;">Daily Usage</span>
                        <span style="color: #667eea; font-weight: 600;">${used} / ${limit} analyses</span>
                    </div>
                    <div style="background: #e2e8f0; height: 8px; border-radius: 4px; overflow: hidden;">
                        <div style="background: linear-gradient(135deg, #667eea, #764ba2); height: 100%; width: ${percentage}%; transition: width 0.5s ease;"></div>
                    </div>
                </div>
            `;
        }
    },
    
    // Update usage after analysis
    updateUsage: async function() {
        try {
            const response = await fetch('/api/user/status');
            const data = await response.json();
            
            if (data.authenticated) {
                this.updateUIForAuth(data);
                
                // Show warning if approaching limit
                const limit = data.plan === 'pro' ? 10 : 5;
                const used = data.usage_today || 0;
                
                if (used >= limit) {
                    this.showLimitReached(data.plan);
                } else if (used >= limit - 1) {
                    this.showLimitWarning(limit - used);
                }
            }
        } catch (error) {
            console.log('Usage update failed:', error);
        }
    },
    
    // Show limit reached message
    showLimitReached: function(plan) {
        const messageArea = document.getElementById('authMessageArea');
        if (messageArea) {
            messageArea.innerHTML = `
                <div style="background: linear-gradient(135deg, #ef4444, #dc2626); color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: center;">
                    <h3 style="margin-bottom: 10px;"><i class="fas fa-exclamation-triangle"></i> Daily Limit Reached</h3>
                    <p style="margin-bottom: 15px;">You've used all your daily analyses. Your limit will reset tomorrow.</p>
                    ${plan === 'free' ? `
                    <a href="/pricingplan" style="background: rgba(255,255,255,0.2); color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; display: inline-block;">
                        <i class="fas fa-crown"></i> Upgrade to Pro for More Analyses
                    </a>
                    ` : ''}
                </div>
            `;
        }
    },
    
    // Show limit warning
    showLimitWarning: function(remaining) {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: linear-gradient(135deg, #f59e0b, #d97706);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            z-index: 1000;
            font-weight: 600;
            animation: slideIn 0.3s ease;
        `;
        
        notification.innerHTML = `
            <i class="fas fa-exclamation-circle"></i> 
            Only ${remaining} ${remaining === 1 ? 'analysis' : 'analyses'} remaining today!
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    },
    
    // Handle login
    login: async function(email, password) {
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            
            if (data.success) {
                localStorage.setItem('authToken', data.token);
                localStorage.setItem('userEmail', data.email);
                localStorage.setItem('userPlan', data.plan);
                window.location.reload();
            } else {
                throw new Error(data.message || 'Login failed');
            }
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    },
    
    // Handle logout
    logout: async function() {
        try {
            await fetch('/api/logout', { method: 'POST' });
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            localStorage.removeItem('authToken');
            localStorage.removeItem('userEmail');
            localStorage.removeItem('userPlan');
            window.location.href = '/';
        }
    }
};

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        if (window.authAnalysis && typeof window.authAnalysis.init === 'function') {
            window.authAnalysis.init();
        }
    });
} else {
    // DOM is already ready
    if (window.authAnalysis && typeof window.authAnalysis.init === 'function') {
        window.authAnalysis.init();
    }
}
