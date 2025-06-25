from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from dotenv import load_dotenv, find_dotenv
import os
from pydantic import SecretStr
from langgraph.prebuilt import create_react_agent, InjectedState
from langgraph.graph.graph import CompiledGraph
from langgraph.types import Command
from models.graphState import GraphState
from tools.customer_id_validation import validate_customer_id
from typing import (
    Annotated, 
    Dict, 
    Any
)
from langchain_core.messages import AIMessage


load_dotenv(find_dotenv())
model = ChatOpenAI(
    model= "gpt-4o",
    temperature= 0,
    api_key= SecretStr(os.getenv("OPENAI_API_KEY", ''))
)

prompt = """
You are a welcome agent for a Loan application system.
Your role is to greet the user and perform validation on their customer ID.

PRIMARY OBJECTIVES:
1. Greet customers warmly and professionally
2. Validate customer identity using their customer ID

PROCESS:
- If no message exists, proactively greet the customer & ask for their customer ID.
- When customer provides ID, use validate_customer_id tool to check it
- If validation is successful, call the customer by their name and provide a summary of their account.
- If validation fails, call the validation_failure tool to handle the failure.

TOOLS:
- validate_customer_id: Validates the customer ID and returns customer details if successful.
"""


@tool
def handle_validation_failure(state: Annotated[Dict[str, Any], InjectedState]) -> Command:
    '''
    Handles the case when customer ID validation fails.
    '''
    current_retries = state["current_retries"]
    max_retries = state.get("validation_retries", 3)

    if current_retries == max_retries:
        return Command(
            update={
                "messages": [
                    AIMessage(content="Maximum validation attempts reached. Please contact support.")
                ],
                "validated": False,
            },
        )
    
    
    return Command(
        update={
            "messages": [
                AIMessage(content= "Validation failed. Please check your Customer ID and try again.")
            ],
            "validated": False,
            "current_retries": current_retries + 1,
        },
    )


def get_welcome_agent() -> CompiledGraph:
    agent = create_react_agent(
        model= model,
        tools= [validate_customer_id, handle_validation_failure],
        prompt= prompt,
        name= "welcome_agent",
        state_schema= GraphState,
    )

    return agent
