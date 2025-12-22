# app/agents/rag.py
from app.schemas import RagResult
from app.rag.vectorstore import retrieve

def rag_answer(summary: str, keywords: list[str]) -> RagResult:
    query = summary + " " + " ".join(keywords)
    docs = retrieve(query)  # assume each doc has `page_content`, `metadata`, and `similarity` attributes

    if not docs:
        return RagResult(
            answer="INSUFFICIENT_CONTEXT",
            sources=[],
            similarity_score=0.0  # optional field for evaluator
        )

    # Concatenate all retrieved documents
    answer = "\n".join(d.page_content for d in docs)
    sources = [d.metadata.get("source", "unknown") for d in docs]

    # Take highest similarity among returned docs
    highest_similarity = max(getattr(d, "similarity", 0.8) for d in docs)

    return RagResult(
        answer=answer,
        sources=sources,
        similarity_score=highest_similarity  # pass this to evaluator
    )
