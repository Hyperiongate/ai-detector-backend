/* ============================================
   NEWS VERIFICATION PLATFORM - COMPONENT STYLES
   ============================================ */

/* Beta Banner */
.beta-banner {
    background: linear-gradient(45deg, #ff6b35, #f7931e);
    padding: 8px 0;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.beta-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(45deg, transparent, rgba(255,255,255,0.3), transparent);
    animation: shimmer 3s infinite;
    transform: rotate(45deg);
}

.beta-content {
    position: relative;
    z-index: 2;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 15px;
    color: white;
    font-weight: 600;
}

.beta-badge {
    background: rgba(255,255,255,0.2);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: bold;
}

.beta-join-btn {
    background: rgba(255,255,255,0.2);
    border: 2px solid rgba(255,255,255,0.3);
    color: white;
    padding: 6px 16px;
    border-radius: 25px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
    text-decoration: none;
    font-size: 0.9rem;
}

.beta-join-btn:hover {
    background: rgba(255,255,255,0.3);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

/* Modal Styles */
.modal {
    display: none;
    position: fixed;
    z-index: 10000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.8);
    backdrop-filter: blur(5px);
}

.modal-content {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    margin: 5% auto;
    padding: 0;
    border-radius: 20px;
    width: 90%;
    max-width: 500px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

.modal-header {
    background: rgba(255,255,255,0.1);
    padding: 2rem;
    text-align: center;
    border-bottom: 1px solid rgba(255,255,255,0.2);
}

.modal-header h2 {
    color: white;
    margin-bottom: 0.5rem;
    font-size: 1.8rem;
}

.modal-header p {
    color: rgba(255,255,255,0.8);
    font-size: 1rem;
}

.modal-body {
    padding: 2rem;
}

.modal-body .input-group {
    margin-bottom: 1rem;
}

.modal-body input {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.3);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    width: 100%;
    font-size: 1rem;
}

.modal-body input::placeholder {
    color: rgba(255,255,255,0.6);
}

.modal-footer {
    padding: 1.5rem 2rem 2rem;
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
}

.close {
    position: absolute;
    right: 1rem;
    top: 1rem;
    color: rgba(255,255,255,0.8);
    font-size: 2rem;
    font-weight: bold;
    cursor: pointer;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
}

.close:hover {
    background: rgba(255,255,255,0.2);
    color: white;
}

/* Info Sections Grid */
.info-sections-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
    margin-bottom: 30px;
}

/* Compact Dropdown Sections */
.dropdown-section.compact {
    border: 2px solid rgba(102, 126, 234, 0.15);
    border-radius: 12px;
    overflow: hidden;
    background: rgba(249, 250, 251, 0.5);
    transition: all 0.3s ease;
}

.dropdown-section.compact:hover {
    border-color: rgba(102, 126, 234, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
}

.dropdown-section.compact.active {
    border-color: #667eea;
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.15);
}

.compact-header {
    background: rgba(102, 126, 234, 0.05);
    padding: 15px 18px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: all 0.3s ease;
}

.compact-header:hover {
    background: rgba(102, 126, 234, 0.08);
}

.compact-header.open {
    background: rgba(102, 126, 234, 0.12);
    border-bottom: 2px solid rgba(102, 126, 234, 0.2);
}

.compact-header-content {
    display: flex;
    align-items: center;
    gap: 12px;
}

.compact-header-content i {
    font-size: 1.3rem;
    color: #667eea;
}

.compact-header-text {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.compact-title {
    font-weight: 700;
    color: #4a5568;
    font-size: 1rem;
}

.compact-subtitle {
    font-size: 0.85rem;
    color: #6b7280;
    font-weight: 400;
}

.compact-header .dropdown-icon {
    font-size: 1rem;
    color: #6b7280;
    transition: transform 0.3s ease;
}

.compact-header.open .dropdown-icon {
    transform: rotate(180deg);
    color: #667eea;
}

.dropdown-section.compact .dropdown-content {
    max-height: 0;
    overflow: hidden;
    padding: 0;
    background: white;
    border-top: 1px solid rgba(102, 126, 234, 0.1);
    transition: all 0.5s ease;
}

.dropdown-section.compact .dropdown-content.open {
    max-height: 600px;
    padding: 25px;
    overflow-y: auto;
}

#usage-section .compact-header-content i {
    color: #10b981;
}

