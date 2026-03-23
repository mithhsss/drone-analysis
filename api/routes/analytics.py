"""
Analytics route — GET /analytics
"""
import time
import logging
from fastapi import APIRouter
from api.models.responses import AnalyticsResponse
from api.services.analytics_service import analytics
from api.dependencies import get_pinecone_index

router = APIRouter()
logger = logging.getLogger("api.analytics")


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics():
    start_time = time.time()
    try:
        stats = analytics.get_stats()
        
        # Get Pinecone Stats
        try:
            from api.dependencies import get_pinecone_index
            import os
            idx = get_pinecone_index()
            idx_stats = idx.describe_index_stats()
            vector_count = idx_stats.total_vector_count
            index_name = os.getenv("PINECONE_INDEX_NAME", "drone-intelligence1")
        except Exception as e:
            logger.error(f"Pinecone stats error: {e}")
            vector_count = 0
            index_name = "unknown"

        # Derived Analytics
        tool_counts = stats.get("tool_usage_counts", {})
        top_tool = max(tool_counts, key=tool_counts.get) if tool_counts else "none"
        
        cat_counts = stats.get("query_category_counts", {})
        top_category = max(cat_counts, key=cat_counts.get) if cat_counts else "none"
        
        # Requests breakdown
        endpoints = stats.get("requests_by_endpoint", {})
        unique_endpoints = len([k for k, v in endpoints.items() if v > 0])

        processing_time_ms = round((time.time() - start_time) * 1000, 2)
        
        # Track analytics call itself if desired, but task says "every route must track"
        # However, calling track inside get_analytics might lead to infinite recursion 
        # or weird stats if not careful. I'll track it AFTER building the response.
        analytics.track("/analytics", "get_stats", processing_time_ms, tool_used="direct", model_used="direct")

        return AnalyticsResponse(
            generated_at=stats["generated_at"],
            total_requests=stats["total_requests"],
            requests_by_endpoint=endpoints,
            tool_usage_counts=tool_counts,
            query_category_counts=cat_counts,
            response_times=stats["response_times"],
            recent_queries=stats["recent_queries"][:20],  # Last 20 for list
            popular_queries=stats["popular_queries"],
            hourly_distribution=stats["hourly_distribution"],
            model_usage=stats["model_usage"],
            pinecone_vector_count=vector_count,
            pinecone_index_name=index_name,
            success=True,
            processing_time_ms=processing_time_ms
        )
    except Exception as e:
        logger.error(f"Analytics route error: {e}")
        return AnalyticsResponse(success=False)
