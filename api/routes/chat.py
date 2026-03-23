"""
Chat route — POST /api/chat/
Frontend calls: POST http://localhost:8000/api/chat/ with {message}
Frontend reads:  data.answer, data.sources [{title, link, snippet}]
"""
import time
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
        analytics.track("/chat", request.message, result.get("processing_time_ms", 0), 
                        tool_used=result.get("tool_used"), model_used=result.get("model_used"))
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
    start = time.time()
    from api.services.db_service import get_all_chats
    res = get_all_chats()
    ms = round((time.time() - start) * 1000, 2)
    analytics.track("/chats", "list_chats", ms, tool_used="System Action", model_used="none")
    return {"chats": res}

@router.get("/chats/{chat_id}")
async def get_chat(chat_id: str):
    """Returns the full conversation payload for a specific chat ID."""
    start = time.time()
    from api.services.db_service import get_chat_history_full
    messages = get_chat_history_full(chat_id)
    # mapped gracefully
    formatted_messages = []
    
    import json
    from api.services.chat_service import _citations_to_sources
    
    for msg in messages:
        cit_array = []
        try:
            raw_source = msg.get("source", "{}")
            source_data = json.loads(raw_source)
            if isinstance(source_data, dict) and "citations" in source_data:
                cit_array = source_data["citations"]
        except Exception:
            pass
            
        formatted_messages.append({
            "role": "assistant" if msg["role"] == "model" else msg["role"],
            "content": msg["content"],
            "sources": _citations_to_sources(cit_array) if cit_array else []
        })
    ms = round((time.time() - start) * 1000, 2)
    analytics.track(f"/chats/{chat_id}", f"get_chat {chat_id}", ms, tool_used="System Action", model_used="none")
    return {"chat_id": chat_id, "messages": formatted_messages}
