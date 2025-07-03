from base_store import BaseVectorStore
import os
import shutil

payments_docs_source = r"C:\Users\yash\source\AgenticCustomerSupportChatbot\docs\Payments"
profile_docs_source = r"C:\Users\yash\source\AgenticCustomerSupportChatbot\docs\Profile"


def update_vector_stores():
    """
    Updates the vector stores for documents provided.
    """

    # Update the Payments vector store
    payments_store = BaseVectorStore(
        source_directory= payments_docs_source, 
        collection= "Payments", 
        persist_directory= "./qdrant/Payments")
    payments_store.update_vector_store()
    
    
    profile_store = BaseVectorStore(
        source_directory= profile_docs_source,
        collection= "Profile",
        persist_directory= "./qdrant/Profile"
    )
    profile_store.update_vector_store()


def reset_vector_stores():
    """
    Resets the vector stores by deleting the existing directories.
    """
    shutil.rmtree("./dqrant/Payments", ignore_errors=True)

    payments_index = os.path.join(payments_docs_source, 'index.csv')
    if os.path.exists(payments_index):
        os.remove(payments_index)
    
    profile_index = os.path.join(profile_docs_source, 'index.csv')
    if os.path.exists(profile_index):
        os.remove(profile_index)