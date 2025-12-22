# app/agents/responder.py
from app.schemas import FinalResponse
from app.utils.llm import call_llm

SYSTEM = """You rewrite answers to be polite and professional.
Do not add new information.
"""

def generate_response(answer: str, ticket_id: str = "unknown") -> FinalResponse:
    prompt = f"""
Rewrite this as a polite customer support reply:

{answer}
"""
    response = call_llm(SYSTEM, prompt, temperature=0.5)
    return FinalResponse(final_ticket_id=ticket_id, response=response)
