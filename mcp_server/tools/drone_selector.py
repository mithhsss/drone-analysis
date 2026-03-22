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

    import os
    import csv

    # Parse structural CSV dataset explicitly
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    csv_path = os.path.join(base_dir, "data", "structured", "drone_models.csv")

    try:
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    price = float(row.get("price_inr", 0) or 0)
                    payload = float(row.get("max_payload_kg", 0) or 0)
                    flight_time = float(row.get("max_flight_time_min", 0) or 0)
                    obs_avoidance = str(row.get("obstacle_avoidance", "No")).strip() == "Yes"
                    cases = str(row.get("use_cases", "")).lower()

                    # Filtering constraints
                    if price > budget_inr:
                        continue
                    if payload < payload_required_kg:
                        continue
                    if flight_time < flight_time_required_min:
                        continue
                    if indoor_use and not obs_avoidance:
                        continue
                    if use_case.lower() not in cases:
                        continue
                    
                    # Target Matched!
                    rec_str = f"{row.get('model_name')} by {row.get('manufacturer')} (₹{price:,.0f}) | Payload: {payload}kg | {flight_time}min flight | Category: {row.get('dgca_category')}"
                    recommendations.append(rec_str)
                    citations.append(f"drone_models.csv (Model: {row.get('model_name')})")
                except ValueError:
                    continue  # Skip unparseable malformed rows securely
        rag_sources_used = len(recommendations)
    except Exception as e:
        recommendations = [f"Structural DB unavailable: {e}"]
        
    if not recommendations:
        recommendations = ["No drones precisely match all criteria. Consider expanding your budget or lowering payload minimums."]

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