/* Tools Section */
.tools-employed {
    background: linear-gradient(145deg, #f8fafc, #ffffff);
    border-radius: 15px;
    padding: 25px;
    margin-bottom: 30px;
    border: 2px solid rgba(102, 126, 234, 0.1);
    position: relative;
    overflow: hidden;
}

.tools-employed::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #10b981, #667eea, #764ba2);
    animation: pulse 2s infinite;
}

.tools-title {
    font-weight: 700;
    color: #4a5568;
    margin-bottom: 20px;
    font-size: 1.2rem;
    display: flex;
    align-items: center;
    gap: 10px;
}

.tools-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 15px;
}

.tool-item {
    background: rgba(102, 126, 234, 0.05);
    padding: 15px 20px;
    border-radius: 12px;
    border-left: 4px solid #667eea;
    font-size: 0.95rem;
    font-weight: 600;
    color: #4a5568;
    transition: all 0.3s ease;
}

.tool-item:hover {
    background: rgba(102, 126, 234, 0.1);
    transform: translateY(-2px);
}

.tool-item i {
    margin-right: 8px;
    color: #667eea;
}

/* Progress Section */
.progress-section {
    margin-bottom: 30px;
    background: linear-gradient(145deg, #f8fafc, #ffffff);
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    border: 2px solid rgba(102, 126, 234, 0.1);
    position: sticky;
    top: 80px;
    z-index: 100;
    overflow: hidden;
}

.progress-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #667eea, #10b981, #764ba2, #667eea);
    background-size: 300% 100%;
    animation: rainbow-flow 4s ease-in-out infinite;
}

@keyframes rainbow-flow {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

.progress-title {
    font-weight: 700;
    color: #4a5568;
    margin-bottom: 25px;
    font-size: 1.3rem;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
}

/* Multi-stage progress indicators */
.progress-stages {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
    padding: 0 20px;
}

.progress-stage {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    position: relative;
}

.progress-stage:not(:last-child)::after {
    content: '';
    position: absolute;
    top: 20px;
    left: 60%;
    width: 80%;
    height: 2px;
    background: #e2e8f0;
    z-index: -1;
}

.progress-stage.active::after {
    background: linear-gradient(90deg, #667eea, #10b981);
}

.progress-stage.completed::after {
    background: #10b981;
}

.stage-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #e2e8f0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    margin-bottom: 8px;
    transition: all 0.3s ease;
}

.progress-stage.active .stage-icon {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    animation: stagePulse 1s ease-in-out infinite;
}

.progress-stage.completed .stage-icon {
    background: #10b981;
    color: white;
}

@keyframes stagePulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}

.stage-label {
    font-size: 0.8rem;
    color: #6b7280;
    text-align: center;
    max-width: 100px;
}

.progress-stage.active .stage-label {
    color: #667eea;
    font-weight: 600;
}

.progress-stage.completed .stage-label {
    color: #10b981;
}

/* Progress Bar */
.progress-bar {
    background: #e2e8f0;
    height: 30px;
    border-radius: 15px;
    overflow: hidden;
    position: relative;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
    border: 2px solid rgba(255, 255, 255, 0.8);
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, 
        #ff6b6b 0%, 
        #f06595 14%, 
        #cc5de8 28%, 
        #845ef7 42%, 
        #5c7cfa 56%, 
        #339af0 70%, 
        #22b8cf 84%, 
        #20c997 100%);
    border-radius: 13px;
    width: 0%;
    transition: width 0.5s ease;
    position: relative;
    background-size: 200% 100%;
    animation: gradient-shift 3s ease-in-out infinite;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

@keyframes gradient-shift {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

.progress-fill::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, 
        transparent, 
        rgba(255,255,255,0.6), 
        transparent);
    animation: shine 2s infinite;
}

