from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from pymongo import MongoClient
from pydantic import SecretStr
from dotenv import load_dotenv
from email_reminder import send_reminder
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

db = client.agenticai
accounts_col = db.Accounts
payments_col = db.LoanPayments
payment_reminders_col = db.PaymentReminders

model = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    streaming=False,
    api_key=SecretStr(os.getenv("OPENAI_API_KEY"))
)

def fetch_payment_dates(customer_id):
    payments = payments_col.find({"customerId": customer_id}).sort("PaymentDate", 1)
    return [p["PaymentDate"].strftime("%Y-%m-%d") for p in payments]

def has_payment_this_month(payment_dates):
    now = datetime.now()
    for date_str in payment_dates:
        payment_date = datetime.strptime(date_str, "%Y-%m-%d")
        if payment_date.year == now.year and payment_date.month == now.month:
            return True
    return False

def call_gpt_predict_date(payment_dates):
    prompt = f"""
Customer has made loan payments on these dates:
{', '.join(payment_dates)}

Please predict the user's next payment date in YYYY-MM-DD format.
If there is a clear consistent pattern in their payment dates, provide the most likely next payment date.
If there is no consistency or recognizable pattern, respond with the date two days before the 30th of the next month (i.e., the 28th).
Only reply with the date.
"""
    response = model.invoke([HumanMessage(content=prompt)])
    predicted_date = response.content.strip()
    try:
        datetime.strptime(predicted_date, "%Y-%m-%d")
        return predicted_date
    except ValueError:
        return None

def update_reminder_dates():
    customers = accounts_col.find({"PaymentReminder": True})
    today = datetime.today()
    for customer in customers:
        customer_id = customer["CustomerId"]
        payment_dates = fetch_payment_dates(customer_id)

        if not payment_dates:
            year = today.year
            month = today.month
            reminder_date = datetime(year, month, 28).strftime("%Y-%m-%d")
        else:
            predicted_date = call_gpt_predict_date(payment_dates)
            if predicted_date is None:
                year = today.year
                month = today.month
                predicted_date = datetime(year, month, 28).strftime("%Y-%m-%d")
            reminder_date = predicted_date

        payment_reminders_col.update_one(
            {"customerId": customer_id},
            {"$set": {"reminder_date": reminder_date, "reminder_sent": False}},
            upsert=True
        )
        print(f"Set reminder for {customer_id} to {reminder_date}")

if __name__ == "__main__":
    update_reminder_dates()
    send_reminder()
