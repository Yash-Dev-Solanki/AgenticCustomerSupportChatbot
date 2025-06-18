from tools.query_handlers.RAG import RAG
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr
import os
from dotenv import load_dotenv
from langchain_core.tools import BaseTool, tool


load_dotenv()
embeddings = OpenAIEmbeddings(model= "text-embedding-3-small", api_key= SecretStr(os.getenv("OPENAI_API_KEY", "")))
payments_vector_store = Chroma(
    collection_name= 'Payments',
    embedding_function= embeddings,
    persist_directory= './chroma/Payments'
)

payments_prompt = '''
You're an AI agent tasked with answering user queries related to Customer Relation Summary.
INSTRUCTIONS:
- Answer based solely on the provided context
- If the answer is not in the context, clearly state that the information is not available in the policy documents
- Quote relevant parts of the context when appropriate
- If there are multiple relevant pieces of information, synthesize them coherently

Context: 
{context}

Question: {question}
'''


def get_payments_query_handler() -> BaseTool:
    payments_rag = RAG(vector_store= payments_vector_store, prompt= payments_prompt)
    payments_rag.create_rag()

    @tool(parse_docstring= True)
    def invoke_model(query: str):
        """
        Invoke the Deposit Account Agrrement to answer a given query. This method processes a user query through the RAG (Retrieval-Augmented Generation) system, which retrieves relevant information and generates an answer based on the retrieved context and the model's description.

        Args:
            query (str): The question or query to be answered by the RAG model.
        """
        print("Processing payments query")
        result = payments_rag.rag.invoke({"question": query})
        return result["answer"]

    
    return invoke_model