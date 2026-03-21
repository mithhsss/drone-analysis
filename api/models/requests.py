"""
Pydantic request models — field names match the MCP tool function signatures.
"""
from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class FlightTimeRequest(BaseModel):
    battery_mah: float = 5000.0
    drone_weight_kg: float = 1.5
    payload_kg: float = 0.0
    wind_speed_kmh: float = 0.0
    temperature_celsius: float = 25.0


class ROIRequest(BaseModel):
    use_case: str = "agriculture"
    drone_cost_inr: float = 500000.0
    monthly_operational_cost_inr: float = 25000.0
    monthly_revenue_inr: float = 80000.0
    financing_months: int = 0


class ComplianceRequest(BaseModel):
    drone_weight_kg: float = 5.0
    use_type: str = "commercial"
    location: str = "Delhi"
    has_remote_pilot_licence: bool = False


class DroneSelectRequest(BaseModel):
    use_case: str = "agriculture"
    budget_inr: float = 500000.0
    payload_required_kg: float = 0.0
    flight_time_required_min: float = 20.0
    indoor_use: bool = False
