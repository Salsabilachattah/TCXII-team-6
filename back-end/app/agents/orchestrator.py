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
    1. Analyze ticket content
    2. Retrieve knowledge via RAG
    3. Evaluate confidence / decision
    4. Generate final response (if approved)
    """

    # Step 1: Analyze
    
    analysis: AnalysisResult = analyze_ticket(ticket.content)

    # Step 2: RAG retrieval
    # rag_result: RagResult = rag_answer(analysis.summary, analysis.keywords)
    rag_result: RagResult = rag_answer(analysis.summary)

    # Optionally filter chunks below cosine similarity threshold
    if hasattr(rag_result, "similarities") and rag_result.similarities:
        filtered_answer_chunks = []
        filtered_sources = []
        for chunk, score in zip(rag_result.answer.split("\n"), rag_result.similarities):
            if score >= cosine_threshold:
                filtered_answer_chunks.append(chunk)
                filtered_sources.append(rag_result.sources[rag_result.answer.split("\n").index(chunk)])
        rag_result.answer = "\n".join(filtered_answer_chunks)
        rag_result.sources = filtered_sources

    # Step 3: Evaluate
    evaluation: EvaluationResult = evaluate(
        summary=analysis.summary,
        rag_answer=rag_result.answer,
        keywords=analysis.keywords,
        similarity_score=getattr(rag_result, "similarity_score", 0.0)
    )

    # Step 4: Generate response if approved
    if evaluation.decision == "APPROVE":
        final_response: FinalResponse = generate_response(
            answer=rag_result.answer,
            ticket=ticket
        )
    else:
        # Escalated ticket
        final_response = FinalResponse(
            response=f"Ticket escalated to human support. Reason: {evaluation.reason}"
        )
    
    return final_response




