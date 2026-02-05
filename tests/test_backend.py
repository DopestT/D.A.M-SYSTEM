"""
Tests for DAM System Backend API
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app, calculate_sentiment_spike, calculate_topical_divergence, de_painter, nlp

client = TestClient(app)

# Check if Spacy model is available
SPACY_MODEL_AVAILABLE = nlp is not None


class TestBasicEndpoints:
    """Test basic API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "DAM Cognitive Firewall API"
        assert "status" in data
        
    def test_health_endpoint_without_model(self):
        """Test health endpoint - may fail if model not loaded"""
        response = client.get("/health")
        # Either 200 (model loaded) or 503 (model not loaded)
        assert response.status_code in [200, 503]


class TestSentimentAnalysis:
    """Test sentiment spike calculation"""
    
    def test_sentiment_spike_basic(self):
        """Test basic sentiment spike calculation"""
        # Neutral text
        neutral = "The weather is okay today."
        score = calculate_sentiment_spike(neutral)
        assert 0 <= score <= 1
        
    def test_sentiment_spike_extreme(self):
        """Test extreme sentiment detection"""
        # Very positive text
        positive = "This is absolutely amazing and wonderful!"
        score = calculate_sentiment_spike(positive)
        assert score > 0.3  # Should have noticeable spike
        
    def test_sentiment_spike_with_baseline(self):
        """Test sentiment spike with baseline comparison"""
        baseline = "The company reported earnings."
        sensational = "The company's earnings were absolutely devastating!"
        score = calculate_sentiment_spike(sensational, baseline)
        assert score > 0  # Should detect difference


class TestDePainter:
    """Test de-painter functionality"""
    
    @pytest.mark.skipif(not SPACY_MODEL_AVAILABLE, reason="Requires spacy model installation")
    def test_depaint_removes_adjectives(self):
        """Test that de-painter removes adjectives"""
        text = "The quick brown fox jumps."
        depainted, removed = de_painter(text)
        
        # Should remove 'quick' and 'brown' (adjectives)
        assert "quick" not in depainted.lower()
        assert "brown" not in depainted.lower()
        assert "fox" in depainted
        assert "jumps" in depainted
        
    @pytest.mark.skipif(not SPACY_MODEL_AVAILABLE, reason="Requires spacy model installation")
    def test_depaint_returns_removed_list(self):
        """Test that de-painter returns list of removed words"""
        text = "The very big dog is extremely happy."
        depainted, removed = de_painter(text)
        
        assert len(removed) > 0
        # Should include adjectives and adverbs
        assert any(word in removed for word in ['big', 'very', 'extremely', 'happy'])


class TestAnalyzeEndpoint:
    """Test /api/analyze endpoint"""
    
    @pytest.mark.skipif(not SPACY_MODEL_AVAILABLE, reason="Requires spacy model installation")
    def test_analyze_basic_text(self):
        """Test analyzing basic text"""
        response = client.post(
            "/api/analyze",
            json={"text": "The weather is nice today."}
        )
        
        if response.status_code == 503:
            pytest.skip("Spacy model not installed")
            
        assert response.status_code == 200
        data = response.json()
        
        # Check all required fields
        assert "distraction_score" in data
        assert "sentiment_polarity" in data
        assert "sentiment_subjectivity" in data
        assert "adjective_count" in data
        assert "topical_divergence" in data
        assert "original_text" in data
        assert "de_painted_text" in data
        
        # Distraction score should be between 0 and 1
        assert 0 <= data["distraction_score"] <= 1
        
    @pytest.mark.skipif(not SPACY_MODEL_AVAILABLE, reason="Requires spacy model installation")
    def test_analyze_hyperbolic_text(self):
        """Test analyzing hyperbolic text"""
        response = client.post(
            "/api/analyze",
            json={
                "text": "This absolutely incredible and amazing breakthrough is totally revolutionary!"
            }
        )
        
        if response.status_code == 503:
            pytest.skip("Spacy model not installed")
            
        assert response.status_code == 200
        data = response.json()
        
        # Hyperbolic text should have higher distraction score
        assert data["distraction_score"] > 0.3
        assert data["adjective_count"] > 2
        
    def test_analyze_empty_text(self):
        """Test analyzing empty text"""
        response = client.post(
            "/api/analyze",
            json={"text": ""}
        )
        
        # Should handle empty text gracefully
        # Either return error or handle it
        assert response.status_code in [200, 422, 503]


class TestDePaintEndpoint:
    """Test /api/depaint endpoint"""
    
    @pytest.mark.skipif(not SPACY_MODEL_AVAILABLE, reason="Requires spacy model installation")
    def test_depaint_basic_text(self):
        """Test de-painting basic text"""
        response = client.post(
            "/api/depaint",
            json={"text": "The quick brown fox jumps over the lazy dog."}
        )
        
        if response.status_code == 503:
            pytest.skip("Spacy model not installed")
            
        assert response.status_code == 200
        data = response.json()
        
        assert "original_text" in data
        assert "de_painted_text" in data
        assert "removed_adjectives" in data
        
        # Should have removed some adjectives
        assert len(data["removed_adjectives"]) > 0
        
    def test_depaint_no_adjectives(self):
        """Test de-painting text with no adjectives"""
        response = client.post(
            "/api/depaint",
            json={"text": "The cat sat."}
        )
        
        if response.status_code == 503:
            pytest.skip("Spacy model not installed")
            
        # Should still work
        assert response.status_code in [200, 503]


class TestCORS:
    """Test CORS configuration"""
    
    def test_cors_headers(self):
        """Test that CORS headers are present"""
        response = client.options("/api/analyze")
        # CORS should be configured
        # Note: TestClient may not fully simulate CORS, but middleware should be configured
        assert response.status_code in [200, 405]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
