from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.dependencies import get_db
from app.core.permissions import require_roles
from app.schemas.ticket import (
    TicketCreate,
    TicketResponse,
    TicketDetail,
    TicketListResponse,
    AgentResponse,
    AgentResponseDetail,
    TicketFeedback,
    FeedbackResponse,
    TicketEscalation,
    EscalationResponse,
)
from app.api.tickets import controller

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("/", response_model=TicketResponse)
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db), current_user = Depends(require_roles("client", "admin"))):
    return controller.create_ticket(ticket, db, current_user)


@router.get("/list", response_model=TicketListResponse)
def get_client_tickets(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), current_user = Depends(require_roles("client", "admin"))):
    return controller.get_client_tickets(page, page_size, db, current_user)


@router.get("/{ticket_id}", response_model=TicketDetail)
def get_ticket_detail(ticket_id: int, db: Session = Depends(get_db), current_user = Depends(require_roles("client", "admin"))):
    return controller.get_ticket_detail(ticket_id, db, current_user)


@router.post("/{ticket_id}/feedback", response_model=FeedbackResponse)
def submit_feedback(ticket_id: int, feedback: TicketFeedback, db: Session = Depends(get_db), current_user = Depends(require_roles("client", "admin"))):
    return controller.submit_feedback(ticket_id, feedback, db, current_user)


# Agent endpoints
@router.get("/agent/list", response_model=TicketListResponse)
def get_agent_tickets(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), current_user = Depends(require_roles("agent", "admin"))):
    return controller.get_agent_tickets(page, page_size, db, current_user)


@router.get("/agent/search", response_model=TicketListResponse)
def search_tickets(ticket_id: Optional[int] = Query(None), title: Optional[str] = Query(None), client_id: Optional[int] = Query(None), category: Optional[str] = Query(None), escalated: Optional[bool] = Query(None), processed: Optional[bool] = Query(None), page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), current_user = Depends(require_roles("agent", "admin"))):
    return controller.search_tickets(ticket_id, title, client_id, category, escalated, processed, page, page_size, db, current_user)


@router.get("/agent/{ticket_id}", response_model=TicketDetail)
def get_agent_ticket_detail(ticket_id: int, db: Session = Depends(get_db), current_user = Depends(require_roles("agent", "admin"))):
    return controller.get_agent_ticket_detail(ticket_id, db, current_user)


@router.post("/agent/{ticket_id}/response", response_model=AgentResponseDetail)
def respond_to_ticket(ticket_id: int, response: AgentResponse, db: Session = Depends(get_db), current_user = Depends(require_roles("agent", "admin"))):
    return controller.respond_to_ticket(ticket_id, response, db, current_user)


@router.post("/agent/{ticket_id}/escalate", response_model=EscalationResponse)
def escalate_ticket(ticket_id: int, escalation: TicketEscalation, db: Session = Depends(get_db), current_user = Depends(require_roles("agent", "admin"))):
    return controller.escalate_ticket(ticket_id, escalation, db, current_user)
