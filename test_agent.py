import asyncio
from api.services.agent import execute_agent

async def test():
    print("Testing 'hi'")
    res1 = await execute_agent("hi")
    print("Response 1:", res1["answer"])

if __name__ == "__main__":
    asyncio.run(test())
