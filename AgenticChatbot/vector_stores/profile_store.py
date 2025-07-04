from base_store import BaseVectorStore

source_path = r"C:\Users\sanka\Downloads\AgenticCustomerSupportChatbot\AgenticChatbot\data\docs\profile_docs"
profile_store = BaseVectorStore(source_directory= source_path, collection= 'Profile', persist_directory= './chroma/Profile')
profile_store.update_vector_store()