import time
from dotenv import load_dotenv
import streamlit as st
import streamlit_extras.stateful_button as stx
from langchain_core.messages import HumanMessage, AIMessage
from typing import List, Dict, Any
from langchain_core.runnables import RunnableConfig
from uuid import uuid4
import asyncio
from services.pdf_generation import generate_pdf_bytes, generate_excel_bytes
import re
from graph import build_model, invoke_model
from speech_processing import recognize_from_microphone, text_to_microphone
from services.chat_logic import *
from utils import *
from datetime import datetime, timezone


async def stream_text_output(text: str):
    """
    Stream text letter by letter in a parent st.chat_message().
    """
    message_placeholder = st.empty()
    displayed_text = ""

    for char in text:
        displayed_text += char
        message_placeholder.markdown(displayed_text + "▌")  # add cursor for effect
        time.sleep(0.04)  # use time.sleep for Streamlit, not asyncio

    message_placeholder.markdown(displayed_text)  # remove cursor


async def stream_output_with_audio(content):
    ivr_message = ivr_message_generation(content)
    await asyncio.gather(
        text_to_microphone(ivr_message),
        stream_text_output(content),
        return_exceptions= False
    )

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
    st.session_state.messages.append({
        "role": "assistant", 
        "content": ai_msg.content, 
        "to_stream": True,
        "statement_generation": response.get("loan_statement_generation", False)
    })

    # Reset statement generation flag
    st.session_state.state["loan_statement_generation"] = False

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
            "loan_statement_generation": False
        }
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_chat" not in st.session_state:
        st.session_state.current_chat = None
    
    for i, msg in enumerate(st.session_state.messages):
        role = msg.get("role")
        content = msg.get("content")
        to_stream = msg.get("to_stream", False)
        with st.chat_message(role):
            if to_stream:
                await stream_output_with_audio(content)
                msg["to_stream"] = False
            else:
                st.markdown(content)


            if msg.get("statement_generation", False):
                table_match = re.search(r"(\| No\..*?)(\n\n|$)", content, re.DOTALL)
                if table_match:
                    md_table = table_match.group(1)
                    payments = parse_markdown_table(md_table)
                    if payments:
                        pdf_bytes = generate_pdf_bytes(payments)
                        st.download_button(
                            label="Download PDF",
                            data=pdf_bytes,
                            file_name="loan_statement.pdf",
                            mime="application/pdf",
                            key=f"loan_pdf_{i}"
                        )
                        excel_bytes = generate_excel_bytes(payments)
                        st.download_button(
                            label="Download Excel",
                            data=excel_bytes,
                            file_name="loan_statement.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"loan_excel_{i}"
                        )
                
    
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
                        recognize_from_microphone()
                else:
                    if "transcription_results" in st.session_state:
                        with st.spinner("Processing..."):
                            time.sleep(7)
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

    model = build_model()
    config = RunnableConfig({"configurable": {"thread_id": str(uuid4())}})
    asyncio.run(run_app())