@keyframes shine {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

.progress-percentage {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-weight: bold;
    color: white;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    font-size: 1.1rem;
    z-index: 2;
}

.progress-status {
    text-align: center;
    color: #6b7280;
    font-size: 1.1rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
}

.progress-spinner {
    display: inline-block;
    width: 24px;
    height: 24px;
    border: 3px solid transparent;
    border-top: 3px solid #667eea;
    border-right: 3px solid #10b981;
    border-bottom: 3px solid #764ba2;
    border-left: 3px solid #f59e0b;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

/* Summary Banner */
.summary-banner {
    background: linear-gradient(135deg, #ffffff, #f8fafc);
    border-radius: 20px;
    padding: 35px;
    margin-bottom: 25px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    border: 2px solid rgba(102, 126, 234, 0.15);
    position: relative;
    overflow: hidden;
}

.summary-banner::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 5px;
    background: linear-gradient(90deg, #10b981, #667eea, #764ba2);
    animation: pulse 3s infinite;
}

.credibility-header {
    display: flex;
    align-items: center;
    gap: 30px;
    margin-bottom: 25px;
}

.credibility-score-container {
    flex-shrink: 0;
    position: relative;
}

.credibility-score-circle {
    width: 180px;
    height: 180px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    flex-shrink: 0;
    background: conic-gradient(
        from 0deg,
        #ff6b6b 0deg,
        #feca57 90deg,
        #48dbfb 180deg,
        #1dd1a1 270deg,
        #ff6b6b 360deg
    );
}

@keyframes rotateGradient {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.credibility-score-circle::before {
    content: '';
    position: absolute;
    width: 150px;
    height: 150px;
    background: white;
    border-radius: 50%;
    z-index: 1;
}

.score-number {
    font-size: 3.5rem;
    font-weight: 900;
    color: #1f2937;
    z-index: 2;
    text-shadow: 0 0 20px rgba(102, 126, 234, 0.8);
}

.score-label {
    font-size: 0.9rem;
    color: #6b7280;
    font-weight: 600;
    z-index: 2;
}

.score-indicator {
    position: absolute;
    width: 100%;
    height: 100%;
    z-index: 3;
    pointer-events: none;
}

.score-indicator::after {
    content: '';
    position: absolute;
    top: 10px;
    left: 50%;
    width: 4px;
    height: 30px;
    background: #1f2937;
    transform-origin: center 80px;
    transform: translateX(-50%) rotate(var(--score-rotation));
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.8);
}

/* Quick Actions */
.quick-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin-top: 2rem;
}

.quick-action {
    padding: 0.5rem 1rem;
    background: rgba(102, 126, 234, 0.1);
    border: 1px solid rgba(102, 126, 234, 0.3);
    border-radius: 8px;
    color: #667eea;
    text-decoration: none;
    font-size: 0.875rem;
    transition: all 0.3s ease;
}

.quick-action:hover {
    background: rgba(102, 126, 234, 0.2);
    transform: translateY(-2px);
}

.credibility-details {
    flex: 1;
}

.credibility-title {
    font-size: 1.8rem;
    font-weight: 800;
    color: #1f2937;
    margin-bottom: 10px;
}

.credibility-subtitle {
    font-size: 1.1rem;
    color: #6b7280;
    line-height: 1.6;
    margin-bottom: 15px;
}

.methodology-note {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(102, 126, 234, 0.1);
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 0.9rem;
    color: #667eea;
    font-weight: 600;
}

.pro-upgrade-note {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(217, 119, 6, 0.1));
    border: 2px solid rgba(245, 158, 11, 0.3);
    border-radius: 15px;
    padding: 20px;
    margin-top: 20px;
    text-align: center;
}

.pro-upgrade-note p {
    color: #d97706;
    font-weight: 600;
    font-size: 1.05rem;
    margin-bottom: 12px;
}

.pro-upgrade-note button {
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: white;
    border: none;
    padding: 12px 30px;
    border-radius: 25px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 1rem;
}

.pro-upgrade-note button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(245, 158, 11, 0.4);
}

