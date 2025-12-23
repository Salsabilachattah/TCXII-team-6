from app.schemas import FinalResponse, TicketInput
from app.utils.llm import call_llm
import json

SYSTEM = """
You are a customer support assistant.

You MUST follow these rules strictly:
- Reply in the SAME language as the customer's question.
- Use ONLY the provided context.
- Do NOT invent, infer, or add information.
- Output VALID JSON ONLY.
"""

def generate_response(
    context: str,
    ticket: TicketInput,
) -> FinalResponse:
    """
    Generate a professional customer support reply based strictly on the provided context.
    """

    prompt = f"""
CUSTOMER QUESTION:
{ticket.content}

KNOWLEDGE BASE CONTEXT:
{context}

Return the FINAL ANSWER as a JSON object with EXACTLY these keys:

{{
  "response": "<short professional reply in the SAME language as the customer, using ONLY the context>",
  "escalate": true | false
}}

Rules:
- If the context does NOT answer the question:
  - Set "response" to EXACTLY:
    "I'm sorry, but I don't have enough information to answer your question at this time. Please contact our support team for further assistance."
  - Set "escalate" to true
- Otherwise:
  - Provide a short, clear, professional reply
  - Set "escalate" to false
- Do NOT add extra keys
- Do NOT output anything outside JSON
"""

    raw = call_llm(
        SYSTEM,
        prompt,
        temperature=0.1,
    )
    
    if raw.startswith("```"):
        raw = raw.split("```")[1]
    if raw.startswith("json"):
        raw = raw[4:]
    parsed = json.loads(raw)
# Try to parse JSON
    
    
 
    if parsed.get("escalate") is True:
        return FinalResponse(
            response=parsed.get("response"),
            ticket_id=ticket.ticket_id,
            escalated=True,
            reason="Insufficient information to answer the ticket."
        )

    return FinalResponse(
        response=parsed.get("response"),
        ticket_id=ticket.ticket_id,
        escalated=False,
        reason="Answered by automated system."
    )
