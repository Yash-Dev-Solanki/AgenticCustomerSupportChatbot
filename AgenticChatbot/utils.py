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

ivr_model = ChatOpenAI(
    model= "gpt-4.1-nano",
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


def ivr_message_generation(content: str) -> str:
    """
    Converts the given content into a shorter message that can easily read by the ivr system
    Args:
        content: The original message content
    Returns:
        str: Shortened IVR friendly message
    """

    IVR_PROMPT = ChatPromptTemplate.from_messages(
        [
            ("system", "Shorten the following message to a message that can be communicated by an IVR teleprompter. Make sure to not omit important details."),
            ("user", "{content}"),
        ]
    )

    chain = IVR_PROMPT | ivr_model | StrOutputParser()
    return chain.invoke({"content": content}).strip()



def parse_markdown_table(md_table: str):
    lines = [line.strip() for line in md_table.strip().splitlines() if line.strip()]
    # Remove separator lines like: |-----|------|
    lines = [line for line in lines if not set(line) <= {'|', '-', ' '}]
    if not lines:
        return []
    header = [h.strip() for h in lines[0].strip('|').split('|')]
    data_rows = []
    for line in lines[1:]:
        cols = [c.strip() for c in line.strip('|').split('|')]
        if len(cols) == len(header):
            data_rows.append(dict(zip(header, cols)))
    return data_rows


