from pydantic import BaseModel
from typing import List
from datetime import datetime

class Address(BaseModel):
    addressLine1: str
    addressLine2: str
    city: str
    state: str
    country: str
    postalCode: str

class PhoneInfo(BaseModel):
    homePhone: str
    workPhone: str

class Customer(BaseModel):
    customerId: str
    customerName: str
    paymentMethod: str
    createdOn: datetime
    nextPayment: datetime
    finalPayment: datetime
    address: Address
    emailAddress: str
    phoneInfo: PhoneInfo
    paymentReminder: bool
    notes: list[str]

