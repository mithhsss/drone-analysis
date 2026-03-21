"""
Drone Intelligence System — FastAPI Backend
Connects the React frontend to MCP tools and Pinecone RAG.

Frontend API contract (from ChatAssistant.tsx):
  POST http://localhost:8000/api/chat/
  Request:  { message: string }
  Response: { answer: string, sources: [{title, link, snippet}] }
"""
import os
import sys
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Ensure project root is on sys.path for mcp_server imports
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("drone-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    from api.dependencies import get_pinecone_index
    try:
        index = get_pinecone_index()
        stats = index.describe_index_stats()
        logger.info(f"Drone Intelligence API started")
        logger.info(f"Pinecone index: drone-intelligence | Vectors: {stats.total_vector_count}")
    except Exception as e:
        logger.warning(f"Could not connect to Pinecone at startup: {e}")
    yield


app = FastAPI(
    title="Drone Intelligence System — India",
    description="AI-powered drone knowledge hub with Pinecone RAG and MCP tools",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from api.routes import chat, calculate, compliance, recommend, upload, analytics

# /api/chat/ — matches frontend's fetch URL exactly
app.include_router(chat.router, prefix="/api", tags=["Chat"])

# /api/v1/* — additional direct tool endpoints
app.include_router(calculate.router, prefix="/api/v1", tags=["Calculate"])
app.include_router(compliance.router, prefix="/api/v1", tags=["Compliance"])
app.include_router(recommend.router, prefix="/api/v1", tags=["Recommend"])
app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])


@app.get("/", tags=["Health"])
async def health_check():
    from api.dependencies import get_pinecone_index
    try:
        stats = get_pinecone_index().describe_index_stats()
        vector_count = stats.total_vector_count
    except Exception:
        vector_count = "unavailable"
    return {
        "status": "ok",
        "service": "Drone Intelligence API",
        "version": "1.0.0",
        "vectors": vector_count,
    }
