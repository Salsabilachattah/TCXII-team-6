# app/agents/evaluator.py
from app.schemas import EvaluationResult

def evaluate(summary: str, rag_answer: str) -> EvaluationResult:
    if "INSUFFICIENT_CONTEXT" in rag_answer:
        return EvaluationResult(
            decision="ESCALATE",
            confidence_score=0.0,
            reason="No KB match"
        )
  
#   we need to implement a valid confidence score calculation mechnanism here 
    confidence = 0.8 

    if confidence < 0.6:
        return EvaluationResult(
            decision="ESCALATE",
            confidence_score=confidence,
            reason="Low confidence in KB answer"
        )
    else : 
        return EvaluationResult(
           decision="APPROVE",
           confidence_score=confidence,
           reason="Clear KB answer"
     )
