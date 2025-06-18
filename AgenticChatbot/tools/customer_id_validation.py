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
def validate_customer_id(customer_id: str, tool_call_id: Annotated[str, InjectedToolCallId], state: Annotated[Dict[str, Any], InjectedState]) -> Command:
    """
    Makes a RESTful Get API request to a database & checks for existence the existence of the customer in the collection on the basis of Customer Id provided. 
    Returns the details of the customer parsed as a Customer pydantic model if the customer exists in the collection or a string describing the errors raised when customer is not found.

    Args:
        customer_id (str): the customer Id to be looked up in the collection
        tool_call_id (str): the id injected into into the tool call by the caller agent
        state: A state object containing relevant metadata that serves as short-term memory checkpointer for the agent
    """


    print(f"Validating customer id {customer_id}")

    context = ssl.create_default_context(cafile= certifi.where())
    headers = {"customerId": customer_id}
    response = requests.get(Endpoints.GET_CUSTOMER_BY_ID, headers= headers, verify= False)

    if response.status_code == 200:
        customer = Customer(**response.json()['customer'])
        tool_content = f"The customer was succesfully validated. Name: {customer.customerName} with CustomerId: {customer.customerId}"
        tool_message = ToolMessage(content= tool_content, tool_call_id= tool_call_id)
        
        command = Command(update= {
            "messages": [
                tool_message
            ],
            "customer": customer.model_dump(mode= 'json'),
            "validated": True
        })
    else:
        status = response.status_code
        errors = '\t'.join(response.json()['errors'])
        tool_content =  f"The customer could not be validated. Status code: {status}. Errors: {errors}"
        tool_message = ToolMessage(content= tool_content, tool_call_id= tool_call_id)
        
        command = Command(update= {
            "messages": [
                tool_message
            ],
            "customer": None,
            "validated": False
        })
    
    
    return command