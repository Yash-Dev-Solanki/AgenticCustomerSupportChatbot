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
from pydantic import SecretStr
from dotenv import load_dotenv
import os
from models.graphState import GraphState

load_dotenv()
model = ChatOpenAI(model= "gpt-4o",
                   temperature= 0,
                   api_key= SecretStr(os.getenv('OPENAI_API_KEY', ''))
        )


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

        print(f"State before handoff: {state['messages']}")
        print(f"Handing Off to {name}")
        
        return Command(
            goto= agent_name,
            update= {"messages": state["messages"] + [tool_message]},
            graph= Command.PARENT,
        )
    
    return handoff_tool



# Handoff Tools
assign_to_update_agent = create_handoff_tool(agent_name= "update_agent", description= "Assign task to a update agent")
assign_to_query_agent = create_handoff_tool(agent_name= "query_agent", description= "Assign task to query agent")


def get_supervisor_agent(members: List[str]) -> CompiledGraph:
    supervisor_agent = create_react_agent(
        model= model,
        tools= [ assign_to_update_agent, assign_to_query_agent],
        prompt = (
            f"""
            You're a supervisor tasked with managing conversation between the following workers: {members}

            The workers can perform the following tasks:
            - an updation agent: Perform updates to customer data stored in the collection. 
            - a query agent: Retrieve responses to user queries from policy documents

            Important Rules:
            1. Do not do any work yourself. 
            2. Assign work to one agent at a time, do not call agents in parallel.
            """   
        ),
        name= "supervisor",
        state_schema= GraphState
    )
        
    return supervisor_agent