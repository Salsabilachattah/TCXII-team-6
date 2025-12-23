# app/agents/evaluator.py
from app.schemas import EvaluationResult
from textblob import TextBlob  # for simple sentiment analysis, can swap with any lib

# Configurable thresholds / rules
CONFIDENCE_THRESHOLD = 0.6
NEGATIVE_EMOTION_THRESHOLD = -0.2  # sentiment polarity below this triggers escalation

def evaluate(summary: str, rag_answer: str, snippets_confidences: list[float], keywords: list[str]) -> EvaluationResult:
    """
    Evaluate the RAG answer and return a decision and confidence score.

    Parameters:
    - summary: ticket summary
    - rag_answer: answer retrieved from KB
    - snippets_confidences: list of confidence scores for each snippet (0-1)
    - keywords: extracted keywords from ticket
    """

    # 1. Average confidence check
    avg_conf = sum(snippets_confidences) / (len(snippets_confidences) or 1)

    if "INSUFFICIENT_CONTEXT" in rag_answer or avg_conf < CONFIDENCE_THRESHOLD:
        reason = "Low KB confidence" if avg_conf < CONFIDENCE_THRESHOLD else "No KB match"
        return EvaluationResult(
            decision="ESCALATE",
            confidence_score=round(avg_conf, 3),
            reason=reason
        )

    # 2. Negative emotion detection in summary
    try:
        sentiment = TextBlob(summary).sentiment.polarity
        if sentiment < NEGATIVE_EMOTION_THRESHOLD:
            return EvaluationResult(
                decision="ESCALATE",
                confidence_score=round(avg_conf, 3),
                reason="Negative sentiment detected in ticket"
            )
    except Exception as e:
        # fallback on exception
        return EvaluationResult(
            decision="ESCALATE",
            confidence_score=round(avg_conf, 3),
            reason=f"Exception during evaluation: {str(e)}"
        )

    # 3. Default approve
    return EvaluationResult(
        decision="APPROVE",
        confidence_score=round(avg_conf, 3),
        reason="Sufficient KB confidence and neutral/positive sentiment"
    )
