import time
import uuid
import logging
import google.generativeai as genai
from api.services.agent import execute_agent
from api.services.db_service import get_recent_history, create_chat, add_message

logger = logging.getLogger(__name__)

def _citations_to_sources(citations: list[str]) -> list[dict]:
    """Convert citation strings to the {title, link, snippet} format the frontend expects."""
    sources = []
    for c in citations:
        sources.append({
            "title": c.split("(")[0].strip() if "(" in c else c,
            "link": "#",
            "snippet": c,
        })
    return sources

async def handle_chat(message: str, conversation_id: str = None) -> dict:
    is_new_chat = False
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
        is_new_chat = True

    if is_new_chat:
        try:
            # Auto-generate succinct title via LLM
            title_prompt = f"Summarize this user query into a concise 3-5 word title. Do not wrap in quotes or explain. Query: {message}"
            title_model = genai.GenerativeModel("models/gemini-2.5-flash")
            title_resp = await title_model.generate_content_async(title_prompt)
            title = title_resp.text.strip().replace('"', '')
        except Exception:
            # Fallback title
            title = message[:30] + "..."
            
        create_chat(chat_id=conversation_id, title=title)

    # Get conversation history from SQLite for State Memory using 'model'/'user' mapping
    try:
        history = get_recent_history(conversation_id, limit=6) # Store 3 turns
    except Exception:
        history = []

    try:
        agent_result = await execute_agent(message, conversation_history=history)
        answer = agent_result["answer"]
        citations = agent_result["citations"]
        tool_used = agent_result["tool_used"]
        processing_time_ms = agent_result["processing_time_ms"]
        
        # Word Limit Safeguard (< 100 words)
        words = answer.split()
        if len(words) >= 100:
            answer = " ".join(words[:99]) + "..."
            
        # Store securely to persistent memory DB
        # User message
        add_message(
            message_id=str(uuid.uuid4()),
            chat_id=conversation_id,
            role="user",
            content=message,
            model_used="user",
            source="user"
        )
        
        # Assistant message
        add_message(
            message_id=str(uuid.uuid4()),
            chat_id=conversation_id,
            role="model",  # the generative AI expected role
            content=answer,
            model_used="gemini-2.5-flash",
            source=tool_used
        )
        
    except Exception as e:
        answer = f"An error occurred while processing your query with the AI Agent: {str(e)}"
        citations = []
        tool_used = "error"
        processing_time_ms = 0

    return {
        "answer": answer,
        "sources": _citations_to_sources(citations),
        "conversation_id": conversation_id,
        "tool_used": tool_used,
        "processing_time_ms": processing_time_ms
    }
