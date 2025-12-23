from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List

TICKET_CATEGORIES = ["guide", "faq", "policies", "general"]

# ========== TICKET CREATION (CLIENT) ==========
class TicketCreate(BaseModel):
    """Schéma pour créer un ticket"""
    title: str = Field(..., min_length=5, max_length=200, description="Sujet du ticket")
    description: str = Field(..., min_length=10, description="Description complète")
    category: str = Field(default="general")
    
    @validator('category')
    def validate_category(cls, v):
        if v not in TICKET_CATEGORIES:
            raise ValueError(f"Catégorie invalide. Options: {', '.join(TICKET_CATEGORIES)}")
        return v
    
    class Config:
        from_attributes = True


# ========== TICKET BASE ==========
# class TicketBase(BaseModel):
#     """Schéma de base pour les tickets"""
#     title: str = Field(..., min_length=5, max_length=200, description="Sujet du ticket")
#     description: str = Field(..., min_length=10, description="Description complète")
#     category: str = Field(default="general")
    
#     @validator('category')
#     def validate_category(cls, v):
#         if v not in TICKET_CATEGORIES:
#             raise ValueError(f"Catégorie invalide. Options: {', '.join(TICKET_CATEGORIES)}")
#         return v


# ========== TICKET RESPONSE (VIEW) ==========
class TicketResponse(BaseModel):
    """Pour renvoyer un ticket - Vue client"""
    id: int
    title: str
    description: str
    category: str
    client_id: int
    escalated: bool = False
    processed: bool = False
    created_at: datetime
    reference: Optional[str] = None
    
    class Config:
        from_attributes = True


# ========== TICKET DETAIL (COMPREHENSIVE) ==========
class TicketDetail(BaseModel):
    """Schéma détaillé d'un ticket - pour agents support"""
    id: int
    title: str
    description: str
    category: str
    client_id: int
    agent_id: Optional[int] = None
    escalated: bool = False
    processed: bool = False
    response: Optional[str] = None  # Has response when processed = True
    responded_at: Optional[datetime] = None
    feedback_satisfied: Optional[bool] = None
    feedback_reason: Optional[str] = None
    created_at: datetime
    reference: Optional[str] = None

    class Config:
        from_attributes = True


# ========== TICKET LIST WITH PAGINATION ==========
class TicketListItem(BaseModel):
    """Item dans une liste paginée de tickets"""
    id: int
    title: str
    reference: Optional[str] = None
    category: str
    escalated: bool = False
    processed: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    """Réponse paginée de tickets"""
    items: List[TicketListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# ========== AGENT RESPONSE ==========
class AgentResponse(BaseModel):
    """Schéma pour répondre à un ticket"""
    response: str = Field(..., min_length=10, description="Réponse à fournir")
    
    class Config:
        from_attributes = True


class AgentResponseDetail(BaseModel):
    """Réponse détaillée de l'agent"""
    ticket_id: int
    response: str
    responded_at: datetime
    agent_id: int
    
    class Config:
        from_attributes = True


# ========== FEEDBACK ==========
class TicketFeedback(BaseModel):
    """Pour le feedback client post-réponse"""
    satisfied: bool
    reason: Optional[str] = Field(None, max_length=500, description="Raison si non satisfait")
    
    class Config:
        from_attributes = True


class FeedbackResponse(BaseModel):
    """Réponse après feedback"""
    ticket_id: int
    satisfied: bool
    reason: Optional[str]
    submitted_at: datetime
    
    class Config:
        from_attributes = True


# ========== TICKET SEARCH & FILTER ==========
class TicketSearchParams(BaseModel):
    """Paramètres de recherche et filtrage"""
    ticket_id: Optional[int] = None
    title: Optional[str] = None
    client_id: Optional[int] = None
    category: Optional[str] = None
    escalated: Optional[bool] = None
    processed: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    
    @validator('category')
    def validate_category(cls, v):
        if v and v not in TICKET_CATEGORIES:
            raise ValueError(f"Catégorie invalide. Options: {', '.join(TICKET_CATEGORIES)}")
        return v

    class Config:
        from_attributes = True


# ========== ESCALATION ==========
class TicketEscalation(BaseModel):
    """Schéma pour escalader un ticket à l'IA"""
    ticket_id: int
    reason: Optional[str] = Field(None, max_length=500, description="Raison de l'escalade")
    
    class Config:
        from_attributes = True


class EscalationResponse(BaseModel):
    """Réponse d'escalade"""
    ticket_id: int
    escalated: bool = True
    escalated_at: datetime
    ai_processing: bool = False
    
    class Config:
        from_attributes = True
