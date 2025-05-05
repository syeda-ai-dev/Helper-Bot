from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from mhire.com.config.config import get_settings
from mhire.com.app.services.helper_bot.helper_bot_router import router as chat_router

settings = get_settings()
logger = settings.get_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="A helper bot API for guiding users through the system",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include chat router
app.include_router(chat_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
