from datetime import datetime
import httpx
import asyncio

async def fetch_all_chats(customer_id):
    url = f"http://localhost:5142/api/Chat/{customer_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            chats = response.json()
            return [
            {
                "chatId": chat["chatId"],
                "title": f"Chat {chat['createdAt'][:10]}"
            } 
            for chat in chats
        ]
        else:
            print(f"[ERROR] fetch_all_chats failed with status {response.status_code}: {response.text}")
            return []

async def fetch_chat_messages(customer_id, chat_id):
    if not customer_id or not chat_id:
        return []

    url = f"http://localhost:5142/api/Chat/{customer_id}/{chat_id}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            chat = response.json()
            messages = chat.get("messages", [])
            return [
                {
                    **msg,
                    "content": (msg.get("content") or msg.get("message") or "").strip()
                }
                for msg in messages
                if (msg.get("message") or msg.get("content") or "").strip()
            ]
    except httpx.RequestError as e:
        print(f"[ERROR] fetch_chat_messages: {e}")
        return []


async def save_chat_messages(chat_id, customer_id, messages):
    if not messages:
        print("[DEBUG] No messages passed — skipping save.")
        return
    filtered = []
    for msg in messages:
        content = msg.get("content") or msg.get("message") or ""
        if content.strip():
            sender = msg.get("role") or msg.get("sender") or "unknown"
            filtered.append({
                "sender": sender.strip().lower(),
                "message": content.strip(),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })

    if not filtered:
        print("[DEBUG] All messages are empty — skipping save.")
        return
    get_url = f"http://localhost:5142/api/Chat/{customer_id}/{chat_id}"
    try:
        async with httpx.AsyncClient() as client:
            get_response = await client.get(get_url)
            get_response.raise_for_status()
            existing_messages = get_response.json().get("messages", [])
    except Exception as e:
        print(f"[ERROR] Failed to fetch existing messages: {e}")
        existing_messages = []

    def normalize(msg):
        return {
            "sender": (msg.get("sender") or msg.get("role") or "").strip().lower(),
            "message": (msg.get("message") or msg.get("content") or "").strip()
        }

    existing_normalized = [normalize(m) for m in existing_messages]
    new_normalized = [normalize(m) for m in filtered]

    if existing_normalized == new_normalized:
        print("[DEBUG] No new messages or changes detected — skipping save.")
        return
    post_url = "http://localhost:5142/api/Chat/store-messages"
    
    payload = {
        "chatId": chat_id,
        "customerId": customer_id,
        "messages": filtered
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(post_url, json=payload)
        if response.status_code == 200:
            print(f"[INFO] Saved {len(filtered)} messages to chat {chat_id}")
        else:
            print(f"[ERROR] Failed to save messages: {response.status_code} - {response.text}")

async def create_new_chat(customer_id):
    url = "http://localhost:5142/api/Chat/create-chat"
    payload = {
        "customerId": customer_id
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            if response.status_code == 201:
                chat = response.json()
                return chat.get("chatId")
            else:
                print(f"[ERROR] create_new_chat failed: {response.status_code} - {response.text}")
            return None
    except httpx.RequestError as e:
        print(f"[EXCEPTION] create_new_chat failed: {e}")
        return None
