from app.schemas import FinalResponse, TicketInput
from app.utils.llm import call_llm
import json

SYSTEM = """
You are a customer support assistant.

Follow these rules strictly:
- Detect the user's language from the question and reply in that  language.
- Structure your response following this template:  Thanks + Problem + Solution 
- Use ONLY the provided context; if the context lacks the answer, say so.
- If the ticket is in english , reply in english. If in french, answer in french.
- Output VALID JSON ONLY with exactly these keys:
{
  "response": "<professional reply in the user's language, following the template: thanks + problem summary + solution ",
  "escalate": true | false
}
- If the context does NOT answer the question:
  - Set "response" following the template (thanks + acknowledge problem + explain limitation + action to contact support)
  - Set "escalate" to true
- Otherwise, set "escalate" to false.
- Do NOT add extra keys or any text outside JSON.

Response Template Examples:
- French: "Merci pour votre demande. Nous comprenons que [problème]. [Solution basée sur le contexte]. Action requise: [action spécifique]."
- English: "Thank you for your request. We understand that [problem]. [Solution based on context]. Required action: [specific action]."
"""

def generate_response(
    context: str,
    ticket: TicketInput,
) -> FinalResponse:
    """
    Generate a professional customer support reply based strictly on the provided context.
    """
    prompt = f"""
QUESTION:
{ticket.content}

KNOWLEDGE BASE CONTEXT:
{context}
If the ticket is in english , reply in english. If in french, answer in french.
Return the FINAL ANSWER as a JSON object with EXACTLY these keys:

{{
  "response": "<professional reply in the user's language, following the template: thanks + problem summary + solution + required action>",
  "escalate": true | false
}}

Rules:
1. Detect the language from the QUESTION and respond in that language
2. Structure your response following this template:
   - Remerciements/Thanks: Thank the user for their request
   - Problème/Problem: Acknowledge and summarize their issue
   - Solution: Provide the solution based on the context
   - Action: Specify what action should be taken next

3. If the context does NOT answer the question:
   - Follow the template: thank them, acknowledge the problem, explain you don't have the information, provide action (contact support)
   - Set "escalate" to true
   
4. If the context answers the question:
   - Follow the template: thank them, acknowledge the problem, provide solution from context, specify next action
   - Set "escalate" to false

5. Do NOT add extra keys
6. Do NOT output anything outside JSON

Example structure for French:
"Merci pour votre demande. Nous comprenons que [résumé du problème]. [Solution basée sur le contexte]. Action requise : [action spécifique]."

Example structure for English:
"Thank you for your request. We understand that [problem summary]. [Solution based on context]. Required action: [specific action]."
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
