from base_store import BaseVectorStore

source_path = r"C:\Users\yash\source\AgenticCustomerSupportChatbot\docs\Payments"
profile_store = BaseVectorStore(source_directory= source_path, collection= 'Payments', persist_directory= './qdrant/Payments')
profile_store.update_vector_store()