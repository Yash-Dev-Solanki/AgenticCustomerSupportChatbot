import os
from langchain.vectorstores.base import VectorStore
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_cohere import CohereRerank
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from typing import (
    TypedDict,
    List
)
from dotenv import load_dotenv
from langgraph.graph import START, StateGraph
from pydantic import SecretStr

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

class RAG:
    def __init__(
        self, 
        vector_store: VectorStore, 
        prompt: str, 
        top_k_retrieval: int = 20, 
        top_k_rerank: int = 5,
    ):
        load_dotenv()
        self.embedding_function = OpenAIEmbeddings(
            model= "text-embedding-3-large",
            api_key= SecretStr(os.getenv('OPENAI_API_KEY', '')) 
        )
        self.vector_store = vector_store
        self.PROMPT = PromptTemplate(template= prompt, input_variables= ['context', 'question'])  
        self.top_k_retrieval = top_k_retrieval
        self.top_k_rerank = top_k_rerank
        self.model = ChatOpenAI(model= "gpt-4o-mini", temperature= 0, api_key= SecretStr(os.getenv('OPENAI_API_KEY', ''))) # type: ignore
        self.setup_reranked_retriever()
    

    def setup_reranked_retriever(self) -> None:
        # Setup vector store as retriever
        retriever = self.vector_store.as_retriever(
            search_type= "similarity",
            search_kwargs= {
                "k": self.top_k_retrieval
            }
        )
        compressor = CohereRerank(
            model= "rerank-english-v3.0",
            top_n= self.top_k_rerank,
            cohere_api_key= SecretStr(os.getenv('COHERE_API_KEY', ''))
        )

        # Wrap the ChromaDB base retriever with a reranker that reranks the docs using a Cohere Rerank
        self.retriever = ContextualCompressionRetriever(
            base_compressor= compressor, base_retriever= retriever
        )

    
    def retrieve(self, state: State):
        retrieved_docs = self.retriever.invoke(state["question"])
        return {"context": retrieved_docs}

    def generate(self, state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = self.PROMPT.invoke({
            "context": docs_content, 
            "question": state["question"]})
        response = self.model.invoke(messages)
        return {"answer": response.content}
    

    def create_rag(self):
        self.rag = (
            StateGraph(State)
            .add_node("retrieve", self.retrieve)
            .add_node("generate", self.generate)
            .add_edge(START, "retrieve")
            .add_edge("retrieve", "generate")
        ).compile()







