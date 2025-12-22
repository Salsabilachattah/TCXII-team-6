from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt

from app.core.dependencies import get_db
from app.models.users import User
from app.schemas.user import UserResponse, UserUpdate

SECRET_KEY = "SECRET_KEY_HACKATHON"
ALGORITHM = "HS256"

router = APIRouter(prefix="/users", tags=["Users"])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user_from_token)):
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
):
    for key, value in data.dict(exclude_unset=True).items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/Desactiver-compte")
def desactivate_account(current_user: User = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    """Désactive le compte de l'utilisateur courant."""
    user = current_user

    if not user.is_active:
        return {"message": "Account is already deactivated"}

    user.is_active = False
    db.commit()

    return {"message": "Account desactivated successfully"}


@router.post("/Reactiver-compte")
def reactivate_account(current_user: User = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    """Réactive le compte de l'utilisateur courant."""
    user = current_user

    if user.is_active:
        return {"message": "Account is already active"}

    user.is_active = True
    db.commit()

    return {"message": "Account reactivated successfully"}


@router.delete("/delete-account")
def delete_account(current_user: User = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    """Supprime définitivement le compte de l'utilisateur courant."""
    user = current_user

    db.delete(user)
    db.commit()

    return {"message": "Account deleted successfully"}
