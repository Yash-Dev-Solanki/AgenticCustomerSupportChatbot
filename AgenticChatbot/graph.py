from models.graphState import GraphState

from agents.validation_agent import get_validation_agent
from agents.update_agent import get_update_agent
from agents.supervisor_agent import get_supervisor_agent

from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig

from langgraph.graph.graph import CompiledGraph

def build_model() -> CompiledGraph:
    validation_agent = get_validation_agent()
    update_agent = get_update_agent()
    agents = [validation_agent, update_agent]
    members = ["validation_agent", "update_agent"]
    supervisor_agent = get_supervisor_agent(members= members)


    checkpointer= InMemorySaver()

    supervisor = (
        StateGraph(GraphState)
        .add_node(supervisor_agent, destinations= ("validation_agent", "update_agent", END))
        .add_node(validation_agent)
        .add_node(update_agent)
        .add_edge(START, "supervisor")
        .add_edge("validation_agent", "supervisor")
        .add_edge("update_agent", "supervisor")
    ).compile(checkpointer= checkpointer)

    return supervisor




config = RunnableConfig({"configurable": {"thread_id": 1}})


def invoke_model(model: CompiledGraph, input_state: Dict[str, Any]) -> Dict[str, Any]:
    response = model.invoke(input_state, config= config)

    return model.get_state(config= config).values

