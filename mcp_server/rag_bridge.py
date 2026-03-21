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
    _index = _pc.Index("drone-intelligence1")


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


def extract_meaningful_excerpt(text: str, max_words: int = 60) -> str:
    """
    Returns a complete-sentence excerpt from text within max_words limit.
    Never cuts mid-sentence. If the first sentence exceeds max_words,
    truncates at the last complete word and appends '...'
    If text fits within max_words, returns it fully without truncation.
    """
    if not text or not text.strip():
        return ""

    # count words
    words = text.strip().split()
    if len(words) <= max_words:
        return text.strip()

    # find sentence boundaries ('. ', '! ', '? ', '.\n')
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    result = ""
    for sentence in sentences:
        candidate = (result + " " + sentence).strip()
        if len(candidate.split()) <= max_words:
            result = candidate
        else:
            break

    # if even first sentence is too long, truncate at word boundary
    if not result:
        result = " ".join(words[:max_words]) + "..."

    return result.strip()


def format_rag_output(chunks: list[dict], max_words_per_chunk: int = 60) -> list[str]:
    """
    Converts retrieved chunks to meaningful excerpts.
    Each excerpt is a complete sentence or ends cleanly.
    Returns list of strings ready to display to user.
    """
    output = []
    for chunk in chunks:
        text = chunk.get("text", "")
        excerpt = extract_meaningful_excerpt(text, max_words=max_words_per_chunk)
        if excerpt:
            output.append(excerpt)
    return output
