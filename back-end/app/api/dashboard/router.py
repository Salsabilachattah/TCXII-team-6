from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.dependencies import get_db
from app.api.dashboard import controller
from app.schemas.dash_schemas import DashboardStats, AlertResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    return controller.get_dashboard_stats(db)


@router.get("/detailed-metrics")
def get_detailed_metrics(db: Session = Depends(get_db)):
    return controller.get_detailed_metrics(db)


@router.get("/alerts", response_model=List[AlertResponse])
def get_system_alerts(db: Session = Depends(get_db)):
    return controller.get_system_alerts(db)


@router.get("/category-breakdown")
def get_category_breakdown(db: Session = Depends(get_db)):
    return controller.get_category_breakdown(db)


@router.get("/agent-performance")
def get_agent_performance(db: Session = Depends(get_db)):
    return controller.get_agent_performance(db)
