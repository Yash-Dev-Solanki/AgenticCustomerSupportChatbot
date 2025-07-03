import time
from dotenv import load_dotenv
import os
import streamlit as st
import streamlit_extras.stateful_button as stx
from langchain_core.messages import HumanMessage, AIMessage
from typing import List, Dict, Any
from langchain_core.runnables import RunnableConfig
from uuid import uuid4
import asyncio

from graph import build_model, invoke_model
from speech_processing import recognize_from_microphone
from chat_logic import *
from utils import chat_title_generation
from datetime import datetime, timezone

async def load_messages(messages: List[Dict[str, Any]]):
    """
    Load messages into the Streamlit chat interface.
    """
    
    for msg in messages:
        if msg["role"] == "user":
            st.session_state.state["messages"].append(HumanMessage(content= msg["message"]))
            st.session_state.messages.append({"role": "user", "content": msg["message"]})
        elif msg["role"] == "assistant":
            st.session_state.state["messages"].append(AIMessage(content= msg["message"]))
            st.session_state.messages.append({"role": "assistant", "content": msg["message"]})


async def handle_prompt(prompt: str):
    with st.chat_message("user"):
        st.markdown(prompt)

    messages_to_add = []
    if not (prompt is None or prompt.strip() == ""):       
        st.session_state.state["messages"].append(HumanMessage(content=prompt))
        st.session_state.messages.append({"role": "user", "content": prompt})

        if st.session_state.state["validated"] == True:
            if st.session_state.current_chat is None:
                chat_title = chat_title_generation(prompt)
                st.session_state.current_chat = await create_new_chat(
                    st.session_state.state["customer"]["customerId"],
                    chat_title,
                )
            
            messages_to_add.append({
                "role": "user", 
                "message": prompt, 
                "timestamp": datetime.now(timezone.utc).isoformat()})

    response = invoke_model(model, input_state= st.session_state.state, config= config)
    ai_msg = response["messages"][-1]
    st.session_state.state = response
    st.session_state.messages.append({"role": "assistant", "content": ai_msg.content})

    if st.session_state.state["validated"] == True and st.session_state["current_chat"] is not None:
        messages_to_add.append({
            "role": "assistant",
            "message": ai_msg.content,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        await add_messages_to_chat(
            chat_id= st.session_state.current_chat,
            messages= messages_to_add
        )
        
    st.rerun()


async def run_app():
    validated = None
    if "state" in st.session_state:
        validated = st.session_state.state.get("validated", None)
    
    if validated == True:
        st.set_page_config(initial_sidebar_state= "expanded")
        st.session_state["chatHistory"] = await fetch_all_chats_by_customer_id(st.session_state.state["customer"]["customerId"])
    else:
        st.set_page_config(initial_sidebar_state= "collapsed")
    
    
    st.title("Concorde Finances")
    st.markdown("Providing Loan Customer Assistance")

    if "state" not in st.session_state: 
        st.session_state.state = {
            "customer": None,
            "validated": None,
            "messages": [],
            "validation_retries": 3,
            "current_retries": 0,
        }
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_chat" not in st.session_state:
        st.session_state.current_chat = None
    

    for msg in st.session_state.messages:
        role = msg.get("role")
        content = msg.get("content")
        with st.chat_message(role):
            st.markdown(content)

    
    if st.session_state.state["validated"] is None and len(st.session_state.state["messages"]) == 0:
        await handle_prompt("")

    
    with st.container():
        col1, col2 = st.columns([4, 10], border=True)
        with col1:
            input_method = st.radio("Select Input Method", options=["Text", "Speech"])
        with col2:          
            if input_method == "Text":
                if prompt := st.chat_input("Say Something"):
                    await handle_prompt(prompt)
            elif input_method == "Speech":
                speech_to_text = stx.button(":material/mic:", key="recording_in_progress")
                if speech_to_text:
                    if "transcription_results" not in st.session_state:
                        st.session_state.transcription_results = recognize_from_microphone(st.session_state)
                else:
                    if "transcription_results" in st.session_state:
                        with st.spinner("Processing..."):
                            time.sleep(5)
                            speech_contents = ' '.join(st.session_state.transcription_results)
                            del st.session_state.transcription_results
                        await handle_prompt(speech_contents)
    
    with st.sidebar:
        welcome_message = f"Welcome to Concorde Finances, {st.session_state.state['customer']['customerName'] if validated else 'Guest'}!"
        st.header(welcome_message)
        new_chat_button = st.button("New Chat", disabled= not validated, type= "primary")
        if new_chat_button:
            print("[DEBUG] New chat button clicked")
            st.session_state.current_chat = None
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("### Chat History")
        for chat in st.session_state.get("chatHistory", []):
            chatId = chat['chatId']
            chatTitle = chat['chatTitle']
            isCurrentChat = chatId == st.session_state.current_chat
            load_chat_buton = st.button(chatTitle, key= chatId, disabled= isCurrentChat, type= "tertiary" if isCurrentChat else "secondary")
            if load_chat_buton:
                print(f"[DEBUG] Load chat button clicked for chatId: {chatId}")
                st.session_state.state["messages"] = []
                st.session_state.messages = []
                st.session_state.current_chat = chatId
                chat_messages = await fetch_messages_by_chat_id(chatId)
                await load_messages(chat_messages)
                st.rerun()


if __name__ == "__main__":
    load_dotenv()
    openai_key = os.getenv("OPENAI_API_KEY")

    if not openai_key:
        raise Exception("API Key not set in environment variables")

    model = build_model()
    config = RunnableConfig({"configurable": {"thread_id": str(uuid4())}})
    asyncio.run(run_app())
