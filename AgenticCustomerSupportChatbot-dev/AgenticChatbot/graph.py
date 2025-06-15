from models.graphState import GraphState

from agents.validation_agent import get_validation_agent
from agents.update_agent import get_update_agent
from agents.supervisor_agent import get_supervisor_agent
from agents.query_agent import get_query_agent
from agents.payments_agent import create_payments_agent
from agents.kyc_agent import create_kyc_agent
from agents.profile_agent import create_profile_agent

from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig

from langgraph.graph.graph import CompiledGraph
from langchain_core.messages import AIMessage, HumanMessage

def build_model() -> CompiledGraph:
    checkpointer= InMemorySaver()
    validation_agent = get_validation_agent()
    update_agent = get_update_agent()
    query_agent = get_query_agent()
    payments_agent = create_payments_agent()
    kyc_agent = create_kyc_agent()
    profile_agent = create_profile_agent()
    members = ["validation_agent", "update_agent", "query_agent", "payments_agent", "kyc_agent", "profile_agent"]
    supervisor_agent = get_supervisor_agent(members= members)

    supervisor = (
        StateGraph(GraphState)
        .add_node(supervisor_agent, destinations= ("validation_agent", "update_agent", "query_agent","payments_agent","kyc_agent", "profile_agent", END))
        .add_node(validation_agent)
        .add_node(update_agent)
        .add_node(query_agent)
        .add_node(payments_agent)
        .add_node(kyc_agent)
        .add_node(profile_agent)
        .add_edge(START, "supervisor")
        .add_edge("validation_agent", "supervisor")
        .add_edge("update_agent", "supervisor")
        .add_edge("payments_agent", "supervisor")
        .add_edge("query_agent", "supervisor")
        .add_edge("kyc_agent", "supervisor")
        .add_edge("profile_agent", "supervisor")
    ).compile(checkpointer= checkpointer)

    return supervisor


config = RunnableConfig({"configurable": {"thread_id": 1}})


def invoke_model(model: CompiledGraph, input_state: Dict[str, Any]) -> Dict[str, Any]:
    response = model.invoke(input_state, config= config)
    print(f"invoke_model got response: {response}")
    return model.get_state(config= config).values
    
    