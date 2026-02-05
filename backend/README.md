# Backend

FastAPI backend for D.A.M-SYSTEM Cognitive Firewall.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Download TextBlob corpora (first time only):
```bash
python -m textblob.download_corpora
```

3. Run the server:
```bash
python app.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /` - Root endpoint with API info
- `GET /health` - Health check
- `POST /analyze` - Analyze text and calculate distraction score

## Files

- `app.py` - FastAPI application with API endpoints
- `brain.py` - NLP logic for calculating distraction scores
- `requirements.txt` - Python dependencies
