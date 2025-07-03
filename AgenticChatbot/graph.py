from models.graphState import GraphState
from agents.update_agent import get_update_agent
from agents.supervisor_agent import get_supervisor_agent
from agents.query_agent import get_query_agent
from agents.welcome_agent import get_welcome_agent
from agents.summary_agent import get_summary_agent

from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig

from langgraph.graph.graph import CompiledGraph
from typing import Literal

def build_model() -> CompiledGraph:
    def router(state: GraphState) -> Literal["welcome_agent", "supervisor", "end"]:
        """
        Routes the state to the appropriate agent based on validation status.
        """
        if state["validated"] == True:
            return "supervisor"
        else:
            if state["current_retries"] <= state["validation_retries"]:
                return "welcome_agent"
            else:
                return "end"

    
    
    
    checkpointer= InMemorySaver()
    update_agent = get_update_agent()
    query_agent = get_query_agent()
    summary_agent = get_summary_agent()
    members = ["update_agent", "query_agent", "summary_agent"]
    supervisor_agent = get_supervisor_agent(members= members)
    welcome_agent = get_welcome_agent()

    graph = (
        StateGraph(GraphState)
        .add_node(welcome_agent)
        .add_node(supervisor_agent, destinations= ("update_agent", "query_agent", "summary_agent", END))
        .add_node(update_agent)
        .add_node(query_agent)
        .add_node(summary_agent)
        .add_conditional_edges(
            START, router,
            {
                "welcome_agent": "welcome_agent",
                "supervisor": "supervisor",
                "end": END
            }
        )
        .add_edge("welcome_agent", END)
        .add_edge("update_agent", "supervisor")
        .add_edge("query_agent", "supervisor")
        .add_edge("summary_agent", "supervisor")
    ).compile(checkpointer= checkpointer)

    return graph


def invoke_model(model: CompiledGraph, input_state: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
    response = model.invoke(input_state, config= config)
    return model.get_state(config= config).values

