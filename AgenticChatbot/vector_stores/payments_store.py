from base_store import BaseVectorStore

source_path = r"C:\Users\sanka\Downloads\AgenticCustomerSupportChatbot\AgenticChatbot\data\docs\payments_docs"
profile_store = BaseVectorStore(source_directory= source_path, collection= 'Payments', persist_directory= './chroma/Payments')
profile_store.update_vector_store()