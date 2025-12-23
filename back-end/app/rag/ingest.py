import os
from pathlib import Path
from langchain_community.vectorstores.faiss import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.docstore.document import Document
from PIL import Image
import pytesseract
import pdfplumber

# ---------- Config ----------
DOCS_FOLDER = "docs/"
VECTORSTORE_PATH = "vectorstore"
CHUNK_SIZE = 200     # target words per chunk
CHUNK_OVERLAP = 50   # overlap in words
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
ALLOWED_CATEGORIES = {"policies", "faq", "guide"}  # KB categories

# ---------- Helper functions ----------
def load_text_file(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if ext in {".md", ".txt"}:
        return Path(file_path).read_text(encoding="utf-8")
    return ""

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
    return text

def extract_text_from_image(file_path: str) -> str:
    try:
        image = Image.open(file_path)
        return pytesseract.image_to_string(image)
    except Exception as e:
        print(f"Error reading image {file_path}: {e}")
        return ""

def split_markdown_blocks(text: str):
    lines = text.splitlines()
    blocks = []
    current = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            if current:
                blocks.append("\n".join(current).strip())
                current = []
            current.append(line)
        elif stripped == "":
            if current:
                blocks.append("\n".join(current).strip())
                current = []
        else:
            current.append(line)
    if current:
        blocks.append("\n".join(current).strip())
    return [b for b in blocks if b]

def chunk_text(text: str, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Chunk text by logical blocks, then pack to target word count with overlap."""
    blocks = split_markdown_blocks(text)
    if not blocks:
        words = text.split()
        return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), max(1, chunk_size - overlap))]
    
    chunks = []
    buffer = []
    buffer_words = 0

    for block in blocks:
        block_words = block.split()
        if buffer_words + len(block_words) <= chunk_size or not buffer:
            buffer.append(block)
            buffer_words += len(block_words)
            continue

        chunks.append("\n\n".join(buffer))
        buffer = []
        buffer_words = 0

        if overlap > 0 and chunks:
            prev_words = chunks[-1].split()
            carry = prev_words[-overlap:] if len(prev_words) > overlap else prev_words
            if carry:
                buffer.append(" ".join(carry))
                buffer_words = len(carry)

        buffer.append(block)
        buffer_words += len(block_words)

    if buffer:
        chunks.append("\n\n".join(buffer))
    return chunks

# ---------- Main ingestion ----------
def ingest_docs():
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    all_docs = []

    for file_path in Path(DOCS_FOLDER).rglob("*"):
        ext = file_path.suffix.lower()
        text = ""

        if ext in {".md", ".txt"}:
            text = load_text_file(file_path)
            doc_type = "official"
        elif ext == ".pdf":
            text = extract_text_from_pdf(file_path)
            doc_type = "pdf"
        elif ext in {".png", ".jpg", ".jpeg"}:
            text = extract_text_from_image(file_path)
            doc_type = "image"
        else:
            continue  # unsupported format

        if not text.strip():
            continue

        # Determine category from folder, fallback to 'uncategorized'
        category = file_path.parent.name.lower()
        if category not in ALLOWED_CATEGORIES:
            category = "uncategorized"

        chunks = chunk_text(text)

        for idx, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "source": file_path.name,
                    "category": category,
                    "doc_type": doc_type,
                    "chunk_id": idx
                }
            )
            all_docs.append(doc)

    if not all_docs:
        print("No documents found to ingest.")
        return

    db = FAISS.from_documents(all_docs, embeddings, normalize_L2=True)
    db.save_local(VECTORSTORE_PATH)
    print(f"Ingested {len(all_docs)} chunks into '{VECTORSTORE_PATH}'.")

# ---------- Run ----------
if __name__ == "__main__":
    ingest_docs()
