import os
import json
import docx
import fitz 
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
from tqdm import tqdm
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

import os
os.environ["OPENAI_API_KEY"] = "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"


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # utils folder
BASE_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "data"))
VECTORSTORE_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "vectorstore"))
TIMESTAMP_FILE = os.path.join(VECTORSTORE_PATH, "last_processed.json")

AGENT_DOC_PATHS = {
    "kyc": os.path.join(BASE_PATH, "kyc_docs.pdf"),
    "payments": os.path.join(BASE_PATH, "payments_docs.pdf"),
    "profile": os.path.join(BASE_PATH, "profile_docs.pdf")
}

AGENT_STORE_PATHS = {
    "kyc": os.path.join(VECTORSTORE_PATH, "kyc_store"),
    "payments": os.path.join(VECTORSTORE_PATH, "payments_store"),
    "profile": os.path.join(VECTORSTORE_PATH, "profile_store")
}

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                page_text = page.get_text()
                if page_text.strip():
                    text += page_text
        if text.strip():
            print(f"Loaded raw text from {file_path}: {len(text)} characters")
            return text
        print(f"No text found in {file_path}. Trying OCR...")

        images = convert_from_path(file_path, dpi=300)
        for i, image in enumerate(images):
            ocr_text = pytesseract.image_to_string(image)
            text += ocr_text + "\n"

        print(f"OCR extracted text from {file_path}: {len(text)} characters")
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
    
    return text


def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])


def load_and_chunk_doc(file_path):
    documents = []
    if file_path.endswith(".pdf"):
        raw_text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        raw_text = extract_text_from_docx(file_path)
    else:
        print(f"Unsupported file format: {file_path}")
        return documents

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_text(raw_text)
    for chunk in chunks:
        documents.append({"text": chunk, "metadata": {"source": os.path.basename(file_path)}})
    return documents




def embed_and_store(documents, persist_dir):
    embedding_model = OpenAIEmbeddings()

    texts = [doc["text"] for doc in documents]
    metadatas = [doc["metadata"] for doc in documents]

    vectorstore = Chroma.from_texts(
        texts=texts,
        embedding=embedding_model,
        metadatas=metadatas,
        persist_directory=persist_dir
    )
    print(f"Stored {len(texts)} chunks in {persist_dir}")


def load_timestamps():
    if os.path.exists(TIMESTAMP_FILE):
        with open(TIMESTAMP_FILE, "r") as f:
            return json.load(f)
    return {}

def save_timestamps(timestamps):
    os.makedirs(os.path.dirname(TIMESTAMP_FILE), exist_ok=True)
    with open(TIMESTAMP_FILE, "w") as f:
        json.dump(timestamps, f)

def get_file_mod_time(filepath):
    return os.path.getmtime(filepath)

def documents_need_update(domain_name, timestamps):
    file_path = AGENT_DOC_PATHS[domain_name]
    mod_time = get_file_mod_time(file_path)
    filename = os.path.basename(file_path)
    if filename not in timestamps or timestamps[filename] < mod_time:
        return True
    return False


def update_timestamps(domain_name):
    file_path = AGENT_DOC_PATHS[domain_name]
    filename = os.path.basename(file_path)
    timestamps = {}
    timestamps[filename] = get_file_mod_time(file_path)
    return timestamps

def process_domain_if_needed(domain_name):
    timestamps = load_timestamps()
    if documents_need_update(domain_name, timestamps):
        print(f"Changes detected in {domain_name} doc — vectorizing...")
        documents = load_and_chunk_doc(AGENT_DOC_PATHS[domain_name])

        if documents:
            embed_and_store(documents, AGENT_STORE_PATHS[domain_name])
            new_timestamps = update_timestamps(domain_name)
            # Merge with old timestamps so we don't lose info for other domains
            timestamps.update(new_timestamps)
            save_timestamps(timestamps)
        else:
            print(f"No documents loaded for {domain_name}. Skipping vectorization.")
    else:
        print(f"No changes in {domain_name} doc — skipping vectorization.")

def vectorize_all_domains_at_startup():
    for domain in AGENT_DOC_PATHS.keys():
        process_domain_if_needed(domain)
        
if __name__ == "__main__":
    vectorize_all_domains_at_startup()
