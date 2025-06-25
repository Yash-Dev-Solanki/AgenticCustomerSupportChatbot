import requests
import urllib3
urllib3.disable_warnings()
from datetime import datetime



def fetch_all_chats(customer_id):
    url = f"https://localhost:7260/api/Chat/{customer_id}"
    response = requests.get(
        url, 
        headers={'accept': '*/*'},
        verify=False,           
        allow_redirects=True,
        timeout=30
    )
    
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

def fetch_chat_messages(customer_id, chat_id):
    if not customer_id or not chat_id:
        return []
    url = f"https://localhost:7260/api/Chat/{customer_id}/{chat_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        chat = response.json()
        return chat.get("messages", [])
    except requests.RequestException as e:
        print(f"[ERROR] fetch_chat_messages: {e}")
        return []

import requests
from datetime import datetime

def save_chat_messages(chat_id, customer_id, messages):
    if not messages:
        print("[DEBUG] No messages passed — skipping save.")
        return

    # Step 1: Filter out empty messages and format them
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

    # Step 2: Fetch existing messages from backend
    get_url = f"https://localhost:7260/api/Chat/{customer_id}/{chat_id}"
    try:
        get_response = requests.get(get_url)
        get_response.raise_for_status()
        existing_messages = get_response.json().get("messages", [])
    except Exception as e:
        print(f"[ERROR] Failed to fetch existing messages: {e}")
        existing_messages = []

    # Step 3: Normalize both sets for comparison
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

    # Step 4: POST updated messages
    url = "https://localhost:7260/api/Chat/store-messages"
    headers = {"Content-Type": "application/json"}
    payload = {
        "chatId": chat_id,
        "customerId": customer_id,
        "messages": filtered
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"[INFO] Saved {len(filtered)} messages to chat {chat_id}")
    else:
        print(f"[ERROR] Failed to save messages: {response.status_code} - {response.text}")



def create_new_chat(customer_id):

    url = "https://localhost:7260/api/Chat/create-chat"
    payload = {
        "customerId": customer_id
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 201:
            chat = response.json()
            return chat.get("chatId")
        else:
            print(f"[ERROR] create_new_chat failed: {response.status_code} - {response.text}")
            return None
    except requests.RequestException as e:
        print(f"[EXCEPTION] create_new_chat failed: {e}")
        return None
