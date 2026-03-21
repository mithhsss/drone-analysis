"""
RAG Bridge — the ONLY connection between MCP tools and the existing RAG system.
Wraps the Pinecone + Google GenAI setup from rag/ without rewriting any RAG logic.
"""

import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("rag_bridge")

# Lazy-initialized globals
_pc = None
_index = None
_genai_configured = False


def _ensure_initialized():
    """Lazily initialize Pinecone and GenAI clients."""
    global _pc, _index, _genai_configured
    if _index is not None:
        return

    from pinecone import Pinecone
    import google.generativeai as genai

    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not pinecone_api_key or not google_api_key:
        raise RuntimeError("PINECONE_API_KEY or GOOGLE_API_KEY not set in .env")

    genai.configure(api_key=google_api_key)
    _genai_configured = True
    _pc = Pinecone(api_key=pinecone_api_key)
    _index = _pc.Index("drone-intelligence")


def _embed_query(query: str) -> list[float]:
    """Embed query using same Gemini model as ingestion."""
    import google.generativeai as genai
    result = genai.embed_content(model="models/gemini-embedding-001", content=query)
    return result["embedding"]


def _parse_match(match) -> dict:
    """Parse a Pinecone match into a standardized dict with citation fields."""
    md = match.metadata or {}
    return {
        "text": md.get("text", ""),
        "score": round(float(match.score), 3),
        "source": md.get("source", "unknown"),
        "source_type": md.get("source_type", "unknown"),
        "category": md.get("category", "unknown"),
        "citation_label": md.get("citation_label", md.get("source", "unknown")),
        "record_id": md.get("record_id", ""),
        "chunk_index": md.get("chunk_index", ""),
        "section_heading": md.get("section_heading", ""),
        "row_index": md.get("row_index", ""),
    }


def query_pinecone(query: str, top_k: int = 5) -> list[dict]:
    """Query Pinecone for relevant chunks. Returns list of dicts with citation fields."""
    try:
        _ensure_initialized()
        embedding = _embed_query(query)
        matches = _index.query(vector=embedding, top_k=top_k, include_metadata=True)
        return [_parse_match(m) for m in matches.matches]
    except Exception as e:
        logger.error(f"query_pinecone failed: {e}")
        return []


def query_pinecone_filtered(query: str, category: str, top_k: int = 5) -> list[dict]:
    """Query Pinecone with category filter. Same return format as query_pinecone."""
    try:
        _ensure_initialized()
        embedding = _embed_query(query)
        matches = _index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=True,
            filter={"category": {"$eq": category}},
        )
        return [_parse_match(m) for m in matches.matches]
    except Exception as e:
        logger.error(f"query_pinecone_filtered failed: {e}")
        return []


def format_citations(chunks: list[dict]) -> list[str]:
    """Convert retrieved chunks into human-readable citation strings."""
    citations = []
    for c in chunks:
        label = c.get("citation_label", "")
        if label and label != "unknown":
            # Enrich with record_id if available
            rid = c.get("record_id", "")
            if rid and f"record_id" not in label:
                label = f"{label}, record_id: {rid}"
            citations.append(label)
        else:
            source = c.get("source", "unknown")
            row = c.get("row_index", "")
            ci = c.get("chunk_index", "")
            if row != "":
                citations.append(f"{source} (row {row})")
            elif ci != "":
                heading = c.get("section_heading", "")
                citations.append(f"{source} (chunk {ci}, section: {heading})")
            else:
                citations.append(source)
    return citations
