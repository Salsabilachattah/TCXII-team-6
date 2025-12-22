# app/agents/rag.py
from app.schemas import RagResult
from app.rag.vectorstore import retrieve

def rag_answer(summary: str, keywords: list[str]) -> RagResult:
    query = summary + " " + " ".join(keywords)
    docs = retrieve(query)

    if not docs:
        return RagResult(
            answer="INSUFFICIENT_CONTEXT",
            sources=[]
        )

    answer = "\n".join(d.page_content for d in docs)
    sources = [d.metadata.get("source", "unknown") for d in docs]

    return RagResult(answer=answer, sources=sources)
