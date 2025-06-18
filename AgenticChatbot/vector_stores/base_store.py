from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from typing import (
    List
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import glob
import pandas as pd
import hashlib
from typing import Tuple
from utils import get_extracted_documents
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
from dotenv import load_dotenv, find_dotenv
from pydantic import SecretStr

class BaseVectorStore:
    def __init__(
            self, 
            source_directory: str, 
            collection: str, 
            persist_directory: str,
            chunk_size: int = 1000, 
            chunk_overlap: int = 200
    ):
        load_dotenv(find_dotenv(raise_error_if_not_found= True))
        self.source_directory = source_directory
        self.embeddings = OpenAIEmbeddings(model= "text-embedding-3-small", api_key= SecretStr(os.getenv("OPENAI_API_KEY", "")))
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.db_directory = persist_directory
        self.collection = collection

        if os.path.isfile(os.path.join(self.source_directory, 'index.csv')):
            self.index = pd.read_csv(os.path.join(self.source_directory, 'index.csv'))
        else:
            self.index = pd.DataFrame(columns= ['HashCode', 'Source'])
    
    
    def generate_current_hash_codes(self) -> pd.DataFrame:
        current_index = pd.DataFrame(columns= ['HashCode', 'Source'])
        documents = glob.glob(os.path.join(self.source_directory, '**', '*.pdf'), recursive= True)
        for doc in documents:
            with open(doc, 'rb') as f:
                hash_code = hashlib.md5(f.read()).hexdigest()
            
            doc_metadata = pd.Series({'HashCode': hash_code, 'Source': doc})
            current_index = pd.concat([current_index, doc_metadata.to_frame().T], ignore_index= True)
        
        return current_index
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size= self.chunk_size,
            chunk_overlap= self.chunk_overlap
        )

        chunks = text_splitter.split_documents(documents)
        return chunks
    
    def get_vector_store(self) -> Chroma:
        vector_store = Chroma(
            embedding_function= self.embeddings,
            persist_directory= self.db_directory,
            collection_name= self.collection
        )
        return vector_store
    
    def fetch_to_delete_and_update(self, current_index: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Identify records to delete and update by comparing current index with existing index.
    
        Args:
            current_index (pd.DataFrame): The new/current index DataFrame containing 'HashCode' 
            column to compare against the existing index.
    
        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing:
            - to_delete (pd.DataFrame): Records from existing index that are not present 
            in current_index (based on HashCode comparison)
            - to_update (pd.DataFrame): Records from current_index that are not present 
            in existing index (based on HashCode comparison)

        """
        to_delete = self.index[~self.index['HashCode'].isin(current_index['HashCode'])]
        to_update = current_index[~current_index['HashCode'].isin(self.index['HashCode'])]

        return (to_delete, to_update)


    def update_vector_store(self):
        if not os.path.exists(self.db_directory):
            os.makedirs(self.db_directory)
        
        vector_store = self.get_vector_store()
        current_index = self.generate_current_hash_codes()
        to_delete, to_update = self.fetch_to_delete_and_update(current_index)
        
        # Deleting outdated documents from vector store
        for index, row in to_delete.iterrows():
            hash_to_delete = row['HashCode']
            vector_store.delete(where= {
                "HashCode": hash_to_delete
            })
        
        extracted_documents = []
        # Adding updated docs to the vector db
        for index, row in to_update.iterrows():
            meta_data = row.to_dict()
            loader = AzureAIDocumentIntelligenceLoader(
                api_endpoint= os.getenv("AZURE_DOCUMENT_ENDPOINT", ""),
                api_key= os.getenv("AZURE_DOCUMENT_API_KEY"),
                file_path= row['Source'],
                api_model= 'prebuilt-read'
            )

            documents = loader.load()
            for doc in documents:
                extracted_documents.extend(get_extracted_documents(document= doc, metadata= meta_data))

        chunks = self.split_documents(extracted_documents)
        vector_store.add_documents(chunks)
        
        current_index.to_csv(os.path.join(self.source_directory, 'index.csv'), index= False)