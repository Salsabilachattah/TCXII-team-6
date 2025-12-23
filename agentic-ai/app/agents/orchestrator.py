from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import TicketInput, AnalysisResult, RagResult, EvaluationResult, FinalResponse
from app.agents import analyze_ticket , rag_answer, evaluate, generate_response
from typing import Optional

app = FastAPI(title="Multi-Agent Ticketing System")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def process_ticket(ticket: TicketInput, cosine_threshold: float = 0.6) -> FinalResponse:
    """
    Complete pipeline for a ticket:
    1. Analyze ticket content and extract key words and make summary
    2. Retrieve knowledge via RAG using summary
    3. Evaluate confidence / decision and decide weither to directly respond to ticket or escalate it to Tech support
    4. Generate final response if approved or generate reason of escalation
    """

    # Step 1: Analyze
    
    analysis: AnalysisResult = analyze_ticket(ticket.content)

    # Step 2: RAG retrieval
    rag_result: RagResult = rag_answer(analysis.summary)

    if hasattr(rag_result, "similarities") and rag_result.similarities:
        filtered_answer_chunks = []
        filtered_sources = []
        for chunk, score in zip(rag_result.context.split("\n"), rag_result.similarities):
            if score >= cosine_threshold:
                filtered_answer_chunks.append(chunk)
                filtered_sources.append(rag_result.sources[rag_result.context.split("\n").index(chunk)])
        rag_result.context = "\n".join(filtered_answer_chunks)
        rag_result.sources = filtered_sources

    # Step 3: Evaluate
    evaluation: EvaluationResult = evaluate(
    summary=analysis.summary,
    rag_answer=rag_result.context,
    snippets_confidences=[rag_result.similarity_score] * 5,  # assume 5 snippets
    keywords=analysis.keywords
)
    print(f"Evaluation decision: {evaluation.decision}, reason: {evaluation.reason}")
    # Step 4: Generate response if approved
    if evaluation.decision == "APPROVE":
        final_response: FinalResponse = generate_response(
            context=rag_result.context,
            ticket=ticket
        )
    else:
        # Escalated ticket
        final_response = FinalResponse(
            ticket_id=ticket.ticket_id,
            response=f"Ticket escalated to human support.",
            escalated=True,
            reason=evaluation.reason
        )
    
    return final_response




