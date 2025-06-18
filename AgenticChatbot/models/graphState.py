from typing import (
    Optional,
    Dict,
    Any,
    List
)
from langchain.schema import BaseMessage 
from langgraph.prebuilt.chat_agent_executor import AgentState


class GraphState(AgentState):
    customer: Optional[Dict[str, Any]]
    validated: Optional[bool]
    messages: Optional[List[BaseMessage]] = []
    remaining_steps: Optional[int] = None
    answer: Optional[str] = None
