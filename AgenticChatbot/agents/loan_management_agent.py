from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from dotenv import load_dotenv
import os

from tools.loan_management_tools import (
    get_outstanding_balance,
    get_loan_closure_amount,
    simulate_tenure_reduction,
    simulate_part_payment_impact,
)

from models.graphState import GraphState

load_dotenv()

model = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    streaming=True,
    api_key=SecretStr(os.getenv('OPENAI_API_KEY', ''))
)

def get_loan_management_agent():
    agent = create_react_agent(
        model=model,
        tools=[
            get_outstanding_balance,
            get_loan_closure_amount,
            simulate_tenure_reduction,
            simulate_part_payment_impact,
        ],
        prompt=(
            """You are a helpful and specialized loan management assistant.

            You are allowed to use ONLY the following tools:
            - `get_outstanding_balance`
            - `get_loan_closure_amount`
            - `simulate_tenure_reduction`
            - `simulate_part_payment_impact`

            Your job is to help customers manage their loan by calling the appropriate tool
            based on what the user says.

            INSTRUCTIONS:
            - If the user asks how much loan is remaining, balance, or outstanding amount,
              call `get_outstanding_balance`.

            - If they want to know how much they need to pay to close the loan,
              including interest and foreclosure charges, call `get_loan_closure_amount`.

            - If they want to reduce the tenure and want to know how their EMI will change,
              call `simulate_tenure_reduction`. Make sure `tenure_reduction_months` is provided.

            - If they mention part payment, lump sum, or want to reduce EMI or tenure by paying extra,
              call `simulate_part_payment_impact`. Make sure `part_payment` is provided.

            RULES:
            - Do not reply directly.
            - Always call the tool directly when you detect a relevant request.
            - Do not ask for clarification unless absolutely required.
            - If you don't have required input (like part_payment or tenure_reduction_years), ask for it.
            - Stop after one tool call. Return control to the supervisor or user.

            Your responses must only be tool calls or minimal clarifying questions.
            """
        ),
        name="loan_management_agent",
        state_schema=GraphState,
    )
    return agent
