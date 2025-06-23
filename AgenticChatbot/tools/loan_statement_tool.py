from typing import Annotated, Dict, Any
from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.messages.tool import ToolMessage
from langgraph.types import Command
from langgraph.prebuilt import InjectedState
from dateutil.parser import isoparse
from services.loan_service import fetch_loan_statement


@tool(parse_docstring=True)
def get_loan_statement(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[Dict[str, Any], InjectedState],
) -> Command:
    """
    Fetch loan statement, including payment history and loan summary, for a customer.

    Args:
        tool_call_id: Unique identifier for the tool call.
        state: The current state of the conversation, including the customer ID.

    Returns:
         Command: Command with loan statement as ToolMessage.
    """

    print("Transferred to loan_statement_tool")

    customer_id = state["customer"]["customerId"]
    data = fetch_loan_statement(customer_id)
    for p in data.paymentHistory:
        p.paymentDate = isoparse(p.paymentDate)

    if not data.success:
        content = f"Could not fetch loan statement: {', '.join(data.errors or ['Unknown error'])}"
    else:
        summary = data.loanSummary
        payments = sorted(data.paymentHistory or [], key=lambda x: x.paymentDate)
        initial_principal = summary.loanAmount
        interest_rate_annual = summary.interestRate
        interest_rate_monthly = interest_rate_annual / 12 / 100 
        emi = summary.emiAmount
        previous_principal = initial_principal

        content = f"## Loan Statement for Customer ID `{data.customerId}`\n"
        content += f"- **Loan Account Number**: {data.loanAccountNumber}\n"
        content += f"- **Loan Amount**: ₹{initial_principal:,.2f}\n"
        content += f"- **Interest Rate**: {interest_rate_annual}%\n"
        content += f"- **Tenure**: {summary.tenureMonths} months\n"
        content += f"- **EMI Amount**: {emi:,.2f}\n"
        content += f"- **Start Date**: {summary.startDate.strftime('%d-%b-%Y')}\n"
        content += f"- **Status**: {summary.status}\n\n"

        if payments:
            content += "Payment History:\n\n"
            content += "| No. | Payment Date | EMI Paid | Interest | Principal Paid | Prev Principal | Curr Principal | Mode | Txn ID |\n"
            content += "|-----|--------------|----------|----------|----------------|----------------|----------------|------|--------|\n"

            for idx, p in enumerate(payments, 1):
                interest = round(previous_principal * interest_rate_monthly, 2)
                principal_paid = round(emi - interest, 2)
                current_principal = round(previous_principal - principal_paid, 2)

                content += (
                    f"| {idx} | {p.paymentDate.strftime('%d-%b-%Y')} "
                    f"| {emi:,.2f} | {interest:,.2f} | {principal_paid:,.2f} "
                    f"| {previous_principal:,.2f} | {current_principal:,.2f} "
                    f"| {p.paymentMode} | {p.transactionId} |\n"
                )

                previous_principal = current_principal
        else:
            content += "No payments found."

        tool_message = ToolMessage(
            content=content,
            name="get_loan_statement",
            tool_call_id=tool_call_id,
        )

    return Command(
    update={
        "messages": [tool_message], 
        "answer": content,
    },
    graph=Command.PARENT,
)
