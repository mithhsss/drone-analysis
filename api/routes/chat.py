"""
Chat route — POST /api/chat/
Frontend calls: POST http://localhost:8000/api/chat/ with {message}
Frontend reads:  data.answer, data.sources [{title, link, snippet}]
"""
import logging
from fastapi import APIRouter
from api.models.requests import ChatRequest
from api.models.responses import ChatResponse
from api.services.chat_service import handle_chat
from api.services.analytics_service import analytics

router = APIRouter()
logger = logging.getLogger("api.chat")


@router.post("/chat/", response_model=ChatResponse)
@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = await handle_chat(
            message=request.message,
            conversation_id=request.conversation_id,
        )
        analytics.track("/chat", request.message, result.get("processing_time_ms", 0))
        return result
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return ChatResponse(
            answer="An error occurred while processing your request. Please try again.",
            sources=[],
            success=False,
        )
