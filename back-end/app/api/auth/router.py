from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.api.auth import controller
from app.api.users.controller import get_current_user_from_token
from app.schemas.auth import LoginRequest, RegisterRequest, RefreshTokenRequest, ChangePasswordRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    return controller.register(data, db)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return controller.login(data, db)


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    return controller.refresh(data, db)


@router.post("/logout")
def logout(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    return controller.logout(data, db)


@router.post("/change-password")
def change_password(data: ChangePasswordRequest, current_user = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    return controller.change_password(data, current_user, db)
