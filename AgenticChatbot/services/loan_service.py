import requests
from models.loan import LoanStatementResponse
from endpoints import Endpoints

def fetch_loan_statement(customer_id: str) -> LoanStatementResponse:

    headers = {
        "customerId": customer_id 
    }

    response = requests.get(Endpoints.FETCH_LOAN_STATEMENT, headers=headers, verify= False)
    response.raise_for_status()
    data = response.json()
    return LoanStatementResponse(**data)