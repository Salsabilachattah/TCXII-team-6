from fastapi import FastAPI
from app.schemas import TicketInput, FinalResponse
from app.agents.orchestrator import process_ticket

app = FastAPI(
    title="Multi-Agent Ticket System",
    description="API for ticket processing pipeline",
    version="1.0"
)

@app.post("/ticket", response_model=FinalResponse)
def handle_ticket(ticket: TicketInput):
    """
    Accepts a ticket and returns the processed response
    """
    print(f"\n=== RECEIVED TICKET ===")
    print(f"ID: {ticket.ticket_id}")
    print(f"Content: {ticket.content}")
    print(f"Full object: {ticket.model_dump()}")
    print("=" * 30)
    
    final_response = process_ticket(ticket)
    
    print(f"\n=== FINAL RESPONSE ===")
    print(f"Response: {final_response.response}")
    print("=" * 30)
    return final_response
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)