/* Analysis Section Styles */
.analysis-section {
    background: white;
    border-radius: 15px;
    margin-bottom: 20px;
    overflow: hidden;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
    border: 2px solid rgba(102, 126, 234, 0.1);
    transition: all 0.3s ease;
}

.analysis-section.expanded {
    border-color: #667eea;
    box-shadow: 0 8px 30px rgba(102, 126, 234, 0.15);
}

.analysis-header {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(102, 126, 234, 0.1));
    padding: 25px 30px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: all 0.3s ease;
}

.analysis-header:hover {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.08), rgba(102, 126, 234, 0.15));
}

.analysis-header.expanded {
    border-bottom: 2px solid rgba(102, 126, 234, 0.2);
}

.analysis-header-content {
    display: flex;
    align-items: center;
    gap: 20px;
    flex: 1;
}

.analysis-icon {
    width: 50px;
    height: 50px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    background: white;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
}

.analysis-title-group {
    flex: 1;
}

.analysis-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 5px;
}

.analysis-summary {
    font-size: 0.95rem;
    color: #6b7280;
}

.expand-icon {
    font-size: 1.2rem;
    color: #667eea;
    transition: transform 0.3s ease;
}

.analysis-header.expanded .expand-icon {
    transform: rotate(180deg);
}

.analysis-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.5s ease;
}

.analysis-content.expanded {
    max-height: 2000px;
}

.analysis-body {
    padding: 30px;
}

.analysis-explanation {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(99, 102, 241, 0.1));
    border: 2px solid rgba(99, 102, 241, 0.2);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 25px;
    position: relative;
    overflow: hidden;
}

.analysis-explanation::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 5px;
    height: 100%;
    background: linear-gradient(180deg, #6366f1, #8b5cf6);
}

.analysis-explanation-icon {
    font-size: 1.3rem;
    color: #6366f1;
    margin-right: 10px;
}

.analysis-explanation-text {
    color: #4b5563;
    font-size: 1.05rem;
    line-height: 1.6;
    font-weight: 500;
}

/* Political Bias Compass Design */
.bias-compass-container {
    margin: 30px 0;
    padding: 20px;
    text-align: center;
}

.bias-compass-title {
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 30px;
    font-size: 1.4rem;
    text-align: center;
}

.bias-compass {
    position: relative;
    width: 300px;
    height: 300px;
    margin: 0 auto;
}

.compass-circle {
    position: absolute;
    border-radius: 50%;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}

.compass-outer {
    width: 300px;
    height: 300px;
    background: linear-gradient(45deg, #3b82f6 0%, #10b981 25%, #fbbf24 50%, #f59e0b 75%, #ef4444 100%);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.compass-inner {
    width: 200px;
    height: 200px;
    background: white;
    box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.1);
}

.compass-center {
    width: 80px;
    height: 80px;
    background: #f3f4f6;
    font-weight: 900;
    font-size: 1.8rem;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #1f2937;
}

.compass-labels {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
}

