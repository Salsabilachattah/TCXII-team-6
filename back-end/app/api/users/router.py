from fastapi import APIRouter, Depends
from app.api.users import controller
from app.core.dependencies import get_db
from sqlalchemy.orm import Session
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def me(current_user = Depends(controller.get_current_user_from_token)):
    return controller.me(current_user)


@router.patch("/me", response_model=UserResponse)
def update_me(data: UserUpdate, current_user = Depends(controller.get_current_user_from_token), db: Session = Depends(get_db)):
    return controller.update_me(data, current_user, db)


@router.post("/Desactiver-compte")
def desactivate_account(current_user = Depends(controller.get_current_user_from_token), db: Session = Depends(get_db)):
    return controller.desactivate_account(current_user, db)


@router.post("/Reactiver-compte")
def reactivate_account(current_user = Depends(controller.get_current_user_from_token), db: Session = Depends(get_db)):
    return controller.reactivate_account(current_user, db)


@router.delete("/delete-account")
def delete_account(current_user = Depends(controller.get_current_user_from_token), db: Session = Depends(get_db)):
    return controller.delete_account(current_user, db)
