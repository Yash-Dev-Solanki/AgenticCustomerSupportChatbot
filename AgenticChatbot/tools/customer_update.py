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
import certifi
import ssl
import urllib3
urllib3.disable_warnings()

@tool(parse_docstring= True)
def update_customer_email(customer_id: str, email_address: str, tool_call_id: Annotated[str, InjectedToolCallId], state: Annotated[Dict[str, Any], InjectedState]) -> Command:
    """
    Makes a RESTful Post API request to a database client to update the email address of a customer in the accounts collection. The customer is identified in the collection using the customer id field. 
    Returns the details of the customer after the update is complete with a status code of 202 if the update operation is successful. Otherwise, returns a list of errors on why the operation failed.

    Args:
        customer_id (str): the customer Id to be looked up in the collection
        email_address (str): the new email address of the customer
        tool_call_id (str): the id injected into into the tool call by the caller agent
        state: A state object containing relevant metadata that serves as short-term memory checkpointer for the agent
    """

    context = ssl.create_default_context(cafile= certifi.where())
    headers = {"customerId": customer_id, "newEmailAddress": email_address}
    response = requests.post(Endpoints.UPDATE_CUSTOMER_EMAIL, headers= headers, verify= False)

    if response.status_code == 202:
        customer = Customer(**response.json()['customer'])
        tool_content = f"The customer email for Id {customer.customerId} has been updated to {customer.emailAddress}"
        tool_message = ToolMessage(content= tool_content, tool_call_id= tool_call_id)
        command = Command(update= {
            "messages": state['messages'] + [tool_message],
            "customer": customer.model_dump(mode= 'json'),
        })
    else:
        status = response.status_code
        errors = '\t'.join(response.json()['errors'])
        tool_content = f"The customer email could not be updated. Status code: {status}. Errors: {errors}"
        tool_message = ToolMessage(content= tool_content, tool_call_id= tool_call_id)
        command = Command(update= {
            "messages": state["messages"] + [tool_message]
        })
        
    return command


@tool(parse_docstring= True)
def update_customer_payment_reminder(customer_id: str, payment_reminder: bool, tool_call_id: Annotated[str, InjectedToolCallId], state: Annotated[Dict[str, Any], InjectedState]) -> Command:
    """
    Makes a RESTful Post API request to a database client to update the payment reminder of a customer in the accounts collection which signifies whether a customer has opted into payment reminders. The customer is identified in the collection using the customer id field. 
    Returns the details of the customer after the update is complete with a status code of 202 if the update operation is successful. Otherwise, returns a list of errors on why the operation failed.

    Args:
        customer_id (str): the customer Id to be looked up in the collection
        payment_reminder (bool): whether the customer wishes to opt into payment reminders
        tool_call_id (str): the id injected into into the tool call by the caller agent
        state: A state object containing relevant metadata that serves as short-term memory checkpointer for the agent
    """

    context = ssl.create_default_context(cafile= certifi.where())
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
            "customer": customer.model_dump(mode= 'json'),
        })
    else:
        print("Not updated")
        status = response.status_code
        errors = '\t'.join(response.json()['errors'])
        tool_content = f"The customer payment reminder status could not be updated. Status code: {status}. Errors: {errors}"
        tool_message = ToolMessage(content= tool_content, tool_call_id= tool_call_id)
        command = Command(update= {
            "messages": state["messages"] + [tool_message]
        })
        
    return command