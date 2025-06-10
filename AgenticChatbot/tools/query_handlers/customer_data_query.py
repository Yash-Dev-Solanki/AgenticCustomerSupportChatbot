from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langchain_core.tools import tool
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessagesState
from langgraph.prebuilt import InjectedState

from typing import (
    Dict,
    Any,
    Annotated
)


class QueryState(MessagesState):
    Customer: Dict[str, Any]
    original_query: str
    current_query: str
    generated_output: str
    grade: str
    final_result: str



chat_model = ChatOpenAI(model= "gpt-4.1-nano", temperature= 0, streaming= True)


GENERATE_PROMPT = """
You are an assistant for question-answering tasks for queries related to customer data stored in the database.
INPUT FORMAT:
1. Question: Describes the user query
2. Customer: The current customer data as it is stored in the database.
OUTPUT FORMAT:
Return all relevant fields fetched in the form of a json where each json element is in the format:
FieldName : FieldValue
"""


GRADE_PROMPT = """
You are a grader assessing the relevance of the retrieved fields from Customer model on the basis of a user question.
If the document contains the fields related to the user question, grade it as relevant.
Give a binary score 'SATISFACTORY' or 'UNSATISFACTORY' score to indicate whether the retrieved fields is relevant to the question.
"""


REWRITE_PROMPT = """
You are a query optimization expert. Rewrite the given query to be more specific, clear, and likely to produce a better response. Make the query more specific, add context if needed, or rephrase for clarity.
            
Return only the rewritten query, nothing else.
"""

def generate_answer(state: QueryState):
    """Generate output based on the current query"""
    generation_prompt = ChatPromptTemplate.from_messages([
        ("system", GENERATE_PROMPT),
        ("human", "Customer Data is follows: {customer}. The user query is: {query}")
    ])

    chain = generation_prompt | chat_model | StrOutputParser()
    response = chain.invoke({"customer": state["Customer"], "query": state["current_query"]})

    return {
        "generated_output": response
    }


def grade_ouptut(state: QueryState):
    """Determine whether the fields retrieved from the customer database are relevant to the user query"""
    
    grading_prompt = ChatPromptTemplate.from_messages([
        ("system", GRADE_PROMPT),
        ("human", """"
         Customer: {customer_data}
         Original Query: {original_query},
         Current Query: {current_query},
         Generated Output: {output}
        """)
    ])

    chain = grading_prompt | chat_model | StrOutputParser()
    score = chain.invoke({
        "customer_data": str(state["Customer"]),
        "original_query": state["original_query"],
        "current_query": state["current_query"],
        "output": state["generated_output"]
    })

    return {
        "grade": score.strip()
    }


def rewrite_query(state: QueryState):
    """Rewrite the query to improve output quality"""

    rewrite_prompt = ChatPromptTemplate.from_messages([
        ("system", REWRITE_PROMPT),
        ("human", """
        Customer: {customer_data}
        Original uery: {original_query},
        Current Query: {current_query},
        Generated Output: {output}
        Grade: {grade}
        """)
    ])

    chain = rewrite_prompt | chat_model | StrOutputParser()
    response = chain.invoke({
        "customer_data": str(state["Customer"]),
        "original_query": state["original_query"],
        "current_query": state["current_query"],
        "grade": state["grade"],
        "output": state["generated_output"]
    })

    return {
        "current_query": response.strip()
    }


def should_rewrite(state: QueryState) -> bool:
    """Determine if query should be rewritten based on grade and iteration count"""
    if state["grade"] == "SATISFACTORY":
        return False
    else:
        return True


def finalize_result(state: QueryState):
    """Finalizes the result"""
    return {
        "final_result": state["generated_output"]
    }



@tool(parse_docstring= True)
def process_customer_data_query(user_query: str, state: Annotated[Dict[str, Any], InjectedState]):
    """
    Creates chat completion call to a LLM in order to parse and fetch relevant fields from the customer data according to the user query 

    Args:
        user_query (str): the user query that needs to be processed by the tool
        state: A state object containing relevant metadata that serves as short-term memory checkpointer for the agent
    """
    workflow = StateGraph(QueryState)

    workflow.add_node("generate_output", generate_answer)
    workflow.add_node("grade_output", grade_ouptut)
    workflow.add_node("rewrite_query", rewrite_query)
    workflow.add_node("finalize_result", finalize_result)

    workflow.add_edge(START, "generate_output")
    workflow.add_edge("generate_output", "grade_output")
    workflow.add_conditional_edges(
        "grade_output",
        should_rewrite,
        {
            True: "rewrite_query",
            False: "finalize_result"
        }
    )
    workflow.add_edge("rewrite_query", "generate_output")
    workflow.add_edge("finalize_result", END)

    query_state = {
        "Customer": state["customer"],
        "original_query": user_query,
        "current_query": user_query,
        "generated_output": "",
        "grade": "",
        "final_result": ""
    }


    graph = workflow.compile()
    result = graph.invoke(query_state)
    return {
        "messages": result
    }
