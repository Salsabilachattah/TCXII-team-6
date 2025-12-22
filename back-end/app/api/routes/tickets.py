from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.dependencies import get_db
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

from app.models.tickets import Ticket
from app.models.users import User
from datetime import datetime
import math

router = APIRouter(prefix="/tickets", tags=["Tickets"])


# ========== CLIENT ENDPOINTS ==========

@router.post("/", response_model=TicketResponse)
async def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    current_user_id: int = None  # Would come from auth
):
    """
    Client submits a new ticket via form
    - Sujet (title)
    - Description complète (description)
    - Catégorie (category)
    """
    if current_user_id is None:
        raise HTTPException(status_code=401, detail="Authentication required (stub)")

    db_ticket = Ticket(
        title=ticket.title,
        description=ticket.description,
        category=ticket.category,
        client_id=current_user_id,
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)

    return TicketResponse(
        id=db_ticket.id,
        title=db_ticket.title,
        description=db_ticket.description,
        category=db_ticket.category,
        client_id=db_ticket.client_id,
        escalated=db_ticket.escalated,
        processed=db_ticket.processed,
        created_at=db_ticket.created_at,
    )


@router.get("/list", response_model=TicketListResponse)
async def get_client_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user_id: int = None  # Would come from auth
):
    """
    Client views their tickets with pagination
    """
    if current_user_id is None:
        raise HTTPException(status_code=401, detail="Authentication required (stub)")

    query = db.query(Ticket).filter(Ticket.client_id == current_user_id).order_by(Ticket.created_at.desc())
    total = query.count()
    offset = (page - 1) * page_size
    rows = query.offset(offset).limit(page_size).all()

    items = [
        {
            "id": t.id,
            "title": t.title,
            "category": t.category,
            "escalated": t.escalated,
            "processed": t.processed,
            "created_at": t.created_at,
        }
        for t in rows
    ]

    total_pages = math.ceil(total / page_size) if page_size else 1

    return TicketListResponse(items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)


@router.get("/{ticket_id}", response_model=TicketDetail)
async def get_ticket_detail(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = None  # Would come from auth
):
    """
    Client views details of their ticket
    """
    if current_user_id is None:
        raise HTTPException(status_code=401, detail="Authentication required (stub)")

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id, Ticket.client_id == current_user_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return TicketDetail(
        id=ticket.id,
        title=ticket.title,
        description=ticket.description,
        category=ticket.category,
        client_id=ticket.client_id,
        agent_id=ticket.agent_id,
        escalated=ticket.escalated,
        processed=ticket.processed,
        response=ticket.response,
        responded_at=ticket.responded_at,
        feedback_satisfied=ticket.feedback_satisfied,
        feedback_reason=ticket.feedback_reason,
        created_at=ticket.created_at,
    )


@router.post("/{ticket_id}/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    ticket_id: int,
    feedback: TicketFeedback,
    db: Session = Depends(get_db),
    current_user_id: int = None  # Would come from auth
):
    """
    Client leaves feedback post-response
    - Satisfait ou Non satisfait
    - Raison si non satisfait
    """
    if current_user_id is None:
        raise HTTPException(status_code=401, detail="Authentication required (stub)")

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id, Ticket.client_id == current_user_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if not ticket.processed:
        raise HTTPException(status_code=400, detail="Cannot submit feedback before ticket is processed")

    ticket.feedback_satisfied = feedback.satisfied
    ticket.feedback_reason = feedback.reason
    db.add(ticket)
    db.commit()

    return FeedbackResponse(ticket_id=ticket.id, satisfied=ticket.feedback_satisfied, reason=ticket.feedback_reason, submitted_at=datetime.utcnow())


# ========== AGENT SUPPORT ENDPOINTS ==========

@router.get("/agent/list", response_model=TicketListResponse)
async def get_agent_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user_id: int = None  # Would come from auth (agent)
):
    """
    Support agent views all tickets submitted by clients with pagination
    """
    # For now require authentication stub
    if current_user_id is None:
        raise HTTPException(status_code=401, detail="Authentication required (agent stub)")

    query = db.query(Ticket).order_by(Ticket.created_at.desc())
    total = query.count()
    offset = (page - 1) * page_size
    rows = query.offset(offset).limit(page_size).all()

    items = [
        {
            "id": t.id,
            "title": t.title,
            "category": t.category,
            "escalated": t.escalated,
            "processed": t.processed,
            "created_at": t.created_at,
        }
        for t in rows
    ]

    total_pages = math.ceil(total / page_size) if page_size else 1
    return TicketListResponse(items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)


