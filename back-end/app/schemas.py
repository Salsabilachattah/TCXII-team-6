from pydantic import BaseModel
from typing import List, Literal, Optional

class TicketInput(BaseModel):
    ticket_id: str
    content: str

class AnalysisResult(BaseModel):
    summary: str
    keywords: List[str]

class RagResult(BaseModel):
    context: str
    sources: List[str]
    similarity_score: Optional[float] = 0.0  

class EvaluationResult(BaseModel):
    decision: Literal["APPROVE", "ESCALATE"]
    confidence_score: float
    reason: str

class FinalResponse(BaseModel):
    ticket_id: str
    response: str
    escalated: bool
    reason: str
