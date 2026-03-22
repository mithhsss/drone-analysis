import asyncio
import json
from dotenv import load_dotenv
load_dotenv()

from api.services.chat_service import handle_chat
from api.routes.chat import list_chats, get_chat

async def test():
    print("=== TURN 1: New Chat ===")
    res1 = await handle_chat("What are the rules for flying drones at night?")
    chat_id = res1["conversation_id"]
    print(f"Chat ID: {chat_id}")
    print(f"A: {res1['answer']}\n")

    print("\n=== TURN 2: Follow-up ===")
    res2 = await handle_chat("What if I use a nano drone instead? Does that change anything?", conversation_id=chat_id)
    print(f"A: {res2['answer']}\n")

    print("\n=== API TEST: GET /chats ===")
    chats_res = await list_chats()
    print(json.dumps(chats_res, indent=2))

    print("\n=== API TEST: GET /chats/{chat_id} ===")
    history_res = await get_chat(chat_id)
    print(json.dumps(history_res, indent=2))

if __name__ == "__main__":
    asyncio.run(test())
