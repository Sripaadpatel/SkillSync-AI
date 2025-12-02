import os
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import uvicorn

# Import the singleton engine instance
from recsys_engine import engine

app = FastAPI(title="SkillSync AI Recommendation Engine", version="1.0")

# --- Response Models (Strict Schema for Swagger UI) ---
class AIAnalysis(BaseModel):
    match_score: Union[str, int, float]
    matching_skills: List[str]
    missing_skills: List[str]
    advice: str

class RecommendResponse(BaseModel):
    user_id: Union[str, int, float]
    filters_applied: Dict[str, Any]  # Shows what "Cold Start" filters were used
    top_recommendation: Dict[str, Any]
    ai_analysis: AIAnalysis
    other_matches: List[Dict[str, Any]]

# --- Endpoints ---

@app.get("/")
def health_check():
    return {"status": "running", "engine": "SkillSync AI v1.0"}

@app.post("/recommend", response_model=RecommendResponse)
async def recommend_jobs(file: UploadFile = File(...)):
    """
    Main Endpoint:
    1. Parses Resume (PDF)
    2. Extracts Metadata & Filters (Single-Pass LLM)
    3. Performs Hybrid Vector Search
    4. Generates AI Gap Analysis
    """
    # 1. Validate File Type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF allowed.")
    
    # 2. Save File Temporarily
    temp_filename = f"temp_{uuid.uuid4()}.pdf"
    try:
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # ---------------------------------------------------------
        # STEP 1: Single-Pass Extraction (ETL)
        # ---------------------------------------------------------
        # This calls the LLM once to get Email, Filters, and Summary
        processed_data = engine.process_resume(temp_filename)
        
        user_email = processed_data.get("user_email", "Unknown User")
        filters = processed_data.get("filters", {})
        query_text = processed_data.get("summary", "") # Use refined summary for better search

        # ---------------------------------------------------------
        # STEP 2: Hybrid Search (Vector + Metadata)
        # ---------------------------------------------------------
        # First, try strict search (e.g., "New York" + "Full-time")
        #TODO: change the filter parameter name back to filters
        matches = engine.recommend_jobs(query_text, k=3, filters=None)
        
        # Fallback: If strict search fails, relax the filters
        if not matches and filters:
            print(f"⚠️ No matches found with filters {filters}. Retrying with broad search...")
            matches = engine.recommend_jobs(query_text, k=3, filters=None)
            # Mark filters as empty in response to indicate broad search was used
            filters = {} 

        # Handle Case: Still no jobs found
        if not matches:
            return {
                "user_id": user_email,
                "filters_applied": filters,
                "top_recommendation": {},
                "ai_analysis": {
                    "match_score": "0%", 
                    "matching_skills": [], 
                    "missing_skills": [], 
                    "advice": "No relevant jobs found in the database. Try adding more jobs via indexer.py."
                },
                "other_matches": []
            }

        # ---------------------------------------------------------
        # STEP 3: AI Gap Analysis (Reasoning Agent)
        # ---------------------------------------------------------
        top_match = matches[0]
        # We analyze only the #1 result to keep latency low (~5-10s)
        gap_analysis = engine.analyse_gap(query_text, top_match.get('description', ''))

        # ---------------------------------------------------------
        # STEP 4: Final Response
        # ---------------------------------------------------------
        return {
            "user_id": user_email,
            "filters_applied": filters,
            "top_recommendation": top_match,
            "ai_analysis": gap_analysis,
            "other_matches": matches[1:]
        }

    except Exception as e:
        print(f"❌ Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup: Remove temp file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

if __name__ == "__main__":
    # Run server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)