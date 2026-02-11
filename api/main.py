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

@app.get("/api/health")
async def health_check():
    
    logger.info("Health check endpoint called")
    return {
        "status": "healthy",
        "app_name": get_config_val("app.name"),
        "version": get_config_val("app.version")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
