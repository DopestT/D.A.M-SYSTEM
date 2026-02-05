# DAM Chrome Extension

This is the Chrome Extension component of the DAM Cognitive Firewall system.

## Features

- **HUD Overlay**: Displays real-time distraction metrics on news websites
- **Sober Mode**: Strips hyperbolic language from articles
- **Popup Interface**: Easy toggle controls for all features
- **Automatic Analysis**: Analyzes page content automatically

## Installation

1. Make sure the DAM backend is running on `http://localhost:8000`
2. Open Chrome and go to `chrome://extensions/`
3. Enable "Developer mode" (toggle in top-right)
4. Click "Load unpacked"
5. Select this `extension` directory
6. The DAM icon should appear in your browser toolbar

## Supported Websites

The extension currently works on:
- CNN
- Fox News
- BBC
- New York Times
- Washington Post
- Generic news sites

To add more sites, edit `manifest.json` and add to the `matches` array.

## Files

- `manifest.json` - Extension configuration (Manifest V3)
- `background.js` - Service worker for API communication
- `content.js` - Injected script for HUD and Sober Mode
- `popup.html` - Extension popup interface
- `popup.js` - Popup logic
- `styles.css` - Styling for HUD and popup
- `icon*.png` - Extension icons

## Usage

1. Navigate to a supported news website
2. The HUD will appear in the top-right corner showing the distraction score
3. Click the extension icon to access controls
4. Toggle "Sober Mode" to activate de-painting
5. Toggle "HUD Overlay" to show/hide the metrics display

## Development

The extension communicates with the backend API at `http://localhost:8000`. You can change this URL in `background.js` by modifying the `API_BASE_URL` constant.

## Customization

### Change HUD Position
Edit `styles.css` and modify the `#dam-hud` position properties.

### Change Colors
Edit the color values in `styles.css` to match your preferences.

### Add More Metrics
Modify `content.js` to display additional metrics from the API response.
