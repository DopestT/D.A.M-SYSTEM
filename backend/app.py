"""
FastAPI backend for D.A.M-SYSTEM (Cognitive Firewall)
Provides API endpoints for analyzing text and calculating distraction scores.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from brain import calculate_distraction_score

app = FastAPI(
    title="D.A.M-SYSTEM API",
    description="Cognitive Firewall API for analyzing and neutralizing media distractions",
    version="0.1.0"
)

# Configure CORS for browser extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TextAnalysisRequest(BaseModel):
    """Request model for text analysis"""
    text: str
    url: Optional[str] = None


class TextAnalysisResponse(BaseModel):
    """Response model for text analysis"""
    distraction_score: float
    sentiment: float
    subjectivity: float
    analysis: str


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "D.A.M-SYSTEM API",
        "version": "0.1.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/analyze", response_model=TextAnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """
    Analyze text and calculate distraction score
    
    Args:
        request: TextAnalysisRequest containing text to analyze
        
    Returns:
        TextAnalysisResponse with distraction score and analysis
    """
    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        result = calculate_distraction_score(request.text)
        
        # Determine analysis message based on score
        if result["distraction_score"] >= 0.7:
            analysis = "High distraction content detected. Consider skipping."
        elif result["distraction_score"] >= 0.4:
            analysis = "Moderate distraction level. Read critically."
        else:
            analysis = "Low distraction content. Appears informative."
        
        return TextAnalysisResponse(
            distraction_score=result["distraction_score"],
            sentiment=result["sentiment"],
            subjectivity=result["subjectivity"],
            analysis=analysis
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
