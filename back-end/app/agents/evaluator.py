# app/agents/evaluator.py
from app.schemas import EvaluationResult

def evaluate(summary: str, rag_answer: str, keywords: list[str], similarity_score: float) -> EvaluationResult:
    """
    Evaluate the RAG answer and return a decision and confidence score.
    
    Parameters:
    - summary: ticket summary
    - rag_answer: answer retrieved from KB
    - keywords: extracted keywords from ticket
    - similarity_score: similarity score of the retrieved answer
    """
    
    if "INSUFFICIENT_CONTEXT" in rag_answer:
        return EvaluationResult(
            decision="ESCALATE",
            confidence_score=0.0,
            reason="No KB match"
        )
        
    if similarity_score < 0.6:
        return EvaluationResult(
            decision="ESCALATE",
            confidence_score=similarity_score,
            reason="Low confidence in KB answer"
        )
    else:
        return EvaluationResult(
            decision="APPROVE",
            confidence_score=similarity_score,
            reason="Sufficient confidence in KB answer"
        )
