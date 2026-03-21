"""
Chat Service — routes natural language queries to the right MCP tool or RAG.
Returns response in the format the frontend expects: {answer, sources}.
"""
import re
import time
import uuid

from mcp_server.tools.flight_time import calculate_flight_time
from mcp_server.tools.roi_calc import calculate_roi
from mcp_server.tools.compliance_checker import check_compliance
from mcp_server.tools.drone_selector import select_drone


def detect_intent(message: str) -> str:
    msg = message.lower()
    if any(w in msg for w in ["flight time", "battery", "how long", "fly", "range"]):
        return "flight_time"
    if any(w in msg for w in ["roi", "profit", "invest", "break-even", "breakeven",
                               "return", "revenue", "cost", "payback"]):
        return "roi"
    if any(w in msg for w in ["legal", "comply", "compliance", "permit", "licence",
                               "license", "dgca", "allowed", "register", "rule"]):
        return "compliance"
    if any(w in msg for w in ["recommend", "which drone", "best drone", "suggest",
                               "buy", "select", "compare"]):
        return "drone_selector"
    return "rag"


def extract_numbers(message: str) -> list[float]:
    numbers = re.findall(r'[\d,]+\.?\d*', message.replace(',', ''))
    return [float(n) for n in numbers if n]


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
    start = time.time()
    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    intent = detect_intent(message)
    citations = []
    answer = ""

    try:
        if intent == "flight_time":
            nums = extract_numbers(message)
            result = calculate_flight_time(
                battery_mah=nums[0] if len(nums) > 0 else 17500,
                drone_weight_kg=nums[1] if len(nums) > 1 else 5.0,
                payload_kg=nums[2] if len(nums) > 2 else 0.0,
            )
            citations = result.get("citations", [])
            answer = (
                f"Estimated flight time: {result['estimated_flight_time_minutes']} minutes. "
                f"Safe operating time: {result['safe_flight_time_minutes']} minutes. "
                f"Range: {result['range_estimate_km']} km."
            )
            if result.get("warnings"):
                answer += f" Warnings: {', '.join(result['warnings'])}"

        elif intent == "roi":
            nums = extract_numbers(message)
            result = calculate_roi(
                use_case=message[:50],
                drone_cost_inr=nums[0] if len(nums) > 0 else 500000,
                monthly_operational_cost_inr=nums[1] if len(nums) > 1 else 25000,
                monthly_revenue_inr=nums[2] if len(nums) > 2 else 80000,
            )
            citations = result.get("citations", [])
            answer = (
                f"ROI Analysis: {result['verdict']}. "
                f"Break-even in {result['breakeven_months']} months. "
                f"Year 1 ROI: {result['roi_12_months_percent']}%. "
                f"Year 3 ROI: {result['roi_36_months_percent']}%."
            )

        elif intent == "compliance":
            nums = extract_numbers(message)
            result = check_compliance(
                drone_weight_kg=nums[0] if nums else 5.0,
                use_type="commercial" if "commercial" in message.lower() else "recreational",
                location=message,
                has_remote_pilot_licence="have licence" in message.lower()
                                         or "have rpl" in message.lower(),
            )
            citations = result.get("citations", [])
            status = "COMPLIANT" if result["is_compliant"] else "NOT COMPLIANT"
            answer = (
                f"Compliance Status: {status}. "
                f"Drone Category: {result['drone_category']}. "
            )
            if result.get("missing_permits"):
                answer += f"Missing: {', '.join(result['missing_permits'])}."
            else:
                answer += "All requirements met."

        elif intent == "drone_selector":
            nums = extract_numbers(message)
            result = select_drone(
                use_case=message[:60],
                budget_inr=nums[0] if nums else 500000,
            )
            citations = result.get("citations", [])
            recs = result.get("recommendations", [])
            answer = (
                f"Budget category: {result['budget_category']}. "
                f"Found {result.get('rag_sources_used', 0)} relevant drone options. "
            )
            if recs:
                answer += f"Top recommendation: {recs[0][:200]}..."

        else:
            # Pure RAG fallback
            from mcp_server.rag_bridge import query_pinecone, format_citations
            chunks = query_pinecone(message, top_k=5)
            citations = format_citations(chunks)
            if chunks:
                answer = "Based on the drone knowledge base: " + " ".join(
                    c["text"][:300] for c in chunks[:2]
                )
            else:
                answer = "I could not find specific information about that. Please try rephrasing your question."

    except Exception as e:
        answer = f"An error occurred while processing your query: {str(e)}"

    processing_time = round((time.time() - start) * 1000, 2)

    return {
        "answer": answer,
        "sources": _citations_to_sources(citations),
        "conversation_id": conversation_id,
        "tool_used": intent,
        "processing_time_ms": processing_time,
        "success": True,
    }
