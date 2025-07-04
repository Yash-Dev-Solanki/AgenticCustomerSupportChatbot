from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent, InjectedState
from langchain_openai import ChatOpenAI
from typing import (
    Dict,
    List,
    Annotated, 
    Any
)
from langgraph.graph.graph import CompiledGraph

import requests
import certifi
import ssl
import urllib3
urllib3.disable_warnings()
from endpoints import Endpoints
from datetime import datetime, timezone, timedelta
from utils import chat_summary_generation
from dotenv import load_dotenv, find_dotenv
from pydantic import SecretStr
import os
from models.graphState import GraphState


load_dotenv(find_dotenv())

model = ChatOpenAI(
    model= "gpt-4o",
    temperature= 0,
    api_key= SecretStr(os.getenv('OPENAI_API_KEY', ''))
)


def fetch_all_chats_by_customer_id(customer_id: str) -> List[Dict]:
    url = Endpoints.GET_CHAT_BY_CUSTOMER_ID
    headers = {
        "customerId": customer_id
    }

    try:
        response = requests.get(
            url,
            headers= headers,
            verify= False,
        )
        data = response.json()
        if response.status_code == 200:
            chats = data.get('chats', [])
            sorted_chats = sorted(
                        chats, 
                        key= lambda x: datetime.fromisoformat(x['createdAt'].replace('Z', '+00:00')), 
                        reverse=True
                    )
            return sorted_chats
        else:
            print(f"[ERROR] fetch_all_chats failed with status {response.status_code}: {data['errors']}")
            return []
    except Exception as e:
        print("[EXCEPTION] Could not complete request", e)
        return []


def fetch_messages_by_chat_id(chatId: str) -> List[Dict]:
    url = Endpoints.GET_MESSAGES_BY_CHAT_ID.format(chatId= chatId)

    try:
        response = requests.get(
            url,
            verify= False
        )
        data = response.json()
        if response.status_code == 200:
            return data['chat']['messages']
        else:
            print(f"[ERROR] fetch_messages_by_chat_id failed with status {response.status_code}: {data['errors']}")
            return []
    except Exception as e:
        print("[EXCEPTION] Could not complete request", e)
        return []


def fetch_summary_for_chat_id(chatId: str) -> str:
    url = Endpoints.GET_MESSAGES_BY_CHAT_ID.format(chatId= chatId)

    try:
        response = requests.get(
            url,
            verify= False
        )
        data = response.json()
        if response.status_code == 200:
            summary = data['chat']['summary']
            return summary if summary else ""
             
        else:
            print(f"[ERROR] fetch_messages_by_chat_id failed with status {response.status_code}: {data['errors']}")
            return ""
    except Exception as e:
        print("[EXCEPTION] Could not complete request", e)
        return ""


def add_summary_to_chat(chatId: str, summary: str) -> bool:
    url = Endpoints.SET_CHAT_SUMMARY
    headers = {
        "accept": "*/*",
        "Content-Type": "application/json"
    }
    payload = {
        "chatId": chatId,
        "summary": summary
    }

    try:
        response = requests.post(
            url,
            headers= headers,
            json= payload,
            verify= False
        )
        if response.status_code == 201:
            return True
        else:
            print(f"[ERROR] fetch_messages_by_chat_id failed with status {response.status_code}")
            return False
    except Exception as e:
        print("[EXCEPTION] Could not complete request", e)
        return False




# In Memory Cache to avoid repeated API calls
cache = {}

@tool(parse_docstring= True)
def setup_summary_cache(state: Annotated[Dict[str, Any], InjectedState]) -> List[Dict]:
    """
    Sets up a cache of chat summaries for a given customer by retrieving their chat history and checking for existing summaries in the cache.

    Args:
        state (Dict[str, Any]): The current state containing customer information, injected automatically.
    """

    customer_id = state["customer"]["customerId"]
    summaries = []
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days= 7)
    chat_history = fetch_all_chats_by_customer_id(customer_id)
    for chat in chat_history:
        # Check cutoff date of past week
        created_at = datetime.fromisoformat(chat['createdAt'].replace("Z", "+00:00"))
        if created_at < cutoff:
            break

        if chat['chatId'] not in cache:
            messages = fetch_messages_by_chat_id(chat['chatId'])
            current_summary = fetch_summary_for_chat_id(chat['chatId'])
            if current_summary:
                summary = current_summary
            else:
                summary = chat_summary_generation(messages)
                add_summary_to_chat(chat['chatId'], summary)
            
            cache[chat['chatId']] = summary
        
        
        chat['summary'] = cache[chat['chatId']]
        summaries.append(chat)

    return summaries



def get_summary_agent() -> CompiledGraph:
    agent = create_react_agent(
        model= model,
        tools= [setup_summary_cache],
        prompt= (
            """
            You're a summarization agent for an application tasked responding to user queries about the operations performed by them via the chatbot application over the past week.

            PROCESS FLOW:
            1. Make use of the setup_summary_cache tool to retreive details about the chats initiated by the user along with their respective summaries.
            2. Utilize these summaries to answer the user query appropriately


            INSTRUCTIONS:
            - Assist only with user activity & summarization queries.
            - After you're done, respond to the supervisor directly
            - Respond ONLY with the results, do NOT include ANY other text.
            - While providing summaries, also include the pecise datetime on which the operation was performed.
            """
        ),
        name= "summary_agent",
        state_schema= GraphState
    )

    return agent




