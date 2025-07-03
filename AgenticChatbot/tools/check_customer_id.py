from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from endpoints import Endpoints
from typing import Union
import requests
import certifi
import ssl
import urllib3
urllib3.disable_warnings()

@tool(parse_docstring= True)
def check_customer_id(customer_id: str) -> Union[bool, str]:
    """
    Checks if the provided customer ID is present in the customer database.
    
    Args:
        customer_id (str): The customer ID to validate.
    """

    context = ssl.create_default_context(cafile= certifi.where())
    headers = {"customerId": customer_id}
    response = requests.get(Endpoints.CHECK_CUSTOMER_ID, headers= headers, verify= False)

    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        return False
    else:
        status = response.status_code
        errors = '\t'.join(response.json().get('errors', ['Unknown error']))
        return f"Customer ID check failed. Status code: {status}. Errors: {errors}"

