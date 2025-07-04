from typing import Annotated, Dict, Any
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from dateutil.parser import isoparse
from datetime import datetime
from services.loan_service import fetch_loan_statement
import math
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from pydantic import SecretStr
import os

load_dotenv()
llm = ChatOpenAI(model= "gpt-4o",
                   temperature= 0,
                   streaming= True,
                   api_key= SecretStr(os.getenv('OPENAI_API_KEY', ''))
        )

def run_financial_calculator(prompt_instruction: str, user_data: dict) -> str:
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_instruction),
        ("human", "{input}")
    ])
    chain = prompt | llm
    return chain.invoke({"input": user_data})


@tool(parse_docstring=True, return_direct=True)
def get_outstanding_balance(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[Dict[str, Any], InjectedState],
) -> str:
    """
    Retrieve and explain the customer's current outstanding loan balance using an LLM.

    This tool fetches the latest loan payment data and uses a language model
    to generate a user-friendly summary of the current outstanding principal.

    Args:
        tool_call_id (str): Tool call identifier injected by LangGraph.
        state (Dict[str, Any]): Injected state from LangGraph. Must include
            'customer' key with 'customerId'.

    Returns:
        str: A formatted message describing the customer's outstanding balance.
    """

    customer_id = state["customer"]["customerId"]
    data = fetch_loan_statement(customer_id)

    if not data.success or not data.paymentHistory:
        return "Loan data unavailable or no payment history found."

    for p in data.paymentHistory:
        if not isinstance(p.paymentDate, datetime):
            p.paymentDate = isoparse(p.paymentDate)

    latest = max(data.paymentHistory, key=lambda p: p.paymentDate)
    input_data = {
        "customerId": data.customerId,
        "paymentDate": latest.paymentDate.strftime('%Y-%m-%d'),
        "currentPrincipal": latest.currentPrincipal
    }

    return run_financial_calculator(
        """You are a financial assistant. 
        Format all currency in US dollars ($) with commas and 2 decimal places (e.g., $12,345.67).
        Given the payment date and outstanding principal, generate a user-friendly summary of the current loan balance.""",
        input_data
    )

@tool(parse_docstring=True, return_direct=True)
def get_loan_closure_amount(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[Dict[str, Any], InjectedState],
) -> str:
    """
    Calculate and explain the total amount required to close the customer's loan.

    The tool fetches the current outstanding principal, estimates one month of interest,
    and adds foreclosure charges. These values are passed to a language model, which
    generates a breakdown of the total closure amount.

    Args:
        tool_call_id (str): Tool call identifier injected by LangGraph.
        state (Dict[str, Any]): Injected LangGraph state. Must contain 'customer.customerId'.

    Returns:
        str: A markdown-formatted message with total closure amount and its breakdown.
    """

    customer_id = state["customer"]["customerId"]
    data = fetch_loan_statement(customer_id)

    if not data.success or not data.paymentHistory:
        return "Loan data unavailable or no payment history found."

    for p in data.paymentHistory:
        if not isinstance(p.paymentDate, datetime):
            p.paymentDate = isoparse(p.paymentDate)

    latest = max(data.paymentHistory, key=lambda p: p.paymentDate)
    summary = data.loanSummary

    input_data = {
        "customerId": data.customerId,
        "asOfDate": datetime.today().strftime('%Y-%m-%d'),
        "outstandingPrincipal": latest.currentPrincipal,
        "interestRate": summary.interestRate,
        "foreclosureChargePercent": 2
    }

    return run_financial_calculator(
        """
        You are a financial assistant. Given the outstanding principal, annual interest rate, and foreclosure charge percent:
        - Calculate one month of interest using simple interest formula.
        - Calculate foreclosure fee.
        - Sum all to get total closure amount.
        - Return a readable breakdown in markdown.
        - Format and return all amounts in **US dollars ($)** with two decimal places and commas.
        """,
        input_data
    )

@tool(parse_docstring=True, return_direct=True)
def simulate_tenure_reduction(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[Dict[str, Any], InjectedState],
    tenure_reduction_months: int,
) -> str:
    """
    Simulate EMI increase if the loan tenure is reduced.

    This tool allows the customer to explore how their EMI would change
    if they chose to shorten their loan duration. The calculation is performed
    by the LLM based on the current principal, interest rate, and remaining tenure.

    Args:
        tool_call_id (str): Tool call identifier from the calling agent.
        state (Dict[str, Any]): LangGraph state containing customer ID.
        tenure_reduction_months (int): Number of months by which the user wants to reduce tenure.

    Returns:
        str: A message comparing the old and new EMI after tenure reduction.
    """

    if tenure_reduction_months <= 0:
        return "Please enter a valid number of months."

    customer_id = state["customer"]["customerId"]
    data = fetch_loan_statement(customer_id)

    if not data.success or not data.paymentHistory:
        return "Loan data unavailable or no payment history found."

    for p in data.paymentHistory:
        if not isinstance(p.paymentDate, datetime):
            p.paymentDate = isoparse(p.paymentDate)

    latest = max(data.paymentHistory, key=lambda p: p.paymentDate)
    summary = data.loanSummary

    input_data = {
        "principal": latest.currentPrincipal,
        "currentEMI": summary.emiAmount,
        "currentTenure": summary.tenureMonths,
        "interestRate": summary.interestRate,
        "reduceBy": tenure_reduction_months
    }

    return run_financial_calculator(
        """
        You are a financial advisor.
        Given current principal, annual interest rate, and requested reduction in tenure (in months):
        - Calculate new EMI after tenure reduction using EMI formula.
        - Compare old and new EMI.
        - Return a markdown response with comparison and increase in EMI.
        - Format all currency in **US dollars ($)** with commas and 2 decimal places.
        """,
        input_data
    )

@tool(parse_docstring=True, return_direct=True)
def simulate_part_payment_impact(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[Dict[str, Any], InjectedState],
    part_payment: float,
) -> str:
    """
    Simulate the impact of a part payment on EMI and tenure.

    The tool evaluates two scenarios:
    - Option 1: Reduce EMI and keep the same tenure.
    - Option 2: Keep EMI the same and reduce the remaining tenure.

    The LLM calculates the impact of the lump-sum payment on both options
    and presents the results in a markdown-formatted message.

    Args:
        tool_call_id (str): Tool call identifier injected by LangGraph.
        state (Dict[str, Any]): LangGraph state with current customer context.
        part_payment (float): The lump sum amount to reduce the outstanding principal.

    Returns:
        str: A message showing the impact on EMI and tenure after part payment.
    """

    if part_payment <= 0:
        return "Please enter a valid part payment amount."

    customer_id = state["customer"]["customerId"]
    data = fetch_loan_statement(customer_id)

    if not data.success or not data.paymentHistory:
        return "Loan data unavailable or no payment history found."

    for p in data.paymentHistory:
        if not isinstance(p.paymentDate, datetime):
            p.paymentDate = isoparse(p.paymentDate)

    latest = max(data.paymentHistory, key=lambda p: p.paymentDate)
    summary = data.loanSummary

    input_data = {
        "originalPrincipal": latest.currentPrincipal,
        "partPayment": part_payment,
        "interestRate": summary.interestRate,
        "emi": summary.emiAmount,
        "tenureMonths": summary.tenureMonths
    }

    return run_financial_calculator(
        """
        You are a financial assistant. Given a part payment scenario:
        - Reduce the principal.
        - Show Option 1: Recalculate EMI (same tenure).
        - Show Option 2: Recalculate tenure (same EMI).
        - Return a markdown message with both options and savings.
        - Format everything in **US dollars ($)**.
        """,
        input_data
    )
