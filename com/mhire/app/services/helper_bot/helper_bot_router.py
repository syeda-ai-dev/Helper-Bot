from fastapi import APIRouter, Depends
import logging

from mhire.com.app.services.helper_bot.helper_bot import HelperBot
from mhire.com.app.services.helper_bot.helper_bot_schema import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

@router.post()
async def chat():
    """
    Chat endpoint for interacting with the helper bot.
    """
    try:
        response = await bot.generate_response(request.message)
        return response
        
    except Exception as e:
        #a fallback response if something goes wrong
        #return response from network response file
        pass