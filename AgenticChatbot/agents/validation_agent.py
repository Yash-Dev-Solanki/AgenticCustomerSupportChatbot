from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langgraph.graph.graph import CompiledGraph

from tools.customer_id_validation import validate_customer_id
from models.graphState import GraphState

model = ChatOpenAI(model= "gpt-4o",
                   temperature= 0,
                   streaming= True)


def get_validation_agent() -> CompiledGraph:
    agent = create_react_agent(
        model= model,
        tools= [validate_customer_id],
        prompt= (
            """
            You're a customer validation agent for n business application.
            
            INSTRUCTIONS:
            - Your primary role is to validate customer IDs using the validate_customer_id tool
            - When you receive a validation request, use the tool to check the customer ID
            - After validation, provide a clear summary of the results.
            - If validation fails, explain what went wrong
            - Report your findings back to the supervisor clearly.

            RESPONSE FORMAT:
            - Start with "VALIDATION COMPLETE"
            - Provide the validation result (SUCCESS or FAILURE)
            - Include relevant customer details if successful
            - Include error details if failed
            """
        ),
        name= "validation_agent",
        state_schema= GraphState,
    )

    return agent
