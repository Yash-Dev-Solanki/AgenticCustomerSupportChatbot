from langchain_openai import ChatOpenAI
from langchain_core.tools import tool, InjectedToolCallId
from dotenv import load_dotenv, find_dotenv
import os
from pydantic import SecretStr
from langgraph.prebuilt import create_react_agent, InjectedState
from langgraph.graph.graph import CompiledGraph
from langgraph.graph import END
from langgraph.types import Command
from models.graphState import GraphState
from tools.check_customer_id import check_customer_id
from tools.verify_customer_id import verify_customer_id
from typing import (
    Annotated, 
    Dict, 
    Any
)
from langchain_core.messages import ToolMessage


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
- When customer provides ID, use check_customer_id tool to check if the ID exists in the database.
- If the ID exists, use verify_customer_id tool to validate the customer ID against provided phone number. This phone number can be either homePhone or workPhone
- If validation is successful, call the customer by their name and provide a summary of their account.
- If validation fails, call the validation_failure tool to handle the failure.

TOOLS:
- check_customer_id: Checks if the provided customer ID is present in the customer database.
- verify_customer_id: Verifies the customer ID and phone number to validate the customer.
- handle_validation_failure: Handles the case when customer ID validation fails.
"""


@tool(parse_docstring= True)
def handle_validation_failure(tool_call_id: Annotated[str, InjectedToolCallId], state: Annotated[Dict[str, Any], InjectedState]) -> Command:
    '''
    Handles the case when customer ID validation fails.

    Args:
        tool_call_id (str): the id injected into into the tool call by the caller agent
        state: A state object containing relevant metadata that serves as short-term memory checkpointer for the agent
    '''
    current_retries = state["current_retries"]
    max_retries = state["validation_retries"]
    print(f"Current retries: {current_retries}, Max retries: {max_retries}")

    if current_retries == max_retries:
        return Command(
            update={
                "messages": [
                    ToolMessage(content= "Maximum validation attempts reached. Please contact support.", tool_call_id= tool_call_id)
                ],
                "validated": False,
            },
        )
    
    return Command(
        update={
            "messages": [
                ToolMessage(content= "Validation failed. Please check your Customer ID and try again.", tool_call_id= tool_call_id)
            ],
            "validated": False,
            "current_retries": current_retries + 1
        },
    )



def get_welcome_agent() -> CompiledGraph:
    agent = create_react_agent(
        model= model,
        tools= [check_customer_id, verify_customer_id, handle_validation_failure],
        prompt= prompt,
        name= "welcome_agent",
        state_schema= GraphState,
    )

    return agent
