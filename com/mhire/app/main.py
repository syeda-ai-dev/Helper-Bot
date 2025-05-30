import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from com.mhire.app.services.helper_bot.helper_bot_router import router as chat_router
from com.mhire.app.config.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="FixConnect",
    description="A helper bot API for guiding users through the system",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(chat_router)

# Health check endpoint
@app.get("/health", response_class=JSONResponse)
async def health_check(request: Request):
    """Health check endpoint"""
    try:
        # Initialize config to check configuration
        config = Config()
        
        return {
            "status": "healthy",
            "message": "App is up and running",
            "path": request.url.path
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise

# Root endpoint
@app.get("/", response_class=JSONResponse)
async def root(request: Request):
    """Root endpoint"""
    return {
        "name": "FixConnect",
        "version": "1.0.0",
        "description": "AI-powered Helper-bot",
        "path": request.url.path
    }
