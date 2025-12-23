from app.schemas import RagResult
from app.rag.vectorstore import retrieve

def rag_answer(summary: str) -> RagResult:
    """
    Perform Retrieval-Augmented Generation (RAG) retrieval from a ticket summary.

    - Retrieve top N=5 snippets
    - Apply reranking
    - Sort snippets by relevance
    - Return confidence scores in [0, 1]
    """

    query = summary

    # 1. First-pass retrieval 
    docs_with_scores = retrieve(query, k=5)
    # [(doc, raw_score), ...]

    if not docs_with_scores:
        return RagResult(
            context="INSUFFICIENT_CONTEXT",
            sources=[],
            similarity_score=0.0
        )

    # 2. Reranking (placeholder logic)
    # If score = distance → lower is better, so invert
    reranked = [
        {
            "doc": doc,
            "rerank_score": 1.0 / (score + 1e-8)
        }
        for doc, score in docs_with_scores
    ]

    # 3. Sort by rerank score (descending)
    reranked.sort(key=lambda x: x["rerank_score"], reverse=True)

    # 4. Keep top N=5 snippets
    top_docs = reranked[:5]

    # 5. Normalize confidence scores to [0, 1]
    scores = [d["rerank_score"] for d in top_docs]
    min_s, max_s = min(scores), max(scores)
    denom = (max_s - min_s) or 1.0

    snippets = []
    sources = []

    for d in top_docs:
        confidence = (d["rerank_score"] - min_s) / denom
        snippets.append(d["doc"].page_content)
        sources.append(d["doc"].metadata.get("source", "unknown"))

    # 6. Final context = sorted snippets
    context = "\n".join(snippets)

    return RagResult(
        context=context,
        sources=sources,
        similarity_score=round(max((s - min_s) / denom for s in scores), 3)
    )
