from langchain_community.vectorstores.faiss import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from app.rag.cache import get_cached_embedding, cache_embedding
import hashlib

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

# Wrapper that checks persistent cache before computing
def embed_with_cache(text: str):
    key = hashlib.sha256(text.encode()).hexdigest()
    cached = get_cached_embedding(key)
    if cached is not None:
        return cached
    emb = get_embeddings().embed(text)
    cache_embedding(key, emb)
    return emb

def get_db():
    global _db
    if _db is None:
        _db = FAISS.load_local(
            "vectorstore",
            get_embeddings(),
            allow_dangerous_deserialization=True
        )
    return _db

def retrieve(query: str, k=5):
    return get_db().similarity_search_with_score(query, k=k)
