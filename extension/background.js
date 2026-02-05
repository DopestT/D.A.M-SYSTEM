// DAM System - Background Service Worker
// Handles API communication with backend

const API_BASE_URL = 'http://localhost:8000';

// Handle messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'analyzeText') {
    analyzeText(request.text, request.baseline)
      .then(response => sendResponse({ success: true, data: response }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Will respond asynchronously
  } else if (request.action === 'depaintText') {
    depaintText(request.text)
      .then(response => sendResponse({ success: true, data: response }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
});

// Analyze text via backend API
async function analyzeText(text, baseline = '') {
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: text,
      baseline_text: baseline
    })
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
}

// De-paint text via backend API
async function depaintText(text) {
  const response = await fetch(`${API_BASE_URL}/api/depaint`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: text
    })
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
}

// Listen for extension installation
chrome.runtime.onInstalled.addListener(() => {
  console.log('DAM Cognitive Firewall installed');
  
  // Set default settings
  chrome.storage.sync.set({
    soberMode: false,
    hudEnabled: true,
    apiUrl: API_BASE_URL
  });
});
