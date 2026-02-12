from fastapi import FastAPI
from utils.logger import get_logger
from utils.config import get_config_val

# Initialize logger
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=get_config_val("app.name", "AgenticResumeTester"),
    version=get_config_val("app.version", "0.1.0")
)

from fastapi import UploadFile, File, HTTPException, Body
from pydantic import BaseModel, Field
import shutil
import os
from parsers.resume_parser import extract_text
from models.data_models import CandidateProfile
from agents.orchestrator import run_interview_pipeline

# --- Request Models ---
class AnalyzeRequest(BaseModel):
    resume_text: str = Field(..., description="Extracted text from the resume")
    job_description: str = Field("", description="Optional job description")
    candidate_profile: CandidateProfile = Field(..., description="Candidate's self-declared profile")

# --- Response Models (Optional, for better Docs) ---


@app.get("/api/health")
async def health_check():
    
    logger.info("Health check endpoint called")
    return {
        "status": "healthy",
        "app_name": get_config_val("app.name"),
        "version": get_config_val("app.version")
    }

@app.post("/api/extract_text", summary="Step 1: Upload & Extract Resume Text")
async def extract_resume_text(file: UploadFile = File(...)):
    """
    Upload a resume (PDF/TXT) and get the extracted text.
    """
    try:
        temp_filename = f"temp_{file.filename}"
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        text = extract_text(temp_filename)
        
        # Cleanup
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            
        return {"filename": file.filename, "text": text}
        
    except Exception as e:
        logger.error(f"Extraction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze", summary="Step 2: Analyze Resume & Generate Content")
async def analyze_resume(request: AnalyzeRequest):
    """
    Run the full Multi-Agent Interview Pipeline.
    Requires 'resume_text' from Step 1.
    """
    try:
        result = run_interview_pipeline(
            resume_text=request.resume_text,
            candidate_profile=request.candidate_profile,
            job_description=request.job_description
        )
        return result
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
