# Extension

Chrome extension (Manifest V3) for D.A.M-SYSTEM Cognitive Firewall.

## Installation

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select this `extension` folder

## Usage

1. Make sure the backend is running at `http://localhost:8000`
2. Navigate to any webpage
3. The D.A.M-SYSTEM HUD will appear in the top-right corner
4. View the distraction score and analysis

## Files

- `manifest.json` - Chrome extension manifest (Manifest V3)
- `content.js` - Content script for DOM manipulation and API integration
- `style.css` - HUD styling
