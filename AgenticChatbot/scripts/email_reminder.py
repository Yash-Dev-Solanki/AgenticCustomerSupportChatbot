import os
from datetime import datetime
from urllib import response
from pymongo import MongoClient
import smtplib
from email.message import EmailMessage
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from pydantic import SecretStr
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

client = MongoClient(MONGO_URI)
db = client.agenticai
accounts_col = db.Accounts
payments_col = db.LoanPayments
reminders_col = db.PaymentReminders


model = ChatOpenAI(
    model="gpt-4o",
    temperature=0.5,
    streaming=False,
    api_key= SecretStr(os.getenv('OPENAI_API_KEY', ''))
)

def fetch_payment_dates(customer_id):
    payments = payments_col.find({"customerId": customer_id}).sort("PaymentDate", 1)
    return [p["PaymentDate"].strftime("%Y-%m-%d") for p in payments]

def has_paid_this_month(customer_id):
    now = datetime.now()
    start = datetime(now.year, now.month, 1)
    if now.month == 12:
        next_month = datetime(now.year + 1, 1, 1)
    else:
        next_month = datetime(now.year, now.month + 1, 1)
    return payments_col.find_one({
        "customerId": customer_id,
        "PaymentDate": {"$gte": start, "$lt": next_month}
    }) is not None

def generate_email_body(name, due_date, payment_dates=None):
    prompt = f"""
You are a helpful loan assistant sending a personalized reminder email.

Customer name: {name}
Payment due date: {due_date}

Write a friendly, professional email reminding the customer to pay on time. Keep it under 100 words.
Close politely.
The email is sent by the Loan Payment department.
"""
    response = model.invoke([HumanMessage(content=prompt)])
    predicted_text = response.content
    return predicted_text.strip()

def send_email(to_email, name, due_date, body_text):
    msg = EmailMessage()
    print(f"The email body is: {body_text}")

def send_reminder():
    today_str = datetime.today().strftime("%Y-%m-%d")
    reminders = reminders_col.find({
        "reminder_date": today_str,
        "reminder_sent": False
    })

    for reminder in reminders:
        customer_id = reminder["customerId"]
        customer = accounts_col.find_one({"CustomerId": customer_id})

        if not customer:
            print(f"Customer {customer_id} not found.")
            continue

        email = customer.get("EmailAddress")
        name = customer.get("CustomerName", "Customer")

        if not email:
            print(f" No email for {customer_id}")
            continue

        if has_paid_this_month(customer_id):
            print(f"{customer_id} already paid. Skipping.")
            continue

        payment_dates = fetch_payment_dates(customer_id)
        email_body = generate_email_body(name, today_str, payment_dates)

        try:
            send_email(email, name, today_str, email_body)
            reminders_col.update_one(
                {"_id": reminder["_id"]},
                {"$set": {"reminder_sent": True}}
            )
        except Exception as e:
            print(f"Error sending to {email}: {e}")

#if __name__ == "__main__":
    #send_daily_reminders()
