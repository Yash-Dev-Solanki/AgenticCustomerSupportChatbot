from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph.graph import CompiledGraph
from models.graphState import GraphState
from langchain_core.tools import tool
from typing import Annotated, Dict, Any
from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.messages.tool import ToolMessage
from langgraph.types import Command
from langgraph.prebuilt import InjectedState
import os

VECTORSTORE_PATH = "../vectorstore/kyc_store"

os.environ["OPENAI_API_KEY"] = ""

import sys

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

embedding_function = OpenAIEmbeddings()
vectorstore = Chroma(persist_directory=VECTORSTORE_PATH, embedding_function=embedding_function)
retriever = vectorstore.as_retriever()
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True,output_key="answer")

model = ChatOpenAI(model= "gpt-4o",
                   temperature= 0,
                   streaming= True)


CUSTOM_PROMPT = """
You are an expert assistant specializing in Kyc documents.
Use the provided context to answer the question as accurately as possible.
If the answer is not in the context, say "I don't know".

Context:
{context}

Question:
{question}

Answer:
"""

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=CUSTOM_PROMPT,
)

qa_chain = ConversationalRetrievalChain.from_llm(
    llm=model,
    retriever=retriever,
    memory=memory,
    combine_docs_chain_kwargs={"prompt": prompt},
    return_source_documents=True,
    output_key="answer",
)

def ask_kyc(question):
    result = qa_chain.invoke({"question": question})
    print(f"ask_kyc got result: {result}")
    return result["answer"]


@tool(parse_docstring=True)
def kyc_tool(
    question: str,
    tool_call_id: Annotated[str, InjectedToolCallId], 
    state: Annotated[Dict[str, Any], InjectedState],    
) -> Command:  
    """
        Answers kyc-related questions using the QA chain.

        Args:
            question (str): The kyc-related question to answer.
            tool_call_id (str): The injected tool call ID for tracking.
            state (Dict[str, Any]): The injected conversation state.

        Returns:
            Command: A LangGraph command that updates state and returns a ToolMessage with the answer.
    """
    print(f"Kyc tool received question: {question}")

    # Get the answer from the QA chain
    answer = ask_kyc(question)
    
    # Create a ToolMessage (required for OpenAI tool flow)
    tool_message = ToolMessage(
        content=answer,
        tool_call_id=tool_call_id
    )
    
    # Return a Command to update the state
    return Command(
        update={
            "messages": state["messages"] + [tool_message],
            "answer": answer,
        }
    )

def create_profile_agent() -> CompiledGraph:
    return create_react_agent(
        model=model,
        tools=[kyc_tool],
        prompt = """You are a kyc expert agent. For every kyc-related question, ALWAYS call the kyc_tool with the question as input.
        Never answer directly. Always delegate to the kyc_tool.
        """,
        name="kyc_agent",
        state_schema=GraphState,
    )


