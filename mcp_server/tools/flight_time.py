"""
Flight Time Calculator Tool for MCP
Calculates estimated drone flight time based on battery, weight, payload, and conditions.
"""

from mcp_server.rag_bridge import query_pinecone


def calculate_flight_time(
    battery_mah: float,
    drone_weight_kg: float,
    payload_kg: float = 0.0,
    wind_speed_kmh: float = 0.0,
    temperature_celsius: float = 25.0,
) -> dict:
    """
    Calculate estimated flight time for a drone.

    Args:
        battery_mah: Battery capacity in milliamp-hours.
        drone_weight_kg: Drone weight in kilograms.
        payload_kg: Payload weight in kilograms.
        wind_speed_kmh: Wind speed in km/h.
        temperature_celsius: Ambient temperature in Celsius.

    Returns:
        Dict with flight time estimates, warnings, and RAG context.
    """
    warnings: list[str] = []
    rag_context: list[str] = []

    # Query RAG for context
    try:
        rag_results = query_pinecone(
            f"drone battery flight time {drone_weight_kg}kg efficiency specifications",
            top_k=5,
        )
        rag_context = [r["text"][:200] for r in rag_results]
    except RuntimeError:
        rag_context = ["RAG system unavailable — using formula-only calculation."]

    # Base flight time calculation
    total_weight = drone_weight_kg + payload_kg
    base_time_minutes = (battery_mah * 3.7 * 0.8) / (total_weight * 9.81 * 1000 / 60)

    # Wind penalty: subtract 1 minute per 10 km/h wind above 15 km/h
    wind_penalty = 0.0
    if wind_speed_kmh > 15:
        wind_penalty = (wind_speed_kmh - 15) / 10.0
        warnings.append("High wind reduces flight time")

    # Temperature penalty: subtract 0.5 minutes per 5°C below 10°C
    temp_penalty = 0.0
    if temperature_celsius < 10:
        temp_penalty = ((10 - temperature_celsius) / 5.0) * 0.5
        warnings.append("Low temperature reduces battery efficiency")

    estimated_time = base_time_minutes - wind_penalty - temp_penalty

    # Payload warning
    if payload_kg > 0:
        warnings.append(f"Payload of {payload_kg}kg increases total weight to {total_weight}kg")

    # Cap: minimum 2 minutes, maximum 60 minutes
    estimated_time = max(2.0, min(60.0, estimated_time))

    safe_time = estimated_time * 0.85
    average_speed_kmh = 40.0
    range_estimate_km = safe_time * average_speed_kmh / 60.0

    return {
        "estimated_flight_time_minutes": round(estimated_time, 1),
        "safe_flight_time_minutes": round(safe_time, 1),
        "total_weight_kg": round(total_weight, 2),
        "range_estimate_km": round(range_estimate_km, 1),
        "warnings": warnings,
        "rag_context": rag_context,
    }
