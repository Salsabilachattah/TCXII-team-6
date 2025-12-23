# tests/test_similarity.py

import pytest
from app.rag.vectorstore import get_embeddings
from langchain_community.docstore.document import Document
from langchain_community.vectorstores.faiss import FAISS

# ---------- Sample KB documents ----------
SAMPLE_DOCS = [
    Document(page_content="How to reset your password", metadata={"source": "doc1"}),
    Document(page_content="Setting up two-factor authentication", metadata={"source": "doc2"}),
    Document(page_content="Troubleshooting login issues", metadata={"source": "doc3"}),
]

# ---------- Fixture: FAISS DB on sample docs ----------
@pytest.fixture
def faiss_sample():
    embeddings = get_embeddings()
    db = FAISS.from_documents(SAMPLE_DOCS, embeddings, normalize_L2=True)
    return db

# ---------- Unit test: top-K similarity ----------
def test_similarity_top_k(faiss_sample):
    query = "I forgot my password, how can I reset it?"
    results = faiss_sample.similarity_search_with_score(query, k=3)

    print(f"\nQuery: {query}")
    print("Top-K retrieved documents:")

    # Extract L2 distances and convert to cosine similarity
    top_distances = [score for _, score in results]
    cosine_sim = [1 - (d**2)/2 for d in top_distances]  # for normalized embeddings

    for i, (doc_score_pair, sim) in enumerate(zip(results, cosine_sim), start=1):
        doc, l2_dist = doc_score_pair
        print(f"{i}. Source: {doc.metadata['source']}, L2 distance: {l2_dist:.4f}, Cosine similarity: {sim:.4f}")

    # Assert at least one retrieved doc has similarity > 0.8
    assert any(sim > 0.8 for sim in cosine_sim), \
        "Top-K similarity <0.8; check embeddings, chunking, or retrieval logic"

# ---------- Optional: test multiple queries ----------
@pytest.mark.parametrize("query, expected_source", [
    ("How can I reset my password?", "doc1"),
    ("Enable two-factor authentication", "doc2"),
    ("Cannot log into my account", "doc3"),
])
def test_similarity_multiple_queries(faiss_sample, query, expected_source):
    results = faiss_sample.similarity_search_with_score(query, k=3)
    top_doc = results[0][0]  # first document
    print(f"\nQuery: {query} -> Top source: {top_doc.metadata['source']}")
    assert top_doc.metadata["source"] == expected_source, \
        f"Expected top doc {expected_source}, got {top_doc.metadata['source']}"
