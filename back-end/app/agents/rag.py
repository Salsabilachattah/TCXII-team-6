# app/agents/rag.py
from app.schemas import RagResult
from app.rag.vectorstore import retrieve
def rag_answer(summary: str) -> RagResult:
    query = summary 
    docs_with_scores = retrieve(query)  
    
    if not docs_with_scores:
        return RagResult(
            answer="INSUFFICIENT_CONTEXT",
            sources=[],
            similarity_score=0.0
        )

    answer = "\n".join(doc.page_content for doc, _ in docs_with_scores)
    sources = [doc.metadata.get("source", "unknown") for doc, _ in docs_with_scores]
    for doc, score in docs_with_scores:
        print(f"Source: {doc.metadata.get('source', 'unknown')}, Score: {score}")
    # Convert FAISS distance (lower is better) to similarity in (0,1]: 1/(1+distance)
    highest_similarity = max(1.0 / score for _, score in docs_with_scores)

    return RagResult(
        answer=answer,
        sources=sources,
        similarity_score=highest_similarity
    )
