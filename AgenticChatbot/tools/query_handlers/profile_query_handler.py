from tools.query_handlers.RAG import RAG
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr
import os
from dotenv import load_dotenv, find_dotenv
from langchain_core.tools import BaseTool, tool


load_dotenv(find_dotenv())
embeddings = OpenAIEmbeddings(model= "text-embedding-3-large", api_key= SecretStr(os.getenv("OPENAI_API_KEY", "")))

profile_prompt = '''
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


def get_profile_query_handler() -> BaseTool:
    @tool(parse_docstring= True)
    def invoke_model(query: str):
        """
        Invoke the Customer Relation Summary RAG model to answer a given query. This method processes a user query through the RAG (Retrieval-Augmented Generation) system, which retrieves relevant information and generates an answer based on the retrieved context and the model's description.

        Args:
            query (str): The question or query to be answered by the RAG model.
        """
        # Setup Qdrant client and vector store
        client = QdrantClient(path= "./qdrant/Profile")
        profile_vector_store = QdrantVectorStore(
            client= client,
            collection_name= 'Profile',
            embedding= embeddings,
        )
        profile_rag = RAG(vector_store= profile_vector_store, prompt= profile_prompt)
        profile_rag.create_rag()

        # Invoke the RAG model with the query
        print("Processing profile query")
        result = profile_rag.rag.invoke({"question": query})

        # Clean up resources
        del profile_vector_store
        del client
        return result["answer"]

    
    return invoke_model