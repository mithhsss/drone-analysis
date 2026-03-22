import asyncio
from dotenv import load_dotenv
load_dotenv()

from api.services.agent import execute_agent

async def test():
    print("Testing Agent RAG Integration...")
    result = await execute_agent("What are the DGCA penalties for flying over a red zone?")
    print("Answer:", result["answer"])
    print("Tool Used:", result["tool_used"])
    print("Citations Array:", result["citations"])
    
if __name__ == "__main__":
    asyncio.run(test())
