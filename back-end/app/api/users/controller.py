from fastapi import HTTPException, Request, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
import jwt

from app.core.dependencies import get_db
from app.models.users import User
from app.schemas.user import UserResponse, UserUpdate
from app.core.config import settings
SECRET_KEY = "SECRET_KEY_HACKATHON"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), request: Request = None):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # If the user must change password, only allow the password change endpoint and logout/refresh
    allowed_paths = ["/auth/change-password", "/auth/logout"]
    if getattr(user, "must_change_password", False) and request is not None and request.url.path not in allowed_paths:
        raise HTTPException(status_code=403, detail="Password must be changed on first login")

    return user

# Controller actions

def me(current_user: User = Depends(get_current_user_from_token)) -> User:
    return current_user


def update_me(data: UserUpdate, current_user: User = Depends(get_current_user_from_token), db: Session = Depends(get_db)) -> User:
    for key, value in data.dict(exclude_unset=True).items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)
    return current_user


def desactivate_account(current_user: User = Depends(get_current_user_from_token), db: Session = Depends(get_db)) -> dict:
    user = current_user

    if not user.is_active:
        return {"message": "Account is already deactivated"}

    user.is_active = False
    db.commit()

    return {"message": "Account desactivated successfully"}


def reactivate_account(current_user: User = Depends(get_current_user_from_token), db: Session = Depends(get_db)) -> dict:
    user = current_user

    if user.is_active:
        return {"message": "Account is already active"}

    user.is_active = True
    db.commit()

    return {"message": "Account reactivated successfully"}


def delete_account(current_user: User = Depends(get_current_user_from_token), db: Session = Depends(get_db)) -> dict:
    user = current_user

    db.delete(user)
    db.commit()

    return {"message": "Account deleted successfully"}