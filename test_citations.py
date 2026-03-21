import asyncio
from dotenv import load_dotenv
load_dotenv()
from api.services.agent import execute_agent

async def test():
    print("Executing query...")
    res = await execute_agent("what is the flight time for a 15000mah battery and 3.5kg drone?")
    print("Citations extracted:", res["citations"])

if __name__ == "__main__":
    asyncio.run(test())
