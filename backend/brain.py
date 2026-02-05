"""
NLP Logic for D.A.M-SYSTEM
Calculates distraction scores based on sentiment and subjectivity analysis.
"""
from textblob import TextBlob
from typing import Dict, Any


def calculate_distraction_score(text: str) -> Dict[str, float]:
    """
    Calculate a Distraction Score based on sentiment and subjectivity.
    
    The Distraction Score is designed to identify content that may be 
    intentionally distracting or emotionally manipulative. It combines:
    - Sentiment polarity (extreme positive or negative sentiment)
    - Subjectivity (highly subjective vs objective content)
    
    Args:
        text: The text content to analyze
        
    Returns:
        Dict containing:
            - distraction_score: Float between 0-1 (higher = more distracting)
            - sentiment: Float between -1 to 1 (negative to positive)
            - subjectivity: Float between 0 to 1 (objective to subjective)
            
    Algorithm:
        - High subjectivity increases distraction score
        - Extreme sentiment (very positive or very negative) increases score
        - Combines both factors with weights to produce final score
    """
    # Analyze text using TextBlob
    blob = TextBlob(text)
    
    # Get sentiment polarity (-1 to 1) and subjectivity (0 to 1)
    sentiment = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    
    # Calculate sentiment extremity (how far from neutral)
    # Maps [-1, 1] to [0, 1] where 0 is neutral and 1 is extreme
    sentiment_extremity = abs(sentiment)
    
    # Calculate distraction score
    # Weights: 60% subjectivity (subjective content is more distracting)
    #          40% sentiment extremity (extreme emotions are distracting)
    distraction_score = (0.6 * subjectivity) + (0.4 * sentiment_extremity)
    
    # Ensure score is between 0 and 1
    distraction_score = max(0.0, min(1.0, distraction_score))
    
    return {
        "distraction_score": round(distraction_score, 3),
        "sentiment": round(sentiment, 3),
        "subjectivity": round(subjectivity, 3)
    }


def analyze_hyperbole(text: str) -> Dict[str, Any]:
    """
    Identify potential hyperbolic language in text.
    
    This is a placeholder for future enhancement to detect and strip
    rhetorical "paint" (hyperbole) from content.
    
    Args:
        text: The text content to analyze
        
    Returns:
        Dict containing hyperbole analysis
    """
    # TODO: Implement hyperbole detection
    # Could use patterns like:
    # - Excessive superlatives (best, worst, most, least)
    # - Absolute terms (always, never, everyone, nobody)
    # - Intensifiers (very, extremely, incredibly)
    
    return {
        "hyperbole_detected": False,
        "hyperbolic_phrases": []
    }


def extract_primary_sources(text: str) -> Dict[str, Any]:
    """
    Extract and identify primary sources from text.
    
    This is a placeholder for future enhancement to surface
    primary sources referenced in content.
    
    Args:
        text: The text content to analyze
        
    Returns:
        Dict containing primary source information
    """
    # TODO: Implement primary source extraction
    # Could look for:
    # - Citations and references
    # - URLs to official sources
    # - Quotes with attribution
    
    return {
        "primary_sources": [],
        "has_sources": False
    }
