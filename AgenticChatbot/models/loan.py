from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class LoanPayment(BaseModel):
    paymentDate: datetime
    amountPaid: float
    paymentMode: str
    status: str
    transactionId: Optional[str] = None
    loanAccountNumber: Optional[str] = None

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
