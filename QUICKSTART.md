# DAM System - Quick Start Guide

## 🚀 Quick Start (5 minutes)

### Step 1: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m textblob.download_corpora
```

### Step 2: Start the Backend

```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Verify Backend is Running

Open your browser and go to:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Step 4: Load Chrome Extension

1. Open Chrome
2. Go to `chrome://extensions/`
3. Enable "Developer mode" (top-right toggle)
4. Click "Load unpacked"
5. Select the `extension` folder
6. You should see the DAM extension icon appear

### Step 5: Test It Out

1. Go to any news website (e.g., https://www.bbc.com/news)
2. The HUD should appear in the top-right corner
3. Click the extension icon to toggle Sober Mode

## 🧪 Testing

```bash
# Run backend tests
pytest tests/ -v

# Test a specific endpoint
curl -X POST http://localhost:8000/api/depaint \
  -H "Content-Type: application/json" \
  -d '{"text": "The very amazing cat is extremely happy."}'
```

## ⚠️ Troubleshooting

### Backend won't start
- Make sure you're using Python 3.8+
- Install dependencies: `pip install -r requirements.txt`
- Download Spacy model: `python -m spacy download en_core_web_sm`

### Extension not loading
- Make sure Developer mode is enabled in Chrome
- Check that the backend is running on port 8000
- Look at the browser console for errors

### HUD not appearing
- Check that the website is in the manifest.json matches list
- Verify backend is running: http://localhost:8000/health
- Check browser console for errors (F12)

### Sober Mode not working
- Ensure backend is running and Spacy model is installed
- Check that the website has article content
- Look for errors in browser console

## 📚 Next Steps

- Read the full [README.md](../README.md) for detailed documentation
- Explore the API at http://localhost:8000/docs
- Customize the extension in `extension/manifest.json`
- Modify distraction score weights in `backend/main.py`
