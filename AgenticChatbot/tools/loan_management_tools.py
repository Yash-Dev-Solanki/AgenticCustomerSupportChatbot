from typing import Annotated, Dict, Any
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from dateutil.parser import isoparse
from datetime import datetime
from services.loan_service import fetch_loan_statement
import math

@tool(parse_docstring=True, return_direct=True)
def get_outstanding_balance(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[Dict[str, Any], InjectedState],
) -> str:
    """
    Fetch and return the current outstanding principal (loan balance) 
    for the customer whose ID is stored in state.

    This tool accesses the latest loan payment, and extracts the 
    currentPrincipal, which is considered the remaining balance.
    
    Args:
        tool_call_id (str): ID injected by the agent.
        state (Dict[str, Any]): Injected LangGraph state, must contain 
            state['customer']['customerId'].

    Returns:
        str: A human-readable message showing outstanding principal.
    """
    print("Transferred to outstanding_balance_tool")

    customer_id = state["customer"]["customerId"]
    data = fetch_loan_statement(customer_id)

    if not data.success:
        return f"Could not fetch loan data: {', '.join(data.errors or ['Unknown error'])}"

    if not data.paymentHistory:
        return "No payment history found for this customer."

    for p in data.paymentHistory:
        if not isinstance(p.paymentDate, datetime):
            p.paymentDate = isoparse(p.paymentDate)

    latest_payment = max(data.paymentHistory, key=lambda p: p.paymentDate)
    balance = latest_payment.currentPrincipal
    date = latest_payment.paymentDate.strftime('%d-%b-%Y')

    return (
        f"As of {date}, your current outstanding loan balance is ${balance:,.2f}."
    )

@tool(parse_docstring=True, return_direct=True)
def get_loan_closure_amount(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[Dict[str, Any], InjectedState],
) -> str:
    """
    Calculates the amount required to close the loan as of today.
    This includes the outstanding principal, one month of interest, and foreclosure charges.
    
    Args:
        tool_call_id (str): Tool call ID (injected)
        state (Dict[str, Any]): LangGraph state with customer['customerId']

    Returns:
        str: Closure amount with breakdown
    """
    print("Transferred to loan_closure_tool")

    customer_id = state["customer"]["customerId"]
    data = fetch_loan_statement(customer_id)

    if not data.success:
        return f"Could not fetch loan data: {', '.join(data.errors or ['Unknown error'])}"

    if not data.paymentHistory:
        return "No payment history found for this customer."

    for p in data.paymentHistory:
        if not isinstance(p.paymentDate, datetime):
            p.paymentDate = isoparse(p.paymentDate)

    latest_payment = max(data.paymentHistory, key=lambda p: p.paymentDate)
    summary = data.loanSummary

    outstanding_principal = latest_payment.currentPrincipal

    annual_interest_rate = summary.interestRate / 100
    monthly_interest_rate = annual_interest_rate / 12
    one_month_interest = outstanding_principal * monthly_interest_rate

    foreclosure_fee_percent = 0.02
    foreclosure_fee = outstanding_principal * foreclosure_fee_percent

    total_closure_amount = outstanding_principal + one_month_interest + foreclosure_fee

    today = datetime.today().strftime('%d-%b-%Y')

    return (
        f"To close your loan as of {today}, you need to pay ${total_closure_amount:,.2f}.\n\n"
        f"Breakdown:\n"
        f"- Outstanding Principal: ${outstanding_principal:,.2f}\n"
        f"- Interest for 1 month: ${one_month_interest:,.2f}\n"
        f"- Foreclosure Charges (2%): ${foreclosure_fee:,.2f}"
    )
    
