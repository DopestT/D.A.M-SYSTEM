# 🦫 DAM System - Cognitive Firewall

**D**istraction **A**nalysis & **M**itigation System

DAM System is an open-source "Cognitive Firewall" designed to neutralize "Flood the Zone" media tactics. Using a Python/FastAPI backend and a Chrome extension, it calculates a **Distraction Score**, strips rhetorical "paint" (hyperbole) in real-time with the **De-Painter**, and helps you reclaim your focus from the noise.

## 🎯 Features

### Backend API (FastAPI + Spacy + TextBlob)
- **Distraction Score Calculation**: Analyzes text for sentiment spikes and topical divergence from factual reporting
- **De-Painter Function**: Strips adjectives and intensifiers to reveal core factual content
- **Sentiment Analysis**: Detects extreme emotional language using TextBlob
- **Topical Divergence**: Measures ratio of hyperbole to factual content using Spacy NLP
- **RESTful API**: Easy integration with any frontend

### Chrome Extension (Manifest V3)
- **HUD Overlay**: Real-time distraction score display on news websites
- **Sober Mode**: Visually suppress hyperbolic text by de-painting articles
- **Automatic Analysis**: Analyzes article content as you browse
- **Manual Control**: Toggle features on/off via popup interface
- **Modern Design**: Sleek, unobtrusive interface with dark theme

## 📋 Requirements

### Backend
- Python 3.8+
- FastAPI
- Spacy (with `en_core_web_sm` model)
- TextBlob
- Uvicorn

### Extension
- Google Chrome or Chromium-based browser
- Running DAM backend on localhost:8000

## 🚀 Installation

### 1. Backend Setup

Navigate to the backend directory and install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Download the Spacy language model:

```bash
python -m spacy download en_core_web_sm
```

Download TextBlob corpora (first time only):

```bash
python -m textblob.download_corpora
```

### 2. Start the Backend Server

```bash
cd backend
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

Check the API documentation at `http://localhost:8000/docs`

### 3. Install Chrome Extension

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right corner)
3. Click "Load unpacked"
4. Select the `extension` directory from this repository
5. The DAM extension should now appear in your extensions

## 📖 Usage

### Using the Extension

1. **Navigate to a news website** (e.g., CNN, Fox News, BBC, NY Times)
2. **The HUD overlay** will automatically appear in the top-right corner
3. **View the Distraction Score** and metrics:
   - Distraction Score: 0-100% (lower is better)
   - Sentiment: Emotional polarity of the text
   - Hyperbole: Percentage of hyperbolic content
   - Adjectives: Count of removed descriptive words

4. **Toggle Sober Mode**:
   - Click the extension icon
   - Enable "Sober Mode" toggle
   - Articles will be automatically de-painted to show only factual content
   - Hover over de-painted text to see it's been processed

### Using the API Directly

#### Analyze Text

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This absolutely incredible breakthrough is totally revolutionary!",
    "baseline_text": "The company announced a new product."
  }'
```

Response:
```json
{
  "distraction_score": 0.653,
  "sentiment_polarity": 0.825,
  "sentiment_subjectivity": 0.9,
  "adjective_count": 4,
  "topical_divergence": 0.712,
  "original_text": "This absolutely incredible breakthrough is totally revolutionary!",
  "de_painted_text": "This breakthrough is revolutionary!"
}
```

#### De-Paint Text

```bash
curl -X POST "http://localhost:8000/api/depaint" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The quick brown fox jumps over the lazy dog."
  }'
```

Response:
```json
{
  "original_text": "The quick brown fox jumps over the lazy dog.",
  "de_painted_text": "The fox jumps over the dog.",
  "removed_adjectives": ["quick", "brown", "lazy"]
}
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest tests/ -v
```

Note: Some tests require the Spacy model to be installed and will be skipped if not available.

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│     Chrome Extension (Manifest V3)  │
│  ┌──────────┐  ┌─────────────────┐ │
│  │  Popup   │  │  Content Script │ │
│  │   UI     │  │   (HUD + Sober) │ │
│  └────┬─────┘  └────────┬────────┘ │
│       │                 │          │
│  ┌────▼──────────────────▼───────┐ │
│  │   Background Service Worker   │ │
│  └────────────┬──────────────────┘ │
└───────────────┼────────────────────┘
                │
                │ HTTP/JSON
                ▼
┌───────────────────────────────────────┐
│      FastAPI Backend (Python)         │
│  ┌─────────────────────────────────┐  │
│  │      API Endpoints              │  │
│  │  • /api/analyze                 │  │
│  │  • /api/depaint                 │  │
│  │  • /health                      │  │
│  └────────┬────────────────────────┘  │
│           │                           │
│  ┌────────▼────────┐  ┌────────────┐ │
│  │  Spacy NLP      │  │  TextBlob  │ │
│  │  (Topical       │  │  (Sentiment│ │
│  │   Analysis)     │  │   Analysis)│ │
│  └─────────────────┘  └────────────┘ │
└───────────────────────────────────────┘
```

## 🔧 API Documentation

### `POST /api/analyze`
Analyze text and calculate distraction score.

**Request Body:**
- `text` (string, required): Text to analyze
- `baseline_text` (string, optional): Baseline text for comparison

**Response:**
- `distraction_score` (float): 0-1, combined metric of distraction
- `sentiment_polarity` (float): -1 to 1, emotional tone
- `sentiment_subjectivity` (float): 0-1, subjectivity level
- `adjective_count` (int): Number of adjectives detected
- `topical_divergence` (float): 0-1, hyperbole ratio
- `original_text` (string): Input text
- `de_painted_text` (string): Text with adjectives removed

### `POST /api/depaint`
Remove adjectives and intensifiers from text.

**Request Body:**
- `text` (string, required): Text to de-paint

**Response:**
- `original_text` (string): Input text
- `de_painted_text` (string): Text with adjectives removed
- `removed_adjectives` (array): List of removed words

### `GET /health`
Health check endpoint.

**Response:**
- `status` (string): "healthy" if operational
- `nlp_model` (string): Loaded Spacy model name

## 🎨 Customization

### Modify Distraction Score Weights

Edit `backend/main.py` line ~185:

```python
# Current weights:
distraction_score = (sentiment_spike * 0.4) + (topical_divergence * 0.6)

# Adjust to your preference:
distraction_score = (sentiment_spike * 0.5) + (topical_divergence * 0.5)
```

### Add More News Sites

Edit `extension/manifest.json` to add more sites to the `matches` array:

```json
"matches": [
  "*://*.yournewssite.com/*"
]
```

### Customize HUD Appearance

Edit `extension/styles.css` to modify colors, position, or styling.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🛡️ Privacy & Security

- **No data collection**: DAM processes all text locally and via your own backend
- **No tracking**: The extension does not track your browsing
- **Open source**: All code is transparent and auditable
- **Local processing**: Your data never leaves your machine (except to your own API)

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- NLP powered by [Spacy](https://spacy.io/)
- Sentiment analysis by [TextBlob](https://textblob.readthedocs.io/)
- Inspired by the need to combat information overload and media manipulation

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Remember**: DAM is a tool to help you think critically about the content you consume. It's not a replacement for your own judgment and critical thinking. 🧠🛡️
