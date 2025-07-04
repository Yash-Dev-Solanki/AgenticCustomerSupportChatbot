from typing import Annotated, Dict, Any
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from dateutil.parser import isoparse
from services.loan_service import fetch_loan_statement
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from pydantic import SecretStr
import os
import json

load_dotenv()
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    streaming=True,
    api_key=SecretStr(os.getenv('OPENAI_API_KEY', ''))
)

@tool(parse_docstring=True, return_direct=True)
def get_loan_statement(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[Dict[str, Any], InjectedState],
) -> str:
    """
    Fetch and return the loan statement for the current customer using LLM formatting.
    Includes a Markdown table for display and raw JSON array for backend use.

    Args:
        tool_call_id (str): Tool call ID injected by LangGraph.
        state (Dict[str, Any]): Current LangGraph state with customerId.

    Returns:
        str: A formatted loan statement with summary, Markdown table, and raw JSON array.
    """
    print("Transferred to loan_statement_tool")

    customer_id = state["customer"]["customerId"]
    data = fetch_loan_statement(customer_id)

    if data.paymentHistory:
        for p in data.paymentHistory: 
            if not isinstance(p.paymentDate, datetime):
                p.paymentDate = isoparse(p.paymentDate)

    if not data.success:
        return f"Could not fetch loan statement: {', '.join(data.errors or ['Unknown error'])}"

    print(f"Fetched loan statement for customer {data.customerId}")

    loan_input = {
        "customerId": data.customerId,
        "loanAccountNumber": data.loanAccountNumber,
        "summary": {
            "loanAmount": data.loanSummary.loanAmount,
            "interestRate": data.loanSummary.interestRate,
            "tenureMonths": data.loanSummary.tenureMonths,
            "emiAmount": data.loanSummary.emiAmount,
            "startDate": data.loanSummary.startDate.strftime('%Y-%m-%d'),
            "status": data.loanSummary.status
        },
        "paymentHistory": [
            {
                "date": p.paymentDate.strftime('%Y-%m-%d'),
                "paymentAmount": p.paymentAmount,
                "interestPaid": p.interestPaid,
                "principalPaid": p.principalPaid,
                "previousPrincipal": p.previousPrincipal,
                "currentPrincipal": p.currentPrincipal,
                "paymentMode": p.paymentMode,
                "transactionId": p.transactionId,
            }
            for p in sorted(data.paymentHistory or [], key=lambda x: x.paymentDate)
        ]
    }

    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are a helpful financial assistant.
        
        Given the following loan JSON data:
        1. Generate a loan summary in plain readable text (no markdown headers or bullet points).
        2. Then generate a payment history **Markdown table**.
           Use columns: No., Date, EMI, Interest, Principal, Prev, Curr, Mode, Txn ID.
        3. After the table, on a new line, include only the **raw JSON array** of payment records.
           Do not explain or format the JSON in any way.
        4. All currency must be formatted as US dollars (e.g. $10,000.00).
        """),
        ("human", "{input}")
    ])

    chain = prompt | llm
    return chain.invoke({"input": json.dumps(loan_input)})
