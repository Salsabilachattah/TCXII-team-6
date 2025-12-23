from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import math
from fastapi import HTTPException

from app.models.tickets import Ticket
from app.models.users import User
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


def create_ticket(ticket: TicketCreate, db: Session, current_user: User):
    db_ticket = Ticket(
        title=ticket.title,
        description=ticket.description,
        category=ticket.category,
        client_id=current_user.id,
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)

    from app.features.ticket_reference.generator import generate_reference

    db_ticket.reference = generate_reference(db_ticket.id, category=db_ticket.category, created_at=db_ticket.created_at)
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
        reference=db_ticket.reference,
    )


def get_client_tickets(page: int, page_size: int, db: Session, current_user: User):
    query = db.query(Ticket).filter(Ticket.client_id == current_user.id).order_by(Ticket.created_at.desc())
    total = query.count()
    offset = (page - 1) * page_size
    rows = query.offset(offset).limit(page_size).all()

    items = [
        {
            "id": t.id,
            "title": t.title,
            "reference": t.reference,
            "category": t.category,
            "escalated": t.escalated,
            "processed": t.processed,
            "created_at": t.created_at,
        }
        for t in rows
    ]

    total_pages = math.ceil(total / page_size) if page_size else 1

    return TicketListResponse(items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)


def get_ticket_detail(ticket_id: int, db: Session, current_user: User):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id, Ticket.client_id == current_user.id).first()
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
        reference=ticket.reference,
    )


def submit_feedback(ticket_id: int, feedback: TicketFeedback, db: Session, current_user: User):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id, Ticket.client_id == current_user.id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if not ticket.processed or not ticket.response or not ticket.responded_at:
        raise HTTPException(status_code=400, detail="Cannot submit feedback before ticket is processed and answered")

    if ticket.feedback_satisfied is not None:
        raise HTTPException(status_code=400, detail="Feedback already submitted for this ticket")

    if feedback.satisfied is False and (not feedback.reason or feedback.reason.strip() == ""):
        raise HTTPException(status_code=400, detail="Reason is required when marking feedback as not satisfied")

    ticket.feedback_satisfied = feedback.satisfied
    ticket.feedback_reason = feedback.reason
    db.add(ticket)
    db.commit()

    return FeedbackResponse(ticket_id=ticket.id, satisfied=ticket.feedback_satisfied, reason=ticket.feedback_reason, submitted_at=datetime.utcnow())


# Agent functions

def get_agent_tickets(page: int, page_size: int, db: Session, current_user: User):
    query = db.query(Ticket).order_by(Ticket.created_at.desc())
    total = query.count()
    offset = (page - 1) * page_size
    rows = query.offset(offset).limit(page_size).all()

    items = [
        {
            "id": t.id,
            "title": t.title,
            "reference": t.reference,
            "category": t.category,
            "escalated": t.escalated,
            "processed": t.processed,
            "created_at": t.created_at,
        }
        for t in rows
    ]

    total_pages = math.ceil(total / page_size) if page_size else 1
    return TicketListResponse(items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)


def search_tickets(ticket_id: Optional[int], title: Optional[str], client_id: Optional[int], category: Optional[str], escalated: Optional[bool], processed: Optional[bool], page: int, page_size: int, db: Session, current_user: User):
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
            "reference": t.reference,
            "category": t.category,
            "escalated": t.escalated,
            "processed": t.processed,
            "created_at": t.created_at,
        }
        for t in rows
    ]

    total_pages = math.ceil(total / page_size) if page_size else 1
    return TicketListResponse(items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)


def get_agent_ticket_detail(ticket_id: int, db: Session, current_user: User):
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
        reference=ticket.reference,
    )


def respond_to_ticket(ticket_id: int, response: AgentResponse, db: Session, current_user: User):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.response = response.response
    ticket.responded_at = datetime.utcnow()
    ticket.processed = True
    ticket.agent_id = current_user.id
    db.add(ticket)
    db.commit()

    return AgentResponseDetail(ticket_id=ticket.id, response=ticket.response, responded_at=ticket.responded_at, agent_id=ticket.agent_id)


def escalate_ticket(ticket_id: int, escalation: TicketEscalation, db: Session, current_user: User):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.escalated = True
    ticket.escalated_at = datetime.utcnow()
    db.add(ticket)
    db.commit()

    return EscalationResponse(ticket_id=ticket.id, escalated=ticket.escalated, escalated_at=ticket.escalated_at, ai_processing=False)
