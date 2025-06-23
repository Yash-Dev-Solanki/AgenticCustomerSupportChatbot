from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

from tools.loan_statement_tool import get_loan_statement
from models.graphState import GraphState
from dotenv import load_dotenv
from pydantic import SecretStr
import os

load_dotenv()

model = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    streaming=True,
    api_key=SecretStr(os.getenv('OPENAI_API_KEY', ''))
)

def get_loan_statement_agent():
    agent = create_react_agent(
        model=model,
        tools=[get_loan_statement],
        prompt=(
            """You are a helpful loan statement assistant.

            ONLY use the `get_loan_statement` tool to respond to the user's request.

            INSTRUCTIONS:
            - If the user asks for their loan statement in any form (e.g., "get my loan statement", "show statement", "I want my EMI breakdown", "okay", "yes", "please show"), immediately call the tool.
            - Do NOT ask follow-up questions.
            - Do NOT respond directly.
            - Do NOT repeat the tool call.
            - Call the tool exactly ONCE.
            - The tool will use information from the conversation state.

            Once the tool has been used, stop and return control to the supervisor or user."""
        ),
        name="loan_statement_agent",
        state_schema=GraphState,
    )
    
    return agent
