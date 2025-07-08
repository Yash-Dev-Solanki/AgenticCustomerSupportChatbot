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
def check_customer(customer_id: str= "", SSN: str= "") -> str:
    """
    Checks if the provided customer ID is present in the customer database.
    
    Args:
        customer_id (str): The customer ID to validate. 
        SSN (str): The Social Security Number to validate. 
    """

    context = ssl.create_default_context(cafile= certifi.where())
    print(f"Checking customer with ID: {customer_id} and SSN: {SSN}")
    headers = {"customerId": customer_id, "SSN": SSN}
    response = requests.get(Endpoints.CHECK_CUSTOMER_ID, headers= headers, verify= False)
    data = response.json()
    print(f"Response from check_customer: {data}")
    if response.status_code == 200:
        return f"Customer was successfully validated. The customerId is {data['customerId']}"
    elif response.status_code == 404:
        return "Customer ID not found in the database. Please check the provided customer ID and SSN."
    else:
        status = response.status_code
        errors = '\t'.join(response.json().get('errors', ['Unknown error']))
        return f"Customer ID check failed. Status code: {status}. Errors: {errors}"

