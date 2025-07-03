from typing import Annotated, Dict, Any
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from dateutil.parser import isoparse
from services.loan_service import fetch_loan_statement
from datetime import datetime

@tool(parse_docstring=True,return_direct=True)
def get_loan_statement(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[Dict[str, Any], InjectedState],
) -> str:
    """
    Fetch and return the loan statement for the current customer.

    This tool retrieves loan-related details for the customer whose ID is 
    available in the injected LangGraph state. It is designed to be used 
    by an agent that has access to the current session's context.

    Args:
        tool_call_id (str): 
            The ID injected into the tool call by the caller agent.
        state (Dict[str, Any]): 
            The current injected LangGraph state. It must contain a 
            dictionary with a 'customer' key that includes the 'customerId'.

    Returns:
        str: A formatted string containing the loan statement details
    """
    print("Transferred to loan_statement_tool")

    customer_id = state["customer"]["customerId"]
    data = fetch_loan_statement(customer_id)

    for p in data.paymentHistory:
        if not isinstance(p.paymentDate, datetime):
            p.paymentDate = isoparse(p.paymentDate)

    if not data.success:
        statement_text = f"Could not fetch loan statement: {', '.join(data.errors or ['Unknown error'])}"
    else:
        print(f"Fetched loan statement for customer {data.customerId}")
        summary = data.loanSummary
        payments_raw = sorted(data.paymentHistory or [], key=lambda x: x.paymentDate)
        initial_principal = summary.loanAmount
        interest_rate_annual = summary.interestRate
        emi = summary.emiAmount
        summary_lines = [
            f"Loan Account Number: {data.loanAccountNumber}",
            f"Loan Amount: ${initial_principal:,.2f}",
            f"Interest Rate: {interest_rate_annual}%",
            f"Tenure: {summary.tenureMonths} months",
            f"EMI Amount: ${emi:,.2f}",
            f"Start Date: {summary.startDate.strftime('%d-%b-%Y')}",
            f"Status: {summary.status}",
        ]

        statement_text = f"## Loan Statement for Customer ID `{data.customerId}`\n"
        statement_text += "\n".join(summary_lines) + "\n\n"
        statement_text += "Payment History:\n\n"
        statement_text += "| No. | Date | EMI | Interest | Principal | Prev | Curr | Mode | Txn ID |\n"
        statement_text += "|-----|------|-----|----------|-----------|------|------|------|--------|\n"

        for idx, p in enumerate(payments_raw, 1):
            statement_text += (
                f"| {idx} | {p.paymentDate.strftime('%d-%b-%Y')} | ${p.paymentAmount:,.2f} | "
                f"${p.interestPaid:,.2f} | ${p.principalPaid:,.2f} | "
                f"${p.previousPrincipal:,.2f} | ${p.currentPrincipal:,.2f} | "
                f"{p.paymentMode} | {p.transactionId} |\n"
            )
    return statement_text
