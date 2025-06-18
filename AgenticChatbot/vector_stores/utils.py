from langchain_core.documents import Document
from typing import List, Dict

def get_extracted_documents(document: Document, metadata: Dict) -> List[Document]:
    '''
    Returns the line wise documents from document extracted via Azure Document Intelligence

    '''
    result = []

    if 'paragraphs' in document.metadata:
        for para in document.metadata['paragraphs']:
            result.append(Document(page_content= para['content'], metadata= metadata))

    return result
