from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

def send_payment_reminder(email_address: str):
    print(f"Mailing {email_address} regarding their upcoming payment")

def send_past_due_date_reminder(email_address: str):
    print(f"Mailing {email_address} regarding their late payment")


load_dotenv()
uri = os.getenv("CONNECTION_STRING")
db = os.getenv("DATABASE_NAME")
collection = os.getenv("COLLECTION_NAME", "")

client = MongoClient(uri)

try:
    accounts = client.get_database(db).get_collection(collection)
    cursor = accounts.find({"PaymentReminder": True}, projection= {"NextPayment": 1, "EmailAddress": 1})
    counter = 0
    for account in cursor:
        next_payment = account["NextPayment"].date()
        payment_reminder_criteria = datetime.now().date() + timedelta(days= 2)

        if next_payment < datetime.now().date():
            send_past_due_date_reminder(account["EmailAddress"])
        elif next_payment < payment_reminder_criteria:
            send_payment_reminder(account["EmailAddress"])
        
        counter += 1

except Exception as e:
    raise Exception("Unable to access document due to: ", e)