.compass-label {
    position: absolute;
    font-weight: 700;
    font-size: 0.9rem;
    color: #1f2937;
    background: white;
    padding: 5px 15px;
    border-radius: 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.compass-label.left {
    top: 50%;
    left: -20px;
    transform: translateY(-50%);
}

.compass-label.right {
    top: 50%;
    right: -20px;
    transform: translateY(-50%);
}

.compass-label.far-left {
    top: 20%;
    left: 10%;
}

.compass-label.far-right {
    top: 20%;
    right: 10%;
}

.compass-label.center {
    bottom: -40px;
    left: 50%;
    transform: translateX(-50%);
}

.compass-needle {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 4px;
    height: 120px;
    background: #1f2937;
    transform-origin: center bottom;
    transform: translate(-50%, -100%) rotate(0deg);
    transition: transform 1s ease;
    z-index: 10;
}

.compass-needle::before {
    content: '';
    position: absolute;
    top: -20px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 15px solid transparent;
    border-right: 15px solid transparent;
    border-bottom: 30px solid #1f2937;
}

.bias-position-badge {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 12px 25px;
    border-radius: 30px;
    font-weight: 700;
    font-size: 1.2rem;
    margin-top: 30px;
    display: inline-block;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

/* Enhanced Cross-Source Comparison */
.verification-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-bottom: 30px;
}

.stat-card {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(102, 126, 234, 0.1));
    border-radius: 15px;
    padding: 25px;
    text-align: center;
    border: 2px solid rgba(102, 126, 234, 0.2);
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
}

.stat-number {
    font-size: 2.5rem;
    font-weight: 900;
    color: #667eea;
    margin-bottom: 5px;
}

.stat-label {
    color: #6b7280;
    font-weight: 600;
}

.stat-icon {
    font-size: 2rem;
    color: #667eea;
    margin-bottom: 10px;
}

/* Emotional Language Meter */
.emotion-meter-container {
    margin: 30px 0;
}

.emotion-meter {
    background: #e5e7eb;
    height: 40px;
    border-radius: 20px;
    overflow: hidden;
    position: relative;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.emotion-fill {
    height: 100%;
    background: linear-gradient(90deg, #10b981 0%, #fbbf24 50%, #ef4444 100%);
    border-radius: 20px;
    transition: width 1s ease;
    position: relative;
}

.emotion-marker {
    position: absolute;
    top: -10px;
    transform: translateX(-50%);
    width: 4px;
    height: 60px;
    background: #1f2937;
}

.emotion-marker::before {
    content: attr(data-value);
    position: absolute;
    bottom: -30px;
    left: 50%;
    transform: translateX(-50%);
    background: #1f2937;
    color: white;
    padding: 4px 12px;
    border-radius: 15px;
    font-weight: 700;
    font-size: 0.9rem;
}

.emotion-labels {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
    color: #6b7280;
    font-size: 0.85rem;
    font-weight: 600;
}

/* Smaller detail cards */
.source-details-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-top: 20px;
}

.source-detail-card {
    background: rgba(249, 250, 251, 0.5);
    border: 2px solid rgba(102, 126, 234, 0.1);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    transition: all 0.3s ease;
}

.source-detail-card:hover {
    background: white;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
}

.detail-icon {
    width: 30px;
    height: 30px;
    margin: 0 auto 8px;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(102, 126, 234, 0.2));
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
}

.detail-value {
    font-size: 1.3rem;
    font-weight: 800;
    color: #1f2937;
    margin-bottom: 5px;
}

.detail-label {
    font-size: 0.85rem;
    color: #6b7280;
    font-weight: 600;
}

/* Enhanced Transparency Explanation */
.transparency-breakdown {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.05), rgba(16, 185, 129, 0.1));
    border-radius: 15px;
    padding: 25px;
    margin: 20px 0;
    border: 2px solid rgba(16, 185, 129, 0.2);
}

.transparency-item {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 15px;
    padding: 10px;
    background: white;
    border-radius: 10px;
    transition: all 0.3s ease;
}

.transparency-item:hover {
    transform: translateX(5px);
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
}

.transparency-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    flex-shrink: 0;
}

.transparency-icon.positive {
    background: rgba(16, 185, 129, 0.2);
    color: #059669;
}

.transparency-icon.negative {
    background: rgba(239, 68, 68, 0.2);
    color: #dc2626;
}

.transparency-text {
    flex: 1;
}

.transparency-title {
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 2px;
}

.transparency-description {
    font-size: 0.9rem;
    color: #6b7280;
    line-height: 1.4;
}
