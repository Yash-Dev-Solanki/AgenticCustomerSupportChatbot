from typing import (
    Optional, 
    Dict,
    Any
)

from langchain_core.messages import AnyMessage
from langgraph.prebuilt.chat_agent_executor import AgentState


class GraphState(AgentState):
    customer: Optional[Dict[str, Any]]
    validated: Optional[bool]
