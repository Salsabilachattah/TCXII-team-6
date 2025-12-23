from pydantic import BaseModel
from typing import Dict
from datetime import datetime


class DashboardStats(BaseModel):
    total_tickets: int = 0
    tickets_en_attente: int = 0
    tickets_traites: int = 0
    par_categorie: Dict[str, int] = {"guide": 0, "faq": 0, "policies": 0, "general": 0}
    taux_escalade: float = 0.0
    tickets_escalades: int = 0
    taux_satisfaction_ai: float = 0.0
    generated_at: datetime


class AlertCreate(BaseModel):
    title: str
    message: str
    severity: str


class AlertResponse(BaseModel):
    id: int
    title: str
    message: str
    severity: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
