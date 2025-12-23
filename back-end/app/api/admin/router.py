from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.permissions import require_roles
from app.schemas.user import AgentCreate, AgentResponse
from app.api.admin import controller

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.post("/agents", response_model=AgentResponse)
def create_agent_endpoint(data: AgentCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: dict = Depends(require_roles("admin"))):
    """Endpoint wrapper: calls the controller and returns the result."""
    return controller.create_agent(data, db)
