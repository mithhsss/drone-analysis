import asyncio
import uuid
from dotenv import load_dotenv
load_dotenv()

from api.services.chat_service import handle_chat

async def test():
    chat_id = str(uuid.uuid4())
    print(f"Testing with chat_id: {chat_id}")
    
    print("\nTURN 1: Initial Question")
    res1 = await handle_chat("What is the flight time for a 15000mah battery and 3.5kg drone?", chat_id)
    print("A:", res1["answer"])
    print("Words:", len(res1["answer"].split()))
    
    print("\nTURN 2: Follow-up Question (Memory Test)")
    res2 = await handle_chat("What if I swapped the battery out to 5000mah instead? Do the exact same calculation.", chat_id)
    print("A:", res2["answer"])
    print("Words:", len(res2["answer"].split()))
    
    print("\nTURN 3: Open-ended length test")
    res3 = await handle_chat("Write me a complete, incredibly exhaustive two-page essay about drone regulations in India with as many words as possible.", chat_id)
    print("A:", res3["answer"])
    print("Words:", len(res3["answer"].split()))

if __name__ == "__main__":
    asyncio.run(test())
