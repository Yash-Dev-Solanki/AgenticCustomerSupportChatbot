import aiohttp
from datetime import datetime
from typing import List, Dict, Any
from endpoints import Endpoints
from dateutil.parser import parse


async def fetch_all_chats_by_customer_id(customer_id: str) -> List[Dict[str, Any]]:
    url = Endpoints.GET_CHAT_BY_CUSTOMER_ID
    headers = {'customerId': customer_id}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                url, 
                headers= headers, 
                ssl=False,
            ) as response:
                data = await response.json()
                status = response.status
                if status == 200:
                    chats = data.get('chats', [])
                    sorted_chats = sorted(
                        chats, 
                        key=lambda x: x.get('createdAt', ''),
                        reverse=True
                    )

                    return sorted_chats
                else:
                    print(f"[ERROR] fetch_all_chats failed with status {response.status}: {data['errors']}")
                    return []
        except aiohttp.ClientError as e:
            print(f"[EXCEPTION] fetch_all_chats_by_customer_id failed: {e}")
            return []


async def create_new_chat(customer_id: str, chat_title: str) -> str:
    url = Endpoints.CREATE_NEW_CHAT
    headers = {'customerId': customer_id, "chatTitle": chat_title}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                url, 
                headers=headers, 
                ssl=False,
            ) as response:
                data = await response.json()
                status = response.status
                if status == 201:
                    print(f"[INFO] New chat created successfully for customer {customer_id}")
                    return data.get('chatId', "")
                else:
                    print(f"[ERROR] create_new_chat failed with status {response.status}: {data['errors']}")
                    return ""
        except aiohttp.ClientError as e:
            print(f"[EXCEPTION] create_new_chat failed: {e}")
            return ""


async def add_messages_to_chat(chat_id: str, messages: List[dict]) -> bool:
    if not chat_id.strip():
        print("[DEBUG] Invalid chat_id — skipping.")
        return False
    if not messages or len(messages) == 0:
        print("[DEBUG] No messages to add — skipping.")
        return False

    url = Endpoints.ADD_MESSAGES_TO_CHAT
    headers = {
        'accept': '*/*',
        'Content-Type': 'application/json'}
    body = {
        "chatId": chat_id,
        "messages": messages
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, 
                headers= headers,
                json= body, 
                ssl= False,
            ) as response:
                print(response.status)
                if response.status == 201:
                    print(f"[INFO] Successfully added {len(messages)} messages to chat {chat_id}")
                    return True
                else:
                    data = await response.json()
                    print(f"[ERROR] add_messages_to_chat failed with status {response.status}: {data['errors']}")
                    return False
    except aiohttp.ClientError as e:
        print(f"[EXCEPTION] add_messages_to_chat failed: {e}")
        return False


async def fetch_messages_by_chat_id(chat_id: str) -> List[Dict[str, Any]]:
    url = Endpoints.GET_MESSAGES_BY_CHAT_ID.format(chatId= chat_id)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                url, 
                ssl=False,
            ) as response:
                data = await response.json()
                if response.status == 200:
                    return data['chat']['messages']
                else:
                    print(f"[ERROR] fetch_messages_by_chat_id failed with status {response.status}: {data['errors']}")
                    return []
        except aiohttp.ClientError as e:
            print(f"[EXCEPTION] fetch_messages_by_chat_id failed: {e}")
            return []







