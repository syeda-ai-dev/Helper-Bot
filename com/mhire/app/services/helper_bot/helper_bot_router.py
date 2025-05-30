import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from com.mhire.app.services.helper_bot.helper_bot import HelperBot
from com.mhire.app.services.helper_bot.helper_bot_schema import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["chat"]
)

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request):
    """Chat endpoint for interacting with the helper bot"""
    try:
        # Log incoming request
        logger.info(
            f"Chat request - User Type: {request.user_type}, "
            f"Message Length: {len(request.message)}, "
            f"Client IP: {http_request.client.host}"
        )
        
        # Initialize helper bot
        bot = HelperBot()
        
        # Process chat request
        response = await bot.get_response(
            query=request.message,
            user_type=request.user_type
        )
        
        # Log successful response
        logger.info(
            f"Chat response - Source: {response.source}, "
            f"Confidence: {response.confidence_score}"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in chat request: {str(e)}")
        raise