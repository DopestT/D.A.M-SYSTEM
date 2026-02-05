// DAM System - Popup Script

const hudToggle = document.getElementById('hud-toggle');
const soberToggle = document.getElementById('sober-toggle');
const backendStatus = document.getElementById('backend-status');

// Load current settings
chrome.storage.sync.get(['hudEnabled', 'soberMode'], (result) => {
  hudToggle.checked = result.hudEnabled !== false;
  soberToggle.checked = result.soberMode || false;
});

// Save settings when toggles change
hudToggle.addEventListener('change', (e) => {
  chrome.storage.sync.set({ hudEnabled: e.target.checked });
});

soberToggle.addEventListener('change', (e) => {
  chrome.storage.sync.set({ soberMode: e.target.checked });
});

// Check backend status
async function checkBackendStatus() {
  try {
    const response = await fetch('http://localhost:8000/health');
    if (response.ok) {
      backendStatus.textContent = '✓ Connected';
      backendStatus.style.color = '#2ecc71';
    } else {
      backendStatus.textContent = '✗ Error';
      backendStatus.style.color = '#e74c3c';
    }
  } catch (error) {
    backendStatus.textContent = '✗ Offline';
    backendStatus.style.color = '#e74c3c';
  }
}

checkBackendStatus();
