"""
Drone Selector Tool for MCP
Recommends suitable drone models based on use case, budget, and requirements.
"""

from mcp_server.rag_bridge import query_pinecone


def select_drone(
    use_case: str,
    budget_inr: float,
    payload_required_kg: float = 0.0,
    flight_time_required_min: float = 20.0,
    indoor_use: bool = False,
) -> dict:
    """
    Recommend suitable drone models based on requirements.

    Args:
        use_case: Primary use case (e.g., "agriculture", "photography").
        budget_inr: Budget in INR.
        payload_required_kg: Required payload capacity in kg.
        flight_time_required_min: Minimum flight time required in minutes.
        indoor_use: Whether the drone is for indoor use.

    Returns:
        Dict with recommendations, budget category, and considerations.
    """
    recommendations: list[str] = []
    all_chunks: list[str] = []
    rag_sources_used = 0

    # Query RAG with two different queries
    try:
        results_1 = query_pinecone(
            f"drone models India {use_case} specifications price",
            top_k=5,
        )
        results_2 = query_pinecone(
            f"best drone {use_case} under {budget_inr} INR payload {payload_required_kg}kg",
            top_k=5,
        )

        # Combine and deduplicate by first 50 chars
        seen_prefixes: set[str] = set()
        for r in results_1 + results_2:
            prefix = r["text"][:50]
            if prefix not in seen_prefixes:
                seen_prefixes.add(prefix)
                all_chunks.append(r["text"])

        rag_sources_used = len(all_chunks)
        recommendations = all_chunks[:5]  # top 5

    except RuntimeError:
        recommendations = [
            "RAG system unavailable. Please ensure Pinecone is running and try again."
        ]

    # Budget category
    if budget_inr < 100000:
        budget_category = "Budget <1L"
    elif budget_inr < 500000:
        budget_category = "Mid-range 1-5L"
    else:
        budget_category = "Premium >5L"

    # Key considerations
    key_considerations: list[str] = []
    key_considerations.append(f"Use case: {use_case}")
    key_considerations.append(f"Budget range: {budget_category}")

    if payload_required_kg > 0:
        key_considerations.append(
            f"Payload requirement: {payload_required_kg}kg — check max payload specs"
        )
    if flight_time_required_min > 30:
        key_considerations.append(
            "Extended flight time needed — consider models with swappable batteries"
        )
    if indoor_use:
        key_considerations.append(
            "Indoor use — prioritize prop guards, smaller form factor, and obstacle avoidance"
        )
    if budget_inr < 50000:
        key_considerations.append(
            "Entry-level budget — limited options for commercial-grade features"
        )

    return {
        "search_criteria": {
            "use_case": use_case,
            "budget_inr": budget_inr,
            "payload_required_kg": payload_required_kg,
            "flight_time_required_min": flight_time_required_min,
            "indoor_use": indoor_use,
        },
        "recommendations": recommendations,
        "budget_category": budget_category,
        "key_considerations": key_considerations,
        "rag_sources_used": rag_sources_used,
    }