@tool(parse_docstring=True, return_direct=True)
def simulate_tenure_reduction(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[Dict[str, Any], InjectedState],
    tenure_reduction_months: int,
) -> str:
    """
    Simulates EMI change when the user reduces their loan tenure by X months.

    Args:
        tool_call_id (str): ID from the agent context
        state (Dict[str, Any]): LangGraph injected state (must contain customerId)
        tenure_reduction_months (int): The number of months by which tenure will be reduced

    Returns:
        str: A message showing the new EMI and increase compared to the current EMI
    """
    print("Transferred to tenure_reduction_tool")

    customer_id = state["customer"]["customerId"]

    if not isinstance(tenure_reduction_months, int) or tenure_reduction_months <= 0:
        return "Please provide a valid positive number of months to reduce the tenure."

    data = fetch_loan_statement(customer_id)

    if not data.success or not data.paymentHistory:
        return "Could not fetch loan data or payment history is missing."

    for p in data.paymentHistory:
        if not isinstance(p.paymentDate, datetime):
            p.paymentDate = isoparse(p.paymentDate)

    latest_payment = max(data.paymentHistory, key=lambda p: p.paymentDate)
    summary = data.loanSummary

    principal = latest_payment.currentPrincipal
    annual_rate = summary.interestRate / 100
    monthly_rate = annual_rate / 12

    current_emi = summary.emiAmount
    current_tenure_months = summary.tenureMonths

    new_tenure_months = max(current_tenure_months - tenure_reduction_months, 1)

    numerator = principal * monthly_rate * (1 + monthly_rate) ** new_tenure_months
    denominator = (1 + monthly_rate) ** new_tenure_months - 1
    new_emi = numerator / denominator

    emi_increase = new_emi - current_emi

    return (
        f"If you reduce your tenure by {tenure_reduction_months} month(s), "
        f"your EMI will increase from ${current_emi:,.2f} to ${new_emi:,.2f}.\n"
        f"That's an increase of ${emi_increase:,.2f} per month."
    )
    
@tool(parse_docstring=True, return_direct=True)
def simulate_part_payment_impact(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[Dict[str, Any], InjectedState],
    part_payment: float,
) -> str:
    """
    Simulates how a part payment affects the loan:
    - Option 1: Reduce EMI (keep tenure same)
    - Option 2: Reduce Tenure (keep EMI same)

    Args:
        tool_call_id (str): Tool call ID
        state (Dict[str, Any]): LangGraph state with customer['customerId']
        part_payment (float): The lump sum part payment amount

    Returns:
        str: A report showing the new EMI or new tenure based on the user's part payment
    """
    print("Transferred to part_payment_simulation_tool")

    customer_id = state["customer"]["customerId"]

    if part_payment <= 0:
        return "Please enter a valid part payment greater than zero."

    data = fetch_loan_statement(customer_id)

    if not data.success or not data.paymentHistory:
        return "Could not fetch loan data or payment history is missing."

    for p in data.paymentHistory:
        if not isinstance(p.paymentDate, datetime):
            p.paymentDate = isoparse(p.paymentDate)

    latest_payment = max(data.paymentHistory, key=lambda p: p.paymentDate)
    summary = data.loanSummary

    old_principal = latest_payment.currentPrincipal
    new_principal = old_principal - part_payment

    if new_principal <= 0:
        return "The part payment exceeds the outstanding loan. Please enter a lower amount."

    rate_annual = summary.interestRate / 100
    rate_monthly = rate_annual / 12
    current_emi = summary.emiAmount
    current_tenure_months = summary.tenureMonths

    # Option 1: Reduce EMI (same tenure)
    numerator = new_principal * rate_monthly * (1 + rate_monthly) ** current_tenure_months
    denominator = (1 + rate_monthly) ** current_tenure_months - 1
    new_emi = numerator / denominator
    emi_diff = current_emi - new_emi
    try:
        new_tenure_months = math.log(
            current_emi / (current_emi - new_principal * rate_monthly)
        ) / math.log(1 + rate_monthly)
        tenure_saved = current_tenure_months - new_tenure_months
    except ValueError:
        return "The current EMI is too low to support this part payment at current rate."
    return (
        f"If you make a part payment of ${part_payment:,.2f}, here's how your loan will be affected:\n\n"
        f"Your EMI will reduce from ${current_emi:,.2f} to ${new_emi:,.2f}, saving ${emi_diff:,.2f} every month,\n"
        f"**or**\n"
        f"You can keep the same EMI of ${current_emi:,.2f} and close your loan "
        f"{math.floor(tenure_saved)} months earlier "
        f"({math.floor(tenure_saved // 12)} year(s), {math.floor(tenure_saved % 12)} month(s)) sooner."
    )
