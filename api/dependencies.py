"""
Shared dependency injection.
"""
import os
from functools import lru_cache
from pinecone import Pinecone


@lru_cache(maxsize=1)
def get_pinecone_index():
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    return pc.Index(os.getenv("PINECONE_INDEX_NAME", "drone-intelligence"))
