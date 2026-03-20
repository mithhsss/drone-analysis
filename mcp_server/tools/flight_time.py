"""
Flight Time Calculator Tool for MCP
"""

def calculate_flight_time(battery_mah, weight_grams, wind_speed_kmh):
    # Simplified calculation logic for demonstration
    # In a real scenario, this would involve physics models
    base_time = (battery_mah / 1000) * 15 # baseline: 1Ah = 15 mins
    weight_penalty = (weight_grams / 100) * 0.5 # 100g = 0.5 min penalty
    wind_penalty = wind_speed_kmh * 0.2
    
    total_time = max(5, base_time - weight_penalty - wind_penalty)
    return {
        "flight_time_minutes": round(total_time, 2),
        "conditions": {
            "battery": battery_mah,
            "weight": weight_grams,
            "wind": wind_speed_kmh
        }
    }
