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

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.get("/api/sample-resume", summary="Get sample resume text")
async def get_sample_resume():
    """
    Get the text of the sample resume.
    """
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, "sample_resume.txt")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="sample_resume.txt not found in workspace root.")
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"filename": "sample_resume.txt", "text": content}
    except Exception as e:
        logger.error(f"Failed to read sample resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


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

from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

# Serve compiled React frontend
dist_dir = "frontend/dist"
assets_dir = os.path.join(dist_dir, "assets")
index_path = os.path.join(dist_dir, "index.html")

# Ensure the assets directory exists so Starlette doesn't crash on startup
os.makedirs(assets_dir, exist_ok=True)

app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

@app.get("/")
async def serve_index():
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse(
        content="""
        <html>
            <head><title>System Setup</title></head>
            <body style="font-family: sans-serif; padding: 2rem; background: #08090f; color: #ffffff; text-align: center;">
                <h1 style="color: #00f2fe; margin-top: 5rem;">Frontend Not Built Yet</h1>
                <p style="color: #8b949e; font-size: 1.1rem;">The backend is running, but the frontend React application has not been compiled.</p>
                <p style="color: #8b949e;">Please make sure the <code>frontend/dist/</code> directory is committed to Git and pushed, or run <code>npm run build</code> in the frontend folder.</p>
            </body>
        </html>
        """,
        status_code=503
    )

@app.get("/{catchall:path}")
async def catch_all(catchall: str):
    if catchall.startswith("api"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=503, detail="Frontend build files missing")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
