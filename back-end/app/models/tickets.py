from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    # Clé primaire
    id = Column(Integer, primary_key=True, index=True)

    # Informations du ticket
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)

    # Relations avec users
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Statut du ticket
    escalated = Column(Boolean, default=False)
    escalated_at = Column(DateTime, nullable=True)
    processed = Column(Boolean, default=False)
    category = Column(String(100), nullable=False)  
    reference = Column(String(50), unique=True, nullable=True, index=True)

    # Réponse
    response = Column(Text, nullable=True)
    responded_at = Column(DateTime, nullable=True)

    # Feedback
    feedback_satisfied = Column(Boolean, nullable=True)
    feedback_reason = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    client = relationship(
        "User",
        foreign_keys=[client_id],
        back_populates="tickets_created"
    )

    agent = relationship(
        "User",
        foreign_keys=[agent_id],
        back_populates="tickets_handled"
    )
