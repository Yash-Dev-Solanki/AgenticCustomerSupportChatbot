from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langgraph.graph.graph import CompiledGraph

from models.graphState import GraphState
from tools.query_handlers.customer_data_query import process_customer_data_query
from tools.query_handlers import profile_query_handler, payments_query_handler

from pydantic import SecretStr
from dotenv import load_dotenv
import os

load_dotenv()
model = ChatOpenAI(model= "gpt-4o",
                   temperature= 0,
                   streaming= True, 
                   api_key= SecretStr(os.getenv('OPENAI_API_KEY', ''))
        )

process_profile_query = profile_query_handler.get_profile_query_handler()
process_payments_query = payments_query_handler.get_payments_query_handler()

def get_query_agent() -> CompiledGraph:
    query_agent = create_react_agent(
        model= model, 
        tools= [process_profile_query, process_payments_query],
        prompt= (
            f"""
            You're a query handler  management agent tasked with routing the user query to the appropriate query handlers.
            You're equipped with following handlers:
            - profile_data_query_handler: invokes the Customer Profile Summary RAG to retrieve & generate response to user query related to details regarding Customer Profile
            - payments_data_query_handler: invokes the Banking Payments RAG to retrieve & generate response to user queries realted to Payment Operations peformed by the bank

            INSTRUCTIONS:
            1. Return the response as is fetched by the appropriate query agents.
            3. Direct a user query only to a single appropriate query handler
            """
        ),
        name= "query_agent",
        state_schema= GraphState,
    )

    return query_agent
