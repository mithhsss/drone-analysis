import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from dotenv import load_dotenv
from pinecone import Pinecone
import google.generativeai as genai

load_dotenv()

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

# Will be initialized lazily on first request
_initialized = False
_index = None


def _ensure_initialized():
    """Lazily initialize Pinecone and GenAI on first request."""
    global _initialized, _index
    if _initialized:
        return

    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    google_api_key = os.getenv("GOOGLE_API_KEY")

    if not pinecone_api_key or not google_api_key:
        raise HTTPException(status_code=500, detail="PINECONE_API_KEY or GOOGLE_API_KEY not set in .env")

    genai.configure(api_key=google_api_key)
    pc = Pinecone(api_key=pinecone_api_key)
    _index = pc.Index("drone-intelligence")
    _initialized = True


def get_embedding(text: str) -> list:
    """Generate embedding using Google's embedding model."""
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text
    )
    return result['embedding']


def query_pinecone(query_text: str, top_k: int = 4):
    """Query Pinecone for relevant document chunks."""
    query_embedding = get_embedding(query_text)
    results = _index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    return results.matches


def generate_answer(query: str, context_chunks: list) -> str:
    """Use Gemini to generate an answer based on retrieved context."""
    context_text = "\n\n---\n\n".join([
        f"[Source: {m.metadata.get('source', 'Unknown')}, Page: {m.metadata.get('page_number', '?')}]\n{m.metadata.get('text', '')}"
        for m in context_chunks
    ])

    prompt = f"""You are an expert Drone Intelligence Assistant for India.
Use the following retrieved context to answer the user's question accurately.
If you don't know the answer or the context is insufficient, say so and suggest they refer to official DGCA guidelines. Do not hallucinate.

Retrieved Context:
{context_text}

User Question: {query}

Answer:"""

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text


@router.post("/")
async def chat_endpoint(request: ChatRequest):
    try:
        _ensure_initialized()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Init failed: {str(e)}")

    try:
        # 1. Query Pinecone for relevant chunks
        matches = query_pinecone(request.message)

        # 2. Generate answer using Gemini
        answer = generate_answer(request.message, matches)

        # 3. Extract sources for the frontend
        sources = []
        seen = set()
        for m in matches:
            title = f"Source: {m.metadata.get('source', 'Unknown')}"
            if title not in seen:
                seen.add(title)
                snippet = m.metadata.get('text', '')[:100] + "..."
                page = m.metadata.get('page_number', '')
                sources.append({
                    "title": title,
                    "link": f"page={page}",
                    "snippet": snippet
                })

        return {
            "answer": answer,
            "sources": sources
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
