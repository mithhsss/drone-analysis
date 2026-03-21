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
    total_requests: int = 0
    requests_by_endpoint: dict = {}
    popular_queries: List[str] = []
    average_response_time_ms: float = 0.0
    pinecone_vector_count: int = 0
