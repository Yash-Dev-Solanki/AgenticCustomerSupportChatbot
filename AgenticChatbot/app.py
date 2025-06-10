import time
from dotenv import load_dotenv
import os

import streamlit as st
import streamlit_extras.stateful_button as stx 
from langchain_core.messages import AIMessage, HumanMessage


from graph import build_model, invoke_model
from speech_processing import recognize_from_microphone

def handle_prompt(prompt: str):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
        
        # Add message to chat history
    st.session_state.state["messages"].append(HumanMessage(content= prompt))
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = invoke_model(model, input_state= st.session_state.state)
    st.session_state.messages.append({"role": "assistant", "content": response["messages"][-1].content})
    st.session_state.state = response
    st.rerun()


def run_app():
    st.title("Concorde Finances")
    st.markdown("Providing Loan Customer Assistance")
    
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How May I Help You?"}]
    
    if "state" not in st.session_state:
        st.session_state["state"] = {
            "messages": [AIMessage(content= "How May I Hep You?")],
            "customer": None,
            "validated": None
        }
    
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    with st.container():
        col1, col2 = st.columns([4, 10], border= True)
        with col1:
           input_method = st.radio("Select Input Method", options= ["Text", "Speech"])
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
                        with st.spinner(""):
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
    


