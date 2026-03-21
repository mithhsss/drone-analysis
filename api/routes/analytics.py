"""
Analytics route — GET /analytics
"""
import logging
from fastapi import APIRouter
from api.models.responses import AnalyticsResponse
from api.services.analytics_service import analytics
from api.dependencies import get_pinecone_index

router = APIRouter()
logger = logging.getLogger("api.analytics")


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics():
    try:
        stats = analytics.get_stats()
        try:
            idx = get_pinecone_index()
            vector_count = idx.describe_index_stats().total_vector_count
        except Exception:
            vector_count = 0

        return AnalyticsResponse(
            total_requests=stats["total_requests"],
            requests_by_endpoint=stats["requests_by_endpoint"],
            popular_queries=stats["popular_queries"],
            average_response_time_ms=stats["average_response_time_ms"],
            pinecone_vector_count=vector_count,
        )
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return AnalyticsResponse()
