import os
import time
import contextvars
import functools
import google.generativeai as genai
from google.generativeai.types import content_types

from mcp_server.tools.flight_time import calculate_flight_time
from mcp_server.tools.roi_calc import calculate_roi
from mcp_server.tools.compliance_checker import check_compliance
from mcp_server.tools.drone_selector import select_drone
from mcp_server.rag_bridge import query_pinecone, format_citations

# Ensure Gemini is configured
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def retrieve_knowledge_base(query: str, top_k: int = 5) -> dict:
    """
    Searches the Pinecone Drone Intelligence vector database for relevant documentation.
    Use this tool whenever the user asks a general knowledge question about drones, rules, markets, or operations.
    Returns paragraphs of context to help form an answer.
    """
    chunks = query_pinecone(query, top_k=top_k)
    return {
        "context": [c["text"] for c in chunks],
        "citations": format_citations(chunks)
    }

async def execute_agent(message: str, conversation_history: list = None) -> dict:
    """
    The main agent loop capable of executing functions returning the response.
    """
    start_time = time.time()
    local_citations = []
    
    def _wrap_tool(tool_func):
        @functools.wraps(tool_func)
        def wrapper(*args, **kwargs):
            res = tool_func(*args, **kwargs)
            if isinstance(res, dict) and "citations" in res:
                local_citations.extend(res["citations"])
            return res
        return wrapper

    local_mcp_tools = [
        _wrap_tool(calculate_flight_time),
        _wrap_tool(calculate_roi),
        _wrap_tool(check_compliance),
        _wrap_tool(select_drone),
        _wrap_tool(retrieve_knowledge_base)
    ]
    
    system_instruction = (
        "You are the central Drone Intelligence routing agent. Your job is to answer user queries accurately. "
        "Answer in under 100 words clearly and concisely. "
        "You CAN make use of your tools to gather facts or calculate answers when you need concrete data. "
        "DO NOT use tools for casual greetings or if you don't need them. "
        "If you are asked a factual question, YOU MUST ONLY use the data returned by your tools to answer. Do not use your internal general knowledge. "
        "If the tools do not contain the answer, state that you do not know based on the provided intelligence. "
        "When parsing user input into tool arguments, rigorously ensure the types and formats match exactly what the tool requires. "
        "For example, convert string numbers ('30kg') to raw float values (30.0). "
        "If multiple tools are needed, you may execute them iteratively. "
        "Once you have gathered the data from the tools, synthesize it into a clean, markdown-formatted response."
    )

    local_agent_model = genai.GenerativeModel(
        model_name="models/gemini-2.5-flash",
        tools=local_mcp_tools,
        system_instruction=system_instruction
    )

    chat = local_agent_model.start_chat(
        enable_automatic_function_calling=True,
        history=conversation_history
    )
    
    response = await chat.send_message_async(message)
    
    citations = list(set(local_citations))
    tool_used = "llm"
    
    for part in chat.history:
        if part.role == "model" and part.parts:
            for p in part.parts:
                if getattr(p, "function_call", None):
                    tool_used = p.function_call.name

    processing_time_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "answer": response.text,
        "citations": citations,
        "tool_used": tool_used,
        "processing_time_ms": processing_time_ms
    }
