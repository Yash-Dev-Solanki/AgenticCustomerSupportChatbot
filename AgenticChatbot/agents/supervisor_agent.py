from langchain_openai import ChatOpenAI
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import InjectedState, create_react_agent
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.types import Command
from langchain_core.messages.tool import ToolMessage

from typing import (
    List,
    Annotated,
    Dict, 
    Any
)

from models.graphState import GraphState

model = ChatOpenAI(model= "gpt-4o",
                   temperature= 0,
                   streaming= True)


def create_handoff_tool(*, agent_name: str, description: str | None = None):
    name = f"transfer_to_{agent_name}"
    description = description or f"Ask {agent_name} for help"

    @tool(name, description= description) 
    def handoff_tool(
        state: Annotated[Dict[str, Any], InjectedState], tool_call_id: Annotated[str, InjectedToolCallId]
    ) -> Command:
        tool_message = ToolMessage(
            content = f"Successfully transferred to {agent_name}",
            name= name, 
            tool_call_id= tool_call_id
        )

        print(f"Handing Off to {name}")
        
        return Command(
            goto= agent_name,
            update= {"messages": state["messages"] + [tool_message]},
            graph= Command.PARENT,
        )
    
    return handoff_tool



# Handoff Tools
assign_to_validation_agent = create_handoff_tool(agent_name= "validation_agent", description= "Assign task to a validation agent")
assign_to_update_agent = create_handoff_tool(agent_name= "update_agent", description= "Assign task to a update agent")
assign_to_query_agent = create_handoff_tool(agent_name= "query_agent", description= "Assign task to query agent")
assign_to_payments_agent = create_handoff_tool(agent_name= "payments_agent", description= "Assign task to payments agent")
assign_to_profile_agent = create_handoff_tool(agent_name= "profile_agent", description= "Assign task to profile agent")
assign_to_kyc_agent = create_handoff_tool(agent_name= "kyc_agent", description= "Assign task to kyc agent")

def get_supervisor_agent(members: List[str]) -> CompiledGraph:
    supervisor_agent = create_react_agent(
        model= model,
        tools= [assign_to_validation_agent, assign_to_update_agent, assign_to_query_agent,assign_to_payments_agent,assign_to_profile_agent, assign_to_kyc_agent],
        prompt = (
            f"""
            You're a supervisor tasked with managing conversation between the following workers: {members}

            The workers can perform the following tasks:
            - a validation agent: Perform customer validation on the basis of customer Id provided by the user.
            - an updation agent: Perform updates to customer data stored in the collection.
            - a payments agent: Handle all payment-related queries and operations.
            - a profile agent: Manage user profile information and updates.
            - a kyc agent: Handle Know Your Customer (KYC) processes and verifications.

            Important Rules:
            1. Do not do any work yourself.
            2. Only perform customer validation if the requested operation is an update. 
                - If validated is None, delegate to the validation agent.
                - If validated is False, terminate the conversation with the reason.
                - If validated is True, proceed with the update.
                - For queries or payment tasks, no validation is required.
            """
        ),
        name= "supervisor",
        state_schema= GraphState
    )
        
    return supervisor_agent