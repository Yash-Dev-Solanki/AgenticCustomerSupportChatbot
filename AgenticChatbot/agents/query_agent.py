from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langgraph.graph.graph import CompiledGraph

from models.graphState import GraphState
from tools.query_handlers.customer_data_query import process_customer_data_query

model = ChatOpenAI(model= "gpt-4o",
                   temperature= 0,
                   streaming= True)

def get_query_agent() -> CompiledGraph:
    query_agent = create_react_agent(
        model= model, 
        tools= [process_customer_data_query],
        prompt= (
            f"""
            You're a query handler  management agent tasked with routing the user query to the appropriate query handlers.
            You're equipped with following handlers:
            - customer_data_query_handler: fetches data that is stored in the database regarding the customer account details

            INSTRUCTIONS:
            Return the response as is fetched by the appropriate query agents.
            """
        ),
        name= "query_agent",
        state_schema= GraphState,
    )

    return query_agent
