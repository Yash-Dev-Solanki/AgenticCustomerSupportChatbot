from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

from tools.customer_update import update_customer_email
from models.graphState import GraphState

model = ChatOpenAI(model= "gpt-4o-mini",
                   temperature= 0,
                   streaming= True)


def get_update_agent():
    agent = create_react_agent(
        model= model,
        tools= [update_customer_email],
        prompt= (
            """
            You're a updation agent for an application tasked with updating customer account details in the database.
            INSTRUCTIONS:
            - Assist ONLY with account updation tasks.
            - After you're done, respond to the supervisor directly
            - Respond ONLY with the results, do NOT include ANY other text.
            """
        ),
        name= "update_agent",
        state_schema= GraphState
    )

    return agent