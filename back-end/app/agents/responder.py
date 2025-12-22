# app/agents/responder.py
from app.schemas import FinalResponse
from app.utils.llm import call_llm

SYSTEM = """You rewrite answers with the same language as the ticket's to be polite and professional.
Do not add new information.
"""

def generate_response(answer: str, ticket_content: str ) -> FinalResponse:
    prompt = f"""
Given this customer support ticket :
{ticket_content}
Extract only the relevant information from the following answer and rewrite it to be a polite and professional response to the customer:
{answer}

"""
    response = call_llm(SYSTEM, prompt, temperature=0.3)
    return FinalResponse(response=response)
    # return FinalResponse(final_ticket_id=ticket_id, response=response)
