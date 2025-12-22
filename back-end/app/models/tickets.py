from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from core.database import Base


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
    escaladed = Column(Boolean, default=False)
    processed = Column(Boolean, default=False)

    # Réponse
    response = Column(Text, nullable=True)
    responsed_at = Column(DateTime, nullable=True)

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
