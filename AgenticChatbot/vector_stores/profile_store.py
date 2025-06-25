from base_store import BaseVectorStore

source_path = r"C:\Users\yash\source\AgenticCustomerSupportChatbot\docs\Profile"
profile_store = BaseVectorStore(source_directory= source_path, collection= 'Profile', persist_directory= './qdrant/Profile')
profile_store.update_vector_store()