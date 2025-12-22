# app/rag/ingest.py

import os
from pathlib import Path
from langchain_community.vectorstores.faiss import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.docstore.document import Document


# ---------- Config ----------
DOCS_FOLDER = "docs/"
VECTORSTORE_PATH = "vectorstore"
CHUNK_SIZE = 200     # words per chunk
CHUNK_OVERLAP = 50  # overlap in words
EMBEDDING_MODEL_NAME="sentence-transformers/all-MiniLM-L6-v2"
# ---------- Helper functions ----------
def load_doc(file_path: str) -> str:
    """Read txt files"""
    ext = Path(file_path).suffix.lower()
    if ext == ".txt":
        return Path(file_path).read_text(encoding="utf-8")
    else:
        print(f"Unsupported file format: {file_path}")
        return ""

def chunk_text(text: str, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunks.append(" ".join(words[i:i+chunk_size]))
    return chunks

# ---------- Main ingestion ----------
def ingest_docs():
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    all_docs = []

    # Loop through all files
    for file_path in Path(DOCS_FOLDER).rglob("*.txt"):
        text = load_doc(file_path)
        if not text.strip():
            continue

        category = file_path.parent.name  # folder name as category

        chunks = chunk_text(text)
        for idx, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "source": file_path.name,
                    "category": category,
                    "doc_type": "official",
                    "chunk_id": idx
                }
            )
            all_docs.append(doc)

    if not all_docs:
        print("No documents found to ingest.")
        return

    # Build FAISS vectorstore
    db = FAISS.from_documents(all_docs, embeddings)
    db.save_local(VECTORSTORE_PATH)
    print(f"Ingested {len(all_docs)} chunks into '{VECTORSTORE_PATH}'.")

# ---------- Run ----------
if __name__ == "__main__":
    ingest_docs()
