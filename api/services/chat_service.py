"""
Chat Service — routes natural language queries to the newly upgraded Gemini Agent.
Returns response in the format the frontend expects: {answer, sources}.
"""
import time
import uuid

from api.services.agent import execute_agent


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
    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    try:
        agent_result = await execute_agent(message)
        answer = agent_result["answer"]
        citations = agent_result["citations"]
        tool_used = agent_result["tool_used"]
        processing_time_ms = agent_result["processing_time_ms"]
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
        "processing_time_ms": processing_time_ms,
        "success": True,
    }
