"""
Pydantic response models — field names match what the frontend reads.
"""
from pydantic import BaseModel
from typing import Any, List, Optional


class ChatResponse(BaseModel):
    """Matches frontend: data.answer, data.sources"""
    answer: str
    sources: List[dict] = []
    conversation_id: str = ""
    tool_used: str = ""
    processing_time_ms: float = 0.0
    success: bool = True


class ToolResponse(BaseModel):
    """Standard envelope for all direct tool API calls."""
    success: bool = True
    tool_used: str = ""
    citations: List[str] = []
    processing_time_ms: float = 0.0
    data: dict = {}
    error: str = ""


class UploadResponse(BaseModel):
    success: bool
    filename: str = ""
    vectors_added: int = 0
    message: str = ""


class AnalyticsResponse(BaseModel):
    generated_at: str = ""
    total_requests: int = 0
    requests_by_endpoint: dict = {}
    tool_usage_counts: dict = {}
    query_category_counts: dict = {}
    response_times: dict = {"avg": 0.0, "min": 0.0, "max": 0.0, "p95": 0.0}
    recent_queries: List[dict] = []
    popular_queries: List[dict] = []
    hourly_distribution: dict = {}
    model_usage: dict = {}
    pinecone_vector_count: int = 0
    pinecone_index_name: str = ""
    success: bool = True
    processing_time_ms: float = 0.0
