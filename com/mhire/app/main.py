import time, logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from com.mhire.app.common.network_responses import (NetworkResponse, HTTPCode)
from mhire.com.app.services.helper_bot.helper_bot_router import router as chat_router

# Configure logging with proper format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

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

# Health check endpoint
@app.get("/health", response_class=JSONResponse)
async def health_check(http_request: Request):
    """Health check endpoint"""
    start_time = time.time()
    return NetworkResponse().success_response(
        http_code=HTTPCode.SUCCESS,
        message="Health check successful",
        data={
            "status": "healthy",
            "message": "App is up and running."
        },
        resource=http_request.url.path,
        start_time=start_time
    )

# Root endpoint
@app.get("/", response_class=JSONResponse)
async def root(http_request: Request):
    """Root endpoint"""
    start_time = time.time()
    return NetworkResponse().success_response(
        http_code=HTTPCode.SUCCESS,
        message="Root endpoint data",
        data={
            "name": "FixConnect",
            "version": "1.0.0",
            "description": "AI-powered Helper-bot"
        },
        resource=http_request.url.path,
        start_time=start_time
    )
