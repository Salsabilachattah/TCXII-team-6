from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import jwt

from app.core.dependencies import get_db
from app.models.users import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest,
    ChangePasswordRequest,
)
from app.core.security import hash_password, verify_password

# Token settings (kept as constants to match previous behavior)
SECRET_KEY = "SECRET_KEY_HACKATHON"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def register(data: RegisterRequest, db: Session):
    existing = db.query(User).filter(User.email == data.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone_num=data.phone_num,
        date_naissance=data.date_naissance,
        gender=data.gender,
        profession=data.profession,
        hashed_password=hash_password(data.password),
        role="client",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_token(
        {"user_id": user.id, "role": user.role},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    refresh_token = create_token(
        {"user_id": user.id},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    user.refresh_token = refresh_token
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def login(data: LoginRequest, db: Session):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_token(
        {"user_id": user.id, "role": user.role},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    refresh_token = create_token(
        {"user_id": user.id},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    user.refresh_token = refresh_token
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        must_change_password=bool(user.must_change_password),
    )


def refresh(data: RefreshTokenRequest, db: Session):
    user = db.query(User).filter(User.refresh_token == data.refresh_token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access_token = create_token(
        {"user_id": user.id, "role": user.role},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=data.refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def logout(data: RefreshTokenRequest, db: Session):
    user = db.query(User).filter(User.refresh_token == data.refresh_token).first()
    if user:
        user.refresh_token = None
        db.commit()

    return {"message": "Logged out successfully"}


def change_password(data: ChangePasswordRequest, current_user: User, db: Session):
    """Change password for authenticated user. Requires old_password and new_password."""

    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=401, detail="Old password is incorrect")

    current_user.hashed_password = hash_password(data.new_password)
    # Invalidate existing refresh token(s)
    current_user.refresh_token = None
    db.commit()

    return {"message": "Password changed successfully"}