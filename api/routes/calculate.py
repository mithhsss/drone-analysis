"""
Calculate routes — flight time and ROI.
"""
import time
import logging
from fastapi import APIRouter
from api.models.requests import FlightTimeRequest, ROIRequest
from api.models.responses import ToolResponse
from api.services.analytics_service import analytics
from mcp_server.tools.flight_time import calculate_flight_time
from mcp_server.tools.roi_calc import calculate_roi

router = APIRouter()
logger = logging.getLogger("api.calculate")


@router.post("/calculate/flight-time", response_model=ToolResponse)
async def flight_time(request: FlightTimeRequest):
    try:
        start = time.time()
        result = calculate_flight_time(**request.model_dump())
        ms = round((time.time() - start) * 1000, 2)
        analytics.track("/calculate/flight-time", f"flight {request.drone_weight_kg}kg", ms)
        result.pop("rag_context", None)
        return ToolResponse(
            success=True, tool_used="flight_time_calculator",
            citations=result.pop("citations", []),
            processing_time_ms=ms, data=result,
        )
    except Exception as e:
        logger.error(f"Flight time error: {e}")
        return ToolResponse(success=False, error=str(e), tool_used="flight_time_calculator")


@router.post("/calculate/roi", response_model=ToolResponse)
async def roi(request: ROIRequest):
    try:
        start = time.time()
        result = calculate_roi(**request.model_dump())
        ms = round((time.time() - start) * 1000, 2)
        analytics.track("/calculate/roi", f"roi {request.use_case}", ms)
        result.pop("rag_insights", None)
        result.pop("sources", None)
        return ToolResponse(
            success=True, tool_used="roi_calculator",
            citations=result.pop("citations", []),
            processing_time_ms=ms, data=result,
        )
    except Exception as e:
        logger.error(f"ROI error: {e}")
        return ToolResponse(success=False, error=str(e), tool_used="roi_calculator")
