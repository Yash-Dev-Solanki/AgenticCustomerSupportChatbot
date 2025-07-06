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
    validation_retries: int
    current_retries: int
    loan_statement_generation: bool
