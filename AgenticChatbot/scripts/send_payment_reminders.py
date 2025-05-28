import time
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

def send_payment_reminder(email_address: str):
    print(f"Mailing {email_address} regarding their upcoming payment")

def send_past_due_date_reminder(email_address: str):
    print(f"Mailing {email_address} regarding their upcoming payment")


load_dotenv()
uri = os.getenv("CONNECTION_STRING")
db = os.getenv("DATABASE_NAME")
collection = os.getenv("COLLECTION_NAME", "")

client = MongoClient(uri)

try:
    accounts = client.get_database(db).get_collection(collection)
    cursor = accounts.find({}, projection= {"NextPayment": 1, "EmailAddress": 1})
    for account in cursor:
        next_payment = account["NextPayment"].date()
        payment_reminder_criteria = datetime.now().date() + timedelta(days= 2)
        print(payment_reminder_criteria)

        if next_payment > datetime.now().date():
            send_past_due_date_reminder(account["EmailAddress"])
        elif next_payment > payment_reminder_criteria:
            send_payment_reminder(account["EmailAddress"])

except Exception as e:
    raise Exception("Unable to access document due to: ", e)