import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import pickle

load_dotenv()

PDF_PATH = "./clients/poway/data/PowayGPT_Detailed_Training.pdf"
VECTORSTORE_PATH = "./clients/poway/data"

def load_pdf_text(path):
    reader = PdfReader(path)
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

from langchain_core.documents import Document  # Add this import at the top

def split_text(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_documents([Document(page_content=text)])


def main():
    print("📄 Loading PDF...")
    text = load_pdf_text(PDF_PATH)

    print("✂️ Splitting into chunks...")
    chunks = split_text(text)

    print("🧠 Creating vector store...")
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts([doc.page_content for doc in chunks], embeddings)


    print("💾 Saving vector store...")
    VECTOR_DIR = "./clients/poway/data"
    vectorstore.save_local(VECTOR_DIR)


    print("✅ Ingestion complete.")

if __name__ == "__main__":
    main()
