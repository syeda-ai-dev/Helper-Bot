from fastapi import APIRouter, Depends
from typing import Optional
import logging

from mhire.com.app.services.helper_bot.helper_bot import HelperBot
from mhire.com.app.services.helper_bot.helper_bot_schema import ChatRequest, ChatResponse
from mhire.com.config.config import get_settings

settings = get_settings()
logger = settings.get_logger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

async def get_helper_bot():
    settings = get_settings()
    bot = HelperBot(
        openai_api_key=settings.OPENAI_API_KEY,
        openai_endpoint=settings.OPENAI_ENDPOINT,
        model=settings.MODEL
    )
    await bot.load_site_map()
    return bot

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, bot: HelperBot = Depends(get_helper_bot)):
    """
    Chat endpoint for interacting with the helper bot.
    """
    try:
        response = await bot.generate_response(request.message)
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return ChatResponse(
            message="I encountered an error while processing your request. Please try again.",
            navigation_path=None
        )