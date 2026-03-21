"""
Compliance route — POST /check/compliance
"""
import time
import logging
from fastapi import APIRouter
from api.models.requests import ComplianceRequest
from api.models.responses import ToolResponse
from api.services.analytics_service import analytics
from mcp_server.tools.compliance_checker import check_compliance

router = APIRouter()
logger = logging.getLogger("api.compliance")


@router.post("/check/compliance", response_model=ToolResponse)
async def compliance(request: ComplianceRequest):
    try:
        start = time.time()
        result = check_compliance(**request.model_dump())
        ms = round((time.time() - start) * 1000, 2)
        analytics.track("/check/compliance", f"compliance {request.drone_weight_kg}kg {request.use_type}", ms)
        return ToolResponse(
            success=True, tool_used="compliance_checker",
            citations=result.pop("citations", []),
            processing_time_ms=ms, data=result,
        )
    except Exception as e:
        logger.error(f"Compliance error: {e}")
        return ToolResponse(success=False, error=str(e), tool_used="compliance_checker")
