"""
Full Multi-Agent System Test
Tests the complete ticket processing pipeline:
1. Analyzer extracts summary/keywords
2. RAG retrieves relevant knowledge
3. Evaluator decides APPROVE/ESCALATE
4. Responder generates final reply
"""

import sys
import json
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.agents.analyzer import analyze_ticket
from app.agents.rag import rag_answer
from app.agents.evaluator import evaluate
from app.agents.responder import generate_response


def test_ticket(ticket_id: str, ticket_content: str):
    """Test a single ticket through the full pipeline"""
    print(f"\n{'='*70}")
    print(f"TICKET #{ticket_id}")
    print(f"{'='*70}")
    print(f"Content: {ticket_content}")
    print(f"-"*70)
    
    try:
        # Step 1: Analyze
        print("🔍 STEP 1: Analyzing ticket...")
        analysis = analyze_ticket(ticket_content)
        print(f"   Summary: {analysis.summary}")
        print(f"   Keywords: {analysis.keywords}")
        print(f"   JSON Output:")
        print(json.dumps(analysis.model_dump(), indent=2))
        
        # Step 2: RAG retrieval
        print("\n📚 STEP 2: Searching knowledge base...")
        rag_result = rag_answer(analysis.summary)

        print(f"   Answer length: {len(rag_result.answer)} chars")
        print(f"   Sources: {rag_result.sources}")
        if rag_result.answer == "INSUFFICIENT_CONTEXT":
            print(f"   ⚠️  No knowledge base match found")
        else:
            print(f"   Preview: {rag_result.answer[:150]}...")
        print(f"   JSON Output:")
        print(json.dumps(rag_result.model_dump(), indent=2))
        
        # Step 3: Evaluate
        print("\n⚖️  STEP 3: Evaluating confidence...")
        evaluation = evaluate(analysis.summary, rag_result.answer, analysis.keywords,rag_result.similarity_score)
        print(f"   Decision: {evaluation.decision}")
        print(f"   Confidence: {evaluation.confidence_score}")
        print(f"   Reason: {evaluation.reason}")
        print(f"   JSON Output:")
        print(json.dumps(evaluation.model_dump(), indent=2))
        
        # Step 4: Generate response (if approved)
        if evaluation.decision == "APPROVE":
            print("\n✅ STEP 4: Generating final response...")
            final = generate_response(rag_result.answer, ticket_content)
            print(f"   Response: {final.response[:200]}...")
            print(f"   JSON Output:")
            print(json.dumps(final.model_dump(), indent=2))
        else:
            print("\n🚨 STEP 4: Ticket escalated to human support")
        
        print(f"\n{'='*70}")
        print(f"✓ Pipeline completed for ticket #{ticket_id}")
        print(f"{'='*70}\n")
        
        return {
            "ticket_id": ticket_id,
            "analysis": analysis,
            "rag_result": rag_result,
            "evaluation": evaluation,
            "success": True
        }
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print(f"{'='*70}\n")
        return {
            "ticket_id": ticket_id,
            "error": str(e),
            "success": False
        }


def run_test_suite():
    """Run multiple test cases"""
    print("\n" + "="*70)
    print("MULTI-AGENT TICKETING SYSTEM - FULL TEST SUITE")
    print("="*70)
    
    test_cases = [
        {
            "id": "T001",
            "content": "J'ai oublié mon mot de passe et je ne peux pas me connecter à mon compte."
        },
        {
            "id": "T002", 
            "content": "Comment activer l'authentification à deux facteurs pour sécuriser mon compte ?"
        },
        {
            "id": "T003",
            "content": "Quels sont vos tarifs et offres disponibles ?"
        },
        {
            "id": "T004",
            "content": "Mon compte a été verrouillé après plusieurs tentatives de connexion."
        },
        {
            "id": "T005",
            "content": "xyz random query that will not match anything in the knowledge base"
        }
    ]
    
    results = []
    for test in test_cases:
        result = test_ticket(test["id"], test["content"])
        results.append(result)
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    successful = sum(1 for r in results if r["success"]) 
    print(f"Total tickets tested: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")
    
    # Decision breakdown
    approved = sum(1 for r in results if r["success"] and r.get("evaluation") and r["evaluation"].decision == "APPROVE")
    escalated = sum(1 for r in results if r["success"] and r.get("evaluation") and r["evaluation"].decision == "ESCALATE")
    print(f"\nApproved: {approved}")
    print(f"Escalated: {escalated}")
    print("="*70 + "\n")


if __name__ == "__main__":
    # First ensure vectorstore is built
    print("\n⚠️  Make sure you've run ingestion first:")
    print("   python back-end/app/main.py ingest\n")
    
    # Run single ticket test or full suite
    if len(sys.argv) > 1:
        # Test single ticket from command line
        ticket_content = " ".join(sys.argv[1:])
        test_ticket("CUSTOM", ticket_content)
    else:
        # Run full test suite
        run_test_suite()

    
    results = []
    # for test in test_cases:
    #     result = test_ticket(test["id"], test["content"])
    #     results.append(result)
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    successful = sum(1 for r in results if r["success"])
    print(f"Total tickets tested: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")
    
    # Decision breakdown
    approved = sum(1 for r in results if r["success"] and r.get("evaluation") and r["evaluation"].decision == "APPROVE")
    escalated = sum(1 for r in results if r["success"] and r.get("evaluation") and r["evaluation"].decision == "ESCALATE")
    print(f"\nApproved: {approved}")
    print(f"Escalated: {escalated}")
    print("="*70 + "\n")


if __name__ == "__main__":
    # First ensure vectorstore is built
    print("\n⚠️  Make sure you've run ingestion first:")
    print("   python back-end/app/main.py ingest\n")
    
    # Run single ticket test or full suite
    if len(sys.argv) > 1:
        # Test single ticket from command line
        ticket_content = " ".join(sys.argv[1:])
        test_ticket("CUSTOM", ticket_content)
    else:
        # Run full test suite
        run_test_suite()
