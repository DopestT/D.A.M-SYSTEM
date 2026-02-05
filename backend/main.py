"""
DAM System - Cognitive Firewall Backend API
FastAPI application for calculating Distraction Scores and text de-painting
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import spacy
from textblob import TextBlob
from typing import List, Dict
import re

app = FastAPI(title="DAM Cognitive Firewall API", version="1.0.0")

# CORS middleware to allow Chrome extension to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify extension ID
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Spacy model for NLP processing
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Model not installed, will provide instructions
    nlp = None


class TextAnalysisRequest(BaseModel):
    text: str
    baseline_text: str = ""  # Optional baseline for comparison


class TextAnalysisResponse(BaseModel):
    distraction_score: float
    sentiment_polarity: float
    sentiment_subjectivity: float
    adjective_count: int
    topical_divergence: float
    original_text: str
    de_painted_text: str


class DePaintRequest(BaseModel):
    text: str


class DePaintResponse(BaseModel):
    original_text: str
    de_painted_text: str
    removed_adjectives: List[str]


def calculate_sentiment_spike(text: str, baseline: str = "") -> float:
    """
    Calculate sentiment spike by comparing text sentiment to baseline.
    Returns a score from 0-1 where higher means more extreme sentiment.
    """
    blob = TextBlob(text)
    sentiment = abs(blob.sentiment.polarity)
    
    if baseline:
        baseline_blob = TextBlob(baseline)
        baseline_sentiment = abs(baseline_blob.sentiment.polarity)
        spike = abs(sentiment - baseline_sentiment)
    else:
        # Without baseline, use absolute polarity as spike indicator
        spike = sentiment
    
    return min(spike, 1.0)


def calculate_topical_divergence(text: str, baseline: str = "") -> float:
    """
    Calculate topical divergence using named entities and noun chunks.
    Returns a score from 0-1 where higher means more divergence from factual reporting.
    """
    if not nlp:
        return 0.0
    
    doc = nlp(text)
    
    # Count ratio of adjectives and adverbs to total tokens (hyperbole indicator)
    total_tokens = len([token for token in doc if not token.is_punct and not token.is_space])
    if total_tokens == 0:
        return 0.0
    
    hyperbolic_tokens = len([token for token in doc if token.pos_ in ["ADJ", "ADV"]])
    hyperbole_ratio = hyperbolic_tokens / total_tokens
    
    # Count entities (factual content indicator)
    entity_count = len(doc.ents)
    entity_ratio = min(entity_count / max(total_tokens / 10, 1), 1.0)
    
    # Divergence: high hyperbole ratio and low entity ratio = high divergence
    divergence = (hyperbole_ratio * 0.7) + ((1 - entity_ratio) * 0.3)
    
    return min(divergence, 1.0)


def de_painter(text: str) -> tuple[str, List[str]]:
    """
    Strip adjectives and intensifiers from text to create a "sober" version.
    Returns: (de_painted_text, list_of_removed_adjectives)
    """
    if not nlp:
        return text, []
    
    doc = nlp(text)
    removed_adjectives = []
    tokens_to_keep = []
    
    for token in doc:
        # Remove adjectives and adverbs (intensifiers)
        if token.pos_ in ["ADJ", "ADV"]:
            removed_adjectives.append(token.text)
        else:
            tokens_to_keep.append(token.text_with_ws)
    
    de_painted_text = "".join(tokens_to_keep)
    
    # Clean up extra spaces
    de_painted_text = re.sub(r'\s+', ' ', de_painted_text).strip()
    
    return de_painted_text, removed_adjectives


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "DAM Cognitive Firewall API",
        "version": "1.0.0",
        "status": "operational",
        "nlp_model_loaded": nlp is not None
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if nlp is None:
        raise HTTPException(
            status_code=503,
            detail="NLP model not loaded. Run: python -m spacy download en_core_web_sm"
        )
    return {"status": "healthy", "nlp_model": "en_core_web_sm"}


@app.post("/api/analyze", response_model=TextAnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """
    Analyze text and calculate Distraction Score
    
    The Distraction Score combines:
    - Sentiment spikes (extreme emotional language)
    - Topical divergence (ratio of hyperbole to factual content)
    """
    if not nlp:
        raise HTTPException(
            status_code=503,
            detail="NLP model not loaded. Run: python -m spacy download en_core_web_sm"
        )
    
    text = request.text
    baseline = request.baseline_text
    
    # Calculate components
    blob = TextBlob(text)
    sentiment_polarity = blob.sentiment.polarity
    sentiment_subjectivity = blob.sentiment.subjectivity
    
    sentiment_spike = calculate_sentiment_spike(text, baseline)
    topical_divergence = calculate_topical_divergence(text, baseline)
    
    # Distraction Score: weighted combination
    # Higher score = more distracting/hyperbolic content
    distraction_score = (sentiment_spike * 0.4) + (topical_divergence * 0.6)
    
    # De-paint the text
    de_painted_text, adjectives = de_painter(text)
    
    return TextAnalysisResponse(
        distraction_score=round(distraction_score, 3),
        sentiment_polarity=round(sentiment_polarity, 3),
        sentiment_subjectivity=round(sentiment_subjectivity, 3),
        adjective_count=len(adjectives),
        topical_divergence=round(topical_divergence, 3),
        original_text=text,
        de_painted_text=de_painted_text
    )


@app.post("/api/depaint", response_model=DePaintResponse)
async def depaint_text(request: DePaintRequest):
    """
    Strip adjectives and intensifiers from text (De-Painter function)
    """
    if not nlp:
        raise HTTPException(
            status_code=503,
            detail="NLP model not loaded. Run: python -m spacy download en_core_web_sm"
        )
    
    de_painted_text, removed_adjectives = de_painter(request.text)
    
    return DePaintResponse(
        original_text=request.text,
        de_painted_text=de_painted_text,
        removed_adjectives=removed_adjectives
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
