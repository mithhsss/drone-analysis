"""
RAG Bridge — the ONLY connection between MCP tools and the existing RAG system.
Wraps the Pinecone + Google GenAI setup from rag/ without rewriting any RAG logic.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def query_pinecone(query: str, top_k: int = 5) -> list[dict]:
    """
    Query the Pinecone vector database for relevant document chunks.

    Args:
        query: The search query string.
        top_k: Number of top results to return (default 5).

    Returns:
        A list of dicts, each with keys: "text" (str), "score" (float), "source" (str).

    Raises:
        RuntimeError: If the RAG system is not available.
    """
    try:
        from pinecone import Pinecone
        import google.generativeai as genai
    except ImportError as e:
        raise RuntimeError(f"RAG system not available: {e}")

    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    google_api_key = os.getenv("GOOGLE_API_KEY")

    if not pinecone_api_key or not google_api_key:
        raise RuntimeError(
            "RAG system not available: PINECONE_API_KEY or GOOGLE_API_KEY not set in .env"
        )

    try:
        # Generate query embedding
        genai.configure(api_key=google_api_key)
        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=query,
        )
        query_embedding = result["embedding"]

        # Query Pinecone
        pc = Pinecone(api_key=pinecone_api_key)
        index = pc.Index("drone-intelligence")
        matches = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
        )

        results = []
        for match in matches.matches:
            results.append(
                {
                    "text": match.metadata.get("text", ""),
                    "score": float(match.score),
                    "source": match.metadata.get("source", "Unknown"),
                }
            )
        return results

    except Exception as e:
        raise RuntimeError(f"RAG system not available: {e}")
