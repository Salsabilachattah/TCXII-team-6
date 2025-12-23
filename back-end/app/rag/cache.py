import hashlib, pickle, time
import sqlite3

CACHE_DB = "embedding_cache.db"
TTL = 86400  # 24h

conn = sqlite3.connect(CACHE_DB)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS embeddings_cache(
    key TEXT PRIMARY KEY,
    embedding BLOB,
    timestamp REAL
)
""")
conn.commit()

def get_cached_embedding(key: str):
    row = c.execute("SELECT embedding, timestamp FROM embeddings_cache WHERE key=?", (key,)).fetchone()
    if row:
        emb, ts = row
        if time.time() - ts < TTL:
            return pickle.loads(emb)
    return None

def cache_embedding(key: str, emb):
    c.execute(
        "REPLACE INTO embeddings_cache(key, embedding, timestamp) VALUES (?, ?, ?)",
        (key, pickle.dumps(emb), time.time())
    )
    conn.commit()

def invalidate_cache_for_key(key: str):
    c.execute("DELETE FROM embeddings_cache WHERE key=?", (key,))
    conn.commit()

def invalidate_cache_for_file(file_path: str):
    key = hashlib.sha256(file_path.encode()).hexdigest()
    invalidate_cache_for_key(key)
