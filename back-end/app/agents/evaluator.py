# app/agents/evaluator.py
from app.schemas import EvaluationResult

def evaluate(summary: str, rag_answer: str, keywords: list[str], similarity_score: float = 0.8) -> EvaluationResult:
    """
    Evaluate the RAG answer and return a decision and confidence score.
    
    Parameters:
    - summary: ticket summary
    - rag_answer: answer retrieved from KB
    - keywords: extracted keywords from ticket
    - similarity_score: optional, similarity of top KB doc (0-1)
    """
    
    if "INSUFFICIENT_CONTEXT" in rag_answer:
        return EvaluationResult(
            decision="ESCALATE",
            confidence_score=0.0,
            reason="No KB match"
        )
    
    if keywords:
        keyword_coverage = sum(1 for kw in keywords if kw.lower() in rag_answer.lower()) / len(keywords)
    else:
        keyword_coverage = 0.0
    
    length_factor = min(len(rag_answer) / 200, 1.0)  # cap at 1.0 for long answers
    
    confidence = 0.5 * similarity_score + 0.3 * keyword_coverage + 0.2 * length_factor
    
    if confidence < 0.6:
        return EvaluationResult(
            decision="ESCALATE",
            confidence_score=confidence,
            reason="Low confidence in KB answer"
        )
    else:
        return EvaluationResult(
            decision="APPROVE",
            confidence_score=confidence,
            reason="Sufficient confidence in KB answer"
        )
