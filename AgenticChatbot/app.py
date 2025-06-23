import time
from dotenv import load_dotenv
import os
import streamlit as st
import streamlit_extras.stateful_button as stx
from langchain_core.messages import AIMessage, HumanMessage

from graph import build_model, invoke_model
from speech_processing import recognize_from_microphone

from chat_logic import fetch_all_chats, fetch_chat_messages, save_chat_messages, create_new_chat


def handle_prompt(prompt: str):
    if "current_chat_id" not in st.session_state or not st.session_state.current_chat_id:
        new_chat_id = create_new_chat(st.session_state.state["customer"]["customerId"])
        st.session_state.current_chat_id = new_chat_id
        st.session_state.chats = load_chats(st.session_state.state["customer"]["customerId"])
        st.session_state.messages = []
        st.session_state.to_be_saved_messages = []
        st.session_state.state["messages"] = []

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.state["messages"].append(HumanMessage(content=prompt))
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.to_be_saved_messages = st.session_state.messages.copy()

    response = invoke_model(model, input_state=st.session_state.state)
    ai_msg = response["messages"][-1]

    st.session_state.state["messages"].append(ai_msg)
    st.session_state.messages.append({"role": "assistant", "content": ai_msg.content})
    st.session_state.to_be_saved_messages = st.session_state.messages.copy()
    save_chat_messages(
    st.session_state.current_chat_id,
    st.session_state.state["customer"]["customerId"],
    st.session_state.to_be_saved_messages
    )
    st.session_state.chats = load_chats(st.session_state.state["customer"]["customerId"])
    st.rerun()


def load_chats(customer_id):
    if not customer_id:
        return []

    chats = fetch_all_chats(customer_id)
    if not chats:
        return []

    # Filter chats to include only those that have at least one non-empty message
    valid_chats = []
    for chat in chats:
        chat_id = chat.get("chatId")
        if not chat_id:
            continue

        messages = fetch_chat_messages(customer_id, chat_id)

        # Filter out chats with no non-empty messages
        for msg in messages:
            content = msg.get("message") or msg.get("content") or ""
            if content.strip():  # if any valid message found
                valid_chats.append(chat)
                break

    return sorted(valid_chats, key=lambda c: c.get("createdAt", c.get("chatId", "")), reverse=True)

def load_chat_messages_to_state(messages):
    converted = []
    for m in messages:
        role = m.get("role") or m.get("sender")
        content = m.get("content") or m.get("message")
        if role == "user":
            converted.append(HumanMessage(content=content))
        else:
            converted.append(AIMessage(content=content))
    return converted

def run_app():
    st.title("Concorde Finances")
    st.markdown("Providing Loan Customer Assistance")

    customer_id_input = st.text_input("Enter Customer ID", key="customer_input")

    if not customer_id_input:
        st.info("Please enter your Customer ID above to start chatting.")
        return

    if ("state" not in st.session_state or
        st.session_state.state.get("customer", {}).get("customerId") != customer_id_input):

        st.session_state.state = {
            "messages": [AIMessage(content="How May I Help You?")],
            "customer": {"customerId": customer_id_input},
            "validated": None
        }
        st.session_state.messages = [{"role": "assistant", "content": "How May I Help You?"}]
        st.session_state.to_be_saved_messages = st.session_state.messages.copy()
        st.session_state.chats = load_chats(customer_id_input)
        st.session_state.current_chat_id = None

    with st.sidebar:
        st.header("Chats")

        if st.button("New Chat"):
            if st.session_state.get("current_chat_id"):
                save_chat_messages(
                    st.session_state.current_chat_id,
                    customer_id_input,
                    st.session_state.to_be_saved_messages
                )

            st.session_state.current_chat_id = None
            st.session_state.messages = [{"role": "assistant", "content": "How May I Help You?"}]
            st.session_state.to_be_saved_messages = st.session_state.messages.copy()
            st.session_state.state["messages"] = [AIMessage(content="How May I Help You?")]

        for chat in st.session_state.chats:
            label = chat.get("title", chat.get("chatId"))
            if st.button(label, key=f"chat_{chat.get('chatId')}"):
                if st.session_state.get("current_chat_id"):
                    save_chat_messages(
                        st.session_state.current_chat_id,
                        customer_id_input,
                        st.session_state.to_be_saved_messages
                    )

                st.session_state.current_chat_id = chat["chatId"]
                messages = fetch_chat_messages(customer_id_input, chat["chatId"])
                st.session_state.messages = messages if messages else []
                st.session_state.to_be_saved_messages = st.session_state.messages.copy()
                st.session_state.state["messages"] = load_chat_messages_to_state(st.session_state.messages)

    for msg in st.session_state.messages:
        role = msg.get("role") or msg.get("sender") or "assistant"
        content = msg.get("content") or msg.get("message") or ""
        with st.chat_message(role):
            st.markdown(content)

    with st.container():
        col1, col2 = st.columns([4, 10], border=True)
        with col1:
            input_method = st.radio("Select Input Method", options=["Text", "Speech"])
        with col2:
            if input_method == "Text":
                if prompt := st.chat_input("Say Something"):
                    handle_prompt(prompt)
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
                        handle_prompt(speech_contents)


if __name__ == "__main__":
    load_dotenv()
    openai_key = os.getenv("OPENAI_API_KEY")

    if not openai_key:
        raise Exception("API Key not set in environment variables")

    model = build_model()
    run_app()
