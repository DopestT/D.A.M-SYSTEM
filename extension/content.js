// DAM System - Content Script
// Injects HUD overlay and implements Sober Mode

let soberMode = false;
let hudEnabled = true;
let hudElement = null;
let processedElements = new WeakSet();

// Initialize
init();

async function init() {
  // Load settings
  const settings = await chrome.storage.sync.get(['soberMode', 'hudEnabled']);
  soberMode = settings.soberMode || false;
  hudEnabled = settings.hudEnabled !== false;

  if (hudEnabled) {
    createHUD();
  }

  if (soberMode) {
    activateSoberMode();
  }

  // Listen for settings changes
  chrome.storage.onChanged.addListener((changes) => {
    if (changes.soberMode) {
      soberMode = changes.soberMode.newValue;
      if (soberMode) {
        activateSoberMode();
      } else {
        deactivateSoberMode();
      }
    }
    if (changes.hudEnabled) {
      hudEnabled = changes.hudEnabled.newValue;
      if (hudEnabled && !hudElement) {
        createHUD();
      } else if (!hudEnabled && hudElement) {
        hudElement.remove();
        hudElement = null;
      }
    }
  });

  // Monitor DOM changes
  observePageChanges();
}

function createHUD() {
  // Create HUD overlay
  hudElement = document.createElement('div');
  hudElement.id = 'dam-hud';
  hudElement.innerHTML = `
    <div class="dam-hud-header">
      <span class="dam-logo">🦫 DAM</span>
      <button class="dam-close" id="dam-close-btn">×</button>
    </div>
    <div class="dam-hud-content">
      <div class="dam-score-display">
        <div class="dam-score-label">Distraction Score</div>
        <div class="dam-score-value" id="dam-score">--</div>
      </div>
      <div class="dam-metrics">
        <div class="dam-metric">
          <span class="dam-metric-label">Sentiment:</span>
          <span class="dam-metric-value" id="dam-sentiment">--</span>
        </div>
        <div class="dam-metric">
          <span class="dam-metric-label">Hyperbole:</span>
          <span class="dam-metric-value" id="dam-hyperbole">--</span>
        </div>
        <div class="dam-metric">
          <span class="dam-metric-label">Adjectives:</span>
          <span class="dam-metric-value" id="dam-adjectives">--</span>
        </div>
      </div>
      <div class="dam-status" id="dam-status">Ready</div>
    </div>
  `;
  
  document.body.appendChild(hudElement);

  // Add close button handler
  document.getElementById('dam-close-btn').addEventListener('click', () => {
    hudElement.style.display = 'none';
  });

  // Analyze page content
  analyzePage();
}

async function analyzePage() {
  // Get main article content
  const articleText = extractArticleText();
  
  if (!articleText || articleText.length < 50) {
    updateHUDStatus('No article content found');
    return;
  }

  updateHUDStatus('Analyzing...');

  try {
    // Send to background script for API call
    const response = await chrome.runtime.sendMessage({
      action: 'analyzeText',
      text: articleText,
      baseline: ''
    });

    if (response.success) {
      updateHUD(response.data);
      updateHUDStatus('Analysis complete');
    } else {
      updateHUDStatus('Error: ' + response.error);
    }
  } catch (error) {
    updateHUDStatus('Error: Backend not available');
    console.error('DAM analysis error:', error);
  }
}

function extractArticleText() {
  // Try to find article content using common selectors
  const selectors = [
    'article',
    '[role="article"]',
    '.article-body',
    '.story-body',
    '.post-content',
    'main'
  ];

  for (const selector of selectors) {
    const element = document.querySelector(selector);
    if (element) {
      return element.innerText.substring(0, 5000); // Limit to first 5000 chars
    }
  }

  // Fallback to body text
  return document.body.innerText.substring(0, 5000);
}

function updateHUD(data) {
  const scoreElement = document.getElementById('dam-score');
  const sentimentElement = document.getElementById('dam-sentiment');
  const hyperboleElement = document.getElementById('dam-hyperbole');
  const adjectivesElement = document.getElementById('dam-adjectives');

  if (scoreElement) {
    scoreElement.textContent = (data.distraction_score * 100).toFixed(0) + '%';
    
    // Color code based on score
    scoreElement.className = 'dam-score-value';
    if (data.distraction_score > 0.7) {
      scoreElement.classList.add('dam-score-high');
    } else if (data.distraction_score > 0.4) {
      scoreElement.classList.add('dam-score-medium');
    } else {
      scoreElement.classList.add('dam-score-low');
    }
  }

  if (sentimentElement) {
    sentimentElement.textContent = data.sentiment_polarity.toFixed(2);
  }

  if (hyperboleElement) {
    hyperboleElement.textContent = (data.topical_divergence * 100).toFixed(0) + '%';
  }

  if (adjectivesElement) {
    adjectivesElement.textContent = data.adjective_count;
  }
}

function updateHUDStatus(status) {
  const statusElement = document.getElementById('dam-status');
  if (statusElement) {
    statusElement.textContent = status;
  }
}

function activateSoberMode() {
  // Find all text nodes and de-paint them
  const textNodes = getTextNodes(document.body);
  
  textNodes.forEach(async (node) => {
    if (processedElements.has(node) || !node.textContent.trim()) {
      return;
    }

    const originalText = node.textContent;
    
    if (originalText.length < 20) {
      return; // Skip short text
    }

    try {
      const response = await chrome.runtime.sendMessage({
        action: 'depaintText',
        text: originalText
      });

      if (response.success && response.data.de_painted_text !== originalText) {
        // Store original text
        if (!node.parentElement.hasAttribute('data-dam-original')) {
          node.parentElement.setAttribute('data-dam-original', originalText);
        }
        
        // Replace with de-painted text
        node.textContent = response.data.de_painted_text;
        node.parentElement.classList.add('dam-depainted');
        processedElements.add(node);
      }
    } catch (error) {
      console.error('DAM de-paint error:', error);
    }
  });
}

function deactivateSoberMode() {
  // Restore original text
  const depaintedElements = document.querySelectorAll('.dam-depainted');
  
  depaintedElements.forEach((element) => {
    const original = element.getAttribute('data-dam-original');
    if (original) {
      element.textContent = original;
      element.removeAttribute('data-dam-original');
      element.classList.remove('dam-depainted');
    }
  });
  
  processedElements = new WeakSet();
}

function getTextNodes(element) {
  const textNodes = [];
  const walker = document.createTreeWalker(
    element,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode: function(node) {
        // Skip script, style, and the HUD
        if (node.parentElement.tagName === 'SCRIPT' ||
            node.parentElement.tagName === 'STYLE' ||
            node.parentElement.closest('#dam-hud')) {
          return NodeFilter.FILTER_REJECT;
        }
        return NodeFilter.FILTER_ACCEPT;
      }
    }
  );

  let node;
  while (node = walker.nextNode()) {
    textNodes.push(node);
  }

  return textNodes;
}

function observePageChanges() {
  // Watch for dynamic content changes
  const observer = new MutationObserver((mutations) => {
    if (soberMode) {
      // Re-apply sober mode to new content
      setTimeout(() => activateSoberMode(), 500);
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
}
