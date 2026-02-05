/**
 * D.A.M-SYSTEM Content Script
 * Handles DOM manipulation and displays the HUD overlay with distraction scores
 */

// Configuration
const API_BASE_URL = 'http://localhost:8000';
const ANALYSIS_DELAY = 1000; // Wait 1 second after page load
let hudElement = null;
let isAnalyzing = false;

/**
 * Initialize the D.A.M-SYSTEM on page load
 */
function init() {
  console.log('D.A.M-SYSTEM: Initializing Cognitive Firewall...');
  
  // Create HUD element
  createHUD();
  
  // Wait for page to settle, then analyze
  setTimeout(() => {
    analyzePageContent();
  }, ANALYSIS_DELAY);
}

/**
 * Create the HUD overlay element
 */
function createHUD() {
  // Remove existing HUD if present
  if (hudElement) {
    hudElement.remove();
  }
  
  // Create HUD container
  hudElement = document.createElement('div');
  hudElement.id = 'dam-system-hud';
  hudElement.className = 'dam-hud';
  hudElement.innerHTML = `
    <div class="dam-hud-header">
      <span class="dam-hud-icon">🦫🛡️</span>
      <span class="dam-hud-title">D.A.M-SYSTEM</span>
      <button class="dam-hud-close" id="dam-close-btn">×</button>
    </div>
    <div class="dam-hud-content">
      <div class="dam-hud-loading">
        <div class="dam-spinner"></div>
        <p>Analyzing content...</p>
      </div>
      <div class="dam-hud-results" style="display: none;">
        <div class="dam-score-display">
          <div class="dam-score-label">Distraction Score</div>
          <div class="dam-score-value" id="dam-score">--</div>
          <div class="dam-score-bar">
            <div class="dam-score-fill" id="dam-score-fill"></div>
          </div>
        </div>
        <div class="dam-analysis" id="dam-analysis">--</div>
        <div class="dam-details">
          <div class="dam-detail-item">
            <span class="dam-detail-label">Sentiment:</span>
            <span class="dam-detail-value" id="dam-sentiment">--</span>
          </div>
          <div class="dam-detail-item">
            <span class="dam-detail-label">Subjectivity:</span>
            <span class="dam-detail-value" id="dam-subjectivity">--</span>
          </div>
        </div>
      </div>
      <div class="dam-hud-error" style="display: none;">
        <p id="dam-error-message">Analysis failed</p>
      </div>
    </div>
  `;
  
  // Add to page
  document.body.appendChild(hudElement);
  
  // Add close button listener
  const closeBtn = document.getElementById('dam-close-btn');
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      hudElement.style.display = 'none';
    });
  }
}

/**
 * Extract text content from the page
 */
function extractPageText() {
  // Get main content areas (articles, main, body text)
  const contentSelectors = [
    'article',
    'main',
    '[role="main"]',
    '.content',
    '.article-body',
    '.post-content'
  ];
  
  let text = '';
  
  // Try to find main content area
  for (const selector of contentSelectors) {
    const element = document.querySelector(selector);
    if (element) {
      text = element.innerText;
      break;
    }
  }
  
  // Fallback to body text if no main content found
  if (!text) {
    text = document.body.innerText;
  }
  
  // Limit text length to avoid huge payloads
  const MAX_LENGTH = 10000;
  if (text.length > MAX_LENGTH) {
    text = text.substring(0, MAX_LENGTH);
  }
  
  return text.trim();
}

/**
 * Analyze page content using the backend API
 */
async function analyzePageContent() {
  if (isAnalyzing) return;
  isAnalyzing = true;
  
  try {
    // Extract page text
    const pageText = extractPageText();
    
    if (!pageText || pageText.length < 50) {
      showError('Insufficient content to analyze');
      return;
    }
    
    // Call API
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: pageText,
        url: window.location.href
      })
    });
    
    if (!response.ok) {
      throw new Error(`API returned ${response.status}`);
    }
    
    const result = await response.json();
    
    // Display results
    displayResults(result);
    
  } catch (error) {
    console.error('D.A.M-SYSTEM: Analysis error:', error);
    showError('Unable to connect to D.A.M-SYSTEM API. Make sure the backend is running.');
  } finally {
    isAnalyzing = false;
  }
}

/**
 * Display analysis results in the HUD
 */
function displayResults(result) {
  // Hide loading, show results
  const loading = hudElement.querySelector('.dam-hud-loading');
  const results = hudElement.querySelector('.dam-hud-results');
  const error = hudElement.querySelector('.dam-hud-error');
  
  loading.style.display = 'none';
  error.style.display = 'none';
  results.style.display = 'block';
  
  // Update score
  const scoreElement = document.getElementById('dam-score');
  const scoreFill = document.getElementById('dam-score-fill');
  const scorePercent = Math.round(result.distraction_score * 100);
  
  scoreElement.textContent = scorePercent;
  scoreFill.style.width = `${scorePercent}%`;
  
  // Color code based on score
  if (result.distraction_score >= 0.7) {
    scoreFill.className = 'dam-score-fill dam-score-high';
  } else if (result.distraction_score >= 0.4) {
    scoreFill.className = 'dam-score-fill dam-score-medium';
  } else {
    scoreFill.className = 'dam-score-fill dam-score-low';
  }
  
  // Update analysis
  document.getElementById('dam-analysis').textContent = result.analysis;
  
  // Update details
  document.getElementById('dam-sentiment').textContent = result.sentiment.toFixed(2);
  document.getElementById('dam-subjectivity').textContent = result.subjectivity.toFixed(2);
}

/**
 * Display error message in the HUD
 */
function showError(message) {
  const loading = hudElement.querySelector('.dam-hud-loading');
  const results = hudElement.querySelector('.dam-hud-results');
  const error = hudElement.querySelector('.dam-hud-error');
  
  loading.style.display = 'none';
  results.style.display = 'none';
  error.style.display = 'block';
  
  document.getElementById('dam-error-message').textContent = message;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
