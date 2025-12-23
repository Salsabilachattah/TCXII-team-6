from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    # Clé primaire
    id = Column(Integer, primary_key=True, index=True)

    # Informations personnelles
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone_num = Column(String(20), unique=False, nullable=True)
    gender = Column(String(10))
    date_naissance = Column(Date)
    profession = Column(String(100))

    # Authentification et autorisation
    hashed_password = Column(String(255), nullable=False)
    refresh_token = Column(String(500), nullable=True)

    role = Column(String(50), nullable=False)  # client | agent | admin
    is_active = Column(Boolean, default=True)

    # Force agent to change password on first login
    must_change_password = Column(Boolean, default=False)

    # Statistiques
    nbr_of_tickets = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    tickets_created = relationship(
        "Ticket",
        foreign_keys="Ticket.client_id",
        back_populates="client"
    )

    tickets_handled = relationship(
        "Ticket",
        foreign_keys="Ticket.agent_id",
        back_populates="agent"
    )
