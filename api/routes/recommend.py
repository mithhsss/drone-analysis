"""
Recommend route — POST /recommend/drone
"""
import time
import logging
from fastapi import APIRouter
from api.models.requests import DroneSelectRequest
from api.models.responses import ToolResponse
from api.services.analytics_service import analytics
from mcp_server.tools.drone_selector import select_drone

router = APIRouter()
logger = logging.getLogger("api.recommend")


@router.post("/recommend/drone", response_model=ToolResponse)
async def recommend(request: DroneSelectRequest):
    try:
        start = time.time()
        result = select_drone(**request.model_dump())
        ms = round((time.time() - start) * 1000, 2)
        analytics.track("/recommend/drone", f"recommend {request.use_case}", ms, tool_used="Drone Recommender", model_used="none")
        return ToolResponse(
            success=True, tool_used="drone_selector",
            citations=result.pop("citations", []),
            processing_time_ms=ms, data=result,
        )
    except Exception as e:
        logger.error(f"Recommend error: {e}")
        return ToolResponse(success=False, error=str(e), tool_used="drone_selector")