@router.get("/agent/search", response_model=TicketListResponse)
async def search_tickets(
    ticket_id: Optional[int] = Query(None),
    title: Optional[str] = Query(None),
    client_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    escalated: Optional[bool] = Query(None),
    processed: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user_id: int = None  # Would come from auth (agent)
):
    """
    Support agent searches and filters tickets
    - Par numéro de ticket
    - Par sujet (title)
    - Par client
    - Par catégorie
    - Par état escaladé (escalated)
    - Par état traité (processed)
    """
    if current_user_id is None:
        raise HTTPException(status_code=401, detail="Authentication required (agent stub)")

    query = db.query(Ticket)
    if ticket_id is not None:
        query = query.filter(Ticket.id == ticket_id)
    if title:
        query = query.filter(Ticket.title.ilike(f"%{title}%"))
    if client_id is not None:
        query = query.filter(Ticket.client_id == client_id)
    if category:
        query = query.filter(Ticket.category == category)
    if escalated is not None:
        query = query.filter(Ticket.escalated == escalated)
    if processed is not None:
        query = query.filter(Ticket.processed == processed)

    total = query.count()
    offset = (page - 1) * page_size
    rows = query.order_by(Ticket.created_at.desc()).offset(offset).limit(page_size).all()

    items = [
        {
            "id": t.id,
            "title": t.title,
            "category": t.category,
            "escalated": t.escalated,
            "processed": t.processed,
            "created_at": t.created_at,
        }
        for t in rows
    ]

    total_pages = math.ceil(total / page_size) if page_size else 1
    return TicketListResponse(items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)


@router.get("/agent/{ticket_id}", response_model=TicketDetail)
async def get_agent_ticket_detail(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = None  # Would come from auth (agent)
):
    """
    Support agent views complete ticket details
    """
    if current_user_id is None:
        raise HTTPException(status_code=401, detail="Authentication required (agent stub)")

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return TicketDetail(
        id=ticket.id,
        title=ticket.title,
        description=ticket.description,
        category=ticket.category,
        client_id=ticket.client_id,
        agent_id=ticket.agent_id,
        escalated=ticket.escalated,
        processed=ticket.processed,
        response=ticket.response,
        responded_at=ticket.responded_at,
        feedback_satisfied=ticket.feedback_satisfied,
        feedback_reason=ticket.feedback_reason,
        created_at=ticket.created_at,
    )


@router.post("/agent/{ticket_id}/response", response_model=AgentResponseDetail)
async def respond_to_ticket(
    ticket_id: int,
    response: AgentResponse,
    db: Session = Depends(get_db),
    current_user_id: int = None  # Would come from auth (agent)
):
    """
    Support agent responds to a ticket
    - Marks processed = True
    """
    if current_user_id is None:
        raise HTTPException(status_code=401, detail="Authentication required (agent stub)")

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.response = response.response
    ticket.responded_at = datetime.utcnow()
    ticket.processed = True
    ticket.agent_id = current_user_id
    db.add(ticket)
    db.commit()

    return AgentResponseDetail(ticket_id=ticket.id, response=ticket.response, responded_at=ticket.responded_at, agent_id=ticket.agent_id)


@router.post("/agent/{ticket_id}/escalate", response_model=EscalationResponse)
async def escalate_ticket(
    ticket_id: int,
    escalation: TicketEscalation,
    db: Session = Depends(get_db),
    current_user_id: int = None  # Would come from auth (agent)
):
    """
    Support agent escalates a ticket to AI
    - Marks escalated = True
    """
    if current_user_id is None:
        raise HTTPException(status_code=401, detail="Authentication required (agent stub)")

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.escalated = True
    ticket.escalated_at = datetime.utcnow()
    db.add(ticket)
    db.commit()

    return EscalationResponse(ticket_id=ticket.id, escalated=ticket.escalated, escalated_at=ticket.escalated_at, ai_processing=False)