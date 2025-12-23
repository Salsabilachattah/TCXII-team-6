from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List

from app.core.dependencies import get_db
from app.models.tickets import Ticket
from app.models.users import User
from app.schemas.dash_schemas import (
    DashboardStats,
    AlertResponse
)


def get_dashboard_stats(db: Session) -> DashboardStats:
    total_tickets = db.query(Ticket).count()
    tickets_en_attente = db.query(Ticket).filter(Ticket.processed == False).count()
    tickets_traites = db.query(Ticket).filter(Ticket.processed == True).count()
    tickets_escalades = db.query(Ticket).filter(Ticket.escalated == True).count()

    categories = ["guide", "faq", "policies", "general"]
    par_categorie = {}
    for category in categories:
        count = db.query(Ticket).filter(Ticket.category == category).count()
        par_categorie[category] = count

    taux_escalade = 0.0
    if total_tickets > 0:
        taux_escalade = round((tickets_escalades / total_tickets) * 100, 2)

    ai_tickets_with_feedback = db.query(Ticket).filter(
        Ticket.escalated == False,
        Ticket.feedback_satisfied.isnot(None),
    ).all()

    taux_satisfaction_ai = 0.0
    if ai_tickets_with_feedback:
        satisfied_count = sum(1 for t in ai_tickets_with_feedback if t.feedback_satisfied)
        taux_satisfaction_ai = round((satisfied_count / len(ai_tickets_with_feedback)) * 100, 2)

    return DashboardStats(
        total_tickets=total_tickets,
        tickets_en_attente=tickets_en_attente,
        tickets_traites=tickets_traites,
        par_categorie=par_categorie,
        taux_escalade=taux_escalade,
        tickets_escalades=tickets_escalades,
        taux_satisfaction_ai=taux_satisfaction_ai,
        generated_at=datetime.utcnow(),
    )


def get_detailed_metrics(db: Session) -> dict:
    total = db.query(Ticket).count()

    pending = db.query(Ticket).filter(Ticket.processed == False).count()
    escalated = db.query(Ticket).filter(Ticket.escalated == True).count()
    ai_resolved = db.query(Ticket).filter(Ticket.processed == True, Ticket.escalated == False).count()
    agent_resolved = db.query(Ticket).filter(Ticket.processed == True, Ticket.escalated == True).count()

    categories = db.query(Ticket.category).distinct().all()
    satisfaction_par_categorie = {}
    for (category,) in categories:
        cat_tickets = db.query(Ticket).filter(Ticket.category == category, Ticket.feedback_satisfied.isnot(None)).all()
        if cat_tickets:
            satisfied = sum(1 for t in cat_tickets if t.feedback_satisfied)
            satisfaction_rate = round((satisfied / len(cat_tickets)) * 100, 2)
            satisfaction_par_categorie[category] = satisfaction_rate
        else:
            satisfaction_par_categorie[category] = 0.0

    all_feedback = db.query(Ticket).filter(Ticket.feedback_satisfied.isnot(None)).all()
    overall_satisfaction = 0.0
    alerts = []
    if all_feedback:
        satisfied = sum(1 for t in all_feedback if t.feedback_satisfied)
        overall_satisfaction = round((satisfied / len(all_feedback)) * 100, 2)
        if overall_satisfaction < 75:
            alerts.append({
                "type": "low_satisfaction",
                "message": f"Satisfaction client basse: {overall_satisfaction}%",
                "severity": "high",
            })

    escalation_rate = round((escalated / total * 100), 2) if total > 0 else 0
    if escalation_rate > 50:
        alerts.append({
            "type": "high_escalation",
            "message": f"Taux d'escalade élevé: {escalation_rate}%",
            "severity": "medium",
        })

    agent_stats = (
        db.query(User.id, User.first_name, User.last_name, func.count(Ticket.id).label("tickets_handled"))
        .join(Ticket, User.id == Ticket.agent_id)
        .filter(Ticket.processed == True)
        .group_by(User.id, User.first_name, User.last_name)
        .all()
    )

    agents_performance = [
        {
            "agent_id": agent_id,
            "agent_name": f"{first or ''} {last or ''}".strip() or f"Agent {agent_id}",
            "tickets_handled": tickets_handled,
        }
        for agent_id, first, last, tickets_handled in agent_stats
    ]

    return {
        "totals": {"total_tickets": total, "pending_tickets": pending, "escalated_tickets": escalated, "ai_resolved_tickets": ai_resolved, "agent_resolved_tickets": agent_resolved},
        "percentages": {"ai_resolution_rate": round((ai_resolved / total * 100), 2) if total > 0 else 0, "escalation_rate": escalation_rate, "overall_satisfaction_rate": overall_satisfaction},
        "satisfaction_by_category": satisfaction_par_categorie,
        "alerts": alerts,
        "agent_performance": agents_performance,
        "generated_at": datetime.utcnow().isoformat(),
    }


