from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

from tools.customer_update import *
from models.graphState import GraphState
from pydantic import SecretStr
from dotenv import load_dotenv
import os

load_dotenv()
model = ChatOpenAI(model= "gpt-4o",
                   temperature= 0,
                   streaming= True,
                   api_key= SecretStr(os.getenv('OPENAI_API_KEY', ''))
        )


def get_update_agent():
    agent = create_react_agent(
        model= model,
        tools= [update_customer_email, update_customer_payment_reminder],
        prompt= (
            """
            You're a updation agent for an application tasked with updating customer account details in the database.
            INSTRUCTIONS:
            - Assist ONLY with account updation tasks.
            - After you're done, respond to the supervisor directly
            - Respond ONLY with the results, do NOT include ANY other text.
            - DO NOT ASSUME ANY DEFAULT VALUES.
            """
        ),
        name= "update_agent",
        state_schema= GraphState,
    )

    return agent