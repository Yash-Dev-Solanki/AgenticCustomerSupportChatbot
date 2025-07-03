from click import command
from models.customer import Customer
from endpoints import Endpoints

from typing import (
    Annotated,
    Dict,
    Any
)
from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.messages.tool import ToolMessage
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
import requests
import urllib3
urllib3.disable_warnings()

@tool(parse_docstring=True)  
def update_customer_email(
    email_address: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[Dict[str, Any], InjectedState]
) -> Command:
    """
    Updates the email address of a customer in the accounts collection via a RESTful API call.

    This tool sends a POST request to the configured customer update endpoint, updating
    the customer's email based on their unique customer ID. Upon successful update,
    the updated customer object is returned along with a confirmation message.
    In case of failure, an error message is generated and returned instead.

    Args:
        email_address (str): The new email address to be set for the customer.
        tool_call_id (str): The tool call ID injected by the calling agent, used for traceability.
        state (Dict[str, Any]): A short-term memory state passed by the LangGraph system, containing metadata like previous messages.

    Returns:
        Command: A LangGraph `Command` object containing either the updated customer and a success message,
                 or an error message if the update failed.
    """
    customer_id = state["customer"]["customerId"]
    try:
        headers = {"customerId": customer_id, "newEmailAddress": email_address}
        response = requests.post(Endpoints.UPDATE_CUSTOMER_EMAIL, headers=headers, verify=False)
    except Exception as e:
        error_msg = f"[ERROR] Exception during API call: {e}"
        tool_message = ToolMessage(content=error_msg, tool_call_id=tool_call_id)
        return Command(update={"messages": state["messages"] + [tool_message], "is_last_step": True})

    if response.status_code == 202:
        customer = Customer(**response.json()['customer'])
        tool_content = f"The customer email for Id {customer.customerId} has been updated to {customer.emailAddress}"
        tool_message = ToolMessage(content=tool_content, tool_call_id=tool_call_id)
        return Command(update={
            "messages": state['messages'] + [tool_message],
            "customer": customer,
            "is_last_step": True
        })
    else:
        status = response.status_code
        errors = '\t'.join(response.json().get('errors', []))
        tool_content = f"The customer email could not be updated. Status code: {status}. Errors: {errors}"
        tool_message = ToolMessage(content=tool_content, tool_call_id=tool_call_id)
        return Command(update={
            "messages": state["messages"] + [tool_message],
            "is_last_step": True
        })



@tool(parse_docstring= True)
def update_customer_payment_reminder( payment_reminder: bool, tool_call_id: Annotated[str, InjectedToolCallId], state: Annotated[Dict[str, Any], InjectedState]) -> Command:
    """
    Makes a RESTful Post API request to a database client to update the payment reminder of a customer in the accounts collection which signifies whether a customer has opted into payment reminders. The customer is identified in the collection using the customer id field. 
    Returns the details of the customer after the update is complete with a status code of 202 if the update operation is successful. Otherwise, returns a list of errors on why the operation failed.

    Args:
        payment_reminder (str): whether the customer wishes to opt into payment reminders
        tool_call_id (str): the id injected into into the tool call by the caller agent
        state: A state object containing relevant metadata that serves as short-term memory checkpointer for the agent
    """
    customer_id = state["customer"]["customerId"]
    headers = {"customerId": customer_id, "newPaymentReminder": "true" if payment_reminder else "false"}
    print(headers)
    response = requests.post(Endpoints.UPDATE_CUSTOMER_PAYMENT_REMINDER, headers= headers, verify= False)

    if response.status_code == 202:
        print("Updated")
        customer = Customer(**response.json()['customer'])
        tool_content = f"The customer payment reminder status details for Id {customer.customerId} has been updated to {customer.paymentReminder}"
        tool_message = ToolMessage(content= tool_content, tool_call_id= tool_call_id)
        command = Command(update= {
            "messages": state['messages'] + [tool_message],
            "customer": customer,
            "is_last_step": True
        })
    else:
        print("Not updated")
        status = response.status_code
        errors = '\t'.join(response.json()['errors'])
        tool_content = f"The customer payment reminder status could not be updated. Status code: {status}. Errors: {errors}"
        tool_message = ToolMessage(content= tool_content, tool_call_id= tool_call_id)
        command = Command(update= {
            "messages": state["messages"] + [tool_message],
            "is_last_step": True
        })
        
    return command