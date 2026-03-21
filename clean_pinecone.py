import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
idx = pc.Index('drone-intelligence')

print(f"Stats before deletion: {idx.describe_index_stats().total_vector_count} vectors")
print("Clearing all vectors from index...")
idx.delete(delete_all=True)
print("All vectors deleted.")
