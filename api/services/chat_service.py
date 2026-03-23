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
            title_model = genai.GenerativeModel("models/gemini-3-flash-preview")
            title_resp = await title_model.generate_content_async(title_prompt)
            title = title_resp.text.strip().replace('"', '')
        except Exception:
            # Fallback title
            title = message[:30] + "..."
            
        create_chat(chat_id=conversation_id, title=title)

    # Get conversation history from SQLite for State Memory using 'model'/'user' mapping
    try:
        history = get_recent_history(conversation_id, limit=16) # Store 8 turns
    except Exception:
        history = []

    try:
        agent_result = await execute_agent(message, conversation_history=history)
        answer = agent_result["answer"]
        citations = agent_result["citations"]
        tool_used_raw = agent_result.get("tool_used") or "no_tool"
        
        # Human-readable mapping for analytics
        tool_mapping = {
            "retrieve_knowledge_base": "RAG (Knowledge Base)",
            "calculate_flight_time": "Flight Time Calculator",
            "calculate_roi": "ROI Calculator",
            "check_compliance": "Compliance Checker",
            "select_drone": "Drone Recommender",
            "ingest_tool": "Document Ingestion",
            "no_tool": "Direct Chat (No Tool)",
            "system_api": "System Action"
        }
        tool_used = tool_mapping.get(tool_used_raw, tool_used_raw)
        
        model_used = agent_result.get("model_used", "gemini-3-flash-preview")
        processing_time_ms = agent_result["processing_time_ms"]
        

            
        import json
        source_data = json.dumps({
            "tool": tool_used,
            "citations": citations
        })
            
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
            model_used="gemini-3-flash-preview",
            source=source_data
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
        "model_used": model_used if 'model_used' in locals() else "none",
        "processing_time_ms": processing_time_ms
    }
