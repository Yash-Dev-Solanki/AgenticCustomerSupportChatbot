from dotenv import load_dotenv, find_dotenv
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from typing import List, Dict


# Load environment variables from .env file
load_dotenv(find_dotenv())

title_model = ChatOpenAI(
    model= "gpt-4.1-nano",
    temperature= 0.5,
    api_key= SecretStr(os.getenv("OPENAI_API_KEY", ""))
)

summary_model = ChatOpenAI(
    model= "gpt-4.1-mini",
    temperature= 0,
    api_key= SecretStr(os.getenv("OPENAI_API_KEY", ""))
)

TITLE_GENERATION_PROMPT = """
You are an AI assistant tasked with generating a concise and descriptive title for a chat session based on the initial prompt provided by the user. Do not include any additional information or context beyond the title itself. Do not make use of newline or carriage return characters.

Prompt: {prompt}
"""



def chat_title_generation(prompt: str) -> str:
    """
    Generates a title for the current chat.
    
    Returns:
        str: The title of the application.
    """

    title_prompt = ChatPromptTemplate.from_template(TITLE_GENERATION_PROMPT)
    chain = title_prompt | title_model | StrOutputParser()
    title = chain.invoke({"prompt": prompt})
    return title.strip() if title else "Untitled Chat"

    

def chat_summary_generation(messages : List[Dict]) -> str:
    """
    Generates a summary of a chat conversation from a list of message dictionaries.
    Args:
        messages (List[Dict]): A list of dictionaries, each representing a chat message.
            Each dictionary should typically contain keys such as 'role' (e.g., 'user', 'assistant')
            and 'message' (the text of the message).
    Returns:
        str: A string containing the summarized version of the chat conversation.
    """
    
    SUMMARY_GENERATION_PROMPT = ChatPromptTemplate.from_messages(
        [
            ("system", "Create a detailed summary of the conversation below."),
            ("user", "{messages}")
        ]
    )
    chain = SUMMARY_GENERATION_PROMPT | summary_model | StrOutputParser()
    summary = chain.invoke({"messages": messages})
    return summary.strip()