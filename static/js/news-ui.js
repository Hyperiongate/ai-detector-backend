// News Analysis UI Functions 

// Tab switching
function switchTab(tabName) {
    // Remove active class from all tabs and contents
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Add active class to selected tab and content
    event.target.classList.add('active');
    document.getElementById(tabName + '-content').classList.add('active');
    
    // Load content if not already loaded
    loadTabContent(tabName);
}

// Input selection
function selectInput(type) {
    // Remove active class from all options
    document.querySelectorAll('.input-option').forEach(option => option.classList.remove('active'));
    
    // Add active class to selected option
    event.currentTarget.classList.add('active');
    
    // Show input area
    document.getElementById('input-area').style.display = 'block';
    
    // Update placeholder based on selection
    const input = document.getElementById('articleUrl');
    if (type === 'url') {
        input.placeholder = 'Enter article URL (e.g., https://example.com/article)';
    } else if (type === 'topic') {
        input.placeholder = 'Enter topic to analyze (e.g., "climate change policy")';
    } else if (type === 'comparison') {
        input.placeholder = 'Enter multiple URLs separated by commas';
    }
}

// Toggle claim explanations
function toggleClaim(element) {
    const dropdown = element.nextElementSibling;
    const arrow = element.querySelector('span');
    
    if (dropdown.classList.contains('open')) {
        dropdown.classList.remove('open');
        arrow.textContent = '▼';
    } else {
        dropdown.classList.add('open');
        arrow.textContent = '▲';
    }
}

// Show style detail
function showStyleDetail(type) {
    let message = '';
    switch(type) {
        case 'quotes':
            message = 'Direct Quotes Analysis:\n\n• 12 expert sources quoted\n• Balanced representation (6 industry, 4 government, 2 academic)\n• Average quote length: 23 words\n• All quotes properly attributed\n• No anonymous sources';
            break;
        case 'data':
            message = 'Data & Statistics:\n\n• $2.5 billion funding figure\n• 15 tech CEOs signed support letter\n• Q1 2026 implementation date\n• 70% industry approval rate (survey)\n• 18-month compliance period\n• $10M revenue threshold\n• 3 oversight committee members\n• 90-day public comment period';
            break;
        case 'context':
            message = 'Background Context:\n\n• Previous AI regulation attempts explained\n• International regulatory comparison provided\n• Technical concepts defined for general audience\n• Historical timeline of AI policy development\n• Key stakeholder positions summarized';
            break;
        case 'structure':
            message = 'Article Structure:\n\n• Lead: Main news (framework announcement)\n• Supporting details in order of importance\n• Expert reactions and quotes\n• Background and context\n• Future implications\n• Clear section breaks with subheadings\n• Conclusion summarizing key points';
            break;
    }
    
    // In production, replace with modal
    alert(message);
}

// Show upgrade modal
function showUpgrade() {
    // In production, show proper modal
    alert('Pro Analysis Features:\n\n• Comprehensive 30+ page PDF report\n• Advanced bias detection algorithms\n• Historical pattern analysis\n• Real-time monitoring and alerts\n• API access for automation\n• Priority customer support\n\nContact sales@newsanalysis.ai for pricing');
}
