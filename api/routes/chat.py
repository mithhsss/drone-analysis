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

@router.get("/chats")
async def list_chats():
    """Returns a list of all chats for the frontend sidebar."""
    from api.services.db_service import get_all_chats
    return {"chats": get_all_chats()}

@router.get("/chats/{chat_id}")
async def get_chat(chat_id: str):
    """Returns the full conversation payload for a specific chat ID."""
    from api.services.db_service import get_chat_history_full
    messages = get_chat_history_full(chat_id)
    
    # Map back to the UI interface format if strictly required, but usually 
    # {role, content} is the perfect structure.
    # The frontend is expecting "user" and "assistant" roles typically, while genai uses `model`. We'll format it gracefully:
    formatted_messages = []
    for msg in messages:
        formatted_messages.append({
            "role": "assistant" if msg["role"] == "model" else msg["role"],
            "content": msg["content"]
        })
    return {"chat_id": chat_id, "messages": formatted_messages}
