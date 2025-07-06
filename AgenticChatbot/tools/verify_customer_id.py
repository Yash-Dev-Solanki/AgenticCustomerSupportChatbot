from endpoints import Endpoints
from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.messages.tool import ToolMessage
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from typing import Annotated, Dict, Any
from models.customer import Customer
import requests
import certifi
import ssl
import urllib3
urllib3.disable_warnings()

@tool(parse_docstring=True)
def verify_customer_id(customer_id: str, phoneInfoLastFourDigits: str, tool_call_id: Annotated[str, InjectedToolCallId], state: Annotated[Dict[str, Any], InjectedState]) -> Command:
    """
    Makes a RESTful Get API request to a database & checks for existence the existence of the customer in the collection on the basis of Customer Id provided. 
    Returns the details of the customer parsed as a Customer pydantic model if the customer exists in the collection or a string describing the errors raised when customer is not found.

    Args:
        customer_id (str): the customer Id to be looked up in the collection
        phoneInfoLastFourDigits (str): the last four digits of the customer's phone number to verify identity
        tool_call_id (str): the id injected into into the tool call by the caller agent
        state: A state object containing relevant metadata that serves as short-term memory checkpointer for the agent
    """

    context = ssl.create_default_context(cafile= certifi.where())
    headers = {"customerId": customer_id, "phoneInfoLastFourDigits": phoneInfoLastFourDigits}
    response = requests.get(Endpoints.VERIFY_CUSTOMER_ID, headers= headers, verify=False)

    if response.status_code == 200:
        customer = Customer(**response.json()['customer'])
        print(customer.model_dump(mode='json'))
        tool_content = f"The customer was successfully validated. Name: {customer.customerName} with CustomerId: {customer.customerId}"
        tool_message = ToolMessage(content= tool_content, tool_call_id=tool_call_id)
        
        command = Command(update={
            "messages": [tool_message],
            "customer": customer.model_dump(mode= 'json'),
            "validated": True
        })
    else:
        status = response.status_code
        errors = '\t'.join(response.json().get('errors'))
        tool_content = f"The customer could not be validated. Status code: {status}. Errors: {errors}"
        tool_message = ToolMessage(content= tool_content, tool_call_id= tool_call_id)
        
        command = Command(update={
            "messages": [tool_message],
            "customer": None,
            "validated": False,
        })

    return command