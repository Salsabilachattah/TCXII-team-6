from langchain_community.vectorstores.faiss import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Lazy initialization to avoid loading on every import
_embeddings = None
_db = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    return _embeddings

def get_db():
    global _db
    if _db is None:
        _db = FAISS.load_local(
            "vectorstore",
            get_embeddings(),
            allow_dangerous_deserialization=True   
        )
    return _db

# Retrieve top-k relevant chunks
def retrieve(query: str, k=4):
    return get_db().similarity_search(query, k=k)