def get_system_alerts(db: Session) -> List[AlertResponse]:
    alerts_data = []
    alert_id = 1

    all_feedback = db.query(Ticket).filter(Ticket.feedback_satisfied.isnot(None)).all()
    if all_feedback:
        satisfied = sum(1 for t in all_feedback if t.feedback_satisfied)
        satisfaction_rate = (satisfied / len(all_feedback)) * 100
        if satisfaction_rate < 75:
            alerts_data.append({
                "id": alert_id,
                "title": "Satisfaction client basse",
                "message": f"Le taux de satisfaction client est de {satisfaction_rate:.1f}% (< 75%)",
                "severity": "high",
                "is_read": False,
                "created_at": datetime.utcnow(),
            })
            alert_id += 1

    total = db.query(Ticket).count()
    escalated = db.query(Ticket).filter(Ticket.escalated == True).count()
    if total > 0:
        escalation_rate = (escalated / total) * 100
        if escalation_rate > 50:
            alerts_data.append({
                "id": alert_id,
                "title": "Taux d'escalade élevé",
                "message": f"Le taux d'escalade est de {escalation_rate:.1f}% (> 50%)",
                "severity": "medium",
                "is_read": False,
                "created_at": datetime.utcnow(),
            })
            alert_id += 1

    pending = db.query(Ticket).filter(Ticket.processed == False).count()
    if pending > 100:
        alerts_data.append({
            "id": alert_id,
            "title": "Backlog important",
            "message": f"{pending} tickets en attente de traitement",
            "severity": "medium",
            "is_read": False,
            "created_at": datetime.utcnow(),
        })

    return alerts_data


def get_category_breakdown(db: Session) -> dict:
    categories = ["guide", "faq", "policies", "general"]
    breakdown = {}

    for category in categories:
        cat_query = db.query(Ticket).filter(Ticket.category == category)
        total = cat_query.count()
        if total == 0:
            breakdown[category] = {"total": 0, "escalated": 0, "resolved": 0, "satisfaction_rate": 0.0}
            continue
        escalated = cat_query.filter(Ticket.escalated == True).count()
        resolved = cat_query.filter(Ticket.processed == True).count()
        feedback_tickets = cat_query.filter(Ticket.feedback_satisfied.isnot(None)).all()
        satisfaction_rate = 0.0
        if feedback_tickets:
            satisfied = sum(1 for t in feedback_tickets if t.feedback_satisfied)
            satisfaction_rate = round((satisfied / len(feedback_tickets)) * 100, 2)
        breakdown[category] = {
            "total": total,
            "escalated": escalated,
            "resolved": resolved,
            "escalation_rate": round((escalated / total * 100), 2) if total > 0 else 0,
            "resolution_rate": round((resolved / total * 100), 2) if total > 0 else 0,
            "satisfaction_rate": satisfaction_rate,
        }

    return {"categories": breakdown, "generated_at": datetime.utcnow().isoformat()}
