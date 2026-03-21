"""
Drone Selector Tool for MCP
Recommends suitable drone models based on use case, budget, and requirements.
"""

from mcp_server.rag_bridge import query_pinecone_filtered, format_citations, format_rag_output


def select_drone(
    use_case: str,
    budget_inr: float,
    payload_required_kg: float = 0.0,
    flight_time_required_min: float = 20.0,
    indoor_use: bool = False,
) -> dict:
    """
    Selects and recommends the best drone models based on the user's specific use case, allocated budget in INR, payload requirement, required flight time, and whether it's for indoor use.
    Returns drone hardware recommendations and considerations.
    """
    recommendations: list[str] = []
    citations: list[str] = []
    rag_sources_used = 0

    try:
        chunks1 = query_pinecone_filtered(
            f"drone models India {use_case} specifications price payload",
            category="drone_specs", top_k=4,
        )
        chunks2 = query_pinecone_filtered(
            f"best drone {use_case} budget INR {budget_inr} payload {payload_required_kg}kg",
            category="drone_specs", top_k=4,
        )

        # Deduplicate by first 60 chars
        seen: set[str] = set()
        deduped = []
        for c in chunks1 + chunks2:
            prefix = c["text"][:60]
            if prefix not in seen:
                seen.add(prefix)
                deduped.append(c)

        rag_sources_used = len(deduped)
        recommendations = [c["text"] for c in deduped[:5]]
        citations = format_citations(deduped)
    except Exception:
        recommendations = ["RAG system unavailable. Please ensure Pinecone is running."]

    if budget_inr < 100000:
        budget_category = "Budget <1L"
    elif budget_inr < 500000:
        budget_category = "Mid-range 1-5L"
    else:
        budget_category = "Premium >5L"

    key_considerations = [f"Use case: {use_case}", f"Budget range: {budget_category}"]
    if payload_required_kg > 0:
        key_considerations.append(f"Payload: {payload_required_kg}kg — check max payload specs")
    if flight_time_required_min > 30:
        key_considerations.append("Extended flight time — consider swappable batteries")
    if indoor_use:
        key_considerations.append("Indoor use — prioritize prop guards and obstacle avoidance")

    return {
        "search_criteria": {
            "use_case": use_case, "budget_inr": budget_inr,
            "payload_required_kg": payload_required_kg,
            "flight_time_required_min": flight_time_required_min,
            "indoor_use": indoor_use,
        },
        "recommendations": recommendations,
        "budget_category": budget_category,
        "key_considerations": key_considerations,
        "citations": citations,
        "rag_sources_used": rag_sources_used,
    }
