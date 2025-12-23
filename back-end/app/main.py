from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine

# Agents
from app.schemas import TicketInput, FinalResponse
from app.agents.orchestrator import process_ticket

# Routers (if you have other routers)
from app.api.router import api_router


def create_app() -> FastAPI:
    """
    Factory for FastAPI app
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        description="Multi-Agent Ticket System API",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # change in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include additional routers
    app.include_router(api_router)

    # Startup event: create DB tables (before Alembic)
    @app.on_event("startup")
    def on_startup():
        Base.metadata.create_all(bind=engine)

    # Health check
    @app.get("/", tags=["Health"])
    def health_check():
        return {
            "status": "ok",
            "app": settings.APP_NAME,
            "environment": settings.ENV,
        }

    # Ticket endpoint
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

    return app


# Create app
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)