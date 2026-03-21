"""
Flight Time Calculator Tool for MCP
Calculates estimated drone flight time based on battery, weight, payload, and conditions.
"""

from mcp_server.rag_bridge import query_pinecone_filtered, format_citations, format_rag_output


def calculate_flight_time(
    battery_mah: float,
    drone_weight_kg: float,
    payload_kg: float = 0.0,
    wind_speed_kmh: float = 0.0,
    temperature_celsius: float = 25.0,
) -> dict:
    """
    Calculates estimated and safe drone flight times based on battery capacity, drone weight, payload weight, wind speed, and temperature.
    Returns flight time in minutes and an estimated range.
    """
    warnings: list[str] = []
    rag_context: list[str] = []
    citations: list[str] = []

    # Query RAG for drone specs context
    try:
        chunks = query_pinecone_filtered(
            f"drone battery efficiency flight time {drone_weight_kg}kg specifications",
            category="drone_specs", top_k=3,
        )
        rag_context = [c["text"] for c in chunks]
        citations = format_citations(chunks)
    except Exception:
        rag_context = ["RAG system unavailable — using formula-only calculation."]

    # Base flight time calculation
    total_weight = drone_weight_kg + payload_kg
    base_time_minutes = (battery_mah * 3.7 * 0.8) / (total_weight * 9.81 * 1000 / 60)

    # Wind penalty: 1 min per 10 km/h above 15 km/h
    wind_penalty = 0.0
    if wind_speed_kmh > 15:
        wind_penalty = (wind_speed_kmh - 15) / 10.0
        warnings.append("High wind reduces flight time")

    # Temperature penalty: 0.5 min per 5°C below 10°C
    temp_penalty = 0.0
    if temperature_celsius < 10:
        temp_penalty = ((10 - temperature_celsius) / 5.0) * 0.5
        warnings.append("Low temperature reduces battery efficiency")

    if payload_kg > 0:
        warnings.append(f"Payload of {payload_kg}kg increases total weight to {total_weight}kg")

    estimated_time = max(2.0, min(60.0, base_time_minutes - wind_penalty - temp_penalty))
    safe_time = estimated_time * 0.85
    range_estimate_km = safe_time * 40.0 / 60.0

    return {
        "estimated_flight_time_minutes": round(estimated_time, 1),
        "safe_flight_time_minutes": round(safe_time, 1),
        "total_weight_kg": round(total_weight, 2),
        "range_estimate_km": round(range_estimate_km, 1),
        "warnings": warnings,
        "rag_context": rag_context,
        "citations": citations,
    }
