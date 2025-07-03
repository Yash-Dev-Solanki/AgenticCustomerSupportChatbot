import requests
from models.loan import LoanStatementResponse

def fetch_loan_statement(customer_id: str) -> LoanStatementResponse:

    headers = {
        "customerId": customer_id 
    }

    response = requests.get("http://localhost:5142/api/LoanStatement", headers=headers)
    response.raise_for_status()
    data = response.json()
    return LoanStatementResponse(**data)