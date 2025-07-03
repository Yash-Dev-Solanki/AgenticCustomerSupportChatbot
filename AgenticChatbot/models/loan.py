from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class LoanPayment(BaseModel):
    paymentDate: datetime
    paymentAmount: float
    interestPaid: float
    principalPaid: float
    previousPrincipal: float
    currentPrincipal: float
    paymentMode: str
    transactionId: str

class LoanSummary(BaseModel):
    loanAmount: float
    interestRate: float
    tenureMonths: int
    emiAmount: float
    startDate: datetime
    status: str

class LoanStatementResponse(BaseModel):
    success: bool
    statusCode: int
    errors: Optional[List[str]]
    customerId: str
    loanAccountNumber: str
    loanSummary: LoanSummary
    paymentHistory: Optional[List[LoanPayment]]
